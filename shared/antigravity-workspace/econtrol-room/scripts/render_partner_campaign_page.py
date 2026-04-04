#!/usr/bin/env python3
from __future__ import annotations

import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from render_ui import shell_page, write_text, BUILD_DIR

PC_BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/partner-campaign')
DB_PATH = PC_BASE / 'data' / 'partner_campaign.db'
REPORTS_DIR = PC_BASE / 'reports'
CONFIG_PATH = PC_BASE / 'config.template.json'
ARCH_PATH = PC_BASE / 'SYSTEM_ARCHITECTURE.md'
OPS_PATH = PC_BASE / 'DAILY_OPERATIONS.md'
ROADMAP_PATH = PC_BASE / 'IMPLEMENTATION_ROADMAP.md'
OUTPUT_PATH = BUILD_DIR / 'partner-campaign.html'


def utc_now_label() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')


def load_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def latest_report() -> dict:
    files = sorted(REPORTS_DIR.glob('hot-prospects-*.json'))
    return load_json(files[-1]) if files else {}


def compact(text: str | None, limit: int = 120) -> str:
    text = (text or '-').replace('\n', ' ').strip()
    return text if len(text) <= limit else text[: limit - 1] + '…'


def stat_card(label: str, value: str, note: str, tone: str = 'accent') -> str:
    return f'''<article class="stat-card stat-{tone}"><span class="stat-label">{label}</span><strong class="stat-value">{value}</strong><div class="stat-note">{note}</div></article>'''


def lead_card(item: dict) -> str:
    return f'''<article class="lead-card">
      <div class="lead-top"><span class="pill pill-accent">score {item.get('score', '-')}</span><span class="pill {'pill-live' if item.get('recommended_action') == 'BEL VANDAAG' else 'pill-warn' if item.get('recommended_action') in {'HANDMATIG MAILEN','OPVOLGEN'} else 'pill-soft'}">{item.get('recommended_action', '-')}</span></div>
      <h3>{item.get('company_name', '-')}</h3>
      <p>{item.get('contact_person') or item.get('email') or item.get('website') or '-'}</p>
      <div class="lead-meta"><div><span class="mini-label">Warmte</span><strong>{item.get('warmth') or '-'}</strong></div><div><span class="mini-label">Opens</span><strong>{item.get('open_count', 0)}</strong></div><div><span class="mini-label">Clicks</span><strong>{item.get('click_count', 0)}</strong></div><div><span class="mini-label">Replies</span><strong>{item.get('reply_count', 0)}</strong></div></div>
    </article>'''


def main() -> None:
    report = latest_report()
    config = load_json(CONFIG_PATH)

    total_leads = 0
    status_counter = Counter()
    contactable = 0
    with_email = 0
    warmish = 0
    hot_score_avg = 0.0
    top_leads = []
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        total_leads = conn.execute('SELECT COUNT(*) FROM leads').fetchone()[0]
        rows = conn.execute('SELECT status, email, warmth, hot_score FROM leads').fetchall()
        status_counter = Counter((row['status'] or 'unknown') for row in rows)
        contactable = sum(1 for row in rows if row['status'] not in {'unsubscribed', 'bounced', 'dead'})
        with_email = sum(1 for row in rows if row['email'])
        warmish = sum(1 for row in rows if 'WARM' in str(row['warmth'] or '').upper())
        hot_scores = [float(row['hot_score'] or 0) for row in rows]
        hot_score_avg = round(sum(hot_scores) / len(hot_scores), 1) if hot_scores else 0.0
        top_rows = conn.execute('SELECT company_name, email, contact_person, website, warmth, hot_score, status FROM leads ORDER BY hot_score DESC, lead_score DESC, company_name ASC LIMIT 8').fetchall()
        top_leads = [dict(r) for r in top_rows]
        conn.close()

    hot_prospects = report.get('hot_prospects', [])[:6]
    hot_cards = ''.join(lead_card(item) for item in hot_prospects) or '<p class="empty">Nog geen hot prospects report.</p>'
    top_cards = ''.join(lead_card({
        'company_name': item.get('company_name'),
        'contact_person': item.get('contact_person'),
        'email': item.get('email'),
        'website': item.get('website'),
        'warmth': item.get('warmth'),
        'score': item.get('hot_score', 0),
        'open_count': 0,
        'click_count': 0,
        'reply_count': 0,
        'recommended_action': item.get('status', '-')
    }) for item in top_leads) or '<p class="empty">Nog geen ranked leads.</p>'

    stat_cards = ''.join([
        stat_card('Leads totaal', str(total_leads), 'Huidige databasebasis', 'accent'),
        stat_card('Contacteerbaar', str(contactable), 'Niet bounced/unsubscribed', 'live'),
        stat_card('Met email', str(with_email), 'Brevo-klaar deel van lijst', 'accent'),
        stat_card('Warm leads', str(warmish), 'Researchlaag met hogere kans', 'warn'),
    ])

    status_rows = ''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in sorted(status_counter.items())) or '<tr><td colspan="2">Nog geen statusdata.</td></tr>'
    foundation_items = [
        ('Architectuur', 'ready' if ARCH_PATH.exists() else 'missing'),
        ('Daily ops', 'ready' if OPS_PATH.exists() else 'missing'),
        ('Roadmap', 'ready' if ROADMAP_PATH.exists() else 'missing'),
        ('Brevo config template', 'ready' if CONFIG_PATH.exists() else 'missing'),
        ('Local DB', 'ready' if DB_PATH.exists() else 'missing'),
        ('Hot report', 'ready' if report else 'missing'),
    ]
    foundation_html = ''.join(f'<li><strong>{name}</strong><div class="sub">{status}</div></li>' for name, status in foundation_items)
    waiting_html = ''.join(f'<li>{item}</li>' for item in config.get('brevo', {}).keys())
    if waiting_html:
        waiting_html = '<li>Brevo config placeholders staan klaar: api_key, sender_name, sender_email, webhook_secret, webhook_url.</li>'

    content = f'''
      <section class="hero-card">
        <div class="eyebrow">Partner campaign</div>
        <h1>Partners</h1>
        <div class="subhead">Autonome Brevo outreachlaag voor installateurs en partners. Deze cockpit bundelt leadbasis, hot prospects, campaign readiness en dagelijkse opvolglogica.</div>
        <div class="hero-grid">
          <div class="hero-metric"><div class="label">DB</div><div class="value">{'Ready' if DB_PATH.exists() else 'Missing'}</div></div>
          <div class="hero-metric"><div class="label">Hot prospects</div><div class="value">{report.get('hot_count', 0)}</div></div>
          <div class="hero-metric"><div class="label">Avg hot score</div><div class="value">{hot_score_avg}</div></div>
          <div class="hero-metric"><div class="label">Built</div><div class="value" style="font-size:18px">{utc_now_label()}</div></div>
        </div>
      </section>
      <div class="grid">
        <section class="panel span-12"><div class="panel-head"><div><div class="eyebrow">Foundation</div><h2>Systeemfundament</h2></div><span class="status status-live">core ready</span></div><div class="stats-grid">{stat_cards}</div></section>
        <section class="panel span-7"><div class="panel-head"><div><div class="eyebrow">Daily action</div><h2>Hot prospects vandaag</h2></div></div><div class="lead-grid">{hot_cards}</div></section>
        <section class="panel span-5"><div class="panel-head"><div><div class="eyebrow">Readiness</div><h2>Wat staat al</h2></div></div><ul class="stack">{foundation_html}</ul><div class="notice-box"><strong>Nog nodig van Milan</strong><ul><li>Brevo EcoHandel config</li><li>Verified sender</li><li>Webhook details</li><li>HTML prijslijst</li></ul></div></section>
        <section class="panel span-7"><div class="panel-head"><div><div class="eyebrow">Lead base</div><h2>Top ranked leads</h2></div></div><div class="lead-grid">{top_cards}</div></section>
        <section class="panel span-5"><div class="panel-head"><div><div class="eyebrow">Pipeline</div><h2>Statusverdeling</h2></div></div><div class="table-wrap"><table><thead><tr><th>Status</th><th>Aantal</th></tr></thead><tbody>{status_rows}</tbody></table></div><div class="notice-box"><strong>Operating model</strong><ul><li>Brevo = verzendlaag</li><li>Lokale DB = bron van waarheid</li><li>Replies/productintentie wegen zwaarder dan opens</li></ul></div></section>
      </div>
    '''

    extra_css = '''
    .stats-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}
    .stat-card{padding:16px;border-radius:18px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06)}
    .stat-label{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}
    .stat-value{display:block;margin-top:8px;font-size:26px;letter-spacing:-.04em}
    .stat-note{margin-top:6px;color:var(--muted);font-size:13px;line-height:1.5}
    .stat-live .stat-value{color:#86efac}.stat-warn .stat-value{color:#fcd34d}.stat-accent .stat-value{color:var(--cyan)}
    .lead-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
    .lead-card{padding:18px;border-radius:20px;background:linear-gradient(180deg,rgba(7,19,31,.8),rgba(10,24,40,.95));border:1px solid rgba(255,255,255,.07);min-width:0}
    .lead-top{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}
    .lead-card h3{margin:12px 0 8px;font-size:20px;letter-spacing:-.03em;overflow-wrap:anywhere}
    .lead-card p{margin:0;color:var(--muted);line-height:1.6;overflow-wrap:anywhere}
    .lead-meta{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:14px;padding-top:12px;border-top:1px solid rgba(255,255,255,.06)}
    .notice-box{margin-top:16px;padding:16px;border-radius:18px;background:rgba(34,211,238,.09);border:1px solid rgba(34,211,238,.18)}
    .notice-box ul{margin:10px 0 0;padding-left:18px;display:grid;gap:8px}
    @media (max-width:1180px){.stats-grid,.lead-grid,.lead-meta{grid-template-columns:1fr}}
    '''

    html = shell_page(
        title='EcoHandel.nl — Partner Campaign',
        page_title='Partners',
        page_subtitle='Brevo outreach, hot prospects en partner intelligence',
        description='Partner campaign cockpit voor EcoHandel.nl',
        active='partner_campaign',
        content=content,
        extra_css=extra_css,
    )
    write_text(OUTPUT_PATH, html)
    print(f'Wrote {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
