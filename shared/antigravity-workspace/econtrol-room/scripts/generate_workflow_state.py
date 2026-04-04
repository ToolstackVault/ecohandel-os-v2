#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
STATE_DIR = BASE / 'state'
SCRIPTS_DIR = BASE / 'scripts'

OPS_STATUS_PATH = STATE_DIR / 'ops-status.json'
CRON_STATUS_PATH = STATE_DIR / 'cron-status.json'
DEPLOY_STATUS_PATH = STATE_DIR / 'deploy-status.json'
PUBLISH_STATUS_PATH = STATE_DIR / 'publish-status.json'
AGENT_STATUS_PATH = STATE_DIR / 'agent-status.json'
SOURCE_SIGNALS_PATH = STATE_DIR / 'source-signals.json'
QUEUE_HEALTH_PATH = STATE_DIR / 'queue-health.json'
SOURCE_MIX_PATH = STATE_DIR / 'source-mix.json'
LEARNING_PATH = STATE_DIR / 'learning-summary.json'
SPECIALIST_TRIGGERS_PATH = STATE_DIR / 'specialist-triggers.json'
SMART_QUEUE_PATH = BASE / 'queue' / 'SMART_CONTENT_QUEUE.json'
REFRESH_QUEUE_PATH = BASE / 'queue' / 'REFRESH_QUEUE.json'

WORKFLOW_REGISTRY_PATH = STATE_DIR / 'workflow-registry.json'
WORKFLOW_RUNS_PATH = STATE_DIR / 'workflow-runs.json'
WORKFLOW_CONTROLS_PATH = STATE_DIR / 'workflow-controls.json'
WORKFLOW_DEPENDENCIES_PATH = STATE_DIR / 'workflow-dependencies.json'
WORKFLOW_ALERTS_PATH = STATE_DIR / 'workflow-alerts.json'
WORKFLOW_RECOMMENDATIONS_PATH = STATE_DIR / 'workflow-recommendations.json'
WORKFLOW_HEALTH_PATH = STATE_DIR / 'workflow-health.json'
WORKFLOW_ACTIONS_PATH = STATE_DIR / 'workflow-actions.json'


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def load_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def parse_iso(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except Exception:
        return None


def age_hours(value: str | None):
    dt = parse_iso(value)
    if not dt:
        return None
    return round((datetime.now(timezone.utc) - dt).total_seconds() / 3600, 1)


def normalize_step_status(step_name: str, ops_status: dict, deploy_status: dict, publish_status: dict) -> tuple[str, str | None, str | None]:
    logs = {log.get('step'): log for log in ops_status.get('step_logs', [])}
    log = logs.get(step_name, {})
    if step_name == 'deploy_live' and deploy_status.get('status') == 'dry_run':
        return 'dry_run', None, deploy_status.get('notes')
    if step_name == 'publish_execute' and publish_status:
        return publish_status.get('status', 'idle'), None, publish_status.get('notes')
    if log:
        return ('success' if log.get('ok') else 'failed'), None, (log.get('stderr') or log.get('stdout') or None)
    return 'pending', None, None


def build_registry(ops_status: dict, cron_status: dict, deploy_status: dict, publish_status: dict) -> list[dict]:
    common_owner = 'ops_agent'
    workflows = [
        {
            'id': 'ops_cycle',
            'name': 'Ops Cycle Orchestration',
            'lane': 'review_learn',
            'description': 'Orkestreert de volledige deterministic Econtrol Room run.',
            'driver_type': 'script',
            'owner': common_owner,
            'mode': 'auto',
            'enabled': True,
            'approval_required': False,
            'status': ops_status.get('ops_status', 'unknown'),
            'last_run': ops_status.get('last_run'),
            'next_run': None,
            'dependencies': ['source_refresh', 'queue_scoring', 'state_update', 'dashboard_render', 'queue_render', 'workflow_state_build', 'workflow_render', 'specialist_trigger_generation', 'deploy_sync'],
            'outputs': ['state/ops-status.json'],
            'last_error': None,
            'notes': 'Hoofdorkestratie voor de machine.',
        },
        {
            'id': 'source_refresh',
            'name': 'Source Refresh',
            'lane': 'ingest',
            'description': 'Haalt source signals en snapshotdata binnen of ververst bestaande brondata.',
            'driver_type': 'script',
            'owner': common_owner,
            'mode': 'auto',
            'enabled': True,
            'approval_required': False,
            'status': 'success' if cron_status.get('source_refresh_ready') else 'pending',
            'last_run': ops_status.get('last_run'),
            'next_run': None,
            'dependencies': ['gsc', 'ads', 'shopify', 'ga4', 'manual_inputs', 'business_rules'],
            'outputs': ['state/source-signals.json'],
            'last_error': None,
            'notes': 'Script-first ingestlaag.',
        },
        {
            'id': 'queue_scoring',
            'name': 'Queue Scoring',
            'lane': 'decide',
            'description': 'Zet signalen om naar Top 5, Next Up, Refresh en Watchlist.',
            'driver_type': 'script',
            'owner': common_owner,
            'mode': 'auto',
            'enabled': True,
            'approval_required': False,
            'status': 'success' if cron_status.get('queue_scoring_ready') else 'pending',
            'last_run': ops_status.get('last_run'),
            'next_run': None,
            'dependencies': ['source_refresh'],
            'outputs': ['queue/SMART_CONTENT_QUEUE.json', 'queue/REFRESH_QUEUE.json'],
            'last_error': None,
            'notes': 'Revenue-first scoringmotor.',
        },
        {
            'id': 'state_update',
            'name': 'State Update',
            'lane': 'interpret',
            'description': 'Berekt queue health, source mix, cron readiness en learning summary.',
            'driver_type': 'script',
            'owner': common_owner,
            'mode': 'auto',
            'enabled': True,
            'approval_required': False,
            'status': 'success' if cron_status.get('state_update_ready') else 'pending',
            'last_run': ops_status.get('last_run'),
            'next_run': None,
            'dependencies': ['queue_scoring'],
            'outputs': ['state/queue-health.json', 'state/source-mix.json', 'state/learning-summary.json', 'state/cron-status.json'],
            'last_error': None,
            'notes': 'Gezondheids- en operating metrics.',
        },
        {
            'id': 'dashboard_render',
            'name': 'Dashboard Render',
            'lane': 'execute',
            'description': 'Bouwt de homepage van Econtrol Room.',
            'driver_type': 'script',
            'owner': common_owner,
            'mode': 'auto',
            'enabled': True,
            'approval_required': False,
            'status': 'success' if cron_status.get('render_ready') else 'pending',
            'last_run': ops_status.get('last_run'),
            'next_run': None,
            'dependencies': ['state_update'],
            'outputs': ['build/index.html'],
            'last_error': None,
            'notes': 'Hoofddashboard render.',
        },
        {
            'id': 'queue_render',
            'name': 'Queue Page Render',
            'lane': 'execute',
            'description': 'Bouwt de Smart Content Queue pagina.',
            'driver_type': 'script',
            'owner': common_owner,
            'mode': 'auto',
            'enabled': True,
            'approval_required': False,
            'status': 'success' if cron_status.get('queue_page_ready') else 'pending',
            'last_run': ops_status.get('last_run'),
            'next_run': None,
            'dependencies': ['queue_scoring'],
            'outputs': ['build/smart-content-queue.html'],
            'last_error': None,
            'notes': 'Queue-specific outputlaag.',
        },
        {
            'id': 'workflow_state_build',
            'name': 'Workflow State Build',
            'lane': 'interpret',
            'description': 'Combineert bestaande states tot workflow-registry, runs, alerts en recommendations.',
            'driver_type': 'script',
            'owner': common_owner,
            'mode': 'auto',
            'enabled': True,
            'approval_required': False,
            'status': 'success' if cron_status.get('workflow_state_ready') else 'pending',
            'last_run': ops_status.get('last_run'),
            'next_run': None,
            'dependencies': ['state_update', 'specialist_trigger_generation'],
            'outputs': ['state/workflow-registry.json', 'state/workflow-runs.json', 'state/workflow-alerts.json'],
            'last_error': None,
            'notes': 'Nieuwe aggregatielaag voor workflowcockpit.',
        },
        {
            'id': 'workflow_render',
            'name': 'Workflows Page Render',
            'lane': 'execute',
            'description': 'Bouwt de nieuwe Workflows cockpitpagina op /agents.html.',
            'driver_type': 'script',
            'owner': common_owner,
            'mode': 'auto',
            'enabled': True,
            'approval_required': False,
            'status': 'success' if cron_status.get('workflows_page_ready') else 'pending',
            'last_run': ops_status.get('last_run'),
            'next_run': None,
            'dependencies': ['workflow_state_build'],
            'outputs': ['build/agents.html'],
            'last_error': None,
            'notes': 'Behoudt voorlopig /agents.html als URL maar toont Workflows.',
        },
        {
            'id': 'partner_campaign_render',
            'name': 'Partner Campaign Page Render',
            'lane': 'execute',
            'description': 'Bouwt de partner outreach cockpitpagina voor leads, hot prospects en campaign readiness.',
            'driver_type': 'script',
            'owner': common_owner,
            'mode': 'auto',
            'enabled': True,
            'approval_required': False,
            'status': 'success' if cron_status.get('partner_campaign_page_ready') else 'pending',
            'last_run': ops_status.get('last_run'),
            'next_run': None,
            'dependencies': ['content_system'],
            'outputs': ['build/partner-campaign.html'],
            'last_error': None,
            'notes': 'Nieuwe cockpit voor Brevo outreach, leadstatus en hot prospect handoff.',
        },
        {
            'id': 'specialist_trigger_generation',
            'name': 'Specialist Trigger Generation',
            'lane': 'decide',
            'description': 'Genereert triggeradviezen voor specialist-agents.',
            'driver_type': 'script',
            'owner': common_owner,
            'mode': 'hybrid',
            'enabled': True,
            'approval_required': False,
            'status': 'success' if cron_status.get('trigger_logic_ready') else 'pending',
            'last_run': ops_status.get('last_run'),
            'next_run': None,
            'dependencies': ['queue_scoring'],
            'outputs': ['state/specialist-triggers.json'],
            'last_error': None,
            'notes': 'Trigger-only; voert niets autonoom uit.',
        },
        {
            'id': 'deploy_sync',
            'name': 'Deploy Sync',
            'lane': 'execute',
            'description': 'Schrijft deploy status terug en blijft nu bewust in dry-run.',
            'driver_type': 'script',
            'owner': common_owner,
            'mode': 'manual',
            'enabled': True,
            'approval_required': True,
            'status': deploy_status.get('status', 'pending'),
            'last_run': deploy_status.get('updated_at') or ops_status.get('last_run'),
            'next_run': None,
            'dependencies': ['dashboard_render', 'queue_render', 'workflow_render'],
            'outputs': ['state/deploy-status.json'],
            'last_error': None,
            'notes': deploy_status.get('notes', 'Deploy control state.'),
        },
        {
            'id': 'publish_readiness',
            'name': 'Publish Readiness',
            'lane': 'review_learn',
            'description': 'Controleert of publish-flow technisch klaarstaat.',
            'driver_type': 'script',
            'owner': common_owner,
            'mode': 'hybrid',
            'enabled': cron_status.get('publish_wrapper_ready', False),
            'approval_required': True,
            'status': 'ready' if cron_status.get('publish_wrapper_ready') else 'pending',
            'last_run': publish_status.get('updated_at'),
            'next_run': None,
            'dependencies': ['publish_execute', 'content_system'],
            'outputs': ['state/publish-status.json'],
            'last_error': None,
            'notes': 'Wrapper staat klaar, linked aan de EcoHandel content system playbook/template stack.',
        },
        {
            'id': 'publish_execute',
            'name': 'Publish Execute',
            'lane': 'execute',
            'description': 'Gecontroleerde Shopify publish subflow voor EcoHandel.',
            'driver_type': 'script',
            'owner': common_owner,
            'mode': 'manual',
            'enabled': True,
            'approval_required': True,
            'status': publish_status.get('status', 'idle'),
            'last_run': publish_status.get('updated_at'),
            'next_run': None,
            'dependencies': ['publish_readiness'],
            'outputs': ['state/publish-status.json'],
            'last_error': None,
            'notes': publish_status.get('notes', 'Shopify publish wrapper.'),
        },
        {
            'id': 'finance_sync',
            'name': 'Finance Sync (Wefact)',
            'lane': 'ingest',
            'description': 'Toekomstige read-only finance truth layer voor facturen, offertes en omzetvalidatie.',
            'driver_type': 'script',
            'owner': common_owner,
            'mode': 'manual',
            'enabled': False,
            'approval_required': True,
            'status': 'blocked',
            'last_run': None,
            'next_run': None,
            'dependencies': ['wefact'],
            'outputs': ['state/finance-status.json'],
            'last_error': 'Wefact whitelist ontbreekt nog voor IP 84.85.55.133.',
            'notes': 'Business-critical volgende laag voor omzetwaarheid.',
        },
        {
            'id': 'cron_health',
            'name': 'Cron Health Check',
            'lane': 'review_learn',
            'description': 'Meet script- en cron-readiness van de machine.',
            'driver_type': 'state',
            'owner': common_owner,
            'mode': 'auto',
            'enabled': True,
            'approval_required': False,
            'status': 'success' if cron_status.get('ops_cycle_ready') else 'warning',
            'last_run': cron_status.get('updated_at'),
            'next_run': None,
            'dependencies': [],
            'outputs': ['state/cron-status.json'],
            'last_error': None,
            'notes': cron_status.get('notes', 'Cron readiness status.'),
        },
    ]
    return workflows


def build_controls(registry: list[dict]) -> dict:
    items = []
    for wf in registry:
        items.append({
            'workflow_id': wf['id'],
            'enabled': wf['enabled'],
            'mode': wf['mode'],
            'approval_required': wf['approval_required'],
            'driver_type': wf['driver_type'],
            'live_mode': 'dry_run' if wf['id'] == 'deploy_sync' else ('gated_live' if wf['id'] == 'publish_execute' else 'safe'),
            'retry_allowed': wf['id'] not in {'finance_sync'},
            'escalation_target': 'jean',
        })
    return {'updated_at': utc_now(), 'items': items}


def build_dependencies(source_signals: dict, cron_status: dict) -> dict:
    snapshots = source_signals.get('snapshots', {})
    items = [
        {
            'id': 'gsc',
            'name': 'Google Search Console',
            'status': 'ready' if snapshots.get('gsc_fetched_at') else 'partial',
            'freshness_hours': age_hours(snapshots.get('gsc_fetched_at')),
            'used_by': ['source_refresh', 'queue_scoring'],
            'fallback': True,
        },
        {
            'id': 'ads',
            'name': 'Google Ads',
            'status': 'ready' if snapshots.get('ads_fetched_at') else 'partial',
            'freshness_hours': age_hours(snapshots.get('ads_fetched_at')),
            'used_by': ['source_refresh', 'queue_scoring'],
            'fallback': True,
        },
        {
            'id': 'ga4',
            'name': 'GA4',
            'status': 'ready' if snapshots.get('ga4_fetched_at') else 'partial',
            'freshness_hours': age_hours(snapshots.get('ga4_fetched_at')),
            'used_by': ['source_refresh'],
            'fallback': True,
        },
        {
            'id': 'shopify',
            'name': 'Shopify Snapshots',
            'status': 'ready' if snapshots.get('shopify_fetched_at') else 'partial',
            'freshness_hours': age_hours(snapshots.get('shopify_fetched_at')),
            'used_by': ['source_refresh', 'queue_scoring', 'publish_execute'],
            'fallback': True,
        },
        {
            'id': 'wefact',
            'name': 'Wefact',
            'status': 'blocked',
            'freshness_hours': None,
            'used_by': ['finance_sync'],
            'fallback': False,
        },
        {
            'id': 'manual_inputs',
            'name': 'Manual Topics & Business Rules',
            'status': 'ready',
            'freshness_hours': None,
            'used_by': ['source_refresh', 'queue_scoring'],
            'fallback': False,
        },
        {
            'id': 'business_rules',
            'name': 'Business Rules',
            'status': 'ready',
            'freshness_hours': None,
            'used_by': ['source_refresh', 'queue_scoring'],
            'fallback': False,
        },
        {
            'id': 'render_stack',
            'name': 'Render Stack',
            'status': 'ready' if cron_status.get('render_ready') and cron_status.get('queue_page_ready') else 'partial',
            'freshness_hours': None,
            'used_by': ['dashboard_render', 'queue_render', 'workflow_render'],
            'fallback': False,
        },
        {
            'id': 'content_system',
            'name': 'EcoHandel Content System',
            'status': 'ready' if cron_status.get('publish_system_ready') else 'partial',
            'freshness_hours': None,
            'used_by': ['publish_readiness', 'publish_execute'],
            'fallback': False,
        },
        {
            'id': 'partner_campaign_system',
            'name': 'Partner Campaign System',
            'status': 'ready' if (Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign/data/partner_campaign.db')).exists() else 'partial',
            'freshness_hours': None,
            'used_by': ['partner_campaign_render'],
            'fallback': False,
        },
    ]
    return {'updated_at': utc_now(), 'items': items}


def build_runs(registry: list[dict], ops_status: dict, deploy_status: dict, publish_status: dict) -> dict:
    step_logs = {log.get('step'): log for log in ops_status.get('step_logs', [])}
    mapping = {
        'source_refresh': 'refresh_sources',
        'queue_scoring': 'score_queue',
        'state_update': 'update_state',
        'dashboard_render': 'render_dashboard',
        'queue_render': 'render_queue_page',
        'workflow_state_build': 'generate_workflow_state',
        'workflow_render': 'render_workflows_page',
        'partner_campaign_render': 'render_partner_campaign_page',
        'specialist_trigger_generation': 'trigger_specialists',
        'deploy_sync': 'deploy_live',
    }
    runs = []
    for wf in registry:
        step_name = mapping.get(wf['id'])
        step_log = step_logs.get(step_name, {})
        status = wf.get('status', 'pending')
        if wf['id'] == 'publish_execute':
            status = publish_status.get('status', 'idle')
        elif wf['id'] == 'deploy_sync' and deploy_status.get('status') == 'dry_run':
            status = 'dry_run'
        runs.append({
            'workflow_id': wf['id'],
            'name': wf['name'],
            'status': status,
            'trigger_type': 'cron' if wf['mode'] == 'auto' else 'manual',
            'last_run': wf.get('last_run'),
            'duration_ms': None,
            'last_output': step_log.get('stdout') or step_log.get('stderr') or wf.get('notes'),
            'last_error': wf.get('last_error') or step_log.get('stderr'),
        })
    return {'updated_at': utc_now(), 'items': runs}


def build_alerts(queue_health: dict, cron_status: dict, deploy_status: dict, registry: list[dict], specialist_triggers: dict) -> dict:
    alerts = []
    for warning in queue_health.get('warnings', []):
        alerts.append({'severity': 'warning', 'type': 'queue_health', 'message': warning})
    if deploy_status.get('status') == 'dry_run':
        alerts.append({'severity': 'info', 'type': 'deploy', 'message': 'Deploy staat bewust nog op dry-run.'})
    if not cron_status.get('workflow_state_ready'):
        alerts.append({'severity': 'warning', 'type': 'workflow', 'message': 'Workflow state laag is nog niet volledig gekoppeld.'})
    if specialist_triggers.get('count', 0) > 10:
        alerts.append({'severity': 'info', 'type': 'specialists', 'message': f"{specialist_triggers.get('count', 0)} specialist triggers klaar voor review."})
    blocked = [wf for wf in registry if wf.get('status') == 'blocked']
    for wf in blocked:
        alerts.append({'severity': 'warning', 'type': 'blocked_workflow', 'message': f"{wf['name']} is geblokkeerd: {wf.get('last_error') or wf.get('notes')}"})
    return {'updated_at': utc_now(), 'items': alerts}


def build_recommendations(queue_health: dict, alerts: dict, specialist_triggers: dict, source_mix: dict, cron_status: dict) -> dict:
    items = []
    if any('Ads value is 0' in alert['message'] for alert in alerts.get('items', [])):
        items.append({'priority': 'high', 'title': 'Purchase value sanity check', 'recommended_action': 'Vergelijk Ads conversion value direct met Shopify omzet en GA4 revenue.'})
    if any('Wefact' in alert['message'] for alert in alerts.get('items', [])):
        items.append({'priority': 'high', 'title': 'Wefact truth layer activeren', 'recommended_action': 'Whitelist IP 84.85.55.133 en koppel read-only finance sync.'})
    if specialist_triggers.get('count', 0) > 0:
        items.append({'priority': 'medium', 'title': 'Specialist review backlog', 'recommended_action': f"Review {specialist_triggers.get('count', 0)} triggeradviezen en bepaal welke echt waarde toevoegen."})
    if queue_health.get('low_confidence_count', 0) > 3:
        items.append({'priority': 'medium', 'title': 'Low-confidence topics aanscherpen', 'recommended_action': 'Laat strategist/fact-product alleen los op high-impact kandidaten met matige confidence.'})
    if source_mix.get('sources', {}).get('manual_milan', 0) > source_mix.get('sources', {}).get('gsc', 0):
        items.append({'priority': 'medium', 'title': 'Bronmix verbreden', 'recommended_action': 'Maak live bronpulls belangrijker zodat de queue minder leunt op handmatige input.'})
    if not cron_status.get('publish_system_ready'):
        items.append({'priority': 'high', 'title': 'EcoHandel content system koppelen', 'recommended_action': 'Zorg dat playbook, template en publish script op vaste plek staan en gekoppeld zijn aan Econtrol Room.'})
    if not items:
        items.append({'priority': 'low', 'title': 'Machine stabiel houden', 'recommended_action': 'Geen kritieke aanbevelingen; focus op polish en control layer.'})
    return {'updated_at': utc_now(), 'items': items}


def build_actions(registry: list[dict]) -> dict:
    items = []
    actionable = {
        'source_refresh',
        'queue_scoring',
        'state_update',
        'dashboard_render',
        'queue_render',
        'workflow_state_build',
        'workflow_render',
        'partner_campaign_render',
        'specialist_trigger_generation',
        'deploy_sync',
    }
    for wf in registry:
        workflow_id = wf['id']
        if workflow_id not in actionable:
            continue
        items.append({
            'workflow_id': workflow_id,
            'label': wf['name'],
            'run_command': f"python3 ecohandel/econtrol-room/scripts/run_workflow.py {workflow_id}",
            'retry_command': f"python3 ecohandel/econtrol-room/scripts/run_workflow.py {workflow_id}",
            'safe_to_rerun': workflow_id != 'deploy_sync',
            'notes': 'Use from workspace root. Deploy remains guarded; other listed actions are safe reruns.'
        })
    items.append({
        'workflow_id': 'refresh_stack',
        'label': 'Refresh Stack',
        'run_command': 'python3 ecohandel/econtrol-room/scripts/run_workflow.py refresh_stack',
        'retry_command': 'python3 ecohandel/econtrol-room/scripts/run_workflow.py refresh_stack',
        'safe_to_rerun': True,
        'notes': 'Refresh + score + state update.'
    })
    items.append({
        'workflow_id': 'render_stack',
        'label': 'Render Stack',
        'run_command': 'python3 ecohandel/econtrol-room/scripts/run_workflow.py render_stack',
        'retry_command': 'python3 ecohandel/econtrol-room/scripts/run_workflow.py render_stack',
        'safe_to_rerun': True,
        'notes': 'Dashboard + queue + workflows render.'
    })
    items.append({
        'workflow_id': 'retry_failed',
        'label': 'Retry Failed Workflows',
        'run_command': 'python3 ecohandel/econtrol-room/scripts/retry_failed_workflows.py',
        'retry_command': 'python3 ecohandel/econtrol-room/scripts/retry_failed_workflows.py',
        'safe_to_rerun': True,
        'notes': 'Retries the most recent failed mapped steps from ops-status.json.'
    })
    items.append({
        'workflow_id': 'publish_docs',
        'label': 'Open EcoHandel Publish Playbook',
        'run_command': 'cat ecohandel/content-system/kennisblog/PUBLISH_PLAYBOOK.md',
        'retry_command': 'cat ecohandel/content-system/kennisblog/PUBLISH_PLAYBOOK.md',
        'safe_to_rerun': True,
        'notes': 'Source of truth for markdown -> HTML -> preview-first knowledge publishing.'
    })
    return {'updated_at': utc_now(), 'items': items}


def build_health(registry: list[dict], alerts: dict, dependencies: dict, runs: dict) -> dict:
    status_counter = Counter(item.get('status', 'unknown') for item in registry)
    dep_counter = Counter(item.get('status', 'unknown') for item in dependencies.get('items', []))
    run_counter = Counter(item.get('status', 'unknown') for item in runs.get('items', []))
    overall = 'healthy'
    if status_counter.get('blocked', 0) or dep_counter.get('blocked', 0):
        overall = 'warning'
    if any(item.get('severity') == 'warning' for item in alerts.get('items', [])):
        overall = 'warning'
    return {
        'updated_at': utc_now(),
        'overall_status': overall,
        'workflow_counts': dict(status_counter),
        'dependency_counts': dict(dep_counter),
        'run_counts': dict(run_counter),
        'alerts_count': len(alerts.get('items', [])),
    }


def main() -> None:
    ops_status = load_json(OPS_STATUS_PATH)
    cron_status = load_json(CRON_STATUS_PATH)
    deploy_status = load_json(DEPLOY_STATUS_PATH)
    publish_status = load_json(PUBLISH_STATUS_PATH)
    agent_status = load_json(AGENT_STATUS_PATH)
    source_signals = load_json(SOURCE_SIGNALS_PATH)
    queue_health = load_json(QUEUE_HEALTH_PATH)
    source_mix = load_json(SOURCE_MIX_PATH)
    learning = load_json(LEARNING_PATH)
    specialist_triggers = load_json(SPECIALIST_TRIGGERS_PATH)
    _ = agent_status, learning  # kept loaded for future extension

    registry = build_registry(ops_status, cron_status, deploy_status, publish_status)
    controls = build_controls(registry)
    dependencies = build_dependencies(source_signals, cron_status)
    runs = build_runs(registry, ops_status, deploy_status, publish_status)
    alerts = build_alerts(queue_health, cron_status, deploy_status, registry, specialist_triggers)
    recommendations = build_recommendations(queue_health, alerts, specialist_triggers, source_mix, cron_status)
    actions = build_actions(registry)
    health = build_health(registry, alerts, dependencies, runs)

    write_json(WORKFLOW_REGISTRY_PATH, {'updated_at': utc_now(), 'items': registry})
    write_json(WORKFLOW_CONTROLS_PATH, controls)
    write_json(WORKFLOW_DEPENDENCIES_PATH, dependencies)
    write_json(WORKFLOW_RUNS_PATH, runs)
    write_json(WORKFLOW_ALERTS_PATH, alerts)
    write_json(WORKFLOW_RECOMMENDATIONS_PATH, recommendations)
    write_json(WORKFLOW_ACTIONS_PATH, actions)
    write_json(WORKFLOW_HEALTH_PATH, health)

    print(f'Wrote {WORKFLOW_REGISTRY_PATH}')
    print(f'Wrote {WORKFLOW_CONTROLS_PATH}')
    print(f'Wrote {WORKFLOW_DEPENDENCIES_PATH}')
    print(f'Wrote {WORKFLOW_RUNS_PATH}')
    print(f'Wrote {WORKFLOW_ALERTS_PATH}')
    print(f'Wrote {WORKFLOW_RECOMMENDATIONS_PATH}')
    print(f'Wrote {WORKFLOW_ACTIONS_PATH}')
    print(f'Wrote {WORKFLOW_HEALTH_PATH}')


if __name__ == '__main__':
    main()
