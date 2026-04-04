#!/usr/bin/env python3
"""Rebuild ALL Econtrol Room pages from state data.

Pages: index.html (dashboard), workflows.html, smart-content-queue.html, partner-campaign.html
Also regenerates sw.js with cache-busting.

Model-agnostic: any agent can run this to regenerate all pages.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
STATE = BASE / 'state'
QUEUE = BASE / 'queue'
BUILD = BASE / 'build'

VERSION = str(int(time.time()))


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def load_json(path: Path) -> dict | list:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def esc(s) -> str:
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def fmt_num(v) -> str:
    if v is None:
        return '—'
    if isinstance(v, float):
        if v >= 1000:
            return f'€{v:,.0f}'.replace(',', '.')
        return f'{v:.1f}'
    if isinstance(v, int) and v >= 1000:
        return f'{v:,}'.replace(',', '.')
    return str(v)


def fmt_pct(v) -> str:
    if not v:
        return '—'
    return f'{v}%'


def fmt_dt(v: str | None, with_time: bool = True) -> str:
    if not v:
        return '—'
    try:
        s = str(v).replace('Z', '+00:00')
        dt = datetime.fromisoformat(s)
        if with_time:
            return dt.astimezone(timezone.utc).strftime('%d-%m-%Y %H:%M')
        return dt.astimezone(timezone.utc).strftime('%d-%m-%Y')
    except Exception:
        return str(v)


def trend_label(current, previous, suffix: str = '') -> str:
    try:
        c = float(current or 0)
        p = float(previous or 0)
    except Exception:
        return '—'
    if p == 0:
        if c > 0:
            return f'↑ nieuw{suffix}'
        return '—'
    diff = ((c - p) / p) * 100
    arrow = '↑' if diff > 0 else '↓' if diff < 0 else '→'
    return f'{arrow} {abs(diff):.1f}%{suffix}'


def render_ai_recommendation_block(title: str, intro: str, items: list[dict]) -> str:
    if not items:
        return f'''<div class="p s12"><div class="ph"><div><div class="ey">AI recommendations</div><h2>{esc(title)}</h2></div></div><div class="note"><strong>Geen concrete aanbevelingen</strong><div class="sub" style="margin-top:6px">{esc(intro)}</div></div></div>'''

    cards = ''
    for item in items[:4]:
        cards += f'''<div class="list-card">
  <strong>{esc(item.get("title", "Aanbeveling"))}</strong>
  <div class="meta"><span class="pill {esc(item.get("pill_class", "pill-c"))}">{esc(item.get("pill", "advies"))}</span></div>
  <div class="desc">{esc(item.get("text", ""))}</div>
</div>'''
    return f'''<div class="p s12"><div class="ph"><div><div class="ey">AI recommendations</div><h2>{esc(title)}</h2></div></div><div class="sub" style="margin-bottom:12px">{esc(intro)}</div><div class="card-grid">{cards}</div></div>'''


# ──────────────────────────────────────────────
# SHARED CSS + LAYOUT
# ──────────────────────────────────────────────
CSS = """:root{--bg:#06111d;--bg2:#091827;--panel:#0f2236;--panel2:#14314d;--line:#21415c;--text:#e8f0f7;--muted:#8ea7be;--green:#22c55e;--amber:#f59e0b;--red:#ef4444;--cyan:#22d3ee;--blue:#38bdf8;--purple:#8b5cf6;--pink:#ec4899;--safe-top:env(safe-area-inset-top,0px);--safe-bottom:env(safe-area-inset-bottom,0px);--nav-h:76px;--radius:20px}
*{box-sizing:border-box}html{scroll-behavior:smooth;background:var(--bg)}
body{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;background:radial-gradient(circle at top right,#163857 0,#06111d 44%);color:var(--text);-webkit-font-smoothing:antialiased;padding-bottom:calc(var(--nav-h) + var(--safe-bottom) + 20px);overflow-x:hidden}
a{color:inherit;text-decoration:none}
.shell{max-width:1680px;margin:0 auto;padding:calc(10px + var(--safe-top)) 14px 0;overflow-x:hidden}
.topbar{position:sticky;top:0;z-index:20;padding-top:4px;backdrop-filter:blur(20px)}
.topbar-inner{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 14px;border:1px solid rgba(255,255,255,.08);background:rgba(8,17,28,.86);border-radius:20px;box-shadow:0 12px 36px rgba(0,0,0,.22)}
.brand{display:flex;align-items:center;gap:10px;min-width:0}
.brand-mark{width:38px;height:38px;border-radius:12px;display:block;object-fit:cover;background:#0b1b2b;border:1px solid rgba(255,255,255,.08);box-shadow:0 8px 20px rgba(0,0,0,.22)}
.brand-copy{min-width:0}.brand-ey{font-size:10px;color:var(--cyan);text-transform:uppercase;letter-spacing:.12em;font-weight:800}
.brand-t{font-size:17px;font-weight:900;letter-spacing:-.03em}.brand-s{font-size:11px;color:var(--muted)}
.pill-page{padding:6px 10px;border-radius:999px;background:rgba(34,211,238,.08);border:1px solid rgba(34,211,238,.18);color:var(--cyan);font-size:11px;font-weight:800;letter-spacing:.04em}
.dnav{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 16px}
.dnav a{display:inline-flex;align-items:center;gap:6px;padding:8px 12px;border-radius:999px;font-weight:800;font-size:13px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.03);color:#dbe8f5}
.dnav a.on{background:#16a34a;color:#fff;border-color:rgba(22,163,74,.35);box-shadow:0 6px 16px rgba(22,163,74,.22)}
.wrap{padding:14px 0 0}
.hero{padding:22px;border-radius:24px;background:linear-gradient(180deg,rgba(15,34,54,.97),rgba(20,49,77,.93));border:1px solid rgba(255,255,255,.08);box-shadow:0 20px 60px rgba(0,0,0,.28);margin-bottom:18px}
.ey{font-size:10px;color:var(--cyan);text-transform:uppercase;letter-spacing:.1em;font-weight:800}
h1{margin:8px 0 10px;font-size:clamp(30px,6vw,46px);line-height:.94;letter-spacing:-.05em}
.sub{color:var(--muted);font-size:13px;line-height:1.6;max-width:920px}
.ts{color:var(--muted);font-size:12px;margin-top:10px}
.g{display:grid;gap:14px;margin-top:14px}
.g2{grid-template-columns:repeat(2,1fr)}.g3{grid-template-columns:repeat(3,1fr)}.g4{grid-template-columns:repeat(4,1fr)}.g12{grid-template-columns:repeat(12,1fr)}
.s6{grid-column:span 6}.s7{grid-column:span 7}.s5{grid-column:span 5}.s12{grid-column:span 12}.s4{grid-column:span 4}.s8{grid-column:span 8}
.p{padding:18px;border-radius:22px;background:linear-gradient(180deg,rgba(15,34,54,.94),rgba(20,49,77,.88));border:1px solid rgba(255,255,255,.08);box-shadow:0 16px 50px rgba(0,0,0,.22)}
.ph{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;margin-bottom:16px}
h2{margin:2px 0 0;font-size:21px;letter-spacing:-.035em}
.badge{padding:5px 10px;border-radius:999px;font-size:10px;font-weight:900;text-transform:uppercase;letter-spacing:.06em}
.badge-ok{background:rgba(34,197,94,.12);color:var(--green);border:1px solid rgba(34,197,94,.25)}
.badge-warn{background:rgba(245,158,11,.12);color:#fbbf24;border:1px solid rgba(245,158,11,.25)}
.badge-off{background:rgba(255,255,255,.05);color:var(--muted);border:1px solid rgba(255,255,255,.08)}
.sg{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.hero .sg{grid-template-columns:repeat(5,minmax(0,1fr));margin-top:16px}
.sc{padding:15px 16px;border-radius:18px;background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.025));border:1px solid rgba(255,255,255,.07);box-shadow:inset 0 1px 0 rgba(255,255,255,.03)}
.sl{display:block;font-size:9px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}
.sv{display:block;margin-top:7px;font-size:24px;letter-spacing:-.045em;font-weight:900;line-height:1.05}
.sn{margin-top:6px;color:var(--muted);font-size:12px;line-height:1.45}
.sc-g .sv{color:#86efac}.sc-w .sv{color:#fcd34d}.sc-c .sv{color:var(--cyan)}.sc-r .sv{color:#fca5a5}
.tw{position:relative;overflow-x:auto;overflow-y:hidden;-webkit-overflow-scrolling:touch;padding-bottom:6px;scrollbar-width:thin;scrollbar-color:rgba(34,211,238,.35) transparent}
.tw::-webkit-scrollbar{height:8px}
.tw::-webkit-scrollbar-thumb{background:rgba(34,211,238,.28);border-radius:999px}
table{width:100%;border-collapse:collapse}th,td{padding:8px 6px;border-top:1px solid var(--line);text-align:left;vertical-align:top;font-size:13px}
th{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}
.pill{display:inline-flex;padding:4px 8px;border-radius:999px;font-size:10px;font-weight:900;letter-spacing:.05em;text-transform:uppercase;border:1px solid rgba(255,255,255,.08)}
.pill-g{background:rgba(34,197,94,.16);color:#86efac}.pill-w{background:rgba(245,158,11,.16);color:#fcd34d}
.pill-c{background:rgba(34,211,238,.12);color:var(--cyan)}.pill-s{background:rgba(255,255,255,.05);color:var(--muted)}
.pill-r{background:rgba(239,68,68,.16);color:#fca5a5}
.note{padding:15px 16px;border-radius:18px;background:rgba(34,211,238,.08);border:1px solid rgba(34,211,238,.14);margin-top:12px}
.note ul,.note ol{margin:8px 0 0;padding-left:16px;display:grid;gap:6px}
.stack{display:grid;gap:12px}.stack-tight{display:grid;gap:10px}.stretch{height:100%}
.insight-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:14px}
.insight-card{padding:15px 16px;border-radius:18px;background:rgba(255,255,255,.028);border:1px solid rgba(255,255,255,.06)}
.insight-card strong{display:block;font-size:12px;letter-spacing:-.01em;margin-bottom:6px}.insight-card .mini{font-size:12px;color:var(--muted);line-height:1.45}
.card-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.stat-card{padding:15px 16px;border-radius:18px;background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.025));border:1px solid rgba(255,255,255,.07)}
.stat-card .k{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}
.stat-card .v{display:block;margin-top:8px;font-size:23px;font-weight:900;letter-spacing:-.04em;line-height:1.05}
.stat-card .n{display:block;margin-top:6px;font-size:12px;line-height:1.5;color:var(--muted)}
.list-card{padding:14px 16px;border-radius:18px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);overflow:hidden}
.list-card strong{display:block;font-size:14px;letter-spacing:-.01em;word-break:break-word}
.list-card .meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.list-card .desc{margin-top:8px;font-size:12px;line-height:1.55;color:var(--muted);word-break:break-word}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.muted{color:var(--muted)}
.refresh-btn{position:fixed;top:calc(var(--safe-top) + 70px);right:16px;z-index:30;width:42px;height:42px;border-radius:50%;background:rgba(34,211,238,.15);border:1px solid rgba(34,211,238,.25);color:var(--cyan);font-size:18px;display:flex;align-items:center;justify-content:center;cursor:pointer;backdrop-filter:blur(10px);box-shadow:0 6px 20px rgba(0,0,0,.3);transition:transform .2s}
.refresh-btn:active{transform:scale(.9)}
.bnav{position:fixed;left:0;right:0;bottom:0;z-index:40;padding:8px 12px calc(8px + var(--safe-bottom));pointer-events:none}
.bnav-in{max-width:720px;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:8px;padding:8px;border-radius:20px;background:rgba(8,17,28,.88);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.08);box-shadow:0 -8px 30px rgba(0,0,0,.28);pointer-events:auto}
.bnav a{display:flex;flex-direction:column;align-items:center;gap:4px;padding:8px 6px;border-radius:14px;color:#cfe2f3;font-size:10px;font-weight:800;letter-spacing:.04em}
.bnav a .ic{font-size:16px;line-height:1}
.bnav a.on{background:linear-gradient(135deg,rgba(34,211,238,.18),rgba(139,92,246,.18));color:#fff;border:1px solid rgba(255,255,255,.08)}
@media(max-width:1180px){.sg,.hero .sg,.g2,.g3,.g4,.insight-grid,.card-grid{grid-template-columns:1fr}.g12{grid-template-columns:1fr}.s4,.s5,.s6,.s7,.s8,.s12{grid-column:span 1}.dnav{display:none}.shell{padding:calc(8px + var(--safe-top)) 10px 0}.topbar{padding-top:2px}.topbar-inner{flex-direction:column;align-items:flex-start;padding:12px 12px 10px}.brand{width:100%}.brand-s{white-space:normal;overflow:visible;text-overflow:clip;line-height:1.4}.pill-page{width:100%;text-align:center;justify-content:center}.hero{padding:16px 14px 14px;border-radius:20px}.p{padding:14px;border-radius:20px}.ph{margin-bottom:12px}.refresh-btn{top:auto;bottom:calc(var(--safe-bottom) + 92px);right:12px;width:46px;height:46px}h1{font-size:clamp(28px,9vw,36px);line-height:1}h2{font-size:18px}.sub,.ts,.sn,.list-card .desc{font-size:12px}.sv{font-size:22px}.tw{margin:0 -4px;padding:0 4px 8px}.tw::after{content:'↔ swipe';display:block;margin-top:6px;font-size:11px;font-weight:700;letter-spacing:.04em;color:var(--muted);text-align:right}.tw table,table{min-width:680px}.mobile-cards{overflow:visible;margin:0;padding:0}.mobile-cards::after{display:none}.mobile-cards table{min-width:0}.mobile-cards thead{display:none}.mobile-cards tbody{display:grid;gap:10px}.mobile-cards tr{display:block;padding:12px;border:1px solid rgba(255,255,255,.08);border-radius:16px;background:rgba(255,255,255,.03)}.mobile-cards td{display:block;border-top:none;padding:0 0 8px;font-size:13px;word-break:break-word}.mobile-cards td:last-child{padding-bottom:0}.mobile-cards td::before{content:attr(data-label);display:block;margin-bottom:4px;font-size:10px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:800}.mobile-cards td .sub{margin-top:4px;font-size:12px;line-height:1.45}.mobile-cards .pill{margin-top:2px;max-width:100%;white-space:normal}.mobile-cards strong,.mobile-cards span,.mobile-cards div{word-break:break-word}}
@media(min-width:1181px){.bnav{display:none}.shell{padding-left:24px;padding-right:24px}}"""


def shell(title: str, subtitle: str, page_label: str, active_page: str, body: str) -> str:
    """Wrap body in the standard app shell with nav + refresh button."""
    pages = [
        ('/', 'Dashboard', '⌂'),
        ('/smart-content-queue.html', 'Queue', '◎'),
        ('/workflows.html', 'Workflows', '◈'),
        ('/partner-campaign.html', 'Partners', '✉'),
    ]
    dnav = '\n'.join(f'<a href="{url}" class="{"on" if url.split("/")[-1].replace(".html","") == active_page or (active_page == "dashboard" and url == "/") else ""}">{label}</a>' for url, label, _ in pages)
    bnav = '\n'.join(f'<a href="{url}" class="{"on" if url.split("/")[-1].replace(".html","") == active_page or (active_page == "dashboard" and url == "/") else ""}"><span class="ic">{icon}</span><span>{label}</span></a>' for url, label, icon in pages)

    return f'''<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>EcoHandel.nl — {esc(title)}</title>
<meta name="theme-color" content="#07111d">
<meta name="apple-mobile-web-app-title" content="EcoHandel.nl">
<link rel="manifest" href="/app.webmanifest?v={VERSION}">
<link rel="icon" href="/favicon.png?v={VERSION}" type="image/png">
<link rel="shortcut icon" href="/favicon.png?v={VERSION}" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v={VERSION}">
<link rel="apple-touch-icon-precomposed" href="/apple-touch-icon.png?v={VERSION}">
<style>{CSS}</style>
</head>
<body>
<button class="refresh-btn" onclick="location.reload(true)" title="Refresh">⟳</button>
<div class="shell">
  <div class="topbar"><div class="topbar-inner">
    <div class="brand"><img class="brand-mark" src="/favicon.png?v={VERSION}" alt="EcoHandel logo"><div class="brand-copy"><div class="brand-ey">Mission board</div><div class="brand-t">EcoHandel.nl</div><div class="brand-s">{esc(subtitle)}</div></div></div>
    <span class="pill-page">{esc(page_label)}</span>
  </div></div>
  <div class="wrap">
    <nav class="dnav">{dnav}</nav>
    {body}
  </div>
</div>
<nav class="bnav"><div class="bnav-in">{bnav}</div></nav>
<script>if("serviceWorker"in navigator)navigator.serviceWorker.getRegistrations().then(r=>r.forEach(w=>w.unregister()));
</script>
</body>
</html>'''


# ──────────────────────────────────────────────
# PAGE 1: DASHBOARD
# ──────────────────────────────────────────────
def build_dashboard() -> str:
    signals = load_json(STATE / 'source-signals.json')
    snap = signals.get('snapshots', {})
    partner = load_json(STATE / 'partner-campaign-live.json')
    brevo = partner.get('brevo', {})
    db = partner.get('db', {})
    ops = load_json(STATE / 'ops-status.json')
    ga4 = load_json(BASE / 'dashboard-data' / 'data' / 'ga4.json')
    gsc = load_json(BASE / 'dashboard-data' / 'data' / 'gsc.json')
    wefact = load_json(BASE / 'dashboard-data' / 'data' / 'wefact.json')
    ads = load_json(BASE / 'dashboard-data' / 'data' / 'ads.json')

    now = utc_now()

    def card(label, val, note='', css='sc-c'):
        return f'<div class="sc {css}"><span class="sl">{esc(label)}</span><span class="sv">{esc(val)}</span><span class="sn">{esc(note)}</span></div>'

    ga4w = ga4.get('windows', {})
    gscw = gsc.get('windows', {})
    wew = wefact.get('windows', {})
    adsw = ads.get('windows', {})
    pmax = ads.get('pmax', {})

    ga4_today = ga4w.get('today', {})
    ga4_yesterday = ga4w.get('yesterday', {})
    ga4_7d = ga4w.get('last_7_days', {})
    ga4_28d = ga4w.get('last_28_days', {})
    gsc_7d = gscw.get('last_7_days', {})
    gsc_28d = gscw.get('last_28_days', {})
    we_7d = wew.get('last_7_days', {})
    we_28d = wew.get('last_28_days', {})
    we_intel = wefact.get('finance_intelligence', {})

    ga4_sessions = snap.get('ga4_sessions_7d', 0)
    wefact_total = snap.get('wefact_invoice_total_28d', 0)
    wefact_quotes = snap.get('wefact_quotes_28d', 0)
    ads_value = snap.get('ads_value_28d', 0)
    leads_total = db.get('total_leads', 0)
    brevo_credits = brevo.get('credits_remaining', 0)
    campaigns = brevo.get('kpi', {}).get('total_campaigns', 0)
    ads_7d = adsw.get('last_7_days', {})
    ads_28d = adsw.get('last_28_days', {})

    traffic_kpi_html = f'''<div class="sg">
{card("Vandaag verkeer", ga4_today.get('sessions_fmt', fmt_num(ga4_today.get('sessions', 0))), f"gisteren {ga4_yesterday.get('sessions_fmt', fmt_num(ga4_yesterday.get('sessions', 0)))} · {trend_label(ga4_today.get('sessions', 0), ga4_yesterday.get('sessions', 0))}", "sc-c")}
{card("GSC clicks 7d", gsc_7d.get('clicks_fmt', fmt_num(gsc_7d.get('clicks', 0))), f"28d {gsc_28d.get('clicks_fmt', fmt_num(gsc_28d.get('clicks', 0)))} · CTR {gsc_28d.get('ctr_fmt', '—')}", "sc-g")}
{card("Traffic 7d", ga4_7d.get('sessions_fmt', fmt_num(ga4_7d.get('sessions', ga4_sessions))), f"28d {ga4_28d.get('sessions_fmt', fmt_num(ga4_28d.get('sessions', 0)))} · users {ga4_28d.get('active_users_fmt', '—')}", "sc-c")}
{card("PMax 7d", pmax.get('roas', '—'), f"spend {ads_7d.get('cost_eur', '—')} · value {ads_7d.get('value_eur', '—')}", "sc-c")}
{card("Wefact 28d", we_28d.get('invoice_total_fmt', fmt_num(wefact_total)), f"7d {we_7d.get('invoice_total_fmt', '—')} · {we_28d.get('quote_count_fmt', fmt_num(wefact_quotes))} offertes", "sc-g")}
</div>'''

    sources = [
        ('Google Search Console', 'GSC', snap.get('gsc_fetched_at', ''), True),
        ('Google Analytics 4', 'GA4', snap.get('ga4_fetched_at', ''), ga4_sessions and ga4_sessions > 0),
        ('Wefact', 'Finance', snap.get('wefact_fetched_at', ''), wefact_total and wefact_total > 0),
        ('Google Ads', 'Ads', snap.get('ads_fetched_at', ''), True),
        ('Shopify', 'Orders', snap.get('shopify_fetched_at', ''), True),
        ('Brevo', 'Email', brevo.get('fetched_at', ''), brevo.get('brevo_ok', False)),
    ]
    src_rows = ''
    for name, stype, fetched, ok in sources:
        badge = '<span class="pill pill-g">OK</span>' if ok else '<span class="pill pill-w">CHECK</span>'
        ts = fmt_dt(fetched)
        src_rows += f'<tr><td data-label="Bron"><strong>{esc(name)}</strong></td><td data-label="Type">{esc(stype)}</td><td data-label="Status">{badge}</td><td data-label="Ververst" class="muted">{esc(ts)}</td></tr>'

    seo_html = ''
    topics = signals.get('topics', [])
    if topics:
        seo_rows = ''
        for t in topics[:8]:
            source = ', '.join(t.get('signal_sources', [])) if t.get('signal_sources') else t.get('source', '—')
            seo_rows += f'<tr><td data-label="Onderwerp / kans">{esc(t.get("title","?"))}</td><td data-label="Bron" class="muted">{esc(source or "—")}</td></tr>'
        seo_html = f'<div class="tw mobile-cards"><table><thead><tr><th>Onderwerp / kans</th><th>Bron</th></tr></thead><tbody>{seo_rows}</tbody></table></div>'
    else:
        seo_html = '<p class="muted">Geen SEO-kansen beschikbaar. Run source refresh.</p>'

    ops_status = ops.get('ops_status', 'unknown')
    ops_badge = 'badge-ok' if ops_status == 'ok' else 'badge-warn'
    brevo_kpi = brevo.get('kpi', {})

    traffic_rows = f'''
<tr><td data-label="Periode"><strong>Vandaag</strong></td><td data-label="Sessies">{esc(ga4_today.get('sessions_fmt', '—'))}</td><td data-label="Users">{esc(ga4_today.get('active_users_fmt', '—'))}</td><td data-label="Clicks">{esc(gscw.get('today', {}).get('clicks_fmt', '—'))}</td><td data-label="Impressions">{esc(gscw.get('today', {}).get('impressions_fmt', '—'))}</td><td data-label="CTR">{esc(gscw.get('today', {}).get('ctr_fmt', '—'))}</td><td data-label="Trend" class="muted">{trend_label(ga4_today.get('sessions', 0), ga4_yesterday.get('sessions', 0), ' vs gister')}</td></tr>
<tr><td data-label="Periode"><strong>Gisteren</strong></td><td data-label="Sessies">{esc(ga4_yesterday.get('sessions_fmt', '—'))}</td><td data-label="Users">{esc(ga4_yesterday.get('active_users_fmt', '—'))}</td><td data-label="Clicks">{esc(gscw.get('yesterday', {}).get('clicks_fmt', '—'))}</td><td data-label="Impressions">{esc(gscw.get('yesterday', {}).get('impressions_fmt', '—'))}</td><td data-label="CTR">{esc(gscw.get('yesterday', {}).get('ctr_fmt', '—'))}</td><td data-label="Trend" class="muted">Referentie</td></tr>
<tr><td data-label="Periode"><strong>Last 7 days</strong></td><td data-label="Sessies">{esc(ga4_7d.get('sessions_fmt', '—'))}</td><td data-label="Users">{esc(ga4_7d.get('active_users_fmt', '—'))}</td><td data-label="Clicks">{esc(gsc_7d.get('clicks_fmt', '—'))}</td><td data-label="Impressions">{esc(gsc_7d.get('impressions_fmt', '—'))}</td><td data-label="CTR">{esc(gsc_7d.get('ctr_fmt', '—'))}</td><td data-label="Trend" class="muted">{trend_label(ga4_7d.get('sessions', 0), ga4_28d.get('sessions', 0) / 4 if ga4_28d.get('sessions') else 0, ' vs 28d avg')}</td></tr>
<tr><td data-label="Periode"><strong>Last 28 days</strong></td><td data-label="Sessies">{esc(ga4_28d.get('sessions_fmt', '—'))}</td><td data-label="Users">{esc(ga4_28d.get('active_users_fmt', '—'))}</td><td data-label="Clicks">{esc(gsc_28d.get('clicks_fmt', '—'))}</td><td data-label="Impressions">{esc(gsc_28d.get('impressions_fmt', '—'))}</td><td data-label="CTR">{esc(gsc_28d.get('ctr_fmt', '—'))}</td><td data-label="Trend" class="muted">Basislijn</td></tr>
'''

    ads_rows = f'''
<tr><td data-label="Periode"><strong>Vandaag</strong></td><td data-label="Spend">{esc(adsw.get('today', {}).get('cost_eur', '—'))}</td><td data-label="Value">{esc(adsw.get('today', {}).get('value_eur', '—'))}</td><td data-label="Clicks">{esc(str(adsw.get('today', {}).get('clicks', '—')))}</td><td data-label="CTR">{esc(adsw.get('today', {}).get('ctr', '—'))}</td><td data-label="Conversies">{esc(str(adsw.get('today', {}).get('conversions', '—')))}</td></tr>
<tr><td data-label="Periode"><strong>Gisteren</strong></td><td data-label="Spend">{esc(adsw.get('yesterday', {}).get('cost_eur', '—'))}</td><td data-label="Value">{esc(adsw.get('yesterday', {}).get('value_eur', '—'))}</td><td data-label="Clicks">{esc(str(adsw.get('yesterday', {}).get('clicks', '—')))}</td><td data-label="CTR">{esc(adsw.get('yesterday', {}).get('ctr', '—'))}</td><td data-label="Conversies">{esc(str(adsw.get('yesterday', {}).get('conversions', '—')))}</td></tr>
<tr><td data-label="Periode"><strong>Last 7 days</strong></td><td data-label="Spend">{esc(ads_7d.get('cost_eur', '—'))}</td><td data-label="Value">{esc(ads_7d.get('value_eur', '—'))}</td><td data-label="Clicks">{esc(str(ads_7d.get('clicks', '—')))}</td><td data-label="CTR">{esc(ads_7d.get('ctr', '—'))}</td><td data-label="Conversies">{esc(str(ads_7d.get('conversions', '—')))}</td></tr>
<tr><td data-label="Periode"><strong>Last 28 days</strong></td><td data-label="Spend">{esc(ads_28d.get('cost_eur', '—'))}</td><td data-label="Value">{esc(ads_28d.get('value_eur', '—'))}</td><td data-label="Clicks">{esc(str(ads_28d.get('clicks', '—')))}</td><td data-label="CTR">{esc(ads_28d.get('ctr', '—'))}</td><td data-label="Conversies">{esc(str(ads_28d.get('conversions', '—')))}</td></tr>
'''

    traffic_insights = f'''
    <div class="insight-grid">
      <div class="insight-card">
        <strong>Traffic trend</strong>
        <div class="mini">Vandaag {esc(ga4_today.get('sessions_fmt', '—'))} sessies tegenover gisteren {esc(ga4_yesterday.get('sessions_fmt', '—'))}. {esc(trend_label(ga4_today.get('sessions', 0), ga4_yesterday.get('sessions', 0), ' vs gister'))}.</div>
      </div>
      <div class="insight-card">
        <strong>Organic signal</strong>
        <div class="mini">GSC pakt {esc(gsc_7d.get('clicks_fmt', '—'))} clicks in 7 dagen bij {esc(gsc_28d.get('ctr_fmt', '—'))} CTR over 28 dagen.</div>
      </div>
      <div class="insight-card">
        <strong>PMax pulse</strong>
        <div class="mini">Spend {esc(ads_7d.get('cost_eur', '—'))}, value {esc(ads_7d.get('value_eur', '—'))}, ROAS {esc(pmax.get('roas', '—'))} op {esc(pmax.get('campaign_name', '—'))}.</div>
      </div>
      <div class="insight-card">
        <strong>Finance pulse</strong>
        <div class="mini">Wefact 28d {esc(we_28d.get('invoice_total_fmt', '—'))}, open {esc(we_28d.get('open_outstanding_fmt', '—'))}, follow-up {esc(we_intel.get('quote_followup_count_fmt', '0'))} offertes.</div>
      </div>
    </div>
    '''

    pmax_asset_rows = ''
    for ag in pmax.get('asset_groups', [])[:5]:
        pmax_asset_rows += f"<tr><td data-label='Naam'><strong>{esc(ag.get('name', '-'))}</strong></td><td data-label='Status'>{esc(ag.get('status', '-'))}</td><td data-label='Spend'>{esc(ag.get('cost_eur', '—'))}</td><td data-label='Value'>{esc(ag.get('value_eur', '—'))}</td><td data-label='Clicks'>{esc(str(ag.get('clicks', '—')))}</td><td data-label='Conversies'>{esc(str(ag.get('conversions', '—')))}</td></tr>"
    if not pmax_asset_rows:
        pmax_asset_rows = '<tr><td data-label="Status" colspan="6" class="muted">Geen PMax asset group data.</td></tr>'

    dashboard_ai_items = [
        {
            'title': 'Focus de contentmachine op thuisbatterij-money pages',
            'pill': 'revenue',
            'pill_class': 'pill-g',
            'text': 'De hoogste business-fit zit nu op thuisbatterij + Deye-combi’s. Eerst deze money pages domineren, daarna pas verbreden naar randtopics.',
        },
        {
            'title': 'Gebruik Wefact als waarheid voor omzet',
            'pill': 'finance',
            'pill_class': 'pill-c',
            'text': f"Wefact toont nu {we_28d.get('invoice_total_fmt', fmt_num(wefact_total))} in 28 dagen. Gebruik finance-truth als stuurlaag voor prioriteit en opvolging, niet alleen verkeer of Ads.",
        },
        {
            'title': 'PMax pas opschalen na betere landingsfit',
            'pill': 'ads',
            'pill_class': 'pill-w',
            'text': f"PMax draait op spend {ads_7d.get('cost_eur', '—')} en value {ads_7d.get('value_eur', '—')}. Eerst betere landing pages en value messaging, daarna pas agressiever budgetten.",
        },
        {
            'title': 'Partner machine warm houden',
            'pill': 'partners',
            'pill_class': 'pill-c',
            'text': f"De partnerlaag laat {fmt_num(db.get('engagement', {}).get('total_clicks', 0))} clicks en {fmt_num(db.get('engagement', {}).get('total_replies', 0))} replies zien. Dat is nu een directe groeimotor en verdient dagelijks ritme.",
        },
    ]
    dashboard_ai_html = render_ai_recommendation_block(
        'Stuuradvies voor EcoHandel',
        'AI-duiding voor de hoofdcockpit: waar zit nu de meeste commerciële hefboom?',
        dashboard_ai_items,
    )

    body = f'''
<div class="hero">
  <div class="ey">Dashboard</div>
  <h1>Econtrol Room</h1>
  <div class="sub">Centrale cockpit — verkeer, zoekvraag, finance, partner campaign en stijgende lijn.</div>
  <div class="ts">Laatst ververst: {esc(fmt_dt(now))} · Ops: <span class="badge {ops_badge}">{esc(ops_status)}</span></div>
  {traffic_kpi_html}
</div>

<div class="g g12">
  <div class="p s7 stretch">
    <div class="ph"><div><div class="ey">Traffic snapshot</div><h2>Vandaag / gisteren / last 7 days / last 28 days</h2></div></div>
    <div class="tw mobile-cards"><table><thead><tr><th>Periode</th><th>GA4 sessies</th><th>Users</th><th>GSC clicks</th><th>Impr.</th><th>CTR</th><th>Lijn</th></tr></thead><tbody>{traffic_rows}</tbody></table></div>
    {traffic_insights}
  </div>
  <div class="p s5 stretch">
    <div class="ph"><div><div class="ey">Business</div><h2>Finance + partners</h2></div></div>
    <div class="stack-tight">
      {card("Facturen 7d", we_7d.get('invoice_count_fmt', '—'), we_7d.get('invoice_total_fmt', '—'), "sc-g")}
      {card("Facturen 28d", we_28d.get('invoice_count_fmt', fmt_num(wefact_quotes)), we_28d.get('invoice_total_fmt', fmt_num(wefact_total)), "sc-g")}
      {card("Offerte follow-up", we_intel.get('quote_followup_count_fmt', '0'), we_intel.get('quote_followup_amount_fmt', '€0,00'), "sc-w")}
      {card("Achterstallig open", we_intel.get('overdue_invoice_count_fmt', '0'), we_intel.get('overdue_amount_fmt', '€0,00'), "sc-w")}
      {card("Partner leads", fmt_num(leads_total), f"{db.get('leads_with_email',0)} met email", "sc-c")}
      {card("Brevo campaign", fmt_num(campaigns), f"credits {fmt_num(brevo_credits)} · open {fmt_pct(brevo_kpi.get('open_rate', 0))}", "sc-c")}
    </div>
  </div>
</div>

<div class="g g12">
  {dashboard_ai_html}
</div>

<div class="g g12">
  <div class="p s7">
    <div class="ph"><div><div class="ey">Paid performance</div><h2>Google Ads + PMax</h2></div></div>
    <div class="tw mobile-cards"><table><thead><tr><th>Periode</th><th>Spend</th><th>Value</th><th>Clicks</th><th>CTR</th><th>Conv.</th></tr></thead><tbody>{ads_rows}</tbody></table></div>
  </div>
  <div class="p s5">
    <div class="ph"><div><div class="ey">PMax</div><h2>Actieve campagne</h2></div></div>
    <div class="sg" style="grid-template-columns:1fr">
      {card("Campagne", pmax.get('campaign_name', '—'), pmax.get('status', '—'), "sc-c")}
      {card("ROAS 7d", pmax.get('roas', '—'), f"CPA {pmax.get('cpa_eur', '—')} · value {pmax.get('value_eur', '—')}", "sc-g")}
      {card("Clicks / impr.", pmax.get('clicks', '—'), f"impr. {pmax.get('impressions', '—')} · conv. {pmax.get('conversions', '—')}", "sc-c")}
    </div>
    <div class="note"><strong>Asset groups</strong><div class="tw mobile-cards"><table><thead><tr><th>Naam</th><th>Status</th><th>Spend</th><th>Value</th><th>Clicks</th><th>Conv.</th></tr></thead><tbody>{pmax_asset_rows}</tbody></table></div></div>
  </div>
</div>

<div class="g g12">
  <div class="p s7">
    <div class="ph"><div><div class="ey">Databronnen</div><h2>Live koppelingen</h2></div></div>
    <div class="tw mobile-cards"><table><thead><tr><th>Bron</th><th>Type</th><th>Status</th><th>Laatst</th></tr></thead><tbody>{src_rows}</tbody></table></div>
  </div>
  <div class="p s5">
    <div class="ph"><div><div class="ey">Finance</div><h2>Wefact snapshot</h2></div></div>
    <div class="note"><strong>Vensters</strong><ul>
      <li>Vandaag: {esc(wew.get('today', {}).get('invoice_total_fmt', '—'))} · {esc(wew.get('today', {}).get('invoice_count_fmt', '—'))} facturen</li>
      <li>Gisteren: {esc(wew.get('yesterday', {}).get('invoice_total_fmt', '—'))} · {esc(wew.get('yesterday', {}).get('invoice_count_fmt', '—'))} facturen</li>
      <li>7d: {esc(we_7d.get('invoice_total_fmt', '—'))} · {esc(we_7d.get('quote_count_fmt', '—'))} offertes</li>
      <li>28d: {esc(we_28d.get('invoice_total_fmt', '—'))} · open {esc(we_28d.get('open_outstanding_fmt', '—'))}</li>
    </ul></div>
    <div class="note"><strong>Finance signalen</strong><ul>
      <li>Offerte follow-up: {esc(we_intel.get('quote_followup_count_fmt', '0'))} · {esc(we_intel.get('quote_followup_amount_fmt', '€0,00'))}</li>
      <li>Achterstallig open: {esc(we_intel.get('overdue_invoice_count_fmt', '0'))} · {esc(we_intel.get('overdue_amount_fmt', '€0,00'))}</li>
      <li>Grootste debiteur: {esc(((we_intel.get('top_debtors') or [{}])[0]).get('company', '—'))} · {esc(((we_intel.get('top_debtors') or [{}])[0]).get('open_amount_fmt', '€0,00'))}</li>
    </ul></div>
    <div class="note"><strong>Brevo partner campaign</strong><ul>
      <li>Credits: {fmt_num(brevo_credits)}</li>
      <li>Campagnes: {campaigns}</li>
      <li>Open rate: {fmt_pct(brevo_kpi.get("open_rate", 0))}</li>
      <li>Click rate: {fmt_pct(brevo_kpi.get("click_rate", 0))}</li>
    </ul></div>
  </div>
</div>

<div class="g g12">
  <div class="p s12">
    <div class="ph"><div><div class="ey">SEO opportunities</div><h2>Content kansen uit data</h2></div></div>
    {seo_html}
  </div>
</div>
'''

    return shell('Dashboard', 'Centrale cockpit', 'Dashboard', 'dashboard', body)


# ──────────────────────────────────────────────
# PAGE 2: WORKFLOWS
# ──────────────────────────────────────────────
def build_workflows() -> str:
    registry = load_json(STATE / 'workflow-registry.json')
    ops = load_json(STATE / 'ops-status.json')
    health = load_json(STATE / 'workflow-health.json')
    cron_data = load_json(STATE / 'openclaw-crons.json')

    now = utc_now()
    items = registry.get('items', [])

    def status_pill(s):
        s = str(s).lower()
        if s in ('ok', 'success', 'ready', 'active'):
            return f'<span class="pill pill-g">{esc(s)}</span>'
        if s in ('dry_run', 'pending'):
            return f'<span class="pill pill-c">{esc(s)}</span>'
        if s in ('blocked', 'error', 'failed'):
            return f'<span class="pill pill-r">{esc(s)}</span>'
        return f'<span class="pill pill-s">{esc(s)}</span>'

    def workflow_card(w):
        return f'''<div class="list-card">
  <strong>{esc(w.get("name", w.get("id", "?")))}</strong>
  <div class="meta">{status_pill(w.get("status", "?"))}<span class="pill pill-s">{esc(w.get("mode", "-"))}</span><span class="pill pill-s">{esc(w.get("owner", "-"))}</span></div>
  <div class="desc">{esc(w.get("description", ""))}</div>
  <div class="desc"><span class="mono">{esc(w.get("id", "?"))}</span> · laatste run {esc(fmt_dt(w.get("last_run")))}</div>
</div>'''

    def cron_card(c):
        enabled_pill = '<span class="pill pill-g">live</span>' if c.get('enabled') else '<span class="pill pill-s">paused</span>'
        status = status_pill(c.get('status', 'unknown'))
        next_run = fmt_dt(c.get('next_run')) if c.get('next_run') else '—'
        return f'''<div class="list-card">
  <strong>{esc(c.get("name", "?"))}</strong>
  <div class="meta">{enabled_pill}{status}<span class="pill pill-s">{esc(c.get("schedule", "-"))}</span></div>
  <div class="desc">{esc(c.get("note", ""))}</div>
  <div class="desc">volgende run {esc(next_run)}</div>
</div>'''

    item_map = {i.get('id', ''): i for i in items}
    sections_map = {
        'Core loop': ['ops_cycle', 'source_refresh', 'state_update', 'dashboard_render', 'queue_render', 'workflow_state_build', 'workflow_render', 'cron_health'],
        'Content & publishing': ['queue_scoring', 'specialist_trigger_generation', 'publish_readiness', 'publish_execute'],
        'Partner & deploy': ['partner_campaign_render', 'deploy_sync', 'finance_sync'],
    }

    sections = ''
    for label, ids in sections_map.items():
        cards = ''.join(workflow_card(item_map[wid]) for wid in ids if wid in item_map)
        if not cards:
            continue
        sections += f'''<div class="p" style="margin-bottom:14px">
<div class="ph"><div><div class="ey">Workflow lane</div><h2>{esc(label)}</h2></div></div>
<div class="card-grid">{cards}</div>
</div>'''

    completed = ops.get('completed_steps', [])
    failed = ops.get('failed_steps', [])
    ops_badge = 'badge-ok' if not failed else 'badge-warn'

    active_workflows = sum(1 for item in items if item.get('enabled'))
    paused_workflows = sum(1 for item in items if not item.get('enabled'))
    blocked_workflows = sum(1 for item in items if str(item.get('status', '')).lower() in {'blocked', 'error', 'failed'})
    manual_workflows = sum(1 for item in items if item.get('mode') == 'manual')

    cron_items = cron_data.get('items', [])
    cron_groups = {}
    for cron in cron_items:
        cron_groups.setdefault(cron.get('group', 'Overig'), []).append(cron)

    cron_sections = ''
    for group, group_items in cron_groups.items():
        cards = ''.join(cron_card(c) for c in group_items)
        cron_sections += f'''<div class="p" style="margin-bottom:14px">
<div class="ph"><div><div class="ey">Cron group</div><h2>{esc(group)}</h2></div></div>
<div class="card-grid">{cards}</div>
</div>'''

    step_rows = ''.join(
        f'<tr><td data-label="Stap"><strong>{esc(step.get("step", "?"))}</strong></td><td data-label="Status">{"OK" if step.get("ok") else "FAIL"}</td><td data-label="Output" class="muted">{esc((step.get("stdout") or "—").splitlines()[0][:120])}</td></tr>'
        for step in ops.get('step_logs', [])
    )

    workflows_ai_items = [
        {
            'title': 'Hou de machine klein en waarheidsgetrouw',
            'pill': 'ops',
            'pill_class': 'pill-g',
            'text': 'Alleen workflows tonen die echt bijdragen aan EcoHandel. Minder lanes, minder ruis, meer vertrouwen in de cockpit.',
        },
        {
            'title': 'Finance Sync mag nu als live bouwsteen gelden',
            'pill': 'finance',
            'pill_class': 'pill-c',
            'text': 'Wefact is weer echt live. Gebruik die status ook verderop in automations voor follow-up, signalering en omzetcontext.',
        },
        {
            'title': 'Cronlaag strak houden op ritme, niet op volume',
            'pill': 'cron',
            'pill_class': 'pill-w',
            'text': 'Core heartbeat plus partner-slots is voorlopig genoeg. Voeg alleen nieuwe crons toe als timing echt exact moet zijn.',
        },
        {
            'title': 'Volgende stap: agent-acties bovenop deze workflows',
            'pill': 'next',
            'pill_class': 'pill-c',
            'text': 'De workflowlaag is nu schoon genoeg om later slimme triggers, opvolgadviezen en operator-actions erbovenop te bouwen.',
        },
    ]
    workflows_ai_html = render_ai_recommendation_block(
        'Advies voor de machine',
        'AI-duiding voor de operatiekant van EcoHandel: wat moet deze OS-laag vooral wel en juist niet doen?',
        workflows_ai_items,
    )

    body = f'''
<div class="hero">
  <div class="ey">Workflows</div>
  <h1>Machine overzicht</h1>
  <div class="sub">Clean overzicht van wat de Econtrol Room-machine echt draait: kernworkflows, live cronritme, partner slots en wat nog legacy of paused is.</div>
  <div class="ts">Ops cycle: <span class="badge {ops_badge}">{esc(ops.get("ops_status","?"))}</span> · Laatste run: {esc(fmt_dt(ops.get("last_run")))} · Stappen: {len(completed)}/{len(completed)+len(failed)}</div>
  <div class="card-grid" style="margin-top:16px">
    <div class="stat-card"><span class="k">Actieve workflows</span><span class="v">{active_workflows}</span><span class="n">Alles wat nu enabled staat in de registry.</span></div>
    <div class="stat-card"><span class="k">Manual / guarded</span><span class="v">{manual_workflows}</span><span class="n">Flows met bewuste handmatige of approval-gate.</span></div>
    <div class="stat-card"><span class="k">Blocked / error</span><span class="v">{blocked_workflows}</span><span class="n">Alleen echte aandachtspunten, geen oude ruis.</span></div>
    <div class="stat-card"><span class="k">Paused workflows</span><span class="v">{paused_workflows}</span><span class="n">Bekend maar nu niet actief in de machine.</span></div>
  </div>
</div>

{sections}

<div class="g g12">
  {workflows_ai_html}
</div>

<div class="g g12">
  <div class="p s7">
    <div class="ph"><div><div class="ey">Ops cycle</div><h2>Laatste runstappen</h2></div></div>
    <div class="tw mobile-cards"><table><thead><tr><th>Stap</th><th>Status</th><th>Output</th></tr></thead><tbody>{step_rows}</tbody></table></div>
  </div>
  <div class="p s5">
    <div class="ph"><div><div class="ey">Focus</div><h2>Wat hier bewust niet staat</h2></div></div>
    <div class="note"><strong>Opgeschoond</strong><ul>
      <li>Geen verouderde EcoDash-verwijzingen meer als primaire cockpitlogica</li>
      <li>Geen oude placeholder-cronlijstjes meer</li>
      <li>Geen dump van alle state-files zonder context</li>
      <li>Alleen workflows die nu echt onderdeel zijn van de machine of bewust paused staan</li>
    </ul></div>
  </div>
</div>

{cron_sections}
'''

    return shell('Workflows', 'Operaties & automatisering', 'Workflows', 'workflows', body)


# ──────────────────────────────────────────────
# PAGE 3: SMART CONTENT QUEUE
# ──────────────────────────────────────────────
def build_queue() -> str:
    queue = load_json(QUEUE / 'SMART_CONTENT_QUEUE.json')
    health = load_json(STATE / 'queue-health.json')
    signals = load_json(STATE / 'source-signals.json')

    now = utc_now()

    top5 = queue.get('top_5_now', [])
    nextup = queue.get('next_up', [])
    watchlist = queue.get('watchlist', [])
    refresh = queue.get('refresh_first', [])

    # Published articles (Shopify Kennis blog)
    published = [
        {'title': 'Deye Smart Home Systeem: Alles Draadloos Aansturen via LoRa', 'date': '2026-03-23', 'status': 'live'},
        {'title': 'Deye Copilot: AI-gestuurd Energiebeheer voor je Thuisbatterij', 'date': '2026-03-23', 'status': 'live'},
        {'title': 'Deye Smart Wallbox: Slim Laden op Zonne-energie', 'date': '2026-03-23', 'status': 'live'},
        {'title': 'Deye vs Growatt: Vergelijking voor Installateurs', 'date': '2026-03-23', 'status': 'live'},
        {'title': 'Deye LV vs HV Batterijsysteem: Wanneer Kies je Wat?', 'date': '2026-03-23', 'status': 'live'},
    ]

    def source_label(item):
        srcs = item.get('signal_sources') or []
        if srcs:
            return ', '.join(srcs[:3])
        return item.get('source') or item.get('primary_cluster') or '—'

    def render_topic_card(item):
        return f'''<div class="list-card">
  <strong>{esc(item.get("title", "?"))}</strong>
  <div class="meta"><span class="pill pill-g">{esc(item.get("priority_label", "focus"))}</span><span class="pill pill-s">{esc(item.get("content_type", item.get("intent", "content")))}</span><span class="pill pill-s">score {esc(str(item.get("total_score", "—")))}</span></div>
  <div class="desc">{esc(item.get("why_now") or item.get("recommended_next_step") or 'Nog zonder extra toelichting.')}</div>
  <div class="desc">bron: {esc(source_label(item))}</div>
</div>'''

    rec_cards = ''.join(render_topic_card(t) for t in top5[:5])
    next_cards = ''.join(render_topic_card(t) for t in nextup[:5])
    watch_cards = ''.join(render_topic_card(t) for t in watchlist[:5])

    # Published table
    pub_rows = ''.join(f'<tr><td data-label="Artikel">{esc(a["title"])}</td><td data-label="Datum">{esc(a["date"])}</td><td data-label="Status"><span class="pill pill-g">{esc(a["status"])}</span></td></tr>' for a in published)

    # Health stats
    total = health.get('total_items', 0)
    by_lane = health.get('by_lane', {})

    queue_ai_items = []
    if top5:
        queue_ai_items.append({
            'title': f"Zet direct druk op: {top5[0].get('title', 'topprioriteit')}",
            'pill': 'p1',
            'pill_class': 'pill-g',
            'text': top5[0].get('why_now') or 'Dit is nu het sterkste content-signaal in de queue.',
        })
    if len(top5) > 1:
        queue_ai_items.append({
            'title': 'Bundel de battery buying-intent pages',
            'pill': 'cluster',
            'pill_class': 'pill-c',
            'text': 'De bovenste queue draait sterk om thuisbatterij-keuze, Deye/Marstek en combinaties. Bouw deze pages als een hechte commerciële cluster met onderlinge interne links.',
        })
    queue_ai_items.append({
        'title': 'Refreshwerk alleen doen als het omzet of SEO-structuur raakt',
        'pill': 'guardrail',
        'pill_class': 'pill-w',
        'text': 'Laat de queue niet vollopen met onderhoudsruis. Alleen refresh-taken prioriteren als ze title/meta, ranking of een money page raken.',
    })
    queue_ai_items.append({
        'title': 'Gebruik published lane als bewijs, niet als trofeeënkast',
        'pill': 'ops',
        'pill_class': 'pill-c',
        'text': 'Elke live kennispagina moet doorlinken naar een relevante product- of vergelijking-lane. Anders blijft het losse content in plaats van omzetmachine.',
    })
    queue_ai_html = render_ai_recommendation_block(
        'Advies voor contentprioriteit',
        'AI-duiding voor wat de queue nú moet doen om EcoHandel sneller te laten groeien.',
        queue_ai_items,
    )

    body = f'''
<div class="hero">
  <div class="ey">Smart content queue</div>
  <h1>Smart content queue</h1>
  <div class="sub">Zelfde cockpitstijl als dashboard en partners: compacte lane-kaarten, duidelijke volgorde en alleen de content die nu telt.</div>
  <div class="ts">Items in queue: {total} · Top 5: {by_lane.get("top_5_now",0)} · Next up: {by_lane.get("next_up",0)} · Watchlist: {by_lane.get("watchlist",0)}</div>
  <div class="card-grid" style="margin-top:16px">
    <div class="stat-card"><span class="k">Top 5 now</span><span class="v">{by_lane.get("top_5_now",0)}</span><span class="n">Artikelen met directe commerciële of SEO-prio.</span></div>
    <div class="stat-card"><span class="k">Next up</span><span class="v">{by_lane.get("next_up",0)}</span><span class="n">Klaar om door te schuiven zodra lane 1 leeg is.</span></div>
    <div class="stat-card"><span class="k">Watchlist</span><span class="v">{by_lane.get("watchlist",0)}</span><span class="n">Nog volgen, nog niet pushen.</span></div>
    <div class="stat-card"><span class="k">Published</span><span class="v">{len(published)}</span><span class="n">Live kennisartikelen in de huidige stack.</span></div>
  </div>
</div>

<div class="g g12">
  <div class="p s12">
    <div class="ph"><div><div class="ey">Aanbevolen</div><h2>Top 5 — nu schrijven</h2></div><span class="badge badge-ok">PRIORITEIT</span></div>
    <div class="card-grid">{rec_cards if rec_cards else '<div class="list-card muted">Geen items in queue. Run source refresh.</div>'}</div>
  </div>
</div>

<div class="g g12">
  {queue_ai_html}
</div>

<div class="g g12">
  <div class="p s7">
    <div class="ph"><div><div class="ey">Volgende</div><h2>Next up</h2></div></div>
    <div class="card-grid">{next_cards if next_cards else '<div class="list-card muted">Geen next up items.</div>'}</div>
  </div>
  <div class="p s5">
    <div class="ph"><div><div class="ey">Watchlist</div><h2>Later bekijken</h2></div></div>
    <div class="card-grid">{watch_cards if watch_cards else '<div class="list-card muted">Geen watchlist items.</div>'}</div>
  </div>
</div>

<div class="g g12">
  <div class="p s12">
    <div class="ph"><div><div class="ey">Gepubliceerd</div><h2>Geplaatste kennisartikelen</h2></div><span class="badge badge-ok">{len(published)} LIVE</span></div>
    <div class="tw mobile-cards"><table><thead><tr><th>Artikel</th><th>Datum</th><th>Status</th></tr></thead><tbody>{pub_rows}</tbody></table></div>
  </div>
</div>
'''

    return shell('Smart Content Queue', 'Content planning & artikelen', 'Queue', 'smart-content-queue', body)


# ──────────────────────────────────────────────
# SERVICE WORKER (cache-bust)
# ──────────────────────────────────────────────
def build_sw() -> str:
    return f'''// Auto-generated — v{VERSION}
// Network-first with no aggressive caching
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(
  caches.keys().then(keys => Promise.all(keys.map(k => caches.delete(k)))).then(() => self.clients.claim())
));
self.addEventListener("fetch", e => {{
  if (e.request.method !== "GET") return;
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
}});
'''


def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)

    print('▶ Building dashboard...')
    dashboard_html = build_dashboard()
    (BUILD / 'index.html').write_text(dashboard_html, encoding='utf-8')
    (BUILD / 'dashboard.html').write_text(dashboard_html, encoding='utf-8')

    print('▶ Building workflows...')
    (BUILD / 'workflows.html').write_text(build_workflows(), encoding='utf-8')

    print('▶ Building smart content queue...')
    (BUILD / 'smart-content-queue.html').write_text(build_queue(), encoding='utf-8')

    print('▶ Building service worker...')
    (BUILD / 'sw.js').write_text(build_sw(), encoding='utf-8')

    # Partner campaign page is built by its own renderer
    print('▶ Partner campaign page: run render_partner_campaign_page.py separately')

    for f in BUILD.glob('*.html'):
        print(f'  ✅ {f.name} ({f.stat().st_size:,} bytes)')
    print(f'  ✅ sw.js')
    print(f'✅ All pages built (version {VERSION})')


if __name__ == '__main__':
    main()
