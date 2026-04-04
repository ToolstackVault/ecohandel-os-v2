# Deye Copilot: AI-gestuurd Energiebeheer voor je Thuisbatterij

> **Shopify Blog Instellingen:**
> - Blog: `kennis`
> - URL handle: `deye-copilot-ai-energiebeheer`
> - SEO Title: `Deye Copilot: AI Energiebeheer voor je Thuisbatterij | EcoHandel`
> - SEO Description: `Deye Copilot is het AI-gestuurde energiemanagementsysteem dat je batterij automatisch optimaliseert op basis van stroomprijzen en weer. Gratis te activeren. Uitleg, instellen en resultaten.`
> - Tags: `deye, copilot, ai, energiebeheer, dynamisch tarief, thuisbatterij, tibber, frank energie`
> - Featured image: gebruik een screenshot van de Deye Cloud app met Copilot-dashboard, of het Deye-logo op donkere achtergrond
> - Author: EcoHandel

---

<!-- type: serie-nav -->

| Status | Titel | Beschrijving | Link |
|--------|-------|-------------|------|
| Deel 1 | Deye Smart Home & LoRa | Alle componenten en hoe ze samenwerken | /blogs/kennis/deye-smart-home-lora-systeem |
| Deel 2 | Deye Wallbox: Slim Laden | Laad je EV gratis met zonne-energie | /blogs/kennis/deye-wallbox-slim-laden-zonne-energie |
| **Actief — Je leest dit nu** | Deye Copilot: AI Energiebeheer | Automatische optimalisatie met AI | — |

<!-- /serie-nav -->

---

De meeste thuisbatterij-eigenaars in Nederland stellen hun omvormer in op vaste tijden. Laden van 01:00 tot 05:00, ontladen van 17:00 tot 21:00. Het werkt, maar het is niet slim. Energieprijzen veranderen elk uur. Morgen schijnt de zon misschien de hele dag — of juist niet. Je verbruikspatroon op dinsdag is anders dan op zaterdag.

Wat als je systeem dit allemaal zelf kon uitzoeken? Elke 15 minuten een nieuw plan maken, gebaseerd op real-time stroomprijzen, weersvoorspellingen en jouw verbruikshistorie? Dat is precies wat **Deye Copilot** doet — en het is gratis.

---

## Inhoudsopgave

1. [Wat is Deye Copilot?](#wat)
2. [Hoe werkt de AI?](#ai)
3. [Wat levert het op?](#resultaten)
4. [Copilot instellen — stap voor stap](#instellen)
5. [Copilot + het Deye Smart Home systeem](#smarthome)
6. [Compatibiliteit en vereisten](#compatibiliteit)
7. [Veelgestelde vragen](#faq)

---

## Wat is Deye Copilot? {#wat}

Deye Copilot is een **AI-gestuurd Energy Management System (EMS)** dat draait op het Deye Cloud platform. Het is geen apart apparaat — het is software die je activeert op je bestaande Deye hybride omvormer via de Deye Cloud app. Geen extra hardware, geen extra kosten.

Na activering neemt Copilot de aansturing van je batterij over. In plaats van vaste laad- en ontlaadtijden kijkt Copilot naar drie databronnen:

- **Dynamische stroomprijzen** — de uurprijzen van je energieleverancier (Tibber, Frank Energie, ANWB Energie, of handmatig ingestelde tarieven)
- **Weersvoorspellingen** — hoeveel zonne-opbrengst er morgen en overmorgen wordt verwacht
- **Jouw verbruikspatroon** — hoe je huishouden energie gebruikt op verschillende dagen en tijdstippen

Op basis van deze drie bronnen maakt Copilot continu een optimaal laad- en ontlaadplan. Het doel is simpel: **laad de batterij als stroom goedkoop is, ontlaad als stroom duur is, en gebruik zoveel mogelijk je eigen zonnestroom.**

<!-- type: keypoint -->
> **Gratis en zonder extra hardware.** Deye Copilot is beschikbaar voor alle Deye hybride omvormers met batterij. Activering is gratis via de Deye Cloud app. Er is geen extra apparaat, dongle of abonnement nodig. Je hebt alleen een werkende internetverbinding nodig (de omvormer moet online zijn via WiFi of LAN).
<!-- /keypoint -->

---

## Hoe werkt de AI? {#ai}

"AI" is een groot woord dat vaak wordt misbruikt. Bij Deye Copilot gaat het om concreet, meetbaar gedrag. Dit is wat het systeem doet:

### Prijsanalyse: 24-48 uur vooruit kijken

Copilot haalt de dynamische energieprijzen op voor de komende 24 tot 48 uur. Voor Nederlandse gebruikers werkt dit met Tibber (via API-token), Frank Energie en andere aanbieders van dynamische contracten. Het systeem weet elk uur wat stroom kost.

Op basis hiervan plant Copilot automatisch:
- **Laden in de goedkoopste uren** — vaak 's nachts of in de vroege middag
- **Ontladen in de duurste uren** — vaak tussen 17:00 en 21:00
- **Terugleveren aan het net** als de terugleverprijzen hoog genoeg zijn om winst te maken

### Weersvoorspelling: morgen zonnig of bewolkt?

Copilot combineert de prijsdata met weersvoorspellingen. Dit is cruciaal:

- **Morgen zonnig?** → Copilot laadt de batterij vannacht NIET vol van het net. Morgen doen de panelen het werk gratis. De goedkope nachtelijke stroom wordt bewaard voor dagen zonder zon.
- **Morgen bewolkt?** → Copilot laadt de batterij wél vol in de goedkoopste nachtelijke uren, zodat je morgen niet hoeft te kopen tegen piektarief.

Zonder deze weerscomponent laadt een "dom" systeem elke nacht op daltarief, ook als morgen de zon alles levert. Dat is weggegooid geld.

### Verbruikspatroon: het systeem leert jou kennen

Na activering begint Copilot je verbruikspatroon te leren:
- **Na 2-3 weken:** het kent je dagritme — wanneer je veel verbruikt, wanneer weinig
- **Na 2-3 maanden:** het kent je seizoenspatronen — zomer vs. winter, doordeweeks vs. weekend
- **Doorlopend:** het past zich aan bij veranderingen — thuiswerken, nieuwe apparaten, vakantie

Elke 15 minuten maakt Copilot een nieuw optimalisatieplan en stuurt dit naar je omvormer. De omvormer past zijn laad- en ontlaadstrategie automatisch aan. Jij hoeft niets te doen.

---

## Wat levert het op? {#resultaten}

De besparingen hangen af van je systeemgrootte, je verbruik en de volatiliteit van de stroomprijzen. Maar de richting is duidelijk:

### Rekenvoorbeeld

**Systeem:** Deye hybride omvormer + 10 kWh batterij + zonnepanelen + dynamisch contract

**Zonder Copilot (vaste tijden):**
- Laden 01:00-05:00 (gemiddeld €0,10/kWh)
- Ontladen 17:00-21:00 (gemiddeld €0,30/kWh)
- Spread: €0,20/kWh × 10 kWh × 300 cycli/jaar = **~€600/jaar besparing**

**Met Copilot (AI-optimalisatie):**
- Laden op de allergoedkoopste uren (soms negatieve prijzen = je krijgt geld TOE)
- Ontladen op pieken (soms €0,50+/kWh)
- Slimmer omgaan met zonne-opbrengst (niet laden als morgen de zon schijnt)
- Gemiddelde spread stijgt naar €0,28/kWh
- 10 kWh × €0,28 × 300 cycli = **~€840/jaar besparing**

**Extra besparing door Copilot: ~€240/jaar** — oftewel 40% meer dan zonder.

En dit is een conservatief voorbeeld. Op dagen met grote prijsschommelingen (die in Nederland steeds vaker voorkomen) kan Copilot significant meer besparen. Sommige gebruikers in België en Australië melden besparingen van meer dan 50% extra ten opzichte van vaste schema's.

<!-- type: keypoint -->
> **De kern:** Copilot vervangt het gokwerk. In plaats van zelf in te schatten wanneer stroom goedkoop is en of morgen de zon schijnt, laat je de AI dit doen. 24/7, 365 dagen per jaar, met meer data dan jij ooit kunt verwerken.
<!-- /keypoint -->

---

## Copilot instellen — stap voor stap {#instellen}

De activering duurt 10 minuten. Hier is het volledige proces:

### Stap 1: Open de Deye Cloud app
Log in op de Deye Cloud app (iOS of Android) en ga naar de installatie (plant) waarop je Copilot wilt activeren.

### Stap 2: Vraag Copilot aan
Tik op het menu (rechtsboven, drie puntjes) en selecteer **"Apply for Deye Copilot"**. Vul de gevraagde gegevens in: installatiegegevens, batterijcapaciteit en regio.

### Stap 3: Stel je tariefstructuur in
Na het indienen kun je direct je tariefplan configureren. Twee opties:

- **Dynamisch tarief (aanbevolen):** Koppel je Tibber-account door je API-token in te voeren. Copilot haalt automatisch de uurprijzen op. Voor Frank Energie en andere aanbieders: stel het tarieftype in en Copilot gebruikt de ENTSO-E day-ahead prijzen.
- **Vast tarief:** Voer handmatig je dal- en piektijden en -prijzen in. Copilot optimaliseert dan binnen die structuur.

### Stap 4: Wacht op goedkeuring
Deye reviewt je aanvraag. Dit duurt 1-2 werkdagen. Na goedkeuring ontvang je een bericht in het "Message Center" van de app.

### Stap 5: Copilot is actief
Na goedkeuring activeert Copilot automatisch. Je ziet op het dashboard de dynamische prijzen, de weersvoorspelling en het geplande laad/ontlaadschema voor de komende uren. Copilot stuurt de omvormer nu zelf aan — je vaste tijdschema wordt overgenomen door het AI-schema.

### Stap 6: Monitor en optimaliseer
In de app kun je navigeren tussen "Live", "Dag", "Maand" en "Jaar" om te zien wat Copilot oplevert. Je ziet:
- Productiestroom (zonnepanelen)
- Batterijcurve (laden/ontladen)
- Netverbruik en -teruglevering
- Kostenbesparingen

**Hulp nodig bij het instellen?** EcoHandel helpt installateurs en klanten bij de configuratie van Copilot. Neem [contact](/pages/contact) op of bel 085-333 2453.

---

## Copilot + het Deye Smart Home systeem {#smarthome}

Copilot wordt nóg krachtiger in combinatie met het [Deye Smart Home systeem](/blogs/kennis/deye-smart-home-lora-systeem). Samen vormen ze een volledig autonoom energiesysteem:

**Copilot** stuurt de omvormer en batterij aan op basis van prijzen, weer en verbruik.

**De omvormer** stuurt via LoRa de rest van het huishouden aan:
- [Smart Plugs](/blogs/kennis/deye-smart-home-lora-systeem#componenten) schakelen de boiler en wasmachine op overschotmomenten
- De [Smart Wallbox](/blogs/kennis/deye-wallbox-slim-laden-zonne-energie) laadt je auto als er gratis zonnestroom is
- De [Wireless CT](/products/deye-smart-wireless-ct-meter-lora) meet real-time het totale verbruik

**Het resultaat:** een woning die zichzelf aanstuurt.
- Laadt de batterij als stroom goedkoop is
- Verwarmt de boiler als er zonne-overschot is
- Laadt de auto met gratis zonnestroom
- Ontlaadt de batterij op piektarief
- Levert terug aan het net als de prijs hoog genoeg is
- Dit alles zonder dat jij iets hoeft te doen

Deye noemt dit hun "Every Watt Counts" filosofie. En het is nu beschikbaar — alle componenten zijn leverbaar bij EcoHandel.

---

## Compatibiliteit en vereisten {#compatibiliteit}

### Wat heb je nodig?

- **Deye hybride omvormer** — elke serie (enkelfase SG05LP1, driefase LV SG04LP3/SG05LP3, driefase HV SG01HP3)
- **Batterij** — aangesloten op de omvormer (Deye, Pylontech, Dyness of ander compatibel merk)
- **Internetverbinding** — de omvormer moet online zijn via WiFi of LAN (Copilot draait in de cloud)
- **Deye Cloud account** — gratis aan te maken
- **Dynamisch energiecontract** — aanbevolen maar niet verplicht. Werkt ook met vaste tarieven.

### Compatibele energieleveranciers (Nederland)

Copilot werkt het beste met dynamische contracten. In Nederland zijn de belangrijkste:
- **Tibber** — directe API-koppeling via token
- **Frank Energie** — via ENTSO-E day-ahead prijzen
- **ANWB Energie (dynamisch)** — via ENTSO-E day-ahead prijzen
- **Zonneplan** — via ENTSO-E day-ahead prijzen
- **EasyEnergy** — via ENTSO-E day-ahead prijzen

Bij een vast contract kun je handmatig je dal/piek-tijden invoeren. Copilot optimaliseert dan binnen die structuur, maar de besparingen zijn kleiner dan met een dynamisch contract.

### Wat kost het?
Niets. Copilot is gratis. Geen abonnement, geen licentiekosten, geen extra hardware.

---

## Veelgestelde vragen {#faq}

<!-- type: faq-accordion -->

**Is Deye Copilot echt gratis?**
Ja. Er zijn geen kosten verbonden aan Copilot — geen abonnement, geen licentie, geen extra hardware. De enige vereiste is een Deye hybride omvormer met batterij en een werkende internetverbinding.

**Heb ik een dynamisch energiecontract nodig?**
Niet verplicht, maar sterk aanbevolen. Met een dynamisch contract (Tibber, Frank Energie, etc.) kan Copilot inspelen op uurlijkse prijsschommelingen — dat levert de grootste besparingen op. Met een vast contract optimaliseert Copilot op je dal/piek-tijden, maar de besparingen zijn beperkter.

**Werkt Copilot met batterijen van andere merken dan Deye?**
Ja. Copilot communiceert met de omvormer, niet direct met de batterij. Elke batterij die compatibel is met je Deye hybride omvormer werkt met Copilot — inclusief Pylontech, Dyness en andere merken.

**Kan ik Copilot uitschakelen en teruggaan naar handmatige instellingen?**
Ja. Je kunt in de Deye Cloud app op elk moment schakelen tussen Copilot-modus en handmatige tijdsinstellingen. Er zit geen lock-in.

**Hoe lang duurt het voordat Copilot optimaal werkt?**
Copilot begint direct met optimaliseren op basis van prijzen en weer. Het verbruikspatroon leert het systeem geleidelijk: na 2-3 weken kent het je dagritme, na 2-3 maanden je seizoenspatronen. De besparingen groeien mee naarmate Copilot meer data heeft.

**Heeft Copilot internet nodig om te werken?**
Ja. Copilot draait in de cloud en heeft een werkende internetverbinding nodig om prijsdata en weersvoorspellingen op te halen. Als je internet tijdelijk uitvalt, valt de omvormer terug op het laatst bekende schema. Het LoRa Smart Home systeem (Smart Plugs, Wallbox, CT) werkt wel lokaal zonder internet.

**Kan EcoHandel helpen bij het instellen van Copilot?**
Ja. Als officieel Deye servicepunt helpen wij bij de activering en configuratie van Copilot, inclusief het koppelen van je dynamische tarief (Tibber-token etc.). Neem [contact](/pages/contact) op of bel 085-333 2453.

<!-- /faq-accordion -->

---

<!-- type: cta-blok -->
<!-- variant: donker -->

**Begin met AI-gestuurd energiebeheer**

Deye Copilot is gratis te activeren op elke Deye hybride omvormer met batterij. Combineer met het Smart Home systeem voor een volledig autonome woning.

→ [Bekijk Deye hybride omvormers](/collections/omvormers)
→ [Bekijk het Smart Home systeem](/blogs/kennis/deye-smart-home-lora-systeem)
→ [Word installatiepartner](/pages/installatie-partners)

<!-- /cta-blok -->

---

<!-- type: serie-nav -->

**De complete serie: Deye Smart Energy Ecosysteem**

| Status | Titel | Beschrijving | Link |
|--------|-------|-------------|------|
| Deel 1 | Deye Smart Home & LoRa | Het complete draadloze ecosysteem | /blogs/kennis/deye-smart-home-lora-systeem |
| Deel 2 | Deye Smart Wallbox: Slim Laden | Laad je EV op zonne-energie | /blogs/kennis/deye-wallbox-slim-laden-zonne-energie |
| Hub | Alle Deye producten bij EcoHandel | Omvormers, batterijen, accessoires | /pages/deye |

<!-- /serie-nav -->
