"""
Geocoder toutes les adresses culturevalais et ajouter les noms de lieux.
Aussi: vérifier et corriger les events des AUTRES sources.
"""
import requests, sys, io, json, time, re
from bs4 import BeautifulSoup

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])

# Charger les fixes v2
with open('culturevalais_fixes_v2.json', 'r', encoding='utf-8') as f:
    prev_fixes = json.load(f)

# Map ID -> fix
fix_map = {f['id']: f for f in prev_fixes}

# Events culturevalais
cv_events = [ev for ev in events if 'culturevalais.ch' in (ev.get('source_url', '') or '')]

# AUSSI: chercher "Combat de reines Approz"
approz_events = [ev for ev in events if 'approz' in (ev.get('title', '') or '').lower() or 
                 'combat de reines' in (ev.get('title', '') or '').lower() or
                 'reines' in (ev.get('title', '') or '').lower()]

# AUSSI: chercher "attache ta tuque"
tuque_events = [ev for ev in events if 'tuque' in (ev.get('title', '') or '').lower() or
                'industries' in (ev.get('location', '') or '').lower() or
                'conthey' in (ev.get('location', '') or '').lower()]

print(f"Events culturevalais: {len(cv_events)}")
for e in approz_events:
    print(f"  Approz: ID {e['id']}: {e.get('title','')[:40]} @ {e.get('location','')[:50]}")
for e in tuque_events:
    print(f"  Tuque: ID {e['id']}: {e.get('title','')[:40]} @ {e.get('location','')[:50]}")

# Geocoder une adresse
geocode_cache = {}
def geocode(address):
    if address in geocode_cache:
        return geocode_cache[address]
    
    time.sleep(1.5)
    
    # Nettoyer l'adresse pour Nominatim
    clean = address.replace('tbd, ', '')
    
    try:
        resp = requests.get('https://nominatim.openstreetmap.org/search', params={
            'q': clean + ', Suisse',
            'format': 'json',
            'limit': 1,
            'countrycodes': 'ch'
        }, headers={'User-Agent': 'MapEventAI-Bot/1.0'}, timeout=10)
        
        results = resp.json()
        if results:
            lat = float(results[0]['lat'])
            lon = float(results[0]['lon'])
            geocode_cache[address] = (lat, lon)
            return (lat, lon)
        
        # Fallback: essayer juste la rue et le CP ville
        # Extraire "Rue xxx, XXXX Ville"
        m = re.search(r'((?:Rue|Ch\.|Chemin|Route|Avenue|Av\.|Boulevard|Place|Quai|Rte|Passage|Bahnhofstr)[^,]+),\s*(\d{4}\s+\S+)', clean)
        if m:
            street_cp = f"{m.group(1)}, {m.group(2)}, Suisse"
            time.sleep(1)
            resp2 = requests.get('https://nominatim.openstreetmap.org/search', params={
                'q': street_cp,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'ch'
            }, headers={'User-Agent': 'MapEventAI-Bot/1.0'}, timeout=10)
            
            results2 = resp2.json()
            if results2:
                lat = float(results2[0]['lat'])
                lon = float(results2[0]['lon'])
                geocode_cache[address] = (lat, lon)
                return (lat, lon)
        
        # Dernier fallback: juste CP ville
        cp_match = re.search(r'(\d{4}\s+\S+)', clean)
        if cp_match:
            time.sleep(1)
            resp3 = requests.get('https://nominatim.openstreetmap.org/search', params={
                'q': cp_match.group(1) + ', Suisse',
                'format': 'json',
                'limit': 1,
                'countrycodes': 'ch'
            }, headers={'User-Agent': 'MapEventAI-Bot/1.0'}, timeout=10)
            results3 = resp3.json()
            if results3:
                lat = float(results3[0]['lat'])
                lon = float(results3[0]['lon'])
                geocode_cache[address] = (lat, lon)
                return (lat, lon)
    except Exception as e:
        print(f"  Geocode error: {e}")
    
    geocode_cache[address] = None
    return None


# =============================================
# Phase 1: Geocoder les events culturevalais
# =============================================
print(f"\n{'='*60}")
print("PHASE 1: Geocodage culturevalais.ch")
print(f"{'='*60}")

coord_fixes = []

for ev in cv_events:
    eid = ev['id']
    loc = ev.get('location', '') or ''
    
    if not loc or loc == 'tbd, 3900 Brig':
        print(f"  ID {eid}: {ev.get('title', '')[:40]} - SKIP (pas d'adresse)")
        continue
    
    coords = geocode(loc)
    if coords:
        lat, lon = coords
        old_lat = ev.get('latitude', 0) or 0
        old_lon = ev.get('longitude', 0) or 0
        
        # Calculer la distance
        import math
        dlat = (lat - old_lat) * 111320
        dlon = (lon - old_lon) * 111320 * math.cos(math.radians(lat))
        dist = math.sqrt(dlat**2 + dlon**2)
        
        if dist > 50:  # Plus de 50m de différence
            coord_fixes.append({
                'id': eid,
                'latitude': lat,
                'longitude': lon
            })
            print(f"  ID {eid}: {loc[:40]} -> ({lat:.5f}, {lon:.5f}) [décalage {dist:.0f}m]")
        else:
            print(f"  ID {eid}: OK ({dist:.0f}m)")
    else:
        print(f"  ID {eid}: ÉCHEC geocodage pour '{loc[:40]}'")

# =============================================
# Phase 2: Combat de reines Approz
# =============================================
print(f"\n{'='*60}")
print("PHASE 2: Combat de reines Approz")
print(f"{'='*60}")

for ev in approz_events:
    eid = ev['id']
    print(f"  ID {eid}: {ev.get('title', '')}")
    print(f"    Location: {ev.get('location', '')}")
    print(f"    Coords: ({ev.get('latitude', '')}, {ev.get('longitude', '')})")
    print(f"    Date: {ev.get('date', '')}")
    print(f"    Source: {ev.get('source_url', '')}")
    
    # Géocoder "Route d'Approz, 1994 Aproz (Nendaz), Suisse"
    # C'est la commune d'Aproz/Nendaz
    # L'arène des combats de reines est à Aproz
    coords = geocode("Aproz, 1994 Nendaz")
    if coords:
        lat, lon = coords
        print(f"    -> Geocode: ({lat:.5f}, {lon:.5f})")
        coord_fixes.append({
            'id': eid,
            'latitude': lat,
            'longitude': lon,
            'location': "Arène des combats de reines, 1994 Aproz (Nendaz)"
        })

# =============================================
# Phase 3: Attache ta tuque / Conthey
# =============================================
print(f"\n{'='*60}")
print("PHASE 3: Attache ta tuque / Conthey")
print(f"{'='*60}")

for ev in tuque_events:
    eid = ev['id']
    print(f"  ID {eid}: {ev.get('title', '')}")
    print(f"    Location: {ev.get('location', '')}")
    print(f"    Source: {ev.get('source_url', '')}")
    
    # L'utilisateur dit: Rue des Industries 11, Conthey
    coords = geocode("Rue des Industries 11, 1964 Conthey")
    if coords:
        lat, lon = coords
        print(f"    -> Geocode: ({lat:.5f}, {lon:.5f})")
        coord_fixes.append({
            'id': eid,
            'latitude': lat,
            'longitude': lon,
            'location': "Rue des Industries 11, 1964 Conthey"
        })

# =============================================
# APPLICATION
# =============================================
print(f"\n{'='*60}")
print(f"TOTAL CORRECTIONS COORDS: {len(coord_fixes)}")

if coord_fixes:
    resp = requests.post(
        f'{API_URL}/api/events/fix-details-batch',
        json={'fixes': coord_fixes},
        timeout=60
    )
    if resp.status_code == 200:
        result = resp.json()
        print(f"  Mis à jour: {result.get('updated', 0)}/{len(coord_fixes)}")
        if result.get('errors'):
            for err in result['errors'][:5]:
                print(f"  Erreur: {err}")
    else:
        print(f"  ERREUR: {resp.text[:200]}")

# Sauvegarder le cache
with open('geocode_cache_cv.json', 'w', encoding='utf-8') as f:
    json.dump({k: v for k, v in geocode_cache.items() if v}, f, ensure_ascii=False, indent=2)

print("\nDONE")
