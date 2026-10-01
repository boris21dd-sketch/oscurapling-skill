#!/usr/bin/env python3
"""oscurapling fetch CLI wrapper — stable machine contract for agents.

Wraps the pinned engine's typer CLI with:
- exit codes 0/1 deterministic
- --json contract (schema below, never silently changed)
- engine-name validation BEFORE batch runs (typo = instant clear error)

Usage:
  PYTHONPATH=oscurapling python scripts/scrape.py fetch https://example.com
  PYTHONPATH=oscurapling python scripts/scrape.py fetch https://example.com --engine obscura
  PYTHONPATH=oscurapling python scripts/scrape.py batch urls.txt --concurrency 8
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALID_ENGINES = {"json", "md", "js", "cf", "stealth", "auto", "auto-fast"}


def _setup_path() -> None:
    root_pkg = ROOT / "oscurapling"
    if root_pkg.is_dir():
        sys.path.insert(0, str(ROOT))
        sys.path.insert(0, str(root_pkg))
    else:
        sys.path.insert(0, str(ROOT.parent / "oscurapling"))
        sys.path.insert(0, str(ROOT.parent))


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: scrape.py fetch URL [--engine E] [--json] | batch FILE [--concurrency N]")
        return 2
    _setup_path()
    cmd, rest = argv[1], argv[2:]

    # versioned clickwrap gate (quorum R2: browsewrap is unenforceable vs
    # anonymous users — acceptance must be affirmative + traceable)
    if cmd in ("fetch", "batch"):
        from accept_terms import require
        require()  # exit 3 + E_NO_ACCEPTANCE until recorded

    if cmd == "fetch" and rest:
        url = rest[0]
        engine = None
        for i, a in enumerate(rest):
            if a == "--engine" and i + 1 < len(rest):
                engine = rest[i + 1]
        if engine and engine not in VALID_ENGINES:
            # fail FAST and CLEAR (batch = silent zero-success otherwise)
            print(json.dumps({"ok": False, "error": f"E_UNKNOWN_ENGINE: {engine}",
                              "valid": sorted(VALID_ENGINES)}))
            return 1
        from opfetch import fetch
        from opsec import KillSwitchActive, SecurityViolation
        try:
            res = fetch(url, engine=engine)
        except SecurityViolation as ex:
            print(json.dumps({"ok": False, "error": f"E_GATE_SSRF: {ex}"}))
            return 1
        except KillSwitchActive as ex:
            print(json.dumps({"ok": False, "error": f"E_KILL_SWITCH: {ex}"}))
            return 1
        print(json.dumps({"ok": res.ok, "status": res.status,
                          "engine_used": res.engine_used,
                          "timing_ms": round(res.timing_ms, 1),
                          "html_len": len(res.html or ""),
                          "text_len": len(res.text or ""),
                          "title": res.title or "",
                          "cached": res.cached, "retries": res.retries,
                          "url_final": res.url_final,
                          "error": (res.error or "")[:120]}))
        return 0 if res.ok else 1

    if cmd == "batch" and rest:
        urlfile = Path(rest[0])
        conc = 8
        if "--concurrency" in rest:
            conc = int(rest[rest.index("--concurrency") + 1])
        urls = [u.strip() for u in urlfile.read_text().splitlines()
                if u.strip() and not u.startswith("#")]
        import asyncio
        from oscurapling.opasync import afetch_batch
        rs = asyncio.run(afetch_batch(urls, concurrency=conc, timeout_s=25))
        rows = [{" url": u, "ok": bool(r.ok), "status": r.status,
                 "engine": r.engine_used, "ms": round(r.timing_ms, 1),
                 "error": (r.error or "")[:90]} for r, u in zip(rs, urls)]
        ok = sum(1 for r in rows if r["ok"])
        ms = sorted(r["ms"] for r in rows if r["ok"])
        print(json.dumps({"ok": ok, "total": len(rows),
                          "median_ms": ms[len(ms)//2] if ms else 0,
                          "rows": rows}))
        return 0

    print(json.dumps({"ok": False, "error": f"E_USAGE: unknown cmd {cmd}"}))
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))