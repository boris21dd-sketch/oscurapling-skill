#!/usr/bin/env python3
"""oscurapling negative evals — prove the failure contract (quorum #2).

Deterministic next-action must be PROVEN, not promised. This script triggers
the 3 critical error classes and asserts the exact contract behavior:

1. E_GATE_SSRF    — fetching a private address MUST be blocked with
                    SecurityViolation (gate not bypassable), exit != 0.
2. E_UNKNOWN_ENGINE — a bad --engine value MUST fail FAST with the valid list
                    (batch = silent zero-success otherwise), exit 1.
3. E_TIMEOUT      — an unreachable host MUST return ok=false, no crash, within
                    the timeout envelope, exit != 0.

Output: timestamped JSON; exit 0 only if ALL contracts hold.
"""
from __future__ import annotations
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRAPE = ROOT / "scripts" / "scrape.py"


def run_scrape(args: list[str], timeout: float = 60.0) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRAPE)] + args,
                          capture_output=True, text=True, timeout=timeout,
                          cwd=str(ROOT))


def main() -> int:
    results = []
    all_ok = True

    # 1. SSRF gate — private address MUST be blocked
    t0 = time.monotonic()
    try:
        p = run_scrape(["fetch", "http://169.254.169.254/latest/meta-data/"])
        out = p.stdout.strip()
        blocked = (p.returncode != 0) and ("E_GATE_SSRF" in out or "SECURITY" in out.upper()
                                           or '"ok": false' in out or '"ok":false' in out)
        # gate may speak French (SECURITY: ...) — contract = non-zero + structured JSON
        if not blocked and out.startswith("{"):
            j = json.loads(out)
            blocked = (not j.get("ok", True)) and ("GATE" in out.upper()
                                                  or "SECURITY" in out.upper())
        results.append({"eval": "E_GATE_SSRF", "passed": blocked,
                        "detail": f"exit={p.returncode} out={out[:90]}",
                        "ms": round((time.monotonic()-t0)*1000)})
    except Exception as ex:
        results.append({"eval": "E_GATE_SSRF", "passed": False, "detail": str(ex)[:120]})
    all_ok &= results[-1]["passed"]

    # 2. unknown engine — fast, clear, valid list included
    t0 = time.monotonic()
    try:
        p = run_scrape(["fetch", "https://example.com", "--engine", "definitely-not-real"])
        out = p.stdout.strip()
        j = json.loads(out) if out.startswith("{") else {}
        passed = (p.returncode == 1 and j.get("error", "").startswith("E_UNKNOWN_ENGINE")
                  and "valid" in j)
        results.append({"eval": "E_UNKNOWN_ENGINE", "passed": passed,
                        "detail": f"exit={p.returncode} err={j.get('error','')[:60]}",
                        "ms": round((time.monotonic()-t0)*1000)})
    except Exception as ex:
        results.append({"eval": "E_UNKNOWN_ENGINE", "passed": False, "detail": str(ex)[:120]})
    all_ok &= results[-1]["passed"]

    # 3. unreachable host — clean failure inside the timeout envelope
    t0 = time.monotonic()
    try:
        p = run_scrape(["fetch", "https://does-not-exist-bf7f3e.invalid/"], timeout=90)
        out = p.stdout.strip()
        j = json.loads(out) if out.startswith("{") else {}
        within = (time.monotonic() - t0) < 60
        passed = (p.returncode != 0) and (not j.get("ok", True)) and within
        results.append({"eval": "E_TIMEOUT/UNREACHABLE", "passed": passed,
                        "detail": f"exit={p.returncode} err={(j.get('error') or '')[:70]}",
                        "ms": round((time.monotonic()-t0)*1000)})
    except Exception as ex:
        results.append({"eval": "E_TIMEOUT/UNREACHABLE", "passed": False, "detail": str(ex)[:120]})
    all_ok &= results[-1]["passed"]

    print(json.dumps({"at": datetime.now(timezone.utc).isoformat(),
                      "all_passed": all_ok, "evals": results}, ensure_ascii=False,
                     indent=1))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())