#!/usr/bin/env python3
from __future__ import annotations

from html import escape
from pathlib import Path

from render_ui import BASE, BUILD_DIR, load_json, shell_page, utc_now_label, write_text

QUEUE_PATH = BASE / 'queue' / 'SMART_CONTENT_QUEUE.json'
REFRESH_PATH = BASE / 'queue' / 'REFRESH_QUEUE.json'
OUTPUT_PATH = BUILD_DIR / 'smart-content-queue.html'


def item_card(item: dict) -> str:
    return f'''<article class="queue-card">
      <div class="queue-top"><span class="queue-score">{item.get('total_score', '-')}</span><div class="queue-tags"><span class="pill pill-live">{escape(item.get('priority_label', '-'))}</span><span class="pill pill-soft">{escape(item.get('content_type', '-'))}</span></div></div>
      <h3>{escape(item.get('title', 'Untitled'))}</h3>
      <p>{escape(item.get('why_now', ''))}</p>
      <div class="queue-foot">
        <div><span class="mini-label">Goal</span><strong>{escape(item.get('business_goal', '-'))}</strong></div>
        <div><span class="mini-label">Next</span><strong>{escape(item.get('recommended_next_step', '-'))}</strong></div>
        <div><span class="mini-label">Cluster</span><strong>{escape(item.get('primary_cluster', '-'))}</strong></div>
        <div><span class="mini-label">Confidence</span><strong>{int(round((item.get('confidence') or 0) * 100))}%</strong></div>
      </div>
    </article>'''


def refresh_card(item: dict) -> str:
    return f'''<article class="refresh-card">
      <div class="refresh-top"><span class="pill {'pill-warn' if item.get('severity') == 'high' else 'pill-accent'}">{escape(item.get('severity', '-'))}</span><span class="pill pill-soft">{escape(item.get('issue_type', '-'))}</span></div>
      <h3>{escape(item.get('url','-'))}</h3>
      <p>{escape(item.get('recommended_fix','-'))}</p>
    </article>'''


def lane_card(label: str, value: str, note: str) -> str:
    return f'''<article class="lane-card"><span class="lane-label">{escape(label)}</span><strong class="lane-value">{escape(value)}</strong><div class="lane-note">{escape(note)}</div></article>'''


def main() -> None:
    queue = load_json(QUEUE_PATH)
    refresh = load_json(REFRESH_PATH)

    top = ''.join(item_card(i) for i in queue.get('top_5_now', [])) or '<p class="empty">Geen top-5 items.</p>'
    next_up = ''.join(item_card(i) for i in queue.get('next_up', [])) or '<p class="empty">Geen next-up items.</p>'
    watch = ''.join(item_card(i) for i in queue.get('watchlist', [])) or '<p class="empty">Geen watchlist items.</p>'
    refresh_cards = ''.join(refresh_card(i) for i in refresh.get('items', [])) or '<p class="empty">Geen refresh items.</p>'
    lane_cards = ''.join([
        lane_card('Top 5', str(len(queue.get('top_5_now', []))), 'Wat nu telt'),
        lane_card('Next up', str(len(queue.get('next_up', []))), 'Wat hierna komt'),
        lane_card('Watchlist', str(len(queue.get('watchlist', []))), 'Nog volgen'),
        lane_card('Refresh', str(len(refresh.get('items', []))), 'Bestaande pagina’s fixen'),
    ])

    content = f'''
      <section class="hero-card">
        <div class="eyebrow">Queue</div>
        <h1>Smart Content Queue</h1>
        <div class="subhead">De prioriteitenmotor van EcoHandel. Niet alleen een lijstje, maar de commerciële volgorde van de machine: nu, hierna, later en refresh.</div>
        <div class="lane-grid">{lane_cards}</div>
        <div class="hero-note">Built {utc_now_label()} · Revenue-first blijft leidend · Refresh blijft bewust in beeld.</div>
      </section>
      <div class="grid">
        <section class="panel span-12"><div class="panel-head"><div><div class="eyebrow">Now</div><h2>Top 5 now</h2></div></div><div class="queue-grid">{top}</div></section>
        <section class="panel span-8"><div class="panel-head"><div><div class="eyebrow">Next lane</div><h2>Next up</h2></div></div><div class="queue-grid">{next_up}</div></section>
        <section class="panel span-4"><div class="panel-head"><div><div class="eyebrow">Later</div><h2>Watchlist</h2></div></div><div class="queue-grid queue-grid-single">{watch}</div></section>
        <section class="panel span-12"><div class="panel-head"><div><div class="eyebrow">Refresh</div><h2>Refresh queue</h2></div></div><div class="refresh-grid">{refresh_cards}</div></section>
      </div>
    '''

    extra_css = '''
    .lane-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-top:18px}
    .lane-card{padding:16px;border-radius:18px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06)}
    .lane-label{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}
    .lane-value{display:block;margin-top:8px;font-size:26px;letter-spacing:-.04em;color:var(--cyan)}
    .lane-note{margin-top:6px;color:var(--muted);font-size:13px;line-height:1.5}
    .hero-note{margin-top:14px;color:var(--muted);font-size:13px;line-height:1.6}
    .queue-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
    .queue-grid-single{grid-template-columns:1fr}
    .refresh-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
    .queue-card,.refresh-card{padding:18px;border-radius:20px;background:linear-gradient(180deg,rgba(7,19,31,.8),rgba(10,24,40,.95));border:1px solid rgba(255,255,255,.07);min-width:0}
    .queue-top,.refresh-top{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}
    .queue-score{width:54px;height:54px;border-radius:16px;background:linear-gradient(135deg,rgba(34,211,238,.22),rgba(139,92,246,.22));display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:900;flex:0 0 auto}
    .queue-tags{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
    .queue-card h3,.refresh-card h3{margin:14px 0 10px;font-size:21px;letter-spacing:-.03em;line-height:1.2;overflow-wrap:anywhere}
    .queue-card p,.refresh-card p{margin:0;color:var(--muted);line-height:1.6;overflow-wrap:anywhere}
    .queue-foot{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-top:14px;padding-top:12px;border-top:1px solid rgba(255,255,255,.06)}
    .queue-foot strong{font-size:13px}
    @media (max-width:1180px){.lane-grid,.queue-grid,.refresh-grid,.queue-foot{grid-template-columns:1fr}}
    '''

    html = shell_page(
        title='EcoHandel.nl — Smart Content Queue',
        page_title='Queue',
        page_subtitle='Prioriteiten, refresh en contentkansen',
        description='Smart Content Queue voor EcoHandel.nl',
        active='queue',
        content=content,
        extra_css=extra_css,
    )
    write_text(OUTPUT_PATH, html)
    print(f'Wrote {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
