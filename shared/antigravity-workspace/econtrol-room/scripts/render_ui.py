#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

BASE = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room')
BUILD_DIR = BASE / 'build'
ECODASH_DATA_DIR = BASE.parent / 'ecodash-v3' / 'dashboard' / 'data'


def load_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def utc_now_label() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')


def shell_head(title: str, page_title: str, description: str, extra_css: str = '') -> str:
    return f'''<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <meta name="theme-color" content="#07111d">
  <meta name="apple-mobile-web-app-title" content="EcoHandel.nl">
  <link rel="manifest" href="/app.webmanifest">
  <link rel="icon" href="/favicon.png?v=3" type="image/png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png?v=3">
  <link rel="apple-touch-icon-precomposed" href="/apple-touch-icon.png?v=3">
  <style>
    :root{{--bg:#06111d;--bg2:#091827;--panel:#0f2236;--panel2:#14314d;--panel3:#0b1b2b;--line:#21415c;--text:#e8f0f7;--muted:#8ea7be;--green:#22c55e;--amber:#f59e0b;--red:#ef4444;--cyan:#22d3ee;--blue:#38bdf8;--purple:#8b5cf6;--pink:#ec4899;--safe-top:env(safe-area-inset-top,0px);--safe-bottom:env(safe-area-inset-bottom,0px);--nav-h:76px;--radius:24px;}}
    *{{box-sizing:border-box}}
    html{{scroll-behavior:smooth;background:var(--bg)}}
    body{{margin:0;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,sans-serif;background:radial-gradient(circle at top right,#163857 0,#06111d 44%);color:var(--text);-webkit-font-smoothing:antialiased;padding-bottom:calc(var(--nav-h) + var(--safe-bottom) + 20px);overflow-x:hidden}}
    a{{color:inherit}}
    .app-shell{{max-width:1680px;margin:0 auto;padding:calc(16px + var(--safe-top)) 18px 0;overflow-x:hidden}}
    .topbar{{position:sticky;top:0;z-index:20;padding-top:8px;backdrop-filter:blur(20px)}}
    .topbar-inner{{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:14px 16px;border:1px solid rgba(255,255,255,.08);background:rgba(8,17,28,.78);border-radius:20px;box-shadow:0 14px 40px rgba(0,0,0,.22)}}
    .brand{{display:flex;align-items:center;gap:12px;min-width:0}}
    .brand-mark{{width:42px;height:42px;border-radius:14px;background:linear-gradient(135deg,#22d3ee,#8b5cf6 55%,#ec4899);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:900;box-shadow:0 10px 24px rgba(34,211,238,.25)}}
    .brand-copy{{min-width:0}}
    .brand-eyebrow{{font-size:11px;color:var(--cyan);text-transform:uppercase;letter-spacing:.12em;font-weight:800}}
    .brand-title{{font-size:18px;font-weight:900;letter-spacing:-.03em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
    .brand-sub{{font-size:12px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
    .top-actions{{display:flex;align-items:center;gap:10px;flex-shrink:0}}
    .page-pill{{display:inline-flex;align-items:center;padding:8px 12px;border-radius:999px;background:rgba(34,211,238,.08);border:1px solid rgba(34,211,238,.18);color:var(--cyan);font-size:12px;font-weight:800;letter-spacing:.04em}}
    .wrap{{padding:18px 0 0}}
    .desktop-nav{{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 18px}}
    .desktop-nav a{{display:inline-flex;align-items:center;gap:8px;padding:10px 14px;border-radius:999px;text-decoration:none;font-weight:800;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.03);color:#dbe8f5}}
    .desktop-nav a.is-active{{background:#16a34a;color:#fff;border-color:rgba(22,163,74,.35);box-shadow:0 8px 20px rgba(22,163,74,.22)}}
    .hero-card,.panel{{background:linear-gradient(180deg,var(--panel) 0,var(--panel2) 100%);border:1px solid var(--line);border-radius:var(--radius);box-shadow:0 20px 70px rgba(0,0,0,.28)}}
    .hero-card{{padding:22px}}
    .eyebrow{{font-size:11px;color:var(--cyan);text-transform:uppercase;letter-spacing:.1em;font-weight:800}}
    h1{{margin:8px 0 10px;font-size:clamp(34px,7vw,54px);line-height:.96;letter-spacing:-.05em}}
    .subhead{{color:var(--muted);line-height:1.6;max-width:900px}}
    .timestamp{{color:var(--muted);font-size:13px;line-height:1.6}}
    .grid{{display:grid;grid-template-columns:repeat(12,1fr);gap:18px;margin-top:18px}}
    .span-4{{grid-column:span 4}} .span-5{{grid-column:span 5}} .span-6{{grid-column:span 6}} .span-7{{grid-column:span 7}} .span-8{{grid-column:span 8}} .span-12{{grid-column:span 12}}
    .panel{{padding:18px 18px 16px}}
    .panel-head{{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:16px}}
    h2{{margin:4px 0 0;font-size:24px;letter-spacing:-.03em}}
    .status{{padding:8px 12px;border-radius:999px;font-size:12px;font-weight:900;text-transform:uppercase;letter-spacing:.06em}}
    .status-live{{background:rgba(34,197,94,.12);color:var(--green);border:1px solid rgba(34,197,94,.25)}}
    .status-seed{{background:rgba(34,211,238,.12);color:var(--cyan);border:1px solid rgba(34,211,238,.25)}}
    .status-warn{{background:rgba(245,158,11,.12);color:#fbbf24;border:1px solid rgba(245,158,11,.25)}}
    .hero-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:18px}}
    .hero-metric,.kpi-card{{padding:16px;border-radius:18px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06)}}
    .label,.kpi-label,.mini-label{{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em}}
    .value,.kpi-value{{font-size:26px;font-weight:900;margin-top:7px;letter-spacing:-.04em}}
    .muted{{color:var(--muted)}}
    .sub{{color:var(--muted);font-size:14px;line-height:1.55;margin-top:4px}}
    .stack{{display:grid;gap:10px;margin:0;padding-left:18px}}
    .table-wrap{{overflow:auto;margin:0 -4px;padding:0 4px;-webkit-overflow-scrolling:touch}}
    table{{width:100%;border-collapse:collapse;min-width:0}}
    th,td{{padding:10px 8px;border-top:1px solid var(--line);text-align:left;vertical-align:top;word-break:break-word}}
    th{{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}}
    .pill{{display:inline-flex;align-items:center;padding:5px 10px;border-radius:999px;font-size:11px;font-weight:900;letter-spacing:.06em;text-transform:uppercase;border:1px solid rgba(255,255,255,.08)}}
    .pill-soft{{background:rgba(255,255,255,.05);color:var(--muted)}}
    .pill-live{{background:rgba(34,197,94,.16);color:#86efac}}
    .pill-warn{{background:rgba(245,158,11,.16);color:#fcd34d}}
    .pill-accent{{background:rgba(34,211,238,.12);color:var(--cyan)}}
    .empty{{color:var(--muted)}}
    .bottom-nav{{position:fixed;left:0;right:0;bottom:0;z-index:40;padding:10px 14px calc(10px + var(--safe-bottom));pointer-events:none}}
    .bottom-nav-inner{{max-width:720px;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:10px;padding:10px;border-radius:24px;background:rgba(8,17,28,.88);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.08);box-shadow:0 -10px 40px rgba(0,0,0,.28);pointer-events:auto}}
    .bottom-nav a{{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;padding:10px 8px;border-radius:16px;text-decoration:none;color:#cfe2f3;font-size:11px;font-weight:800;letter-spacing:.04em}}
    .bottom-nav a .icon{{font-size:18px;line-height:1}}
    .bottom-nav a.is-active{{background:linear-gradient(135deg,rgba(34,211,238,.18),rgba(139,92,246,.18));color:#fff;border:1px solid rgba(255,255,255,.08)}}
    .install-hint{{display:none}}
    .sr-only{{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}}
    {extra_css}
    @media (max-width:1180px){{.grid,.hero-grid{{grid-template-columns:1fr}} .span-4,.span-5,.span-6,.span-7,.span-8,.span-12{{grid-column:span 1}} .desktop-nav{{display:none}} h2{{font-size:22px}} .topbar-inner{{align-items:flex-start;flex-direction:column}} .brand-sub{{white-space:normal;overflow:visible;text-overflow:clip}} .top-actions{{width:100%}} .page-pill{{width:100%;justify-content:center}} table{{min-width:0}} th,td{{font-size:13px;padding:10px 6px}}}}
    @media (min-width:1181px){{.bottom-nav{{display:none}} .app-shell{{padding-left:28px;padding-right:28px}}}}
  </style>
  <script>
    if ('serviceWorker' in navigator) {{
      window.addEventListener('load', function() {{ navigator.serviceWorker.register('/sw.js').catch(function(){{}}); }});
    }}
  </script>
</head>'''


def shell_top(page_title: str, page_subtitle: str, active: str) -> str:
    return f'''<div class="topbar">
      <div class="topbar-inner">
        <div class="brand">
          <div class="brand-mark">EH</div>
          <div class="brand-copy">
            <div class="brand-eyebrow">Mission board</div>
            <div class="brand-title">EcoHandel.nl</div>
            <div class="brand-sub">{escape(page_subtitle)}</div>
          </div>
        </div>
        <div class="top-actions"><span class="page-pill">{escape(page_title)}</span></div>
      </div>
    </div>
    <div class="wrap">
      <nav class="desktop-nav" aria-label="Hoofdnavigatie">
        <a href="/" class="{'is-active' if active == 'dashboard' else ''}">Dashboard</a>
        <a href="/smart-content-queue.html" class="{'is-active' if active == 'queue' else ''}">Queue</a>
        <a href="/workflows.html" class="{'is-active' if active == 'workflows' else ''}">Workflows</a>
        <a href="/partner-campaign.html" class="{'is-active' if active == 'partner_campaign' else ''}">Partners</a>
      </nav>'''


def shell_bottom(active: str) -> str:
    return f'''<nav class="bottom-nav" aria-label="App navigatie">
      <div class="bottom-nav-inner">
        <a href="/" class="{'is-active' if active == 'dashboard' else ''}"><span class="icon">⌂</span><span>Dashboard</span></a>
        <a href="/smart-content-queue.html" class="{'is-active' if active == 'queue' else ''}"><span class="icon">◎</span><span>Queue</span></a>
        <a href="/workflows.html" class="{'is-active' if active == 'workflows' else ''}"><span class="icon">◈</span><span>Flows</span></a>
        <a href="/partner-campaign.html" class="{'is-active' if active == 'partner_campaign' else ''}"><span class="icon">✉</span><span>Partners</span></a>
      </div>
    </nav>'''


def shell_page(title: str, page_title: str, page_subtitle: str, description: str, active: str, content: str, extra_css: str = '', extra_js: str = '') -> str:
    return f'''<!doctype html>
<html lang="nl">
{shell_head(title, page_title, description, extra_css)}
<body>
  <div class="app-shell">
    {shell_top(page_title, page_subtitle, active)}
    {content}
  </div>
  {shell_bottom(active)}
  {extra_js}
</body>
</html>'''


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
