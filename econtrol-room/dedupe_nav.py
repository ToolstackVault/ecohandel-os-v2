from pathlib import Path

for path_str in [
    '/var/www/html/control.ecohandel.nl/index.html',
    '/var/www/html/control.ecohandel.nl/smart-content-queue.html',
]:
    path = Path(path_str)
    html = path.read_text()
    marker = '<div class="nav">'
    first = html.find(marker)
    if first != -1:
        second = html.find(marker, first + 1)
        if second != -1:
            end = html.find('</div>', second)
            if end != -1:
                html = html[:second] + html[end+6:]
                path.write_text(html)
print('deduped nav')
