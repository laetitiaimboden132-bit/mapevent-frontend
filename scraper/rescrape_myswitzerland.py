"""
Re-scrape TOUS les events myswitzerland.com.
Extraire UNIQUEMENT les infos de la page source.
NE RIEN INVENTER.
"""
import requests, sys, io, json, time, re
from bs4 import BeautifulSoup

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])

# Filtrer myswitzerland.com events
ms_events = [ev for ev in events if 'myswitzerland.com' in (ev.get('source_url', '') or '')]
print(f"Events myswitzerland.com: {len(ms_events)}\n")

fixes = []

for ev in ms_events:
    eid = ev['id']
    title = ev.get('title', '')
    source_url = ev.get('source_url', '')
    current_loc = ev.get('location', '') or ''
    current_date = ev.get('date', '') or ''
    
    print(f"--- ID {eid}: {title[:50]} ---")
    print(f"  DB LOC:  {current_loc}")
    print(f"  DB DATE: {current_date}")
    
    if not source_url:
        continue
    
    time.sleep(8)
    
    try:
        resp = requests.get(source_url, headers={
            'User-Agent': 'MapEventAI-Bot/1.0'
        }, timeout=15)
        
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code}")
            continue
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text(separator='\n')
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        fix = {'id': eid}
        changed = False
        
        # =============================================
        # EXTRAIRE L'ADRESSE - myswitzerland.com structure:
        # Le bloc "Contact" ou "Adresse de contact" contient l'adresse
        # Format: Nom du lieu\nRue\nCP Ville
        # OU: bloc "Lieu" dans le tableau d'infos
        # =============================================
        
        found_address = None
        
        # Méthode 1: Chercher "Contact" section
        for i, line in enumerate(lines):
            if line.lower() in ['contact', 'adresse de contact']:
                # Lire les lignes suivantes pour trouver adresse
                remaining = lines[i+1:i+10]
                venue = None
                street = None
                postal_city = None
                
                for rline in remaining:
                    # Stop si on atteint une autre section
                    if rline.lower() in ['date', 'prix', 'event homepage', 'vérifier', 'informations', 'découvrir']:
                        break
                    
                    # Détecter CP ville (4 chiffres suisses au début)
                    cp_match = re.match(r'^(\d{4})\s+(.+)', rline)
                    if cp_match:
                        postal_city = rline
                        continue
                    
                    # Détecter rue
                    if re.match(r'^(Rue|Ch\.|Chemin|Route|Avenue|Av\.|Boulevard|Place|Quai|Passage|Rte|Allée)', rline, re.I):
                        street = rline
                        continue
                    
                    # Détecter téléphone - skip
                    if rline.startswith('Téléphone') or rline.startswith('+41') or '@' in rline:
                        continue
                    if rline.startswith('http') or rline.endswith('.ch') or rline.endswith('.com'):
                        continue
                    
                    # Sinon c'est le nom du lieu
                    if not venue and len(rline) > 2 and not rline.startswith('Cliquez'):
                        venue = rline
                
                if postal_city:
                    parts = []
                    if venue:
                        parts.append(venue)
                    if street:
                        parts.append(street)
                    parts.append(postal_city)
                    found_address = ', '.join(parts)
                    break
        
        # Méthode 2: Chercher "Lieu" dans le tableau
        if not found_address:
            for i, line in enumerate(lines):
                if line == 'Lieu':
                    remaining = lines[i+1:i+6]
                    venue = None
                    street = None
                    postal_city = None
                    
                    for rline in remaining:
                        if rline.lower() in ['event homepage', 'prix', 'contact', 'adresse']:
                            break
                        cp_match = re.match(r'^(\d{4})\s+(.+)', rline)
                        if cp_match:
                            postal_city = rline
                            continue
                        if re.match(r'^(Rue|Ch\.|Chemin|Route|Avenue|Av\.|Boulevard|Place|Quai|Passage|Rte)', rline, re.I):
                            street = rline
                            continue
                        if not venue and len(rline) > 2 and rline != 'Switzerland':
                            venue = rline
                    
                    if venue or postal_city:
                        parts = []
                        if venue:
                            parts.append(venue)
                        if street:
                            parts.append(street)
                        if postal_city:
                            parts.append(postal_city)
                        found_address = ', '.join(parts)
                        break
        
        # =============================================
        # EXTRAIRE LA DATE
        # =============================================
        found_date = None
        found_end_date = None
        
        # Chercher "Date" section - format "21. mars 2026" ou "06 - 10. mai 2026"
        months_fr = {
            'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
            'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
            'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
        }
        
        for i, line in enumerate(lines):
            if line == 'Date' and i+1 < len(lines):
                date_text = lines[i+1]
                
                # Format "21. mars 2026"
                m = re.search(r'(\d{1,2})\.\s*(\w+)\s+(\d{4})', date_text)
                if m:
                    day = m.group(1).zfill(2)
                    month_name = m.group(2).lower()
                    year = m.group(3)
                    if month_name in months_fr:
                        found_date = f"{year}-{months_fr[month_name]}-{day}"
                
                # Format "06 - 10. mai 2026"
                m2 = re.search(r'(\d{1,2})\s*-\s*(\d{1,2})\.\s*(\w+)\s+(\d{4})', date_text)
                if m2:
                    day1 = m2.group(1).zfill(2)
                    day2 = m2.group(2).zfill(2)
                    month_name = m2.group(3).lower()
                    year = m2.group(4)
                    if month_name in months_fr:
                        found_date = f"{year}-{months_fr[month_name]}-{day1}"
                        found_end_date = f"{year}-{months_fr[month_name]}-{day2}"
                
                # Format "06. mai - 10. mai 2026"
                m3 = re.search(r'(\d{1,2})\.\s*(\w+)\s*-\s*(\d{1,2})\.\s*(\w+)\s+(\d{4})', date_text)
                if m3:
                    day1 = m3.group(1).zfill(2)
                    month1 = m3.group(2).lower()
                    day2 = m3.group(3).zfill(2)
                    month2 = m3.group(4).lower()
                    year = m3.group(5)
                    if month1 in months_fr and month2 in months_fr:
                        found_date = f"{year}-{months_fr[month1]}-{day1}"
                        found_end_date = f"{year}-{months_fr[month2]}-{day2}"
                
                break
        
        # =============================================
        # COMPARER ET CORRIGER
        # =============================================
        if found_address and found_address != current_loc:
            fix['location'] = found_address
            changed = True
            print(f"  PAGE LOC: {found_address[:60]}")
        elif found_address:
            print(f"  LOC OK")
        else:
            print(f"  LOC: PAS TROUVÉ SUR LA PAGE ⚠")
        
        if found_date and found_date != current_date[:10]:
            fix['start_date'] = found_date
            if found_end_date:
                fix['end_date'] = found_end_date
            changed = True
            print(f"  PAGE DATE: {found_date} -> {found_end_date or found_date}")
        elif found_date:
            print(f"  DATE OK")
        else:
            print(f"  DATE: PAS TROUVÉ SUR LA PAGE ⚠")
        
        if changed:
            fixes.append(fix)
        
    except Exception as e:
        print(f"  ERREUR: {e}")
    print()

# =============================================
# RÉSUMÉ
# =============================================
print(f"\n{'='*60}")
print(f"CORRECTIONS: {len(fixes)}")
for f in fixes:
    print(f"  ID {f['id']}: {f}")

# Sauvegarder
with open('myswitzerland_fixes.json', 'w', encoding='utf-8') as f:
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
