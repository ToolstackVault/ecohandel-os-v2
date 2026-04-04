# Lead Scoring Model — EcoHandel Partner Campaign

## Doel
Hot prospects niet op gevoel bepalen, maar met een uitlegbaar model dat aansluit op partner-intentie.

## Scorelagen
Er zijn twee scores:
- **lead_score** = structurele fit van de lead
- **hot_score** = actuele koop-/opvolgintentie gebaseerd op gedrag

## 1. Lead Score (fit)
Startscore op basis van basisfit:

### Warmte uit research
- `WARM` = +25
- `MIDDEL-WARM` = +18
- `MIDDEL` = +10
- onbekend = +0

### Deye fit
- `JA` of Deye dealer / verkoopt Deye = +20
- `ONBEKEND` = +5
- `NIET` = +0

### Batterij ervaring
- duidelijke batterijervaring = +15
- zakelijk batterijaanbod = +18
- onbekend = +0

### Contactkwaliteit
- email aanwezig = +10
- telefoon aanwezig = +8
- contactpersoon bekend = +8

### Strategische fit
- landelijke dekking = +10
- regionale installateur in relevante regio = +6
- sterk zakelijk / netcongestie profiel = +12

## 2. Hot Score (actuele intentie)
### Email engagement
- delivered = +1
- eerste open = +3
- extra open = +2 per keer
- unieke click = +12
- extra click = +7
- prijslijst click = +18
- product click = +22
- meerdere product clicks binnen 72h = +15 bonus

### Menselijk signaal
- reply ontvangen = +45
- duidelijke interesse-reply = +60
- vraag om terugbellen / prijs / dealerinfo = +70

### Tijdscomponent
- activiteit <24h = +20
- activiteit <72h = +12
- activiteit <7d = +5

### Negatieve signalen
- unsubscribe = -100 en direct uitsluiten
- hard bounce = -120 en direct uitsluiten
- soft bounce = -40
- 0 engagement na meerdere sends = -10 tot -30

## Statusregels
- `validated` = basislead klaar voor campagne
- `queued_for_campaign` = op verzendlijst
- `sent` = mail verstuurd
- `engaged` = minimaal open of click
- `hot` = hot_score >= 60 of belangrijke clickcombi
- `replied` = reply ontvangen
- `qualified` = handmatig/agent bevestigd als interessante partner
- `customer` = deal / partner actief
- `unsubscribed` = nooit meer mailen
- `bounced` = deliverability probleem
- `dead` = geen zinvolle vervolgactie meer

## Hot prospect beslisregels
Een lead is hot als één van deze geldt:
- reply ontvangen
- 1 productclick + WARM lead
- prijslijst click + 2+ opens binnen 72h
- hot_score >= 60

## Recommended action mapping
- `reply_count > 0` => **BEL VANDAAG**
- `product_clicks >= 1` => **HANDMATIG OPVOLGEN**
- `price_list_clicks >= 1 && open_count >= 2` => **OPVOLGEN**
- `open_count >= 2 && click_count = 0` => **NOG EVEN LATEN LOPEN**
- `unsubscribe/bounce` => **UITSLUITEN**

## Belangrijke regel
Replies en productintentie wegen veel zwaarder dan opens. Open-only leads zijn interessant, maar nog geen echte koopintentie.
