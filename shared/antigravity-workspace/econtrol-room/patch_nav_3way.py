from pathlib import Path

def nav(active):
    def cls(name):
        return 'nav-live' if active == name else 'nav-dark'
    return f'''
<div class="nav">
  <a href="/" class="{cls('dashboard')}">Dashboard</a>
  <a href="/smart-content-queue.html" class="{cls('queue')}">Smart Content Queue</a>
  <a href="/agents.html" class="{cls('agents')}">Agents</a>
</div>
'''

def patch(path_str, active):
    p = Path(path_str)
    html = p.read_text()
    html = html.replace('<body>', '<body>')
    # remove old nav blocks if present
    start = html.find('<div class="nav">')
    if start != -1:
        end = html.find('</div>', start)
        if end != -1:
            html = html[:start] + html[end+6:]
    idx = html.find('<body>')
    if idx != -1:
        html = html[:idx+6] + nav(active) + html[idx+6:]
    # inject nav styles if missing
    if '.nav{' not in html:
        html = html.replace('</style>', '.nav{max-width:1680px;margin:0 auto;padding:16px 28px 0;display:flex;gap:12px;flex-wrap:wrap}.nav a{display:inline-flex;padding:10px 16px;border-radius:999px;text-decoration:none;font-weight:800;font-family:Inter,system-ui,sans-serif}.nav-dark{background:#0f2236;color:#e8f0f7;border:1px solid #21415c}.nav-live{background:#16a34a;color:#fff;box-shadow:0 6px 18px rgba(0,0,0,.15)}</style>')
    p.write_text(html)

patch('/var/www/html/control.ecohandel.nl/index.html', 'dashboard')
patch('/var/www/html/control.ecohandel.nl/smart-content-queue.html', 'queue')
patch('/var/www/html/control.ecohandel.nl/agents.html', 'agents')
print('patched 3-way nav')
