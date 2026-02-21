"""
Goabase.net - API gratuite pour events electro/techno/house/trance.
Pas de cle API requise. JSON direct.
https://www.goabase.net/api/party/
"""
import requests, json, time, sys, re
from datetime import date
sys.stdout.reconfigure(line_buffering=True)

TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (contact: mapevent777@gmail.com)"}
API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

# ==========================================================================
# 1. Explorer l'API Goabase
# ==========================================================================
print("=" * 70)
print("GOABASE - API Electro gratuite")
print("=" * 70)

# Test de base
print("\nTest API Goabase...")
r = requests.get("https://www.goabase.net/api/party/json/", headers=HEADERS, timeout=30)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    if isinstance(data, list):
        print(f"Format: liste de {len(data)} events")
        if data:
            print(f"\nExemple record:")
            print(json.dumps(data[0], indent=2, ensure_ascii=False)[:500])
    elif isinstance(data, dict):
        print(f"Format: dict avec cles: {list(data.keys())[:10]}")
        events = data.get("events", data.get("results", data.get("parties", [])))
        if not events and "itemListElement" in data:
            events = data["itemListElement"]
        print(f"Events trouves: {len(events) if events else 0}")
        if events:
            print(f"\nExemple record:")
            print(json.dumps(events[0], indent=2, ensure_ascii=False)[:600])

time.sleep(2)

# Suisse
print("\n\n--- GOABASE SUISSE ---")
r = requests.get("https://www.goabase.net/api/party/json/?country=CH", headers=HEADERS, timeout=30)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    events_ch = data if isinstance(data, list) else data.get("itemListElement", data.get("events", []))
    print(f"Events Suisse: {len(events_ch)}")
    for e in events_ch[:5]:
        if isinstance(e, dict):
            name = e.get("name", e.get("title", "?"))
            start = e.get("startDate", e.get("date", "?"))
            loc = e.get("location", {})
            if isinstance(loc, dict):
                loc_name = loc.get("name", "?")
            else:
                loc_name = str(loc)[:50]
            print(f"  {name[:50]} | {str(start)[:10]} | {loc_name[:40]}")

time.sleep(2)

# France
print("\n\n--- GOABASE FRANCE ---")
r = requests.get("https://www.goabase.net/api/party/json/?country=FR", headers=HEADERS, timeout=30)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    events_fr = data if isinstance(data, list) else data.get("itemListElement", data.get("events", []))
    print(f"Events France: {len(events_fr)}")
    for e in events_fr[:5]:
        if isinstance(e, dict):
            name = e.get("name", e.get("title", "?"))
            start = e.get("startDate", e.get("date", "?"))
            loc = e.get("location", {})
            if isinstance(loc, dict):
                loc_name = loc.get("name", "?")
            else:
                loc_name = str(loc)[:50]
            print(f"  {name[:50]} | {str(start)[:10]} | {loc_name[:40]}")


# ==========================================================================
# 2. Edmtrain API
# ==========================================================================
print("\n\n" + "=" * 70)
print("EDMTRAIN API")
print("=" * 70)

# Essayer l'API Edmtrain (peut necessiter une cle)
print("\nTest Edmtrain...")
try:
    r = requests.get("https://edmtrain.com/api/events", params={
        "includeElectronicGenreInd": "true",
        "startDate": TODAY,
        "endDate": "2026-06-30",
    }, headers=HEADERS, timeout=30)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, dict):
            print(f"Cles: {list(data.keys())}")
            events = data.get("data", data.get("events", []))
            print(f"Events: {len(events)}")
            if events:
                print(f"Exemple: {json.dumps(events[0], indent=2, ensure_ascii=False)[:400]}")
        elif isinstance(data, list):
            print(f"Events: {len(data)}")
    else:
        print(f"Response: {r.text[:300]}")
except Exception as e:
    print(f"Erreur: {e}")

# ==========================================================================
# 3. Test aussi avec filtre type/genre sur Goabase
# ==========================================================================
print("\n\n" + "=" * 70)
print("GOABASE - Filtres avances")
print("=" * 70)

for params_str in [
    "country=CH&type=festival",
    "country=CH&type=club",
    "country=FR&type=festival",
    "country=FR&type=club",
    "country=CH&from=" + TODAY,
    "country=FR&from=" + TODAY,
]:
    print(f"\nGoabase ?{params_str}")
    try:
        r = requests.get(f"https://www.goabase.net/api/party/json/?{params_str}", headers=HEADERS, timeout=20)
        if r.status_code == 200:
            data = r.json()
            events = data if isinstance(data, list) else data.get("itemListElement", data.get("events", []))
            print(f"  {len(events)} events")
            for e in events[:3]:
                if isinstance(e, dict):
                    name = e.get("name", "?")
                    start = str(e.get("startDate", "?"))[:10]
                    print(f"    {name[:50]} | {start}")
        else:
            print(f"  Status: {r.status_code}")
        time.sleep(1)
    except Exception as ex:
        print(f"  Erreur: {ex}")
