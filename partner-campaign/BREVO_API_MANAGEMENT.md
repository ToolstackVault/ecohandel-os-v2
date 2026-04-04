# Brevo API Management — EcoHandel

Deze beheerlaag is de praktische API-bediening voor de EcoHandel partner-campaign.

## Doel
Gebruik Brevo niet alleen als verzendlaag, maar ook als beheerlaag voor:
- account/status checks
- contactlijsten bekijken
- nieuwe lijsten aanmaken
- CSV-contacten importeren in een gekozen lijst
- recente campagnes controleren

## Script
- `scripts/brevo_api.py`

## Voorwaarden
- `config.local.json` moet gevuld zijn
- Brevo API key van EcoHandel moet actief zijn

## Voorbeelden

### 1. Status check
```bash
python3 ecohandel/partner-campaign/scripts/brevo_api.py status
```

### 2. Lijsten bekijken
```bash
python3 ecohandel/partner-campaign/scripts/brevo_api.py lists --limit 50
```

### 3. Campagnes bekijken
```bash
python3 ecohandel/partner-campaign/scripts/brevo_api.py campaigns --limit 20
```

### 4. Nieuwe lijst maken
```bash
python3 ecohandel/partner-campaign/scripts/brevo_api.py create-list "EcoHandel Partners Test"
```

### 5. CSV importeren in een lijst
```bash
python3 ecohandel/partner-campaign/scripts/brevo_api.py import-csv 123 ecohandel/partner-campaign/data/ECOHANDEL_LEADS_READY.csv --email-column email
```

## Belangrijke regels
- eerst testen met een kleine lijst
- nooit direct de hele leadvoorraad blind importeren
- lokale database blijft bron van waarheid
- Brevo wordt gebruikt voor transport, lijstbeheer en campagnezicht
- webhook- en engagementdata moeten terug de lokale DB in

## Aanbevolen werkwijze
1. `status`
2. `lists`
3. testlijst aanmaken
4. kleine CSV batch importeren
5. campagne aanmaken/checken
6. events terug laten landen via webhook + lokale ingest

## Opmerking over webhook URL
Gebruik voor live instellingen de tokenized route:
- `https://control.ecohandel.nl/hooks/brevo/partner-campaign/?token=<BREVO_ECOHANDEL_WEBHOOK_SECRET>`
