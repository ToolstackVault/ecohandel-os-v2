# EcoHandel Partnercampagne — Send Plan 2026-04-09

## Doel
- Totaal **50 live mails**
- **25 mails om 09:00** via slot `A0900`
- **25 mails om 12:00** via slot `B1200`
- Tracking is topprioriteit: campaign-status, delivered, opens, clicks, bounces en prijslijst-CTA attributie moeten schoon blijven.

## Source of truth
- Config: `ecohandel/partner-campaign/daily_send_config.json`
- Master prijslijst live: `https://control.ecohandel.nl/partners/p/a7x9kQ3m/`
- Process doc: `ecohandel/partner-campaign/DAILY_SEND_PROCESS.md`

## Vastgezet op 2026-04-08
### Config
- `A0900.count = 25`
- `B1200.count = 25`
- `unique_leads_only = true`

### Geplande runs
- `08:50` prepare batches
- `09:00` send A0900
- `09:20` tracking check A0900
- `12:00` send B1200
- `12:20` tracking check B1200
- `15:30` full tracking check A0900 + B1200

## Harde campaign guards
1. Alleen unieke leads
2. Geen interne/test/Nova-Cell adressen
3. Geen bestaande `queued` / `ready` / `sent` leads opnieuw opnemen
4. Geen `unsubscribed`, `bounced`, `replied`, `do_not_contact`
5. Prijslijst-link + `cid` + campaign-context moeten leidend blijven voor attributie
6. Geen oude testcampaign-state hergebruiken voor validatie
7. Na send altijd stats sync + state refresh

## Kritieke trackingwaarheid
Brevo is verzendwaarheid.
De lokale campaign DB / cockpit is trackingwaarheid voor interpretatie.
Die twee moeten morgen expliciet gelijk blijven.

## Verwachte output
- Dagbatchs gegenereerd met 25 + 25
- Twee live sends op tijd
- Korte Telegram updates alleen bij echte statusdata
- Schone attribueerbare tracking op prijslijst-CTA

## Note
Als een check mislukt of een anomalie ziet, moet exact de failure gemeld worden in plaats van stil doorlopen.
