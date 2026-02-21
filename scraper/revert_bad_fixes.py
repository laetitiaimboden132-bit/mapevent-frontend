"""
REVERT des corrections erronées du script verify_failed_geocodes.py.
Le script avait extrait juste "3960 Sierre" ou "1260 Nyon" au lieu de l'adresse complète,
déplaçant les pointeurs au centre-ville au lieu du vrai lieu.
"""
import requests, sys, io, time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

def geocode(query):
    try:
        resp = requests.get('https://nominatim.openstreetmap.org/search', params={
            'q': query, 'format': 'json', 'limit': 1, 'countrycodes': 'ch'
        }, headers={'User-Agent': 'MapEventAI-Fix/1.0'}, timeout=10)
        results = resp.json()
        if results:
            return float(results[0]['lat']), float(results[0]['lon']), results[0].get('display_name', '')
    except:
        pass
    return None, None, ''

fixes = []

# 1) Colline de Daval (2 events) → coordonnées OFFICIELLES du site sierretourisme.ch
print("1) Asperges en folie à Daval → Colline de Daval 5 (coords officielles)")
fixes.append({'id': 2084, 'latitude': 46.2743089, 'longitude': 7.5143782})
print("   GPS: 46.2743089, 7.5143782")

print("2) Initiation dégustation vin → Colline de Daval 5 (coords officielles)")
fixes.append({'id': 2071, 'latitude': 46.2743089, 'longitude': 7.5143782})
print("   GPS: 46.2743089, 7.5143782")

# 3) Déjeuner du monde → Avenue des Écoles 6, Sierre (PAS centre-ville!)
print("\n3) Déjeuner du monde → Avenue des Écoles 6, Sierre")
lat, lon, name = geocode("Avenue des Écoles 6, 3960 Sierre")
if lat:
    fixes.append({'id': 2085, 'latitude': lat, 'longitude': lon})
    print(f"   GPS: {lat:.6f}, {lon:.6f} ({name[:50]})")
time.sleep(1.5)

# 4) Caribana Festival → Port de Crans, Nyon (PAS centre de Nyon!)
print("\n4) Caribana Festival → Port de Crans, Nyon")
lat, lon, name = geocode("Port de Crans, Nyon")
if lat:
    fixes.append({'id': 2140, 'latitude': lat, 'longitude': lon})
    print(f"   GPS: {lat:.6f}, {lon:.6f} ({name[:50]})")
else:
    # Coordonnées originales connues
    fixes.append({'id': 2140, 'latitude': 46.3591007, 'longitude': 6.2183964})
    print("   GPS: 46.3591007, 6.2183964 (originales)")
time.sleep(1.5)

# 5) Festival Rive Jazzy → Quartier de Rive, Nyon (PAS centre de Nyon!)
print("\n5) Festival Rive Jazzy → Quartier de Rive, Nyon")
lat, lon, name = geocode("Rive, Nyon")
if lat:
    fixes.append({'id': 2142, 'latitude': lat, 'longitude': lon})
    print(f"   GPS: {lat:.6f}, {lon:.6f} ({name[:50]})")
else:
    fixes.append({'id': 2142, 'latitude': 46.3820585, 'longitude': 6.2402791})
    print("   GPS: 46.3820585, 6.2402791 (originales)")
time.sleep(1.5)

# 6) Paléo Festival → Route de St-Cergue, Nyon (PAS centre de Nyon!)
print("\n6) Paléo Festival → Route de St-Cergue 312, Nyon")
lat, lon, name = geocode("Paléo Festival, Nyon")
if lat:
    fixes.append({'id': 1140, 'latitude': lat, 'longitude': lon})
    print(f"   GPS: {lat:.6f}, {lon:.6f} ({name[:50]})")
else:
    fixes.append({'id': 1140, 'latitude': 46.4028147, 'longitude': 6.2107769})
    print("   GPS: 46.4028147, 6.2107769 (originales)")
time.sleep(1.5)

# 7) Triathlon Genève → Genève Plage (PAS juste Cologny centre!)
print("\n7) Triathlon Genève → Genève Plage, Cologny")
lat, lon, name = geocode("Genève Plage, Cologny")
if lat:
    fixes.append({'id': 1174, 'latitude': lat, 'longitude': lon})
    print(f"   GPS: {lat:.6f}, {lon:.6f} ({name[:50]})")
else:
    fixes.append({'id': 1174, 'latitude': 46.2140225, 'longitude': 6.1730199})
    print("   GPS: 46.2140225, 6.1730199 (originales)")
time.sleep(1.5)

# Les corrections OK à garder:
# - Montreux Jazz (Rue du Théâtre 5 → correct)
# - Soirée fondue luge (La Lécherette → probablement OK)
# - Big Big Horse Party (Ch. de l'Eglise → probablement OK)
# Vérifions quand même

# 8) Soirée fondue luge - vérifier
print("\n8) Soirée fondue luge → Cabane des Monts Chevreuils, Les Mosses")
lat, lon, name = geocode("Cabane des Monts Chevreuils, Les Mosses")
if lat:
    fixes.append({'id': 1158, 'latitude': lat, 'longitude': lon})
    print(f"   GPS: {lat:.6f}, {lon:.6f} ({name[:50]})")
else:
    lat, lon, name = geocode("La Lécherette, Les Mosses")
    if lat:
        fixes.append({'id': 1158, 'latitude': lat, 'longitude': lon})
        print(f"   GPS: {lat:.6f}, {lon:.6f} ({name[:50]})")
    else:
        fixes.append({'id': 1158, 'latitude': 46.4676196, 'longitude': 7.1243325})
        print("   GPS: 46.4676196, 7.1243325 (originales)")
time.sleep(1.5)

# Appliquer
print(f"\n=== APPLICATION DE {len(fixes)} REVERTS/CORRECTIONS ===")
resp = requests.post(f'{API_URL}/api/events/fix-details-batch',
                    json={'fixes': fixes}, timeout=30)
if resp.status_code == 200:
    result = resp.json()
    print(f"  ✅ {result.get('updated', 0)}/{result.get('total', 0)} corrigés")
else:
    print(f"  ❌ {resp.status_code}: {resp.text[:200]}")

print("\nTerminé!")
