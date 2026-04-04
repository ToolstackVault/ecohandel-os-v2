-- EcoHandel OS — SQLite Schema v1.0
-- Only CREATE TABLE statements — safe to run on existing VPS DB
-- Uses IF NOT EXISTS so existing tables are preserved

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

-- Tenants table
CREATE TABLE IF NOT EXISTS tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- api_users (voor Flask API auth — gescheiden van PHP app users)
CREATE TABLE IF NOT EXISTS api_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL DEFAULT 'eco001',
    email TEXT,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin',
    api_token_hash TEXT,
    is_agent INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(tenant_id, email)
);

-- Insert API users
INSERT OR IGNORE INTO api_users (tenant_id, email, name, role, is_agent) VALUES
    ('eco001', 'jean@ecohandel.nl', 'Jean Clawd', 'admin', 1),
    ('eco001', 'milan@ecohandel.nl', 'Milan', 'admin', 0),
    ('eco001', 'tom@ecohandel.nl', 'Tom', 'admin', 0);

-- Queue items (Smart Content Queue)
CREATE TABLE IF NOT EXISTS queue_items (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL DEFAULT 'eco001',
    title TEXT NOT NULL,
    slug_candidate TEXT,
    content_type TEXT NOT NULL,
    business_goal TEXT NOT NULL,
    priority_label TEXT NOT NULL DEFAULT 'P3',
    status TEXT NOT NULL DEFAULT 'new',
    lane TEXT NOT NULL DEFAULT 'unqueued',
    primary_cluster TEXT,
    secondary_cluster TEXT,
    target_audience TEXT DEFAULT 'mixed',
    total_score INTEGER DEFAULT 0,
    confidence REAL DEFAULT 0.5,
    signal_sources TEXT DEFAULT '[]',
    why_now TEXT,
    recommended_format TEXT,
    recommended_next_step TEXT,
    owner TEXT DEFAULT 'jean',
    assigned_agent TEXT,
    notes TEXT,
    refresh_target_url TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    done_at TEXT
);

-- Queue health snapshots
CREATE TABLE IF NOT EXISTS queue_health (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL DEFAULT 'eco001',
    generated_at TEXT NOT NULL,
    total_items INTEGER DEFAULT 0,
    p1_count INTEGER DEFAULT 0,
    p2_count INTEGER DEFAULT 0,
    p3_count INTEGER DEFAULT 0,
    p4_count INTEGER DEFAULT 0,
    p5_count INTEGER DEFAULT 0,
    lane_counts TEXT DEFAULT '{}',
    low_confidence_count INTEGER DEFAULT 0,
    stale_count INTEGER DEFAULT 0,
    health_flags TEXT DEFAULT '[]'
);

-- Agent runs
CREATE TABLE IF NOT EXISTS agent_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL DEFAULT 'eco001',
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    items_processed INTEGER DEFAULT 0,
    errors TEXT DEFAULT '[]',
    output_summary TEXT
);

-- Workflow registry (definitie)
CREATE TABLE IF NOT EXISTS workflows (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL DEFAULT 'eco001',
    name TEXT NOT NULL,
    description TEXT,
    driver_type TEXT NOT NULL,
    owner TEXT NOT NULL,
    mode TEXT NOT NULL DEFAULT 'auto',
    enabled INTEGER NOT NULL DEFAULT 1,
    approval_required INTEGER NOT NULL DEFAULT 0,
    dependencies TEXT DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Workflow runs
CREATE TABLE IF NOT EXISTS workflow_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL DEFAULT 'eco001',
    workflow_id TEXT NOT NULL,
    status TEXT NOT NULL,
    triggered_by TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    steps_completed INTEGER DEFAULT 0,
    steps_failed INTEGER DEFAULT 0,
    next_actions TEXT DEFAULT '[]',
    health_flags TEXT DEFAULT '[]'
);

-- Activity log (audit trail)
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL DEFAULT 'eco001',
    actor TEXT NOT NULL,
    actor_type TEXT NOT NULL,
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id TEXT,
    metadata TEXT DEFAULT '{}',
    ip_address TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Campaign events (Brevo webhook events)
CREATE TABLE IF NOT EXISTS campaign_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL DEFAULT 'eco001',
    contact_id INTEGER,
    campaign_id TEXT,
    event_type TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    metadata TEXT DEFAULT '{}'
);

-- Campaign contacts (partner leads)
CREATE TABLE IF NOT EXISTS campaign_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL DEFAULT 'eco001',
    email TEXT NOT NULL,
    first_name TEXT,
    company_name TEXT,
    status TEXT DEFAULT 'new',
    source TEXT,
    brevo_contact_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_contacted_at TEXT,
    engagement_score INTEGER DEFAULT 0,
    open_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    bounce_count INTEGER DEFAULT 0,
    unsub_count INTEGER DEFAULT 0
);

-- Publish requests (approval workflow)
CREATE TABLE IF NOT EXISTS publish_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL DEFAULT 'eco001',
    queue_item_id TEXT,
    content_type TEXT,
    content_payload TEXT,
    title TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    requested_by TEXT NOT NULL,
    approved_by TEXT,
    rejected_by TEXT,
    published_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Learning entries
CREATE TABLE IF NOT EXISTS learning_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL DEFAULT 'eco001',
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    trigger TEXT,
    applied_to TEXT,
    evidence TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    resolved_at TEXT
);

-- Indexes voor performance
CREATE INDEX IF NOT EXISTS idx_queue_items_tenant ON queue_items(tenant_id);
CREATE INDEX IF NOT EXISTS idx_queue_items_status ON queue_items(status);
CREATE INDEX IF NOT EXISTS idx_queue_items_lane ON queue_items(lane);
CREATE INDEX IF NOT EXISTS idx_queue_items_priority ON queue_items(priority_label);
CREATE INDEX IF NOT EXISTS idx_queue_items_score ON queue_items(total_score DESC);
CREATE INDEX IF NOT EXISTS idx_agent_runs_tenant ON agent_runs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_agent_runs_name ON agent_runs(agent_name);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_tenant ON workflow_runs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_workflow_runs_workflow ON workflow_runs(workflow_id);
CREATE INDEX IF NOT EXISTS idx_publish_requests_tenant ON publish_requests(tenant_id);
CREATE INDEX IF NOT EXISTS idx_publish_requests_status ON publish_requests(status);
CREATE INDEX IF NOT EXISTS idx_learning_entries_tenant ON learning_entries(tenant_id);

-- Tenants table ( voor nu: alleen eco001)
INSERT OR IGNORE INTO tenants (id, name) VALUES ('eco001', 'EcoHandel.nl');

-- Default workflows (only insert if not exists)
INSERT OR IGNORE INTO workflows (id, tenant_id, name, description, driver_type, owner, mode, enabled, approval_required, dependencies) VALUES
    ('ops_cycle', 'eco001', 'Ops Cycle Orchestration', 'Orkestreert de volledige deterministic Econtrol Room run.', 'script', 'ops_agent', 'auto', 1, 0, '["source_refresh","queue_scoring","state_update","dashboard_render","queue_render","workflow_state_build","workflow_render","specialist_trigger_generation","deploy_sync"]'),
    ('partner_daily', 'eco001', 'Partner Campaign Daily Cycle', 'Draait dagelijkse partner campaign cyclus: stats ophalen, scoring, mail versturen.', 'script', 'ops_agent', 'auto', 1, 0, '["fetch_brevo_stats","run_daily_cycle","render_partner_campaign_page"]'),
    ('content_refresh', 'eco001', 'Content Refresh Scan', 'Scan bestaande content op refresh-kansen (CTR, schema, links).', 'script', 'ops_agent', 'auto', 1, 0, '["refresh_sources","score_refresh_queue","render_queue_page"]'),
    ('daily_briefing', 'eco001', 'Daily Briefing', 'Genereert dagelijkse briefing voor Milan/Tom.', 'script', 'ops_agent', 'auto', 1, 0, '["gather_data","render_briefing","send_notification"]'),
    ('gsc_sync', 'eco001', 'GSC Data Sync', 'Haalt Search Console data op en verwerkt signals.', 'script', 'ops_agent', 'auto', 1, 0, '["gsc_fetch","process_queries","update_source_signals"]');

-- Additional indexes for new tables
CREATE INDEX IF NOT EXISTS idx_activity_log_tenant ON activity_log(tenant_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_created ON activity_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_campaign_contacts_tenant ON campaign_contacts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_campaign_contacts_email ON campaign_contacts(email);
CREATE INDEX IF NOT EXISTS idx_campaign_contacts_status ON campaign_contacts(status);
CREATE INDEX IF NOT EXISTS idx_campaign_events_tenant ON campaign_events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_campaign_events_contact ON campaign_events(contact_id);
