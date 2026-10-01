# DISCLAIMER & LEGAL NOTICE (international)

**Read before using, forking, or redistributing anything in this repository.**

## 1. Nature of the software

`oscurapling` and this skill are dual-use technical frameworks for automated HTTP
content retrieval — functionally comparable to `curl`, `wget` or headless-browser
automation. They execute the instructions of the person operating them. The
author ships code; the operator makes choices. Every anti-bot, stealth or
rendering capability is provided to access **public content the OPERATOR IS
AUTHORIZED to access**, and to keep failed fetches from becoming silent data
loss.

## 2. Warranty disclaimer

The software is provided **"AS IS", WITHOUT WARRANTY OF ANY KIND**, express or
implied, including merchantability, fitness for a particular purpose and
non-infringement. Accuracy of fetched content, continuity of third-party
websites, and fitness for your use case are **never** guaranteed.

## 3. Limitation of liability & indemnification

To the maximum extent permitted by applicable law, in no event shall the author
or copyright holder be liable for any claim, damages, data loss, legal exposure,
regulatory fine or other liability arising from use of the software.

**By using, modifying or redistributing this software, you agree to indemnify,
defend and hold harmless the author and contributors from any claim, demand,
action, fine, or expense (including reasonable legal fees) arising out of or
related to your use or misuse of the software.**

## 4. Lawful use is YOUR responsibility — in every jurisdiction

You are solely responsible for verifying that your use complies with all laws,
regulations, and third-party rights applicable **to you and to the targets you
fetch** — including, without limitation:

| Jurisdiction | Examples of regimes you must respect (non-exhaustive) |
|---|---|
| EU | GDPR, ePrivacy Directive, InfoSoc Directive (2001/29/EC), DSA |
| France | RGPD, Loi Informatique et Libertés, LCEN, Code pénal art. 323-1/323-2 (accès/traveau frauduleux), CPI L.335-2 |
| USA | CFAA (18 U.S.C. §1030), DMCA §1201 (anti-circumvention), CCPA/CPRA, state anti-bot laws |
| UK | Computer Misuse Act 1990, UK GDPR |
| Germany | StGB §202c ("Hackerparagraph"), BDSG |
| Canada | Criminal Code s.342.1, PIPEDA |
| Australia | Cybercrime Act 2001 (s.477), Privacy Act |
| China | Cybersecurity Law, PIPL |
| Brazil | LGPD |
| India | IT Act s.43/66 |
| Japan | Act on Prohibition of Unauthorized Computer Access, APPI |

This list is illustrative, constantly evolving, and **never** a substitute for
your own legal verification.

## 5. Personal data

If content fetched through this skill contains personal data, **you are the sole
data controller** (GDPR art. 4(7) and equivalents) for that processing. The
author is neither a controller nor a processor for your fetches, receives no
data from your fetches (no telemetry, no call-home), and provides no legal basis
for your processing. Establishing your lawful basis (GDPR art. 6) is **your**
obligation.

## 6. Not legal advice

The author is not a lawyer. Nothing in this repository — including this file —
is legal advice, counsel, or an opinion on the legality of any specific use.
Consult a qualified lawyer in your jurisdiction for your actual use case.

## 7. Non-affiliation & trademarks

This project is **not affiliated with, endorsed by, or sponsored by** Anthropic,
the Scrapling project, the Obscura project, D4Vinci, h4ckf0r0day, GitHub, or any
of their owners. Scrapling, Obscura, Claude, Anthropic and all third-party marks
are property of their respective owners, used here **for description and
attribution only** (nominative/fair use). The pinned engine is a private fork —
bugs there are not bugs of upstream projects.

## 8. Capacity & restricted parties

Do not use this software if you are under 18 (or the age of legal capacity where
you live), or if you are subject to US/EU/UK sanctions, export restrictions, or
are a listed restricted party.

## 9. Precedence & severability

If any provision here is void under your local law, the remainder survives in
full. The most protective applicable provision prevails. Usage of the repo
after an update of this file constitutes acceptance of the updated version.

## 10. Report abuse

Suspected illegal use of this repository: open a GitHub issue titled
`[abuse]` or contact the repository owner via GitHub. Vectors of misuse will be
documented and, where feasible, technically blocked in future releases.

## 11. Governing law, forum & dispute resolution

**Any dispute** relating to this software, its use or misuse — including any
claim of harm arising from another user's usage — is governed by **French law**
(loi française), **excluding** its conflict-of-laws rules and the UN CISG,
and falls under the **exclusive jurisdiction of the courts of the author's
domicile in France**, except where mandatory local consumer law grants you a
different forum. **Users of the software agree to resolve all disputes by final
and binding individual arbitration under French applicable rules, and to
expressly waive any class, collective or representative action** to the
fullest extent permitted by their local law (no waiver will be asserted where
void: e.g. certain EU consumer claims).

**Explicit no-waiver honesty note:** the author recognizes that click-through
or browsewrap terms may be **hard to enforce against anonymous GitHub users**
in some jurisdictions (notably US courts on indemnity by mere use). This clause
is therefore a **maximum-reasonable protection, not magic**: combined with
§3 (indemnity), §4 (user responsibility) and §10 (abuse channel), it forms the
strongest non-lawyer shield available; nothing can make a private individual
literally "unattackable" against a bad-faith actor's own legal costs.

## Appendix A — United States — detailed notice (non-exhaustive; informative only)

### A.1 — Computer fraud: CFAA (18 U.S.C. § 1030)
"Access without authorization / exceeding authorized access." After *Van Buren
v. United States*, 593 U.S. 374 (2021), fetching **publicly available** web
pages generally falls outside CFAA's "gates-down" reading — but that comfort
does NOT extend to: credential-protected or authenticated portions, systems
behind technical access barriers, or **state** computer-crime statutes that may
be broader (e.g., Cal. Penal Code § 502). Do not rely on *hiQ Labs v.
LinkedIn*: the Ninth Circuit's CFAA holding was undercut by the 2022 jury
verdict for LinkedIn on contract claims (case settled); **no US court has ever
declared scraping "legal in general"** — anyone telling you otherwise is
selling something.

### A.2 — Anti-circumvention: DMCA § 1201 (17 U.S.C.)
Circumventing an "effective technological measure" controlling access to a
copyrighted work (login walls, obfuscation, sophisticated bot checks) is an
independent violation, with **criminal** exposure where done for commercial
advantage or private financial gain; triennial Library of Congress exemptions
are narrow (security research, preservation, etc.). This skill's stealth
engines present browser-grade fingerprints so that PUBLIC pages a normal
browser can open are retrievable; **if a target's bot-wall is argued to be a
§ 1201 TPM, the operator assumes that legal risk** — never the author.

### A.3 — Intermediary defenses: do not overread § 230
47 U.S.C. § 230 protects "interactive computer services" hosting third-party
speech. A code author shipping a fetching tool **cannot safely rely on it**;
this disclaimer makes no such claim.

### A.4 — Privacy: federal & state (operator = "business")
CCPA/CPRA (California), Virginia CDPA, Colorado CPA, Connecticut CTDPA, Utah
UCPA, Washington My Health My Data, Nevada SB 370: scraped content containing
residents' personal information can make the **operator** a "business" (or
"service provider") with notice, deletion, opt-out ("sale"/"share" is broadly
defined) and sensitive-data duties; penalties accrue **per violation**.
**Illinois BIPA (740 ILCS 14/)**: biometric identifiers (faces, voiceprints)
without written consent = **private right of action, $1,000-$5,000 statutory
damages per violation** — the US class-action magnet; the engines never build
biometric templates and operators must not either. **FTC Act § 5** (unfair or
deceptive practices): misrepresenting identity/purpose to sites or data
subjects, or repurposing scraped data contrary to posted notices, has fed
multiple FTC consent decrees (data-broker line).

### A.5 — IP contracts & related torts
Copyright: fair use (17 U.S.C. § 107) is a **four-factor defense**, not a
license — "it was public" ≠ right to republish (cf. *AP v. Meltwater*). Trade
secrets: DTSA (18 U.S.C. § 1836) for marked/confidential material. Right of
publicity (Cal. Civ. Code § 3344 + state torts) for names/likenesses.
*Trespass to chattels*/server-burden theories (the *eBay v. Bidder's Edge*
line) and **breach of the site's Terms of Service** (a contract claim
independent of CFAA) remain live theories against aggressive scrapers.
**CAN-SPAM (15 U.S.C. § 7704)** and **TCPA (47 U.S.C. § 227)**: harvesting
emails/phone numbers to send unsolicited messages is a **PROHIBITED USE** of
this software.

### A.6 — Export controls & sanctions
EAR/OFAC: providing the software to sanctioned persons or destinations, or for
listed end-uses, may violate US law; §8 binds US users equally.

### A.7 — Honest limits of this protection in the US (read twice)
(i) A French governing-law/forum clause does **not** strip US courts of
jurisdiction over US plaintiffs or US-targeted harm; it adds defense LAYERS
(forum non conveniens, arbitration motion) — it is not a wall.
(ii) Arbitration + class-action waivers bind US consumers only when embedded
in a properly formed **clickwrap** (cf. *AT&T Mobility v. Concepcion*);
browsewrap terms are routinely **not** enforced against anonymous GitHub users.
(iii) § 230, the First Amendment (code-as-speech, *Bernstein v. DOJ*) and the
dual-use doctrine (substantial non-infringing uses, the Sony/BetMax line) are
real defenses — that cost real money to litigate. The only genuinely
risk-minimizing strategy for a private author is layered: technical gates +
kill switch + abuse channel + compliance-by-default + fast takedown response +
**never marketing evasion**. This Appendix + §§1-11 is the maximum defensible
stack for a non-lawyer; it is shield depth, not a guarantee.

## 12. No inducement, no secondary liability (author-aiming theories)

**Nothing in this repository, its documentation, its examples or its
benchmarks constitutes encouragement, inducement, authorization, facilitation,
or assistance toward any unlawful use.** The author does not control, direct,
monitor or benefit from any user's fetches (no telemetry), and disclaims all
derivative or secondary liability theories aimed at tool authors, including
without limitation: inducement (*MGM Studios v. Grokster*), contributory and
vicarious liability, aiding-and-abetting, civil conspiracy, tortious
interference with third-party terms of service, and negligence-based
oversight claims. The anti-bot engines exist to retrieve **public pages any
ordinary browser can open**, the compliance defaults (robots, rate limits,
breakers, SSRF gates, kill switch) are the author's **affirmative steps in the
opposite direction**, marketing and documentation must never be read as
inviting evasion, and any user quoting this repo as "permission" misquotes it.

---

**Résumé (FR, non contractuel)** : logiciel à double usage fourni "en l'état",
sans garantie ; l'utilisateur est seul responsable de la légalité de son usage
dans son pays (RGPD, CFAA, CMA 1990, §202c StGB…) ; il s'engage à indemniser
l'auteur pour tout usage qu'il en ferait ; l'auteur n'est pas juriste — ceci
n'est pas un avis juridique ; aucune affiliation avec Anthropic/Scrapling/
Obscura ; usage interdit aux mineurs et parties sous sanctions ; Annexe A = réglementation
US détaillée (CFAA post-Van Buren, DMCA §1201, CCPA/CPRA, BIPA, FTC §5, CAN-SPAM/TCPA,
limites honnêtes des protections aux USA).