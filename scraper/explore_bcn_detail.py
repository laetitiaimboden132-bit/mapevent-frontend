"""Explore format détaillé Barcelone + Lisbonne"""
import requests, json

HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}

# === BARCELONE - Détails ===
print("BARCELONE - Détails d'un événement")
print("=" * 60)
url = "https://opendata-ajuntament.barcelona.cat/data/dataset/2767159c-1c98-46b8-a686-2b25b40cb053/resource/59b9c807-f6c1-4c10-ac51-1ace65485079/download"
r = requests.get(url, headers=HEADERS, timeout=30)
data = r.json()
print(f"Total: {len(data)} events")

# 3 samples détaillés
for item in data[:3]:
    print(f"\n--- {item.get('name')} ---")
    print(f"  register_id: {item.get('register_id')}")
    print(f"  status: {item.get('status')}")
    
    # Adresses
    addrs = item.get('addresses', [])
    for a in addrs[:1]:
        print(f"  Address: {a.get('address_name')} {a.get('start_street_number')}, {a.get('town')}")
        print(f"  Place: {a.get('place')}")
        print(f"  District: {a.get('district_name')}")
        loc = a.get('location', {})
        geoms = loc.get('geometries', [])
        for g in geoms:
            print(f"  Coords (UTM?): {g.get('coordinates')}")
    
    # Values (dates, etc)
    values = item.get('values', [])
    print(f"  Values ({len(values)}):")
    for v in values[:5]:
        print(f"    {v}")
    
    # Classifications
    classifications = item.get('classifications_data', [])
    print(f"  Classifications ({len(classifications)}):")
    for c in classifications[:5]:
        print(f"    {c}")
    
    # Secondary filters
    sf = item.get('secondary_filters_data', [])
    print(f"  Filters ({len(sf)}):")
    for f in sf[:3]:
        print(f"    {f}")

# === LISBONNE ===
print("\n\n" + "=" * 60)
print("LISBONNE - Détails d'un événement")
print("=" * 60)
try:
    r = requests.get("https://www.agendalx.pt/wp-json/agendalx/v1/events", headers=HEADERS, timeout=15)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list):
            print(f"Total: {len(data)} events")
            for item in data[:3]:
                print(f"\n  Clés: {list(item.keys())[:20]}")
                print(f"  {json.dumps(item, indent=2, ensure_ascii=False)[:1500]}")
        elif isinstance(data, dict):
            print(f"Clés: {list(data.keys())}")
            # Check for common CKAN / WP patterns
            for key in ['events', 'data', 'results', 'items']:
                if key in data:
                    items = data[key]
                    print(f"  {key}: {len(items)} items")
                    if items:
                        print(f"  Clés: {list(items[0].keys())[:20]}")
                        print(f"  Sample: {json.dumps(items[0], indent=2, ensure_ascii=False)[:1500]}")
                    break
            else:
                print(f"  {json.dumps(data, indent=2, ensure_ascii=False)[:2000]}")
except Exception as e:
    print(f"Erreur: {e}")

# Also try Cantanhede
print("\n\nCANTANHEDE:")
try:
    r = requests.get("https://cm-cantanhede.pt/mcsite/api/json/agenda", headers=HEADERS, timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, list):
            print(f"Total: {len(data)}")
            if data: print(json.dumps(data[0], indent=2, ensure_ascii=False)[:800])
        elif isinstance(data, dict):
            print(f"Clés: {list(data.keys())}")
except Exception as e:
    print(f"Erreur: {e}")
