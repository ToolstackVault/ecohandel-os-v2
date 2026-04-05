from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sqlite3, os
from datetime import datetime, timezone

app = FastAPI(title="EcoHandel OS API")
DATABASE_PATH = "/var/www/html/control.ecohandel.nl/data/ecohandel.db"
DEFAULT_TENANT = "eco001"
API_VERSION = "1.0"

def get_db():
    conn = sqlite3.connect(DATABASE_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/health")
def health():
    try:
        db = get_db()
        rows = db.execute("SELECT id FROM tenants LIMIT 1").fetchall()
        db.close()
        return {"ok": True, "data": {"status": "ok", "database": "ok" if rows else "no_tenant", "version": API_VERSION, "tenant": DEFAULT_TENANT}, "meta": {"tenant_id": DEFAULT_TENANT, "generated_at": datetime.now(timezone.utc).isoformat(), "version": API_VERSION}}
    except Exception as e:
        return JSONResponse({"ok": False, "error": {"code": "DB_ERROR", "message": str(e)}}, status_code=500)

@app.get("/")
@app.get("/dashboard")
def dashboard():
    return {"ok": True, "data": {"service": "EcoHandel OS API", "version": API_VERSION, "status": "running"}, "meta": {"generated_at": datetime.now(timezone.utc).isoformat(), "version": API_VERSION}}

@app.get("/queue")
def queue():
    try:
        db = get_db()
        items = db.execute("SELECT * FROM queue_items ORDER BY total_score DESC LIMIT 50").fetchall()
        db.close()
        return {"ok": True, "data": [dict(r) for r in items]}
    except Exception as e:
        return JSONResponse({"ok": False, "error": {"code": "DB_ERROR", "message": str(e)}}, status_code=500)

@app.get("/workflows")
def workflows():
    try:
        db = get_db()
        wf = db.execute("SELECT * FROM workflows WHERE enabled=1 ORDER BY name").fetchall()
        db.close()
        return {"ok": True, "data": [dict(r) for r in wf]}
    except Exception as e:
        return JSONResponse({"ok": False, "error": {"code": "DB_ERROR", "message": str(e)}}, status_code=500)

@app.get("/agents/status")
def agents_status():
    return {"ok": True, "data": []}

@app.get("/campaigns/stats")
def campaigns():
    return {"ok": True, "data": {"contacts": 0, "sent": 0, "open_rate": 0, "click_rate": 0}}

@app.get("/activity")
def activity():
    try:
        db = get_db()
        log = db.execute("SELECT * FROM activity_log ORDER BY created_at DESC LIMIT 50").fetchall()
        db.close()
        return {"ok": True, "data": [dict(r) for r in log]}
    except Exception as e:
        return JSONResponse({"ok": False, "error": {"code": "DB_ERROR", "message": str(e)}}, status_code=500)
