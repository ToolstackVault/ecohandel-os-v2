# Deployment Plan — EcoHandel OS API naar VPS

**Doel:** Flask API (queue/agents/workflows) op VPS naast bestaande PHP API (partner campaign)

---

## Huidige Situatie

| Laag | VPS Status |
|------|-----------|
| Apache + PHP | ✅ Draait op poort 443 |
| PHP API (`/api/data.php`) | ✅ Draait, leest `data/ecohandel.db` |
| SQLite DB | ✅ `data/ecohandel.db` (827KB, actief) |
| Flask/Gunicorn | ❌ Niet geïnstalleerd |
| Python 3.12 | ✅ Beschikbaar op VPS |

---

## Aanpak: Apache → Flask via Reverse Proxy

```
HTTPS (443) → Apache → Proxy to Flask (port 5555)
                        ↓
                  Flask API v1
                  (queue/agents/workflows/activity)
                        ↓
                  Shared SQLite DB
                  (data/ecohandel.db)
```

### Voordelen:
- Bestaande PHP API blijft ongemoeid
- Flask API op zelfde domain (`control.ecohandel.nl/api/v1/`)
- Zelfde database, geen data duplicatie
- Apache handelt SSL + Basic Auth af

---

## Stappen (uit te voeren door Jean)

### Stap A: VPS — Flask installeren
```bash
ssh root@135.181.148.220
pip3 install flask gunicorn
mkdir -p /var/www/html/control.ecohandel.nl/api/v1
```

### Stap B: VPS — Flask app uploaden
```bash
# Lokale bestanden naar VPS:
scp API/app.py root@135.181.148.220:/var/www/html/control.ecohandel.nl/api/v1/
scp DATABASE/schema.sql root@135.181.148.220:/var/www/html/control.ecohandel.nl/
```

### Stap C: VPS — Database uitbreiden (alleen nieuwe tabellen)
```bash
# Onze tabellen toevoegen aan bestaande DB ( géén data verliezen )
sqlite3 /var/www/html/control.ecohandel.nl/data/ecohandel.db < /var/www/html/control.ecohandel.nl/schema.sql
```

### Stap D: VPS — Flask starten met Gunicorn
```bash
cd /var/www/html/control.ecohandel.nl
ECOHANDEL_DB=/var/www/html/control.ecohandel.nl/data/ecohandel.db \
gunicorn -w 2 -b 127.0.0.1:5555 api.v1.app:app \
  --daemon --pid /var/run/ecohandel-api.pid --log-file /var/log/ecohandel-api.log
```

### Stap E: VPS — Apache proxy naar Flask
```apache
# /etc/apache2/sites-enabled/control.ecohandel.nl.conf
# Toevoegen inside <VirtualHost *:443>:

ProxyPass /api/v1/ http://127.0.0.1:5555/
ProxyPassReverse /api/v1/ http://127.0.0.1:5555/

<Location "/api/v1/">
    Require all granted
</Location>
```
```bash
a2enmod proxy proxy_http
systemctl reload apache2
```

### Stap F: Lokale sync naar VPS DB
```bash
# Eerste keer: lokale data naar VPS sync
python3 SCRIPTS/sync_db.py --full  # lokaal
scp DATABASE/ecohandel.db root@135.181.148.220:/var/www/html/control.ecohandel.nl/data/ecohandel.db

# Let op: dit overschrijft partner campaign data!
# Beter: alleen tabellen toevoegen, geen full replace
```

---

## Alternatief: FarmQ/Gunicorn als service

```bash
# Systemd service: /etc/systemd/system/ecohandel-api.service
[Unit]
Description=EcoHandel OS API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/html/control.ecohandel.nl
Environment="ECOHANDEL_DB=/var/www/html/control.ecohandel.nl/data/ecohandel.db"
ExecStart=/usr/local/bin/gunicorn -w 2 -b 127.0.0.1:5555 api.v1.app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable ecohandel-api
systemctl start ecohandel-api
```

---

## API Endpoints (Flask, na deploy)

```
GET  https://control.ecohandel.nl/api/v1/health
GET  https://control.ecohandel.nl/api/v1/queue
POST https://control.ecohandel.nl/api/v1/queue/items
PATCH https://control.ecohandel.nl/api/v1/queue/items/{id}
GET  https://control.ecohandel.nl/api/v1/queue/health
GET  https://control.ecohandel.nl/api/v1/agents/status
POST https://control.ecohandel.nl/api/v1/agents/trigger/{agent}
GET  https://control.ecohandel.nl/api/v1/workflows
POST https://control.ecohandel.nl/api/v1/workflows/{id}/run
GET  https://control.ecohandel.nl/api/v1/activity
GET  https://control.ecohandel.nl/api/v1/campaigns/stats
```

---

## Authenticatie

- **Flask API:** HTTP Basic Auth (`milan:ecohandel2026`, `tom:tom2026`)
- **Jean/Paperclip:** Bearer token
- Apache Basic Auth blijft voor de HTML dashboard pages

---

## Belangrijk: Database Merge Strategie

De VPS DB heeft AL bestaande tabellen. De Flask schema.sql moet:
1. `CREATE TABLE IF NOT EXISTS` gebruiken (geen DROP)
2. Alleen de NIEUWE tabellen toevoegen (queue_items, workflows, etc.)
3. **NIET** de bestaande tabellen overschrijven

Bestaande tabellen op VPS:
- `partner_aanvragen`
- `installer_leads`
- `webhook_events`
- `campaigns`
- `campaign_stats`
- `hot_event_queue`
- `partner_visits`
- `installer_email_registry`

Nieuwe tabellen voor Flask:
- `queue_items`
- `workflows`
- `workflow_runs`
- `agent_runs`
- `queue_health`
- `activity_log`
- `learning_entries`
- `publish_requests`
- `users`
- `tenants`

---

## Status

- [ ] Stap A: Flask installeren op VPS
- [ ] Stap B: Flask app uploaden naar VPS
- [ ] Stap C: Database tabellen toevoegen (IF NOT EXISTS)
- [ ] Stap D: Gunicorn starten
- [ ] Stap E: Apache proxy config
- [ ] Stap F: Eerste data sync
- [ ] Stap G: Test van remote API
