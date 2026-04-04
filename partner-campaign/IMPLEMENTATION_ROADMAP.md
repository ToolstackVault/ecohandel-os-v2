# Implementation Roadmap — EcoHandel Partner Campaign

## Fase 1 — Fundament ✅
- architectuur
- database schema
- lead import
- score/report scripts
- Brevo event ingest skeleton

## Fase 2 — Brevo live wiring
Nog nodig van Milan:
- API key
- sender
- webhook secret/url
- testlijst details

Werk daarna:
- echte webhook endpoint
- echte campaign sync
- echte event mapping
- testcampagne

## Fase 3 — Prijslijst live koppelen
Nog nodig van Milan:
- HTML prijslijst

Werk daarna:
- link register vullen
- product/collectie mappings controleren
- tracking params toevoegen
- mobile QA

## Fase 4 — Daily command layer
- daily Telegram handoff
- hot lead escalaties
- reply samenvattingen
- unsubscribe/bounce hygiene alerts

## Fase 5 — Optimalisatie
- subject line vergelijking
- CTA vergelijking
- segment performance
- product-link heatmap
- lead-to-opportunity inzichten

## Giet-in-beton uitgangspunten
- lokale DB = waarheid
- Brevo = transport + events
- preview/test eerst
- geen lijstsend zonder test
- geen tracking zonder mapping
- dagelijkse opvolging is deel van het systeem, niet een nice-to-have
