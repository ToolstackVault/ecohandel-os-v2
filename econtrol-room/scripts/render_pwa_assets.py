#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import shutil

from render_ui import BUILD_DIR, write_text

MANIFEST_PATH = BUILD_DIR / 'app.webmanifest'
SW_PATH = BUILD_DIR / 'sw.js'
FAVICON_PATH = BUILD_DIR / 'favicon.png'
APPLE_ICON_PATH = BUILD_DIR / 'apple-touch-icon.png'
BROWSERCONFIG_PATH = BUILD_DIR / 'browserconfig.xml'
BRANDING_FAVICON_PATH = Path('/Users/ecohandel.nl/.openclaw/workspace/ecohandel/econtrol-room/assets/branding/Favicon.png')


def main() -> None:
    manifest = {
        'name': 'EcoHandel.nl',
        'short_name': 'EcoHandel',
        'description': 'Econtrol Room mission board voor EcoHandel.nl',
        'start_url': '/',
        'scope': '/',
        'display': 'browser',
        'background_color': '#06111d',
        'theme_color': '#06111d',
        'orientation': 'portrait',
        'icons': [
            {
                'src': '/favicon.png',
                'sizes': '150x150',
                'type': 'image/png',
                'purpose': 'any maskable'
            },
            {
                'src': '/apple-touch-icon.png',
                'sizes': '150x150',
                'type': 'image/png',
                'purpose': 'any'
            }
        ]
    }
    write_text(MANIFEST_PATH, json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')

    sw = '''const CACHE_NAME = "ecohandel-econtrol-v2";
const URLS = ["/", "/smart-content-queue.html", "/workflows.html", "/partner-campaign.html", "/app.webmanifest", "/favicon.png", "/apple-touch-icon.png"];
self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(URLS)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  event.respondWith(fetch(event.request).then((response) => {
    const copy = response.clone();
    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy)).catch(() => {});
    return response;
  }).catch(() => caches.match(event.request).then((cached) => cached || caches.match("/"))));
});
'''
    write_text(SW_PATH, sw)

    if not BRANDING_FAVICON_PATH.exists():
        raise FileNotFoundError(f'Missing branding favicon: {BRANDING_FAVICON_PATH}')
    shutil.copyfile(BRANDING_FAVICON_PATH, FAVICON_PATH)
    shutil.copyfile(BRANDING_FAVICON_PATH, APPLE_ICON_PATH)

    browserconfig = '''<?xml version="1.0" encoding="utf-8"?>
<browserconfig>
  <msapplication>
    <tile>
      <square150x150logo src="/favicon.png"/>
      <TileColor>#07111d</TileColor>
    </tile>
  </msapplication>
</browserconfig>
'''
    write_text(BROWSERCONFIG_PATH, browserconfig)

    print(f'Wrote {MANIFEST_PATH}')
    print(f'Wrote {SW_PATH}')
    print(f'Wrote {FAVICON_PATH}')
    print(f'Wrote {APPLE_ICON_PATH}')
    print(f'Wrote {BROWSERCONFIG_PATH}')


if __name__ == '__main__':
    main()
