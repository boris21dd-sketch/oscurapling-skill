#!/usr/bin/env python3
"""4th negative eval: the clickwrap gate itself."""
import json, os, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path("/home/bob/oscurapling-skill")
SCRAPE = ROOT / "scripts" / "scrape.py"
env = dict(os.environ, PYTHONPATH=str(ROOT / "oscurapling"),
           OSCURAPLING_ACCEPTANCE_FILE=tempfile.mktemp())
# acceptation avec un MAUVAIS hash (terms modifiés depuis):
Path(env["OSCURAPLING_ACCEPTANCE_FILE"]).write_text(json.dumps({
    "terms_version": "2.0", "terms_sha256": "deadbeef",
    "accepted_at": "2020-01-01T00:00:00+00:00", "user": "x", "method": "t"}))
p = subprocess.run([sys.executable, str(SCRAPE), "fetch", "https://example.com"],
                   capture_output=True, text=True, timeout=60, env=env)
accepted = (p.returncode == 3 and "E_NO_ACCEPTANCE" in p.stdout)
print(json.dumps({"eval": "E_NO_ACCEPTANCE (stale hash)", "passed": accepted,
                  "detail": f"exit={p.returncode} out={p.stdout[:80]}"}))
sys.exit(0 if accepted else 1)