from pathlib import Path

for path_str in [
    '/var/www/html/control.ecohandel.nl/index.html',
    '/var/www/html/control.ecohandel.nl/smart-content-queue.html',
]:
    path = Path(path_str)
    html = path.read_text()
    start = html.find('<div style="max-width:1680px;margin:0 auto;padding:16px 28px 0;">')
    if start != -1:
        end = html.find('</div>', start)
        if end != -1:
            end2 = html.find('</div>', end + 6)
            if end2 != -1:
                html = html[:start] + html[end2+6:]
                path.write_text(html)
print('removed inline nav blocks')
