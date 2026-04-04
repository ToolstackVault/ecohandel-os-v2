-- Seed data voor EcoHandel OS (eco001)
-- Wordt gedraaid bij eerste setup en bij reset

-- Tenant
INSERT OR IGNORE INTO tenants (id, name) VALUES ('eco001', 'EcoHandel.nl');

-- Users
INSERT OR IGNORE INTO users (tenant_id, email, name, role, is_agent) VALUES
    ('eco001', 'jean@ecohandel.nl', 'Jean Clawd', 'admin', 1),
    ('eco001', 'milan@ecohandel.nl', 'Milan', 'admin', 0),
    ('eco001', 'tom@ecohandel.nl', 'Tom', 'admin', 0);

-- Default workflows (gekopieerd van huidige state)
INSERT OR IGNORE INTO workflows (id, tenant_id, name, description, driver_type, owner, mode, enabled, approval_required, dependencies) VALUES
    ('ops_cycle', 'eco001', 'Ops Cycle Orchestration', 'Orkestreert de volledige deterministic Econtrol Room run.', 'script', 'ops_agent', 'auto', 1, 0, '["source_refresh","queue_scoring","state_update","dashboard_render","queue_render","workflow_state_build","workflow_render","specialist_trigger_generation","deploy_sync"]'),
    ('partner_daily', 'eco001', 'Partner Campaign Daily Cycle', 'Draait dagelijkse partner campaign cyclus: stats ophalen, scoring, mail versturen.', 'script', 'ops_agent', 'auto', 1, 0, '["fetch_brevo_stats","run_daily_cycle","render_partner_campaign_page"]'),
    ('content_refresh', 'eco001', 'Content Refresh Scan', 'Scan bestaande content op refresh-kansen (CTR, schema, links).', 'script', 'ops_agent', 'auto', 1, 0, '["refresh_sources","score_refresh_queue","render_queue_page"]'),
    ('daily_briefing', 'eco001', 'Daily Briefing', 'Genereert dagelijkse briefing voor Milan/Tom.', 'script', 'ops_agent', 'auto', 1, 0, '["gather_data","render_briefing","send_notification"]'),
    ('gsc_sync', 'eco001', 'GSC Data Sync', 'Haalt Search Console data op en verwerkt signals.', 'script', 'ops_agent', 'auto', 1, 0, '["gsc_fetch","process_queries","update_source_signals"]');
