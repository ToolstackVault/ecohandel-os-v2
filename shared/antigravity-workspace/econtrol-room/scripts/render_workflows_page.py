#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
from html import escape

from render_ui import BASE, BUILD_DIR, load_json, shell_page, utc_now_label, write_text

STATE_DIR = BASE / 'state'
OUTPUT_PATH = BUILD_DIR / 'agents.html'
ALIAS_OUTPUT_PATH = BUILD_DIR / 'workflows.html'

REGISTRY_PATH = STATE_DIR / 'workflow-registry.json'
RUNS_PATH = STATE_DIR / 'workflow-runs.json'
CONTROLS_PATH = STATE_DIR / 'workflow-controls.json'
DEPENDENCIES_PATH = STATE_DIR / 'workflow-dependencies.json'
ALERTS_PATH = STATE_DIR / 'workflow-alerts.json'
RECOMMENDATIONS_PATH = STATE_DIR / 'workflow-recommendations.json'
ACTIONS_PATH = STATE_DIR / 'workflow-actions.json'
HEALTH_PATH = STATE_DIR / 'workflow-health.json'
OPS_STATUS_PATH = STATE_DIR / 'ops-status.json'

LANE_LABELS = {
    'ingest': 'Ingest',
    'interpret': 'Interpret',
    'decide': 'Decide',
    'execute': 'Execute',
    'review_learn': 'Review & Learn',
}


def compact(text: str | None, limit: int = 120) -> str:
    text = (text or '-').replace('\n', ' ').strip()
    return text if len(text) <= limit else text[: limit - 1] + '…'


def render_registry_card(item: dict) -> str:
    return f'''<article class="workflow-card">
      <div class="workflow-top"><div class="workflow-meta"><span class="pill pill-accent">{escape(LANE_LABELS.get(item.get('lane', '-'), item.get('lane', '-')))}</span><span class="pill {'pill-live' if item.get('status') in {'success','ok','ready','active'} else 'pill-warn' if item.get('status') in {'warning','blocked','partial'} else 'pill-soft'}">{escape(item.get('status', 'pending'))}</span></div><span class="pill pill-soft">{escape(item.get('driver_type', '-'))}</span></div>
      <h3>{escape(item.get('name', 'Untitled'))}</h3>
      <p>{escape(item.get('description', ''))}</p>
      <div class="workflow-foot">
        <div><span class="mini-label">Mode</span><strong>{escape(item.get('mode', '-'))}</strong></div>
        <div><span class="mini-label">Owner</span><strong>{escape(item.get('owner', '-'))}</strong></div>
        <div><span class="mini-label">Dependencies</span><strong>{escape(compact(', '.join(item.get('dependencies', [])), 60))}</strong></div>
        <div><span class="mini-label">Outputs</span><strong>{escape(compact(', '.join(item.get('outputs', [])), 60))}</strong></div>
      </div>
    </article>'''


def render_run_card(item: dict) -> str:
    return f'''<article class="meta-card">
      <div class="meta-top"><span class="pill pill-accent">{escape(item.get('trigger_type', '-'))}</span><span class="pill {'pill-live' if item.get('status') in {'success','ok','active'} else 'pill-warn' if item.get('status') in {'warning','blocked','failed'} else 'pill-soft'}">{escape(item.get('status', '-'))}</span></div>
      <h3>{escape(item.get('name', '-'))}</h3>
      <p>{escape(compact(item.get('last_output'), 120))}</p>
      <div class="meta-foot"><div><span class="mini-label">Last run</span><strong>{escape(item.get('last_run') or '-')}</strong></div></div>
    </article>'''


def render_control_card(item: dict) -> str:
    return f'''<article class="meta-card">
      <div class="meta-top"><span class="pill pill-accent">{escape(item.get('workflow_id', '-'))}</span><span class="pill {'pill-warn' if item.get('approval_required') else 'pill-live'}">{'approval' if item.get('approval_required') else 'direct'}</span></div>
      <h3>{escape(item.get('mode', '-'))}</h3>
      <p>Live mode: {escape(item.get('live_mode', '-'))}</p>
      <div class="meta-foot"><div><span class="mini-label">Enabled</span><strong>{'yes' if item.get('enabled') else 'no'}</strong></div></div>
    </article>'''


def render_dependency_card(item: dict) -> str:
    return f'''<article class="meta-card">
      <div class="meta-top"><span class="pill pill-accent">dependency</span><span class="pill {'pill-live' if item.get('status') in {'ok','ready','active'} else 'pill-warn' if item.get('status') in {'warning','blocked','stale'} else 'pill-soft'}">{escape(item.get('status', '-'))}</span></div>
      <h3>{escape(item.get('name', '-'))}</h3>
      <p>Used by: {escape(compact(', '.join(item.get('used_by', [])), 80))}</p>
      <div class="meta-foot"><div><span class="mini-label">Freshness</span><strong>{escape(str(item.get('freshness_hours', '—')))}h</strong></div><div><span class="mini-label">Fallback</span><strong>{'yes' if item.get('fallback') else 'no'}</strong></div></div>
    </article>'''


def health_card(label: str, value: str, note: str) -> str:
    return f'''<article class="health-card"><span class="health-label">{escape(label)}</span><strong class="health-value">{escape(value)}</strong><div class="health-note">{escape(note)}</div></article>'''


def main() -> None:
    registry = load_json(REGISTRY_PATH).get('items', [])
    runs = load_json(RUNS_PATH).get('items', [])
    controls = load_json(CONTROLS_PATH).get('items', [])
    dependencies = load_json(DEPENDENCIES_PATH).get('items', [])
    alerts = load_json(ALERTS_PATH).get('items', [])
    recommendations = load_json(RECOMMENDATIONS_PATH).get('items', [])
    actions = load_json(ACTIONS_PATH).get('items', [])
    health = load_json(HEALTH_PATH)
    ops = load_json(OPS_STATUS_PATH)

    lane_counts = Counter(item.get('lane', 'unknown') for item in registry)
    active_count = sum(1 for item in registry if item.get('enabled'))
    blocked_count = sum(1 for item in registry if item.get('status') == 'blocked')
    approval_count = sum(1 for item in controls if item.get('approval_required'))

    registry_cards = ''.join(render_registry_card(item) for item in registry) or '<p class="empty">Nog geen workflows.</p>'
    run_cards = ''.join(render_run_card(item) for item in runs) or '<p class="empty">Nog geen runs.</p>'
    control_cards = ''.join(render_control_card(item) for item in controls) or '<p class="empty">Nog geen controls.</p>'
    dependency_cards = ''.join(render_dependency_card(item) for item in dependencies) or '<p class="empty">Nog geen dependencies.</p>'
    health_cards = ''.join([
        health_card('Active', str(active_count), 'Workflows live'),
        health_card('Blocked', str(blocked_count), 'Vraagt aandacht'),
        health_card('Approvals', str(approval_count), 'Menselijke gates'),
        health_card('Overall', str(health.get('overall_status', 'unknown')), 'Machine gezondheid'),
    ])
    alerts_list = ''.join(f"<li><strong>{escape(item.get('type', 'alert'))}</strong><div class='sub'>{escape(item.get('message', ''))}</div></li>" for item in alerts) or '<li>Geen alerts.</li>'
    recommendation_list = ''.join(f"<li><strong>{escape(item.get('title', '-'))}</strong><div class='sub'>{escape(item.get('recommended_action', ''))}</div></li>" for item in recommendations) or '<li>Geen aanbevelingen.</li>'
    action_cards = ''.join(f'''<article class="action-card"><div class="action-top"><span class="pill pill-accent">{escape(item.get('workflow_id', '-'))}</span><span class="pill {'pill-live' if item.get('safe_to_rerun') else 'pill-warn'}">{'safe rerun' if item.get('safe_to_rerun') else 'guarded'}</span></div><h3>{escape(item.get('label', '-'))}</h3><p>{escape(item.get('notes', ''))}</p><div class="cmd-box">{escape(item.get('run_command', ''))}</div></article>''' for item in actions[:6]) or '<p class="empty">Nog geen acties.</p>'

    content = f'''
      <section class="hero-card">
        <div class="eyebrow">Workflows</div>
        <h1>Workflows</h1>
        <div class="subhead">De operationele laag van de machine: scripts, crons, controls, dependencies en reruns. Niet als technisch dumpveld, maar als overzicht van wat draait, blokkeert en actie vraagt.</div>
        <div class="health-grid">{health_cards}</div>
        <div class="hero-note">Built {utc_now_label()} · Ops mode {escape(ops.get('mode', '-'))} · lane spread volgt hieronder.</div>
      </section>
      <div class="grid">
        <section class="panel span-12"><div class="panel-head"><div><div class="eyebrow">Registry</div><h2>Workflow registry</h2></div><span class="status {'status-live' if health.get('overall_status') == 'healthy' else 'status-seed'}">{escape(health.get('overall_status', 'unknown'))}</span></div><div class="workflow-grid">{registry_cards}</div></section>
        <section class="panel span-7"><div class="panel-head"><div><div class="eyebrow">Runs</div><h2>Live run monitor</h2></div></div><div class="meta-grid">{run_cards}</div></section>
        <section class="panel span-5"><div class="panel-head"><div><div class="eyebrow">Actions</div><h2>Run & retry</h2></div></div><div class="action-grid">{action_cards}</div></section>
        <section class="panel span-12"><div class="panel-head"><div><div class="eyebrow">Controls</div><h2>Controls & gates</h2></div></div><div class="meta-grid meta-grid-tight">{control_cards}</div></section>
        <section class="panel span-7"><div class="panel-head"><div><div class="eyebrow">Dependencies</div><h2>Dependencies & data sources</h2></div></div><div class="meta-grid">{dependency_cards}</div></section>
        <section class="panel span-5"><div class="panel-head"><div><div class="eyebrow">Alerts</div><h2>Alerts & opportunities</h2></div></div><ul class="stack">{alerts_list}{recommendation_list}</ul><div class="sub" style="margin-top:12px">Ops mode: {escape(ops.get('mode', '-'))} · Lane spread: Ingest {lane_counts.get('ingest', 0)} · Interpret {lane_counts.get('interpret', 0)} · Decide {lane_counts.get('decide', 0)} · Execute {lane_counts.get('execute', 0)} · Review {lane_counts.get('review_learn', 0)}</div></section>
      </div>
    '''

    extra_css = '''
    .health-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:18px}
    .health-card{padding:16px;border-radius:18px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06)}
    .health-label{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}
    .health-value{display:block;margin-top:8px;font-size:26px;letter-spacing:-.04em;color:var(--cyan);overflow-wrap:anywhere}
    .health-note{margin-top:6px;color:var(--muted);font-size:13px;line-height:1.5}
    .hero-note{margin-top:14px;color:var(--muted);font-size:13px;line-height:1.6}
    .workflow-grid,.action-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
    .meta-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
    .meta-grid-tight{grid-template-columns:repeat(3,minmax(0,1fr))}
    .workflow-card,.action-card,.meta-card{padding:16px;border-radius:18px;background:linear-gradient(180deg,rgba(7,19,31,.8),rgba(10,24,40,.95));border:1px solid rgba(255,255,255,.07);min-width:0}
    .workflow-top,.action-top,.meta-top{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
    .workflow-meta{display:flex;gap:8px;flex-wrap:wrap}
    .workflow-card h3,.action-card h3,.meta-card h3{margin:12px 0 8px;font-size:20px;letter-spacing:-.03em;overflow-wrap:anywhere}
    .workflow-card p,.action-card p,.meta-card p{margin:0;color:var(--muted);line-height:1.6;overflow-wrap:anywhere}
    .workflow-foot,.meta-foot{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:14px;padding-top:12px;border-top:1px solid rgba(255,255,255,.06)}
    .cmd-box{margin-top:12px;padding:10px 12px;border-radius:12px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.06);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;line-height:1.5;word-break:break-word}
    @media (max-width:1180px){.health-grid,.workflow-grid,.action-grid,.meta-grid,.meta-grid-tight,.workflow-foot,.meta-foot{grid-template-columns:1fr}}
    '''

    html = shell_page(
        title='EcoHandel.nl — Workflows',
        page_title='Workflows',
        page_subtitle='Scripts, runs, controls en dependencies',
        description='Workflows cockpit voor EcoHandel.nl',
        active='workflows',
        content=content,
        extra_css=extra_css,
    )
    write_text(OUTPUT_PATH, html)
    write_text(ALIAS_OUTPUT_PATH, html)
    print(f'Wrote {OUTPUT_PATH}')
    print(f'Wrote {ALIAS_OUTPUT_PATH}')


if __name__ == '__main__':
    main()
