# EcoHandel Econtrol Room

## Belangrijkste documenten
- `AGENT_ARCHITECTURE_V1.md` — huidige v2-opzet van Jean + Ops Agent + specialistlaag
- `OPS_AGENT_SPEC_V1.md` — vaste operationele agent onder Jean
- `SMART_CONTENT_QUEUE_SPEC_V1.md` — volledige specificatie voor de Smart Content Queue
- `SMART_CONTENT_QUEUE_SCHEMA.json` — formeel schema voor queue entries
- `SMART_CONTENT_QUEUE_EXAMPLES.json` — voorbeelddata voor live integratie
- `AGENT_OUTPUT_CONTRACTS.md` — vaste outputstructuur voor agents
- `ECONTROL_ROOM_INTEGRATION_PLAN_V1.md` — route van spec naar live dashboard
- `IMPLEMENTATION_CHECKLIST_V1.md` — concrete live-checklist
- `WORKFLOWS_PAGE_PLAN_V1.md` — plan van aanpak voor de ombouw van Agents naar Workflows
- `WORKFLOWS_IMPLEMENTATION_PLAN_V1.md` — gefaseerd implementatieplan voor de workflowcockpit

## Belangrijkste mappen
- `sources/` — bronbestanden voor deterministic queue-input
- `scripts/` — deterministic flows (ingest, scoring, health, render, trigger, publish wrapper)
- `cron/` — cron schema en voorbeeld planning
- `queue/` — Smart Content Queue + refresh queue
- `state/` — agent-status, queue-health, source-mix, learnings, ops/cron/deploy status
- `agents/` — trigger-only specialist outputs
- `learn/` — bewezen of terugkerende learnings
- `build/` — render output voor live control room

## Werkende scripts nu
- `scripts/refresh_sources.py`
- `scripts/score_queue.py`
- `scripts/update_state.py`
- `scripts/render_dashboard.py`
- `scripts/render_queue_page.py`
- `scripts/trigger_specialists.py`
- `scripts/deploy_live.py` (bewust dry-run)
- `scripts/publish_ecohandel.py` (approval-gated wrapper)
- `scripts/ops_cycle.py` (orkestreert alles)

## Doel van deze map
Vaste, makkelijk terugvindbare plek voor:
- operating system van EcoHandel
- Smart Content Queue
- operationele queue-bestanden
- state / learnings / agent outputs
- render/deploy bouwlaag

## Richtlijn
De machine draait hier volgens dit principe:
- Jean bepaalt
- Ops Agent voert uit
- scripts doen het bulkwerk
- specialist-agents alleen op trigger
- publish is gecontroleerd en Shopify-specifiek voor EcoHandel.