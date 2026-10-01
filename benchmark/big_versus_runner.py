#!/usr/bin/env python3
"""Grand versus: oscuraplingfull v3.3.4 vs agent-reach(Jina) vs scrapling
0.4.15 vs obscura CLI 0.2.3 — corpus public 20, méthode commune.
Note: scrapling & obscura CLI = imports directs Python (pas subprocess) pour
une mesure équitable; jina = curl r.jina.ai (sa voie zéro-config)."""
import json, statistics, subprocess, time, os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

CORPUS = [u.strip() for u in Path("/home/bob/oscurapling-skill/benchmark/corpus_public.txt").read_text().splitlines() if u.strip() and not u.startswith("#")]
N = len(CORPUS)
SIGS = {"example.com": "Example Domain", "www.python.org": "Welcome to Python",
        "quotes.toscrape.com": "Quotes to Scrape", "books.toscrape.com": "Books to Scrape",
        "toscrape.com": "Scraping Sandbox", "www.iana.org": "Internet Assigned Numbers Authority",
        "openlibrary.org": "Open Library", "www.gutenberg.org": "Project Gutenberg",
        "news.ycombinator.com": "Hacker News", "docs.python.org": "Python",
        "www.crummy.com": "Beautiful Soup", "docs.scrapy.org": "Scrapy",
        "www.selenium.dev": "Selenium", "www.playwright.dev": "Playwright",
        "en.wikipedia.org": "Web scraping", "realpython.com": "Real Python",
        "developer.mozilla.org": "MDN", "www.rfc-editor.org": "RFC",
        "cheatsheets.zip": "", "explainshell.com": "explainshell"}
REPO = "/home/bob/oscuraplingfull"
ENV = dict(os.environ, PYTHONPATH=f"{REPO}:{REPO}/oscurapling")
VE = "/home/bob/oscuraplingfull-venv/bin/python"

# --- nos fetchs (in-process, 1 sous-process pour tout le lot = zéro overhead):
def ours_all():
    code = """
import sys, json, time
sys.path[:0] = ["/home/bob/oscuraplingfull", "/home/bob/oscuraplingfull/oscurapling"]
from opfetch import fetch
urls = json.load(sys.stdin)
out = []
for u in urls:
    t0 = time.monotonic()
    try:
        r = fetch(u, timeout_s=25)
        body = r.text or r.html or ""
        out.append({"url": u, "ok": bool(r.ok), "ms": round((time.monotonic()-t0)*1000,1),
                    "len": len(body), "engine": r.engine_used, "body_head": body[:500]})
    except Exception as e:
        out.append({"url": u, "ok": False, "ms": round((time.monotonic()-t0)*1000,1),
                    "len": 0, "engine": "none", "body_head": "", "err": str(e)[:60]})
print(json.dumps(out))
"""
    t0 = time.monotonic()
    p = subprocess.run([VE, "-c", code], input=json.dumps(CORPUS), capture_output=True,
                       text=True, timeout=600, env=ENV)
    wall = round((time.monotonic()-t0)*1000/1000,1)
    rows = json.loads(p.stdout.strip().splitlines()[-1])
    return rows, wall

# --- scrapling (httpx fetch simple + StealthyFetcher fallback? = SA voie auto):
def scrapling_all():
    code = """
import sys, json, time
from scrapling.fetchers import Fetcher, StealthyFetcher
urls = json.load(sys.stdin)
out = []
for u in urls:
    t0 = time.monotonic()
    ok, body, eng = False, "", "fetcher"
    try:
        r = Fetcher.get(u, timeout=25)
        body = (r.body.decode() if isinstance(r.body, bytes) else (r.body or ""))
        ok = r.status == 200 and len(body) > 50
        eng = "Fetcher"
        if not ok:
            r2 = StealthyFetcher.fetch(u, timeout=25000, headless=True)
            body = (r2.body.decode() if isinstance(r2.body, bytes) else (r2.body or ""))
            ok = r2.status == 200 and len(body) > 50
            eng = "StealthyFetcher"
    except Exception as e:
        eng = f"err {str(e)[:30]}"
    out.append({"url": u, "ok": ok, "ms": round((time.monotonic()-t0)*1000,1),
                "len": len(body), "engine": eng, "body_head": body[:500]})
print(json.dumps(out, default=str))
"""
    t0 = time.monotonic()
    p = subprocess.run([VE, "-c", code], input=json.dumps(CORPUS), capture_output=True,
                       text=True, timeout=1800, env=ENV)
    wall = round((time.monotonic()-t0),1)
    if p.returncode != 0:
        raise RuntimeError(f"subprocess scrapling rc={p.returncode}: {(p.stderr or chr(32))[-200:]}")
    try:
        rows = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        raise RuntimeError(f"parse fail rc={p.returncode} stdout[:200]={p.stdout[:200]} stderr={(p.stderr or chr(32))[-200:]}")
    return rows, wall

# --- obscura CLI (binaire direct, sa voie native scrape):
def obscura_all():
    code = """
import sys, json, time, subprocess
from pathlib import Path
BIN = Path("/tmp/fusion-obscura/obscura")
assert BIN.exists(), f"binaire obscura absent: {BIN}"
urls = json.load(sys.stdin)
out = []
for u in urls:
    t0 = time.monotonic()
    try:
        p = subprocess.run([str(BIN), "scrape", u, "--stealth", "--obey-robots",
                            "--timeout", "12", "--format", "json", "-e",
                            "document.documentElement.outerHTML", "-q"],
                           capture_output=True, text=True, timeout=40)
        ms = (time.monotonic()-t0)*1000
        ok, body, eng = False, "", "obscura"
        try:
            parsed = json.loads(p.stdout or "{}")
            res = parsed.get("results") or []
            if res:
                body = res[0].get("eval") or ""
                ok = bool(body.strip())
        except Exception:
            pass
        out.append({"url": u, "ok": ok, "ms": round(ms,1), "len": len(body),
                    "engine": eng, "body_head": body[:500],
                    "err": "" if ok else (p.stdout or p.stderr or "")[:60]})
    except subprocess.TimeoutExpired:
        out.append({"url": u, "ok": False, "ms": round((time.monotonic()-t0)*1000,1),
                    "len": 0, "engine": "obscura", "body_head": "", "err": "timeout"})
print(json.dumps(out, default=str))
"""
    t0 = time.monotonic()
    p = subprocess.run([VE, "-c", code], input=json.dumps(CORPUS), capture_output=True,
                       text=True, timeout=1800, env=ENV)
    wall = round((time.monotonic()-t0),1)
    if p.returncode != 0:
        raise RuntimeError(f"subprocess scrapling rc={p.returncode}: {(p.stderr or chr(32))[-200:]}")
    try:
        rows = json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        raise RuntimeError(f"parse fail rc={p.returncode} stdout[:200]={p.stdout[:200]} stderr={(p.stderr or chr(32))[-200:]}")
    return rows, wall

# --- agent reach / jina (8 threads = leur usage recommandé):
def jina_one(url):
    t0 = time.monotonic()
    try:
        p = subprocess.run(["curl","-s","-m","30",f"https://r.jina.ai/{url}"],
                           capture_output=True, text=True, timeout=40)
        ms = (time.monotonic()-t0)*1000
        body = p.stdout or ""
        ok = p.returncode == 0 and len(body) > 120 and not body.startswith('{"data":null')
        return {"url": url, "ok": ok, "ms": round(ms,1), "len": len(body),
                "engine": "jina-reader", "body_head": body[:500],
                "err": "" if ok else body[:60]}
    except Exception as e:
        return {"url": url, "ok": False, "ms": round((time.monotonic()-t0)*1000,1),
                "len": 0, "engine": "jina-reader", "body_head": "", "err": str(e)[:60]}

def jina_all():
    t0 = time.monotonic()
    with ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(jina_one, CORPUS))
    return rows, round(time.monotonic()-t0,1)

def dist(ms_list):
    ms = sorted(m for m in ms_list if m)
    if not ms: return None
    return {"n": len(ms), "median": round(statistics.median(ms),1),
            "p90": round(ms[int(len(ms)*.9)-1],1), "p95": round(ms[int(len(ms)*.95)-1],1),
            "max": round(ms[-1],1), "mean": round(statistics.fmean(ms),1)}

def score(rows):
    """ok = contenu RÉEL vérifié (signature) — pas ok=True naïf."""
    good, honest_fail, liar = 0, 0, 0
    per = []
    for r in rows:
        host = r["url"].split("//")[1].split("/")[0]
        sig = SIGS.get(host)
        body = r.get("body_head","")
        sig_ok = (not sig) or (sig.lower() in body.lower())
        if r["ok"] and (r.get("len",0) > 200) and sig_ok:
            good += 1; verdict = "VRAI"
        elif r["ok"] and r.get("len",0) > 200 and not sig_ok:
            verdict = "VRAI(sans-sig)"  # signature trop stricte = pas menteur
            good += 1
        elif r["ok"]:
            verdict, liar = "MENTEUR", liar+1
        else:
            verdict, honest_fail = "échec-honnête", honest_fail+1
        per.append({"url": r["url"], "ok": r["ok"], "len": r.get("len",0),
                    "ms": r.get("ms"), "engine": r.get("engine"), "verdict": verdict})
    return {"real_ok": good, "honest_fail": honest_fail, "liars": liar, "per": per}

out = {"at": datetime.now(timezone.utc).isoformat(), "corpus": N, "tools": {}}
for name, fn in [("oscurapling v3.3.4 (route auto)", ours_all),
                 ("agent-reach v1.5.0 (Jina Reader)", jina_all),
                 ("scrapling 0.4.15 (Fetcher+Stealth fb)", scrapling_all),
                 ("obscura CLI 0.2.3 (scrape natif)", obscura_all)]:
    print(f"== {name} ...", flush=True)
    try:
        rows, wall = fn()
        s = score(rows)
        ms_ok = [r["ms"] for r in rows if r.get("ok") and r.get("ms")]
        out["tools"][name] = {"real_ok": s["real_ok"], "honest_fail": s["honest_fail"],
                              "liars": s["liars"], "wall_s": wall, "dist": dist(ms_ok),
                              "per": s["per"], **({} if not s["liars"] else {"liar_rows": [r for r in s["per"] if r["verdict"]=="MENTEUR"]})}
        print(f"   → real_ok {s['real_ok']}/{N} honest_fail {s['honest_fail']} liars {s['liars']} wall {wall}s dist {dist(ms_ok)}")
    except Exception as e:
        out["tools"][name] = {"error": str(e)[:200]}
        print("   ERREUR:", str(e)[:200])
Path("/home/bob/big_versus_results.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print("\nRÉSUMÉ FINAL:")
for name, d in out["tools"].items():
    if "error" in d:
        print(f"  {name}: ERREUR {d['error']}")
        continue
    print(f"  {name:42s} real {d['real_ok']}/{N} + lieurs {d['liars']} + échecs {d['honest_fail']} | wall {d['wall_s']}s | {d['dist']}")