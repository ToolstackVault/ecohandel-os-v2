# EcoHandel B2B Lead Generation — Research Skills

## Beschikbare Tools

### 1. Multi Search Engine (17 engines, geen API key nodig)
**Skill:** `/Users/ecohandel.nl/.openclaw/workspace/skills/multi-search-engine/SKILL.md`

**Gebruik voor leads:**
- Elke search engine heeft eigen index = andere resultaten
- Parallel zoeken = sneller meer leads
- Geen rate limit als je verschillende engines gebruikt

**Snelste aanpak:**
```python
# Gebruik web_fetch met direct URL:
web_fetch("https://www.google.com/search?q=zonnepaneel+installateur+thuisbatterij+Nederland")
web_fetch("https://duckduckgo.com/html/?q=zonnepaneel+installateur+thuisbatterij+Nederland")
web_fetch("https://bing.com/search?q=zonnepaneel+installateur+thuisbatterij+Nederland")
```

**Sitelinks voorbeelden:**
- `site:linkedin.com "zonnepaneel" "installateur" "Nederland"`
- `site:ondernemerscheck.nl zonne-energie installateur`
- `site:bedrijven.nl zonnepanelen`

---

### 2. Deye Price Guard Scrapers (al werkend!)
**Skill:** `/Users/ecohandel.nl/.openclaw/workspace/skills/deye-price-guard/`

**nkono, Sunnergie, EtronixCenter = Deye dealers**
- Deze bedrijven verkopen Deye aan installateurs
- Installateurs die daar kopen =潜在 Deye klanten = WARMSTE LEADS
- Script: `scrape_competitors.py` (lokaal, met cloudscraper voor NKON)

**Werkwijze:**
1. Haal alle product-URLs van nkon.nl/sunnergie.nl/etronixcenter.com
2. Bedrijven die Deye kopen = doelgroep
3. Check of bedrijven KvK geregistreerd zijn → contactgegevens

---

### 3. Brave Search (rate limited)
Ingebouwde tool, 66 requests/2000 quota per dag. Gebruik als aanvulling.

---

## Focus voor EcoHandel Leads

### Prioriteit 1: Deye-ecosysteem
- NKON.nl klanten (die kopen al Deye)
- Sunnergie.nl klanten
- EtronixCenter.nl klanten
- Officiële Deye servicepunten NL (zijn er 2, EcoHandel is 1)

### Prioriteit 2: Batterij-specialisten
- Bedrijven die thuisbatterijen installeren
- Lead aggregator platforms (Trustoo, Thuisbatterij.nl)
- Reviews en testimonials scrapen → bedrijfsnamen

### Prioriteit 3: Zonnepaneel markt
- Holland Solar leden
- KvK zonne-energie installateurs
- Google Maps bedrijven

---

## Scripts

### scrape_competitors.py (bestaand)
- Locatie: `/Users/ecohandel.nl/.openclaw/workspace/skills/deye-price-guard/scripts/scrape_competitors.py`
- Doel: Deye prijzen scrapen van NKON, Sunnergie, EtronixCenter
- Bruikbaar voor: names大城市 van Deye-kopende bedrijven

### scrape_round2.py
- Uitbreiding op scrape_competitors

---

## TODO
- [ ] Multi-search engine parallel zoekopdrachten opzetten
- [ ] NKON/Sunnergie scrape uitbreiden voor lead info
- [ ] KvK-lookup integreren voor contactgegevens
- [ ] Lead scoring systeem bouwen
