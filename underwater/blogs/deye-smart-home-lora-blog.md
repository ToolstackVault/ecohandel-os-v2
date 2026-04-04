# Deye Smart Home Systeem: Alles Draadloos Aansturen via LoRa

> **Shopify Blog Instellingen:**
> - Blog: `kennis`
> - URL handle: `deye-smart-home-lora-systeem`
> - SEO Title: `Deye Smart Home Systeem: Draadloos Energiebeheer met LoRa | EcoHandel`
> - SEO Description: `Het Deye Smart Home systeem verbindt omvormer, batterij, laadpaal en apparaten via LoRa. Draadloos energiebeheer zonder internet. Uitleg van alle componenten, werking en voordelen.`
> - Tags: `deye, smart home, lora, energiebeheer, wireless ct, smart transmitter, wallbox, smart plug`
> - Featured image: `合集_2.png` (gelabelde collectie met Smart TX, Smart EV Charger, Smart Plug, Wireless CT, Smart Switch)
> - Author: EcoHandel

---

<!-- SERIE-NAVIGATIE: 3 kaarten naast elkaar -->
<!-- type: serie-nav -->

| Status | Titel | Beschrijving | Link |
|--------|-------|-------------|------|
| **Actief — Je leest dit nu** | Deye Smart Home & LoRa | Alle componenten en hoe ze samenwerken | — |
| Deel 2 — Binnenkort | Deye Wallbox: Slim Laden | Laad je EV gratis met zonne-energie | /blogs/kennis/deye-wallbox-slim-laden-zonne-energie |
| Deel 3 — Binnenkort | Deye Copilot: AI Energiebeheer | Automatische optimalisatie met AI | /blogs/kennis/deye-copilot-ai-energiebeheer |

<!-- /serie-nav -->

---

De meeste thuisbatterij-systemen in Nederland werken als losstaande apparaten. De omvormer laadt en ontlaadt de batterij op vaste tijden, maar heeft geen idee wat de rest van je huis doet. Je boiler draait als de zon schijnt maar de batterij al vol is. Je auto laadt 's avonds van het net terwijl er overdag zonnestroom genoeg was. Je wasmachine start wanneer jij op de knop drukt — niet wanneer het energetisch slim is.

Deye heeft hier een compleet ander antwoord op gebouwd: een **draadloos energiemanagementsysteem op basis van LoRa-technologie** dat de omvormer tot het brein van je woning maakt. Niet alleen voor de batterij, maar voor je hele huishouden — van wasmachine tot laadpaal.

In dit artikel leggen we uit hoe dit systeem werkt, welke componenten erbij horen, en waarom dit voor installateurs en woningeigenaren een fundamentele stap vooruit is. **EcoHandel levert alle componenten en biedt technische ondersteuning bij configuratie en installatie.**

---

## Inhoudsopgave

1. [Wat is LoRa — en waarom gebruikt Deye het?](#lora)
2. [De 5 componenten van het systeem](#componenten)
3. [Hoe werkt het als geheel? Een praktijkvoorbeeld](#werking)
4. [LoRa vs. WiFi: technische vergelijking](#vergelijking)
5. [Wat betekent dit voor installateurs?](#installateurs)
6. [Beschikbaarheid en prijzen](#producten)
7. [Veelgestelde vragen](#faq)

---

## Wat is LoRa — en waarom gebruikt Deye het? {#lora}

**LoRa** staat voor *Long Range* en is een draadloze communicatietechnologie die werkt op vrije radiofrequenties (868 MHz in Europa). Het is ontwikkeld door chipfabrikant Semtech en wordt wereldwijd ingezet voor IoT-toepassingen — van slimme landbouw tot industriële sensoren. En nu dus ook voor residentieel energiebeheer.

Het verschil met WiFi is fundamenteel. WiFi-apparaten sturen hun data via je router naar een cloudserver en weer terug. Dat werkt, maar het introduceert vertraging (honderden milliseconden tot seconden) en is afhankelijk van je internetverbinding. Als je internet uitvalt, stopt de communicatie.

LoRa werkt anders. De communicatie gaat **direct en lokaal** — van apparaat naar omvormer, zonder internet, zonder cloud, zonder router. De latency is slechts ~50 milliseconden. Het signaal penetreert moeiteloos door meerdere betonmuren en heeft een bereik tot 200 meter in gebouwen. En het verbruikt vrijwel geen stroom.

<!-- type: keypoint -->
> **Waarom dit ertoe doet:** Bij energiebeheer telt elke milliseconde. Als je omvormer moet beslissen of er zonne-overschot naar de batterij, de boiler of de laadpaal gaat, kan een vertraging van twee seconden (zoals bij WiFi via de cloud) betekenen dat die energie al aan het net is teruggeleverd. Met LoRa reageert het systeem real-time — elke watt gaat naar de juiste plek.
<!-- /keypoint -->

---

## De 5 componenten van het Deye Smart Home systeem {#componenten}

Het systeem is modulair opgebouwd. In het midden staat altijd een **Deye hybride omvormer** — die wordt het controlecentrum. Daaromheen kun je stap voor stap apparaten toevoegen. Elk component communiceert draadloos via LoRa met de omvormer.

### 1. Deye Smart Transmitter (SUN-SMART-TX01)

<!-- type: productkaart -->
<!-- afbeelding: 智能接收器2.png -->
<!-- product-url: /products/deye-smart-wireless-ct-meter-lora -->

**De hub — maakt je omvormer LoRa-geschikt**

De Smart Transmitter wordt aangesloten op de Meter-poort van je Deye hybride omvormer. Het is een klein DIN-rail apparaat met een LoRa-antenne dat de brug vormt tussen de omvormer en alle andere draadloze apparaten in het systeem.

**Zonder de Smart Transmitter is er geen LoRa-netwerk.** Dit is altijd het eerste component dat je installeert als je het draadloze ecosysteem wilt activeren. De installatie is plug-and-play: aansluiten op de Meter-poort, antenne bevestigen, klaar.

`Specs: DIN-rail montage | LoRa 868 MHz | Meter-poort aansluiting | Compatibel met alle Deye hybride omvormers`

→ [Bekijk in de webshop](/products/deye-smart-wireless-ct-meter-lora)

<!-- /productkaart -->

---

### 2. Deye Wireless CT (SUN-SMART-CT01)

<!-- type: productkaart -->
<!-- afbeelding: CT2.png -->
<!-- product-url: /products/deye-smart-wireless-ct-meter-lora -->

**Draadloze energiemeting — het zenuwstelsel**

De Wireless CT wordt in de meterkast geplaatst (DIN-rail) en meet de complete energiestroom van je woning: spanning, stroom, vermogen, frequentie, power factor en energie — **elke seconde ververst**. De nauwkeurigheid is ±0,01A op stroom en ±1W op vermogen.

Deze data gaat via LoRa direct naar de omvormer (via de Smart Transmitter). Hierdoor weet de omvormer real-time of er sprake is van zonne-overschot, netverbruik of teruglevering. Dit is de basis voor **zero-export** (geen teruglevering aan het net) en slimme laadsturing.

De CT ondersteunt enkelfase (L1/N) en driefase (L1/L2/L3/N) installaties. Montage is non-invasief: klem-CT's rond de hoofdkabel, geen doorsnijding nodig. Als LoRa niet gewenst is, kan de CT ook bedraad via RS485 worden aangesloten.

`Specs: 1 Hz sampling (elke seconde) | ±0,01A nauwkeurigheid | LoRa + RS485 dual-mode | 1- en 3-fase | DIN-rail | 200m LoRa-bereik`

→ [Bekijk in de webshop](/products/deye-smart-wireless-ct-meter-lora)

<!-- /productkaart -->

---

### 3. Deye Smart Plug (SUN-SMART-PLUG01P1-F)

<!-- type: productkaart -->
<!-- afbeelding: 智能插座3.png -->

**Slimme stekkerschakelaar — maak elk apparaat slim**

De Smart Plug wordt in een standaard stopcontact gestoken en maakt elk aangesloten apparaat onderdeel van het energiesysteem. Denk aan een boiler, wasmachine, droger of airco.

Via de omvormer kun je logische regels instellen: schakel de Smart Plug pas in als er zonne-overschot is, als de batterij boven een bepaald SOC-niveau zit, of alleen binnen bepaalde tijdsloten. Dit alles wordt lokaal via LoRa aangestuurd — geen cloud, geen vertraging.

Je kunt meerdere Smart Plugs gebruiken en per plug verschillende prioriteiten instellen. Zo gaat overschot-stroom eerst naar de batterij, dan naar de boiler, dan naar de wasmachine.

`Specs: Plug-and-play | LoRa-communicatie | Logische sturing (tijd/SOC/overschot) | EU-stekker (Schuko)`

<!-- /productkaart -->

---

### 4. Deye Smart Switch (SUN-SMART-SWITCH01P3)

<!-- type: productkaart -->
<!-- afbeelding: 智能开关3.png -->

**Voor vaste aansluitingen en zwaardere belastingen**

De Smart Switch is het zwaardere broertje van de Smart Plug. Waar de Smart Plug bedoeld is voor apparaten op een stopcontact, is de Smart Switch bedoeld voor **vast aangesloten apparaten en hogere vermogens** — zoals een warmtepomp, boiler op vaste aansluiting of een airco-buitenunit.

De Smart Switch ondersteunt zowel enkelfase als driefase belastingen en wordt tussen de groep en het apparaat gemonteerd. De logische sturing is identiek aan de Smart Plug: tijd, SOC, overschot, of combinaties daarvan.

Op het apparaat zitten duidelijke "LOAD" en "GRID" aansluitingen en LED-indicatoren voor COM (communicatie), AC/M (modus) en SET (instellingen).

`Specs: Enkelfase + driefase | LoRa-communicatie | Hogere vermogens | Vast aangesloten (hardwired) | IP65 geschikt`

<!-- /productkaart -->

---

### 5. Deye Smart Wallbox (SUN-EVSE22K01-EU-AC)

<!-- type: productkaart -->
<!-- afbeelding: 充电枪.png -->
<!-- product-url: /products/deye-smart-wallbox-ac-charger-22-kw-slimme-ev-lader -->

**Slim EV-laden aangestuurd door je omvormer**

De Deye Smart Wallbox is een volwaardige 22 kW (driefase) of 7 kW (enkelfase) laadpaal die via LoRa wordt aangestuurd door de omvormer. In de **Solar Energy Only**-modus laadt de wallbox je auto alleen als er voldoende zonne-overschot is en de thuisbatterij boven een ingesteld niveau zit.

Daarnaast ondersteunt de wallbox Time-of-Charge (laden in de goedkoopste uren) en Plug & Play (direct laden op vol vermogen). De wallbox is IP66 waterdicht, CE-gecertificeerd en heeft 7-laags beveiliging inclusief DC 6mA aardlekdetectie.

**Over de Wallbox publiceren we binnenkort een uitgebreid vervolgartikel** met rekenvoorbeelden, installatie-instructies en ervaringen. → [Lees het Wallbox-artikel (binnenkort)](/blogs/kennis/deye-wallbox-slim-laden-zonne-energie)

`Specs: 22 kW driefase / 7 kW enkelfase | LoRa + WiFi + Bluetooth | Solar Energy Only modus | IP66 waterdicht | Type 2 connector | 7-laags beveiliging`

→ [Bekijk in de webshop](/products/deye-smart-wallbox-ac-charger-22-kw-slimme-ev-lader)

<!-- /productkaart -->

---

## Hoe werkt het als geheel? Een praktijkvoorbeeld {#werking}

Stel: het is een doordeweekse dag in april. De zon schijnt en je 12 zonnepanelen produceren volop stroom. Niemand is thuis. Dit is wat het Deye Smart Home systeem automatisch doet:

**09:00 — Zonne-opbrengst begint**
De Wireless CT in de meterkast meet dat er meer wordt opgewekt dan verbruikt. Deze data gaat via LoRa naar de Smart Transmitter, die het doorgeeft aan de omvormer.

**09:05 — Batterij laden**
De omvormer begint de thuisbatterij te laden. Prioriteit één: eigen opslag vullen.

**11:30 — Batterij op 85%, overschot groeit**
De batterij nadert het ingestelde SOC-niveau (bijv. 80%). De omvormer ziet via de CT dat er nog steeds flink overschot is. Automatisch schakelt hij de Smart Plug in waarop de boiler is aangesloten. De boiler verwarmt water met gratis zonnestroom.

**12:15 — Nog meer overschot**
De boiler is op temperatuur, de Smart Plug schakelt uit. Maar er is nog steeds overschot. De omvormer stuurt via LoRa een signaal naar de Smart Wallbox: begin met laden van de elektrische auto die op de oprit staat. De wallbox start op het beschikbare overschot-vermogen.

**14:00 — Bewolking trekt over**
De CT meet dat de opbrengst daalt. De omvormer reageert direct (binnen 50 ms): de wallbox gaat naar een lager vermogen, de boiler blijft uit. De batterij houdt zijn niveau vast. Het huishouden draait op zonnestroom + batterij, er wordt niets van het net getrokken.

**14:30 — Zon komt terug**
De CT meet weer overschot. De wallbox schakelt terug naar hoger vermogen.

**17:00 — Bewoners komen thuis**
Het verbruik stijgt. De omvormer ontlaadt de batterij om het huishouden te voeden. De wallbox wordt gepauzeerd. Alles gebeurt automatisch, lokaal, zonder dat iemand iets hoeft te doen.

<!-- type: keypoint -->
> **Het resultaat:** Op deze dag is de boiler verwarmd met gratis zonnestroom, de auto heeft 25 kWh geladen zonder een cent van het net, de batterij is gevuld voor de avond, en er is geen enkele kilowattuur teruggeleverd tegen een laag tarief. Het systeem heeft zichzelf volledig aangestuurd via LoRa — zonder internet, zonder cloud, zonder menselijke input.
<!-- /keypoint -->

---

## LoRa vs. WiFi: waarom maakt het uit? {#vergelijking}

Veel concurrerende systemen gebruiken WiFi of Bluetooth voor communicatie tussen energieapparaten. Dit werkt, maar heeft beperkingen die in de praktijk merkbaar zijn. Hier de technische vergelijking:

<!-- type: vergelijkingstabel -->

| Eigenschap | LoRa (Deye) | WiFi |
|---|---|---|
| **Latency (vertraging)** | ✅ ~50 ms | ❌ 500 ms – 3 sec (via cloud) |
| **Werkt zonder internet** | ✅ Volledig lokaal | ❌ Afhankelijk van router + cloud |
| **Bereik in gebouwen** | ✅ ~200 meter, door meerdere muren | 10-30 meter, signaalverlies bij muren |
| **Stroomverbruik** | ✅ Zeer laag (mW) | Hoger (continu verbonden) |
| **Wake-up tijd apparaat** | ✅ Milliseconden | Seconden (herverbinding) |
| **Beveiliging** | ✅ AES-128 encryptie | WPA2/WPA3 (router-afhankelijk) |
| **Frequentie** | 868 MHz (EU, vrij) | 2.4 / 5 GHz (gedeeld met andere apparaten) |

<!-- /vergelijkingstabel -->

De kern: WiFi is ontworpen om grote hoeveelheden data te versturen (video, webpagina's). LoRa is ontworpen om kleine hoeveelheden data héél betrouwbaar en snel te versturen over lange afstand. Voor energiesturing — waar het gaat om een paar bytes per seconde (vermogenswaarden, schakelopdrachten) — is LoRa veruit de betere keuze.

---

## Wat betekent dit voor installateurs? {#installateurs}

Het Deye Smart Home ecosysteem verandert wat je als installateur kunt aanbieden. In plaats van alleen een omvormer en batterij te plaatsen, installeer je een **compleet slim energiesysteem** dat het hele huishouden optimaliseert.

### Nieuwe verdienmodellen

Begin met een basisinstallatie (omvormer + batterij + Wireless CT) en bouw het systeem stap voor stap uit. Elke uitbreiding — Smart Plug, Smart Switch, Wallbox — is een extra product én een extra service-uur. Klanten die tevreden zijn met de basisinstallatie komen bij je terug voor uitbreidingen.

### Hogere klanttevredenheid

Een systeem dat écht slim werkt — dat de boiler automatisch verwarmt met gratis zonnestroom, de auto laadt als er overschot is, en 's avonds de batterij inzet — levert meetbaar meer besparing op dan een "dom" systeem met vaste tijden. Dat vertaalt zich in betere reviews, meer mond-tot-mondreclame en minder servicecalls.

### Eenvoudige installatie

Geen kabels trekken voor de CT-meting (LoRa is draadloos). De Smart Transmitter is plug-and-play op de omvormer. Smart Plugs steken je in het stopcontact. De complexiteit is minimaal vergeleken met bedrade alternatieven — en dat scheelt installatie-uren.

### Combineer met Deye Copilot

Het Smart Home systeem wordt nog krachtiger in combinatie met **Deye Copilot** — het AI-gestuurde energiemanagementsysteem dat automatisch laad- en ontlaadstrategieën optimaliseert op basis van dynamische stroomprijzen en weersvoorspellingen. Copilot is gratis te activeren op alle Deye hybride omvormers. → [Lees het Copilot-artikel (binnenkort)](/blogs/kennis/deye-copilot-ai-energiebeheer)

<!-- type: cta-blok -->
<!-- variant: donker -->

**Installateur? Word Deye-partner bij EcoHandel PRO**

Dealerprijzen op het complete Deye-assortiment, technische ondersteuning bij elke installatie en klantleads in jouw regio.

→ [Meld je aan als partner](/pages/installatie-partners)
→ [Bel 085-333 2453](tel:0853332453)

<!-- /cta-blok -->

---

## Beschikbaarheid en prijzen {#producten}

Alle componenten van het Deye Smart Home systeem zijn direct leverbaar bij EcoHandel. Hieronder een overzicht van de kernproducten:

| Product | Model | Prijs (excl. BTW) | Link |
|---|---|---|---|
| **Wireless CT + Smart Transmitter** (bundel) | SUN-SMART-CT01 + TX01 | €169,00 | [Bekijk →](/products/deye-smart-wireless-ct-meter-lora) |
| **Smart Wallbox 22 kW** | SUN-EVSE22K01-EU-AC | €549,00 | [Bekijk →](/products/deye-smart-wallbox-ac-charger-22-kw-slimme-ev-lader) |
| **Smart Plug** | SUN-SMART-PLUG01P1-F | Binnenkort beschikbaar | [Vraag aan →](/pages/contact) |
| **Smart Switch** | SUN-SMART-SWITCH01P3 | Binnenkort beschikbaar | [Vraag aan →](/pages/contact) |

**Compatibiliteit:** Het systeem werkt met alle Deye hybride omvormers — enkelfase (SG05LP1-serie), driefase LV (SG04LP3/SG05LP3-serie) en driefase HV (SG01HP3-serie). Bekijk het [complete omvormer-assortiment](/collections/omvormers).

**Installateurs:** Als [EcoHandel PRO partner](/pages/installatie-partners) profiteer je van dealerprijzen op alle bovenstaande producten plus technische ondersteuning bij configuratie.

---

## Veelgestelde vragen {#faq}

<!-- type: faq-accordion -->
<!-- Implementeer als inklapbare details/summary elementen -->

**Heb ik internet nodig voor het Deye Smart Home systeem?**
Nee. Alle communicatie tussen de omvormer, Wireless CT, Smart Plugs, Smart Switch en Wallbox verloopt via LoRa — volledig lokaal, zonder internet. Je hebt alleen internet nodig als je het systeem op afstand wilt monitoren via de Deye Cloud app, of als je Deye Copilot (AI-optimalisatie) wilt gebruiken.

**Werkt het systeem met mijn bestaande Deye omvormer?**
Ja. Het systeem is compatibel met alle Deye hybride omvormers die een Meter-poort hebben. Dit omvat de volledige SG05LP1-serie (enkelfase), SG04LP3/SG05LP3-serie (driefase LV 48V) en SG01HP3-serie (driefase HV). Je hoeft alleen een Smart Transmitter (TX01) aan te sluiten om het LoRa-netwerk te activeren.

**Wat is het bereik van de LoRa-verbinding?**
In vrij zicht tot 200 meter. In gebouwen penetreert het signaal moeiteloos door meerdere betonmuren. Gebruikers melden stabiele verbindingen door twee verdiepingen beton — ideaal voor Europese woningbouw waar de meterkast vaak in de kelder zit en de omvormer op zolder of in de garage.

**Kan ik het systeem stap voor stap uitbreiden?**
Absoluut, en dat is precies hoe het bedoeld is. Begin met de basis: omvormer + batterij + Wireless CT + Smart Transmitter. Voeg later Smart Plugs toe voor je boiler en wasmachine. En als je een elektrische auto krijgt, voeg je de Wallbox toe. Elk component integreert automatisch in het bestaande LoRa-netwerk.

**Wat is het verschil tussen de Smart Plug en de Smart Switch?**
De Smart Plug is bedoeld voor apparaten op een standaard stopcontact (boiler, wasmachine, droger). De Smart Switch is voor vast aangesloten apparaten met hogere vermogens (warmtepomp, airco-buitenunit, EV-lader op vaste aansluiting) en ondersteunt zowel enkelfase als driefase belastingen. De logische sturing (tijd, SOC, overschot) is bij beide identiek.

**Kan EcoHandel helpen bij de configuratie?**
Ja. Als officieel Deye servicepunt in Nederland bieden wij technische ondersteuning bij de installatie en configuratie van het Smart Home systeem. Dit kan remote (via telefoon/scherm delen) of op locatie. [Installateurs in ons partnernetwerk](/pages/installatie-partners) krijgen prioriteitsondersteuning.

<!-- /faq-accordion -->

---

<!-- type: cta-blok -->
<!-- variant: donker -->

**Het complete Deye Smart Home systeem bij EcoHandel**

Alle componenten op voorraad, technische ondersteuning en dealerprijzen voor installateurs.

→ [Bekijk Wireless CT + Smart TX](/products/deye-smart-wireless-ct-meter-lora)
→ [Bekijk Smart Wallbox](/products/deye-smart-wallbox-ac-charger-22-kw-slimme-ev-lader)

<!-- /cta-blok -->

---

<!-- SERIE-NAVIGATIE ONDERAAN -->
<!-- type: serie-nav -->

**Vervolg: meer over het Deye ecosysteem**

| Status | Titel | Beschrijving | Link |
|--------|-------|-------------|------|
| Volgende in de serie | Deye Smart Wallbox: Slim Laden op Zonne-energie | Alles over de 3 laadmodi, rekenvoorbeelden en installatie | /blogs/kennis/deye-wallbox-slim-laden-zonne-energie |
| Deel 3 in de serie | Deye Copilot: AI-gestuurd Energiebeheer | Hoe AI automatisch je batterij optimaliseert op dynamische stroomprijzen en weer | /blogs/kennis/deye-copilot-ai-energiebeheer |
| Assortiment | Alle Deye Accessoires | CT-meters, transmitters, kabels en meer — direct leverbaar | /collections/accessoires-toebehoren |

<!-- /serie-nav -->

---

> **Afbeeldingen voor dit artikel:**
> Upload naar Shopify Files en gebruik in de blogpost:
> 
> | Bestandsnaam in project | Gebruik als | Alt-tekst |
> |---|---|---|
> | 合集_2.png | Featured image + hero | Deye Smart Home ecosysteem: Smart TX, Smart EV Charger, Smart Plug, Wireless CT en Smart Switch |
> | 智能接收器2.png | Bij Smart Transmitter sectie | Deye Smart Transmitter TX01 voorkant met LoRa-antenne |
> | CT2.png | Bij Wireless CT sectie | Deye Wireless CT Meter voorkant met display en navigatieknoppen |
> | 智能插座3.png | Bij Smart Plug sectie | Deye Smart Plug voorkant met power-indicator LED |
> | 智能开关3.png | Bij Smart Switch sectie | Deye Smart Switch met LOAD en GRID aansluitingen |
> | 充电枪.png | Bij Wallbox sectie | Deye Smart Wallbox 22kW EV-lader met laadkabel |
