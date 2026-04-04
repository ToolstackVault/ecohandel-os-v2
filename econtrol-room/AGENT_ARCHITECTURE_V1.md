# EcoHandel Agent Architecture v2 (bestand blijft V1 voor compatibiliteit)

## Doel
Een lean EcoHandel Operating System waarin **Jean Clawd** de command/CEO-laag is, **één vaste Ops Agent** de machine runt, en specialist-agents alleen draaien wanneer hun oordeel echt waarde toevoegt.

---

## Kernprincipe
- **Jean Clawd** beslist prioriteit, tempo, kwaliteitsdrempel en go/no-go.
- **Ops Agent** beheert de operatie: scripts, crons, health, reruns, queue refresh en deploy.
- **Scripts** doen al het deterministische werk.
- **Specialist agents** komen alleen in beeld bij ambiguity, validatie of high-value denkwerk.
- **Publish** is een gecontroleerde Shopify-subflow voor EcoHandel, niet een vrije agent-actie.

---

## Architectuur in 3 lagen

### 1. Command Layer — Jean Clawd
Verantwoordelijkheden:
- businessimpact vertalen naar systeemprioriteiten
- Top 5 / refresh / publish-volgorde bepalen
- output reviewen
- approval gates bewaken
- learnings promoveren naar duurzame regels
- beslissen wanneer iets script, agent of handmatig moet zijn

Jean is de enige laag die definitief bepaalt:
- wat nu prioriteit krijgt
- wat live mag
- welke specialist-agent wordt ingeschakeld
- wanneer autonomie omhoog of omlaag gaat

---

### 2. Core Operating Layer — Ops Agent (vast)
**Rol:** operationele uitvoerder onder Jean

**Doet wel:**
- data refresh cycles aansturen
- scripts draaien en rerunnen
- cron-health bewaken
- queue/state bestanden bijwerken
- render/deploy flow aansturen
- failures signaleren
- publish subflow starten als task approved is
- status terugschrijven naar Econtrol Room

**Doet niet:**
- eigen roadmap bepalen
- zelfstandig Shopify live wijzigingen beslissen
- specialistische inhoudelijke claims valideren zonder trigger
- random agent-calls doen zonder duidelijke reden

**Output contract:**
- run_status
- completed_steps[]
- failed_steps[]
- next_actions[]
- health_flags[]
- usage_notes

**Waarom vast:**
- minder chaos
- minder usage
- centrale debugginglaag
- Jean blijft vrij voor checks, strategie en uitzonderingen

---

### 3. Specialist Layer — alleen op trigger

#### A. Content Strategist Agent
**Alleen voor:** topkandidaten met echte businessimpact

**Doet:**
- vertaalt ruwe signalen naar een scherpe contentrichting
- geeft rationale en aanbevolen format
- helpt bij why-now judgement

**Niet:** autonoom prioriteren of publiceren

---

#### B. SERP Gap Agent
**Alleen voor:** cluster-expansie, concurrentiedruk, onduidelijke gaten

**Doet:**
- analyse van topical gaps
- concurrentie/intent vergelijking
- ondersteunende pagina’s en contentclusters voorstellen

---

#### C. Fact & Product Agent
**Alleen voor:** money pages, productclaims, technische gevoeligheid

**Doet:**
- productspecificaties en claims controleren
- compatibiliteit / use-case logica valideren
- technische/commerciële onzin tegenhouden

---

#### D. Refresh Agent
**Alleen voor:** bestaande pagina’s met duidelijke performance/kwaliteitssignalen

**Doet:**
- refreshkansen beoordelen
- issue + aanbevolen fix structureren
- refresh zwaarder of lichter maken op basis van impact

---

## Wat géén vaste agents meer zijn

### Scout
Geen vaste AI-agent meer. Dit wordt primair een **script/source layer**:
- GSC pulls
- trends/news
- Shopify/productfocus
- concurrentiesignalen
- handmatige input

### Writer
Geen vaste always-on agent. Alleen oproepen als:
- onderwerp is goedgekeurd
- businessdoel helder is
- publishflow echt klaarstaat

---

## Scripts als echte motor
De volgende onderdelen horen script-first te zijn:

1. **Data ingest**
- GSC
- Ads
- Shopify/productfocus
- trends/news
- handmatige overrides

2. **Queue scoring**
- totaal scoremodel
- lane-verdeling
- penalties
- queue health
- source mix

3. **Health/state**
- agent-status
- cron-status
- stale warnings
- confidence mix
- learning-summary

4. **Render/deploy**
- queue + state naar Econtrol Room
- build vernieuwen
- live data verversen

5. **Publish subflow**
- alleen EcoHandel / Shopify
- alleen via bestaande publish skill/script
- alleen na expliciete go

---

## Cronmodel

### Frequent
- data refresh cron
- queue scoring cron
- render/deploy cron

### Dagelijks
- refresh scan cron
- ops audit cron

### Event-driven
- specialist-agent trigger
- publish subflow
- rerun bij failure

---

## Triggerregels voor specialist-agents
Een specialist-agent draait alleen wanneer ten minste één van deze waar is:
- hoge omzetkans
- lage confidence in scriptuitkomst
- conflict tussen signalen
- technische/commerciële validatie nodig
- cluster/intent is te ambigu voor rules-only

Anders geldt: **script is genoeg**.

---

## Shopify publish-regel
Voor EcoHandel blijft gelden:
- publish mag technisch onder de Ops Agent hangen
- maar alleen als gecontroleerde subflow
- en met approval gate zolang Milan geen bredere autonomie geeft

Dus:
- **ja** publish in het systeem
- **nee** geen vrije publish-bot

---

## Harde anti-chaos regels
1. Jean beslist, Ops voert uit.
2. Eerst scripts, dan pas agents.
3. Maximaal 1 vaste agent onder Jean in v2: de Ops Agent.
4. Specialist-agents alleen op trigger.
5. Publish blijft apart en gecontroleerd.
6. Learnings alleen promoveren als ze bewezen of terugkerend zijn.

---

## Aanbevolen foldermodel
`ecohandel/econtrol-room/`

- `scripts/` → deterministic flows
- `cron/` → schema + cron-bestanden
- `queue/` → Smart Content Queue + refresh queue
- `state/` → health, source mix, run status
- `agents/` → only triggered specialist outputs
- `build/` → render output
- `learn/` → verbeterlussen / fouten / proven patterns

---

## Bouwvolgorde

### Fase 1 — Operating system
- Ops Agent definitie
- scripts structureren
- cronflow vastzetten
- state/health standaardiseren

### Fase 2 — Live machine
- echte data ingest
- queue scoring op live signalen
- render/deploy automatiseren

### Fase 3 — Intelligence on top
- Content Strategist
- SERP Gap
- Fact & Product
- Refresh

### Fase 4 — Controlled production
- Shopify publish subflow
- approval gate
- feedback + self-improvement

---

## Samenvatting
De beste v2 voor nu is:
- **Jean = CEO / command layer**
- **Ops Agent = vaste operator**
- **scripts/crons = motor**
- **specialist-agents = alleen op trigger**
- **publish = gecontroleerde Shopify-subflow**

Dit is de leanste en sterkste setup voor EcoHandel: schaalbaar, zuinig, controleerbaar en later makkelijk uit te bouwen.