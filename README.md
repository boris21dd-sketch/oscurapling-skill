# oscurapling — resilient compliant web scraping skill for Claude

![logo](assets/logo.svg)

> **Legal notice — read [`DISCLAIMER.md`](DISCLAIMER.md) first.** Dual-use
> software, provided AS IS, no warranty; **you** are solely responsible for the
> lawfulness of your use in your jurisdiction (FR: art. 323-1/323-2 CP, LCEN,
> RGPD · US: CFAA, DMCA §1201, CCPA/CPRA, **BIPA** ($1k-5k/violation, private
> right of action), FTC §5, CAN-SPAM/TCPA — full table & honest limits in
> **Appendix A**). By using this repository you indemnify the author, accept
> **French law + arbitration + class-action waiver** (§11) and the
> **no-inducement clause (§12)**. 18+, no sanctioned parties. Not legal advice.
> Runtime enforcement: `scripts/accept_terms.py` requires an **affirmative,
> versioned, hash-pinned `I ACCEPT`** before the first fetch (browsewrap is
> unenforceable — the gate is not). Report abuse via a GitHub issue titled
> `[abuse]`.

A **Claude Agent Skill** (agentskills.io spec, as shipped in `anthropics/skills`) that turns the proven **oscurapling** scraping engine into deterministic agent judgment: when to use which engine, exactly what to do on every failure class, and how to stay compliant while doing it.

**Inspired by the best of both worlds:** [`scrapling`](https://github.com/D4Vinci/Scrapling) (stealth fetching, adaptive parsing) and [`obscura`](https://github.com/h4ckf0r0day/obscura) (CDP-grade rendering) — merged into a single routing engine with measured performance, then packaged as a skill following the conventions of the most-starred skill repos.

## Why this skill

| | Typical scraping skills | **oscurapling** |
|---|---|---|
| Engine | patterns & advice only | **6 real engines, routed by domain fingerprint** |
| Performance claims | none | **timestamped JSON bench artifacts you can re-run** |
| Failure handling | prose | **machine-readable error codes (`E_GATE_SSRF`, `E_DAEMON_STALE`…) with deterministic next actions** |
| Compliance | absent | **SSRF gates ON by default, robots honored, rate-limited, anti-bot opt-in only** |

Measured on the private 259-site real-world corpus (v3.3.3): **244/259 (96.8 % of fetchable; 7 dead domains proven by dual-DoH)**, median **93 ms sequential / 221 ms batch**, vs 1 097 ms for v3.2.0 — and versus reference engines on the same machine: scrapling 0.4.15 182 ms (median: 26 fewer sites served), obscura CLI 2 300 ms. **Grand versus, same machine, public corpus of 20 (v3.3.4, run 2026-10-01, JSON artifacts in `benchmark/`):**

| Engine | real coverage | median | p95 | honest |
|---|---|---|---|---|
| **oscurapling v3.3.4** | **20/20, 0 liar** | **241 ms** | 652 ms | every ok = verified real content |
| scrapling 0.4.15 | 20/20 | **147 ms** (fastest point) | 553 ms | 26 fewer sites served on the 259 corpus |
| Agent Reach v1.5.0 (Jina) | 19/20 + **1 liar** | 438 ms warm / **2585 ms COLD** | 579/4709 ms | stale snapshot served as ok=True (proven twice) |
| obscura CLI 0.2.3 | 19/20 | 840 ms | 2867 ms | raw single-binary rendering |

Honest notes: scrapling wins the single-site speed point (147 ms) but plateaus at 87 % on the hard 259-site corpus; **Agent Reach is a *complementary* tool** (Twitter/Reddit/YouTube via local cookies — a different battlefield), and its 265 ms "warm" number is Jina's own cache serving STALE snapshots (proven: `example.com` → dated "Test Document" twice, cache opt-out = HTTP 429).
Stress ×1000: **oscurapling 1000/1000 wall 209 s** (median 104 ms) vs Jina **98/1000** (free-tier rate-limit). See `benchmark/BENCH_X1000.md`.

![bench](assets/bench.svg)

### 2000 difficult sites + bug-bounty platform sweep (2026-10-02, engine v3.3.5)

![bench2000](assets/bench2000.svg)

- Corpus: 2000 domains, Majestic top-1M ranks 30k-250k, seed fixed. Real content = ok AND body > 200 B; liars excluded.
- **oscurapling v3.3.5: 1587/2000 (79.3 %)** — the quality loop re-fetches ok-but-empty rows through the delegation lane (**+379 recovered**); every failure is classified by the dual-DoH quorum (`E_DNS_*` verdicts), not silently dropped: 413 fails = 177 DNS-dead proven + 7 policy (.gov) + 3 DoH-inconclusive + 223 DNS-alive-but-unfetchable (retried, honestly failed).
- scrapling 0.4.15: 1619/2000 (81.0 %), median 422 ms — **fastest, stated as measured**; 0 liar.
- obscura CLI 0.2.3: 1111/2000 (55.5 %) **+ 26 liars** (ok=True, empty body), median 1792 ms.
- Agent Reach 1.5.0 (Jina): 41/2000 (2.0 %) — free-tier rate-limit (~20/round); wall time not comparable.
- Bug-bounty sweep (v3.3.5): **HackerOne 6000 public programs** crawled via public GraphQL, 5750 unique client domains tested → **5990 = 99.8 %**, median 1179 ms, wall 577 s. **Bugcrowd 291 public engagements** → 113 real content; 178 briefs render an empty shell in headless CDP (anti-bot detection) and are counted as failures, honestly.
- Raw aggregates: `benchmark/bench2000_results.json` (per-domain rows live in the engine audit log only — the private corpus is never shipped).

## Install

```bash
git clone https://github.com/boris21dd-sketch/oscurapling   # the engine (pinned v3.3.5)
git clone https://github.com/boris21dd-sketch/oscurapling-skill  # this skill
cd oscurapling-skill
ln -s ../oscurapling oscurapling   # or set PYTHONPATH to the engine dir
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Then point Claude Code (or any Agent-Skills host) at this folder: the skill self-describes via `SKILL.md` frontmatter and is picked up automatically on relevant prompts ("scrape", "fetch this", "403 on that site", "batch of URLs").

## What Claude learns from the skill

- A **decision tree** for the 6-engine route (httpx → curl_cffi → obscura → invisible-fw → scrapling-stealth → fp-js), including honest degradation when Chrome is absent.
- A **failure contract**: every error class maps to exactly one next action. No improvisation on gates.
- **Compliance by reflex**: robots.txt, rate limits, never bypassing SSRF gates, prompt-injection defense when targets could come from scraped content.
- **Measured self-benchmark**: `scripts/bench.py` on a 20-URL public permissive corpus — publishable, PII-free, re-runnable.

## Skill contents

```
oscurapling-skill/
├── SKILL.md                     # the agent-facing instructions (<500 lines, english)
├── scripts/
│   ├── scrape.py                # stable CLI wrapper: fetch/batch, --json, E_* codes
│   └── bench.py                 # public-corpus benchmark runner
├── references/
│   ├── architecture.md          # 6-engine route, warm-pool multi-daemon, DNS proof
│   ├── pitfalls.md              # 10 measured pitfalls (zombie daemons, ETag cache…)
│   └── compliant-use.md         # responsible scraping policy + injection defense
├── benchmark/
│   ├── corpus_public.txt        # 20 permissive educational sites (NOT the private list)
│   ├── bench_results.json       # last public run artifact (timestamped)
│   └── bench2000_results.json   # 2000 difficult sites + bug-bounty sweep (aggregates only)
└── assets/
    ├── logo.svg
    ├── bench.svg
    └── bench2000.svg
```

## License

MIT for the skill. The pinned engine (private repo `oscuraplingfull` v3.3.3) is referenced, not redistributed here.

## Third-party notices & acknowledgment

- [Scrapling](https://github.com/D4Vinci/Scrapling) — **BSD 3-Clause**, © 2024 Karim Shoair (D4Vinci). The engine imports it as a declared dependency (`scrapling==0.4.15`: `Adaptor`, `StealthyFetcher`) and its stealth-fetching design directly inspired the `scrapling-stealth` rung. Its license notice is preserved via the dependency declaration.
- [Obscura](https://github.com/h4ckf0r0day/obscura) — **Apache License 2.0**, © h4ckf0r0day. The engine invokes the independently-installed binary (`--file`, `--dump markdown`, `--obey-robots`) as the CDP-grade rendering rung; its engineering directly inspired the daemon architecture.
- Both projects' names and marks are used for description and attribution only (nominative fair use); **neither endorses this project** — see `DISCLAIMER.md` §7.
- These notices satisfy their respective attribution requirements while the projects remain separate: this repository ships no copy of upstream source code, only imports/calls at their pinned versions.

*Numbers change with networks — re-run the bench, do not trust READMEs, verify.*