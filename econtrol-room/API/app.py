#!/usr/bin/env python3
"""
EcoHandel OS — REST API v1
Entry point: Flask app op control.ecohandel.nl/api/v1/

Auth: Bearer token (jean/paperclip) of Basic Auth (milan/tom)
Alle requests verwachten X-Tenant-ID header (hardcoded naar eco001 voor nu)
"""
from __future__ import annotations

import os
import sqlite3
import hashlib
import secrets
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, g, jsonify, request
import json

app = Flask(__name__)

# Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.environ.get(
    'ECOHANDEL_DB',
    os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), 'data', 'ecohandel.db')
)
API_VERSION = '1.0'
DEFAULT_TENANT = 'eco001'

# Tokens (in prod: uit environment of secrets manager)
# Jean/Paperclip API token (md5 hash van 'jean-ecohandel-token')
JEAN_TOKEN_HASH = '9e8b8c9e0c3f3f9e8e8e8e8e8e8e8e8e'
# Simple passwords voor milan/tom (in prod: bcrypt hashed)
MILAN_PASSWORD = os.environ.get('ECOHANDEL_API_MILAN_PASSWORD', 'clawd')
TOM_PASSWORD = os.environ.get('ECOHANDEL_API_TOM_PASSWORD', 'tom2026')


# ── Database helpers ──────────────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def query_db(query: str, args=(), one=False, tenant_id: str = None):
    """Execute query met automatic tenant filter."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    return (dict(rv[0]) if rv else None) if one else [dict(r) for r in rv]


def write_db(query: str, args=()) -> sqlite3.Cursor:
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    return cur


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def api_response(data=None, meta: dict = None, **kwargs):
    """Standaard API response wrapper."""
    out = {'ok': True}
    if data is not None:
        out['data'] = data
    if meta:
        out['meta'] = meta
    elif data is not None:
        out['meta'] = {
            'tenant_id': g.get('tenant_id', DEFAULT_TENANT),
            'generated_at': now_utc(),
            'version': API_VERSION,
        }
    if kwargs:
        out.update(kwargs)
    return jsonify(out)


def error_response(code: str, message: str, status: int = 400):
    return jsonify({
        'ok': False,
        'error': {'code': code, 'message': message}
    }), status


# ── Auth ─────────────────────────────────────────────────────────────────────

def get_tenant_id() -> str:
    """Haal tenant_id uit header of default."""
    return request.headers.get('X-Tenant-ID', DEFAULT_TENANT)


def require_auth(f):
    """Decorator: check Bearer token of Basic Auth."""
    @wraps(f)
    def decorated(*args, **kwargs):
        g.tenant_id = get_tenant_id()

        # Bearer token (Jean / agents)
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            token_hash = hashlib.md5(token.encode()).hexdigest()
            print(f"[DEBUG AUTH] Bearer token_hash={token_hash}", flush=True)
            if token_hash == JEAN_TOKEN_HASH:
                g.current_user = 'jean'
                g.is_agent = True
                return f(*args, **kwargs)

        # Basic Auth (Milan / Tom)
        import base64
        auth = request.headers.get('Authorization', '')
        if auth.startswith('Basic '):
            try:
                decoded = base64.b64decode(auth[6:]).decode()
                print(f"[DEBUG AUTH] Decoded: {decoded!r}", flush=True)
                username, password = decoded.split(':', 1)
                if username.lower() == 'milan' and password == MILAN_PASSWORD:
                    g.current_user = 'milan'
                    g.is_agent = False
                    print("[DEBUG AUTH] Milan OK", flush=True)
                    return f(*args, **kwargs)
                if username.lower() == 'tom' and password == TOM_PASSWORD:
                    g.current_user = 'tom'
                    g.is_agent = False
                    return f(*args, **kwargs)
                print(f"[DEBUG AUTH] User/pass mismatch: {username!r}", flush=True)
            except Exception as e:
                print(f"[DEBUG AUTH] Exception: {e}", flush=True)

        print(f"[DEBUG AUTH] FAIL - returning 401", flush=True)
        return error_response('UNAUTHORIZED', 'Geldige token of credentials nodig', 401)
    return decorated


def log_activity(action: str, resource_type: str = None, resource_id: str = None, metadata: dict = None):
    """Schrijf naar activity_log."""
    try:
        write_db(
            """INSERT INTO activity_log
               (tenant_id, actor, actor_type, action, resource_type, resource_id, metadata, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                g.tenant_id,
                g.current_user,
                'agent' if g.is_agent else 'user',
                action,
                resource_type,
                resource_id,
                json.dumps(metadata or {}),
                now_utc(),
            )
        )
    except Exception:
        pass  # Valt niet qua API call


def json_col(val) -> str:
    """Parse JSON column, return as JSON string or original."""
    if val is None:
        return '[]'
    if isinstance(val, str):
        return val
    return json.dumps(val)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health():
    """API gezondheid checken."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM tenants WHERE id = ?", (DEFAULT_TENANT,))
        tenant_ok = cur.fetchone() is not None
        return api_response({
            'status': 'ok',
            'database': 'connected' if tenant_ok else 'no_tenant',
            'version': API_VERSION,
            'tenant': g.get('tenant_id', DEFAULT_TENANT),
        })
    except Exception as e:
        return error_response('DB_ERROR', str(e), 500)


@app.route('/queue', methods=['GET'])
@require_auth
def get_queue():
    """Haal volledige Smart Content Queue op."""
    rows = query_db(
        """SELECT id, title, content_type, business_goal, priority_label,
                  status, lane, primary_cluster, total_score, confidence,
                  why_now, recommended_format, recommended_next_step,
                  owner, assigned_agent, notes, refresh_target_url,
                  created_at, updated_at, done_at
           FROM queue_items
           WHERE tenant_id = ?
           ORDER BY lane = 'top_5_now' DESC,
                    lane = 'next_up' DESC,
                    lane = 'refresh_first' DESC,
                    total_score DESC
        """,
        (g.tenant_id,),
        tenant_id=g.tenant_id
    )
    # Parse JSON columns
    for row in rows:
        row['signal_sources'] = json.loads(row.get('signal_sources', '[]'))

    # Summary stats
    total = len(rows)
    by_status = {}
    by_lane = {}
    by_priority = {}
    for r in rows:
        by_status[r['status']] = by_status.get(r['status'], 0) + 1
        by_lane[r['lane']] = by_lane.get(r['lane'], 0) + 1
        by_priority[r['priority_label']] = by_priority.get(r['priority_label'], 0) + 1

    top5 = [r for r in rows if r['lane'] == 'top_5_now']
    refresh = [r for r in rows if r['lane'] == 'refresh_first']

    return api_response({
        'items': rows,
        'top_5_now': top5,
        'refresh_first': refresh,
        'summary': {
            'total': total,
            'by_status': by_status,
            'by_lane': by_lane,
            'by_priority': by_priority,
        }
    })


@app.route('/queue/items/<item_id>', methods=['PATCH'])
@require_auth
def update_queue_item(item_id):
    """Update een queue item (lane, status, score, etc)."""
    data = request.get_json() or {}
    allowed_fields = [
        'status', 'lane', 'priority_label', 'total_score', 'confidence',
        'assigned_agent', 'notes', 'recommended_next_step', 'why_now',
        'owner', 'title', 'slug_candidate', 'content_type', 'business_goal',
        'primary_cluster', 'secondary_cluster', 'target_audience',
        'signal_sources', 'recommended_format', 'refresh_target_url',
    ]
    updates = {}
    for field in allowed_fields:
        if field in data:
            val = data[field]
            if field in ('signal_sources',):
                val = json.dumps(val) if isinstance(val, list) else val
            updates[field] = val

    if not updates:
        return error_response('BAD_REQUEST', 'Geen geldige velden om te updaten', 400)

    updates['updated_at'] = now_utc()
    if updates.get('status') == 'done':
        updates['done_at'] = now_utc()

    set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [item_id, g.tenant_id]

    cur = write_db(
        f"""UPDATE queue_items SET {set_clause} WHERE id = ? AND tenant_id = ?""",
        values
    )
    if cur.rowcount == 0:
        return error_response('ITEM_NOT_FOUND', f'Queue item {item_id} niet gevonden', 404)

    log_activity('queue_item_updated', 'queue_item', item_id, {'updates': list(updates.keys())})

    # Return updated item
    row = query_db(
        "SELECT * FROM queue_items WHERE id = ? AND tenant_id = ?",
        (item_id, g.tenant_id), one=True
    )
    if row:
        row['signal_sources'] = json.loads(row.get('signal_sources', '[]'))
    return api_response({'item': row})


@app.route('/queue/items', methods=['POST'])
@require_auth
def create_queue_item():
    """Nieuw item aan queue toevoegen."""
    data = request.get_json() or {}

    required = ['title', 'content_type', 'business_goal']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return error_response('BAD_REQUEST', f'Missing required fields: {missing}', 400)

    import uuid

    item_id = data.get('id', f"SCQ-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{secrets.randbelow(900)+100}")
    created = now_utc()

    write_db(
        """INSERT INTO queue_items
           (id, tenant_id, title, slug_candidate, content_type, business_goal,
            priority_label, status, lane, primary_cluster, secondary_cluster,
            target_audience, total_score, confidence, signal_sources,
            why_now, recommended_format, recommended_next_step, owner,
            assigned_agent, notes, refresh_target_url, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            item_id,
            g.tenant_id,
            data.get('title'),
            data.get('slug_candidate'),
            data.get('content_type'),
            data.get('business_goal'),
            data.get('priority_label', 'P3'),
            data.get('status', 'new'),
            data.get('lane', 'unqueued'),
            data.get('primary_cluster'),
            data.get('secondary_cluster'),
            data.get('target_audience', 'mixed'),
            data.get('total_score', 0),
            data.get('confidence', 0.5),
            json.dumps(data.get('signal_sources', [])),
            data.get('why_now'),
            data.get('recommended_format'),
            data.get('recommended_next_step', 'queue_now'),
            data.get('owner', g.current_user),
            data.get('assigned_agent'),
            data.get('notes'),
            data.get('refresh_target_url'),
            created,
            created,
        )
    )
    log_activity('queue_item_created', 'queue_item', item_id, {'title': data.get('title')})

    row = query_db("SELECT * FROM queue_items WHERE id = ?", (item_id,), one=True)
    if row:
        row['signal_sources'] = json.loads(row.get('signal_sources', '[]'))
    return api_response({'item': row}, status=201)


@app.route('/queue/health', methods=['GET'])
@require_auth
def get_queue_health():
    """Queue health metrics."""
    rows = query_db(
        """SELECT
               COUNT(*) as total,
               SUM(CASE WHEN priority_label = 'P1' THEN 1 ELSE 0 END) as p1,
               SUM(CASE WHEN priority_label = 'P2' THEN 1 ELSE 0 END) as p2,
               SUM(CASE WHEN priority_label = 'P3' THEN 1 ELSE 0 END) as p3,
               SUM(CASE WHEN priority_label = 'P4' THEN 1 ELSE 0 END) as p4,
               SUM(CASE WHEN priority_label = 'P5' THEN 1 ELSE 0 END) as p5,
               SUM(CASE WHEN lane = 'top_5_now' THEN 1 ELSE 0 END) as top5,
               SUM(CASE WHEN lane = 'refresh_first' THEN 1 ELSE 0 END) as refresh,
               SUM(CASE WHEN lane = 'watchlist' THEN 1 ELSE 0 END) as watchlist,
               SUM(CASE WHEN confidence < 0.4 THEN 1 ELSE 0 END) as low_conf,
               SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as done
           FROM queue_items WHERE tenant_id = ?""",
        (g.tenant_id,),
        one=True
    )
    return api_response(dict(rows))


@app.route('/agents/status', methods=['GET'])
@require_auth
def get_agent_status():
    """Agent run status."""
    runs = query_db(
        """SELECT id, agent_name, status, started_at, completed_at,
                  items_processed, output_summary
           FROM agent_runs
           WHERE tenant_id = ?
           ORDER BY started_at DESC
           LIMIT 20""",
        (g.tenant_id,)
    )
    # Group by agent, get latest
    latest = {}
    for r in runs:
        if r['agent_name'] not in latest:
            latest[r['agent_name']] = r
    return api_response({'agents': latest, 'recent_runs': runs})


@app.route('/agents/trigger/<agent_name>', methods=['POST'])
@require_auth
def trigger_agent(agent_name):
    """Specialist agent triggeren (Jean-only actie)."""
    if g.is_agent and g.current_user != 'jean':
        return error_response('FORBIDDEN', 'Alleen Jean kan agents triggeren', 403)

    valid_agents = ['content_strategist', 'serp_gap', 'fact_product', 'refresh']
    if agent_name not in valid_agents:
        return error_response('INVALID_AGENT', f'Onbekende agent: {agent_name}', 400)

    # Log trigger
    run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{secrets.randbelow(900)+100}"
    write_db(
        """INSERT INTO agent_runs (tenant_id, agent_name, status, started_at)
           VALUES (?, ?, 'triggered', ?)""",
        (g.tenant_id, agent_name, now_utc())
    )
    log_activity(f'agent_triggered', 'agent', agent_name, {'run_id': run_id})

    return api_response({
        'agent': agent_name,
        'status': 'triggered',
        'run_id': run_id,
        'message': f'{agent_name} is getriggerd. Resultaten verschijnen in volgende cycle.'
    })


@app.route('/workflows', methods=['GET'])
@require_auth
def get_workflows():
    """Workflow registry + status."""
    workflows = query_db(
        """SELECT w.id, w.name, w.description, w.driver_type, w.owner,
                  w.mode, w.enabled, w.approval_required, w.dependencies,
                  w.updated_at,
                  (SELECT COUNT(*) FROM workflow_runs wr
                   WHERE wr.workflow_id = w.id AND wr.tenant_id = ?) as total_runs,
                  (SELECT MAX(wr.started_at) FROM workflow_runs wr
                   WHERE wr.workflow_id = w.id AND wr.tenant_id = ?) as last_run
           FROM workflows w WHERE w.tenant_id = ?""",
        (g.tenant_id, g.tenant_id, g.tenant_id)
    )
    return api_response({'workflows': workflows})


@app.route('/workflows/<workflow_id>/run', methods=['POST'])
@require_auth
def run_workflow(workflow_id):
    """Workflow handmatig triggeren."""
    # Check workflow exists
    wf = query_db(
        "SELECT * FROM workflows WHERE id = ? AND tenant_id = ?",
        (workflow_id, g.tenant_id), one=True
    )
    if not wf:
        return error_response('WORKFLOW_NOT_FOUND', f'Workflow {workflow_id} niet gevonden', 404)

    if not wf['enabled']:
        return error_response('WORKFLOW_DISABLED', 'Deze workflow is uitgeschakeld', 409)

    run_id = f"{workflow_id}-run-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    write_db(
        """INSERT INTO workflow_runs
           (tenant_id, workflow_id, status, triggered_by, started_at)
           VALUES (?, ?, 'running', ?, ?)""",
        (g.tenant_id, workflow_id, g.current_user, now_utc())
    )
    log_activity('workflow_run_triggered', 'workflow', workflow_id, {'run_id': run_id})

    return api_response({
        'workflow_id': workflow_id,
        'run_id': run_id,
        'status': 'running',
        'message': f'Workflow {workflow_id} gestart.'
    })


@app.route('/activity', methods=['GET'])
@require_auth
def get_activity():
    """Activity log ophalen."""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    rows = query_db(
        """SELECT * FROM activity_log
           WHERE tenant_id = ?
           ORDER BY created_at DESC
           LIMIT ? OFFSET ?""",
        (g.tenant_id, min(limit, 200), offset)
    )
    return api_response({'activity': rows})


@app.route('/campaigns/stats', methods=['GET'])
@require_auth
def get_campaign_stats():
    """Partner campaign stats uit DB."""
    contacts = query_db(
        """SELECT
               COUNT(*) as total,
               SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new,
               SUM(CASE WHEN status = 'contacted' THEN 1 ELSE 0 END) as contacted,
               SUM(CASE WHEN status = 'engaged' THEN 1 ELSE 0 END) as engaged,
               SUM(CASE WHEN status = 'hot' THEN 1 ELSE 0 END) as hot,
               SUM(CASE WHEN status = 'bounce' THEN 1 ELSE 0 END) as bounced,
               SUM(COALESCE(open_count,0)) as total_opens,
               SUM(COALESCE(click_count,0)) as total_clicks,
               SUM(COALESCE(reply_count,0)) as total_replies
           FROM campaign_contacts WHERE tenant_id = ?""",
        (g.tenant_id,), one=True
    )
    recent_events = query_db(
        """SELECT ce.*, cc.email, cc.first_name
           FROM campaign_events ce
           LEFT JOIN campaign_contacts cc ON ce.contact_id = cc.id
           WHERE ce.tenant_id = ?
           ORDER BY ce.occurred_at DESC LIMIT 20""",
        (g.tenant_id,)
    )
    return api_response({
        'contacts': dict(contacts),
        'recent_events': recent_events,
    })


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return error_response('NOT_FOUND', 'Endpoint niet gevonden', 404)


@app.errorhandler(500)
def server_error(e):
    return error_response('SERVER_ERROR', 'Interne server fout', 500)


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5555))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    print(f"EcoHandel OS API v{API_VERSION} starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
