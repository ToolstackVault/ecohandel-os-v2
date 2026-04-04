import csv
import re
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import time
import random

LEADS_FILE = '/Users/ecohandel.nl/.openclaw/workspace/ecohandel/lead-generation/leads/LEADS.csv'

def get_existing_domains():
    domains = set()
    try:
        with open(LEADS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                domain = row.get('WEBSITE', 'ONBEKEND').lower().replace('https://', '').replace('http://', '').replace('www.', '').strip('/').split('/')[0]
                if domain != 'onbekend' and domain != '':
                    domains.add(domain)
    except Exception as e:
        pass
    return domains

def fetch_html(url):
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
    )
    try:
        response = urllib.request.urlopen(req, timeout=10)
        return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return ""

def search_duckduckgo(query):
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    html = fetch_html(url)
    links = []
    
    # Try finding class="result__url"
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.find_all('a', class_='result__url'):
        href = a.get('href', '')
        if 'uddg=' in href:
            links.append(urllib.parse.unquote(href.split('uddg=')[1].split('&')[0]))
            
    # Fallback to regex if DDG changed classes
    if not links:
        matches = re.findall(r'href=[\'"]\/\/(?:duckduckgo\.com\/)?l\/\?uddg=([^\'&]+)', html)
        for m in matches:
            links.append(urllib.parse.unquote(m))
            
    return links

def extract_contact_info(html):
    phone_pattern = re.compile(r'(?:0[1-9][0-9]{1,2}[-\s]?\d{6,7}|\+31[-\s]?\d{1,3}[-\s]?\d{6,7}|085[-\s]?\d{3}[-\s]?\d{4})')
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    
    phones = phone_pattern.findall(html)
    emails = email_pattern.findall(html)
    
    valid_emails = list(set([e.lower() for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.css', '.js')) and 'sentry' not in e]))
    valid_phones = list(set(phones))
    
    best_email = 'ONBEKEND'
    for e in valid_emails:
        if 'info@' in e or 'contact@' in e or 'hallo@' in e:
            best_email = e
            break
    if best_email == 'ONBEKEND' and valid_emails:
        best_email = valid_emails[0]
        
    return {
        'phone': valid_phones[0] if valid_phones else 'ONBEKEND',
        'email': best_email
    }

def main():
    existing_domains = get_existing_domains()
    steden = ['Amsterdam', 'Rotterdam', 'Den Haag', 'Utrecht', 'Eindhoven', 'Groningen', 'Tilburg', 'Almere', 'Breda', 'Nijmegen', 'Apeldoorn', 'Haarlem', 'Arnhem', 'Zaanstad', 'Den Bosch', 'Zwolle', 'Leeuwarden', 'Middelburg', 'Maastricht']
    stad = random.choice(steden)
    query = f"\"thuisbatterij\" installateur {stad} contact"
    
    links = search_duckduckgo(query)
    new_leads = []
    
    for link in links:
        if len(new_leads) >= 3:
            break
            
        domain = link.lower().replace('https://', '').replace('http://', '').replace('www.', '').strip('/').split('/')[0]
        if domain in existing_domains or any(x in domain for x in ['duckduckgo', 'google', 'trustoo', 'slimster', 'feenstra', 'coolblue', 'soly', 'solaredge', 'facebook', 'linkedin', 'instagram', 'youtube']):
            continue
            
        print(f"-> Scrapen van: {domain}")
        html = fetch_html(link)
        if not html: continue
        
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.string if soup.title else domain
        bedrijfsnaam = title.replace('\n', ' ').split('|')[0].split('-')[0].strip()
        if len(bedrijfsnaam) > 30 or len(bedrijfsnaam) < 3: bedrijfsnaam = domain
            
        contact_info = extract_contact_info(html)
        
        if contact_info['phone'] != 'ONBEKEND' or contact_info['email'] != 'ONBEKEND':
            new_leads.append({
                'BEDRIJF': bedrijfsnaam,
                'PROVINCIE': stad, 
                'WEBSITE': domain,
                'TELEFOON': contact_info['phone'],
                'EMAIL': contact_info['email'],
                'CONTACTPERSOON': 'ONBEKEND',
                'FUNCTIE': 'ONBEKEND',
                'BATTERIJ_ERVARING': 'JA - B2B Scrape',
                'DEYE_KENNIS': 'ONBEKEND',
                'WARMTE': 'MIDDEL',
                'BRON': 'AutoScraper DDG',
                'NOTITIES': f"Gevonden via {stad} search",
                'DATUM': time.strftime('%Y-%m-%d')
            })
            existing_domains.add(domain)
            print(f"   [+] Toevoegen: {bedrijfsnaam} - {contact_info['email']} / {contact_info['phone']}")
        
        time.sleep(random.uniform(1, 3))
        
    if new_leads:
        try:
            with open(LEADS_FILE, 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['BEDRIJF','PROVINCIE','WEBSITE','TELEFOON','EMAIL','CONTACTPERSOON','FUNCTIE','BATTERIJ_ERVARING','DEYE_KENNIS','WARMTE','BRON','NOTITIES','DATUM'])
                writer.writerows(new_leads)
            print(f"Succes! {len(new_leads)} nieuwe leads opgeslagen.")
        except:
            pass
    else:
        print("Geen nieuwe leads deze ronde.")

if __name__ == "__main__":
    main()
