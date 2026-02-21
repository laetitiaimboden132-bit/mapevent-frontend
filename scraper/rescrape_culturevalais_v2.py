"""
Re-scrape culturevalais.ch avec les bons sélecteurs CSS:
- div.portlet_location -> nom du lieu, rue, CP ville
- div.weekday_time -> date "Sa 07.02.2026, 19:00 - 22:30"
- p.address -> adresse formatée
"""
import requests, sys, io, json, time, re
from bs4 import BeautifulSoup

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])

cv_events = [ev for ev in events if 'culturevalais.ch' in (ev.get('source_url', '') or '')]
print(f"Events culturevalais.ch: {len(cv_events)}\n")

fixes = []

for ev in cv_events:
    eid = ev['id']
    title = ev.get('title', '')
    source_url = ev.get('source_url', '')
    
    print(f"--- ID {eid}: {title[:50]} ---")
    
    if not source_url:
        continue
    
    time.sleep(8)
    
    try:
        resp = requests.get(source_url, headers={
            'User-Agent': 'MapEventAI-Bot/1.0 (event-aggregator; contact@mapevent.ai)'
        }, timeout=15)
        
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code}")
            continue
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        fix = {'id': eid}
        changed = False
        
        # =============================================
        # 1. EXTRAIRE LE LIEU (div.portlet_location)
        # =============================================
        location_div = soup.select_one('div.portlet_location')
        if location_div:
            # Extraire le contenu structuré
            # Structure: h3 "Lieu de l'événement", div avec nom, p avec rue, p avec CP ville
            portlet_content = location_div.select_one('div.portlet-content')
            if portlet_content:
                # Récupérer le texte du bloc accordion_content (qui a le nom, rue, CP)
                accordion = portlet_content.select_one('div.accordion_content')
                if accordion:
                    parts = [p.get_text(strip=True) for p in accordion.find_all('p')]
                    # parts devrait être [nom_lieu, rue, CP_ville] ou [rue, CP_ville]
                    venue = None
                    street = None
                    postal_city = None
                    
                    for p in parts:
                        if re.match(r'^\d{4}\s', p):
                            postal_city = p
                        elif re.match(r'^(Rue|Ch\.|Chemin|Route|Avenue|Av\.|Boulevard|Place|Quai|Passage|Rte|Gliserallee|Bahnhof|Furka|Sennerei|Forststr|Bodmen|Tschand)', p, re.I):
                            street = p
                        elif not venue and 'Horaire' not in p and 'transport' not in p:
                            venue = p
                    
                    addr_parts = []
                    if venue:
                        addr_parts.append(venue)
                    if street:
                        addr_parts.append(street)
                    if postal_city:
                        addr_parts.append(postal_city)
                    
                    if addr_parts:
                        new_loc = ', '.join(addr_parts)
                        fix['location'] = new_loc
                        changed = True
                        print(f"  LOC: {new_loc[:60]}")
        
        # Fallback: p.address
        if 'location' not in fix:
            addr_p = soup.select_one('p.address')
            if addr_p:
                addr_text = addr_p.get_text(strip=True)
                # Enlever "Horaire des transports en commun"
                addr_text = addr_text.replace('Horaire des transports en commun', '').strip()
                if addr_text and len(addr_text) > 5:
                    fix['location'] = addr_text
                    changed = True
                    print(f"  LOC (fallback): {addr_text[:60]}")
        
        # =============================================
        # 2. EXTRAIRE LA DATE (div.weekday_time)
        # =============================================
        date_div = soup.select_one('div.weekday_time')
        if date_div:
            date_text = date_div.get_text(strip=True)
            # Format: "Sa 07.02.2026, 19:00 - 22:30"
            date_matches = re.findall(r'(\d{2})\.(\d{2})\.(\d{4})', date_text)
            if date_matches:
                d, m, y = date_matches[0]
                start_date = f"{y}-{m}-{d}"
                fix['start_date'] = start_date
                
                if len(date_matches) > 1:
                    d2, m2, y2 = date_matches[1]
                    fix['end_date'] = f"{y2}-{m2}-{d2}"
                else:
                    fix['end_date'] = start_date
                
                changed = True
                print(f"  DATE: {start_date}")
        else:
            # Chercher dans le texte brut
            text = soup.get_text()
            # Chercher après "Date" 
            m = re.search(r'Date\s*\n\s*\w{2}\s+(\d{2})\.(\d{2})\.(\d{4})', text)
            if m:
                d, mo, y = m.groups()
                start_date = f"{y}-{mo}-{d}"
                fix['start_date'] = start_date
                fix['end_date'] = start_date
                changed = True
                print(f"  DATE (text): {start_date}")
        
        # =============================================
        # 3. EXTRAIRE L'EMAIL ORGANISATEUR
        # =============================================
        # Chercher dans le bloc organisateur
        text = soup.get_text(separator='\n')
        email_match = re.search(r'E-Mail\s*\n\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
        if email_match:
            org_email = email_match.group(1)
            print(f"  EMAIL: {org_email}")
        
        if changed:
            fixes.append(fix)
        else:
            print(f"  PAS DE CHANGEMENT")
        
    except Exception as e:
        print(f"  ERREUR: {e}")

# =============================================
# RÉSUMÉ
# =============================================
print(f"\n{'='*60}")
print(f"CORRECTIONS: {len(fixes)}")

# Sauvegarder avant d'appliquer
with open('culturevalais_fixes_v2.json', 'w', encoding='utf-8') as f:
    json.dump(fixes, f, ensure_ascii=False, indent=2)

if fixes:
    print(f"\nAPPLICATION...")
    resp = requests.post(
        f'{API_URL}/api/events/fix-details-batch',
        json={'fixes': fixes},
        timeout=60
    )
    if resp.status_code == 200:
        result = resp.json()
        print(f"  Mis à jour: {result.get('updated', 0)}/{len(fixes)}")
    else:
        print(f"  ERREUR: {resp.text[:200]}")

print("\nDONE")
