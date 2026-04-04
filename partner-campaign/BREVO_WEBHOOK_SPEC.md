# Brevo Webhook Spec — EcoHandel Partner Campaign

## Doel
Alle relevante campaign events terugschrijven naar de lokale partner database zodat Jean Clawd engagement kan meten, hot prospects kan scoren en daily handoffs kan doen.

## Benodigde eventtypes
Minimaal verwerken:
- delivered
- opened
- clicked
- unsubscribe
- hard_bounce
- soft_bounce
- spam (indien beschikbaar)
- reply (via aparte inbox/reply verwerking indien Brevo marketing webhook dat niet rechtstreeks levert)

## Gewenste webhook payload-uitkomst
Voor elk event willen we kunnen achterhalen:
- emailadres
- campaign ID / naam
- event type
- event timestamp
- link URL / link key (bij click)
- user agent / IP als beschikbaar
- eventuele contact metadata

## Matching strategie
1. Match eerst op emailadres
2. Match daarna op campaign ID
3. Clicks matchen indien mogelijk op `link_key` of tracking URL
4. Bij mismatch event toch opslaan in `events`, maar markeren als unmatched in `meta_json`

## Verwerking per event
### delivered
- update `lead_campaigns.send_status = delivered`
- set `sent_at` indien leeg

### opened
- verhoog open counters
- zet `first_open_at` indien leeg
- update `last_open_at`
- update `leads.last_activity_at`

### clicked
- verhoog click counters
- koppel tracked link
- update `leads.last_activity_at`
- score omhoog

### unsubscribe
- zet `leads.unsubscribed = 1`
- zet `leads.do_not_contact = 1`
- zet `leads.status = unsubscribed`

### hard_bounce / soft_bounce
- zet bounce counters
- hard bounce => `do_not_contact = 1`
- status naar `bounced`

### reply
- entry in `replies`
- `leads.replied = 1`
- status naar `replied` of `hot`
- extra scoreboost

## Beveiliging
- webhook secret of signature valideren zodra Brevo-config bekend is
- alleen POST accepteren
- raw payload altijd loggen
- duplicate event handling op basis van event id/hash

## Testplan
1. testlijst maken met 1-3 adressen
2. campaign versturen
3. open event valideren
4. click event valideren
5. unsubscribe test uitvoeren
6. bounce simuleren indien mogelijk
7. reply-flow apart controleren
