# EcoHandel Partner Campaign System

Doel: een autonoom draaiend outreach- en opvolgsysteem voor installateurs/partners, gestuurd vanuit Brevo + lokale lead intelligence.

## Kernuitkomst
- partnercampagnes versturen via Brevo
- opens, clicks, replies, unsubscribes, bounces en engagement centraliseren
- interactieve prijslijst koppelen aan echte Shopify-productlinks
- hot prospects dagelijks doorgeven aan Milan/Tom
- continue verbetering van onderwerpregels, CTA's, linkprestaties en leadkwaliteit

## Structuur
- `SYSTEM_ARCHITECTURE.md` — totale systeemopzet
- `DATA_MODEL.sql` — SQLite schema als bron van waarheid
- `BREVO_WEBHOOK_SPEC.md` — webhook events en verwerking
- `PRICELIST_LINKING_SPEC.md` — linkstructuur voor interactieve prijslijst
- `DAILY_OPERATIONS.md` — dagelijkse autonome routines
- `scripts/bootstrap_db.py` — maakt database + tabellen
- `scripts/import_leads.py` — importeert bestaande LEADS.csv
- `scripts/report_hot_prospects.py` — dagelijkse hot prospect shortlist

## Belangrijke ontwerpregels
- eerst testlijst, nooit direct de hele lijst
- Brevo is verzend- en eventlaag, lokale database is de bron van waarheid
- alle CTA-links moeten naar echte EcoHandel product-/collectiepagina's wijzen
- mobile responsive prijslijst is verplicht
- scoremodel moet uitlegbaar zijn, niet black-box
- replies wegen zwaarder dan opens
- unsubscribes en bounces direct markeren en uitsluiten

## Huidige leadbron
- `ecohandel/lead-generation/leads/LEADS.csv`

## Nog door Milan aan te leveren
- HTML prijslijst (of nieuwe iteraties daarvan)

## Reeds vastgelegd
- Brevo SMTP/API gegevens zijn lokaal opgeslagen
- afzender bevestigd: `EcoHandel.nl <info@ecohandel.nl>`
- aanbevolen webhook URL vastgelegd in `WEBHOOK_RECOMMENDATION.md`
- webhook secret lokaal gegenereerd en opgeslagen
- voorkeuren voor partnerpropositie / CTA copy
- Brevo beheerlaag actief via `scripts/brevo_api.py`
- beheerhandleiding vastgelegd in `BREVO_API_MANAGEMENT.md`
- API-status bevestigd: account, senders, lists en campaigns reageren allemaal met `200 OK`

## Launch pack — 2026-03-28
De eerste live test voor morgen staat klaar in `launch/`:
- `launch/2026-03-28_top30_launch_leads.csv` — definitieve selectie van 30 leads
- `launch/2026-03-28_batch_plan.md` — 3 batches van 10 met hypothese, onderwerpregel, CTA en tijdstip
- `launch/2026-03-28_launch_plan.md` — kort beslisblad, preflight checks en evaluatiecriteria

Gebruik deze launchbestanden als operationele waarheid voor de eerste mailwave; Brevo blijft alleen de verzendlaag en eventinname.
