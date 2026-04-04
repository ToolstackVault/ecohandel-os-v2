# Launchplan — EcoHandel Partner Mailcampagne (morgen)

## Doel van morgen
De eerste live EcoHandel partner-mailcampagne gecontroleerd uitsturen in **3 batches van 10**, zodat we direct kunnen leren welke combinatie van doelgroep + mailhoek + timing het beste werkt.

## Vaststaande uitgangspunten
- Alleen **EcoHandel** leads gebruiken
- **Lokale database / workspace** blijft bron van waarheid
- **Brevo** alleen gebruiken als verzend- en eventlaag
- Geen brede blast; eerst gecontroleerde test met 30 leads

---

## Beslisblad voor morgen

### 1. Voor 08:30 — preflight check
Check dit vóór de eerste batch live gaat:
- [ ] lijst `2026-03-28_top30_launch_leads.csv` is definitieve bron
- [ ] geen interne / ongewenste adressen in de 30 geselecteerde leads
- [ ] elke batch heeft exact 10 unieke emailadressen
- [ ] onderwerpregel, CTA en campaign key per batch staan vast
- [ ] Brevo sender = `info@ecohandel.nl`
- [ ] links wijzen naar de juiste partnerprijslijst + juiste UTM/campaign key
- [ ] unsubscribe werkt
- [ ] reply-to klopt
- [ ] lokale DB-status voor deze 30 leads op `queued_for_campaign` of equivalent gezet vóór verzending

### 2. Verzendschema
| Tijd | Batch | Segment | Variant | Primaire KPI |
|---|---|---|---|---|
| 08:45 | B1 | Warm / Deye-fit | A | Replies + hot leads |
| 11:45 | B2 | Regionale batterij-installateurs | B | Opens + prijslijstclicks |
| 15:15 | B3 | Challenger / switch prospects | B-challenger | Validatie van tractie |

### 3. Go / no-go regels tussen batches
**Na batch 1 (rond 11:00):**
- Go door als deliverability normaal is en er geen duidelijke fout in rendering/links zit
- Pauzeer als bounce-rate > 5% of als CTA-link kapot is

**Na batch 2 (rond 14:15):**
- Go door met batch 3 als tracking goed binnenkomt en unsubscribe/bounces laag blijven
- Pauzeer als event logging niet consistent binnenloopt in lokale data

---

## Evaluatiecriteria voor morgen

### Opens
- **Goed:** ≥ 45%
- **Twijfelachtig:** 30%–44%
- **Zwak:** < 30%

### Clicks (unieke klik naar prijslijst / product)
- **Goed:** ≥ 8%
- **Sterk:** ≥ 12%
- **Zwak:** < 5%

### Replies
- **Goed:** ≥ 1 reply per batch
- **Sterk:** ≥ 2 replies per batch
- **Topscore:** een reply met concrete vraag over prijzen, levering, dealerinfo of terugbelverzoek

### Hot leads
Lead wordt voor opvolging als **hot** gemarkeerd als één van deze signalen binnenkomt:
- reply ontvangen
- prijslijst click + 2 opens binnen 72 uur
- product click
- hot_score >= 60

### Negatieve signalen
- **Hard bounce:** direct uitsluiten
- **Unsubscribe:** direct uitsluiten
- **Soft bounce:** monitoren, niet meteen opnieuw mailen

---

## Handmatige follow-up regels

### Meteen dezelfde dag oppakken
- reply met vraag over samenwerking
- productclick of meerdere clicks in korte tijd
- prijslijstclick gecombineerd met meerdere opens

### Volgende werkdag oppakken
- alleen opens, nog geen click
- 1 prijslijstclick zonder reply

### Niet direct najagen
- geen opens en geen clicks
- unsubscribes / bounces

---

## Wat na de laatste batch moet gebeuren
- [ ] Brevo events ophalen / valideren
- [ ] lokale DB updaten met send/open/click/reply signalen
- [ ] hot leads export draaien
- [ ] batchvergelijking maken: open rate, CTR, replies, hot leads, bounces
- [ ] winnaar bepalen voor volgende wave

## Eerste beslisregel voor vervolgwave
- **Beste op replies/hot leads** wint boven beste open rate
- Als batch 1 en 2 dicht bij elkaar liggen, kies de variant met de hoogste kwalitatieve replies
- Batch 3 alleen schalen als daar aantoonbaar klik- of replypotentieel uit komt

## Praktische conclusie
Voor morgen draait succes niet om volume, maar om een schone eerste dataset. Liever 30 strak gemeten leads dan 130 halfblind verstuurd.
