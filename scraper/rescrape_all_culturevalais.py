"""
Re-scrape TOUTES les infos (lieu, adresse, dates) depuis les pages source
de agenda.culturevalais.ch.
Extrait: nom du lieu, adresse complète, dates début/fin.
"""
import requests, sys, io, json, time, re
from bs4 import BeautifulSoup

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])

# Filtrer les events culturevalais.ch
cv_events = [ev for ev in events if 'culturevalais.ch' in (ev.get('source_url', '') or '')]
print(f"Events culturevalais.ch: {len(cv_events)}\n")

fixes = []
errors = []

for ev in cv_events:
    eid = ev['id']
    title = ev.get('title', '')
    source_url = ev.get('source_url', '')
    current_loc = ev.get('location', '') or ''
    current_date = ev.get('date', '') or ''
    
    print(f"--- ID {eid}: {title[:50]} ---")
    print(f"  URL: {source_url}")
    
    if not source_url:
        print(f"  SKIP: pas de source URL")
        continue
    
    time.sleep(8)
    
    try:
        resp = requests.get(source_url, headers={
            'User-Agent': 'MapEventAI-Bot/1.0 (event-aggregator; contact@mapevent.ai)'
        }, timeout=15)
        
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code}")
            errors.append(f"ID {eid}: HTTP {resp.status_code}")
            continue
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text(separator='\n')
        
        # =============================================
        # EXTRAIRE LE LIEU ET L'ADRESSE
        # =============================================
        venue_name = None
        street = None
        postal_city = None
        
        # Chercher le bloc "Lieu de l'événement" dans le texte
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        for i, line in enumerate(lines):
            if 'lieu de l' in line.lower() or 'lieu :' in line.lower():
                # Les lignes suivantes contiennent: nom du lieu, rue, CP ville
                remaining = lines[i+1:i+6]
                for j, rline in enumerate(remaining):
                    # Ignorer les lignes de navigation/menu
                    if any(skip in rline.lower() for skip in ['date', 'organisateur', 'catégorie', 'prix', 'contact', 'partager', 'ajouter']):
                        break
                    
                    # Détecter le code postal (4 chiffres suisses)
                    cp_match = re.match(r'^(\d{4})\s+(.+)$', rline)
                    if cp_match:
                        postal_city = rline
                        break
                    
                    # Détecter une rue (commence par Rue, Ch., Route, Avenue, Place, etc.)
                    if re.match(r'^(Rue|Ch\.|Chemin|Route|Avenue|Av\.|Boulevard|Bd|Place|Quai|Passage|Ruelle|Sentier|Impasse)', rline, re.I):
                        street = rline
                    elif not venue_name and not re.match(r'^\d', rline):
                        venue_name = rline
                break
        
        # Construire l'adresse complète
        addr_parts = []
        if venue_name:
            addr_parts.append(venue_name)
        if street:
            addr_parts.append(street)
        if postal_city:
            addr_parts.append(postal_city)
        
        new_location = ', '.join(addr_parts) if addr_parts else None
        
        # =============================================
        # EXTRAIRE LES DATES
        # =============================================
        start_date = None
        end_date = None
        
        # Chercher le bloc "Date" dans le texte
        for i, line in enumerate(lines):
            if line.lower().startswith('date') and i + 1 < len(lines):
                # La ligne suivante contient la date
                # Format typique: "Sa 07.02.2026, 19:00 - 22:30"
                # ou "Sa 07.02.2026, 19:00" 
                # ou "07.02.2026 - 09.02.2026"
                date_text = lines[i+1] if i+1 < len(lines) else ''
                
                # Chercher toutes les dates au format DD.MM.YYYY
                date_matches = re.findall(r'(\d{2})\.(\d{2})\.(\d{4})', date_text)
                
                if not date_matches:
                    # Essayer les lignes suivantes
                    for k in range(2, 5):
                        if i+k < len(lines):
                            date_text += ' ' + lines[i+k]
                    date_matches = re.findall(r'(\d{2})\.(\d{2})\.(\d{4})', date_text)
                
                if date_matches:
                    # Première date = début
                    d, m, y = date_matches[0]
                    start_date = f"{y}-{m}-{d}"
                    
                    if len(date_matches) > 1:
                        # Deuxième date = fin
                        d2, m2, y2 = date_matches[1]
                        end_date = f"{y2}-{m2}-{d2}"
                    else:
                        end_date = start_date
                
                break
        
        # =============================================
        # COMPARER ET PRÉPARER LES CORRECTIONS
        # =============================================
        fix = {'id': eid}
        changed = False
        
        if new_location and new_location != current_loc:
            fix['location'] = new_location
            changed = True
            print(f"  LOC: '{current_loc[:50]}' -> '{new_location[:50]}'")
        else:
            print(f"  LOC OK: {current_loc[:50]}")
        
        if start_date:
            # Comparer avec la date actuelle
            ev_date = ev.get('date', '') or ''
            if start_date != ev_date[:10] if ev_date else True:
                fix['start_date'] = start_date
                if end_date:
                    fix['end_date'] = end_date
                changed = True
                print(f"  DATE: '{ev_date[:10]}' -> '{start_date}'")
            else:
                print(f"  DATE OK: {ev_date[:10]}")
        else:
            print(f"  DATE: pas trouvée")
        
        if changed:
            fixes.append(fix)
        
    except Exception as e:
        print(f"  ERREUR: {e}")
        errors.append(f"ID {eid}: {e}")

# =============================================
# RÉSUMÉ ET APPLICATION
# =============================================
print(f"\n{'='*60}")
print(f"RÉSUMÉ")
print(f"  Events scrappés: {len(cv_events)}")
print(f"  Corrections: {len(fixes)}")
print(f"  Erreurs: {len(errors)}")

if fixes:
    print(f"\nAPPLICATION DES CORRECTIONS...")
    resp = requests.post(
        f'{API_URL}/api/events/fix-details-batch',
        json={'fixes': fixes},
        timeout=60
    )
    if resp.status_code == 200:
        result = resp.json()
        print(f"  Mis à jour: {result.get('updated', 0)}/{len(fixes)}")
        if result.get('errors'):
            for err in result['errors'][:5]:
                print(f"  Erreur: {err}")
    else:
        print(f"  ERREUR API: {resp.text[:200]}")

# Sauvegarder les corrections pour review
with open('culturevalais_fixes.json', 'w', encoding='utf-8') as f:
    json.dump(fixes, f, ensure_ascii=False, indent=2)
print(f"\nFixes sauvegardés dans culturevalais_fixes.json")
