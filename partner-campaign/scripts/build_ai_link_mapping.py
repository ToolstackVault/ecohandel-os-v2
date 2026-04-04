#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

BASE_URL = 'https://www.ecohandel.nl'
OUT_MD = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign/AI_LINK_MAPPING.md')
OUT_JSON = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign/ai-link-mapping.json')

collections = [
    {'label': 'Thuisbatterijen', 'url': f'{BASE_URL}/collections/thuisbatterijen', 'use_for': 'algemene batterijlijn / fallback'},
    {'label': 'Omvormers', 'url': f'{BASE_URL}/collections/omvormers', 'use_for': 'algemene omvormerlijn / fallback'},
    {'label': 'Thuisbatterij + Omvormer Sets', 'url': f'{BASE_URL}/collections/thuisbatterij-omvormer-sets', 'use_for': 'complete set bundels'},
    {'label': 'Accessoires & toebehoren', 'url': f'{BASE_URL}/collections/accessoires-toebehoren', 'use_for': 'meters, controllers en onderdelen'},
]

products = [
    {'group': 'Deye sets', 'label': 'Deye 10kWh Thuisbatterij Set 1-fase LV', 'url': f'{BASE_URL}/products/deye-10kwh-thuisbatterij-set-1-fase-lv-ai-w5-1-b-sun-3-6k-smart-ct'},
    {'group': 'Deye sets', 'label': 'Deye 15kWh Thuisbatterij Set 3-fase HV 10kW', 'url': f'{BASE_URL}/products/deye-15kwh-thuisbatterij-set-3-fase-hv-deye-gb-l-pro-hv-deye-sun-10k-sg01hp3'},
    {'group': 'Deye sets', 'label': 'Deye 16kWh Thuisbatterij Set 1-fase met 6kW Hybride Omvormer', 'url': f'{BASE_URL}/products/deye-se-f16-c-16kwh-deye-sun-6k-sg05lp1-eu-1-fase-set'},
    {'group': 'Deye sets', 'label': 'Deye 32kWh Thuisbatterij Set 3-fase 10kW', 'url': f'{BASE_URL}/products/deye-32kwh-thuisbatterij-set-3-fase-10kw-2x-se-f16-c-sun-10k-sg05lp3-eu'},
    {'group': 'Deye batterijen', 'label': 'Deye 6.14kWh Low Voltage Thuisbatterij', 'url': f'{BASE_URL}/products/deye-6-14kwh-low-voltage-thuisbatterij'},
    {'group': 'Deye batterijen', 'label': 'Deye AI-W5.1-B LV 5.12 kW Batterijset', 'url': f'{BASE_URL}/products/deye-ai-w5-1-b-lv-5-12-kw-batterijset-met-controller-en-base'},
    {'group': 'Deye batterijen', 'label': 'Deye GB-L-Pro HV Batterijtoren', 'url': f'{BASE_URL}/products/deye-gb-l-pro-hv-batterijtoren-8-18-kwh-tot-24-54-kwh'},
    {'group': 'Deye batterijen', 'label': 'Deye SE-F16-C 16kWh Thuisbatterij', 'url': f'{BASE_URL}/products/deye-se-f16-c-16kwh-thuisbatterij-48v-lfp-modulair-systeem'},
    {'group': 'Deye omvormers', 'label': 'Deye SUN-3.6K-SG05LP1-EU', 'url': f'{BASE_URL}/products/sun-3-6k-sg05lp1-eu'},
    {'group': 'Deye omvormers', 'label': 'Deye SUN-5K-SG05LP1-EU', 'url': f'{BASE_URL}/products/sun-5k-sg05lp1-eu'},
    {'group': 'Deye omvormers', 'label': 'Deye SUN-6K-SG05LP1-EU', 'url': f'{BASE_URL}/products/sun-6k-sg05lp1-eu'},
    {'group': 'Deye omvormers', 'label': 'Deye SUN-8K-SG05LP1-EU', 'url': f'{BASE_URL}/products/sun-8k-sg05lp1-eu'},
    {'group': 'Deye omvormers', 'label': 'Deye SUN-10K-SG05LP3-EU', 'url': f'{BASE_URL}/products/sun-10k-sg05lp3-eu'},
    {'group': 'Deye omvormers', 'label': 'Deye SUN-12K-SG04LP3-EU', 'url': f'{BASE_URL}/products/sun-12k-sg04lp3-eu'},
    {'group': 'Deye omvormers', 'label': 'Deye SUN-12K-SG01HP3-EU-AM2', 'url': f'{BASE_URL}/products/deye-sun-12k-sg01hp3-eu-am2-12kw-driefasig-hybride-hv-batterij-ondersteund'},
    {'group': 'Deye omvormers', 'label': 'Deye SUN-15K-SG05LP3-EU', 'url': f'{BASE_URL}/products/deye-sun-15k-sg05lp3-eu-15kw-driefase-hybride-lv-48v'},
    {'group': 'Deye omvormers', 'label': 'Deye SUN-20K-SG01HP3-EU-AM2', 'url': f'{BASE_URL}/products/sun-20k-sg01hp3-eu-am2'},
    {'group': 'Deye omvormers', 'label': 'Deye SUN-30K-SG02HP3-EU-BM', 'url': f'{BASE_URL}/products/sun-30k-sg02hp3-eu-bm3'},
    {'group': 'Deye omvormers', 'label': 'Deye SUN-50K-SG01HP3-EU-BM4', 'url': f'{BASE_URL}/products/sun-50k-sg01hp3-eu-bm4'},
    {'group': 'Deye omvormers', 'label': 'Deye SUN-80K-SG02HP3-EU-EM6', 'url': f'{BASE_URL}/products/deye-sun-80k-hybride-omvormer-80kw-driefase-hv-batterijproducts-sun-80k-sg02hp3-eu-em6'},
    {'group': 'Accessoires', 'label': 'Deye Wireless CT Meter + Smart Transmitter', 'url': f'{BASE_URL}/products/deye-smart-wireless-ct-meter-lora'},
    {'group': 'Accessoires', 'label': 'Deye Smart Wallbox AC Charger 22kW', 'url': f'{BASE_URL}/products/deye-smart-wallbox-ac-charger-22-kw-slimme-ev-lader'},
]

notes = [
    'Gebruik bij prijslijst altijd exact deze URLs of de collectie-fallbacks hieronder.',
    'Als een specifiek product niet in de lijst staat, link dan eerst naar de meest relevante collectie in plaats van een gok-product.',
    'Voor complete residentiële oplossingen heeft de sets-collectie voorrang boven losse producten.',
    'Voor omvormers zonder exact model in de prijslijst: gebruik /collections/omvormers als fallback.',
    'Voor batterijen zonder exact model in de prijslijst: gebruik /collections/thuisbatterijen als fallback.',
]

md = ['# AI Link Mapping — EcoHandel Partner Prijslijst', '', 'Gebruik dit bestand als bron voor de HTML prijslijst of andere AI-output.', '', '## Belangrijke regels']
for n in notes:
    md.append(f'- {n}')
md.extend(['', '## Collectie-fallbacks'])
for c in collections:
    md.append(f"- **{c['label']}** → {c['url']}  ")
    md.append(f"  Gebruik voor: {c['use_for']}")
md.extend(['', '## Productlinks'])
current_group = None
for p in products:
    if p['group'] != current_group:
        current_group = p['group']
        md.extend(['', f'### {current_group}'])
    md.append(f"- {p['label']} → {p['url']}")

OUT_MD.write_text('\n'.join(md) + '\n')
OUT_JSON.write_text(json.dumps({'base_url': BASE_URL, 'notes': notes, 'collections': collections, 'products': products}, indent=2, ensure_ascii=False) + '\n')
print(f'Wrote {OUT_MD}')
print(f'Wrote {OUT_JSON}')

if __name__ == '__main__':
    pass
