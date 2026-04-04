# EcoHandel Kennisblog Publishing Playbook

## Doel
Van aangeleverde markdown (`.md`) een premium EcoHandel kennisartikel maken met vaste styling, structured data voor Google, interne linking en een veilige preview-flow.

**Golden Standard:** `ecohandel/content-system/kennisblog/GOLDEN_STANDARD_TEMPLATE.html`
Gebruik dit bestand als referentie voor styling, structuur en opmaak. Elk nieuw artikel moet dezelfde kwaliteit hebben.

---

## Harde regels

### Content
- **Nooit streepjes in tekst.** Geen em-dashes, en-dashes of losse hyphens als leesteken. Gebruik punten, komma's of herformuleer.
- **Geen emoji's in artikeltekst.** Niet in headings, niet in lopende tekst, niet in CTA's.
- **Geen dubbele H1.** Body bevat geen `<h1>`. Shopify/theme toont de titel automatisch.
- **Interne links EcoHandel-only.** Geen cross-links naar ToolStackVault of andere sites.
- **Blog handle is `kennis`**, niet `kennisbank`. Alle interne links naar `/blogs/kennis/...`
- **Nooit `SolarMan` of `solarman app` als tag of marketingterm gebruiken.** Voor EcoHandel sturen we op Deye Cloud als voorkeursapp.
- **Toegestane auteurs:** alleen `Milan`, `Tom` of `Jean`.

### Publicatie
- **Nooit in een live theme werken.** Altijd eerst test/preview.
- **Huidig test-thema:** alleen het actuele door Milan aangewezen testthema gebruiken.
- **Blog ID:** `126678466901` (Kennis)
- **Preview URL patroon:** `https://n6f6ja-qr.myshopify.com/blogs/kennis/{handle}?preview_theme_id={theme_id}`
- Publiceren pas na expliciete goedkeuring van Milan.
- **Kritieke les:** als een kennisartikel een cover nodig heeft, zet die als **echte featured image op het Shopify artikelobject zelf**. Niet vertrouwen op theme-only fallback-logica. Dat is te fragiel omdat homepage, blogkaarten en artikeltemplate niet altijd via exact dezelfde renderlaag lopen.
- **Cover-kwaliteit:** cover moet visueel schoon zijn zonder zwarte randen of canvas-balken. Zo nodig eerst croppen/opschonen vóór upload.
- **Beeldkeuze-regel:** cover moet logisch passen bij het artikel. Artikel 8 bewees dat een beeld heel goed op het onderwerp moet lijken, bijvoorbeeld echt Deye-omvormer / Deye-batterij-achtig. Artikel 9 bewees dat een mooi gekozen ecosysteembeeld ook werkt als het inhoudelijk strak aansluit op warmtepomp + EV + thuisbatterij.
- **Extra beeldles:** lege of te minimalistische productshots zijn zwakker dan een vollere, premium compositie. Als een cover te leeg oogt, kies liever een rijker Deye-ecosysteembeeld in de stijl van artikel 8.

---

## Bronbestanden

| Bestand | Pad |
|---------|-----|
| Golden Standard Template | `ecohandel/content-system/kennisblog/GOLDEN_STANDARD_TEMPLATE.html` |
| Publisher script | `ecohandel/content-system/kennisblog/publish_article.py` |
| Workflow koppeling | `ecohandel/econtrol-room/scripts/publish_ecohandel.py` |
| Proces config | `ecohandel/econtrol-room/sources/publish-system.json` |
| Blog artikelen map | `~/Documents/EcoHandel.nl/BLOGS/` |

---

## Artikel HTML Structuur (verplicht)

Elk artikel bestaat uit deze onderdelen, in deze volgorde:

### 1. JSON-LD Structured Data (voor Google)

Drie schema blokken, elk in een eigen `<script type="application/ld+json">`:

**a) Article Schema**
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Artikeltitel",
  "description": "SEO description uit markdown header",
  "author": { "@type": "Organization", "name": "EcoHandel", "url": "https://www.ecohandel.nl" },
  "publisher": { "@type": "Organization", "name": "EcoHandel", "url": "https://www.ecohandel.nl" },
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD",
  "mainEntityOfPage": { "@type": "WebPage", "@id": "https://www.ecohandel.nl/blogs/kennis/{handle}" },
  "keywords": ["keyword1", "keyword2"]
}
```

**b) BreadcrumbList Schema**
```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.ecohandel.nl/" },
    { "@type": "ListItem", "position": 2, "name": "Kennisbank", "item": "https://www.ecohandel.nl/blogs/kennis" },
    { "@type": "ListItem", "position": 3, "name": "Korte artikeltitel" }
  ]
}
```

**c) FAQPage Schema** (als het artikel een FAQ sectie heeft)
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Vraagtekst",
      "acceptedAnswer": { "@type": "Answer", "text": "Antwoordtekst" }
    }
  ]
}
```

**Regels voor JSON-LD:**
- Antwoorden in FAQPage moeten exact overeenkomen met de zichtbare FAQ tekst
- Geen streepjes in de JSON-LD teksten
- Geen emoji's in de JSON-LD teksten

### 2. CSS Styling

Alle styling in een `<style>` blok. Kopieer de volledige CSS uit `GOLDEN_STANDARD_TEMPLATE.html`. De styling bevat:

- CSS custom properties (`--eco-green`, `--eco-green-light`, etc.)
- `.eco-kb` wrapper met Inter font, 17px base
- `.eco-breadcrumbs` visuele breadcrumbs
- `.eco-serie` serie-navigatie (links naar andere artikelen in de serie)
- `.eco-lead` intro paragraaf
- `.eco-toc` inhoudsopgave met genummerde items
- `.eco-tbl-wrap` + `.eco-tbl` gestylde tabellen met groene header
- `.eco-callout` + varianten (`-tip`, `-info`) voor highlights
- `.eco-calc` rekenvoorbeelden met blauw thema
- `.eco-product` product cards met hover-effect en badge
- `.eco-cta` call-to-action blok (donkergroen, witte buttons)
- `.eco-faq` accordion FAQ met chevron animatie
- Responsive breakpoints op 768px

**CTA Button styling (altijd fixen, elke publicatie):**
- Alle CTA-knoppen in een groene `.eco-cta` sectie zijn WIT met `#00A651` groene tekst.
- `.eco-cta-primary`: wit, `#00A651` tekst, shadow (1e knop)
- `.eco-cta-secondary`: wit, `#00A651` tekst, shadow (alle overige knoppen)
- NOOIT `background: transparent` of border-styled buttons in een groene CTA-achtergrond.
- Dit is een bekende valkuil bij elke publicatie — check altijd handmatig na publicatie.

### 3. HTML Content

Alles in een `<div class="eco-kb">` wrapper:

```
<div class="eco-kb">
  1. Visuele breadcrumbs (<nav class="eco-breadcrumbs">)
  2. Serie navigatie (<nav class="eco-serie">) - als onderdeel van serie
  3. Lead paragraaf (<p class="eco-lead">)
  4. Inhoudsopgave (<nav class="eco-toc">)
  5. Secties met <h2> en <h3>
  6. Tabellen in .eco-tbl-wrap
  7. Callouts in .eco-callout
  8. Rekenvoorbeelden in .eco-calc
  9. Product cards in .eco-product
  10. CTA blok in .eco-cta
  11. FAQ in .eco-faq met <details>/<summary>
  12. Onderste serie navigatie
</div>
```

---

## Styling Regels

### Kleurenpalet
| Kleur | Variabele | Hex | Gebruik |
|-------|-----------|-----|---------|
| Accentgroen | `--eco-green` | `#00A651` | Headings, accenten, CTA-knoppen |
| Hovergroen | `--eco-green-light` | `#27ae60` | Links, borders, actief |
| Lichgroen | `--eco-green-bright` | `#2ecc71` | Gradients, highlights |
| Achtergrond | `--eco-green-bg` | `#f0faf4` | Achtergronden |
| Donker | `--eco-green-dark` | `#007a39` | CTA gradient onderkant |
| Donkertekst | `--eco-dark` | `#0f1923` | H3, body accenten |
| Bodytekst | `--eco-text` | `#2c3e50` | Lopende tekst |

### Typografie
- Font: Inter, systeemfonts als fallback
- Body: 17px desktop, 16px mobiel
- H2: 1.65em, font-weight 800, met groene onderlijn (60px gradient)
- H3: 1.2em, font-weight 700
- Line-height: 1.8

### Componenten gebruiken

**Vergelijkingstabel:** voor voor/na vergelijkingen, opties naast elkaar
**Keypoint callout (tip):** gele achtergrond, voor kernpunten en adviezen
**Info callout:** groene achtergrond, voor productinfo of features
**Rekenvoorbeeld:** blauwe achtergrond, voor financiele berekeningen
**Product card:** witte kaart met groene top-border, hover-effect, badge (Populair/Bestseller)
**CTA blok:** donkergroene gradient, twee witte buttons
**FAQ:** accordions met chevron, open-state heeft groene border + shadow

---

## Interne Linking Regels

### Verplichte links (minimaal per artikel)
- 1 link naar relevante collectie (`/collections/thuisbatterijen`, `/collections/omvormers`, etc.)
- 1 link naar gerelateerd kennisartikel (`/blogs/kennis/...`)
- 1 commerciele vervolgstap (`/pages/contact`, advies, offerte)
- **Productlinks zijn expliciet toegestaan en gewenst** wanneer ze inhoudelijk logisch zijn. Denk aan relevante Deye omvormers, batterijen, wallboxen, CT-meters of accessoires. Dit versterkt interne linking én sales, zolang het natuurlijk blijft en geen spam wordt.
- Link alleen naar **bestaande** artikelen, collecties, pagina's en producten. Geen gok-handles.

### Serie navigatie
Als een artikel deel uitmaakt van een serie:
- Bovenaan: serie-navigatie met alle artikelen, huidige gemarkeerd
- Onderaan: serie-navigatie met "Lees verder" header
- Huidige artikel krijgt class `current` met groene dot
- Andere artikelen zijn klikbare links

### Link format
- Altijd relatieve paden: `/blogs/kennis/...`, `/collections/...`, `/products/...`
- Nooit absolute URLs met domein
- Blog handle is `kennis`, NIET `kennisbank`

---

## Workflow

### Stap 1: Markdown ophalen
Artikelen staan in `~/Documents/EcoHandel.nl/BLOGS/`. Lees de metadata uit de markdown header (titel, handle, SEO title, SEO description, tags, auteur).

### Stap 2: Markdown naar HTML
- Converteer content naar HTML binnen de golden standard structuur
- Kopieer de volledige CSS uit `GOLDEN_STANDARD_TEMPLATE.html`
- Bouw de drie JSON-LD blokken op basis van artikeldata
- Verwijder alle streepjes uit tekst
- Verwijder alle emoji's uit tekst
- Pas blog handle aan: `kennisbank` in bronbestanden wordt `kennis` in output

### Stap 3: Kwaliteitscheck
Voordat je publiceert, controleer:
- [ ] Geen streepjes in lopende tekst
- [ ] Geen emoji's in content
- [ ] Geen dubbele H1
- [ ] Alle interne links gebruiken `/blogs/kennis/` (niet `/blogs/kennisbank/`)
- [ ] Alle interne links wijzen naar **bestaande** live handles
- [ ] Geen `SolarMan` / `solarman app` als tag of voorkeursframing voor EcoHandel-content
- [ ] Auteur is één van: Milan, Tom, Jean
- [ ] Relevante productlinks toegevoegd waar dat de inhoud sterker maakt
- [ ] JSON-LD Article schema aanwezig en correct
- [ ] JSON-LD BreadcrumbList schema aanwezig
- [ ] JSON-LD FAQPage schema aanwezig (als FAQ sectie bestaat)
- [ ] FAQ antwoorden in JSON-LD matchen exact met zichtbare tekst
- [ ] CTA blok aanwezig met twee goed leesbare witte buttons
- [ ] Alle CTA-knoppen zijn WIT met #00A651-groene tekst (ook 2e, 3e, etc.) — geen transparante of bordered buttons
- [ ] Product cards linken naar echte Shopify product URLs
- [ ] Serie-navigatie klopt (huidige artikel gemarkeerd)
- [ ] Featured image staat als echte article image op Shopify
- [ ] Mobiele responsiveness (768px breakpoint)

### Stap 4: Publiceren naar Kennis blog
```python
import json, urllib.request

TOKEN = "..." # Via client credentials flow
payload = {
    "article": {
        "blog_id": 126678466901,
        "title": "Artikeltitel",
        "body_html": html_content,
        "handle": "url-handle-uit-metadata",
        "tags": "tag1, tag2, tag3",
        "author": "Milan",  # of Tom / Jean
        "summary_html": "SEO description als excerpt",
        "published": True,
        "metafields": [
            {"namespace": "global", "key": "title_tag", "value": "SEO titel", "type": "single_line_text_field"},
            {"namespace": "global", "key": "description_tag", "value": "SEO description", "type": "single_line_text_field"}
        ]
    }
}
```

### Stap 5: Preview sturen
Stuur Milan de preview link:
```
https://n6f6ja-qr.myshopify.com/blogs/kennis/{handle}?preview_theme_id=195769991509
```

### Stap 6: Post-publish checklist
- [ ] Artikel zichtbaar op `/blogs/kennis`
- [ ] Featured image zichtbaar op artikel zelf
- [ ] Featured image zichtbaar op blogkaart(en)
- [ ] Featured image zichtbaar op homepage/kennis-sectie als het artikel daar wordt getoond
- [ ] Cover past inhoudelijk goed bij het onderwerp
- [ ] Geen dubbele H1 in rendered output
- [ ] TOC anchor links werken
- [ ] Interne links kloppen en zijn klikbaar
- [ ] Mobiele styling klopt
- [ ] FAQ accordions openen/sluiten
- [ ] Product card buttons werken
- [ ] CTA buttons zijn goed leesbaar
- [ ] SEO title en meta description staan correct als metafields op het artikel
- [ ] Kleurgebruik klopt met #00A651 EcoHandel-logo-groen
- [ ] Google Rich Results Test: FAQ snippets zichtbaar
- [ ] Google Rich Results Test: Breadcrumbs zichtbaar

---

## Shopify API Referentie

### Token ophalen (24h geldig, herhaalbaar)
```bash
curl -s -X POST "https://n6f6ja-qr.myshopify.com/admin/oauth/access_token" \
  -d "client_id=7c26018c359fde447766ab15b9d0b30e" \
  -d "client_secret=$SHOPIFY_CLIENT_SECRET" \
  -d "grant_type=client_credentials"
```

### Artikel aanmaken
```
POST /admin/api/2024-10/articles.json
```

### Artikel updaten
```
PUT /admin/api/2024-10/articles/{id}.json
```

### Blog ID
`126678466901` (Kennis)

### Test Theme ID
`195769991509`
