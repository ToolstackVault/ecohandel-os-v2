# Interactive Price List Linking Spec

## Doel
De prijslijst moet een commerciële tool zijn, geen statische PDF-vervanger.

## Functionele eisen
- mobile responsive
- snelle scanbaarheid op telefoon
- duidelijke CTA's
- elke relevante regel linkt door naar het echte Shopify product of juiste collectie
- klikdata moet terug naar campaign intelligence

## Linktypes
### 1. Product links
Voor exact productdetailverkeer.

Voorbeeld:
- Deye SUN-12K-SG04LP3-EU -> exacte product URL

### 2. Collection links
Als een item meerdere varianten heeft of voorraad wisselt.

Voorbeeld:
- Deye omvormers -> `/collections/deye-omvormers`

### 3. CTA links
Voor partner worden / contact / advies / offerte.

## Tracking parameters
Elke link krijgt minimaal:
- `utm_source=brevo`
- `utm_medium=email`
- `utm_campaign=<campaign_slug>`
- `utm_content=<link_key>`

Optioneel:
- `lead=<lead_id>` of unieke contact token als privacy/techniek dit toestaat

## Link register
Alle links moeten eerst in `tracked_links` worden geregistreerd met:
- label
- link_key
- destination_url
- link_type
- product_handle / collection_handle indien van toepassing

## Mobile UX regels
- tabel alleen als cards op mobiel goed leesbaar zijn
- prijzen groot en duidelijk
- CTA knop altijd zichtbaar zonder rare horizontale scroll
- klikdoelen minimaal duimvriendelijk

## Contentvolgorde
Mijn voorstel voor de prijslijst:
1. korte intro voor partners
2. voordelen van EcoHandel partnership
3. productblokken / prijsblokken
4. CTA naar partner worden
5. CTA naar direct contact / offerte

## Niet doen
- geen dode links
- geen losse spreadsheets zonder tracking
- geen PDF als hoofdroute
- geen links naar verkeerde varianten of niet-bestaande producten
