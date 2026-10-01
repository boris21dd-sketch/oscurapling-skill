#!/usr/bin/env python3
"""oscurapling bench — public permissive corpus runner.

Runs the pinned oscurapling engine against `benchmark/corpus_public.txt`
(20 permissive educational sites — never the private 259). Writes
`benchmark/bench_results.json` (timestamped, no personal data).

Usage:
  PYTHONPATH=oscurapling python scripts/bench.py [--concurrency 8] [--timeout 25]
"""
from __future__ import annotations
import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(ROOT / "benchmark" / "corpus_public.txt"))
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--timeout", type=float, default=25.0)
    ap.add_argument("--out", default=str(ROOT / "benchmark" / "bench_results.json"))
    args = ap.parse_args()

    root_pkg = ROOT / "oscurapling"
    if root_pkg.is_dir():
        sys.path.insert(0, str(ROOT))
        sys.path.insert(0, str(root_pkg))
    else:
        # engine cloned to a sibling dir by the skill setup
        sys.path.insert(0, str(ROOT.parent / "oscurapling"))
        sys.path.insert(0, str(ROOT.parent))

    from oscurapling.opasync import afetch_batch  # noqa: E402
    try:
        from opcli_version import _VERSION  # type: ignore  # noqa: E402
    except ImportError:
        import oscurapling as _ocp
        _VERSION = getattr(_ocp, "__version__", "unknown")

    urls = [u.strip() for u in Path(args.corpus).read_text().splitlines()
            if u.strip() and not u.startswith("#")]
    print(f"oscurapling bench — {len(urls)} urls, concurrency {args.concurrency}")

    t0 = time.monotonic()
    rs = asyncio.run(afetch_batch(urls, concurrency=args.concurrency,
                                  timeout_s=args.timeout))
    wall = time.monotonic() - t0
    rows = [{"ok": bool(r.ok), "status": r.status, "engine": r.engine_used,
             "ms": round(r.timing_ms, 1), "bytes": len(r.html or ""),
             "error": (r.error or "")[:90], "url": u}
            for r, u in zip(rs, urls)]
    ok_rows = sorted((r["ms"] for r in rows if r["ok"]))
    med = ok_rows[len(ok_rows) // 2] if ok_rows else 0
    p95 = ok_rows[min(int(len(ok_rows) * 0.95), len(ok_rows) - 1)] if ok_rows else 0
    out = {
        "schema": 1,
        "engine_version": os.environ.get("ENGINE_VERSION", _VERSION),
        "run_at": datetime.now(timezone.utc).isoformat(),
        "corpus": len(urls),
        "ok": sum(1 for r in rows if r["ok"]),
        "median_ms": med,
        "p95_ms": p95,
        "wall_s": round(wall, 1),
        "rows": rows,
    }
    Path(args.out).write_text(json.dumps(out, indent=1))
    print(f"RESULT: {out['ok']}/{len(urls)} ok — median {med} ms, "
          f"p95 {p95} ms, wall {wall:.0f}s")
    print(f"written: {args.out}")


if __name__ == "__main__":
    main()