# Brevo Webhook Recommendation — EcoHandel Partner Campaign

## Recommended webhook URL
Use:

`https://control.ecohandel.nl/hooks/brevo/partner-campaign`

## Why this URL
- `control.ecohandel.nl` is already the EcoHandel mission board / control domain
- keeps tracking logic close to Econtrol Room
- clear separation from public webshop routes
- future-proof for daily reporting and hot prospect logic

## Expected behavior
This endpoint should:
1. validate webhook secret / signature
2. accept Brevo POST events
3. store raw payload
4. map event to lead/campaign/link
5. update local partner campaign DB
6. trigger score refresh / hot prospect logic
7. feed Econtrol Room partner page

## Event types to handle
- delivered
- opened
- clicked
- unsubscribe
- hard_bounce
- soft_bounce
- reply (or reply-equivalent via inbox flow)

## Important note
For now, `control.ecohandel.nl` uses Basic Auth. Before live webhook use, make sure the webhook route is either:
- excluded from Basic Auth, or
- served behind a server-side route/proxy that Brevo can reach without browser auth.

## Recommendation
Preferred implementation path:
- webhook endpoint under `control.ecohandel.nl`
- route excluded from browser auth
- local DB remains source of truth
- Econtrol Room reads processed state, not raw event payloads
