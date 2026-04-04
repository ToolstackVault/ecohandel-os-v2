# EcoHandel.nl Underwater Theme Redesign — STATUS

## 📋 Project Overview
**Doel:** EcoHandel.nl onderwater theme (ocean/sea aesthetic voor Deye batterijen) Shopify theme doorvoeren.
**Status:** 🔄 In progress
**Preview:** https://n6f6ja-qr.myshopify.com?preview_theme_id=195485237589
**Live Theme ID:** 195485237589
**Theme Editor:** https://n6f6ja-qr.myshopify.com/admin/themes/195485237589/editor

---

## ✅ Completed

### Setup & Assets
- [x] Hero image (Deye HeroBanner) gecomprimeerd naar 262KB
- [x] Hero image geüpload naar VPS: `https://toolstackvault.com/underwater-hero.jpg`
- [x] `image-banner.liquid` aangepast voor externe URL support (`| slice: 0, 4 == 'http'` check)
- [x] VPS als image host (CDN propagatie Shopify faalde)

### CSS (underwater-theme.css)
- [x] 924 regels, full design system
- [x] CSS custom properties (--uw-navy, --uw-cyan, --uw-orange, etc.)
- [x] Wave SVG dividers
- [x] Card styling (.uw-card, .uw-card-product)
- [x] Trust bar styling (.uw-trust-bar)
- [x] Announcement bar styling (.uw-announcement-bar)
- [x] Footer styling (.uw-footer)
- [x] Button styling (.uw-btn-primary, .uw-btn-secondary)
- [x] B2B section styling
- [x] Contact form tekstkleur fix (dark bg)
- [x] Multi-row/advies section (scheme-2 ice) styling

### Sections
- [x] Trust bar: `uw-trust-bar` class toegevoegd, navy background met !important
- [x] Announcement bar: `uw-announcement-bar` class toegevoegd, navy bg, witte tekst
- [x] Footer: `uw-footer` class toegevoegd, Deye badge + dark navy
- [x] Contact form: description/heading wit, submit button oranje CTA
- [x] Multi-row: headings navy, captions cyan, body tekst navy-tinted
- [x] Collection-list: scheme-4 → scheme-2 (ice) gefixt

---

## 🔲 Remaining Tasks

- [ ] **Header fix** — Terugzetten naar werkende versie + PRO button (prompt: `underwater/prompts/fix-header-simpel.md`)
- [ ] **Clean base redesign** — Live theme dupliceren + nieuwe elementen overbrengen (prompt: `underwater/prompts/prompt-schone-basis-redesign.md`)
- [ ] **Hero banner** — check of image-banner.liquid nu goed werkt met externe URL
- [ ] **Collection cards** — underwater CSS classes toepassen
- [ ] **B2B section** — wave SVG divider toevoegen
- [ ] **Homepage grid** — check of artikelen goed staan na redesign
- [ ] **Product cards** — specifieke underwater styling
- [ ] **Theme push** — let op: er waren Liquid syntax errors bij laatste push
  - Fout: `image-banner.liquid` regel 95: `Expected end_of_string but found pipe`
  - Oplossing: `| slice: 0, 4` syntax fixen voor Shopify Liquid

---

## 🗂️ Key Files

### Local Theme Files (op Mac)
```
/tmp/ecohandel-onderwater/
├── assets/
│   └── underwater-theme.css       # Hoofd CSS (924 regels)
├── sections/
│   ├── image-banner.liquid        # Hero banner (aangepast voor externe URL)
│   ├── trust-bar.liquid           # ✅ underwater class toegevoegd
│   ├── announcement-bar.liquid    # ✅ underwater class toegevoegd
│   ├── footer.liquid              # ✅ underwater class toegevoegd
│   ├── contact-form.liquid        # ✅ tekstkleuren gefixt
│   └── multirow.liquid            # ✅ styling aangepast
├── layout/
│   └── theme.liquid
├── config/
│   └── settings_data.json
└── snippets/
    └── (diverse snippets)
```

### Shopify Theme Editor
- URL: https://n6f6ja-qr.myshopify.com/admin/themes/195485237589/editor
- Theme ID: 195485237589

### VPS Image Hosting
- Hero image: `https://toolstackvault.com/underwater-hero.jpg`
- Locatie VPS: `/var/www/html/toolstackvault.com/underwater-hero.jpg`

---

## 🤝 Partner Campaign System

- **Project root:** `ecohandel/partner-campaign/`
- **Architectuur:** `ecohandel/partner-campaign/SYSTEM_ARCHITECTURE.md`
- **Database schema:** `ecohandel/partner-campaign/DATA_MODEL.sql`
- **Brevo webhook spec:** `ecohandel/partner-campaign/BREVO_WEBHOOK_SPEC.md`
- **Prijslijst linking spec:** `ecohandel/partner-campaign/PRICELIST_LINKING_SPEC.md`
- **Daily ops:** `ecohandel/partner-campaign/DAILY_OPERATIONS.md`
- **Database:** `ecohandel/partner-campaign/data/partner_campaign.db`
- **Lead import:** bestaande `ecohandel/lead-generation/leads/LEADS.csv` ingeladen
- **Doel:** autonoom partner-outreach systeem via Brevo + lokale event intelligence + dagelijkse hot prospect handoff
- **Nog nodig van Milan:** Brevo EcoHandel config, verified sender, webhook details, HTML prijslijst

## 📝 Content System (Kennisblog)

- **Source of truth playbook:** `ecohandel/content-system/kennisblog/PUBLISH_PLAYBOOK.md`
- **Template:** `ecohandel/content-system/kennisblog/TEMPLATE.html`
- **Publisher:** `ecohandel/content-system/kennisblog/publish_article.py`
- **Econtrol Room wrapper:** `ecohandel/econtrol-room/scripts/publish_ecohandel.py`
- **Procesconfig:** `ecohandel/econtrol-room/sources/publish-system.json`
- **Regel:** nooit direct in live theme werken; altijd underwater/test/preview eerst, dan review door Milan, daarna pas live.

## 🔧 ACP Sessions (voor Discord thread)

| Session | Doel | Status |
|---------|------|--------|
| `f4a29269-1dba-4de3-9b05-c813f9f9fad2` | Oude ACP | Loopt |
| `f9717399-7242-4063-bd30-a7041ef86df0` | Footer/B2B/Collection | Loopt |

---

## 🚨 Bekende Problemen

1. **Liquid syntax error in image-banner.liquid (regel 95)**
   - Fout: `| slice: 0, 4 == 'http'` werkt niet in Shopify Liquid
   - Fix nodig: alternatieve string comparison methode

2. **Shopify CDN/asset hosting werkt niet** 
   - Oplossing: altijd VPS gebruiken voor custom images

3. **Telegram → Discord thread spawn werkt niet**
   - Spawns moeten vanaf Discord zelf worden geïnitieerd
   - Of via Telegram zonder thread=true

---

## 📌 Hoe verder te gaan (Discord Thread)

1. **Check of hero banner werkt** — open preview en bekijk homepage
2. **Fix Liquid syntax error** — image-banner.liquid regel 95
3. **Push remaining sections** — collection cards, B2B section
4. **Test alles** — frontend check na elke push
5. **Live zetten** — als alles goed is, theme activeren

---

## 🔗 Handige Links

- **Preview:** https://n6f6ja-qr.myshopify.com?preview_theme_id=195485237589
- **Theme Editor:** https://n6f6ja-qr.myshopify.com/admin/themes/195485237589/editor
- **Shopify Admin:** https://n6f6ja-qr.myshopify.com/admin
- **Jean Clawd Telegram:** Deze conversatie
- **Discord Thread:** https://discord.com/channels/1477613670996639845/1484678406246502511
