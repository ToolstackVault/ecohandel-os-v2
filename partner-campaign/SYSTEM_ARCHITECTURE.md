# System Architecture — EcoHandel Partner Campaign

## 1. Missie
Een meetbaar en autonoom partner-acquisitiesysteem bouwen voor EcoHandel.nl, gericht op installateurs en zakelijke prospects.

## 2. Hoofdcomponenten

### A. Lead source layer
Bronnen:
- bestaande `LEADS.csv`
- toekomstige handmatige toevoegingen
- toekomstige enrichment / research runs

Functie:
- ruwe leads verzamelen
- normaliseren
- status toekennen
- segmenteren op warmte, regio, type partner, Deye-fit

### B. CRM-lite / database layer
Lokale database als bron van waarheid.

Doet:
- lead records bewaren
- email sends loggen
- opens/clicks/replies/unsubs/bounces opslaan
- score en status berekenen
- hot prospects rapporteren

Waarom lokaal?
- Brevo is goed in verzending, niet in volledige businesslogica
- wij willen eigen scoring, eigen daily handoff en eigen leerlus

### C. Campaign execution layer (Brevo)
Brevo verzorgt:
- list/segment management
- campaign send
- deliverability events
- webhook events

Belangrijke regels:
- altijd testlijst eerst
- campaign IDs en list IDs loggen in database
- subject/body variant informatie opslaan voor latere verbetering

### D. Content & CTA layer
Een campagne mail bevat:
- duidelijke partnerpropositie
- 1 primaire CTA: partner worden / contact / prijslijst bekijken
- 1 secundaire CTA: relevante productcategorie of voordeel
- link naar interactieve prijslijst

De interactieve prijslijst:
- mobile responsive HTML
- productregels linken naar echte Shopify URL's
- elke klik krijgt tracking parameters mee

### E. Event ingestion layer
Webhook verwerkt eventtypes zoals:
- delivered
- open / unique_open
- click / unique_click
- reply (indien beschikbaar via inbox/workflow)
- unsubscribe
- hard_bounce / soft_bounce
- spam complaint (indien beschikbaar)

Verwerking:
1. webhook event komt binnen
2. event wordt gevalideerd
3. lead / campaign / link wordt gematcht
4. event wordt opgeslagen
5. lead score en hotness worden herberekend
6. daily shortlist wordt bijgewerkt

### F. Daily intelligence layer
Elke dag een rapport met:
- hottest prospects
- nieuwe replies
- multi-open leads
- leads met prijslijst-clicks
- leads met product-clicks
- unsubscribes/bounces
- aanbeveling: bellen / opvolgen / parkeren / uitsluiten

## 3. Lead lifecycle
- `new`
- `validated`
- `queued_for_campaign`
- `sent`
- `engaged`
- `hot`
- `replied`
- `qualified`
- `customer`
- `unsubscribed`
- `bounced`
- `dead`

## 4. Hot prospect definitie
Een lead wordt hot bij bijvoorbeeld:
- reply ontvangen
- meerdere opens in korte tijd
- klik op prijslijst + productlink
- recente interactie binnen 72 uur
- warme lead + engagement combinatie

## 5. Waarom dit voor EcoHandel werkt
Jullie business is niet puur self-serve e-commerce. Daarom moet het systeem niet alleen tellen:
- mails verzonden
- opens
- clicks

Maar vooral:
- wie toont koopintentie?
- wie bekijkt meerdere relevante links?
- wie vraagt impliciet om opvolging?

## 6. Autonome routines
Dagelijks:
- events syncen
- scores herberekenen
- hot prospect report maken
- anomalies signaleren
- lijst hygiene bijwerken

Wekelijks:
- CTA prestaties vergelijken
- subject line prestaties analyseren
- segment performance review
- underperformers uitsluiten of herschrijven

## 7. Fasevolgorde
### Fase 1 — Fundament
- database
- lead import
- event model
- scoremodel
- rapportage

### Fase 2 — Brevo koppeling
- sender
- webhook
- campaign metadata
- testcampagne

### Fase 3 — Prijslijst
- HTML prijslijst koppelen
- link tracking
- mobile QA

### Fase 4 — Optimalisatie
- variant testing
- segment tuning
- auto-handoff in Econtrol Room / Telegram

## 8. Niet doen
- niet meteen iedereen mailen
- niet zonder testlijst versturen
- niet vertrouwen op Brevo als enige bron van waarheid
- geen losse tracking links zonder mapping register
