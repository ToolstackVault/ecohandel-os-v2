# Uitgebreide SEO Analyse - EcoHandel.nl
**Datum:** 4 april 2026
**Type:** Read-only Frontend Analyse

## 1. Executive Summary & Kritieke Issues
Er is een **kritiek probleem** ontdekt op de live versie van de website (zowel homepage als collectie-pagina's). 
- **ONTBREKENDE `<title>` EN `<meta name="description">`:** De standaard HTML title en meta description ontbreken volledig in de `<head>` van de broncode. OpenGraph en Twitter tags zijn wel aanwezig (`og:title`, `twitter:title`), maar zoekmachines zoals Google leunen primair op de standaard `<title>` en `<meta name="description">`. Dit is een enorme SEO-blokkade die waarschijnlijk in `theme.liquid` of een gerelateerde snippet zit.

## 2. Heading Structuur (H1, H2, H3)
De heading-hiërarchie op de homepage is niet optimaal:
- **H1 Tags:** Er zijn 2 H1-tags aanwezig.
  1. Een lege H1 tag (`<h1> </h1>` of vergelijkbaar).
  2. `<h1>De enige échte Deye specialist van Nederland.</h1>`
  *SEO Best Practice:* Er hoort precies één H1-tag te zijn per pagina die het hoofdonderwerp beschrijft. Een lege H1 is een technische fout.
- **H2 Tags:** Er zijn 26 H2-tags aanwezig. Veel hiervan worden gebruikt voor UI-elementen in plaats van content structuur (bijv. "Je winkelwagen", "Land/regio"). Dit verwatert de semantische waarde van H2's voor zoekmachines.

## 3. Social & Open Graph Tags
De Open Graph tags voor social media sharing (Facebook, LinkedIn, etc.) en Twitter Cards functioneren goed:
- **OG Title:** `Thuisbatterij kopen? DEYE hybride omvormers & opslag | EcoHandel` (Aanwezig en goed geoptimaliseerd)
- **OG Description:** `Koop een thuisbatterij of DEYE hybride omvormer bij EcoHandel. Onafhankelijk advies, technische ondersteuning, installatie via partners en snelle levering in heel Nederland.` (Aanwezig)
- **OG Image:** Aanwezig (Favicon of logo wordt geladen via Shopify CDN).

## 4. Afbeeldingen & Media
- Er zijn 39 afbeeldingen (`<img>` tags) gedetecteerd op de homepage.
- **2 afbeeldingen missen een `alt`-attribuut.** Alt-teksten zijn belangrijk voor toegankelijkheid en image-SEO. Alle afbeeldingen, zeker product- en sfeerbeelden, horen beschrijvende alt-teksten te hebben.

## 5. Structured Data (JSON-LD)
Schema markup is goed geïmplementeerd op de homepage. De volgende Schema.org types zijn gedetecteerd:
- `LocalBusiness`
- `BreadcrumbList`
- `Organization`
- `WebSite`
*Conclusie:* Dit is uitstekend voor Rich Snippets in Google.

## 6. Technische Basis (Robots.txt & Canonical)
- **Canonical Tag:** Is correct geïmplementeerd (`<link rel="canonical" href="https://www.ecohandel.nl/">`). Dit voorkomt duplicate content problemen.
- **Robots.txt:** De standaard Shopify robots.txt is aanwezig en correct geconfigureerd. Het sluit dynamische URL's, checkouts en interne zoekopdrachten netjes uit.
- **Sitemap:** Wordt correct gedeclareerd in robots.txt (`https://www.ecohandel.nl/sitemap.xml`).
- **HTTPS:** Site forceert correct SSL/TLS.

## 📝 Actieplan voor JeanTestV1 Thema (Voor later)
1. **Prio 1:** Fix het ontbreken van de standaard `<title>` en `<meta name="description">` tags in de `<head>` (Liquid bestanden controleren, wsl. `theme.liquid`).
2. **Prio 2:** Verwijder de lege `<h1>` op de homepage en zorg dat UI-elementen in het winkelwagentje (zoals "Je winkelwagen") geen `<h2>` zijn maar `<div>` of `<span>` met CSS styling.
3. **Prio 3:** Loop ontbrekende `alt`-attributen na in de theme beeldbestanden.
