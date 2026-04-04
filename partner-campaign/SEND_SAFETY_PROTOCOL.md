# Send Safety Protocol — EcoHandel Partner Campaign

## Doel
Nooit meer onduidelijkheid over:
- is een batch echt verstuurd?
- naar wie precies?
- kunnen we veilig opnieuw sturen zonder dubbel risico?

## Nieuwe harde regel
De huidige EcoHandel mailflow gebruikt voor partnerbatches **Brevo Campaigns API** met een lokale DB-laag.
Voor echte verificatie gebruik je daarom **beide bronnen samen**:
- `emailCampaigns` / contact statistics voor campaign delivery/open/click
- `/smtp/statistics/events` voor partner-aanvraag notificaties naar `info@ecohandel.nl`

**De lokale DB blijft leidend** voor eigen scoring en event-koppeling.

## Verplichte flow vóór elke live batch
1. Draai eerst een dry-run:
   ```bash
   python3 scripts/send_batch_campaign.py B1 --dry-run
   ```
2. Controleer blokkades:
   - `already_seen_in_brevo_transactional_events`
   - `already_marked_sent_in_local_db`
3. Alleen als de batch schoon is, live versturen:
   ```bash
   python3 scripts/send_batch_campaign.py B1
   ```
4. Daarna direct verificatie draaien:
   ```bash
   python3 scripts/fetch_brevo_stats.py
   ```
5. Pas daarna Econtrol Room / Telegram update.

## Idempotency guard
`send_batch_campaign.py` test veiliger dan voorheen:
- `--test-email` maakt altijd een **nieuwe testlijst + nieuwe testcampagne** aan
- daardoor worden oude testresultaten niet vermengd met nieuwe validatie
- live batches blijven beschermd door lokale DB-status en gecontroleerde batchinput

## Wat telt als bewijs van verzending
Minimaal deze set moet kloppen:
- Brevo campaign stats tonen sent/delivered/open/click voor de test/live campagne
- lokale `lead_campaigns` entry heeft `send_status=sent` en `sent_at`
- partnerbutton-click / aanvraag verschijnt in `partner-aanvragen.ndjson` en wordt daarna ingelezen in DB
- notificatiemail naar `info@ecohandel.nl` krijgt Brevo `requests`/`delivered` events

## Brand-assets regel
- Maillogo's mogen nooit naar tijdelijke of prijslijst-specifieke routes wijzen
- Gebruik alleen vaste publieke asset-paden onder:
  - `https://control.ecohandel.nl/assets/brand/partner-campaign/`
- Het verzendscript moet vóór campaign create/send valideren dat beide logo-URLs `200 OK` geven en `image/*` teruggeven
- Als die check faalt: niet verzenden, eerst assetlaag repareren

## Nooit meer doen
- alleen vertrouwen op reminders of batchplannen
- alleen `emailCampaigns` checken bij transactional sends
- live batches versturen zonder dry-run guard
- batchstatus communiceren zonder echte verzendbron

## Praktische commando's
### Batch verifiëren zonder te sturen
```bash
python3 scripts/send_batch_campaign.py B1 --dry-run
python3 scripts/send_batch_campaign.py B2 --dry-run
python3 scripts/send_batch_campaign.py B3 --dry-run
```

### Batch echt sturen
```bash
python3 scripts/send_batch_campaign.py B1
```

### Transactional waarheid verversen
```bash
python3 scripts/fetch_brevo_stats.py
```
