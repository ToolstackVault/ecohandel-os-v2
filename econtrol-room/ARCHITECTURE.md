# EcoHandel Operating System — Architectuur

**Versie:** 1.0  
**Datum:** 2026-04-02  
**Status:** Fundamenteel besluit  
**Stip op de horizon:** EcoHandel OS = SaaS-product in de toekomst

---

## 1. Vision

EcoHandel heeft een **operating system** nodig: een centrale cockpit waarin Jean Clawd, Milan en Tom content, campagnes, agent-werk en bedrijfsprocessen kunnen aansturen.

Het huidige Econtrol Room is de kern van dat OS. De architectuur wordt nu neergezet met een duidelijke stip:

> **Fase 1: EcoHandel-only. Fase 2: multi-tenant SaaS.**

Alles wat we bouwen moet daarop voorbereid zijn — zonder dat we nu al de complexiteit van multi-tenant implementeren.

---

## 2. Tech Stack (vastgesteld)

| Laag | Keuze | Reden |
|------|-------|-------|
| Database | **SQLite** | Betrouwbaar, zero-config, file-based backups eenvoudig, portabel |
| API-laag | **REST API** (Python/Flask of FastAPI) | Eenvoudig te auditen, developer-friendly, goede ecosystem |
| Frontend | **Static HTML/JS PWA** (wat er nu is) | Werkt nu al, kan later migrate naar React/Vue zonder DB te touchen |
| State | **JSON files naast SQLite** | Transitioneel — SQLite wordt bron van waarheid, JSON voor snapshot/UI |
| Agent-aansturing | **CLI scripts + cron** | Betrouwbaar, debugbaar, geen broker nodig |
| Deploy | **VPS (Hetzner)** + `www-data` user | Huidige setup, werkt perfect |

**Waarom SQLite en niet PostgreSQL/MySQL:**
- Geen serverprocess nodig
- Backup = kopieer bestand
- EcoHandel heeft geen 10.000 gelijktijdige gebruikers
- Veel sneller te ontwikkelen en te testen
- Past uitstekend bij het "eerst werkend, dan schaalbaar" principe

**Waarom REST API en niet GraphQL:**
- Eenvoudiger te bouwen en te debuggen
- Goede integratie met cron/scripts/agents
- Swagger/docs is triviaal
- GraphQL voegt nu geen waarde toe

---

## 3. Gebruikersmodel (Fase 1)

Drie gebruikers, allemaal **admin**:

| User | Rol | Type |
|------|-----|------|
| **Jean Clawd** | AI Command Layer | Agent (API token) |
| **Milan** | Eigenaar | Human (inlog) |
| **Tom** | Mede-eigenaar | Human (inlog) |

**Auth:**
- HTTP Basic Auth voor nu (VPS password-protected)
- Later: JWT tokens via eigen auth-servicetje
- API-toegang voor Jean: vast token (，符合 Paperclip integration)

**Geen rollen nodig in Fase 1.** Alle drie mogen alles. Beperkingen komen als features, niet als architectuur.

---

## 4. Multi-Tenant Voorbereiding (nu aanleggen, niet nu gebruiken)

### Tenant-ID door de hele codebase

Vanaf nu krijgt **elke database tabel** en **elke API-route** een `tenant_id` kolom / parameter. Die is nu hardcoded naar `eco001` (EcoHandel). Bij uitbreiding wordt dit dynamisch.

**Regels:**
1. Elke tabel heeft een `tenant_id TEXT NOT NULL DEFAULT 'eco001'`
2. Elke API-request specificeert `X-Tenant-ID` header (of JWT claim)
3. Jean's API-token is gekoppeld aan `eco001`
4. Scripts die voor EcoHandel draaien: `tenant_id = 'eco001'` hardcoded
5. **Nooit** tenant-agnostisch bouwen tenzij het bewust en getest is

### Wat WEL meenemen in Fase 1:
- [ ] `tenant_id` in alle tabellen
- [ ] API middleware die tenant uit header haalt
- [ ] Seeding script met `eco001` als default
- [ ] Config file met tenant configuratie per omgeving

### Wat NIET meenemen in Fase 1:
- Geen gebruikerstabel met rollen/permissions (nog niet nodig)
- Geen tenant provisioning flow
- Geen billing/kosten-plaatsing
- Geen white-label theming

---

## 5. API Ontwerp

### Basisprincipes

```
Base URL: https://control.ecohandel.nl/api/v1/
Auth: Bearer <token>  (JWT of vast token per user/agent)
Content-Type: application/json
```

### API Resource Overzicht

| Endpoint | Methode | Beschrijving |
|----------|---------|-------------|
| `GET /health` | GET | API gezondheid |
| `GET /queue` | GET | Smart Content Queue ophalen |
| `POST /queue/items` | POST | Nieuw item aan queue toevoegen |
| `PATCH /queue/items/{id}` | PATCH | Item updaten (lane, status, score) |
| `DELETE /queue/items/{id}` | DELETE | Item verwijderen |
| `GET /queue/health` | GET | Queue health metrics |
| `GET /agents/status` | GET | Agent run status |
| `POST /agents/trigger/{agent}` | POST | Specialist agent triggeren |
| `GET /campaigns/{id}/stats` | GET | Partner campaign stats |
| `GET /workflows` | GET | Workflow registry + status |
| `POST /workflows/{id}/run` | POST | Workflow handmatig runnen |
| `GET /workflows/runs` | GET | Run history |
| `GET /publish/pending` | GET | Pending publish items |
| `POST /publish/{id}/approve` | POST | Publish goedkeuren |
| `POST /publish/{id}/reject` | POST | Publish afkeuren |
| `GET /activity` | GET | Activity/audit log |

### Response Structuur

```json
{
  "ok": true,
  "data": { ... },
  "meta": {
    "tenant_id": "eco001",
    "generated_at": "2026-04-02T07:00:00Z",
    "version": "1.0"
  }
}
```

```json
{
  "ok": false,
  "error": {
    "code": "ITEM_NOT_FOUND",
    "message": "Queue item SCQ-xxx niet gevonden"
  }
}
```

### Error Codes
- `400` — Bad request (validatie)
- `401` — Unauthorized (geen geldige token)
- `403` — Forbidden (tenant mismatch)
- `404` — Not found
- `409` — Conflict (bijv. dubbele run)
- `500` — Internal error

---

## 6. Database Schema (SQLite)

### Conceptuele tabellen

```
tenants
  - id (TEXT PK)
  - name
  - created_at

users
  - id (INTEGER PK)
  - tenant_id (TEXT FK)
  - email
  - name
  - role (TEXT)  -- voor nu: admin
  - api_token_hash (TEXT)
  - created_at

queue_items
  - id (TEXT PK)  -- SCQ-YYYYMMDD-NNN
  - tenant_id (TEXT FK)
  - title
  - slug_candidate
  - content_type (TEXT)
  - business_goal (TEXT)
  - priority_label (TEXT)
  - status (TEXT)
  - lane (TEXT)
  - primary_cluster (TEXT)
  - secondary_cluster (TEXT)
  - target_audience (TEXT)
  - total_score (INTEGER)
  - confidence (REAL)
  - signal_sources (TEXT)  -- JSON array
  - why_now (TEXT)
  - recommended_format (TEXT)
  - recommended_next_step (TEXT)
  - owner (TEXT)
  - assigned_agent (TEXT)
  - notes (TEXT)
  - refresh_target_url (TEXT)
  - created_at (TEXT)
  - updated_at (TEXT)
  - done_at (TEXT)

queue_health
  - id (INTEGER PK)
  - tenant_id (TEXT FK)
  - generated_at (TEXT)
  - total_items (INTEGER)
  - p1_count, p2_count, p3_count, p4_count, p5_count (INTEGER)
  - lane_counts (TEXT)  -- JSON
  - low_confidence_count (INTEGER)
  - stale_count (INTEGER)
  - health_flags (TEXT)  -- JSON array

agent_runs
  - id (INTEGER PK)
  - tenant_id (TEXT FK)
  - agent_name (TEXT)
  - status (TEXT)
  - started_at (TEXT)
  - completed_at (TEXT)
  - items_processed (INTEGER)
  - errors (TEXT)  -- JSON array
  - output_summary (TEXT)

workflow_runs
  - id (INTEGER PK)
  - tenant_id (TEXT FK)
  - workflow_id (TEXT)
  - status (TEXT)
  - triggered_by (TEXT)
  - started_at (TEXT)
  - completed_at (TEXT)
  - steps_completed (INTEGER)
  - steps_failed (INTEGER)
  - next_actions (TEXT)  -- JSON
  - health_flags (TEXT)  -- JSON

campaign_contacts
  - id (INTEGER PK)
  - tenant_id (TEXT FK)
  - email
  - first_name (TEXT)
  - company_name (TEXT)
  - status (TEXT)
  - source (TEXT)
  - brevo_contact_id (TEXT)
  - created_at (TEXT)
  - updated_at (TEXT)
  - last_contacted_at (TEXT)
  - engagement_score (INTEGER)
  - open_count (INTEGER)
  - click_count (INTEGER)
  - reply_count (INTEGER)

campaign_events
  - id (INTEGER PK)
  - tenant_id (TEXT FK)
  - contact_id (INTEGER FK)
  - campaign_id (TEXT)
  - event_type (TEXT)  -- sent, open, click, reply, bounce, unsub
  - occurred_at (TEXT)
  - metadata (TEXT)  -- JSON

publish_requests
  - id (INTEGER PK)
  - tenant_id (TEXT FK)
  - queue_item_id (TEXT FK)
  - content_type (TEXT)
  - content_payload (TEXT)  -- JSON of HTML
  - status (TEXT)  -- pending, approved, rejected, published, failed
  - requested_by (TEXT)
  - approved_by (TEXT)
  - published_at (TEXT)
  - created_at (TEXT)
  - updated_at (TEXT)

activity_log
  - id (INTEGER PK)
  - tenant_id (TEXT FK)
  - actor (TEXT)  -- user_id, agent_id, 'system'
  - action (TEXT)
  - resource_type (TEXT)
  - resource_id (TEXT)
  - metadata (TEXT)  -- JSON
  - ip_address (TEXT)
  - created_at (TEXT)

learning_entries
  - id (INTEGER PK)
  - tenant_id (TEXT FK)
  - category (TEXT)  -- error, correction, pattern, improvement
  - title (TEXT)
  - description (TEXT)
  - trigger (TEXT)
  - applied_to (TEXT)
  - evidence (TEXT)
  - created_at (TEXT)
  - resolved_at (TEXT)
```

---

## 7. Folder & File Structuur

```
econtrol-room/
  ├── ARCHITECTURE.md          ← dit bestand
  ├── README.md
  ├── SPECS/
  │   ├── API_SPEC.md          ← gedetailleerde API docs
  │   ├── DB_SCHEMA.md         ← SQLite schema details + migrations
  │   └── QUEUE_SPEC.md        ← Smart Queue specificatie
  ├── DATABASE/
  │   ├── schema.sql           ← SQLite CREATE TABLE statements
  │   ├── migrations/          ← toekomstige schema updates
  │   └── seed.sql             ← eco001 default data
  ├── API/
  │   ├── app.py               ← Flask/FastAPI app entry point
  │   ├── auth.py              ← token validation + tenant resolution
  │   ├── routes/
  │   │   ├── queue.py
  │   │   ├── agents.py
  │   │   ├── campaigns.py
  │   │   ├── workflows.py
  │   │   ├── publish.py
  │   │   └── activity.py
  │   ├── models/
  │   │   ├── __init__.py
  │   │   ├── queue.py
  │   │   ├── campaign.py
  │   │   ├── workflow.py
  │   │   └── user.py
  │   └── middleware/
  │       ├── tenant.py        ← X-Tenant-ID resolution
  │       └── audit.py         ← activity logging
  ├── SCRIPTS/
  │   ├── ops_cycle.py         ← bestaand (blijft)
  │   ├── refresh_sources.py   ← bestaand (blijft)
  │   ├── score_queue.py       ← bestaand (blijft)
  │   ├── update_state.py      ← bestaand (blijft)
  │   ├── sync_db.py           ← NIEUW: SQLite sync (API ↔ files)
  │   └── db_seed.py            ← NIEUW: eco001 seeding
  ├── STATE/                   ← bestaand (wordt snapshot/UI cache)
  ├── QUEUE/                   ← bestaand (wordt snapshot/UI cache)
  ├── BUILD/                   ← bestaand (UI rendering)
  └── TESTS/
      ├── test_api_queue.py
      ├── test_api_auth.py
      └── test_queue_scoring.py
```

---

## 8. Fase 1 — Prioriteit 1: API + Database

De huidige file-based state werkt, maar is op termijn onhoudbaar. De eerste tastbare stap is:

### Stap 1A: SQLite database neerzetten
```
DATABASE/ecohandel.db aanmaken
schema.sql draaien
seed.sql draaien (eco001)
```

### Stap 1B: API entry point
```
Flask app met:
- GET /health
- GET /queue
- PATCH /queue/items/{id}
- POST /publish/{id}/approve
```

### Stap 1C: Sync script
```
sync_db.py: leest huidige JSON files → schrijft naar SQLite
scripts/ blijven hun JSON files schrijven
API leest uit SQLite (single source of truth)
```

### Stap 1D: Auth laag
```
Vast token voor Jean (paperclip token)
HTTP Basic voor Milan/Tom (of simple password)
X-Tenant-ID middleware
```

---

## 9. Fase 2 — Workflow Engine

Na de API basis:
- Workflow registry naar DB
- Workflow runs naar DB (inclusief audit)
- Dependency tracking
- Failure recovery

---

## 10. Fase 3 — Campaign Intelligence

Na Workflow Engine:
- Campaign contacts naar DB
- Brevo webhook events naar DB
- Engagement scoring in DB
- Campaign stats via API

---

## 11. Fase 4 — Full Smart Queue DB

- Queue items naar DB
- Scoring naar DB
- Agent runs naar DB
- Learnings naar DB

---

## 12. Harde Regels (voor nu en toekomst)

1. **Geen tenant data mixen** — Alles-query altijd met `WHERE tenant_id = ?`
2. **API eerst testen** — curl/postman test bij elk nieuw endpoint
3. **Migraties bewaren** — Elke schema-wijziging = migratie bestand
4. **Activity log bij elke mutatie** — Wie, wat, wanneer, tenant
5. **Scripts blijven werken** — Ops cycle hoeft geen API te callen, werkt direct met files/DB
6. **Jean altijd admin** — Geen verdere role-based restrictions in Fase 1
7. **Backup = kopie** — SQLite: `cp ecHandel.db ecHandel.db.bak-$(date +%Y%m%d)`

---

## 13. Besloten / Niet Besloten

### Besloten ✅
- SQLite als database
- REST API als interface
- Single tenant nu, multi-tenant voorbereid
- Jean + Milan + Tom = admin
- Bestaande file-based scripts blijven werken
- Huidige static PWA frontend blijft werken (kan later vervangen)

### Niet Besloten ❓
- Flask vs FastAPI (beide werken, persoonlijke voorkeur?)
- JWT vs vast token (wat werkt het beste met Paperclip?)
- Externe database (SQLite op VPS vs remote server)?
- Monitoring/alerting (Sentry? Pingdom? Zelfbouw?)
- CI/CD pipeline (nu handmatig, later GitHub Actions?)

---

## 14. Eerste concrete todo's

1. [ ] `DATABASE/schema.sql` schrijven
2. [ ] `DATABASE/seed.sql` schrijven
3. [ ] `API/app.py` entry point neerzetten met `/health`
4. [ ] Auth middleware (`auth.py`)
5. [ ] `sync_db.py` script
6. [ ] Test: API leest queue uit SQLite
7. [ ] `SCRIPTS/sync_db.py` in ops_cycle.py toevoegen
8. [ ] Documentatie aanvullen in `SPECS/API_SPEC.md`

---

*Laatst bijgewerkt: 2026-04-02 door Jean Clawd*
*Volgende review: na Stap 1D (eerste werkende API)*
