"""
1. Trouver la vraie adresse du Sierre Blues Festival
2. Trouver les doublons
3. Re-vérifier TOUTES les adresses en les comparant aux pages source
"""
import requests, sys, io, json, time, re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])

print(f"Total events: {len(events)}\n")

# =============================================
# 1. TROUVER LES DOUBLONS (même titre)
# =============================================
print("=" * 60)
print("1. DOUBLONS")
print("=" * 60)

titles = {}
for ev in events:
    t = ev.get('title', '').strip()
    if t not in titles:
        titles[t] = []
    titles[t].append(ev)

duplicates = []
for t, evs in titles.items():
    if len(evs) > 1:
        print(f"\n  DOUBLON: '{t}'")
        for ev in evs:
            print(f"    ID {ev['id']}: {ev.get('location', '')[:50]} | Source: {urlparse(ev.get('source_url', '') or '').netloc}")
        # Garder celui avec la meilleure source/description
        duplicates.append(evs)

# =============================================
# 2. VÉRIFIER ADRESSES VALAIS.CH depuis les pages source
# =============================================
print(f"\n{'=' * 60}")
print("2. VÉRIFICATION ADRESSES DEPUIS PAGES SOURCE (valais.ch)")
print("=" * 60)

valais_events = [ev for ev in events if 'valais.ch' in (ev.get('source_url', '') or '')]
print(f"\n  {len(valais_events)} events valais.ch à vérifier\n")

address_fixes = []

for ev in valais_events:
    eid = ev['id']
    title = ev.get('title', '')
    source_url = ev.get('source_url', '')
    current_loc = ev.get('location', '') or ''
    
    if not source_url:
        continue
    
    time.sleep(8)  # Respecter le délai
    
    try:
        resp = requests.get(source_url, headers={
            'User-Agent': 'MapEventAI-Bot/1.0 (event-aggregator; contact@mapevent.ai)'
        }, timeout=15)
        
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code}: ID {eid} {title[:40]}")
            continue
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Chercher le lieu dans les JSON-LD
        real_location = None
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                ld = json.loads(script.string)
                if isinstance(ld, list):
                    for item in ld:
                        if item.get('@type') == 'Event':
                            loc_data = item.get('location', {})
                            if isinstance(loc_data, dict):
                                name = loc_data.get('name', '')
                                addr = loc_data.get('address', {})
                                if isinstance(addr, dict):
                                    street = addr.get('streetAddress', '')
                                    postal = addr.get('postalCode', '')
                                    city = addr.get('addressLocality', '')
                                    real_location = f"{name}, {street}, {postal} {city}".strip(', ')
                                elif isinstance(addr, str):
                                    real_location = f"{name}, {addr}".strip(', ')
                elif isinstance(ld, dict) and ld.get('@type') == 'Event':
                    loc_data = ld.get('location', {})
                    if isinstance(loc_data, dict):
                        name = loc_data.get('name', '')
                        addr = loc_data.get('address', {})
                        if isinstance(addr, dict):
                            street = addr.get('streetAddress', '')
                            postal = addr.get('postalCode', '')
                            city = addr.get('addressLocality', '')
                            real_location = f"{name}, {street}, {postal} {city}".strip(', ')
            except:
                pass
        
        # Chercher dans le texte de la page "Lieu"
        if not real_location:
            text = soup.get_text()
            # Pattern "Lieu\nXXX\nYYYY - Ville"
            m = re.search(r'Lieu\s*\n\s*(.+?)\s*\n\s*(\d{4})\s*-?\s*(.+?)(?:\n|$)', text)
            if m:
                real_location = f"{m.group(1).strip()}, {m.group(2)} {m.group(3).strip()}"
        
        if real_location:
            # Nettoyer
            real_location = real_location.replace('\n', ', ').strip()
            real_location = re.sub(r',\s*,', ',', real_location)
            real_location = re.sub(r'\s+', ' ', real_location)
            
            # Comparer avec l'adresse actuelle
            if real_location.lower().replace(' ', '') != current_loc.lower().replace(' ', ''):
                # Vérifier si c'est significativement différent
                current_simple = current_loc.split(',')[0].strip().lower()
                real_simple = real_location.split(',')[0].strip().lower()
                
                if current_simple != real_simple:
                    print(f"  DIFF ID {eid}: {title[:40]}")
                    print(f"    ACTUEL: {current_loc[:60]}")
                    print(f"    SOURCE: {real_location[:60]}")
                    address_fixes.append({
                        'id': eid,
                        'title': title,
                        'current': current_loc,
                        'source': real_location,
                    })
                else:
                    print(f"  OK ID {eid}: {title[:40]} (mêmes lieux)")
            else:
                print(f"  OK ID {eid}: {title[:40]}")
        else:
            print(f"  NO ADDR ID {eid}: {title[:40]}")
    
    except Exception as e:
        print(f"  ERR ID {eid}: {title[:40]} -> {e}")

print(f"\n{'=' * 60}")
print(f"RÉSUMÉ")
print(f"{'=' * 60}")
print(f"  Doublons trouvés: {len(duplicates)}")
print(f"  Adresses différentes: {len(address_fixes)}")

# Sauvegarder les résultats pour correction
with open('address_diff_report.json', 'w', encoding='utf-8') as f:
    json.dump({
        'duplicates': [[{'id': ev['id'], 'title': ev.get('title', ''), 'source': ev.get('source_url', '')} for ev in group] for group in duplicates],
        'address_fixes': address_fixes,
    }, f, ensure_ascii=False, indent=2)

print(f"\nRapport sauvegardé dans address_diff_report.json")
