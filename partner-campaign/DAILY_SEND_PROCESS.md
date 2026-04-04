# Daily Send Process — EcoHandel Partner Campaign

## Doel
Elke werkdag een repeteerbare, veilige vaste flow:
- **09:00** → variant **A**
- **12:00** → variant **B**
- standaard **10 unieke leads per slot**
- aantallen later aanpasbaar via config
- nooit dubbel mailen naar leads die al in eerdere batches zijn opgenomen

## Source of truth
- Config: `ecohandel/partner-campaign/daily_send_config.json`
- Batch generator: `scripts/prepare_daily_batches.py`
- Slot sender: `scripts/send_daily_slot.py`
- Verzender: `scripts/send_batch_campaign.py`

## Harde regels
1. **Variant A niet meer inhoudelijk aanpassen** zonder expliciet akkoord van Milan.
2. Variant B blijft technisch/verzendbaar, maar inhoud alleen wijzigen met akkoord.
3. Alleen **unieke leads**:
   - geen leads met bestaande `lead_campaigns` records in status `queued`, `ready` of `sent`
4. Geen leads met:
   - `do_not_contact = 1`
   - `unsubscribed = 1`
   - `bounced = 1`
   - status `replied`, `unsubscribed`, `bounced`
5. Geen Nova-Cell / interne testadressen in live daily batches.

## Dagelijkse flow
### 1. Voorbereiden
```bash
python3 scripts/prepare_daily_batches.py
```
Maakt per dag:
- `launch/daily/YYYY-MM-DD/schedule.json`
- `launch/daily/YYYY-MM-DD/A0900.csv`
- `launch/daily/YYYY-MM-DD/B1200.csv`

### 2. Ochtendslot verzenden
```bash
python3 scripts/send_daily_slot.py A0900
```
Doet:
- batches voorbereiden als ze nog niet bestaan
- variant A verzenden volgens de dagbatch
- daarna `run_daily_cycle.py`
- daarna `fetch_brevo_stats.py`

### 3. Middagslot verzenden
```bash
python3 scripts/send_daily_slot.py B1200
```
Doet hetzelfde voor variant B.

## Config aanpassen
Bestand: `daily_send_config.json`

Voorbeeld:
```json
{
  "slots": [
    { "key": "A0900", "variant": "A", "send_time": "09:00", "count": 10 },
    { "key": "B1200", "variant": "B", "send_time": "12:00", "count": 10 }
  ]
}
```

Als Milan later 15 + 15 wil of 20 + 10:
- alleen `count` aanpassen
- geen codewijziging nodig

## Selectielogica
### Variant A — 09:00
Voorrang voor:
- warmste leads
- duidelijke Deye-fit
- batterijervaring
- hoogste leadscore

### Variant B — 12:00
Voorrang voor:
- resterende batterij/installer-fit
- daarna warmte
- daarna leadscore/hotscore

## Verwachte output
Per dag een volledig herleidbare batchset met:
- datum-map
- schedule.json
- CSV per slot
- unieke recipients
- vaste campaign key per datum + slot

## Belangrijk
Deze flow is gebouwd voor **repeteerbaarheid** en **auditbaarheid**:
- elke dag exact dezelfde machine
- geen handmatig gepruts met losse CSV's
- aantallen instelbaar
- dubbele leads structureel voorkomen
