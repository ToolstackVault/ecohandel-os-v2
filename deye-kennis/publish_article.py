#!/usr/bin/env python3
"""
Deye Kennis Blog Publisher — EcoHandel.nl
==========================================
Publiceert of updatet een artikel op /blogs/kennis.

Gebruik:
  python3 publish_article.py article.html --title "Titel" --author "Milan" --tags "deye,tag2" --excerpt "Korte samenvatting"
  python3 publish_article.py article.html --update 613975720277  # update bestaand artikel

Het script:
1. Haalt automatisch een Shopify API token op
2. Wrapt HTML in <div class="deye-article"> als dat ontbreekt
3. Valideert de HTML structuur
4. Publiceert naar kennis blog (ID: 126678466901)
"""

import urllib.request, json, sys, argparse, re, os

# --- Config ---
SHOP = "n6f6ja-qr.myshopify.com"
CLIENT_ID = "7c26018c359fde447766ab15b9d0b30e"
CLIENT_SECRET = os.environ.get('SHOPIFY_CLIENT_SECRET', '')
BLOG_ID = 126678466901
API_VERSION = "2026-01"
BASE = f"https://{SHOP}/admin/api/{API_VERSION}"

# --- Auth ---
def get_token():
    data = f"client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials".encode()
    req = urllib.request.Request(f"https://{SHOP}/admin/oauth/access_token", data=data)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["access_token"]

def api(method, path, payload=None, token=None):
    url = f"{BASE}{path}"
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(url, data=data, method=method,
        headers={"X-Shopify-Access-Token": token, "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)

# --- Validation ---
def validate_html(html):
    warnings = []
    errors = []

    if '<div class="deye-article">' not in html:
        warnings.append("⚠️  Missing deye-article wrapper — will be added automatically")

    if '<h1' in html:
        errors.append("❌ HTML bevat een <h1> tag — verwijder deze (theme toont de titel)")

    if re.search(r'\[.*?\]\(#\w+\)', html):
        errors.append("❌ Markdown-style links gevonden [text](#anchor) — gebruik <a href=\"#anchor\">text</a>")

    if 'Shopify Blog Instellingen' in html:
        errors.append("❌ Metadata block gevonden in HTML — verwijder 'Shopify Blog Instellingen' sectie")

    if 'Afbeeldingen voor dit artikel' in html:
        errors.append("❌ Image instructies gevonden — verwijder 'Afbeeldingen voor dit artikel' sectie")

    if 'Actief — Je leest dit nu' in html or ('Deel 1' in html and 'Deel 3' in html):
        errors.append("❌ Serie-navigatie tabel gevonden — verwijder deze")

    if '<div class="deye-toc">' not in html and 'Inhoudsopgave' not in html:
        warnings.append("⚠️  Geen inhoudsopgave gevonden — overweeg een TOC toe te voegen")

    if '<details' not in html:
        warnings.append("⚠️  Geen FAQ sectie gevonden — overweeg <details>/<summary> toe te voegen")

    if 'background:#1a1a2e' not in html:
        warnings.append("⚠️  Geen CTA blok gevonden — overweeg een call-to-action toe te voegen")

    return errors, warnings

def prepare_html(html):
    """Clean and wrap HTML if needed."""
    html = html.strip()

    # Wrap in deye-article if missing
    if '<div class="deye-article">' not in html:
        html = f'<div class="deye-article">\n\n{html}\n\n</div>'

    # Remove any H1 (theme shows title)
    html = re.sub(r'\s*<h1[^>]*>.*?</h1>\s*', '\n', html, count=1, flags=re.DOTALL)

    return html

# --- Main ---
def main():
    parser = argparse.ArgumentParser(description="Publish article to EcoHandel Deye Kennis blog")
    parser.add_argument("file", help="HTML file to publish")
    parser.add_argument("--title", help="Article title (required for new articles)")
    parser.add_argument("--author", default="Milan", help="Author name: Milan, Tom, or Jean (default: Milan)")
    parser.add_argument("--tags", default="deye", help="Comma-separated tags (default: deye)")
    parser.add_argument("--excerpt", help="Short summary for blog listing (1-2 sentences)")
    parser.add_argument("--update", type=int, help="Article ID to update (skip creation)")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, don't publish")
    args = parser.parse_args()

    # Read HTML
    with open(args.file, "r") as f:
        html = f.read()

    print(f"📄 Read {len(html)} chars from {args.file}")

    # Validate
    errors, warnings = validate_html(html)
    for w in warnings:
        print(w)
    for e in errors:
        print(e)

    if errors:
        print(f"\n❌ {len(errors)} error(s) found. Fix these before publishing.")
        sys.exit(1)

    if args.dry_run:
        print("\n✅ Validation passed (dry run — not publishing)")
        return

    # Prepare
    html = prepare_html(html)
    print(f"📝 Prepared HTML: {len(html)} chars")

    # Get token
    print("🔑 Getting API token...")
    token = get_token()

    if args.update:
        # Update existing
        payload = {"article": {"id": args.update, "body_html": html}}
        if args.title:
            payload["article"]["title"] = args.title
        if args.excerpt:
            payload["article"]["summary_html"] = f"<p>{args.excerpt}</p>"
        if args.tags:
            payload["article"]["tags"] = args.tags

        result = api("PUT", f"/articles/{args.update}.json", payload, token)
        article = result["article"]
        print(f"\n✅ Updated: {article['title']}")
        print(f"   ID: {article['id']}")
        print(f"   URL: /blogs/kennis/{article['handle']}")

    else:
        # Create new
        if not args.title:
            print("❌ --title is required for new articles")
            sys.exit(1)

        payload = {
            "article": {
                "title": args.title,
                "body_html": html,
                "author": args.author,
                "tags": args.tags,
                "published": True
            }
        }
        if args.excerpt:
            payload["article"]["summary_html"] = f"<p>{args.excerpt}</p>"

        result = api("POST", f"/blogs/{BLOG_ID}/articles.json", payload, token)
        article = result["article"]
        print(f"\n✅ Published: {article['title']}")
        print(f"   ID: {article['id']}")
        print(f"   URL: /blogs/kennis/{article['handle']}")
        print(f"   Author: {article['author']}")

    print("\n📋 Post-publish checklist:")
    print("   □ Artikel zichtbaar op /blogs/kennis?")
    print("   □ TOC links werken?")
    print("   □ Geen dubbele H1?")
    print("   □ Excerpt correct op listing page?")

if __name__ == "__main__":
    main()
