#!/usr/bin/env python3
"""Acceptance gate — clickwrap, versioned (quorum R2: browsewrap ≠ binding).

A user (or an agent driving the CLI) must record an AFFIRMATIVE,
TRACEABLE acceptance of DISCLAIMER.md — pinned to its content hash and
version — before any fetch through scripts/scrape.py is allowed.

Mechanics:
- `accept`            → interactive: prints the summary, requires typing
                        exactly "I ACCEPT", stores {version, hash, at, user}
                        in ~/.oscurapling/acceptance.json (chmod 600).
- `show`              → prints the current version+hash to accept.
- (checked by scrape.py: exit E_NO_ACCEPTANCE until recorded)

The acceptance file is local evidence (timestamped, hash-pinned) — the next
best thing to a signed clickwrap for anonymous users, and it makes agent
drives self-documenting.
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DISCLAIMER = ROOT / "DISCLAIMER.md"
STORE = Path(os.environ.get("OSCURAPLING_ACCEPTANCE_FILE",
                            str(Path.home() / ".oscurapling" / "acceptance.json")))
TERMS_VERSION = "2.0"  # bump on every DISCLAIMER.md material change


def terms_hash() -> str:
    return hashlib.sha256(DISCLAIMER.read_bytes()).hexdigest()


def accepted() -> dict | None:
    if not STORE.exists():
        return None
    try:
        rec = json.loads(STORE.read_text())
    except Exception:
        return None
    if rec.get("terms_version") != TERMS_VERSION:
        return None
    if rec.get("terms_sha256") != terms_hash():
        return None  # terms edited since acceptance → must re-accept
    return rec


def require() -> None:
    """Called by scrape.py before any fetch. Exit 3 = E_NO_ACCEPTANCE."""
    rec = accepted()
    if rec is None:
        print(json.dumps({
            "ok": False, "error": "E_NO_ACCEPTANCE",
            "message": "DISCLAIMER.md acceptance required (versioned clickwrap).",
            "how": "python scripts/accept_terms.py accept",
            "terms_version": TERMS_VERSION, "terms_sha256": terms_hash(),
        }))
        sys.exit(3)


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "show":
        print(json.dumps({"terms_version": TERMS_VERSION,
                          "terms_sha256": terms_hash(),
                          "accepted": accepted()}, indent=1))
        return 0
    if cmd == "accept":
        summary = (DISCLAIMER.read_text(encoding="utf-8")[:1200])
        print(summary)
        print("\n---\nType exactly  I ACCEPT  to accept every clause above")
        print(f"(version {TERMS_VERSION}, sha256 {terms_hash()[:16]}…):")
        answer = input("> ").strip()
        if answer != "I ACCEPT":
            print(json.dumps({"ok": False, "error": "E_ACCEPT_REFUSED",
                              "message": "acceptance not recorded"}))
            return 2
        rec = {"terms_version": TERMS_VERSION, "terms_sha256": terms_hash(),
               "accepted_at": datetime.now(timezone.utc).isoformat(),
               "user": os.environ.get("USER", "unknown"),
               "method": "interactive-clickwrap"}
        STORE.parent.mkdir(parents=True, exist_ok=True)
        STORE.write_text(json.dumps(rec, indent=1))
        os.chmod(STORE, 0o600)
        print(json.dumps({"ok": True, **rec}))
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())