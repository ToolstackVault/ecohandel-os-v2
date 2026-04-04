-- EcoHandel OS — SQLite Schema v1.0
-- Tenant: eco001 (EcoHandel.nl)
-- Let op: alle tabellen hebben tenant_id voor toekomstige multi-tenant

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

-- Tenants table ( voor nu: alleen eco001)
CREATE TABLE IF NOT EXISTS tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Users (Jean Clawd = agent, Milan + Tom = human admins)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
    email TEXT,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin',
    api_token_hash TEXT,
    is_agent INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(tenant_id, email)
);

-- Queue items (Smart Content Queue)
CREATE TABLE IF NOT EXISTS queue_items (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
    title TEXT NOT NULL,
    slug_candidate TEXT,
    content_type TEXT NOT NULL,
    business_goal TEXT NOT NULL,
    priority_label TEXT NOT NULL,
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
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
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
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
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
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
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
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
    workflow_id TEXT NOT NULL REFERENCES workflows(id),
    status TEXT NOT NULL,
    triggered_by TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    steps_completed INTEGER DEFAULT 0,
    steps_failed INTEGER DEFAULT 0,
    next_actions TEXT DEFAULT '[]',
    health_flags TEXT DEFAULT '[]'
);

-- Campaign contacts (partner leads)
CREATE TABLE IF NOT EXISTS campaign_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
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

-- Campaign events (Brevo webhook events)
CREATE TABLE IF NOT EXISTS campaign_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
    contact_id INTEGER REFERENCES campaign_contacts(id),
    campaign_id TEXT,
    event_type TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    metadata TEXT DEFAULT '{}'
);

-- Publish requests (approval workflow)
CREATE TABLE IF NOT EXISTS publish_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
    queue_item_id TEXT REFERENCES queue_items(id),
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

-- Activity log (audit trail)
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
    actor TEXT NOT NULL,
    actor_type TEXT NOT NULL,
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id TEXT,
    metadata TEXT DEFAULT '{}',
    ip_address TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Learning entries
CREATE TABLE IF NOT EXISTS learning_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL REFERENCES tenants(id),
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
CREATE INDEX IF NOT EXISTS idx_campaign_contacts_tenant ON campaign_contacts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_campaign_contacts_email ON campaign_contacts(email);
CREATE INDEX IF NOT EXISTS idx_campaign_contacts_status ON campaign_contacts(status);
CREATE INDEX IF NOT EXISTS idx_campaign_events_tenant ON campaign_events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_campaign_events_contact ON campaign_events(contact_id);
CREATE INDEX IF NOT EXISTS idx_publish_requests_tenant ON publish_requests(tenant_id);
CREATE INDEX IF NOT EXISTS idx_publish_requests_status ON publish_requests(status);
CREATE INDEX IF NOT EXISTS idx_activity_log_tenant ON activity_log(tenant_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_created ON activity_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_learning_entries_tenant ON learning_entries(tenant_id);
