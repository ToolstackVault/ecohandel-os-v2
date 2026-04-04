# Implementation Checklist v2

## Doel
Concrete checklist om EcoHandel Econtrol Room echt werkend te maken als lean operating system.

---

## Stap 1 — operating system vastzetten
- [x] Jean = command layer vastgelegd
- [x] 1 vaste Ops Agent gedefinieerd
- [x] specialist-agents teruggebracht naar trigger-only
- [x] folderstructuur `scripts/`, `cron/`, `agents/`, `learn/` neergezet

---

## Stap 2 — deterministic motor bouwen
- [x] `refresh_sources.py`
- [x] `score_queue.py`
- [x] `update_state.py`
- [x] `render_dashboard.py`
- [x] `render_queue_page.py`
- [x] `deploy_live.py` (dry-run veilig)
- [x] `publish_ecohandel.py` wrapper aangemaakt

---

## Stap 3 — state standaardiseren
- [x] `state/agent-status.json`
- [x] `state/queue-health.json`
- [x] `state/source-mix.json`
- [x] `state/learning-summary.json`
- [x] `state/ops-status.json`
- [x] `state/cron-status.json`
- [x] `state/source-signals.json`
- [x] `state/deploy-status.json`

---

## Stap 4 — cronlaag aanzetten
- [x] cron voorstelbestand aangemaakt
- [ ] data refresh cron echt activeren
- [ ] queue scoring cron echt activeren
- [ ] render/deploy cron echt activeren
- [ ] daily refresh scan cron echt activeren
- [ ] daily ops audit cron echt activeren

---

## Stap 5 — echte output op dashboard
- [x] Top 5 Now uit live scoring
- [x] Next Up uit live scoring
- [x] Queue Health uit live state
- [x] Ops Status zichtbaar
- [x] Cron Health zichtbaar
- [x] aparte Smart Content Queue pagina gebouwd
- [ ] Refresh First lane nog verder verdiepen

---

## Stap 6 — specialist triggers
- [x] triggerlogica basisbestand gemaakt
- [x] Content Strategist triggerlogica basis
- [x] SERP Gap triggerlogica basis
- [x] Fact & Product triggerlogica basis
- [ ] Refresh Agent triggerlogica verder verfijnen
- [ ] echte specialist-executie koppelen

---

## Stap 7 — Shopify publish subflow
- [x] EcoHandel/Shopify scope in wrapper vastgezet
- [x] bestaande Shopify publish script gekoppeld via wrapper
- [x] approval gate ingebouwd (`--approve` vereist)
- [ ] publish result verder terugschrijven naar dashboard

---

## Stap 8 — self-improvement + usage
- [ ] usage logging per run verdiepen
- [ ] failure logging uitbreiden
- [ ] recurring issues dedupen
- [ ] bewezen patterns promoten

---

## Definition of Done
- [x] 1 Ops Agent runt de machine betrouwbaar
- [x] scripts doen het bulkwerk
- [x] specialist-agents draaien alleen op trigger-basis (nog niet auto-executed)
- [x] dashboard leest live queue/state
- [x] publish is gecontroleerd via wrapper
- [ ] usage blijft laag genoeg om autonoom te schalen in echte live productie
- [ ] externe feeds (GSC/Ads/Shopify signalen) echt aansluiten
- [ ] live deploy/sync bewust activeren