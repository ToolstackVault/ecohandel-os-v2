# Workflows Implementation Plan v1

## Doel
De huidige `Agents`-pagina gecontroleerd ombouwen naar een **Workflows-pagina** die de echte EcoHandel-machine toont: scripts, crons, runs, states, gates, bottlenecks en optimalisaties.

Dit plan is bewust gebaseerd op de bestaande architectuur:
- Jean = command layer
- 1 vaste Ops Agent = operator
- scripts/crons = motor
- specialist-agents = trigger-only

---

## Fase 0 — Alignment op bestaande machine
**Doel:** eerst modelleren wat er al is, zonder onnodige verbouwing.

### Acties
- huidige `agents.html` en `AGENTS_PAGE_V1.md` als legacy uitgangspunt markeren
- bestaande scripts, state files en outputpaden mappen naar workflow-entiteiten
- workflow-ID’s kiezen die stabiel kunnen blijven
- lanes toekennen aan alle workflows

### Deliverables
- workflow inventory
- lane mapping
- v1 registry schema

### Verwachte outputbestanden
- `state/workflow-registry.json`
- eventueel `state/workflow-map.json`

---

## Fase 1 — Workflow data model neerzetten
**Doel:** één vaste workflowtaal creëren voor de cockpit.

### Workflow registry per item
Per workflow minimaal:
- `id`
- `name`
- `lane`
- `description`
- `driver_type`
- `owner`
- `mode`
- `enabled`
- `approval_required`
- `status`
- `last_run`
- `next_run`
- `dependencies`
- `outputs`
- `last_error`
- `notes`

### Eerste workflows die erin moeten
- `ops_cycle`
- `source_refresh`
- `queue_scoring`
- `state_update`
- `dashboard_render`
- `queue_render`
- `deploy_sync`
- `publish_readiness`
- `publish_execute`
- `specialist_trigger_generation`
- `cron_health`
- `source_freshness`
- `learning_summary`
- `finance_sync`

### Deliverables
- `state/workflow-registry.json`
- `state/workflow-controls.json`
- `state/workflow-dependencies.json`

---

## Fase 2 — Run/status laag bouwen
**Doel:** echte operationele zichtbaarheid creëren.

### Bronnen hergebruiken
- `state/ops-status.json`
- `state/cron-status.json`
- `state/deploy-status.json`
- `state/publish-status.json`
- `state/agent-status.json`
- `state/source-signals.json`
- `state/specialist-triggers.json`

### Nieuwe aggregatielaag
Script of helper bouwen die bovenstaande combineert naar:
- `state/workflow-runs.json`
- `state/workflow-alerts.json`
- `state/workflow-recommendations.json`

### Wat daarin moet komen
- recente runs
- failed runs
- stale workflows
- blocked workflows
- bottlenecks
- suggested next actions

### Deliverables
- aggregatie-script
- eerste workflow runlogica
- eerste alertlogica

---

## Fase 3 — UI ombouw: Agents → Workflows
**Doel:** de huidige pagina ombouwen zonder dat de rest van Econtrol Room breekt.

### Praktische route
- `build/agents.html` vervangen qua inhoud, maar URL kan in eerste stap nog even `/agents.html` blijven
- titel, copy, navigatie en semantiek omzetten naar `Workflows`
- pagina eerst read-only cockpit maken

### V1-secties bouwen
1. Mission Control Header
2. Workflow Registry
3. Live Run Monitor
4. Controls & Gates
5. Dependencies & Sources
6. Alerts / Bottlenecks / Recommendations
7. Learning & Optimization

### Belangrijk
In v1 hoeven controls nog niet interactief te zijn.
Eerst zichtbaar maken, daarna pas bestuurbaar.

### Deliverables
- vernieuwde renderer of aparte `render_workflows_page.py`
- nieuwe `build/agents.html` of `build/workflows.html`
- UI met live state-binding

---

## Fase 4 — Renderer en buildflow aanpassen
**Doel:** de Workflows-pagina automatisch laten meedraaien in de machine.

### Keuze
Bij voorkeur:
- óf `render_dashboard.py` uitbreiden
- óf aparte renderer toevoegen: `scripts/render_workflows_page.py`

### Aanbevolen aanpak
Aparte renderer maken, zodat dashboard/queue/workflows elk hun eigen renderlogica houden.

### Dan opnemen in ops cycle
Nieuwe volgorde wordt dan ongeveer:
1. refresh_sources
2. score_queue
3. update_state
4. render_dashboard
5. render_queue_page
6. render_workflows_page
7. deploy/live_sync
8. optional_publish_check

### Deliverables
- `scripts/render_workflows_page.py`
- ops cycle update
- build output

---

## Fase 5 — Registry + alerts slimmer maken
**Doel:** van statuspagina naar diagnosecockpit gaan.

### Toevoegen
- workflow severity
- recurring failures
- approval backlog
- dependency failures
- stale source scoring
- “top bottleneck” generator
- “top opportunity” generator

### Nieuwe of uitgebreidere bestanden
- `state/workflow-alerts.json`
- `state/workflow-recommendations.json`
- `state/workflow-health.json`

### Deliverables
- alert generation rules
- bottleneck summary rules
- workflow health metrics

---

## Fase 6 — Controls zichtbaar standaardiseren
**Doel:** machinecontrole expliciet maken.

### Per workflow zichtbaar maken
- enabled / paused
- auto / manual / hybrid
- dry-run / live
- approval required
- retry allowed
- escalation target

### Nog niet per se nodig in v1
- knoppen in de UI
- live toggles
- muterende web controls

### Wel nodig
- bronbestand dat de gewenste control state vastlegt

### Deliverables
- `state/workflow-controls.json`
- weergaveblok in UI

---

## Fase 7 — Finance truth layer voorbereiden
**Doel:** Econtrol Room minder blind maken op omzet- en orderwaarheid.

### Afhankelijk van
- Wefact IP-whitelist voor `84.85.55.133`

### Zodra beschikbaar
- read-only finance sync workflow toevoegen
- offertes + facturen + openstaand bedrag als workflow-output opnemen
- mismatchsignalen tonen t.o.v. Shopify / Ads / GA4

### Deliverables
- `finance_sync` workflow activeren
- finance dependency status
- finance alerts / mismatch flags

---

## Fase 8 — Control panel later interactief maken
**Doel:** pas na stabiliteit echte besturing toevoegen.

### Mogelijke latere acties
- run now
- retry last run
- pause / resume flags
- manual refresh triggers
- publish readiness acknowledge

### Voorwaarde
- eerst betrouwbare state
- eerst stabiele alerting
- eerst duidelijke approval-grenzen

---

## Aanbevolen technische route

## Optie A — minimale verbouwing
- bestaande `agents.html` inhoud vervangen door workflows-cockpit
- URL blijft voorlopig `/agents.html`
- navigatielabel wordt `Workflows`

**Voordeel:** snelste weg, minst risico.

## Optie B — nette route
- nieuwe `workflows.html`
- oude `agents.html` uitfaseren of redirecten
- renderer en nav volledig hernoemen

**Voordeel:** semantisch zuiverder.

### Mijn advies
**Start met optie A**, zodat we snel live bruikbaar zijn.
Daarna kunnen we intern of publiek alsnog naar `workflows.html` migreren.

---

## Definition of Done v1
Deze slag is geslaagd als:
- de huidige machine is gemapt naar workflows
- er een vaste workflow-registry bestaat
- run/status/alerts uit state kunnen worden opgebouwd
- de huidige Agents-pagina inhoudelijk is omgebouwd naar Workflows
- scripts/crons/runs/gates/dependencies zichtbaar zijn
- bottlenecks en volgende acties zichtbaar zijn
- de pagina dient als echte cockpit en niet meer als alleen architectuur-uitleg

---

## Concrete next build order
1. workflow inventory maken uit huidige scripts/state
2. `workflow-registry.json` opzetten
3. `workflow-controls.json` en `workflow-dependencies.json` opzetten
4. workflow aggregatie-script maken
5. Workflows UI-secties bouwen
6. renderer koppelen
7. `ops_cycle.py` uitbreiden
8. live deploy testen
9. daarna pas finance- en interactive-control laag toevoegen

---

## Korte samenvatting
De implementatie moet dus deze volgorde houden:

**eerst modelleren → dan tonen → dan bewaken → dan sturen → dan verdiepen**

Niet andersom.

Dat houdt de machine zuiver, schaalbaar en controleerbaar.