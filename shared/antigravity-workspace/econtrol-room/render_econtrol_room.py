#!/usr/bin/env python3
from __future__ import annotations

from html import escape
from pathlib import Path
import sys

BASE_DIR = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
SCRIPTS_DIR = BASE_DIR / 'scripts'
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from render_ui import BUILD_DIR, BASE, ECODASH_DATA_DIR, load_json, shell_page, utc_now_label, write_text

QUEUE_PATH = BASE / 'queue' / 'SMART_CONTENT_QUEUE.json'
REFRESH_PATH = BASE / 'queue' / 'REFRESH_QUEUE.json'
QUEUE_HEALTH_PATH = BASE / 'state' / 'queue-health.json'
OPS_STATUS_PATH = BASE / 'state' / 'ops-status.json'
WORKFLOW_HEALTH_PATH = BASE / 'state' / 'workflow-health.json'
ALERTS_PATH = BASE / 'state' / 'workflow-alerts.json'
SOURCE_SIGNALS_PATH = BASE / 'state' / 'source-signals.json'
OUTPUT_PATH = BUILD_DIR / 'index.html'

GA4_PATH = ECODASH_DATA_DIR / 'ga4.json'
ADS_PATH = ECODASH_DATA_DIR / 'ads.json'
GSC_PATH = ECODASH_DATA_DIR / 'gsc.json'
SHOPIFY_PATH = ECODASH_DATA_DIR / 'shopify.json'
WEFACT_PATH = ECODASH_DATA_DIR / 'wefact.json'

WINDOW_ORDER = ['today', 'yesterday', 'last_7_days', 'last_28_days']
WINDOW_LABELS = {
    'today': 'Today',
    'yesterday': 'Yesterday',
    'last_7_days': 'Last 7 days',
    'last_28_days': 'Last 28 days',
}


def source_card(source_id: str, title: str, tone: str, description: str, metrics: list[tuple[str, dict]], foot: str = '') -> str:
    metric_html = []
    for label, values in metrics:
        attrs = ' '.join(f'data-{key}="{escape(str(value))}"' for key, value in values.items())
        default_value = escape(str(values.get('today', '-')))
        metric_html.append(f'''<div class="source-metric" {attrs}><span>{escape(label)}</span><strong data-role="metric-value">{default_value}</strong></div>''')
    foot_html = f'<div class="source-foot">{escape(foot)}</div>' if foot else ''
    return f'''<article class="source-card source-{escape(tone)}" data-source-card="{escape(source_id)}">
      <div class="source-card-top">
        <div>
          <div class="eyebrow">Data source</div>
          <h3>{escape(title)}</h3>
        </div>
        <span class="pill {'pill-live' if tone == 'live' else 'pill-warn' if tone == 'warn' else 'pill-accent'}">{escape(tone)}</span>
      </div>
      <p>{escape(description)}</p>
      <div class="source-metrics">{''.join(metric_html)}</div>
      {foot_html}
    </article>'''


def queue_card(item: dict) -> str:
    return f'''<article class="queue-card">
      <div class="queue-card-top"><span class="queue-score">{item.get('total_score', '-')}</span><div class="queue-tags"><span class="pill pill-live">{escape(item.get('priority_label', '-'))}</span><span class="pill pill-soft">{escape(item.get('business_goal', '-'))}</span></div></div>
      <h3>{escape(item.get('title', 'Untitled'))}</h3>
      <p>{escape(item.get('why_now', ''))}</p>
    </article>'''


def summary_card(label: str, note: str, tone: str = 'accent', values: dict | None = None) -> str:
    values = values or {}
    attrs = ' '.join(f'data-{key}="{escape(str(value))}"' for key, value in values.items())
    default_value = escape(str(values.get('last_7_days', '-')))
    return f'''<article class="summary-card summary-{escape(tone)}" {attrs}>
      <span class="summary-label">{escape(label)}</span>
      <strong class="summary-value" data-role="summary-value">{default_value}</strong>
      <div class="summary-note">{escape(note)}</div>
    </article>'''


def pulse_card(title: str, body: str, tone: str = 'accent') -> str:
    return f'''<article class="pulse-card pulse-{escape(tone)}">
      <div class="pulse-title">{escape(title)}</div>
      <div class="pulse-body">{escape(body)}</div>
    </article>'''


def refresh_card(item: dict) -> str:
    return f'''<article class="refresh-card">
      <div class="refresh-top"><span class="pill {'pill-warn' if item.get('severity') == 'high' else 'pill-accent'}">{escape(item.get('severity', '-'))}</span><span class="pill pill-soft">{escape(item.get('issue_type', '-'))}</span></div>
      <h3>{escape(item.get('url','-'))}</h3>
      <p>{escape(item.get('recommended_fix','-'))}</p>
    </article>'''


def build_window_metrics(data: dict, mapping: list[tuple[str, str]]) -> list[tuple[str, dict]]:
    windows = data.get('windows', {})
    metrics = []
    for label, key in mapping:
        values = {}
        for window in WINDOW_ORDER:
            current = windows.get(window, {})
            values[window] = current.get(key, current.get(f'{key}_fmt', '-'))
            fmt_key = f'{key}_fmt'
            if fmt_key in current:
                values[window] = current.get(fmt_key, values[window])
        metrics.append((label, values))
    return metrics


def main() -> None:
    queue = load_json(QUEUE_PATH)
    refresh = load_json(REFRESH_PATH)
    queue_health = load_json(QUEUE_HEALTH_PATH)
    ops = load_json(OPS_STATUS_PATH)
    workflow_health = load_json(WORKFLOW_HEALTH_PATH)
    alerts = load_json(ALERTS_PATH)
    source_signals = load_json(SOURCE_SIGNALS_PATH)

    ga4 = load_json(GA4_PATH)
    ads = load_json(ADS_PATH)
    gsc = load_json(GSC_PATH)
    shopify = load_json(SHOPIFY_PATH)
    wefact = load_json(WEFACT_PATH)

    top_queue = ''.join(queue_card(item) for item in queue.get('top_5_now', [])[:3]) or '<p class="empty">Nog geen top-items.</p>'
    refresh_cards = ''.join(refresh_card(item) for item in refresh.get('items', [])[:4]) or '<p class="empty">Geen refresh-items.</p>'
    alerts_list = ''.join(f"<li><strong>{escape(item.get('type', 'alert'))}</strong><div class='sub'>{escape(item.get('message', ''))}</div></li>" for item in alerts.get('items', [])[:4]) or '<li>Geen actieve alerts.</li>'
    warnings = queue_health.get('warnings', [])
    warning_html = ''.join(f'<li>{escape(item)}</li>' for item in warnings[:4]) or '<li>Geen kritieke warnings.</li>'

    cards = []
    cards.append(source_card(
        'ga4',
        'GA4',
        'live' if ga4.get('status') == 'live' else 'warn',
        'Verkeer en bezoekgedrag vanuit GA4. Dit is je bezoeklaag.',
        build_window_metrics(ga4, [('Sessions', 'sessions'), ('Active users', 'active_users'), ('Revenue', 'revenue')]),
        foot=f"Property {ga4.get('property_id', '-')} · {ga4.get('measurement_id', '-')}",
    ))
    top_ads_campaign = ads.get('campaigns', [])
    cards.append(source_card(
        'ads',
        'Google Ads',
        'warn' if (ads.get('windows', {}).get('last_28_days', {}).get('conversion_value', 0) or 0) == 0 else 'live',
        'Campagnes, spend en gemeten conversion value. Hier wil je later Wefact-validatie naast hebben.',
        build_window_metrics(ads, [('Spend', 'cost_eur'), ('Clicks', 'clicks'), ('CTR', 'ctr'), ('Value', 'value_eur')]),
        foot=(top_ads_campaign[0] if top_ads_campaign else {}).get('focus', ''),
    ))
    cards.append(source_card(
        'gsc',
        'Google Search Console',
        'live' if gsc.get('status') == 'live' else 'warn',
        'SEO-prestaties, klikken en zichtbaarheid in Google.',
        build_window_metrics(gsc, [('Clicks', 'clicks_fmt'), ('Impressions', 'impressions_fmt'), ('CTR', 'ctr_fmt'), ('Position', 'position_fmt')]),
        foot='Opportunities en top-pages voeden de queue.',
    ))
    top_shopify_products = shopify.get('top_products', [])
    cards.append(source_card(
        'shopify',
        'Shopify omzet',
        'live' if shopify.get('status') == 'live' else 'warn',
        'Directe shop-omzet. Niet de volledige waarheid zodra Wefact meedoet.',
        build_window_metrics(shopify, [('Revenue', 'revenue_fmt'), ('Orders', 'orders_fmt'), ('AOV', 'aov_fmt')]),
        foot=(top_shopify_products[0] if top_shopify_products else {}).get('detail', ''),
    ))
    cards.append(source_card(
        'wefact',
        'Wefact',
        'live' if wefact.get('status') == 'live' else 'warn',
        'Finance truth layer voor offertes en facturen. Deze laag laat nu echte Wefact-cijfers zien naast Shopify.',
        build_window_metrics(wefact, [('Facturen', 'invoice_count_fmt'), ('Omzet', 'invoice_total_fmt'), ('Offertes', 'quote_count_fmt'), ('Open', 'open_outstanding_fmt')]),
        foot=f"Debiteuren {wefact.get('debtors_total', '-')} · bron {wefact.get('source', '-')}",
    ))

    snapshots = source_signals.get('snapshots', {})
    summary_cards = ''.join([
        summary_card('Bezoeken', 'GA4 verkeer', 'accent', {
            'today': ga4.get('windows', {}).get('today', {}).get('sessions_fmt', '-'),
            'yesterday': ga4.get('windows', {}).get('yesterday', {}).get('sessions_fmt', '-'),
            'last_7_days': ga4.get('windows', {}).get('last_7_days', {}).get('sessions_fmt', '-'),
            'last_28_days': ga4.get('windows', {}).get('last_28_days', {}).get('sessions_fmt', '-'),
        }),
        summary_card('Organic clicks', 'GSC klikvolume', 'accent', {
            'today': gsc.get('windows', {}).get('today', {}).get('clicks_fmt', '-'),
            'yesterday': gsc.get('windows', {}).get('yesterday', {}).get('clicks_fmt', '-'),
            'last_7_days': gsc.get('windows', {}).get('last_7_days', {}).get('clicks_fmt', '-'),
            'last_28_days': gsc.get('windows', {}).get('last_28_days', {}).get('clicks_fmt', '-'),
        }),
        summary_card('Ads spend', 'Google Ads spend', 'warn', {
            'today': ads.get('windows', {}).get('today', {}).get('cost_eur', '-'),
            'yesterday': ads.get('windows', {}).get('yesterday', {}).get('cost_eur', '-'),
            'last_7_days': ads.get('windows', {}).get('last_7_days', {}).get('cost_eur', '-'),
            'last_28_days': ads.get('windows', {}).get('last_28_days', {}).get('cost_eur', '-'),
        }),
        summary_card('Shopify omzet', 'Shop omzet nu', 'live', {
            'today': shopify.get('windows', {}).get('today', {}).get('revenue_fmt', '-'),
            'yesterday': shopify.get('windows', {}).get('yesterday', {}).get('revenue_fmt', '-'),
            'last_7_days': shopify.get('windows', {}).get('last_7_days', {}).get('revenue_fmt', '-'),
            'last_28_days': shopify.get('windows', {}).get('last_28_days', {}).get('revenue_fmt', '-'),
        }),
        summary_card('Wefact omzet', 'Facturen via Wefact', 'live', {
            'today': wefact.get('windows', {}).get('today', {}).get('invoice_total_fmt', '-'),
            'yesterday': wefact.get('windows', {}).get('yesterday', {}).get('invoice_total_fmt', '-'),
            'last_7_days': wefact.get('windows', {}).get('last_7_days', {}).get('invoice_total_fmt', '-'),
            'last_28_days': wefact.get('windows', {}).get('last_28_days', {}).get('invoice_total_fmt', '-'),
        }),
    ])

    pulse_cards = ''.join([
        pulse_card('Traffic', f"{ga4.get('windows', {}).get('last_7_days', {}).get('sessions_fmt', '-')} sessies in 7 dagen. Genoeg om de commerciële signalen serieus te nemen.", 'accent'),
        pulse_card('Ads', f"{ads.get('windows', {}).get('last_7_days', {}).get('cost_eur', '-')} spend, maar value blijft {ads.get('windows', {}).get('last_28_days', {}).get('value_eur', '-')}. Tracking of conversieketen moet strakker.", 'warn'),
        pulse_card('Finance truth', f"Shopify en Wefact draaien nu naast elkaar. Wefact laat {wefact.get('windows', {}).get('last_28_days', {}).get('invoice_total_fmt', '-')} aan factuurwaarde in 28 dagen zien.", 'live'),
    ])

    hero = f'''
    <section class="hero-card hero-main">
      <div class="hero-head">
        <div>
          <div class="eyebrow">Econtrol Room</div>
          <h1>EcoHandel.nl</h1>
          <div class="subhead">Econtrol Room blijft leidend. Deze app-laag volgt de control room, maakt hem iPhone-proof en houdt de kern scanbaar: verkeer, SEO, ads, omzet, signalen en prioriteiten.</div>
        </div>
        <div class="timestamp">Built {utc_now_label()}<br>Ops status: {escape(ops.get('ops_status', 'unknown'))}<br>Workflow health: {escape(workflow_health.get('overall_status', 'unknown'))}</div>
      </div>
      <div class="summary-grid">{summary_cards}</div>
      <div class="range-switch-wrap"><div class="range-switch" data-range-switch>
        <button class="range-pill" data-range="today">Today</button>
        <button class="range-pill" data-range="yesterday">Yesterday</button>
        <button class="range-pill is-active" data-range="last_7_days">Last 7 days</button>
        <button class="range-pill" data-range="last_28_days">Last 28 days</button>
      </div></div>
      <div class="hero-note">De periode-switch stuurt de datakaarten hieronder. Default staat nu op Last 7 days zodat het dashboard niet leeg oogt als Today nog weinig data heeft. Wefact volgt als finance truth layer zodra de whitelist live staat.</div>
    </section>
    '''

    content = f'''
      {hero}
      <div class="grid">
        <section class="panel span-12">
          <div class="panel-head"><div><div class="eyebrow">Executive pulse</div><h2>Wat nu aandacht vraagt</h2></div><span class="status status-live">lead layer</span></div>
          <div class="pulse-grid">{pulse_cards}</div>
        </section>

        <section class="panel span-12">
          <div class="panel-head"><div><div class="eyebrow">Core data</div><h2>Kernblokken van de machine</h2></div><span class="status status-live">live shell</span></div>
          <div class="sources-grid">{''.join(cards)}</div>
        </section>

        <section class="panel span-5">
          <div class="panel-head"><div><div class="eyebrow">Attention</div><h2>Belangrijkste signalen</h2></div></div>
          <ul class="stack">{alerts_list}</ul>
          <div class="warning-box"><ul>{warning_html}</ul></div>
        </section>

        <section class="panel span-7">
          <div class="panel-head"><div><div class="eyebrow">Mission priority</div><h2>Waar Jean nu op stuurt</h2></div></div>
          <div class="queue-grid">{top_queue}</div>
        </section>

        <section class="panel span-7">
          <div class="panel-head"><div><div class="eyebrow">Refresh first</div><h2>Snelste verbeterkansen</h2></div></div>
          <div class="refresh-grid">{refresh_cards}</div>
        </section>

        <section class="panel span-5">
          <div class="panel-head"><div><div class="eyebrow">System notes</div><h2>Mission board status</h2></div></div>
          <ul class="stack">
            <li><strong>Econtrol Room is leidend</strong><div class="sub">Deze mobiele laag volgt de machine en krijgt geen losse logica buiten de control room om.</div></li>
            <li><strong>Finance truth wordt breder</strong><div class="sub">Shopify blijft shoplaag, maar Wefact draait nu read-only mee voor facturen en offertes.</div></li>
            <li><strong>Data freshness</strong><div class="sub">GA4 {escape(str(snapshots.get('ga4_fetched_at', ga4.get('fetched_at', '-'))))} · Ads {escape(str(snapshots.get('ads_fetched_at', ads.get('fetched_at', '-'))))} · GSC {escape(str(gsc.get('fetched_at', '-')))} · Shopify {escape(str(shopify.get('fetched_at', '-')))} · Wefact {escape(str(wefact.get('fetched_at', '-')))}</div></li>
          </ul>
        </section>
      </div>
    '''

    extra_css = '''
    .hero-main{margin-top:4px}
    .hero-head{display:flex;justify-content:space-between;gap:20px;align-items:flex-end}
    .summary-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin-top:18px}
    .summary-card{padding:16px;border-radius:18px;border:1px solid rgba(255,255,255,.06);background:rgba(255,255,255,.03)}
    .summary-label{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}
    .summary-value{display:block;margin-top:8px;font-size:26px;letter-spacing:-.04em}
    .summary-note{margin-top:6px;color:var(--muted);font-size:13px;line-height:1.5}
    .summary-live .summary-value{color:#86efac}
    .summary-warn .summary-value{color:#fcd34d}
    .summary-accent .summary-value{color:var(--cyan)}
    .range-switch-wrap{margin-top:18px;overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:4px}
    .range-switch{display:flex;gap:10px;flex-wrap:nowrap;min-width:max-content}
    .range-pill{appearance:none;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.04);color:#d9e7f3;padding:10px 14px;border-radius:999px;font-weight:800;cursor:pointer;white-space:nowrap;flex:0 0 auto}
    .range-pill.is-active{background:linear-gradient(135deg,rgba(34,211,238,.18),rgba(139,92,246,.18));border-color:rgba(255,255,255,.14);color:#fff}
    .hero-note{margin-top:14px;color:var(--muted);font-size:13px;line-height:1.6}
    .pulse-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
    .pulse-card{padding:18px;border-radius:20px;border:1px solid rgba(255,255,255,.07);background:rgba(255,255,255,.03)}
    .pulse-title{font-size:12px;text-transform:uppercase;letter-spacing:.1em;font-weight:800;color:var(--muted)}
    .pulse-body{margin-top:10px;font-size:16px;line-height:1.6;overflow-wrap:anywhere}
    .pulse-accent .pulse-body{color:#dff8ff}
    .pulse-warn .pulse-body{color:#fde68a}
    .pulse-live .pulse-body{color:#bbf7d0}
    .sources-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
    .source-card{padding:18px;border-radius:20px;background:linear-gradient(180deg,rgba(7,19,31,.8),rgba(10,24,40,.95));border:1px solid rgba(255,255,255,.07);min-width:0}
    .source-card-top{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
    .source-card h3{margin:6px 0 8px;font-size:22px;letter-spacing:-.03em}
    .source-card p{margin:0;color:var(--muted);line-height:1.6}
    .source-metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:16px}
    .source-metric{padding:14px;border-radius:16px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.05);min-width:0}
    .source-metric span{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}
    .source-metric strong{display:block;margin-top:7px;font-size:23px;letter-spacing:-.04em;overflow-wrap:anywhere}
    .source-foot{margin-top:14px;padding-top:14px;border-top:1px solid rgba(255,255,255,.06);color:var(--muted);font-size:13px;line-height:1.5;overflow-wrap:anywhere}
    .source-pending .source-metric strong{font-size:18px}
    .queue-grid,.refresh-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
    .queue-card,.refresh-card{padding:18px;border-radius:20px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);min-width:0}
    .queue-card-top,.refresh-top{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
    .queue-score{width:50px;height:50px;border-radius:15px;background:linear-gradient(135deg,rgba(34,211,238,.22),rgba(139,92,246,.22));display:flex;align-items:center;justify-content:center;font-weight:900;font-size:22px;flex:0 0 auto}
    .queue-tags{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
    .queue-card h3,.refresh-card h3{margin:14px 0 10px;font-size:20px;line-height:1.2;letter-spacing:-.03em;overflow-wrap:anywhere}
    .queue-card p,.refresh-card p{margin:0;color:var(--muted);line-height:1.6;overflow-wrap:anywhere}
    .warning-box{margin-top:16px;padding:16px;border-radius:18px;background:rgba(245,158,11,.09);border:1px solid rgba(245,158,11,.22)}
    .warning-box ul{margin:0;padding-left:18px;display:grid;gap:8px}
    @media (max-width:1180px){.hero-head,.summary-grid,.pulse-grid,.sources-grid,.queue-grid,.refresh-grid,.source-metrics{grid-template-columns:1fr;display:grid}.hero-head{gap:12px}.source-metrics{gap:10px}}
    '''

    extra_js = '''<script>
    (function(){
      const switcher = document.querySelector('[data-range-switch]');
      if (!switcher) return;
      const setRange = (range) => {
        document.querySelectorAll('.range-pill').forEach(btn => btn.classList.toggle('is-active', btn.dataset.range === range));
        document.querySelectorAll('.source-metric').forEach(metric => {
          const target = metric.querySelector('[data-role="metric-value"]');
          const value = metric.getAttribute('data-' + range);
          if (target && value !== null) target.textContent = value;
        });
        document.querySelectorAll('.summary-card').forEach(card => {
          const target = card.querySelector('[data-role="summary-value"]');
          const value = card.getAttribute('data-' + range);
          if (target && value !== null) target.textContent = value;
        });
      };
      switcher.addEventListener('click', (event) => {
        const btn = event.target.closest('[data-range]');
        if (!btn) return;
        setRange(btn.dataset.range);
      });
      setRange('last_7_days');
    })();
    </script>'''

    html = shell_page(
        title='EcoHandel.nl — Dashboard',
        page_title='Dashboard',
        page_subtitle='Traffic, omzet, SEO en workflows in één mobiele shell',
        description='Econtrol Room dashboard voor EcoHandel.nl',
        active='dashboard',
        content=content,
        extra_css=extra_css,
        extra_js=extra_js,
    )
    write_text(OUTPUT_PATH, html)
    print(f'Wrote {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
