# EcoHandel Handover — Main Focus

**Audience:** Opus 4.6 / high-context strategic continuation  
**Owner:** Jean Clawd / Milan / Tom  
**Status:** Active, main focus  
**Priority:** Highest

---

## 1. Executive Summary

**EcoHandel is now the main focus.**
This is not a side project or a simple webshop support track. The current direction is to turn EcoHandel into a tightly managed growth system with:

- **Econtrol Room** as the mission board / command center
- **Jean Clawd** as orchestration layer
- **Smart Content Queue** as prioritization engine
- **Partner Campaign System** as autonomous outbound + intelligence machine
- **Wefact + Shopify + GA4 + GSC + Google Ads** as the core business telemetry stack

Key strategic truth:
- **Econtrol Room is the main system**
- **EcoDash stays separate**
- Patterns/data may be reused, but systems should not be merged carelessly  
Source: `MEMORY.md#L582-L591`, `memory/2026-03-27.md#L1-L36`

---

## 2. Main Strategic Goals

### A. Build EcoHandel into a controlled growth machine
Priority order remains business-first:
1. direct revenue / customers / conversions
2. growth via SEO / content / lead systems
3. optimization / process / visibility
4. nice-to-have polish

### B. Make Econtrol Room the daily cockpit
It should surface:
- traffic
- SEO
- ads
- Shopify revenue
- Wefact finance truth
- queue priorities
- workflows
- partner campaign status
- mobile mission-layer access

### C. Build a fully autonomous partner email campaign system
This is one of the most important new projects.
It must:
- run via **Brevo**
- use a **mobile responsive interactive price list**
- link to **real Shopify products/collections**
- log opens / clicks / replies / unsubscribes / bounces
- maintain a **local database as source of truth**
- produce a **daily hot prospect handoff**
- improve over time autonomously

### D. Keep finance grounded in reality
Important business correction:
- **Shopify revenue is not the full truth**
- a significant part of EcoHandel reality runs through **Wefact**
- therefore Wefact is essential for reliable validation  
Source: `MEMORY.md#L582-L591`, `memory/2026-03-27.md#L187-L213`

---

## 3. Hard Rules

### Theme / publishing safety
- **Never publish or change in live theme directly**
- Always use **underwater / test / preview first**
- Milan reviews first, then live

### Econtrol Room mobile layer
- mobile shell is **read-only / insight-first**
- no controls pushed into the iPhone layer
- compact, fast, mission-board oriented

### Partner campaign scope
- use **EcoHandel leads only**
- do **not** contaminate with Nova-Cell or other company leads
- if in doubt: route to review list, not first send list

### Link mapping
- never guess product links
- if exact product certainty is missing, use the correct collection fallback
- do not use draft / unlisted / slug-mismatch products as primary links

### Model cost discipline
- **Anthropic tokens are expensive**
- this system must be **token-efficient by design**
- use **Opus 4.6 selectively** for high-value reasoning/strategy
- use **GPT-5.4 / Codex** for orchestration, control, difficult execution, routine analysis, and operational tasks when possible

---

## 4. What Has Already Been Built

## 4.1 Econtrol Room / mission board
Current live control room:
- `https://control.ecohandel.nl/`

Main routes:
- `/` → dashboard
- `/smart-content-queue.html`
- `/workflows.html`
- `/partner-campaign.html`

Important direction:
- old `Agents` concept has been replaced conceptually by **Workflows**
- Econtrol Room is now treated as the mission board
- a mobile app-like shell was built on top of it  
Source: `memory/2026-03-27.md#L1-L36`, `memory/2026-03-27.md#L77-L110`

### Current Econtrol capabilities
- dashboard with GA4 / GSC / Google Ads / Shopify / Wefact
- queue page
- workflows page
- partner campaign page
- iPhone-friendly responsive shell
- EcoHandel favicon/app-icon branding work in progress / partially integrated

### Important implementation note
The mobile shell originally tried a more app-like standalone behavior, but because of Apache Basic Auth + iPhone behavior, the safer path became:
- Safari-compatible browser-mode
- add-to-homescreen still useful
- less reliance on unstable iOS standalone auth behavior

---

## 4.2 Wefact integration
Wefact is now **read-only validated** and wired into dashboard logic.

### Confirmed
- Wefact API key for **EcoHandel administration** works
- IP whitelist for `84.85.55.133` is active
- API endpoint works read-only
- debtors, invoices, and price quotes return data

### Current purpose
- show finance truth beside Shopify
- later expand to:
  - customer follow-up
  - quote follow-up
  - outstanding invoices
  - relationship + mailbox logic

### Important implementation lesson
The Wefact fetcher initially used an older shell env value before the updated `.env/apis.env` value.
This caused false zero-values. The fix was to prioritize file-config first.

---

## 4.3 Content system for EcoHandel articles
A proper content system location was created so markdown articles can later be transformed and published consistently.

### Source of truth
- `ecohandel/content-system/kennisblog/PUBLISH_PLAYBOOK.md`
- `ecohandel/content-system/kennisblog/TEMPLATE.html`
- `ecohandel/content-system/kennisblog/publish_article.py`
- `ecohandel/econtrol-room/scripts/publish_ecohandel.py`
- `ecohandel/econtrol-room/sources/publish-system.json`

### Publishing rules
- markdown in
- clean HTML out
- internal linking required
- no live theme editing
- preview-first / underwater-first

---

## 4.4 Partner Campaign System (major priority)
This is one of Jean’s most important projects now.

### Core docs
Located in:
- `ecohandel/partner-campaign/`

Main docs:
- `README.md`
- `SYSTEM_ARCHITECTURE.md`
- `DATA_MODEL.sql`
- `BREVO_WEBHOOK_SPEC.md`
- `PRICELIST_LINKING_SPEC.md`
- `DAILY_OPERATIONS.md`
- `SCORING_MODEL.md`
- `CAMPAIGN_BLUEPRINT.md`
- `AUTONOMY_RULES.md`
- `IMPLEMENTATION_ROADMAP.md`

### Working assets/scripts already created
- `scripts/bootstrap_db.py`
- `scripts/import_leads.py`
- `scripts/report_hot_prospects.py`
- `scripts/ingest_brevo_event.py`
- `scripts/recalculate_scores.py`
- `scripts/classify_replies.py`
- `scripts/run_daily_cycle.py`
- `scripts/export_ecohandel_ready_leads.py`
- `scripts/build_ai_link_mapping.py`

### Database
- SQLite database exists and is operational:
  - `ecohandel/partner-campaign/data/partner_campaign.db`

### Lead import state
- existing lead file imported:
  - `ecohandel/lead-generation/leads/LEADS.csv`
- **174 leads imported** into local partner campaign database

### EcoHandel-only campaign filtering
This campaign must use **EcoHandel-only** leads.
Files created:
- `ecohandel/partner-campaign/ECOHANDEL_SCOPE_RULES.md`
- `ecohandel/partner-campaign/data/ECOHANDEL_LEADS_READY.csv`
- `ecohandel/partner-campaign/data/ECOHANDEL_LEADS_REVIEW.csv`

Current split:
- **130 ready leads**
- **34 review leads**

Important practical note for future sessions:
- these are the **installateur / partner leads from earlier runs**, distinct from the later raw bulk lists Milan uploaded afterward
- inside the current ready file, **66 leads have an email address** and are immediately usable for Brevo imports
- the remaining **64 ready leads without email** should stay in local DB / review / enrichment flow until contact data is completed
- because some companies share the same mailbox, Brevo may show a slightly lower unique subscriber count than the raw email-row count

### Conceptual rule
Brevo is **not** the source of truth.
The local DB is.
This is critical.
Brevo handles transport/events; local DB handles:
- scoring
- state
- hotness
- exclusions
- daily handoff
- future intelligence

---

## 5. Email Campaign Direction

## 5.1 Big picture
The partner campaign should become a **fully autonomous outreach system**.

The mail should focus on:
- becoming a partner
- engaging installateurs / resellers / relevant EcoHandel-fit prospects
- using a strong CTA structure
- linking into an **interactive HTML price list**
- tracking all meaningful behaviors

### Desired tracked signals
- delivered
- open / unique open
- click / unique click
- price list click
- product click
- reply
- unsubscribe
- bounce

### Daily output
Jean should eventually send a daily handoff with:
- hottest prospects
- new replies
- people with multiple opens
- people who clicked price list / product links
- unsubscribe/bounce hygiene
- action recommendation:
  - BEL VANDAAG
  - HANDMATIG MAILEN
  - OPVOLGEN
  - UITSLUITEN

---

## 5.2 Current Brevo state
Brevo for EcoHandel is now **successfully connected at baseline level**.

### Confirmed
- Brevo account is active on `info@ecohandel.nl`
- sender `info@ecohandel.nl` is active in Brevo
- EcoHandel domain authentication has been added in Brevo
- DMARC `rua` warning was fixed on `ecohandel.nl`
- current DMARC record:
  - `_dmarc.ecohandel.nl` → `v=DMARC1; p=none; rua=mailto:rua@dmarc.brevo.com`

### Stored config / operational values
- sender name: `EcoHandel.nl`
- sender email: `info@ecohandel.nl`
- SMTP relay: `smtp-relay.brevo.com:587`
- active webhook endpoint:
  - `https://control.ecohandel.nl/hooks/brevo/partner-campaign/?token=<BREVO_ECOHANDEL_WEBHOOK_SECRET>`

### Important nuance
- this confirms the **Brevo coupling is in place** for sender/domain/compliance baseline
- the webhook route has now been fixed server-side:
  - only `/hooks/brevo/partner-campaign/` is public
  - the rest of `control.ecohandel.nl` stays behind Basic Auth
  - the webhook uses a tokenized URL because Brevo was configured with **No auth**
- important path detail: use the route **with trailing slash** before `?token=...`
- manual GET/POST tests returned **200 OK** with the tokenized URL and wrote to the webhook log successfully
- log file currently used:
  - `/var/www/html/control.ecohandel.nl/data/brevo-webhook.ndjson`
- event ingest / campaign intelligence layer still belongs in the local partner-campaign system

Brevo remains especially important for:
- tracking
- webhooks
- automation
- campaign analytics
- contact/list management via API
- campaign visibility checks via API

### Brevo management layer now available
Inside `ecohandel/partner-campaign/` the following are now the fixed management entrypoints:
- `scripts/brevo_api.py` → operational API control script
- `BREVO_API_MANAGEMENT.md` → command examples / usage
- `config.local.json` → active EcoHandel Brevo config, webhook URLs, sender, and management flags

Confirmed live via API status check:
- account = `200`
- senders = `200`
- contact lists = `200`
- email campaigns = `200`
- current Brevo account email = `info@ecohandel.nl`
- current visible list count at check time = `1`
- current visible recent campaign count at check time = `0`

This means future sessions can manage:
- contact imports into Brevo lists
- list creation
- campaign checks
- later campaign creation/automation expansions
without re-solving auth or config first.

### Existing installer leads from earlier runs are now also reflected in Brevo
To avoid confusion with the later raw uploads from Milan/Tom, the earlier curated installer batch has now been represented in Brevo separately:
- source file used: `ecohandel/partner-campaign/data/ECOHANDEL_LEADS_READY.csv`
- dedicated Brevo list created: `EcoHandel Installateurs - eerdere runs`
- Brevo list id: `3`
- rows with email in source file: `66`
- skipped because no email present: `64`
- Brevo unique subscribers after import check: `65`

Why the Brevo count is lower than 66:
- at least one row shares an email address already used by another contact/company, so Brevo collapses by unique contact identity

Operational rule:
- treat this Brevo list as the current clean starting point for installer outreach based on earlier research runs
- keep the later raw upload batches separate until cleaned/deduplicated/reviewed

---

## 5.3 Price list / interactive HTML pricing
This is central to the partner campaign.

### Requirements
- mobile responsive
- clear CTAs
- partner-oriented structure
- links must point to **real Shopify products or collections**
- must be safe for future AI-assisted editing

### Current shared work location
A joint Antigravity workspace has been created:
- `ecohandel/shared/antigravity-workspace/`

Contents:
- `logo/` → EcoHandel branding assets
- `prijslijst/ecohandel-deye-prijslijst-v2.html`
- `README.md`

### Branding note
- shared workspace note says to keep using the EcoHandel branding assets from `logo/`
- the current HTML file itself already contains its own styling and should be treated as the active working version unless deliberately replaced

### Current file path used for shared pricing work
**Current sending master / preferred handoff route:**
- `ecohandel/shared/antigravity-workspace/prijslijst/EcoHandel_DeyeV3_embedded_leaf-perfect.html`

**Original source file on disk:**
- `/Users/ecohandel.nl/Documents/EcoHandel.nl/Prijslijst/EcoHandel_DeyeV3.html`

**Current mail-safe master on disk:**
- `/Users/ecohandel.nl/Documents/EcoHandel.nl/Prijslijst/EcoHandel_DeyeV3_embedded_leaf-perfect.html`

**Earlier embedded variant still exists:**
- `/Users/ecohandel.nl/Documents/EcoHandel.nl/Prijslijst/EcoHandel_DeyeV3_embedded.html`

**Legacy/shared earlier file still exists:**
- `ecohandel/shared/antigravity-workspace/prijslijst/ecohandel-deye-prijslijst-v2.html`

**Workspace copy used by partner-campaign system:**
- `ecohandel/partner-campaign/assets/prijslijst/ecohandel-deye-prijslijst-v2.html`

### Handoff rule for Opus / Antigravity
If Opus 4.6 or Antigravity needs the latest pricing HTML, start here first:
1. `ecohandel/shared/antigravity-workspace/prijslijst/EcoHandel_DeyeV3_embedded_leaf-perfect.html`
2. if needed, compare back to the original source file `/Users/ecohandel.nl/Documents/EcoHandel.nl/Prijslijst/EcoHandel_DeyeV3.html`
3. treat the `leaf-perfect` embedded file as the **current sending master** because it no longer depends on local image paths and it preserved the preferred EcoHandel leaf-background header that Milan explicitly approved

### Important mail rendering lesson
- the non-embedded version missed local images when sent externally
- one later embedded variant fixed the gray-header fallback, but visually lost the preferred leaf-background look
- the winning fix was: keep all local assets embedded **and** preserve the leaf-background hero that still renders correctly in mail
- Milan explicitly approved `EcoHandel_DeyeV3_embedded_leaf-perfect.html` as the perfect version and asked to store it as the master

---

## 5.4 AI-safe link mapping for pricing list
Because the pricing list is likely to be touched by AI tooling, safe link mapping files were created.

### Main files
- `ecohandel/partner-campaign/AI_LINK_MAPPING_VALIDATED.md`
- `ecohandel/partner-campaign/ai-link-mapping.json`
- `ecohandel/partner-campaign/LINK_MAPPING_REVIEW_NOTES.md`
- `ecohandel/partner-campaign/AI_LINK_MAPPING_PROMPT_INPUT.md`

### Rules
- use HIGH confidence links directly
- use MEDIUM confidence links only with exact product match
- fallback to collection when uncertain
- never invent product links
- never use draft/unlisted/mismatch links as primary output

This is important because the pricing list should be trustworthy and directly useful for campaign traffic.

---

## 6. Branding Assets
A proper branding folder was created in the workspace for later EcoHandel projects.

### Branding root
- `ecohandel/branding/`

### Logo assets
- `ecohandel/branding/logo/`

Includes:
- wordmark assets
- wordmark + icon assets
- RGB / CMYK exports
- favicon assets
- PNG / SVG / PDF / AI / EPS variants

### Branding note
- **DM Sans** is the font to remember and reuse

### Favicon
Favicon was downloaded from Google Drive and reused for Econtrol Room branding work.
Relevant path:
- `ecohandel/econtrol-room/assets/branding/Favicon.png`

---

## 7. Technical Access / Integrations / Important Paths

## 7.1 Shopify / EcoHandel
Important note: for theme/content work, be careful with theme safety.
Do not assume live theme editing is allowed.
Use preview/test/underwater flow first.

### Known store references from workspace notes
- Admin: `https://admin.shopify.com/store/n6f6ja-qr`
- MyShopify domain: `n6f6ja-qr.myshopify.com`
- Primary domain: `https://www.ecohandel.nl`

### Knowledge blog
- Blog ID: `126678466901`
- Handle: `kennis`

---

## 7.2 Econtrol Room live
- Domain: `https://control.ecohandel.nl`
- Protected by Apache Basic Auth
- Mobile add-to-homescreen works best via Safari/browser mode

### Operational caveat
Permissions on `/var/www/html/control.ecohandel.nl` fell back multiple times and caused auth/post-login errors.
Fix required:
- owner `www-data:www-data`
- dirs `755`
- files `644`

This is an infra reliability point worth hardening later.

---

## 7.3 Wefact
- Base URL: `https://api.mijnwefact.nl/v2/`
- IP whitelist target: `84.85.55.133`
- Integration is active read-only
- Do **not** casually spread the API key in notes or generated docs

---

## 7.4 Shared Antigravity workspace
- `ecohandel/shared/antigravity-workspace/`

Use this as joint working area for:
- design handoff
- pricing list evolution
- branding asset access

---

## 8. Immediate Next Priorities

### Highest practical next moves
1. **Finish Brevo integration for EcoHandel**
   - verified sender
   - webhook details
   - campaign config
   - test list

2. **Finalize interactive pricing list**
   - keep it mobile responsive
   - check CTA structure
   - validate product/collection links
   - keep it AI-safe

3. **Integrate pricing list into partner campaign system**
   - register tracked links
   - add UTMs / campaign metadata
   - ensure price list clicks + product clicks are stored

4. **Upgrade partner page in Econtrol Room further**
   - alerts
   - blockers
   - readiness
   - hot lead trends
   - next actions

5. **Mailbox integration later**
   - `info@ecohandel.nl` should eventually be linked
   - goal: unify replies / follow-up / Wefact / campaign logic

---

## 9. What Opus 4.6 Should Focus On

Opus should be used for **high-value reasoning**, especially:
- campaign strategy
- partner proposition refinement
- CTA and email architecture
- pricing list persuasion structure
- system design decisions
- identifying weak spots in autonomous flows

Avoid spending Opus on repetitive operational work if Codex/GPT-5.4 can do it.

### Good Opus tasks
- refine partner email strategy
- improve segmentation logic
- sharpen conversion paths from email → pricing list → product → reply/call
- critique whether the campaign system matches EcoHandel’s business model
- design follow-up logic that combines pricing list behavior + Wefact + mailbox later

### Bad Opus tasks
- repetitive polling
- routine file reshuffling
- bulk formatting
- simple operational reruns
- low-value monitoring loops

---

## 10. Recommended Reading Order for Opus

If Opus needs to get up to speed fast, read in this order:

1. `ecohandel/HANDOVER_OPUS46_ECOHANDEL_MAIN_FOCUS.md`  
2. `ecohandel/STATUS.md`  
3. `ecohandel/partner-campaign/README.md`  
4. `ecohandel/partner-campaign/SYSTEM_ARCHITECTURE.md`  
5. `ecohandel/partner-campaign/SCORING_MODEL.md`  
6. `ecohandel/partner-campaign/CAMPAIGN_BLUEPRINT.md`  
7. `ecohandel/partner-campaign/PRICELIST_LINKING_SPEC.md`  
8. `ecohandel/partner-campaign/AI_LINK_MAPPING_VALIDATED.md`  
9. `ecohandel/shared/antigravity-workspace/README.md`  
10. current pricing list file in shared workspace

---

## 11. Final Orientation

If you remember only five things, remember these:

1. **EcoHandel is the main focus**
2. **Econtrol Room is the mission board**
3. **Shopify is not the full financial truth — Wefact matters**
4. **The partner campaign with interactive HTML price list is a key autonomous system**
5. **Be smart with model costs: use Opus selectively, use GPT-5.4/Codex aggressively where appropriate**
