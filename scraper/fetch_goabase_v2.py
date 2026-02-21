"""
Goabase API v2 - avec les bons parametres d'apres la doc officielle.
API gratuite, pas de cle, events electro/techno/psy/house.
"""
import requests, json, time, sys, re
from datetime import date
sys.stdout.reconfigure(line_buffering=True)

TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (contact: mapevent777@gmail.com)"}
API_BACKEND = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

BASE = "https://www.goabase.net/api/party"

# 1. Lister les pays
print("=== Pays disponibles ===")
r = requests.get(f"{BASE}/json/?country=list-all", headers=HEADERS, timeout=20)
if r.status_code == 200:
    data = r.json()
    countries = data.get("partylist", data.get("countryList", []))
    if isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, list):
                print(f"  Cle '{key}': {len(val)} items")
                for item in val[:10]:
                    print(f"    {item}")
            elif isinstance(val, (str, int)):
                print(f"  {key}: {val}")

time.sleep(1)

# 2. Tous les events a venir (limite 500)
print("\n=== Tous les events a venir (max 500) ===")
r = requests.get(f"{BASE}/json/?limit=500", headers=HEADERS, timeout=30)
if r.status_code == 200:
    data = r.json()
    parties = data.get("partylist", [])
    print(f"Events: {len(parties)}")
    
    if parties:
        print(f"\n  Exemple 1er event:")
        print(json.dumps(parties[0], indent=2, ensure_ascii=False)[:600])
        
        # Stats par pays
        countries_count = {}
        for p in parties:
            c = p.get("nameCountry", p.get("country", "?"))
            countries_count[c] = countries_count.get(c, 0) + 1
        
        print(f"\n  Par pays:")
        for c, cnt in sorted(countries_count.items(), key=lambda x: -x[1])[:15]:
            print(f"    {c}: {cnt}")

time.sleep(1)

# 3. JSON-LD format (schema.org)
print("\n=== Format JSON-LD ===")
r = requests.get(f"{BASE}/jsonld/?limit=5", headers=HEADERS, timeout=20)
if r.status_code == 200:
    data = r.json()
    events = data.get("itemListElement", [])
    print(f"Events JSON-LD: {len(events)}")
    if events:
        print(json.dumps(events[0], indent=2, ensure_ascii=False)[:600])

time.sleep(1)

# 4. Geoloc autour des villes suisses
print("\n=== Events autour de Geneve (100km) ===")
r = requests.get(f"{BASE}/json/?geoloc=Geneva&limit=100", headers=HEADERS, timeout=20)
if r.status_code == 200:
    data = r.json()
    parties = data.get("partylist", [])
    print(f"Events: {len(parties)}")
    for p in parties[:5]:
        name = p.get("nameParty", "?")
        start = str(p.get("dateStart", "?"))[:10]
        town = p.get("nameTown", "?")
        country = p.get("nameCountry", "?")
        print(f"  {name[:50]} | {start} | {town} ({country})")

time.sleep(1)

print("\n=== Events autour de Zurich (100km) ===")
r = requests.get(f"{BASE}/json/?geoloc=Zurich&limit=100", headers=HEADERS, timeout=20)
if r.status_code == 200:
    data = r.json()
    parties = data.get("partylist", [])
    print(f"Events: {len(parties)}")
    for p in parties[:5]:
        name = p.get("nameParty", "?")
        start = str(p.get("dateStart", "?"))[:10]
        town = p.get("nameTown", "?")
        print(f"  {name[:50]} | {start} | {town}")

time.sleep(1)

print("\n=== Events autour de Paris (200km) ===")
r = requests.get(f"{BASE}/json/?geoloc=Paris&radius=200&limit=100", headers=HEADERS, timeout=20)
if r.status_code == 200:
    data = r.json()
    parties = data.get("partylist", [])
    print(f"Events: {len(parties)}")
    for p in parties[:5]:
        name = p.get("nameParty", "?")
        start = str(p.get("dateStart", "?"))[:10]
        town = p.get("nameTown", "?")
        print(f"  {name[:50]} | {start} | {town}")

time.sleep(1)

# 5. Par type d'event
print("\n=== Par type ===")
for etype in ["festival", "club", "indoor", "openair"]:
    r = requests.get(f"{BASE}/json/?eventtype={etype}&limit=10", headers=HEADERS, timeout=15)
    if r.status_code == 200:
        data = r.json()
        parties = data.get("partylist", [])
        print(f"  {etype}: {len(parties)} events")
    time.sleep(0.5)

# 6. Recherche par mot-cle
print("\n=== Recherche 'techno' ===")
r = requests.get(f"{BASE}/json/?search=techno&limit=50", headers=HEADERS, timeout=20)
if r.status_code == 200:
    data = r.json()
    parties = data.get("partylist", [])
    print(f"Events 'techno': {len(parties)}")
    for p in parties[:5]:
        name = p.get("nameParty", "?")
        start = str(p.get("dateStart", "?"))[:10]
        town = p.get("nameTown", "?")
        country = p.get("nameCountry", "?")
        print(f"  {name[:50]} | {start} | {town} ({country})")
