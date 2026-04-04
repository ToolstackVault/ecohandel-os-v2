# Workflows Page Plan v1

## Waarom deze slag nodig is
De huidige `Agents`-pagina legt het operating model goed uit, maar is nog te veel een architectuur/rollenpagina.

Voor de volgende fase van Econtrol Room moet die laag veranderen naar een **Workflows-pagina** die de echte machine zichtbaar maakt:
- wat draait
- wat faalt
- welke scripts, crons en subflows actief zijn
- welke databronnen leidend zijn
- waar bottlenecks zitten
- welke acties approval nodig hebben
- wat de slimste volgende verbetering is

De Workflows-pagina wordt daarmee de **operationele cockpit van de machine**.

---

## Check van de huidige structuur

## Wat er nu feitelijk staat
De huidige Econtrol Room-architectuur is al behoorlijk scherp en lean ingericht:

### 1. Command layer
- **Jean Clawd** bepaalt prioriteiten, approvals, escalaties en go/no-go.

### 2. Core operating layer
- **1 vaste Ops Agent** als operator.
- Deze laag is bedoeld om de machine te runnen, niet om zelfstandig strategische keuzes te maken.

### 3. Specialistlaag
- `content_strategist`
- `serp_gap`
- `fact_product`
- `refresh`
- `writer`

Maar die zijn expliciet **niet vast draaiend**:
- trigger-only of on-demand
- alleen gebruiken als scripts/rules niet genoeg zijn

### 4. Script-first motor
In `scripts/` zit nu de echte machine:
- `refresh_sources.py`
- `score_queue.py`
- `update_state.py`
- `render_dashboard.py`
- `render_queue_page.py`
- `deploy_live.py`
- `publish_ecohandel.py`
- `ops_cycle.py`

### 5. State-first opzet
In `state/` ligt nu al de basis voor een workflowcockpit:
- `agent-status.json`
- `ops-status.json`
- `cron-status.json`
- `deploy-status.json`
- `publish-status.json`
- `queue-health.json`
- `source-signals.json`
- `specialist-triggers.json`
- `learning-summary.json`
- `source-mix.json`

### 6. Huidige Agents-pagina
De huidige `build/agents.html` toont nu vooral:
- operating model
- vaste laag vs trigger-only agents
- globale workflow
- control rules

Dat is goed als architectuuruitleg, maar nog niet genoeg als cockpit.

---

## Kernconclusie
De basisarchitectuur hoeft **niet opnieuw uitgevonden** te worden.

De goede basis is er al:
- **Jean = command layer**
- **Ops Agent = vaste operator**
- **scripts/crons = echte motor**
- **specialist-agents = alleen op trigger**

Dus de volgende stap is niet “meer agents bouwen”, maar:

**de bestaande machine zichtbaar, bestuurbaar en optimaliseerbaar maken via een Workflows-pagina.**

---

## Nieuwe rol van de Workflows-pagina
De Workflows-pagina moet 5 functies combineren:

### 1. Registry
Overzicht van alle bekende workflows en subflows.

### 2. Monitor
Live zicht op recente runs, failures, stale data en afhankelijkheden.

### 3. Control
Tonen welke workflows auto/manual/hybrid zijn en waar approval-gates zitten.

### 4. Diagnosis
Bottlenecks, alerts en risico’s zichtbaar maken.

### 5. Optimization
Verbeterkansen en structurele machine-aanbevelingen tonen.

---

## Wat een workflow in deze pagina is
De pagina moet niet meer denken in “agents als hoofdentiteit”, maar in **workflows**.

Een workflow is een herhaalbaar proces in de machine, bijvoorbeeld:
- source refresh
- queue scoring
- state update
- dashboard render
- smart queue render
- deploy sync
- publish readiness
- publish execute
- specialist trigger generation
- finance sync
- ops audit

Agents zijn in dit model slechts één type component binnen een workflow.
Scripts en crons zijn minstens zo belangrijk.

---

## Aanbevolen workflow lanes
Om de cockpit logisch te maken, alle workflows onderbrengen in 5 lanes:

### Lane 1 — Ingest
Doel: data of signalen binnenhalen.

Voorbeelden:
- GSC refresh
- Ads refresh
- GA4 refresh
- Shopify refresh
- Wefact sync
- manual topic intake

### Lane 2 — Interpret
Doel: signalen omzetten naar bruikbare inzichten.

Voorbeelden:
- source scoring
- source signal normalization
- CTR opportunity detection
- finance anomaly checks
- refresh signal generation

### Lane 3 — Decide
Doel: prioriteit en routing bepalen.

Voorbeelden:
- queue scoring
- workflow priority rules
- specialist trigger generation
- approval routing

### Lane 4 — Execute
Doel: output draaien of klaarzetten.

Voorbeelden:
- dashboard render
- queue render
- deploy dry-run/live
- publish readiness
- publish wrapper

### Lane 5 — Review & Learn
Doel: machinekwaliteit en verbeteringen bewaken.

Voorbeelden:
- ops audit
- failure review
- learning summary
- recurring issue detection
- confidence / quality review

---

## Structuur van de nieuwe Workflows-pagina

## Blok 1 — Mission Control Header
Bovenste samenvatting van de machine:
- overall system status
- actieve workflows
- failures 24h
- pending approvals
- laatste volledige ops cycle
- top bottleneck
- top opportunity
- data freshness score

## Blok 2 — Workflow Registry
De vaste lijst van workflows.

Per workflow tonen:
- naam
- lane
- doel
- driver (`script`, `cron`, `agent`, `manual`, `hybrid`)
- status
- laatste run
- volgende run
- afhankelijkheden
- approval level
- output-bestanden

## Blok 3 — Live Run Monitor
Recente en actieve runs.

Per run:
- workflow naam
- status (`queued`, `running`, `success`, `warning`, `failed`)
- starttijd
- duur
- triggerbron
- laatste output/fout

## Blok 4 — Controls & Gates
Per workflow zichtbaar maken:
- enabled / disabled
- auto / manual / hybrid
- dry-run / live
- approval required
- safe mode
- retry eligibility

Dit hoeft in v1 nog niet klikbaar te zijn; zichtbaar is eerst genoeg.

## Blok 5 — Dependencies & Data Sources
Zicht op databronnen en onderlinge afhankelijkheden.

Bijvoorbeeld:
- GSC
- Ads
- GA4
- Shopify
- Wefact
- local snapshots
- queue state
- publish state

Per dependency:
- status
- freshness
- gekoppelde workflows
- fallback ja/nee

## Blok 6 — Alerts, Bottlenecks & Recommendations
Slim overzicht van:
- failures
- stale feeds
- cron misses
- publish blocks
- finance blind spots
- te veel handmatig werk
- queue imbalance

En altijd met aanbevolen vervolgstap.

## Blok 7 — Learning & Optimization Layer
Subtiele maar belangrijke laag:
- recurring issues
- gemiddelde succesratio
- workflows met laagste confidence
- laatst toegevoegde verbetering
- optimization suggestions

---

## Mapping van huidige machine naar workflows
Onderstaande workflows bestaan functioneel nu al of zijn logisch direct afleidbaar uit de huidige mapstructuur.

### Bestaande of direct te modelleren workflows
1. Source Refresh
2. Queue Scoring
3. State Update
4. Dashboard Render
5. Smart Queue Render
6. Deploy Dry Run / Live Sync
7. Publish Readiness Check
8. Publish Execute
9. Specialist Trigger Generation
10. Ops Cycle Orchestration
11. Cron Health Check
12. Source Freshness Check
13. Learning Summary Update
14. Finance Sync (voorbereid, nog niet live)

---

## Single source of truth voor de Workflows-pagina
De pagina moet niet op losse aannames draaien, maar op vaste bestanden.

### Voorkeursbronnen voor v1
- `state/ops-status.json`
- `state/cron-status.json`
- `state/deploy-status.json`
- `state/publish-status.json`
- `state/agent-status.json`
- `state/source-signals.json`
- `state/queue-health.json`
- `state/source-mix.json`
- `state/specialist-triggers.json`

### Nieuw aan te maken bestanden voor workflowweergave
- `state/workflow-registry.json`
- `state/workflow-runs.json`
- `state/workflow-controls.json`
- `state/workflow-alerts.json`
- `state/workflow-dependencies.json`
- `state/workflow-recommendations.json`

Deze kunnen in v1 nog deels statisch of script-generated zijn.

---

## Ontwerpprincipes
1. **Workflow-first, niet agent-first**
2. **Script-first blijft leidend**
3. **1 vaste operator blijft genoeg**
4. **Approval-gates zichtbaar houden**
5. **Machine scanbaar maken in 10 seconden**
6. **Niet alleen status tonen, maar ook diagnose + volgende actie**
7. **Finance truth layer voorbereiden via Wefact**

---

## Wat expliciet niet de bedoeling is
- geen terugval naar veel vaste agents
- geen losse brainstormpagina zonder run-data
- geen UI die alleen mooi is maar niets bestuurbaar maakt
- geen vermenging met EcoDash als systeem
- geen live mutaties zonder zichtbare gate/controle

---

## Definition of Ready
De Workflows-pagina is conceptueel klaar om gebouwd te worden als:
- de huidige machine is gemapt naar workflow-entiteiten
- lanes zijn bepaald
- bronbestanden zijn gekozen
- eerste workflow registry is gedefinieerd
- v1-blokken zijn bepaald
- onderscheid tussen `zien`, `bewaken`, `sturen` en `optimaliseren` helder is

---

## Korte samenvatting
De juiste route is:
- huidige lean architectuur behouden
- `Agents` herdefiniëren naar **`Workflows`**
- pagina laten draaien op bestaande state/scripts
- daarna uitbreiden met echte workflow-registry, alerts, controls en later finance-truth layer

Dus:
**niet méér complexiteit bouwen, maar de bestaande machine beter zichtbaar en bestuurbaar maken.**
