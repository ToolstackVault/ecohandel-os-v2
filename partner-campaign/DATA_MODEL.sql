PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS leads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  company_name TEXT NOT NULL,
  province TEXT,
  website TEXT,
  phone TEXT,
  email TEXT,
  contact_person TEXT,
  role TEXT,
  battery_experience TEXT,
  deye_knowledge TEXT,
  warmth TEXT,
  source TEXT,
  notes TEXT,
  source_date TEXT,
  segment TEXT DEFAULT 'installer',
  status TEXT DEFAULT 'new',
  assigned_owner TEXT DEFAULT 'Jean',
  do_not_contact INTEGER DEFAULT 0,
  unsubscribed INTEGER DEFAULT 0,
  bounced INTEGER DEFAULT 0,
  replied INTEGER DEFAULT 0,
  lead_score REAL DEFAULT 0,
  hot_score REAL DEFAULT 0,
  last_activity_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(email, website)
);

CREATE TABLE IF NOT EXISTS campaigns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  brevo_campaign_id TEXT,
  name TEXT NOT NULL,
  campaign_type TEXT DEFAULT 'partner-outreach',
  subject_line TEXT,
  sender_name TEXT,
  sender_email TEXT,
  status TEXT DEFAULT 'draft',
  list_name TEXT,
  segment_name TEXT,
  cta_primary TEXT,
  cta_secondary TEXT,
  price_list_url TEXT,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lead_campaigns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lead_id INTEGER NOT NULL,
  campaign_id INTEGER NOT NULL,
  brevo_contact_id TEXT,
  send_status TEXT DEFAULT 'queued',
  sent_at TEXT,
  first_open_at TEXT,
  last_open_at TEXT,
  open_count INTEGER DEFAULT 0,
  unique_open_count INTEGER DEFAULT 0,
  click_count INTEGER DEFAULT 0,
  unique_click_count INTEGER DEFAULT 0,
  reply_count INTEGER DEFAULT 0,
  unsubscribe_count INTEGER DEFAULT 0,
  bounce_count INTEGER DEFAULT 0,
  last_event_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE,
  FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
  UNIQUE(lead_id, campaign_id)
);

CREATE TABLE IF NOT EXISTS tracked_links (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  campaign_id INTEGER,
  link_key TEXT NOT NULL UNIQUE,
  link_type TEXT NOT NULL,
  label TEXT NOT NULL,
  destination_url TEXT NOT NULL,
  tracking_url TEXT,
  product_handle TEXT,
  collection_handle TEXT,
  active INTEGER DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_type TEXT NOT NULL,
  brevo_event_id TEXT,
  lead_id INTEGER,
  campaign_id INTEGER,
  lead_campaign_id INTEGER,
  tracked_link_id INTEGER,
  email TEXT,
  event_ts TEXT NOT NULL,
  raw_payload TEXT NOT NULL,
  meta_json TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE SET NULL,
  FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL,
  FOREIGN KEY (lead_campaign_id) REFERENCES lead_campaigns(id) ON DELETE SET NULL,
  FOREIGN KEY (tracked_link_id) REFERENCES tracked_links(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS replies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lead_id INTEGER NOT NULL,
  campaign_id INTEGER,
  channel TEXT DEFAULT 'email',
  direction TEXT DEFAULT 'inbound',
  subject TEXT,
  message_preview TEXT,
  received_at TEXT NOT NULL,
  classification TEXT DEFAULT 'unreviewed',
  sentiment TEXT,
  urgency TEXT,
  action_recommendation TEXT,
  raw_source TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE,
  FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS daily_reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  report_date TEXT NOT NULL UNIQUE,
  hot_count INTEGER DEFAULT 0,
  replied_count INTEGER DEFAULT 0,
  opened_count INTEGER DEFAULT 0,
  clicked_count INTEGER DEFAULT 0,
  unsubscribed_count INTEGER DEFAULT 0,
  bounced_count INTEGER DEFAULT 0,
  report_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_events_type_ts ON events(event_type, event_ts);
CREATE INDEX IF NOT EXISTS idx_lead_campaigns_campaign ON lead_campaigns(campaign_id);
CREATE INDEX IF NOT EXISTS idx_lead_campaigns_lead ON lead_campaigns(lead_id);
