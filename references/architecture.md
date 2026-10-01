# Engine architecture (oscuraplingfull v3.3.3, pinned)

Read this file when you need to understand WHY routing behaves as it does, or when debugging an unexpected engine choice.

## The 6-engine route

Default auto route (when `engine="auto"`):

```
httpx → curl_cffi → obscura → invisible-fw → scrapling-stealth → fp-js
```

Each rung is attempted in order; the engine moves to the next rung only on failure (`ok=False`, timeout, or SSRF-clean network error). The **domain bandit** (`~/.oscurapling_bandit.json`) persists per-domain learned rung orders, so repeat fetches of the same domain skip dead rungs.

Engine identities:
- **httpx** — Python HTTP/2, **persistent shared client** (`_httpx_client()`, thread-safe; `OSCURAPLING_NO_PERSISTENT=1` reverts to per-fetch). Med 93 ms sequential.
- **curl_cffi** — Chrome TLS fingerprint (JA3-matched) for anti-bot edge without JS. Med 148-184 ms.
- **obscura** — real Chrome CDP. Subprocess-per-fetch (`_obscura_bin()` finds `/tmp/fusion-obscura/obscura`) OR warm-pool daemons.
- **invisible-fw** — renderer fingerprint-resistant.
- **scrapling-stealth** — Scrapling profile with stealth flag.
- **fp-js** — headless JS w/ fingerprint worker.

Special route values: `auto-fast` is `httpx-first` (identical to v3.3.1 `auto`), `cf` = Cloudflare-hardened ordering.

## Warm-pool multi-daemon design (OSCURAPLING_POOL=1)

Why: the single `obscura serve` daemon **serializes navigations** (measured: books.toscrape 1.1 s alone → 6.3 s behind 3 navs; batch median ×2.4).

Design: N daemons on **distinct ports 9360+**, each with a **semaphore of 1 navigation**. The pool assigns each fetch to the idle-est daemon. Measured improvement: 2 daemons in parallel → books 1 108 ms + quotes 596 ms **non-summed** (the serialization bottleneck disappears). 8 fetchs in parallel → 8/8 ok, max 1.1 s.

Default OFF for batch (`auto` = fast without pool boot); ON (opt-in) for sequential heavy scraping of anti-bot domains.

Environment knobs:
- `OSCURAPLING_POOL=1` enable pool (default 0)
- `OSCURAPLING_POOL_N` (default 4) daemon count
- `OSCURAPLING_POOL_PORT` (default 9360) base port

## Sync/async bridge (fetch_sync)

Rungs run inside to_thread; obscura-pool fetch is native async. The bridge uses a dedicated asyncio thread and a persistent running loop — never create `asyncio.Lock()` inside `__init__` before a loop exists (Python 3.11 loop-bound lock pitfall, measured: "Lock is bound to a different event loop").

## Status capture over CDP

Real HTTP status is captured from CDP events (`Network.responseReceived`) via a single reader/dispatcher task, NOT from `Runtime.evaluate` polling — `Runtime.evaluate` is **blocked during page load**, readyState polling is a dead pattern (measured: blocked 11.2 s on books.toscrape while readyState='loading').

`403/404 → ok=False`. A bot-block page returning HTML is NOT a success.

## DNS proof

Domain-death verdicts use a **double public DoH resolver** (Cloudflare + Google):
- `VERIFIED_NONEXISTENT` — NXDOMAIN on both → site is dead, fails for every engine
- `VERIFIED_NO_A_RECORD` — NOERROR but no A → domain empty
- `RESOLVES` — disagreement → re-probe

Evidence JSONs are timestamped in `OSCURAPLING_DNS_EVIDENCE_DIR` and are the source for any "site dead" claim — never asserted without them.

## Gates (by default, ON)

- **DNS pinning** (`scope_check`) — every connection re-resolves and pins; guards against DNS rebinding SSRF.
- **check_redirect_chain** — each redirect hop is re-scoped (max 5 hops).
- **DENYLIST_TLD** — `.gouv.fr`, `.edu`, `.int`, … blocked by default (policy choice), opt-in via `OSCURAPLING_CENSUS=1` for census workloads only.
- **Kill switch** — global emergency stop state.

## File module map (private engine)

- `opfetch.py` — rungs + breaker + bandit + ETag cache + client persistant
- `opasync.py` — async batch orchestration (`afetch_batch`), robots + limiter + bandit globals
- `oppool.py` — warm-pool multi-daemon (ObscuraPool + ObscuraPool.fetch_sync)
- `opsec.py` — gates (SecurityViolation, KillSwitchActive)
- `dns_proof.py` — double-DoH verdicts
- `opcli.py` — typer CLI (fetch-cmd, batch, extract-cmd, history, stats, watch, doctor, serve)
- `opstore.py` — SQLite at `~/.oscurapling/store.sqlite`