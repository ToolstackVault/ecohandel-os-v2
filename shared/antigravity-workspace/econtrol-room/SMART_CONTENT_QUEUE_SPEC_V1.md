# Smart Content Queue Spec v1

## Doel
De Smart Content Queue is de redactionele en commerciële beslismotor van EcoHandel. Het systeem bepaalt niet alleen *welke content we kunnen maken*, maar vooral *welke content nu de meeste business impact heeft*.

De queue moet voelen als een slimme operator:
- ziet kansen
- weegt commerciële waarde tegen SEO-kans af
- bewaakt bestaande content
- voorkomt random contentproductie
- ondersteunt Jean Clawd bij prioritering

---

## Kernprincipe
De Smart Content Queue is **geen simpele backlog**.
Het is een **continu scorende prioriteitenmotor**.

De queue combineert signalen uit:
- Google Search Console
- Google Ads / commerciële data
- Shopify / productfocus
- bestaande contentdekking
- concurrentie en SERP gaps
- trends / nieuws / actualiteit
- refresh-signalen uit bestaande pagina's
- handmatige businessinput van Milan / Jean

Uitkomst:
- top 5 nu doen
- top 10 in voorbereiding
- refresh eerst
- park later
- kill/noise eruit

---

## Hoofddoelen
1. **Omzet ondersteunen**
2. **SEO-kansen sneller benutten**
3. **EcoHandel als specialist positioneren**
4. **Bestaande content actief onderhouden**
5. **Jean minder laten zoeken, meer laten beslissen**

---

## Content types binnen de queue
Iedere queue entry krijgt exact één primary type:

### 1. Money Page
Doel: directe koopintentie / keuzehulp / vergelijking / review / productondersteuning

Voorbeelden:
- Deye batterij vergelijken
- beste thuisbatterij voor dynamisch contract
- Deye vs Marstek
- welke omvormer past bij thuisbatterij

### 2. Support SEO Page
Doel: vragen beantwoorden die koopintentie ondersteunen

Voorbeelden:
- werkt een thuisbatterij zonder zonnepanelen
- 1-fase of 3-fase thuisbatterij
- wat betekent peak shaving
- verschil tussen hybride en retrofit

### 3. Authority Page
Doel: EcoHandel als specialist neerzetten

Voorbeelden:
- complete gids thuisbatterijen
- complete gids Deye ecosysteem
- salderen, teruglevering en opslag uitgelegd

### 4. Category Booster
Doel: categorie/collectie SEO en interne linkkracht versterken

Voorbeelden:
- ondersteunende pagina rondom Deye omvormers
- clusterpagina voor thuisbatterij use-cases

### 5. Refresh Task
Doel: bestaand bezit verbeteren

Voorbeelden:
- lage CTR verbeteren
- verouderde info bijwerken
- interne links uitbreiden
- FAQ/schema verrijken

---

## Business goals labels
Iedere entry krijgt exact één hoofdlabel:
- `revenue_direct`
- `revenue_support`
- `authority`
- `maintenance`
- `strategic_positioning`

Waarom dit belangrijk is:
Als een onderwerp geen duidelijke businessrol heeft, hoort het niet bovenaan te staan.

---

## Prioriteitslabels
Iedere entry krijgt één prioriteitsklasse:
- `P1` — omzet-direct
- `P2` — koopondersteunend
- `P3` — SEO / authority
- `P4` — maintenance
- `P5` — nice-to-have / watchlist

### Harde regel
De top van de queue mag nooit volledig uit P3 bestaan. Er moet balans zijn tussen omzet en SEO.

---

## Statusmodel
Elke entry heeft één status:
- `new` — nieuw gevonden, nog niet beoordeeld
- `scored` — gescoord maar nog niet gekozen
- `queued` — actief in de Smart Content Queue
- `assigned` — toegewezen aan agent of Jean
- `drafting` — in uitwerking
- `validation` — fact/product check of reviewfase
- `ready` — klaar voor volgende actie / publicatie
- `refresh_needed` — bestaande content moet eerst worden bijgewerkt
- `parked` — nu niet doen, later mogelijk nuttig
- `killed` — afgewezen / ruis / geen businesswaarde
- `done` — afgerond

---

## Queue lanes
De Smart Content Queue moet visueel en logisch in lanes zijn verdeeld.

### Lane 1 — Top 5 Now
De vijf hoogste prioriteiten die nu aandacht verdienen.

### Lane 2 — Next Up
Onderwerpen met hoge waarde maar nog niet direct aan de beurt.

### Lane 3 — Refresh First
Bestaande content die vóór nieuwe creatie aandacht nodig heeft.

### Lane 4 — Watchlist
Interessant maar wacht op data, timing of capaciteit.

### Lane 5 — Killed / Noise
Onderwerpen die bewust worden weggegooid zodat de queue schoon blijft.

---

## Scoringsmodel
Iedere contentkans krijgt een totaalscore op 100 punten.

## Score-as 1 — Omzetpotentie (0–25)
Vragen:
- helpt dit direct een product of categorie verkopen?
- ondersteunt het koopbeslissingen?
- past het bij huidige focusproducten?
- ondersteunt het installateurs of eindklanten met commerciële intentie?

### Richtlijn
- 21–25 = zeer hoge commerciële waarde
- 16–20 = sterke koopondersteuning
- 8–15 = indirect commercieel nuttig
- 0–7 = vooral informatief

---

## Score-as 2 — SEO kans (0–20)
Vragen:
- is er bestaande vraag / impressions / querypotentieel?
- lijkt de SERP haalbaar?
- hebben we hier al signalen uit GSC of trends?
- is de intentie helder genoeg voor ranking?

### Richtlijn
- 16–20 = sterke rankingkans
- 10–15 = degelijk potentieel
- 5–9 = mogelijk, maar minder zeker
- 0–4 = zwakke SEO-case

---

## Score-as 3 — Commerciële intentie (0–15)
Vragen:
- zit de zoeker dicht op aankoop / vergelijking / keuze?
- is de zoekvraag transactioneel of high-intent informatief?
- ondersteunt dit direct het midden/onderste stuk van de funnel?

### Richtlijn
- 13–15 = bottom-of-funnel
- 9–12 = mid-funnel met duidelijke koopkoppeling
- 4–8 = informatief met beperkte koopintentie
- 0–3 = vooral awareness

---

## Score-as 4 — Productdekking / clusterfit (0–15)
Vragen:
- sluit dit aan op prioriteitsproducten?
- vult het een duidelijk contentgat in een cluster?
- helpt dit topical authority rond Deye, batterijen, omvormers, opslag, EV?

### Richtlijn
- 13–15 = exact in kerncluster en duidelijk gat
- 8–12 = goede fit
- 4–7 = randrelevant
- 0–3 = te ver van kernfocus

---

## Score-as 5 — Actualiteit / momentum (0–10)
Vragen:
- speelt dit nu vanwege marktontwikkeling, regelgeving, trends of nieuws?
- neemt het momentum af als we wachten?

### Richtlijn
- 8–10 = nu relevant, snel pakken
- 4–7 = actueel genoeg
- 1–3 = weinig tijdsdruk
- 0 = evergreen zonder momentumfactor

---

## Score-as 6 — Autoriteitswaarde (0–10)
Vragen:
- maakt dit EcoHandel geloofwaardiger als specialist?
- helpt dit de merkpositionering?
- versterkt dit vertrouwen of expertise in een winstgevend cluster?

### Richtlijn
- 8–10 = sterk authority effect
- 4–7 = nuttige expertpositie
- 1–3 = beperkt effect
- 0 = nauwelijks authority-impact

---

## Score-as 7 — Uitvoerbaarheid / frictie (0–5)
Vragen:
- kunnen we dit snel en goed uitvoeren?
- hebben we genoeg kennis/data/productbasis?
- is het makkelijk te valideren?

### Richtlijn
- 5 = snel uitvoerbaar
- 3–4 = haalbaar met beperkte extra effort
- 1–2 = frictie of afhankelijkheden
- 0 = nu nog niet rijp

---

## Penalties
Niet alles hoeft positief te scoren. We gebruiken ook aftrek.

### Penalty 1 — Content conflict (-10)
Als onderwerp conflicteert met bestaande pagina's of cannibalisatie geeft.

### Penalty 2 — Lage bewijsbasis (-10)
Als we de inhoud niet goed kunnen onderbouwen.

### Penalty 3 — Zwakke businessfit (-15)
Als onderwerp wel verkeer kan trekken, maar ver van EcoHandel's focus staat.

### Penalty 4 — Hoge onderhoudslast (-5)
Als onderwerp snel veroudert of veel nazorg vraagt.

---

## Eindscoreformule
`total_score = sum(score_axes) - sum(penalties)`

### Aanbevolen interpretatie
- **80–100** = direct serieuze kandidaat voor Top 5
- **65–79** = sterke queue-kandidaat
- **50–64** = watchlist / verdieping nodig
- **35–49** = alleen doen bij specifieke reden
- **0–34** = meestal kill of parkeren

---

## Beslisregels voor Top 5
De Top 5 is niet simpelweg de hoogste vijf scores. Er gelden balansregels.

### Top 5 balansregels
Minimaal:
- 2 items met `revenue_direct` of `revenue_support`
- maximaal 1 puur authority-item zonder directe koopkoppeling
- minimaal 1 refresh/upgrade-item als er duidelijke bestaande kansen liggen
- niet meer dan 2 onderwerpen uit exact hetzelfde microtopic tenzij het een bewuste clusterpush is

### Jean override
Jean mag altijd afwijken als:
- er een strategisch momentum is
- Milan directe commerciële focus wil
- een onderwerp businesskritisch is ondanks lagere score

---

## Verplichte velden per queue entry
Elke entry moet deze velden hebben:

- `id`
- `title`
- `slug_candidate`
- `content_type`
- `business_goal`
- `priority_label`
- `status`
- `lane`
- `primary_cluster`
- `secondary_cluster`
- `target_audience`
- `search_intent`
- `primary_product_focus`
- `supporting_product_focus`
- `signal_sources`
- `why_now`
- `recommended_format`
- `recommended_next_step`
- `owner`
- `created_at`
- `updated_at`
- `confidence`
- `notes`

### Scorevelden
- `score_revenue`
- `score_seo`
- `score_commercial_intent`
- `score_cluster_fit`
- `score_actuality`
- `score_authority`
- `score_feasibility`
- `penalty_conflict`
- `penalty_evidence`
- `penalty_business_fit`
- `penalty_maintenance`
- `total_score`

### Optionele velden
- `related_urls`
- `related_queries`
- `competitors_seen`
- `refresh_target_url`
- `dependencies`
- `validation_required`
- `assigned_agent`
- `learning_flags`

---

## Doelgroepen
Iedere entry krijgt één hoofd-doelgroep:
- `b2c_homeowner`
- `b2c_advanced_buyer`
- `installer`
- `b2b_business`
- `mixed`

Waarom:
EcoHandel heeft meerdere publieken. Zonder doelgroep wordt content te vaag.

---

## Kernclusters
Gebruik vaste clusters zodat topical authority zichtbaar wordt.

### Aanbevolen clusters v1
- `deye_ecosystem`
- `home_batteries`
- `hybrid_inverters`
- `microinverters`
- `ev_charging`
- `solar_panels`
- `installation_decisions`
- `dynamic_energy_contracts`
- `net_congestion`
- `commercial_storage`
- `smart_energy_management`

---

## Signal sources
Iedere entry moet kunnen terugwijzen naar zijn bron. Gebruik labels:
- `gsc`
- `ga4`
- `ads`
- `shopify`
- `competitor_serp`
- `trend`
- `news`
- `manual_jean`
- `manual_milan`
- `refresh_scan`
- `support_question`
- `forum_reddit`

---

## Recommended next steps
Mogelijke vervolgacties:
- `research_deeper`
- `queue_now`
- `refresh_existing`
- `create_new_page`
- `expand_existing_page`
- `fact_check_first`
- `wait_for_data`
- `kill`

---

## Smart Queue modes
Niet elke run heeft hetzelfde doel. Gebruik modes.

### Mode 1 — Revenue Push
Geeft extra gewicht aan omzet, koopintentie en productfocus.

### Mode 2 — SEO Growth
Geeft extra gewicht aan rankingkans en clusterdekking.

### Mode 3 — Authority Build
Geeft extra gewicht aan autoriteitswaarde en topical depth.

### Mode 4 — Maintenance First
Geeft extra gewicht aan refresh-signalen en bestaande kansen.

### Standaardmodus
Gebruik een hybride modus met revenue-first bias.

---

## Refresh integratie
De Smart Content Queue moet niet blind alleen nieuwe onderwerpen pushen.

### Regels
1. Als een bestaande pagina met impressions en lage CTR sneller resultaat geeft dan een nieuw artikel, dan krijgt refresh voorrang.
2. Als een nieuwe pagina sterk zou cannibaliseren op een bestaande pagina, dan moet eerst refresh of merge worden overwogen.
3. Refresh-taken kunnen in Top 5 staan.

### Refresh issue types
- `low_ctr_high_impressions`
- `content_outdated`
- `missing_internal_links`
- `weak_cta`
- `weak_formatting`
- `missing_faq`
- `missing_schema`
- `misaligned_search_intent`
- `thin_supporting_content`

---

## Kill rules
Niet elk onderwerp verdient aandacht. Killed items zijn een feature, geen verlies.

### Kill wanneer:
- businessfit zwak is
- te generiek is
- buiten kernclusters valt
- te weinig bewijs heeft
- kans op cannibalisatie groot is zonder duidelijke winst
- topic vooral vanity verkeer trekt

### Voordeel
Een schone queue maakt de machine sneller.

---

## Agentrollen in relatie tot de queue

### Scout Agent
- vult `new`
- levert signalen en ruwe kansen

### Strategist Agent
- zet `new` om naar `scored`
- adviseert lane, score en next step

### Refresh Agent
- vult `refresh_needed`
- levert upgrade-items en bewijs

### Jean
- beslist of item naar `queued`, `assigned`, `parked` of `killed` gaat
- mag scores overrulen
- bepaalt uiteindelijke Top 5

---

## JSON voorbeeldstructuur
```json
{
  "id": "SCQ-20260326-001",
  "title": "Beste thuisbatterij voor dynamisch energiecontract",
  "slug_candidate": "beste-thuisbatterij-dynamisch-contract",
  "content_type": "money_page",
  "business_goal": "revenue_direct",
  "priority_label": "P1",
  "status": "queued",
  "lane": "top_5_now",
  "primary_cluster": "home_batteries",
  "secondary_cluster": "dynamic_energy_contracts",
  "target_audience": "b2c_homeowner",
  "search_intent": "commercial_investigational",
  "primary_product_focus": ["home_batteries"],
  "supporting_product_focus": ["smart_energy_management"],
  "signal_sources": ["gsc", "trend", "manual_jean"],
  "why_now": "Sterke koopintentie, marktactueel en direct gekoppeld aan thuisbatterij-conversie.",
  "recommended_format": "comparison_guide",
  "recommended_next_step": "queue_now",
  "owner": "jean",
  "assigned_agent": null,
  "created_at": "2026-03-26T21:30:00Z",
  "updated_at": "2026-03-26T21:30:00Z",
  "confidence": 0.86,
  "score_revenue": 24,
  "score_seo": 16,
  "score_commercial_intent": 15,
  "score_cluster_fit": 15,
  "score_actuality": 8,
  "score_authority": 7,
  "score_feasibility": 5,
  "penalty_conflict": 0,
  "penalty_evidence": 0,
  "penalty_business_fit": 0,
  "penalty_maintenance": 0,
  "total_score": 90,
  "notes": "Sterke P1-kandidaat voor Top 5"
}
```

---

## Econtrol Room UI-blokken
De Smart Content Queue moet zichtbaar worden in deze blokken:

### 1. Top 5 Now
- titel
- score
- contenttype
- why now
- businessgoal
- next step

### 2. Next Up
- top 6–15
- compact overzicht

### 3. Refresh First
- bestaande pagina's met grootste kans
- issue type + severity

### 4. Queue Health
- aantal P1/P2/P3/P4
- teveel authority?
- te weinig refresh?
- te veel items in parked?

### 5. Source Mix
- hoeveel items komen uit GSC
- hoeveel uit trends
- hoeveel uit manual business input
- hoeveel uit refresh

### 6. Agent Status
- laatste scout run
- laatste strategist run
- laatste refresh run
- fouten / stale data / confidence warnings

---

## Queue health rules
De queue moet zichzelf bewaken.

### Gezond als:
- minimaal 5 sterke items in `queued`
- minimaal 2 P1/P2 items in topsegment
- minimaal 1 refresh-item actief
- niet meer dan 25% low-confidence items
- niet meer dan 20% van de queue in exact één subcluster, tenzij dat bewust is

### Ongezond als:
- top 5 alleen SEO/authority is
- teveel items op watchlist blijven hangen
- refresh structureel genegeerd wordt
- signalen niet meer vers zijn

---

## Freshness rules
Niet alle signalen blijven lang waardevol.

### Veroudering
- trend/news signalen: snel vervallen
- GSC query kansen: periodiek herbeoordelen
- refresh-signalen: vervallen zodra issue is opgelost
- manual_milan signalen: hoge prioriteit tot Jean ze verwerkt

### Aanbevolen
- geef ieder item een `stale_after_days`
- stale items automatisch herbeoordelen of downgraden

---

## Self-improving hooks voor de queue
De Smart Content Queue moet zelf ook slimmer worden.

### Wat loggen we als learning?
- onderwerpen die hoog scoorden maar zwak presteerden
- refresh-items die onverwacht veel winst gaven
- signaalbronnen die vaak ruis geven
- scoringsregels die te agressief of te slap blijken
- clusterlabels die te grof zijn

### Wat doen we met die learnings?
1. run note
2. herhaling? -> `.learnings/`
3. bewezen patroon? -> update spec, AGENTS.md of scoremodel

---

## Eerste implementatiefases

### Fase 1 — spec & structuur
- markdown spec afronden
- JSON schema bepalen
- opslagpaden vastzetten

### Fase 2 — handmatig gevoede v1
- Jean / agents vullen eerste 20–30 entries
- top 5 handmatig valideren
- scores testen op gevoel + businessfit

### Fase 3 — halfautomatisch
- Scout / Refresh output automatisch laten landen
- Strategist scorevoorstel laten doen
- Jean reviewt en fiatteert

### Fase 4 — Econtrol Room integratie
- top 5 live in dashboard
- refresh lane zichtbaar
- queue health metrics zichtbaar

---

## Harde ontwerpregels
1. De queue dient business, niet alleen verkeer.
2. Hoge score betekent niet automatisch publiceren.
3. Refresh mag nieuwe content verslaan.
4. Jean houdt override-recht.
5. Killed items zijn waardevol voor focus.
6. Self-improvement hoort in de queue-logica zelf, niet alleen ernaast.

---

## Aanbevolen volgende documenten
Na deze spec horen idealiter nog:
- `SMART_CONTENT_QUEUE_SCHEMA.json`
- `SMART_CONTENT_QUEUE_EXAMPLES.json`
- `REFRESH_QUEUE_SCHEMA.json`
- `AGENT_OUTPUT_CONTRACTS.md`
- `TOPIC_SCORING_PLAYBOOK.md`

---

## Samenvatting
De Smart Content Queue v1 is:
- een scoremotor
- een prioriteitenlaag
- een balanssysteem tussen omzet, SEO en onderhoud
- een bron voor de Econtrol Room
- een self-improving beslislaag voor EcoHandel

Niet een lijstje met ideeën, maar een stuurwiel.
