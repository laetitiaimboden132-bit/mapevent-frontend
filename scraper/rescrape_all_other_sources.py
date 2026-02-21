"""
Re-scrape TOUTES les sources NON culturevalais et NON myswitzerland.
Extrait UNIQUEMENT ce qui est sur la page source.
NE RIEN INVENTER.

Sources à vérifier:
- tempslibre.ch (23 events)  
- vd.leprogramme.ch (14 events)
- valais.ch (25 events)
- vaud.ch (6 events)
- geneve.ch (24 events)
- autres (petites sources)
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

# Exclure culturevalais (déjà fait) et myswitzerland (déjà fait)
skip_domains = ['agenda.culturevalais.ch', 'www.myswitzerland.com']
check_events = [ev for ev in events 
                if urlparse(ev.get('source_url', '') or '').netloc not in skip_domains
                and ev.get('source_url', '')]

print(f"Events à vérifier: {len(check_events)}")
print(f"Sources: {set(urlparse(ev.get('source_url', '')).netloc for ev in check_events)}\n")

problems = []
all_page_data = []

for ev in check_events:
    eid = ev['id']
    title = ev.get('title', '')
    source_url = ev.get('source_url', '')
    current_loc = ev.get('location', '') or ''
    current_date = ev.get('date', '') or ''
    domain = urlparse(source_url).netloc
    
    print(f"--- ID {eid}: {title[:45]} ({domain}) ---")
    
    time.sleep(8)
    
    try:
        resp = requests.get(source_url, headers={
            'User-Agent': 'MapEventAI-Bot/1.0'
        }, timeout=15)
        
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code} ⚠")
            problems.append({'id': eid, 'issue': f'HTTP {resp.status_code}', 'title': title})
            continue
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        text = soup.get_text(separator='\n')
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # =============================================
        # EXTRAIRE L'ADRESSE depuis la page
        # Chercher des patterns: lieu, adresse, CP
        # =============================================
        page_address = None
        page_venue = None
        page_date = None
        
        # Chercher un bloc avec un code postal suisse (4 chiffres)
        # Contexte: les lignes juste avant/après le CP sont le lieu et la rue
        for i, line in enumerate(lines):
            cp_match = re.match(r'^(\d{4})\s+(.+)', line)
            if cp_match and not any(skip in line.lower() for skip in ['sion', 'lausanne'] if 'culture valais' in lines[max(0,i-5):i+1].__str__().lower()):
                # Vérifier si les lignes précédentes sont une adresse
                postal_city = line
                street = None
                venue = None
                
                # Regarder les 3 lignes avant
                for j in range(max(0, i-3), i):
                    prev = lines[j]
                    if re.match(r'^(Rue|Ch\.|Chemin|Route|Avenue|Av\.|Boulevard|Place|Quai|Passage|Rte|Allée|Grand|Sentier)', prev, re.I):
                        street = prev
                    elif len(prev) > 3 and not re.search(r'(menu|contact|accueil|recherche|partager|voir|lire)', prev.lower()):
                        if not re.match(r'^\d', prev) and len(prev) < 80:
                            venue = prev
                
                # C'est une adresse potentielle - vérifier si c'est celle de l'event
                # (pas celle du footer ou d'un autre élément)
                # Heuristique: si c'est dans les 80% du milieu du texte, c'est probablement l'event
                position_pct = i / len(lines) * 100
                if 10 < position_pct < 85:
                    parts = []
                    if venue:
                        parts.append(venue)
                    if street:
                        parts.append(street)
                    parts.append(postal_city)
                    page_address = ', '.join(parts)
                    page_venue = venue
                    # Ne pas casser ici - prendre la PREMIÈRE adresse trouvée dans le corps
                    break
        
        # =============================================
        # EXTRAIRE LA DATE
        # Format commun: DD.MM.YYYY ou DD/MM/YYYY
        # =============================================
        date_matches = re.findall(r'(\d{1,2})[./](\d{1,2})[./](\d{4})', text)
        if date_matches:
            for d, m, y in date_matches:
                potential = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
                if '2026' in y or '2025' in y:
                    page_date = potential
                    break
        
        # Format: "7 mars 2026", "du 20 au 29 mars 2026"
        months_fr = {
            'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
            'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
            'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
        }
        if not page_date:
            for month_name, month_num in months_fr.items():
                m = re.search(rf'(\d{{1,2}})\s+{month_name}\s+(\d{{4}})', text, re.I)
                if m:
                    day = m.group(1).zfill(2)
                    year = m.group(2)
                    page_date = f"{year}-{month_num}-{day}"
                    break
        
        # =============================================
        # COMPARER AVEC LES DONNÉES ACTUELLES
        # =============================================
        page_info = {
            'id': eid,
            'title': title[:50],
            'domain': domain,
            'current_loc': current_loc,
            'page_address': page_address,
            'current_date': current_date,
            'page_date': page_date
        }
        all_page_data.append(page_info)
        
        if page_address:
            # Vérifier si l'adresse actuelle correspond
            # Comparer les codes postaux
            current_cp = re.findall(r'\d{4}', current_loc)
            page_cp = re.findall(r'\d{4}', page_address)
            
            if current_cp and page_cp and current_cp[0] != page_cp[0]:
                problems.append({
                    'id': eid, 
                    'issue': 'CP DIFFÉRENT',
                    'title': title,
                    'current': current_loc[:50],
                    'page': page_address[:50]
                })
                print(f"  ⚠ CP DIFFÉRENT:")
                print(f"    DB:   {current_loc[:60]}")
                print(f"    PAGE: {page_address[:60]}")
            else:
                print(f"  LOC OK ({current_loc[:40]})")
        else:
            print(f"  LOC: pas d'adresse trouvée sur la page")
        
        if page_date:
            if page_date != current_date[:10]:
                print(f"  ⚠ DATE: DB={current_date[:10]} PAGE={page_date}")
            else:
                print(f"  DATE OK")
        
    except Exception as e:
        print(f"  ERREUR: {e}")

# =============================================
# RÉSUMÉ
# =============================================
print(f"\n{'='*60}")
print(f"RÉSUMÉ")
print(f"  Events vérifiés: {len(check_events)}")
print(f"  Problèmes trouvés: {len(problems)}")

if problems:
    print(f"\n  PROBLÈMES:")
    for p in problems:
        print(f"    ID {p['id']}: {p.get('title', '')[:40]} -> {p['issue']}")
        if 'current' in p:
            print(f"      DB:   {p['current']}")
            print(f"      PAGE: {p['page']}")

# Sauvegarder le rapport
with open('all_sources_audit.json', 'w', encoding='utf-8') as f:
    json.dump({
        'problems': problems,
        'all_data': all_page_data
    }, f, ensure_ascii=False, indent=2)

print("\nDONE")
