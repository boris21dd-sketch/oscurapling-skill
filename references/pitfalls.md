# Measured pitfalls (do not re-learn the hard way)

Every entry below was measured during a real bench run or a bugfix; none is hypothetical.

## Zombie daemons skew benchmark medians ×2.5

`obscura serve` daemons killed mid-run (or leftover from an earlier test) keep eating 100-213% CPU each; 4 zombies took a healthy batch from median 1 097 ms to **2 642 ms**. Signs: load average >5 while nothing else runs; `ps aux | grep obscura` shows several entries.

**Fix**: `for pid in $(pgrep -x obscura); do kill $pid; done`, then wait until `uptime` shows load < 2. Never `pkill -f 'obscura serve'` — it matches its own command line and kills your shell (measured SIGTERM).

## Persistent client must be reset between test processes

`_httpx_client()` shares ONE `httpx.Client` globally. If you monkeypatch `httpx.Client` in a test after the shared client already exists, your fake is silently never used — the test passes with real HTTP or fails weirdly.

**Fix**: fixtures reset `opfetch._HTTPX_SHARED = None` and `_HTTPX_SHARED_LOCK = None` before AND after each test (see the shipped `conftest.py` pattern in the private repo tests/).

## ETag / 304 cache masks timing changes

`_fetch_httpx` stores `(etag → body)` pairs and replays a 304 response from cache. A "faster" bench may simply be a cache hit. Cold vs warm timing must always be reported separately.

**Fix**: for honest cold benchmarks, `rm -f` the etag cache file first, or set `cached=false` as a filter on the result rows.

## Stale `__pycache__` = tests pass with yesterday's code

The engine tests import from a `sys.path` stub folder; stale bytecode means a test can run against old classes.

**Fix**: `rm -rf tests/__pycache__ oscurapling/__pycache__` before every pytest invocation. Not optional. Measured: two false-green runs before this became a rule.

## `pkill -f` — never match with text that contains the pattern itself

`pkill -f 'obscura serve'` sends SIGTERM to its own wrapping shell (the pattern appears in the shell command line). **Fix**: `for pid in $(pgrep -x obscura); do kill $pid; done`.

## `Runtime.evaluate` blocks during page load

Polling `document.readyState` inside CDP after `Page.navigate` freezes: on books.toscrape `readyState` was 'loading' for 11.2 s and `Runtime.evaluate` didn't return. **Fix**: listen to `Page.domContentEventFired` as the completion signal (event, not poll).

## Engine names are a closed set; "unknown engine" is silent in batch

`KNOWN_ENGINES()` gates values: a mistyped engine (e.g. `auto-fast` before v3.3.1) returns "moteur inconnu" with **0 successes in a batch that returns a valid-looking JSON skeleton** — the IndexError on empty ms list was the only signal.

**Fix**: when adding an engine, update `KNOWN_ENGINES()` FIRST, and pre-validate a new option name with a single fetch before launching a batch.

## Same-filename bench result overwrites the reference

Two bench runs pointing at the same output JSON (here `/tmp/bench_final.py` writing `bench200_v331final_results.json`) silently overwrite the historical reference. Use a versioned output file per run.

## A global `sed` on bench scripts renverses unrelated parameters

A broad text replace in a shared bench script (e.g. sed `s/auto/auto-fast/`) mutated 4 engine configs at once, producing a silently wrong run. Write a dedicated runner script per variant (the private repo keeps `/tmp/bench_*.py` for each).

## 429 Retry-After loops

`_fetch_httpx` retries a 429/503 up to 2 more times honoring `Retry-After` (≤10 s cap per sleep). A domain that always rate-limits then costs you ~30 s of wall-clock per fetch; the breaker (3 fails/domain → 60 s cooldown) exists for this — let it act, do not lower the cooldown to "speed things up".

## accuweather variance is real, not a bug

Same URL: 21.6 s in one bench run, 296 ms cold the next day. Do not "fix" a slow run by cutting timeouts; re-run the specific URL twice before diagnosing.