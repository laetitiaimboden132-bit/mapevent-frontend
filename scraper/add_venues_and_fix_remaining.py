"""
Phase 3: Ajouter les noms de lieux (venues) aux events culturevalais
+ geocoder précisément Attache ta tuque et Combat de reines
+ vérifier les events avec dates passées
"""
import requests, sys, io, json, time, re
from bs4 import BeautifulSoup

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

def geocode(query):
    time.sleep(1.5)
    try:
        resp = requests.get('https://nominatim.openstreetmap.org/search', params={
            'q': query,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'ch'
        }, headers={'User-Agent': 'MapEventAI-Bot/1.0'}, timeout=10)
        results = resp.json()
        if results:
            return float(results[0]['lat']), float(results[0]['lon'])
    except Exception as e:
        print(f"  Geocode error: {e}")
    return None

r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])

cv_events = [ev for ev in events if 'culturevalais.ch' in (ev.get('source_url', '') or '')]
print(f"Events culturevalais: {len(cv_events)}\n")

# =============================================
# Phase A: Re-scrape pour capturer les NOMS DE LIEUX
# =============================================
print("PHASE A: Extraction des noms de lieux")
print("="*60)

venue_fixes = []

for ev in cv_events:
    eid = ev['id']
    title = ev.get('title', '')
    source_url = ev.get('source_url', '')
    current_loc = ev.get('location', '') or ''
    
    if not source_url:
        continue
    
    time.sleep(8)
    
    try:
        resp = requests.get(source_url, headers={
            'User-Agent': 'MapEventAI-Bot/1.0'
        }, timeout=15)
        
        if resp.status_code != 200:
            continue
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Extraire le nom du lieu depuis div.portlet_location
        portlet = soup.select_one('div.portlet_location')
        venue_name = None
        
        if portlet:
            # Le portlet-content a un accordion_content avec le nom du lieu
            accordion = portlet.select_one('div.accordion_content')
            if accordion:
                paragraphs = accordion.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    # Le nom du lieu est le premier p qui n'est pas une rue ni un CP
                    if not text:
                        continue
                    if re.match(r'^\d{4}\s', text):  # Code postal
                        continue
                    if re.match(r'^(Rue|Ch\.|Chemin|Route|Avenue|Av\.|Boulevard|Place|Quai|Passage|Rte|Gliserallee|Bahnhof|Furka|Ruelle|Sentier|Impasse)', text, re.I):
                        continue
                    if 'Horaire' in text or 'transport' in text:
                        continue
                    venue_name = text
                    break
        
        # Vérifier si le nom du lieu est déjà dans l'adresse
        if venue_name and venue_name not in current_loc:
            new_loc = f"{venue_name}, {current_loc}"
            venue_fixes.append({'id': eid, 'location': new_loc})
            print(f"  ID {eid}: +{venue_name} -> {new_loc[:60]}")
        else:
            print(f"  ID {eid}: OK ({current_loc[:50]})")
        
    except Exception as e:
        print(f"  ID {eid}: ERREUR {e}")

print(f"\n  Total venue fixes: {len(venue_fixes)}")

# =============================================
# Phase B: Geocoder Attache ta tuque PRÉCISÉMENT
# =============================================
print(f"\n{'='*60}")
print("PHASE B: Geocodage précis")
print("="*60)

precise_fixes = []

# 1. Attache ta tuque - Rue des Industries 11, 1964 Conthey
# Essayer avec structured query
time.sleep(1.5)
try:
    resp = requests.get('https://nominatim.openstreetmap.org/search', params={
        'street': 'Rue des Industries 11',
        'city': 'Conthey',
        'postalcode': '1964',
        'country': 'Switzerland',
        'format': 'json',
        'limit': 1
    }, headers={'User-Agent': 'MapEventAI-Bot/1.0'}, timeout=10)
    results = resp.json()
    if results:
        lat = float(results[0]['lat'])
        lon = float(results[0]['lon'])
        precise_fixes.append({'id': 512, 'latitude': lat, 'longitude': lon})
        print(f"  Attache ta tuque: ({lat:.6f}, {lon:.6f})")
    else:
        # Fallback: chercher "Salle polyvalente Conthey"
        coords = geocode("Salle polyvalente, Conthey, Suisse")
        if coords:
            lat, lon = coords
            precise_fixes.append({'id': 512, 'latitude': lat, 'longitude': lon})
            print(f"  Attache ta tuque (fallback salle): ({lat:.6f}, {lon:.6f})")
        else:
            # Fallback 2: chercher juste la rue
            coords = geocode("Rue des Industries, 1964 Conthey, Suisse")
            if coords:
                lat, lon = coords
                precise_fixes.append({'id': 512, 'latitude': lat, 'longitude': lon})
                print(f"  Attache ta tuque (fallback rue): ({lat:.6f}, {lon:.6f})")
            else:
                print(f"  Attache ta tuque: ÉCHEC - utilisation coords manuelles")
                # Coordonnées manuelles pour Conthey centre
                precise_fixes.append({'id': 512, 'latitude': 46.2273, 'longitude': 7.3065})
except Exception as e:
    print(f"  Erreur: {e}")

# 2. Combat de reines - Arène d'Approz
coords = geocode("Aproz, Nendaz, Valais, Suisse")
if coords:
    lat, lon = coords
    precise_fixes.append({'id': 505, 'latitude': lat, 'longitude': lon})
    print(f"  Combat de reines Approz: ({lat:.6f}, {lon:.6f})")
else:
    print(f"  Combat de reines: ÉCHEC")

# 3. Vérifier "tbd, 3900 Brig" (ID 346)
coords = geocode("3900 Brig, Suisse")
if coords:
    lat, lon = coords
    precise_fixes.append({'id': 346, 'latitude': lat, 'longitude': lon, 'location': '3900 Brig'})
    print(f"  Die Kunst der Steuererklärung: ({lat:.6f}, {lon:.6f})")

print(f"\n  Total precise fixes: {len(precise_fixes)}")

# =============================================
# Phase C: Events dates passées
# =============================================
print(f"\n{'='*60}")
print("PHASE C: Events avec dates passées")
print("="*60)

date_fixes = []

# ID 339: "Ce samedi, c'est gratuit" - récurrent
for ev in events:
    if ev['id'] == 339:
        print(f"  ID 339: {ev.get('title', '')} - date: {ev.get('date', '')} - à vérifier sur la page")
        # C'est un event récurrent, cherchons la prochaine date
        src = ev.get('source_url', '')
        if src:
            time.sleep(8)
            try:
                resp = requests.get(src, headers={'User-Agent': 'MapEventAI-Bot/1.0'}, timeout=15)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    date_div = soup.select_one('div.weekday_time')
                    if date_div:
                        date_text = date_div.get_text(strip=True)
                        print(f"    Page date: {date_text}")
                        dm = re.findall(r'(\d{2})\.(\d{2})\.(\d{4})', date_text)
                        if dm:
                            d, m, y = dm[0]
                            new_date = f"{y}-{m}-{d}"
                            if new_date >= '2026-01-01':
                                date_fixes.append({'id': 339, 'start_date': new_date, 'end_date': new_date})
                                print(f"    -> Correction: {new_date}")
                            else:
                                print(f"    -> Date encore passée: {new_date}")
            except:
                pass
        break

# ID 385: "Visite commentée publique" - date 2026-01-11 (passée)
for ev in events:
    if ev['id'] == 385:
        print(f"  ID 385: {ev.get('title', '')} - date: {ev.get('date', '')}")
        src = ev.get('source_url', '')
        if src:
            time.sleep(8)
            try:
                resp = requests.get(src, headers={'User-Agent': 'MapEventAI-Bot/1.0'}, timeout=15)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    # Chercher toutes les dates
                    dates = []
                    for dd in soup.select('div.weekday_time'):
                        dt = dd.get_text(strip=True)
                        dm = re.findall(r'(\d{2})\.(\d{2})\.(\d{4})', dt)
                        for d, m, y in dm:
                            dates.append(f"{y}-{m}-{d}")
                    
                    # Trouver la prochaine date future
                    future_dates = [d for d in dates if d >= '2026-02-05']
                    if future_dates:
                        next_date = min(future_dates)
                        date_fixes.append({'id': 385, 'start_date': next_date, 'end_date': next_date})
                        print(f"    -> Prochaine date: {next_date}")
                    else:
                        print(f"    -> Aucune date future trouvée, toutes: {dates[:5]}")
            except Exception as e:
                print(f"    -> Erreur: {e}")
        break

print(f"\n  Total date fixes: {len(date_fixes)}")

# =============================================
# APPLICATION DE TOUTES LES CORRECTIONS
# =============================================
all_fixes = venue_fixes + precise_fixes + date_fixes

# Merger les fixes par ID
merged = {}
for fix in all_fixes:
    eid = fix['id']
    if eid not in merged:
        merged[eid] = {'id': eid}
    merged[eid].update(fix)

final_fixes = list(merged.values())

print(f"\n{'='*60}")
print(f"APPLICATION: {len(final_fixes)} corrections")

if final_fixes:
    resp = requests.post(
        f'{API_URL}/api/events/fix-details-batch',
        json={'fixes': final_fixes},
        timeout=60
    )
    if resp.status_code == 200:
        result = resp.json()
        print(f"  Mis à jour: {result.get('updated', 0)}/{len(final_fixes)}")
        if result.get('errors'):
            for err in result['errors'][:5]:
                print(f"  Erreur: {err}")
    else:
        print(f"  ERREUR: {resp.text[:200]}")

print("\nDONE")
