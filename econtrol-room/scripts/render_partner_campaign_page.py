#!/usr/bin/env python3
"""Render the Partner Campaign page for Econtrol Room.

Uses the shared shell/CSS from rebuild_all_pages.py for consistent sizing.
Reads: state/partner-campaign-live.json
Writes: build/partner-campaign.html
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
STATE_PATH = BASE / 'state' / 'partner-campaign-live.json'
OUTPUT_PATH = BASE / 'build' / 'partner-campaign.html'

# Import shared shell from rebuild_all_pages
import importlib.util, sys
spec = importlib.util.spec_from_file_location('rebuild', str(BASE / 'scripts' / 'rebuild_all_pages.py'))
_reb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_reb)
shell = _reb.shell
esc = _reb.esc
fmt_num = _reb.fmt_num
fmt_pct = _reb.fmt_pct
fmt_dt = _reb.fmt_dt


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {}
    return json.loads(STATE_PATH.read_text(encoding='utf-8'))


def action_pill(hot_score: float, status: str) -> tuple[str, str]:
    if status == 'replied':
        return 'BEL VANDAAG', 'pill-w'
    if hot_score >= 60:
        return 'HOT — OPVOLGEN', 'pill-g'
    if hot_score >= 25:
        return 'WARM — MONITOREN', 'pill-c'
    if hot_score > 0:
        return 'ENGAGED', 'pill-c'
    return 'GEEN ENGAGEMENT', 'pill-s'


def pill_class(priority: str) -> str:
    return {'high': 'pill-w', 'medium': 'pill-c', 'info': 'pill-s'}.get(priority, 'pill-s')


def render_kpi_cards(kpi: dict, db: dict, brevo: dict) -> str:
    def card(label, val, note='', css='sc-c'):
        return f'<div class="sc {css}"><span class="sl">{esc(label)}</span><span class="sv">{esc(val)}</span><span class="sn">{esc(note)}</span></div>'

    tx = brevo.get('transactional_kpi', {}) or {}
    use_tx_fallback = not kpi.get('total_delivered') and bool(tx.get('delivered'))
    open_rate = tx.get('open_rate', 0) if use_tx_fallback else kpi.get('open_rate', 0)
    click_rate = tx.get('click_rate', 0) if use_tx_fallback else kpi.get('click_rate', 0)
    delivered = tx.get('delivered', 0) if use_tx_fallback else kpi.get('total_delivered', 0)
    opens = tx.get('opened', 0) if use_tx_fallback else kpi.get('total_opens', 0)
    clicks = tx.get('clicks', 0) if use_tx_fallback else kpi.get('total_clicks', 0)
    send_note = 'Tx fallback actief' if use_tx_fallback else 'Campagne stats'

    unsubs = tx.get('unsubs', 0) if use_tx_fallback else kpi.get('total_unsubscribed', 0)
    bounces = tx.get('hard_bounces', 0) if use_tx_fallback else kpi.get('total_bounced', 0)

    cards = [
        card('Campagnes', fmt_num(kpi.get('total_campaigns', 0)), 'Echte campagnes na testfilter', 'sc-c'),
        card('Delivered', fmt_num(delivered), send_note, 'sc-c'),
        card('Open rate', fmt_pct(open_rate), f'{fmt_num(opens)} unique opens', 'sc-g' if open_rate >= 20 else 'sc-c'),
        card('Click rate', fmt_pct(click_rate), f'{fmt_num(clicks)} clicks', 'sc-g' if click_rate >= 3 else 'sc-c'),
        card('Leads totaal', fmt_num(db.get('total_leads', 0)), f'{fmt_num(db.get("leads_with_email", 0))} met email', 'sc-c'),
        card('Echte leads gebruikt', fmt_num(db.get('used_real_leads', 0)), 'Unieke leads zonder tests/interne ruis', 'sc-g'),
        card('Contacteerbaar', fmt_num(db.get('contactable', 0)), 'Niet bounced/unsubscribed', 'sc-g'),
        card('Brevo subs', fmt_num(brevo.get('total_subscribers', 0)), f'{len(brevo.get("lists", []))} lijsten', 'sc-c'),
        card('Credits', fmt_num(brevo.get('credits_remaining', 0)), brevo.get('plan', ''), 'sc-w' if isinstance(brevo.get('credits_remaining'), (int, float)) and brevo.get('credits_remaining', 999) < 100 else 'sc-c'),
    ]
    cards.append(f'<div class="sc sc-c"><span class="sl">Deliverability</span><span class="sv">Monitor</span><div class="stat-badges"><span class="pill {"pill-live" if clicks > 0 else "pill-soft"}">Clicks {fmt_num(clicks)}</span><span class="pill {"pill-warn" if unsubs > 0 else "pill-live"}">Unsubs {fmt_num(unsubs)}</span><span class="pill {"pill-warn" if bounces > 0 else "pill-live"}">Bounces {fmt_num(bounces)}</span></div><span class="sn">Snelle deliverability-check</span></div>')
    return '<div class="sg">' + '\n'.join(cards) + '</div>'


def render_campaign_table(campaigns: list) -> str:
    if not campaigns:
        return '<p class="muted">Nog geen campagnes verstuurd. Start met een testlijst.</p>'
    rows = []
    for c in campaigns[:10]:
        s = c.get('stats', {}) if isinstance(c.get('stats'), dict) else {}
        sent = s.get('sent', 0)
        delivered = s.get('delivered', 0)
        opens = s.get('opens', 0)
        clicks = s.get('clicks', 0)
        or_pct = round(opens / delivered * 100, 1) if delivered else 0
        cr_pct = round(clicks / delivered * 100, 1) if delivered else 0
        subject = c.get('subject', c.get('subject_line', '—'))
        rows.append(f'<tr><td data-label="Naam">{esc(c.get("name","—"))}</td><td data-label="Subject">{esc(subject or "—")}</td><td data-label="Status"><span class="pill pill-{"g" if c.get("status")=="sent" else "s"}">{esc(c.get("status","—"))}</span></td><td data-label="Sent">{fmt_num(sent)}</td><td data-label="Open%">{fmt_pct(or_pct)}</td><td data-label="Click%">{fmt_pct(cr_pct)}</td></tr>')
    return f'<div class="tw mobile-cards"><table><thead><tr><th>Naam</th><th>Subject</th><th>Status</th><th>Sent</th><th>Open%</th><th>Click%</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def render_hot_prospects(prospects: list) -> str:
    if not prospects:
        return '<p class="muted">Nog geen hot prospects.</p>'

    def is_real_prospect(p: dict) -> bool:
        blob = ' '.join(str(p.get(k, '') or '') for k in ('company_name', 'contact_person', 'email')).lower()
        bad_tokens = ['jean test', 'jean cta', 'example.com', 'test@test', 'test bv', 'example']
        return not any(token in blob for token in bad_tokens)

    def action_rank(p: dict) -> int:
        status = (p.get('status') or '').lower()
        hs = p.get('hot_score') or 0
        if status == 'replied':
            return 5
        if hs >= 60:
            return 4
        if hs >= 25:
            return 3
        if hs > 0:
            return 2
        return 1

    def action_reason(p: dict) -> str:
        status = (p.get('status') or '').lower()
        hs = p.get('hot_score') or 0
        if status == 'replied':
            return 'Reply binnen — direct opvolgen'
        if hs >= 60:
            return 'Sterke engagement — bel of mail vandaag'
        if hs >= 25:
            return 'Warm genoeg voor actieve monitoring'
        if hs > 0:
            return 'Engagement gezien — nog niet heet'
        return 'Nog geen interactie'

    filtered = [p for p in prospects if is_real_prospect(p)]
    engaged = [p for p in filtered if (p.get('hot_score') or 0) > 0 or (p.get('status') or '').lower() == 'replied']
    waiting = [p for p in filtered if p not in engaged]

    if not engaged:
        html = '<div class="note" style="margin-bottom:14px"><strong>⏳ Wachten op eerste campagne</strong><p class="sub" style="margin-top:6px">Ranking hieronder is op lead fit. Na eerste send wordt gerankt op engagement: opens → clicks → prijslijst → replies.</p></div>'
        rows = ''.join(f'<tr><td data-label="Bedrijf"><strong>{esc(p.get("company_name","—"))}</strong></td><td data-label="Contact">{esc(p.get("contact_person") or p.get("email") or "—")}</td><td data-label="Fit">{fmt_num(p.get("lead_score",0))}</td><td data-label="Warmte">{esc(p.get("warmth") or "—")}</td><td data-label="Status"><span class="pill pill-s">WACHT</span></td></tr>' for p in sorted(waiting, key=lambda x: -(x.get('lead_score') or 0))[:10])
        html += f'<div class="tw mobile-cards"><table><thead><tr><th>Bedrijf</th><th>Contact</th><th>Fit</th><th>Warmte</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div>'
        return html

    engaged.sort(key=lambda p: (-action_rank(p), -(p.get('hot_score') or 0), -(p.get('lead_score') or 0)))
    rows = ''
    for p in engaged[:10]:
        hs = p.get('hot_score') or 0
        label, cls = action_pill(hs, p.get('status', ''))
        rows += f'<tr><td data-label="Bedrijf"><strong>{esc(p.get("company_name","—"))}</strong><div class="sub">{esc(action_reason(p))}</div></td><td data-label="Contact">{esc(p.get("contact_person") or p.get("email") or "—")}</td><td data-label="Engagement">🔥 {fmt_num(hs)}</td><td data-label="Fit">{fmt_num(p.get("lead_score",0))}</td><td data-label="Actie"><span class="pill {cls}">{label}</span></td></tr>'
    return f'<div class="tw mobile-cards"><table><thead><tr><th>Bedrijf</th><th>Contact</th><th>Engagement</th><th>Fit</th><th>Actie</th></tr></thead><tbody>{rows}</tbody></table></div>'


def render_recommendations(recs: list) -> str:
    if not recs:
        return '<p class="muted">Geen aanbevelingen. Data volgt na eerste campagne.</p>'
    rows = ''.join(f'<tr><td data-label="Prio"><span class="pill {pill_class(r.get("priority","info"))}">{esc(r.get("priority","info"))}</span></td><td data-label="Inzicht"><strong>{esc(r.get("title",""))}</strong><div class="sub">{esc(r.get("detail",""))}</div></td></tr>' for r in recs)
    return f'<div class="tw mobile-cards"><table><thead><tr><th>Prio</th><th>Inzicht</th></tr></thead><tbody>{rows}</tbody></table></div>'


def render_ai_cards(recs: list) -> str:
    if not recs:
        return '<div class="note"><strong>Geen aanbevelingen</strong><div class="sub" style="margin-top:6px">Na meer campagne-data verschijnen hier concrete partneracties.</div></div>'
    cards = []
    for r in recs[:4]:
        cards.append(
            f'''<div class="list-card">
  <strong>{esc(r.get("title", "Aanbeveling"))}</strong>
  <div class="meta"><span class="pill {pill_class(r.get("priority", "info"))}">{esc(r.get("priority", "info"))}</span></div>
  <div class="desc">{esc(r.get("recommended_action") or r.get("detail") or '')}</div>
</div>'''
        )
    return '<div class="card-grid">' + ''.join(cards) + '</div>'


def render_lists(lists_data: list) -> str:
    if not lists_data:
        return '<p class="muted">Geen Brevo lijsten.</p>'
    rows = ''.join(f'<tr><td data-label="Lijst">{esc(l.get("name","—"))}</td><td data-label="Subscribers">{l.get("totalSubscribers",0)}</td></tr>' for l in lists_data)
    return f'<div class="tw mobile-cards"><table><thead><tr><th>Lijst</th><th>Subscribers</th></tr></thead><tbody>{rows}</tbody></table></div>'


def render_status_dist(dist: dict) -> str:
    if not dist:
        return '<p class="muted">Geen data</p>'
    rows = ''.join(f'<tr><td data-label="Status">{esc(k)}</td><td data-label="Aantal"><strong>{v}</strong></td></tr>' for k, v in sorted(dist.items(), key=lambda x: -x[1]))
    return f'<div class="tw mobile-cards"><table><thead><tr><th>Status</th><th>Aantal</th></tr></thead><tbody>{rows}</tbody></table></div>'


def render_warmth_dist(dist: dict) -> str:
    if not dist:
        return '<p class="muted">Geen data</p>'
    known = {'WARM', 'MIDDEL-WARM', 'WARM-MIDDEL', 'MIDDEL', 'KOUD'}
    rows, other = [], 0
    for k, v in sorted(dist.items(), key=lambda x: -x[1]):
        if k.upper() in known:
            rows.append(f'<tr><td data-label="Warmte">{esc(k)}</td><td data-label="Leads"><strong>{v}</strong></td></tr>')
        else:
            other += v
    if other:
        rows.append(f'<tr><td data-label="Warmte" class="muted">Overig</td><td data-label="Leads"><strong>{other}</strong></td></tr>')
    return f'<div class="tw mobile-cards"><table><thead><tr><th>Warmte</th><th>Leads</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def render_events(events: list) -> str:
    if not events:
        return '<p class="muted">Nog geen events. Webhook staat klaar.</p>'
    rows = ''.join(f'<tr><td data-label="Event"><span class="pill pill-s">{esc(e.get("event_type","—"))}</span></td><td data-label="Email">{esc(e.get("email","—"))}</td><td data-label="Tijd" class="muted">{esc(fmt_dt(e.get("event_ts")))}</td></tr>' for e in events[:15])
    return f'<div class="tw mobile-cards"><table><thead><tr><th>Event</th><th>Email</th><th>Tijd</th></tr></thead><tbody>{rows}</tbody></table></div>'


def build_page(state: dict) -> str:
    brevo = state.get('brevo', {})
    db = state.get('db', {})
    kpi = brevo.get('kpi', {})
    recs = state.get('recommendations', [])
    generated = state.get('generated_at', utc_now())

    brevo_ok = brevo.get('brevo_ok', False)
    db_ok = db.get('db_ok', False)
    sys_label = 'LIVE' if brevo_ok and db_ok else 'DEGRADED'
    sys_cls = 'badge-ok' if sys_label == 'LIVE' else 'badge-warn'

    process_html = '''<div class="note" style="margin-top:0">
<strong>🔄 Vast proces (model-agnostic)</strong>
<ol style="margin:8px 0 0;padding-left:18px;display:grid;gap:4px">
<li><strong>fetch_brevo_stats.py</strong> — Brevo + DB data</li>
<li><strong>run_daily_cycle.py</strong> — Scores + reports</li>
<li><strong>render_partner_campaign_page.py</strong> — Pagina</li>
<li><strong>deploy_live.py</strong> — Push naar VPS</li>
<li><strong>Daily handoff</strong> — Hot prospects → Telegram</li>
</ol></div>'''

    body = f'''
<div class="hero">
  <div class="ey">Partner campaign cockpit</div>
  <h1>Partners</h1>
  <div class="sub">Live Brevo + lokale DB intelligence.</div>
  <div class="ts">Brevo: {"live" if brevo_ok else "offline"} · DB: {"live" if db_ok else "offline"} · Ververst: {esc(fmt_dt(generated))} <span class="badge {sys_cls}">{sys_label}</span></div>
  {render_kpi_cards(kpi, db, brevo)}
</div>

<div class="g g12">
  <div class="p s7">
    <div class="ph"><div><div class="ey">Intelligence</div><h2>Hot prospects</h2></div></div>
    {render_hot_prospects(db.get('hot_prospects', []))}
  </div>
  <div class="p s5">
    <div class="ph"><div><div class="ey">AI recommendations</div><h2>Partneradvies</h2></div></div>
    <div class="sub" style="margin-bottom:12px">Korte AI-duiding voor de partnercampagne: waar zit nu de meeste kans op reply, click en opvolging?</div>
    {render_ai_cards(recs)}
  </div>
</div>

<div class="g g12">
  <div class="p s7">
    <div class="ph"><div><div class="ey">Campaigns</div><h2>Brevo campagnes</h2></div></div>
    {render_campaign_table(brevo.get('campaigns', []) or db.get('local_campaigns', []))}
  </div>
  <div class="p s5">
    <div class="ph"><div><div class="ey">Brevo</div><h2>Lijsten</h2></div></div>
    {render_lists(brevo.get('lists', []))}
    {process_html}
  </div>
</div>

<div class="g g12">
  <div class="p s5">
    <div class="ph"><div><div class="ey">Pipeline</div><h2>Status</h2></div></div>
    {render_status_dist(db.get('status_distribution', {}))}
  </div>
  <div class="p s7">
    <div class="ph"><div><div class="ey">Segmentatie</div><h2>Warmte</h2></div></div>
    {render_warmth_dist(db.get('warmth_distribution', {}))}
  </div>
</div>

<div class="g g12">
  <div class="p s12">
    <div class="ph"><div><div class="ey">Events</div><h2>Webhook activity</h2></div></div>
    {render_events(db.get('recent_events', []))}
  </div>
</div>
'''

    return shell('Partner Campaign', 'Brevo outreach + partner intelligence', 'Partners', 'partner-campaign', body)


def main() -> None:
    state = load_state()
    if not state:
        print('⚠ No state file. Run fetch_brevo_stats.py first.')
        return
    html = build_page(state)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding='utf-8')
    print(f'✅ Wrote {OUTPUT_PATH} ({len(html):,} bytes)')


if __name__ == '__main__':
    main()
