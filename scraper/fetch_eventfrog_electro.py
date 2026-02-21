"""
Fetch electronic music events from Eventfrog API (Swiss events)
and other available sources.
"""
import requests, json, time, sys, re
from datetime import date, datetime
sys.stdout.reconfigure(line_buffering=True)

TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (contact: mapevent777@gmail.com)"}
API_BACKEND = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

all_events = []

# ==========================================================================
# 1. Eventfrog API - tester differentes URLs
# ==========================================================================
print("=" * 70)
print("1. Exploration Eventfrog API")
print("=" * 70)

# Tester les endpoints potentiels
test_urls = [
    "https://api.eventfrog.ch/api/v1/events",
    "https://api.eventfrog.net/api/v1/events",
    "https://eventfrog.ch/api/events",
    "https://eventfrog.ch/api/v1/events",
    "https://api.eventfrog.ch/events",
    "https://api.eventfrog.net/events",
    "https://docs.api.eventfrog.net/events",
    "https://eventfrog.ch/api/v1/events?category=house-techno",
    "https://api.eventfrog.ch/api/v1/events?categorySlug=house-techno-161",
    "https://api.eventfrog.ch/v1/events",
    "https://api.eventfrog.ch/v1/events?category=house-techno",
]

for url in test_urls:
    try:
        r = requests.get(url, headers={
            **HEADERS,
            "Accept": "application/json",
        }, timeout=10, allow_redirects=True)
        content_type = r.headers.get("Content-Type", "")
        if "json" in content_type:
            data = r.json()
            if isinstance(data, dict):
                keys = list(data.keys())[:5]
                count = data.get("total", data.get("count", data.get("totalResults", "?")))
                print(f"  OK {url}")
                print(f"     Keys: {keys}, count: {count}")
                if data.get("events") or data.get("results") or data.get("data"):
                    items = data.get("events") or data.get("results") or data.get("data")
                    if items:
                        print(f"     Items: {len(items)}")
                        print(f"     Sample: {json.dumps(items[0], indent=2, ensure_ascii=False)[:300]}")
            elif isinstance(data, list) and data:
                print(f"  OK {url}: {len(data)} items")
                print(f"     Sample: {json.dumps(data[0], indent=2, ensure_ascii=False)[:300]}")
        else:
            if r.status_code != 200:
                print(f"  {r.status_code} {url}")
            else:
                print(f"  {r.status_code} {url} (HTML, not JSON)")
    except Exception as e:
        print(f"  ERR {url}: {e}")
    time.sleep(0.5)


# ==========================================================================
# 2. Essayer Eventfrog via les pages web (JSON embarque)
# ==========================================================================
print("\n" + "=" * 70)
print("2. Eventfrog - scrape JSON from web pages")
print("=" * 70)

categories = [
    "house-techno-161",
    "transe-ambiance-162",
    "drum-n-bass-164",
    "clubbing-51",
]

for cat in categories:
    url = f"https://eventfrog.ch/fr/r/soiree-fete/{cat}.html"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            text = r.text
            # Chercher du JSON-LD (schema.org)
            import re
            ld_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.DOTALL)
            if ld_matches:
                print(f"  {cat}: {len(ld_matches)} JSON-LD blocks")
                for ld in ld_matches[:3]:
                    try:
                        data = json.loads(ld)
                        if isinstance(data, dict):
                            t = data.get("@type", "?")
                            name = data.get("name", "")[:60]
                            print(f"    Type: {t}, Name: {name}")
                            if t == "Event":
                                loc = data.get("location", {})
                                geo = loc.get("geo", {})
                                all_events.append({
                                    "_source": "eventfrog",
                                    "title": data.get("name", ""),
                                    "date": data.get("startDate", "")[:10],
                                    "time": data.get("startDate", "")[11:16] if "T" in data.get("startDate", "") else None,
                                    "location": f"{loc.get('name', '')}, {loc.get('address', {}).get('streetAddress', '')}, {loc.get('address', {}).get('postalCode', '')} {loc.get('address', {}).get('addressLocality', '')}",
                                    "latitude": float(geo.get("latitude", 0)) if geo.get("latitude") else None,
                                    "longitude": float(geo.get("longitude", 0)) if geo.get("longitude") else None,
                                    "source_url": data.get("url", ""),
                                })
                        elif isinstance(data, list):
                            events_in_list = [d for d in data if d.get("@type") == "Event"]
                            print(f"    List of {len(data)}, {len(events_in_list)} events")
                            for d in events_in_list:
                                loc = d.get("location", {})
                                geo = loc.get("geo", {}) if isinstance(loc, dict) else {}
                                addr = loc.get("address", {}) if isinstance(loc, dict) else {}
                                if isinstance(addr, str):
                                    addr = {"streetAddress": addr}
                                all_events.append({
                                    "_source": "eventfrog",
                                    "title": d.get("name", ""),
                                    "date": d.get("startDate", "")[:10],
                                    "time": d.get("startDate", "")[11:16] if "T" in d.get("startDate", "") else None,
                                    "location": f"{loc.get('name', '') if isinstance(loc, dict) else ''}, {addr.get('streetAddress', '')}, {addr.get('postalCode', '')} {addr.get('addressLocality', '')}",
                                    "latitude": float(geo.get("latitude", 0)) if geo.get("latitude") else None,
                                    "longitude": float(geo.get("longitude", 0)) if geo.get("longitude") else None,
                                    "source_url": d.get("url", ""),
                                })
                    except json.JSONDecodeError:
                        pass
            else:
                print(f"  {cat}: pas de JSON-LD")
                
            # Aussi chercher __NEXT_DATA__ ou window.__data__ patterns
            next_data = re.findall(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', text, re.DOTALL)
            if next_data:
                print(f"  {cat}: Found __NEXT_DATA__")
                
            # Chercher des URLs d'events
            event_links = re.findall(r'href="(/fr/p/soiree-fete/[^"]+\.html)"', text)
            if event_links:
                print(f"  {cat}: {len(event_links)} event links found on page")
                for link in event_links[:5]:
                    print(f"    {link[:80]}")
        else:
            print(f"  {cat}: {r.status_code}")
    except Exception as e:
        print(f"  {cat}: {e}")
    time.sleep(2)


# ==========================================================================
# 3. Scrape individual Eventfrog event pages for JSON-LD
# ==========================================================================
print("\n" + "=" * 70)
print("3. Eventfrog - Individual event pages")
print("=" * 70)

# Extraire les liens depuis la page house-techno
try:
    r = requests.get("https://eventfrog.ch/fr/r/soiree-fete/house-techno-161.html", headers=HEADERS, timeout=15)
    event_links = re.findall(r'href="(/fr/p/[^"]+\.html)"', r.text)
    # Dedup
    event_links = list(dict.fromkeys(event_links))
    print(f"  Links house-techno: {len(event_links)}")
    
    # Aussi page trance
    r2 = requests.get("https://eventfrog.ch/fr/r/soiree-fete/transe-ambiance-162.html", headers=HEADERS, timeout=15)
    links2 = re.findall(r'href="(/fr/p/[^"]+\.html)"', r2.text)
    event_links.extend(links2)
    event_links = list(dict.fromkeys(event_links))
    print(f"  Total links (+ trance): {len(event_links)}")
    
    # Visiter chaque page pour JSON-LD
    for i, link in enumerate(event_links[:30]):  # max 30
        url = f"https://eventfrog.ch{link}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                ld_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', r.text, re.DOTALL)
                for ld in ld_matches:
                    try:
                        data = json.loads(ld)
                        if isinstance(data, dict) and data.get("@type") == "Event":
                            loc = data.get("location", {})
                            if isinstance(loc, dict):
                                geo = loc.get("geo", {})
                                addr = loc.get("address", {})
                                if isinstance(addr, str):
                                    addr = {"streetAddress": addr}
                                
                                lat = float(geo.get("latitude", 0)) if geo.get("latitude") else None
                                lng = float(geo.get("longitude", 0)) if geo.get("longitude") else None
                                
                                if lat and lng:
                                    location = f"{loc.get('name', '')}, {addr.get('streetAddress', '')}, {addr.get('postalCode', '')} {addr.get('addressLocality', '')}".strip(", ")
                                    
                                    evt = {
                                        "_source": "eventfrog",
                                        "title": data.get("name", ""),
                                        "date": data.get("startDate", "")[:10],
                                        "time": data.get("startDate", "")[11:16] if "T" in data.get("startDate", "") else None,
                                        "end_date": data.get("endDate", "")[:10] if data.get("endDate") else None,
                                        "end_time": data.get("endDate", "")[11:16] if data.get("endDate") and "T" in data.get("endDate", "") else None,
                                        "location": location,
                                        "latitude": lat,
                                        "longitude": lng,
                                        "source_url": url,
                                        "description": data.get("description", "")[:500] if data.get("description") else "",
                                    }
                                    all_events.append(evt)
                                    print(f"  [{i+1}] {evt['title'][:50]} | {evt['date']} | {evt['location'][:40]}")
                    except json.JSONDecodeError:
                        pass
        except:
            pass
        time.sleep(8)  # Respect Eventfrog (8s entre requetes)
except Exception as e:
    print(f"  Erreur: {e}")


# ==========================================================================
# 4. Goabase - events supplementaires par ville
# ==========================================================================
print("\n" + "=" * 70)
print("4. Goabase - par ville")
print("=" * 70)

cities = [
    ("Lausanne", "46.52", "6.63"),
    ("Bern", "46.95", "7.45"),
    ("Basel", "47.56", "7.59"),
    ("Lucerne", "47.05", "8.31"),
    ("Strasbourg", "48.58", "7.75"),
    ("Annecy", "45.90", "6.13"),
    ("Grenoble", "45.19", "5.72"),
    ("Dijon", "47.32", "5.04"),
    ("Besancon", "47.24", "6.03"),
    ("Mulhouse", "47.75", "7.34"),
]

BASE_GOA = "https://www.goabase.net/api/party"

for city_name, lat, lon in cities:
    try:
        r = requests.get(f"{BASE_GOA}/json/?geoloc={city_name}&georad=50&limit=100", headers=HEADERS, timeout=15)
        if r.status_code == 200:
            parties = r.json().get("partylist", [])
            # Filtrer futures
            future = [p for p in parties if p.get("dateStart", "") >= TODAY]
            if future:
                print(f"  {city_name}: {len(future)} events futurs (sur {len(parties)} total)")
                for p in future[:3]:
                    print(f"    {p.get('nameParty', '')[:50]} | {p.get('dateStart', '')[:10]} | {p.get('nameCountry', '')} {p.get('nameTown', '')}")
                all_events.extend([{**p, "_source": "goabase_city"} for p in future])
            else:
                print(f"  {city_name}: {len(parties)} events, 0 futurs")
        else:
            print(f"  {city_name}: {r.status_code}")
    except Exception as e:
        print(f"  {city_name}: {e}")
    time.sleep(1)


# ==========================================================================
# RESULTAT FINAL
# ==========================================================================
print("\n" + "=" * 70)
print("RESULTAT FINAL")
print("=" * 70)

# Dedup par titre+date
seen = set()
unique = []
for e in all_events:
    if e.get("_source") in ("goabase_city",):
        key = f"{e.get('nameParty', '').lower()}|{e.get('dateStart', '')[:10]}"
    else:
        key = f"{e.get('title', '').lower()}|{e.get('date', '')[:10]}"
    if key not in seen and key != "|":
        seen.add(key)
        unique.append(e)

sources = {}
for e in unique:
    src = e.get("_source", "goabase_city")
    sources[src] = sources.get(src, 0) + 1

print(f"Total unique: {len(unique)}")
for src, cnt in sorted(sources.items(), key=lambda x: -x[1]):
    print(f"  {src}: {cnt}")

# Sauvegarder
with open("scraper/eventfrog_goabase_extra.json", "w", encoding="utf-8") as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)

print(f"\nSauvegarde: scraper/eventfrog_goabase_extra.json")
