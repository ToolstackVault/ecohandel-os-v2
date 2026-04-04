# Econtrol Room Integration Plan v1

## Doel
De Smart Content Queue en agentstructuur moeten niet alleen goed bedacht zijn, maar ook direct inpasbaar zijn in de bestaande Econtrol Room.

Dit plan beschrijft:
- welke databronnen leidend worden
- hoe de queue live in Econtrol Room komt
- welke blokken eerst gebouwd moeten worden
- hoe we veilig van spec -> live UI gaan

---

## Integratieprincipe
Econtrol Room moet drie dingen tegelijk doen:
1. **zien** wat er gebeurt
2. **begrijpen** wat belangrijk is
3. **aansturen** wat nu moet gebeuren

Daarom wordt de Smart Content Queue geen los bestandje naast het dashboard, maar een **native blok** in het operatiecentrum.

---

## Single Source of Truth
Voor live integratie moeten we één bron aanhouden.

### Aanbevolen bronbestanden
- `queue/SMART_CONTENT_QUEUE.json`
- `queue/REFRESH_QUEUE.json`
- `agents/scout/latest.json`
- `agents/strategist/latest.json`
- `agents/refresh/latest.json`
- `state/queue-health.json`
- `state/agent-status.json`

### Waarom
- dashboard leest vaste paden
- agents schrijven naar voorspelbare paden
- Jean kan handmatig overrulen zonder chaos
- debuggen blijft simpel

---

## Live datastromen

### Stroom 1 — Scout input
Bronnen:
- GSC queries
- trends
- concurrentie
- handmatige Jean/Milan input

Output:
- `agents/scout/latest.json`
- nieuwe ruwe kansen voor queue intake

### Stroom 2 — Strategist scoring
Input:
- scout-output
- bestaande queue
- businessregels

Output:
- gescoorde entries
- voorstel voor `top_5_now`
- voorstel voor `next_up`
- watchlist / kills

### Stroom 3 — Refresh input
Input:
- GSC CTR issues
- bestaande pagina's
- formatting/FAQ/schema/linkkansen

Output:
- `agents/refresh/latest.json`
- `queue/REFRESH_QUEUE.json`

### Stroom 4 — Jean review
Input:
- alle bovenste outputs

Output:
- definitieve `SMART_CONTENT_QUEUE.json`
- overrides
- prioriteitsverschuivingen
- toewijzingen

---

## Minimale live dataset
Om het live te zetten hebben we nog niet alles nodig.

### Must-have v1
- `SMART_CONTENT_QUEUE.json`
- `REFRESH_QUEUE.json`
- `agent-status.json`

### Nice-to-have v1.1
- `queue-health.json`
- `source-mix.json`
- `learning-summary.json`

### Later
- run history
- stale detection
- confidence trendlines
- cluster balance analytics

---

## UI-blokken voor live v1

### 1. Smart Content Queue — Top 5 Now
Toon per item:
- titel
- score
- priority label
- content type
- business goal
- why now
- next step
- assigned agent/status

### 2. Next Up
Compacte lijst van nummer 6–15.

### 3. Refresh First
Toon:
- url/pagina
- issue type
- severity
- aanbevolen fix

### 4. Queue Health
Toon:
- aantal items per P1/P2/P3/P4/P5
- lane verdeling
- stale waarschuwingen
- confidence mix
- teveel authority? te weinig refresh?

### 5. Agent Status
Toon:
- laatste scout run
- laatste strategist run
- laatste refresh run
- status: ok / stale / failed

---

## Aanbevolen renderlogica

### Top 5 Now sortering
Sorteer primair op:
1. lane = `top_5_now`
2. `priority_label`
3. `total_score`
4. recentste update

### Refresh First sortering
Sorteer op:
1. severity
2. priority
3. confidence
4. recentste update

### Waarschuwingen
Toon warnings als:
- geen P1 item in top 5
- geen refresh item aanwezig
- >25% low confidence items
- scout/strategist/refresh data verouderd is

---

## Bestandsformaten

### SMART_CONTENT_QUEUE.json
Aanbevolen top-level structuur:
```json
{
  "generated_at": "2026-03-26T22:30:00Z",
  "mode": "hybrid_revenue_first",
  "top_5_now": [],
  "next_up": [],
  "refresh_first": [],
  "watchlist": [],
  "killed_noise": [],
  "done": []
}
```

### REFRESH_QUEUE.json
```json
{
  "generated_at": "2026-03-26T22:30:00Z",
  "items": []
}
```

### agent-status.json
```json
{
  "updated_at": "2026-03-26T22:30:00Z",
  "agents": {
    "scout": {"status": "ok", "last_run": "...", "items_found": 12},
    "strategist": {"status": "ok", "last_run": "...", "items_scored": 12},
    "refresh": {"status": "ok", "last_run": "...", "issues_found": 4}
  }
}
```

---

## Live bouwvolgorde

### Fase 1 — renderbaar maken
Doel: dashboard kan data tonen.

Bouwen:
- basis JSON-bestanden op vaste paden
- voorbeelddata in live-vorm zetten
- UI-blokken aansluiten op die JSON

### Fase 2 — handmatig bestuurbaar maken
Doel: Jean kan de queue echt gebruiken.

Bouwen:
- handmatige override mogelijkheid
- duidelijke status- en lane-indicatoren
- makkelijk verversbare JSON workflow

### Fase 3 — semi-automatisch voeden
Doel: agents leveren echte input.

Bouwen:
- Scout output -> Strategist intake
- Refresh output -> refresh lane
- Jean reviewflow

### Fase 4 — volledig operationeel
Doel: dagelijkse runs + betrouwbaar live overzicht.

Bouwen:
- scheduled updates
- stale checks
- queue health generatie
- learning samenvattingen

---

## Veiligste weg naar live
Niet meteen alle automatisering proberen.

### Eerst live met gecontroleerde data
1. gebruik voorbeelddata + handmatige correcties
2. render alles correct in UI
3. check of layout, sorting en labels goed voelen
4. pas daarna agent-output eraan koppelen

Waarom:
- sneller live
- minder debugging tegelijk
- betere controle over UX
- minder kans op rommel in dashboard

---

## What Jean should control manually in v1
- top 5 override
- priority overrides
- kill / park beslissingen
- refresh vóór nieuw onderwerp
- assignment aan agents

Dit voorkomt dat de machine al te vroeg te autonoom wordt.

---

## Queue health generator
Aanbevolen apart bestand:
`state/queue-health.json`

Voorbeeldinhoud:
- total items
- items per lane
- items per priority
- items per cluster
- low confidence count
- stale count
- missing refresh flag
- overconcentration flag

Dit maakt de UI simpeler.

---

## Source mix generator
Aanbevolen apart bestand:
`state/source-mix.json`

Toont:
- % GSC-based
- % manual
- % trend-based
- % refresh-based
- % competitor-based

Waarom:
Zo zie je of de queue te veel op één soort input leunt.

---

## Learning visibility
Nog niet als groot dashboardblok, wel als subtiele statuslaag.

### In v1
Toon:
- aantal learning flags deze week
- agent met meeste issues
- terugkerende fouten ja/nee

### Later
Apart blok met:
- top learnings
- scoring adjustments
- bronkwaliteit waarschuwingen

---

## Aanbevolen mappenstructuur live
`ecohandel/econtrol-room/`
- `AGENT_ARCHITECTURE_V1.md`
- `SMART_CONTENT_QUEUE_SPEC_V1.md`
- `SMART_CONTENT_QUEUE_SCHEMA.json`
- `SMART_CONTENT_QUEUE_EXAMPLES.json`
- `AGENT_OUTPUT_CONTRACTS.md`
- `ECONTROL_ROOM_INTEGRATION_PLAN_V1.md`
- `queue/SMART_CONTENT_QUEUE.json`
- `queue/REFRESH_QUEUE.json`
- `agents/scout/latest.json`
- `agents/strategist/latest.json`
- `agents/refresh/latest.json`
- `state/agent-status.json`
- `state/queue-health.json`
- `state/source-mix.json`
- `state/learning-summary.json`

---

## Definition of Live Ready
We noemen het live-ready als:
- Top 5 Now zichtbaar is in Econtrol Room
- Next Up zichtbaar is
- Refresh First zichtbaar is
- Agent Status zichtbaar is
- queue JSON op vaste plek staat
- Jean handmatig kan overrulen
- data opnieuw kan worden gegenereerd zonder UI-breuk

---

## Concrete next deliverables
Om echt live te gaan zijn nu nog logisch:
1. `queue/SMART_CONTENT_QUEUE.json`
2. `queue/REFRESH_QUEUE.json`
3. `state/agent-status.json`
4. `state/queue-health.json`
5. `state/source-mix.json`
6. een korte implementatie-checklist voor de UI

---

## Samenvatting
De snelste route naar live:
- eerst vaste JSON-bronnen
- dan renderblokken
- dan handmatige controle
- dan pas echte agentautomatisering

Dus: eerst stabiel, daarna slim.
