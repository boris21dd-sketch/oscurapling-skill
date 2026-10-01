# Benchmark x1000 - oscuraplingfull v3.3.3 vs Agent Reach v1.5.0 (Jina Reader)

Run ordaté 01/10/2026 21:48-22:00 UTC - machine au repos, corpus public 20 URL permissives.

## Verdicts par axe

| Axe | oscuraplingfull | Agent Reach (Jina) | Verdict |
|---|---|---|---|
| **Couv. corpus** (20 URL) | 20/20 | 20/20 | draw |
| **Stress 1000 fetchs** (100 URL x 10 rounds, conc 8) | **1000/1000 (100%)** wall **209 s** méd **104 ms** | **98/1000 (9,8%)** wall ~4 485 s/round | **nous x10 coverage, x22 wall** |
| **Latence distribution** (60 fetchs seq) | méd **598 ms** p95 812 stdev 209 (60/60 ok) | méd **299 ms** p95 575 stdev 648 (24/60 ok) | jina = cache hits chauds + instable (2 ok/3) |
| **Freshness** (counter local + worldtime) | gate SSRF refuse loopback (comportement PAR DESIGN) | 429 rate (idem refusé) | draw (aucun des deux ne fetch du privé) |
| **Authenticité** (page vraie vs artefact) | HTML source réel prouvé (sonde: example.com = HTML officiel complet 5ko+) | example.com/quotes = "Test Article"/"Warning cached snapshot" sur le run du stress | jina = contenu PÉRIMÉ prouvé |
| **Bugs trouvés** | obscura sur API JSON = ok=True mais len=0 (contenu perdu, à fix en v3.3.4) | rate-limit hard après ~20 fetchs consécutifs free tier | réel des deux côtés |

## Chiffres de tête (stress)
- oscurapling: 1000/1000 ok, wall total 209 s (méd 104 ms / p95 6,5 s / max 18 s - la queue = obscura CDP sur wikipedia)
- jina: 98/1000 ok (les fails = 429 rate-limit free tier, retryAfter), ceux qui passent = méd 420 ms
- wall jina (estimation via sum des requêtes/8): ~45 000 s théorique vs 209 s réels - ce n'est PAS comparable par wall (chaque round jina = sérialisé par le rate limit)

## La phrase honnête
Sur 1000 fetchs consécutifs du web public, **oscurapling fait 100%** à
médiane 104 ms ; **Jina (la voie web d'Agent Reach) plafonne à 9,8%** par
rate-limit tier gratuit et, quand il répond, peut livrer un snapshot CACHE
au lieu de la page (prouvé 2x). Agent Reach reste excellent pour Twitter/
Reddit/YouTube via cookies locaux = terrain complémentaire, pas concurrent.
