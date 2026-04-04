# Link Mapping Review Notes — twijfelgevallen en uitsluitingen

Deze file is **niet** voor directe AI-prijslijstbouw, maar voor controle en latere opschoning.

## Niet gebruiken in prijslijst
### Draft / unlisted / onveilig
- Deye Smart Wallbox AC Charger 11kW (`deye-smart-wallbox-ac-charger-11-kw-slimme-ev-lader-kopie`) → draft
- Deye SUN-25K-SG01HP3-EU → draft
- Deye RW-F10.2 LV → unlisted
- Deye RW-F16 16kW LV → unlisted
- Deye SUN-20K-SG01HP3-EU-AM2 (`deye-sun-20k-sg01hp3-eu-am2-20kw-drie-fase-hybride-hv-batterij-ondersteund`) → unlisted
- Deye SUN-20K-SG01HP3-EU-AM2 (`sun-15k-sg05lp3-eu`) → unlisted en duidelijk fout
- Deye SUN-50K-SG01HP3-EU-BM4 (`deye-sun-50k-sg01hp3-eu-bm4-50kw-drie-fase-hybride-hv-batterij-ondersteund`) → unlisted
- Deye SUN-50K-SG01HP3-EU-BM4 (`deye-sun-50k-sg01hp3-eu-bm4-50kw-drie-fase-hybride-hv-batterij-ondersteund-kopie`) → unlisted

## Live maar slug/titel mismatch
Voorzichtig mee omgaan; alleen gebruiken bij exacte modelmatch in de prijslijst.
- SUN-10K-SG01HP3-EU-AM2 → live slug bevat `12kw`
- SUN-6K-SG05LP3-EU → live slug lijkt uit oud/kopie-product te komen
- AI-W5.1-B 15.36 / 20.48 / 25.60 → live maar `-kopie` slugs met mismatch in kW-serie
- SE-F5Pro-C 5.12kWh → live maar draait op `...16kwh...kopie` slug
- SUN-80K-SG02HP3-EU-EM6 → live maar slug is erg vervuild

## Aanbeveling voor later
- Shopify handles opschonen voor deze producten
- Of redirects inrichten naar nette canonical handles
- Daarna AI mapping opnieuw genereren
