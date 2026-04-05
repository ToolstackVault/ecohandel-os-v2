from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, os, json, subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

app = FastAPI(title="EcoHandel OS API v2")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path("/var/www/html/control.ecohandel.nl")
DATA_DIR = BASE_DIR / "dashboard-data" / "data"
DB_PATH = os.environ.get("ECOHANDEL_DB", "/var/www/html/control.ecohandel.nl/data/ecohandel.db")
ENV_FILE = BASE_DIR / ".env"
API_VERSION = "2.0"
DEFAULT_TENANT = "eco001"
GSC_SA = "/var/www/html/control.ecohandel.nl/.gsc-sa.json"

# Load env
for line in ENV_FILE.read_text().splitlines():
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def json_read(name, default=None):
    path = DATA_DIR / name
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return default or {}


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_py(code, timeout=60):
    env = os.environ.copy()
    env["GOOGLE_APPLICATION_CREDENTIALS"] = GSC_SA
    r = subprocess.run(
        ["/opt/ecohandel-venv/bin/python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, env=env
    )
    try:
        return json.loads(r.stdout.strip())
    except Exception:
        return {"error": r.stderr.strip() or r.stdout.strip()}


# ── Data fetch helpers ─────────────────────────────────────────────────────────

def fetch_gsc():
    sa_path = GSC_SA
    code = f"""
import json
from google.oauth2 import service_account
import googleapiclient.discovery
from datetime import datetime, timezone, timedelta
try:
    creds = service_account.Credentials.from_service_account_file(
        '{sa_path}', scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
    svc = googleapiclient.discovery.build('searchconsole', 'v1', credentials=creds)
    today = datetime.now(timezone.utc).date()
    start = (today - timedelta(days=28)).isoformat()
    end = today.isoformat()
    res = svc.searchanalytics().query(
        siteUrl='sc-domain:ecohandel.nl',
        body={{'startDate': start, 'endDate': end, 'dimensions': ['query'],
              'rowLimit': 20, 'aggregationType': 'byPage'}}).execute()
    rows = res.get('rows', [])
    top = []
    for row in rows[:10]:
        top.append({{
            'query': row['keys'][0],
            'clicks': row['clicks'],
            'impressions': row['impressions'],
            'position': round(row['position'], 1)
        }})
    total_clicks = sum(r['clicks'] for r in rows)
    total_impr = sum(r['impressions'] for r in rows)
    print(json.dumps({{
        'clicks': total_clicks,
        'impressions': total_impr,
        'ctr': round(total_clicks/total_impr*100, 1) if total_impr else 0,
        'top_queries': top,
        'fetched_at': datetime.now(timezone.utc).isoformat()
    }}))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
    return run_py(code)


def fetch_ga4():
    sa_path = GSC_SA
    prop_id = os.environ.get("GA4_PROPERTY_ID", "529517517")
    code = f"""
import json
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest
from datetime import datetime, timezone, timedelta
try:
    creds = service_account.Credentials.from_service_account_file(
        '{sa_path}', scopes=['https://www.googleapis.com/auth/analytics.readonly'])
    client = BetaAnalyticsDataClient(credentials=creds)
    today = datetime.now(timezone.utc).date()
    end = today.isoformat()
    start_28 = (today - timedelta(days=28)).isoformat()
    start_7 = (today - timedelta(days=7)).isoformat()
    def run(start):
        req = RunReportRequest(
            property='properties/{prop_id}',
            date_ranges=[{{'start_date': start, 'end_date': end}}],
            metrics=[{{'name': 'sessions'}}, {{'name': 'totalRevenue'}}, {{'name': 'conversions'}}])
        r = client.run_report(request=req)
        if r.rows:
            return {{
                'sessions': int(r.rows[0].metric_values[0].value),
                'revenue': float(r.rows[0].metric_values[1].value),
                'conversions': int(r.rows[0].metric_values[2].value)
            }}
        return {{'sessions': 0, 'revenue': 0.0, 'conversions': 0}}
    print(json.dumps({{
        'last_28_days': run(start_28),
        'last_7_days': run(start_7),
        'fetched_at': datetime.now(timezone.utc).isoformat()
    }}))
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
"""
    return run_py(code)


def fetch_shopify():
    token = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
    shop = os.environ.get("SHOPIFY_STORE_URL", "n6f6ja-qr.myshopify.com")
    if not token:
        return {"orders_today": 0, "revenue_today": 0.0, "error": "no_token"}
    code = f"""
import json, urllib.request
from datetime import datetime, timezone
TOKEN = '{token}'
SHOP = '{shop}'
today = datetime.now(timezone.utc).date().isoformat()
url = 'https://' + SHOP + '/admin/api/2026-01/orders.json?status=any&created_at_min=' + today + 'T00:00:00Z&limit=250'
req = urllib.request.Request(url, headers={{'X-Shopify-Access-Token': TOKEN}})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read())
orders = data.get('orders', [])
revenue = sum(float(o.get('total_price', 0)) for o in orders)
print(json.dumps({{
    'orders_today': len(orders),
    'revenue_today': round(revenue, 2),
    'orders_28d': 0,
    'revenue_28d': 0.0,
    'fetched_at': datetime.now(timezone.utc).isoformat()
}}))
"""
    return run_py(code, timeout=30)


def fetch_wefact():
    key = os.environ.get("WEFACT_API_KEY", "")
    url = os.environ.get("WEFACT_BASE_URL", "https://api.mijnwefact.nl/v2")
    if not key:
        return {"omzet": 0, "openstaand": 0, "facturen": 0, "error": "no_api_key"}
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-d", f"api_key={key}",
        "-d", "controller=invoice",
        "-d", "action=list",
        "-d", "limit=100"
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        raw = json.loads(r.stdout)
    except Exception:
        return {"omzet": 0, "openstaand": 0, "facturen": 0, "error": "parse_error", "raw": r.stdout[:200]}
    invoices = raw.get("invoices", []) if isinstance(raw, dict) else []
    now = datetime.now(timezone.utc)
    this_month = [i for i in invoices if str(i.get("Date", "")).startswith(now.strftime("%Y-%m"))]
    paid = [i for i in invoices if str(i.get("Status", "")) == "8"]
    openstaand = sum(
        float(i.get("AmountOutstanding", 0) or 0)
        for i in invoices if str(i.get("Status", "")) not in ("4", "8", "9")
    )
    return {
        "omzet": round(sum(float(i.get("AmountExcl", 0)) for i in this_month), 2),
        "omzet_totaal": round(sum(float(i.get("AmountExcl", 0)) for i in invoices), 2),
        "openstaand": round(openstaand, 2),
        "facturen_maand": len(this_month),
        "facturen_totaal": len(invoices),
        "facturen_betaald": len(paid),
        "facturen_open": len([i for i in invoices if str(i.get("Status", "")) in ("2", "3", "5")]),
        "paid": paid[:5],
        "open": [i for i in invoices if str(i.get("Status", "")) in ("2", "3", "5")][:10],
        "recent": this_month[:10],
        "fetched_at": utc_now()
    }


def fetch_brevo():
    key = os.environ.get("BREVO_API_KEY", "")
    if not key:
        return {"total_contacts": 0, "error": "no_api_key"}
    import urllib.request
    headers = {"api-key": key}
    try:
        req = urllib.request.Request(
            "https://api.brevo.com/v3/contacts?limit=1",
            headers=headers
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            contacts_data = json.loads(r.read())
        req2 = urllib.request.Request(
            "https://api.brevo.com/v3/emailCampaigns?limit=5",
            headers=headers
        )
        with urllib.request.urlopen(req2, timeout=15) as r2:
            campaigns_data = json.loads(r2.read())
        return {
            "total_contacts": contacts_data.get("count", 0),
            "campaigns": len(campaigns_data.get("campaigns", [])),
            "fetched_at": utc_now()
        }
    except Exception as e:
        return {"total_contacts": 0, "error": str(e)}


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    checks = {"api": "ok", "db": "ok", "vps_disk_ok": True}
    try:
        db = get_db()
        db.execute("SELECT 1").fetchone()
        db.close()
    except Exception:
        checks["db"] = "error"
    try:
        r = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
        usage = int(r.stdout.split("\n")[1].split()[4].rstrip("%"))
        checks["disk_usage_pct"] = usage
        checks["vps_disk_ok"] = usage < 90
    except Exception:
        pass
    healthy = all(v == "ok" or v is True for v in checks.values())
    return {
        "ok": True,
        "data": {"status": "healthy" if healthy else "degraded", **checks, "version": API_VERSION},
        "meta": {"generated_at": utc_now(), "version": API_VERSION}
    }


@app.get("/")
@app.get("/dashboard")
def dashboard():
    return {
        "ok": True,
        "data": {"service": "EcoHandel OS API", "version": API_VERSION, "status": "running"},
        "meta": {"generated_at": utc_now(), "version": API_VERSION}
    }


@app.get("/gsc")
def gsc():
    return {"ok": True, "data": json_read("gsc.json", {})}


@app.get("/ga4")
def ga4():
    return {"ok": True, "data": json_read("ga4.json", {})}


@app.get("/shopify")
def shopify():
    return {"ok": True, "data": json_read("shopify.json", {})}


@app.get("/wefact")
def wefact():
    return {"ok": True, "data": json_read("wefact.json", {})}


@app.get("/brevo")
def brevo():
    return {"ok": True, "data": json_read("brevo.json", {})}


@app.get("/ads")
def ads():
    return {"ok": True, "data": json_read("ads.json", {})}


@app.get("/queue")
def queue():
    try:
        db = get_db()
        items = db.execute(
            "SELECT * FROM queue_items ORDER BY total_score DESC LIMIT 50"
        ).fetchall()
        db.close()
        return {"ok": True, "data": [dict(r) for r in items]}
    except Exception as e:
        return JSONResponse({"ok": False, "error": {"code": "DB_ERROR", "message": str(e)}}, status_code=500)


@app.get("/queue/summary")
def queue_summary():
    try:
        db = get_db()
        total = db.execute("SELECT COUNT(*) FROM queue_items").fetchone()[0]
        top5 = db.execute("SELECT COUNT(*) FROM queue_items WHERE lane='top_5_now'").fetchone()[0]
        done = db.execute("SELECT COUNT(*) FROM queue_items WHERE status='done'").fetchone()[0]
        db.close()
        return {"ok": True, "data": {"total": total, "top_5": top5, "done": done}}
    except Exception as e:
        return JSONResponse({"ok": False, "error": {"code": "DB_ERROR", "message": str(e)}}, status_code=500)


@app.get("/workflows")
def workflows():
    try:
        db = get_db()
        wf = db.execute(
            "SELECT * FROM workflows WHERE enabled=1 ORDER BY name"
        ).fetchall()
        db.close()
        return {"ok": True, "data": [dict(r) for r in wf]}
    except Exception as e:
        return JSONResponse({"ok": False, "error": {"code": "DB_ERROR", "message": str(e)}}, status_code=500)


@app.get("/agents/status")
def agents_status():
    return {"ok": True, "data": []}


@app.get("/campaigns/stats")
def campaigns():
    try:
        db = get_db()
        total = db.execute(
            "SELECT COUNT(*) FROM campaign_contacts WHERE tenant_id=?", (DEFAULT_TENANT,)
        ).fetchone()[0]
        sent = db.execute(
            "SELECT COUNT(*) FROM campaign_contacts WHERE tenant_id=? AND status IN ('sent','engaged','replied','hot')",
            (DEFAULT_TENANT,)
        ).fetchone()[0]
        opened = db.execute(
            "SELECT COUNT(*) FROM campaign_contacts WHERE tenant_id=? AND open_count > 0",
            (DEFAULT_TENANT,)
        ).fetchone()[0]
        clicked = db.execute(
            "SELECT COUNT(*) FROM campaign_contacts WHERE tenant_id=? AND click_count > 0",
            (DEFAULT_TENANT,)
        ).fetchone()[0]
        db.close()
        return {"ok": True, "data": {
            "contacts": total,
            "sent": sent,
            "open_rate": round(opened / sent * 100, 1) if sent else 0,
            "click_rate": round(clicked / sent * 100, 1) if sent else 0,
            "opened": opened,
            "clicked": clicked
        }}
    except Exception as e:
        return JSONResponse({"ok": False, "error": {"code": "DB_ERROR", "message": str(e)}}, status_code=500)


@app.get("/activity")
def activity():
    try:
        db = get_db()
        log = db.execute(
            "SELECT * FROM activity_log ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
        db.close()
        return {"ok": True, "data": [dict(r) for r in log]}
    except Exception as e:
        return JSONResponse({"ok": False, "error": {"code": "DB_ERROR", "message": str(e)}}, status_code=500)


@app.post("/refresh")
def refresh_data():
    """Trigger fresh fetch of all data sources. Runs synchronously."""
    results = {}
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for name, fetcher in [
        ("gsc", fetch_gsc),
        ("ga4", fetch_ga4),
        ("shopify", fetch_shopify),
        ("wefact", fetch_wefact),
        ("brevo", fetch_brevo),
    ]:
        try:
            data = fetcher()
            (DATA_DIR / f"{name}.json").write_text(json.dumps(data, indent=2) + "\n")
            results[name] = "ok" if "error" not in data else f"err: {data.get('error','?')}"
        except Exception as e:
            results[name] = str(e)

    results["fetched_at"] = utc_now()
    return {"ok": True, "data": results}
