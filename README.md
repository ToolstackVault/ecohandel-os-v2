# EcoHandel OS

Besturingssysteem voor EcoHandel.nl — Econtrol Room, Partner Campaigns, SEO Intelligence, en Content System.

## Projectstructuur

```
ecohandel/
├── econtrol-room/         # Econtrol Room OS (main dashboard)
│   ├── DATABASE/          # SQLite schema + seed
│   ├── scripts/           # Render, deploy, sync, ops cycle
│   └── state/             # JSON state files
├── partner-campaign/      # Brevo partner mailcampagne systeem
├── lead-generation/       # B2B lead research & scoring
├── seo/                   # SEO audits, GSC analyse
├── marketing/             # Google Ads tracking & reporting
├── deye-kennis/           # Deye kennisblog publicatie systeem
├── content-system/        # Smart content queue
└── branding/              # Logo's, house style
```

## Architectuur

- **Database:** SQLite (`econtrol-room/DATABASE/ecohandel.db`)
- **API:** Flask/JSON endpoints (in ontwikkeling)
- **Frontend:** Statische HTML dashboards (Econtrol Room)
- **Deployment:** VPS (Hetzner) via GitHub Actions
- **Data sources:** Shopify, Brevo, Wefact, Google Ads, GSC

## Development

```bash
# Clone
git clone https://github.com/ToolstackVault/ecohandel-os.git
cd ecohandel-os

# Python env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Lokale database
sqlite3 econtrol-room/DATABASE/ecohandel.db < econtrol-room/DATABASE/schema.sql
```

## Deployment

Push naar `main` → GitHub Actions deployt automatisch naar VPS.

## Contact

EcoHandel.nl — Duurzame energie webshop
