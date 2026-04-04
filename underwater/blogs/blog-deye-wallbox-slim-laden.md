# Deye Smart Wallbox: Slim Laden op Zonne-energie

> **Shopify Blog Instellingen:**
> - Blog: `kennis`
> - URL handle: `deye-wallbox-slim-laden-zonne-energie`
> - SEO Title: `Deye Smart Wallbox 22 kW: Slim Laden op Zonne-energie | EcoHandel`
> - SEO Description: `De Deye Smart Wallbox laadt je EV slim op zonne-energie via LoRa. 22 kW, 3 laadmodi, IP66 waterdicht. Bespaar €650+ per jaar. Alles over werking, installatie en prijs.`
> - Tags: `deye, wallbox, ev-lader, slim laden, zonne-energie, laadpaal, lora, solar laden`
> - Featured image: `充电枪.png` (Deye Smart Wallbox met laadkabel)
> - Author: EcoHandel

---

<!-- type: serie-nav -->

| Status | Titel | Beschrijving | Link |
|--------|-------|-------------|------|
| Deel 1 | Deye Smart Home & LoRa | Alle componenten en hoe ze samenwerken | /blogs/kennis/deye-smart-home-lora-systeem |
| **Actief — Je leest dit nu** | Deye Wallbox: Slim Laden | Laad je EV gratis met zonne-energie | — |
| Deel 3 — Binnenkort | Deye Copilot: AI Energiebeheer | Automatische optimalisatie met AI | /blogs/kennis/deye-copilot-ai-energiebeheer |

<!-- /serie-nav -->

---

Je hebt zonnepanelen op het dak. Overdag produceer je meer stroom dan je verbruikt. Maar je auto staat op kantoor. 's Avonds kom je thuis, plug je de auto in, en laadt hij van het net — tegen het duurdere avondtarief. Die gratis zonnestroom van overdag? Teruggeleverd aan het net voor een fractie van de prijs.

Dit is het scenario voor honderdduizenden Nederlandse huishoudens met zonnepanelen en een elektrische auto. De **Deye Smart Wallbox** lost dit op. Niet met ingewikkelde schema's of extra software, maar door de laadpaal direct te koppelen aan je Deye-omvormer via LoRa. Het resultaat: je auto laadt wanneer het slim is — op zonnestroom, op daltarief, of op vol vermogen als je haast hebt.

---

## Inhoudsopgave

1. [Wat is de Deye Smart Wallbox?](#wat)
2. [De 3 laadmodi uitgelegd](#laadmodi)
3. [Hoe werkt de LoRa-integratie?](#lora)
4. [Rekenvoorbeeld: hoeveel bespaar je?](#besparing)
5. [Installatie en vereisten](#installatie)
6. [Technische specificaties](#specs)
7. [Veelgestelde vragen](#faq)

---

## Wat is de Deye Smart Wallbox? {#wat}

<!-- type: productkaart -->
<!-- afbeelding: 充电枪.png -->
<!-- product-url: /products/deye-smart-wallbox-ac-charger-22-kw-slimme-ev-lader -->

De Deye Smart Wallbox (model **SUN-EVSE22K01-EU-AC**) is een intelligente AC-laadpaal voor elektrische auto's. Op een driefase-aansluiting levert hij tot **22 kW** (32A, 400V) — genoeg om een auto met een 60 kWh-accu in ongeveer 3 uur volledig te laden. Op enkelfase levert hij tot 7,4 kW.

Maar vermogen is niet wat deze wallbox bijzonder maakt. Het verschil zit in de intelligentie. De wallbox communiceert via **LoRa, WiFi en Bluetooth** en kan worden aangestuurd door een Deye hybride omvormer. Hierdoor laadt hij niet blind op vol vermogen, maar kijkt hij mee naar je zonne-opbrengst, je batterijniveau en de energieprijzen.

De wallbox is **IP66 waterdicht** (buiten plaatsbaar), heeft een standaard **Type 2 connector** en beschikt over 7-laags beveiliging: overstroom, overspanning, aardlek (inclusief DC 6mA), temperatuur, bliksem en meer. CE-gecertificeerd volgens EN IEC 61851-1.

`Specs: 22 kW driefase / 7,4 kW enkelfase | 6A-32A instelbaar | Type 2 | IP66 | LoRa + WiFi + BLE | 7-laags beveiliging | CE-gecertificeerd`

→ [Bekijk in de webshop](/products/deye-smart-wallbox-ac-charger-22-kw-slimme-ev-lader)

<!-- /productkaart -->

---

## De 3 laadmodi uitgelegd {#laadmodi}

De wallbox heeft drie laadmodi die je via de Deye Cloud app instelt. Elke modus is geschikt voor een ander scenario.

### Modus 1: Plug & Play — direct laden

Stekker erin, laden begint. De wallbox levert direct het maximale vermogen dat je aansluiting toestaat (tot 22 kW driefase). De laadstroom is instelbaar van 6A tot 32A via de app.

**Wanneer gebruik je dit?** Als je snel moet laden en het niet uitmaakt wat de stroom kost. Je komt thuis met een bijna lege accu en moet morgenochtend weer weg. Stekker erin, klaar.

### Modus 2: Time of Charge — laden op daltarief

Stel tot 4 tijdsloten in via de Deye Cloud app. De wallbox start en stopt automatisch binnen die tijden. Laad bijvoorbeeld alleen tussen 01:00 en 05:00 als stroom het goedkoopst is.

**Wanneer gebruik je dit?** Als je een dynamisch energiecontract hebt (Tibber, Frank Energie, ANWB Energie) of een dag/nachttarief. Je plugt de auto in als je thuiskomt, maar het laden begint pas als de prijs daalt. Je bespaart tientallen euro's per maand zonder er iets voor te hoeven doen.

### Modus 3: Solar Energy Only — laden op zonnestroom

Dit is de gamechanger. In deze modus laadt de wallbox **uitsluitend** met zonne-overschot. Je stelt een batterij-SOC-drempel in (bijvoorbeeld 80%) — pas als de thuisbatterij boven dat niveau zit, gaat de wallbox aan. Zo gaat je huishouden altijd voor.

**Hoe werkt het technisch?** De wallbox is via LoRa verbonden met de Deye hybride omvormer (via de [Smart Transmitter](/products/deye-smart-wireless-ct-meter-lora)). De [Wireless CT](/products/deye-smart-wireless-ct-meter-lora) in de meterkast meet real-time hoeveel overschot er is. De omvormer berekent hoeveel vermogen er naar de wallbox kan en stuurt dit door via LoRa — binnen 50 milliseconden. De wallbox past zijn laadstroom dynamisch aan: meer zon = meer laden, wolk ervoor = minder laden of pauzeren.

**Wat maakt dit anders dan andere wallboxen?** De meeste "slimme" wallboxen hebben WiFi en een cloud-app nodig om zonne-overschot te berekenen. Dat werkt, maar met vertraging (seconden) en het stopt als je internet uitvalt. De Deye wallbox communiceert lokaal via LoRa — geen internet nodig, latency van 50ms, en het werkt altijd.

<!-- type: keypoint -->
> **Het resultaat van Solar Energy Only:** Je auto laadt gratis met je eigen zonnestroom. Je thuisbatterij wordt niet leeggetrokken. Er gaat geen stroom terug naar het net tegen een laag tarief. En je hoeft er niets voor te doen — stekker erin, de rest regelt het systeem.
<!-- /keypoint -->

Meer over hoe het LoRa-ecosysteem als geheel werkt: → [Lees het Smart Home & LoRa artikel](/blogs/kennis/deye-smart-home-lora-systeem)

---

## Hoe werkt de LoRa-integratie? {#lora}

De slimme laadmodi (met name Solar Energy Only) werken alleen als de wallbox gekoppeld is aan een Deye hybride omvormer. De communicatieketen ziet er zo uit:

**Wireless CT** (in de meterkast) → meet real-time het overschot
↓ LoRa-signaal
**Smart Transmitter** (op de omvormer) → ontvangt de data
↓ intern
**Deye Omvormer** → berekent hoeveel vermogen beschikbaar is voor de wallbox
↓ LoRa-signaal
**Smart Wallbox** → past laadstroom aan (6A-32A)

Dit hele proces duurt minder dan 50 milliseconden. Ter vergelijking: een WiFi-systeem via de cloud doet er 1-3 seconden over. Bij energiebeheer is dat verschil cruciaal — in 3 seconden kan de zon achter een wolk verdwijnen en heb je al stroom van het net getrokken.

**Wat heb je nodig voor LoRa-modus?**
- Deye hybride omvormer (elke serie: enkelfase of driefase)
- [Deye Smart Transmitter (TX01)](/products/deye-smart-wireless-ct-meter-lora) — aangesloten op de Meter-poort
- [Deye Wireless CT (CT01)](/products/deye-smart-wireless-ct-meter-lora) — in de meterkast
- Deye Smart Wallbox

**Standalone WiFi-modus** (zonder omvormer): De wallbox werkt ook standalone via WiFi. Je hebt dan Plug & Play en Time of Charge, maar niet Solar Energy Only. Handig als je (nog) geen Deye-omvormer hebt maar de wallbox alvast wilt gebruiken.

---

## Rekenvoorbeeld: hoeveel bespaar je? {#besparing}

Laten we een concreet voorbeeld doorrekenen voor een gemiddeld Nederlands huishouden.

**Uitgangspunten:**
- Elektrische auto, 15.000 km per jaar
- Verbruik: 18 kWh per 100 km
- Totaal laden per jaar: **2.700 kWh**

**Scenario A: Laden van het net (geen slimme wallbox)**
- Gemiddelde stroomprijs: €0,30/kWh
- Jaarlijkse laadkosten: **€810**

**Scenario B: Laden op zonne-overschot (Solar Energy Only)**
- Kosten zonnestroom: ~€0,06/kWh (terugverdientijd panelen meegerekend)
- Stel 70% van het laden gaat op zonnestroom, 30% op daltarief (€0,15/kWh)
- Jaarlijkse laadkosten: (1.890 kWh × €0,06) + (810 kWh × €0,15) = €113 + €122 = **€235**
- **Besparing: €575 per jaar**

**Scenario C: Laden op zonnestroom + Deye Copilot (dynamisch tarief)**
- Copilot optimaliseert het resterende 30% laden naar de allergoedkoopste uren
- Gemiddeld daltarief via Copilot: €0,08/kWh in plaats van €0,15
- Jaarlijkse laadkosten: (1.890 × €0,06) + (810 × €0,08) = €113 + €65 = **€178**
- **Besparing: €632 per jaar**

<!-- type: keypoint -->
> **Terugverdientijd:** De Deye Smart Wallbox kost €549 excl. BTW. Bij een besparing van €575-€632 per jaar is de wallbox in **minder dan 1 jaar** terugverdiend. Elk jaar daarna is pure winst.
<!-- /keypoint -->

Meer over Deye Copilot en hoe het je laadstrategie automatisch optimaliseert: → [Lees het Copilot-artikel (binnenkort)](/blogs/kennis/deye-copilot-ai-energiebeheer)

---

## Installatie en vereisten {#installatie}

### Elektrische aansluiting
- **Driefase (22 kW):** Vereist een 3-fase 32A aansluiting op een eigen groep in de meterkast met passende zekering. Dit is de standaard voor nieuwbouwwoningen in Nederland.
- **Enkelfase (7,4 kW):** Werkt op een 1-fase 32A aansluiting. Lagere laadsnelheid maar geschikt voor oudere woningen.
- Installatie **moet** worden uitgevoerd door een gekwalificeerd elektricien. Dit is wettelijk verplicht vanwege de hoge vermogens.

### LoRa-koppeling (optioneel maar aanbevolen)
- Deye hybride omvormer met Meter-poort
- Smart Transmitter (TX01) aangesloten op de Meter-poort
- Wireless CT (CT01) in de meterkast
- De wallbox wordt aangesloten op een AC-poort van de omvormer
- Pairing via de Deye Cloud app — eenmalige configuratie

### Standalone installatie
- Zonder Deye-omvormer werkt de wallbox via WiFi
- Je hebt dan Plug & Play en Time of Charge, maar geen Solar Energy Only
- Later upgraden naar LoRa-modus kan altijd, zonder de wallbox te vervangen

### EcoHandel support
Als [EcoHandel PRO partner](/pages/installatie-partners) krijg je technische ondersteuning bij de installatie en configuratie — remote of op locatie. Voor particulieren koppelen we je aan een [gecertificeerde installateur](/pages/professionele-installatiehulp-voor-particulieren) in jouw regio.

---

## Technische specificaties {#specs}

<!-- type: vergelijkingstabel -->

| Eigenschap | Specificatie |
|---|---|
| **Model** | SUN-EVSE22K01-EU-AC |
| **Max. vermogen** | 22 kW (driefase) / 7,4 kW (enkelfase) |
| **Laadstroom** | 6A – 32A (instelbaar via app) |
| **Connector** | Type 2 (IEC 62196-2) |
| **Communicatie** | LoRa + WiFi + Bluetooth |
| **Beschermingsgraad** | IP66 (buiten plaatsbaar) |
| **Beveiliging** | 7-laags: overstroom, overspanning, aardlek, DC 6mA, temperatuur, bliksem, kortsluiting |
| **Laadmodi** | Plug & Play, Time of Charge (4 tijdsloten), Solar Energy Only |
| **Certificering** | CE, EN IEC 61851-1:2019, EN IEC 62752-1:2023, RoHS 2.0 |
| **Compatibiliteit** | Alle Deye hybride omvormers (via LoRa + Smart TX) of standalone (WiFi) |
| **App** | Deye Cloud (iOS + Android) |
| **Kabel** | Geïntegreerd, Type 2 |
| **Garantie** | 2 jaar |

<!-- /vergelijkingstabel -->

---

## Veelgestelde vragen {#faq}

<!-- type: faq-accordion -->

**Heb ik een Deye-omvormer nodig voor de wallbox?**
Nee. De wallbox werkt ook standalone via WiFi met Plug & Play en Time of Charge. Maar voor de Solar Energy Only modus (laden op zonne-overschot) heb je een Deye hybride omvormer + Smart Transmitter nodig. We raden de LoRa-koppeling sterk aan als je zonnepanelen hebt.

**Kan ik de wallbox later upgraden naar LoRa?**
Ja. Als je nu de wallbox standalone installeert en later een Deye-omvormer koopt (of al hebt), hoef je alleen een Smart Transmitter (TX01) toe te voegen. De wallbox zelf blijft dezelfde — je activeert de LoRa-koppeling via de Deye Cloud app.

**Werkt de wallbox met mijn elektrische auto?**
Ja. De wallbox heeft een standaard Type 2 connector die compatibel is met vrijwel alle elektrische auto's die in Europa worden verkocht (Tesla, VW, Hyundai, BMW, Mercedes, Renault, Peugeot, etc.). Tesla-rijders kunnen de meegeleverde adapter gebruiken of direct laden via Type 2.

**Kan de wallbox buiten worden geplaatst?**
Ja. Met IP66 bescherming is de wallbox volledig waterdicht en bestand tegen stof, regen en vorst. Hij kan zonder problemen buiten aan de muur of op een paal worden gemonteerd.

**Hoe snel laadt de wallbox mijn auto?**
Op 22 kW (driefase): ~110-130 km range per uur. Een 60 kWh accu gaat van 10% naar 100% in ~3 uur. Op 7,4 kW (enkelfase): ~35-40 km range per uur, volledig laden in ~8-9 uur (overnacht).

**Wat kost de Deye Smart Wallbox?**
€549 excl. BTW bij EcoHandel. Installateurs met een [EcoHandel PRO partneraccount](/pages/installatie-partners) profiteren van dealerprijzen.

<!-- /faq-accordion -->

---

<!-- type: cta-blok -->
<!-- variant: donker -->

**Klaar om slim te laden?**

De Deye Smart Wallbox is direct leverbaar bij EcoHandel. Combineer met een Wireless CT en Smart Transmitter voor volledig solar laden.

→ [Bekijk de Smart Wallbox](/products/deye-smart-wallbox-ac-charger-22-kw-slimme-ev-lader)
→ [Bekijk Wireless CT + Smart TX](/products/deye-smart-wireless-ct-meter-lora)
→ [Word installatiepartner](/pages/installatie-partners)

<!-- /cta-blok -->

---

<!-- type: serie-nav -->

**Meer uit de serie: Deye Smart Energy Ecosysteem**

| Status | Titel | Beschrijving | Link |
|--------|-------|-------------|------|
| Deel 1 | Deye Smart Home & LoRa | Het complete ecosysteem uitgelegd | /blogs/kennis/deye-smart-home-lora-systeem |
| Deel 3 | Deye Copilot: AI Energiebeheer | Automatische optimalisatie op stroomprijzen en weer | /blogs/kennis/deye-copilot-ai-energiebeheer |
| Assortiment | Alle Deye Accessoires | CT-meters, transmitters, kabels en meer | /collections/accessoires-toebehoren |

<!-- /serie-nav -->

---

> **Afbeeldingen voor dit artikel:**
>
> | Bestandsnaam in project | Gebruik als | Alt-tekst |
> |---|---|---|
> | 充电枪.png | Featured image + productkaart | Deye Smart Wallbox 22kW EV-lader met Deye-logo en laadkabel |
> | 充电枪2.png | Extra productfoto (zijaanzicht) | Deye Smart Wallbox zijaanzicht met kabelophanging |
> | 智能接收器2.png | Bij LoRa-integratie sectie (optioneel) | Deye Smart Transmitter TX01 |
> | CT2.png | Bij LoRa-integratie sectie (optioneel) | Deye Wireless CT Meter voorkant |
