# Partner Campaign — Vast Proces (Model-Agnostic)

> Dit document beschrijft het **complete, vaste proces** voor de EcoHandel partner-mailcampagne.
> Elk model (GPT, Claude, Gemini, lokaal) kan dit volgen zonder voorkennis.

---

## 1. Overzicht

De partner-campagne is een autonoom systeem dat:
- Installateurs en zakelijke prospects mailt via **Brevo**
- Engagement (opens/clicks/replies/bounces) bijhoudt in een **lokale SQLite database**
- Hot prospects dagelijks signaleert aan Milan/Tom
- Campagneprestaties analyseert en optimalisatievoorstellen doet
- De **Partners-pagina** in Econtrol Room (`control.ecohandel.nl/partner-campaign.html`) live houdt

## 2. Architectuur

```
┌─────────────┐    ┌──────────┐    ┌──────────────┐
│  Brevo API  │◄──►│  Scripts  │◄──►│  SQLite DB   │
│  (verzend)  │    │  (motor)  │    │  (waarheid)  │
└─────────────┘    └────┬─────┘    └──────────────┘
                        │
                   ┌────▼─────┐
                   │ Econtrol │
                   │  Room    │
                   │ (render) │
                   └──────────┘
```

**Kernregel:** De lokale database is de bron van waarheid, niet Brevo.

## 3. Bestanden & Locaties

### Scripts (uitvoerbaar)
| Script | Functie |
|--------|---------|
| `scripts/fetch_brevo_stats.py` | Haal live Brevo stats + DB stats op → schrijf state JSON |
| `scripts/run_daily_cycle.py` | Herbereken scores, classificeer replies, genereer hot prospect report |
| `scripts/recalculate_scores.py` | Herbereken lead_score + hot_score voor alle leads |
| `scripts/classify_replies.py` | Classificeer onbeoordeelde replies |
| `scripts/report_hot_prospects.py` | Genereer hot prospect JSON report |
| `scripts/brevo_api.py` | Brevo beheer CLI (status, lists, campaigns, create-list, import-csv) |
| `scripts/import_leads.py` | Importeer leads uit CSV naar lokale DB |
| `scripts/ingest_brevo_event.py` | Verwerk incoming webhook event |
| `scripts/send_test_campaign.py` | Verstuur testcampagne |
| `scripts/export_ecohandel_ready_leads.py` | Export EcoHandel-only leads |
| `scripts/build_ai_link_mapping.py` | Bouw AI-veilige prijslijst-linkmapping |

### Econtrol Room koppeling
| Script | Functie |
|--------|---------|
| `econtrol-room/scripts/render_partner_campaign_page.py` | Render Partners cockpit HTML |
| `econtrol-room/scripts/ops_cycle.py` | Orchestrator — draait alle stappen incl. partner |

### Data & Config
| Pad | Inhoud |
|-----|--------|
| `config.local.json` | Brevo API key, sender, webhook URL, campaign config |
| `data/partner_campaign.db` | SQLite database (leads, events, campaigns, replies) |
| `reports/` | Daily hot prospect reports |
| `imports/raw/` | Ruwe leadbestanden van Milan/Tom |
| `imports/processed/` | Opgeschoonde imports |

### Documentatie
| Document | Inhoud |
|----------|--------|
| `SYSTEM_ARCHITECTURE.md` | Technische architectuur |
| `DATA_MODEL.sql` | Database schema |
| `SCORING_MODEL.md` | Lead scoring regels |
| `CAMPAIGN_BLUEPRINT.md` | Campagnevarianten en CTA-structuur |
| `AUTONOMY_RULES.md` | Wat Jean mag/moet/niet mag |
| `BREVO_WEBHOOK_SPEC.md` | Webhook event types en verwerking |
| `PRICELIST_LINKING_SPEC.md` | Prijslijst product-link regels |
| `ECOHANDEL_SCOPE_RULES.md` | Alleen EcoHandel leads, niet Nova-Cell |
| `DAILY_OPERATIONS.md` | Dagelijkse routine |

## 4. Dagelijks Proces (Automatisch)

### Stap 1: Data ophalen
```bash
python3 scripts/fetch_brevo_stats.py
```
- Haalt account, senders, lists, campaigns + stats op uit Brevo API
- Leest lokale DB voor lead stats, hot prospects, status verdeling
- Berekent AI-recommendations
- Output: `econtrol-room/state/partner-campaign-live.json`

### Stap 2: Daily cycle draaien
```bash
python3 scripts/run_daily_cycle.py
```
Draait achtereenvolgens:
1. `recalculate_scores.py` — herbereken lead_score + hot_score
2. `classify_replies.py` — classificeer nieuwe replies
3. `report_hot_prospects.py` — genereer dagelijks rapport

### Stap 3: Pagina renderen
```bash
python3 econtrol-room/scripts/render_partner_campaign_page.py
```
- Leest `state/partner-campaign-live.json`
- Rendert `build/partner-campaign.html`

### Stap 4: Deploy naar live
```bash
python3 econtrol-room/scripts/deploy_live.py
```
- Pusht alle `build/` bestanden naar VPS `control.ecohandel.nl`

### Stap 5: Hot prospect handoff
- Stuur top hot prospects via Telegram naar Milan
- Format: bedrijf, contact, score, aanbevolen actie (BEL VANDAAG / OPVOLGEN / LATEN LOPEN)

### Volledig in één keer (via ops cycle):
```bash
python3 econtrol-room/scripts/ops_cycle.py
```
Dit draait álle stappen inclusief partner campaign.

## 5. Wekelijks Optimalisatieproces

### Check 1: Subject line vergelijking
- Vergelijk open rates per subject line variant
- Winnaar = hogere unique open rate
- Documenteer in `reports/` of `MEMORY.md`

### Check 2: CTA click-through
- Vergelijk click rates per CTA variant (partner worden vs productfirst vs solution-first)
- Winnaar = hogere click rate + prijslijst-engagement

### Check 3: Segment performance
- Welke segmenten (warmte, type, regio) presteren beter?
- Heroverweeg targeting voor volgende batch

### Check 4: Bounce/unsub hygiene
- Verwijder hard bounces uit Brevo lijst
- Markeer unsubscribes als do_not_contact in DB
- Check of bounce rate <5% en unsub rate <2%

### Check 5: Prijslijst-link heatmap
- Welke productlinks worden het meest geklikt?
- Welke producten genereren de meeste interesse?
- Feedback loop naar productpagina-optimalisatie

## 6. Scoring Model (Samenvatting)

### Lead Score (structurele fit)
- WARM research warmte: +25
- Deye fit: +20
- Batterij ervaring: +15-18
- Email aanwezig: +10
- Contactpersoon: +8
- Strategische fit: +6-12

### Hot Score (actueel gedrag)
- Reply: +45-70
- Product click: +22
- Prijslijst click: +18
- Unique click: +12
- Open: +3 (eerste), +2 (extra)
- Activiteit <24h: +20

### Hot prospect = score ≥60 OF reply OF productclick+WARM

### Beslisregels
| Signaal | Actie |
|---------|-------|
| Reply ontvangen | **BEL VANDAAG** |
| Product click | **HANDMATIG OPVOLGEN** |
| Prijslijst + 2+ opens (72h) | **OPVOLGEN** |
| 2+ opens, geen clicks | **LATEN LOPEN** |
| Unsubscribe/bounce | **UITSLUITEN** |

## 7. Campagne Verzenden (Handmatig / Met Akkoord)

### Voorbereiding
1. Check of leads in juiste Brevo lijst staan
2. Check campaign HTML (variant A, B of C)
3. Check prijslijst-links werken
4. Check sender `info@ecohandel.nl` actief

### Testprotocol
1. Interne testlijst (Milan + Tom)
2. Review rendering desktop + mobiel
3. Kleine warme batch (10-20 leads)
4. Evalueer events na 48h
5. Pas daarna bredere uitrol

### Verzenden via Brevo API
**De partnercampagne draait nu via de Brevo Campaigns API.**

Vaste test/live flow:
```bash
python3 scripts/send_batch_campaign.py B1 --dry-run
python3 scripts/send_batch_campaign.py B1 --test-email milan@nova-cell.com
python3 scripts/send_batch_campaign.py B1
python3 scripts/fetch_brevo_stats.py
```

Belangrijke regels:
- `--test-email` maakt een **verse testlijst + verse testcampagne** aan, zodat oude campaign state de validatie niet vervuilt.
- Links in de mail moeten de persoonlijke flow behouden:
  - `?cid={{contact.EMAIL}}&utm_source=brevo&utm_medium=email&utm_campaign=<campaign_key>`
- De werkende prijslijst-route is:
  - `https://control.ecohandel.nl/partners/p/a7x9kQ3m/`
- De partnerbutton moet automatisch loggen naar:
  - `https://control.ecohandel.nl/partners/api/aanvraag.php`
- Bij campaign-click met bekende `cid` moet direct de bekende-contact-flow werken.
- Bij submit / bekende partnerbutton-click gaat automatisch een notificatiemail naar `info@ecohandel.nl`.

`send_test_campaign.py` blijft alleen legacy voor oude interne tests; gebruik standaard `send_batch_campaign.py`.

### NOOIT zonder akkoord van Milan:
- Eerste live send naar grote lijst
- Nieuwe campagnevariant
- Wijzigingen aan commerciële propositie

## 8. Webhook Events Verwerken

Endpoint: `https://control.ecohandel.nl/hooks/brevo/partner-campaign/?token=<SECRET>`

Events worden gelogd naar:
- `/var/www/html/control.ecohandel.nl/data/brevo-webhook.ndjson`
- Verwerkt door `scripts/ingest_brevo_event.py`

Eventtypen: `delivered`, `open`, `click`, `unsubscribe`, `hard_bounce`, `soft_bounce`, `spam`

## 9. Lead Import

### Nieuwe leads toevoegen
```bash
python3 scripts/import_leads.py path/to/leads.csv
```

### Naar Brevo uploaden
```bash
python3 scripts/brevo_api.py import-csv <list_id> path/to/leads.csv
```

### Scope regel
- **Alleen EcoHandel leads** — geen Nova-Cell of andere bedrijfsleads
- Zie `ECOHANDEL_SCOPE_RULES.md`

## 10. Brevo Beheer

```bash
python3 scripts/brevo_api.py status      # account + senders + lists + campaigns
python3 scripts/brevo_api.py lists        # alle contactlijsten
python3 scripts/brevo_api.py campaigns    # recente campagnes
python3 scripts/brevo_api.py create-list "Naam"  # nieuwe lijst
python3 scripts/brevo_api.py import-csv <list_id> file.csv  # importeer contacten
```

## 11. Econtrol Room Pagina

De Partners-pagina toont:
- **KPI overview** — campagnes, sent, open rate, click rate, leads, credits
- **Brevo campagnes** — tabel met stats per campagne
- **Hot prospects** — top leads met score, warmte, aanbevolen actie
- **AI recommendations** — automatische optimalisatie-inzichten
- **Vast draaiboek** — het proces zelf, zichtbaar in de cockpit
- **Statusverdeling** — lead pipeline
- **Warmteverdeling** — segmentatie overview
- **Daily trend** — 7-daags overzicht
- **Recente events** — webhook activity feed

## 12. Autonomie Regels

### Jean mag autonoom:
- Data ophalen, scores berekenen, reports maken
- Pagina renderen en deployen
- Events verwerken en leads updaten
- Performance analyseren en voorstellen doen
- Prijslijst-mapping controleren

### Jean vraagt akkoord voor:
- Eerste live campaign send
- Grote copywijzigingen
- Nieuwe segmenten met productiebereik

### Jean mag NOOIT:
- Live send naar grote lijst zonder test
- Na unsubscribe opnieuw mailen
- Prijsclaims verzinnen die niet in prijslijst staan

## 13. Modelwisseling

Dit proces is ontworpen zodat elk model het kan uitvoeren:
1. Lees dit document
2. Check `config.local.json` voor API keys en settings
3. Draai de scripts in volgorde
4. Interpreteer de output JSON voor recommendations

**Geen enkele stap vereist model-specifieke kennis.**
