from pathlib import Path

def insert_nav(path_str, active):
    p = Path(path_str)
    html = p.read_text()
    nav = f'''
<div style="max-width:1680px;margin:0 auto;padding:16px 28px 0;">
  <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center">
    <a href="/" style="display:inline-flex;padding:10px 16px;border-radius:999px;{'background:#16a34a;color:#fff;box-shadow:0 6px 18px rgba(0,0,0,.15);' if active=='dashboard' else 'background:#0f2236;color:#e8f0f7;border:1px solid #21415c;'}text-decoration:none;font-weight:800;font-family:Inter,system-ui,sans-serif">Dashboard</a>
    <a href="/smart-content-queue.html" style="display:inline-flex;padding:10px 16px;border-radius:999px;{'background:#16a34a;color:#fff;box-shadow:0 6px 18px rgba(0,0,0,.15);' if active=='queue' else 'background:#0f2236;color:#e8f0f7;border:1px solid #21415c;'}text-decoration:none;font-weight:800;font-family:Inter,system-ui,sans-serif">Smart Content Queue</a>
  </div>
</div>
'''
    idx = html.find('<body>')
    if idx != -1 and 'smart-content-queue.html' not in html:
        html = html[:idx+6] + nav + html[idx+6:]
        p.write_text(html)

insert_nav('/var/www/html/control.ecohandel.nl/index.html', 'dashboard')
insert_nav('/var/www/html/control.ecohandel.nl/smart-content-queue.html', 'queue')
print('patched nav')
