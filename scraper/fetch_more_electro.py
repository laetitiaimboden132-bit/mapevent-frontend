"""
Recherche d'events electro supplementaires.
Sources: TiBillet API, Goabase (recherches avancees), Ticketmaster Discovery API.
"""
import requests, json, time, sys, re
from datetime import date
sys.stdout.reconfigure(line_buffering=True)

TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (contact: mapevent777@gmail.com)"}
API_BACKEND = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

all_new = []

# ==========================================================================
# 1. TiBillet API - events electro
# ==========================================================================
print("=" * 70)
print("1. TiBillet API")
print("=" * 70)

try:
    r = requests.get("https://tibillet.org/api/v2/events/", headers=HEADERS, timeout=20)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        if isinstance(data, dict):
            print(f"  Cles: {list(data.keys())[:10]}")
            events = data.get("results", data.get("events", []))
            print(f"  Events: {len(events)}")
            if events:
                print(f"  Exemple: {json.dumps(events[0], indent=2, ensure_ascii=False)[:400]}")
        elif isinstance(data, list):
            print(f"  Events: {len(data)}")
    else:
        print(f"  Response: {r.text[:300]}")
except Exception as e:
    print(f"  Erreur: {e}")

# Essayer aussi les URLs alternatives
for url in [
    "https://tibillet.org/api/events/",
    "https://lespass.tibillet.org/api/v2/events/",
    "https://demo.tibillet.org/api/v2/events/",
]:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            events = data.get("results", []) if isinstance(data, dict) else data
            if events:
                print(f"  {url}: {len(events)} events!")
                print(f"    Exemple: {json.dumps(events[0], indent=2, ensure_ascii=False)[:300]}")
    except:
        pass
    time.sleep(0.5)


# ==========================================================================
# 2. Goabase - Recherches par genre specifiques
# ==========================================================================
print("\n" + "=" * 70)
print("2. Goabase - Recherches par genre")
print("=" * 70)

BASE_GOA = "https://www.goabase.net/api/party"

genres = ["techno", "house", "drum and bass", "trance", "dubstep", 
          "minimal", "hardstyle", "acid", "ambient", "progressive",
          "electro", "disco", "breakbeat", "garage", "jungle"]

for genre in genres:
    r = requests.get(f"{BASE_GOA}/json/?search={genre}&limit=50", headers=HEADERS, timeout=15)
    if r.status_code == 200:
        parties = r.json().get("partylist", [])
        # Filtrer Suisse + France
        ch_fr = [p for p in parties if p.get("isoCountry") in ("CH", "FR")]
        if ch_fr:
            print(f"  '{genre}': {len(parties)} total, {len(ch_fr)} CH/FR")
            all_new.extend(ch_fr)
        else:
            total = len(parties)
            if total > 0:
                top_countries = {}
                for p in parties:
                    c = p.get("isoCountry", "?")
                    top_countries[c] = top_countries.get(c, 0) + 1
                print(f"  '{genre}': {total} total, 0 CH/FR (top: {dict(list(sorted(top_countries.items(), key=lambda x:-x[1]))[:3])})")
    time.sleep(1)

# Dedup par ID
seen_ids = set()
unique_new = []
for p in all_new:
    pid = p.get("id")
    if pid and pid not in seen_ids:
        seen_ids.add(pid)
        unique_new.append(p)

print(f"\n  Goabase genres CH/FR unique: {len(unique_new)}")


# ==========================================================================
# 3. Ticketmaster Discovery API (gratuit avec cle)
# ==========================================================================
print("\n" + "=" * 70)
print("3. Ticketmaster Discovery API")
print("=" * 70)

# Ticketmaster a une API gratuite avec 5000 req/jour
# Cle demo publique connue
TM_KEY = "GDEgVE4eNQMOx0LgsNRb3uyXIlHQVlVj"  # demo key from their docs

for country, city in [("CH", "Geneva"), ("CH", "Zurich"), ("FR", "Paris"), ("FR", "Lyon"), ("FR", "Marseille")]:
    try:
        url = "https://app.ticketmaster.com/discovery/v2/events.json"
        params = {
            "apikey": TM_KEY,
            "classificationName": "Electronic",
            "countryCode": country,
            "city": city,
            "startDateTime": f"{TODAY}T00:00:00Z",
            "size": 50,
            "sort": "date,asc",
        }
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            embedded = data.get("_embedded", {})
            events = embedded.get("events", [])
            total = data.get("page", {}).get("totalElements", 0)
            print(f"  {city} ({country}): {total} events, {len(events)} recus")
            
            for evt in events:
                name = evt.get("name", "")
                dates = evt.get("dates", {}).get("start", {})
                date_str = dates.get("localDate", "")
                time_str = dates.get("localTime", "")
                
                venue_info = evt.get("_embedded", {}).get("venues", [{}])[0]
                venue_name = venue_info.get("name", "")
                venue_city = venue_info.get("city", {}).get("name", "")
                venue_addr = venue_info.get("address", {}).get("line1", "")
                venue_zip = venue_info.get("postalCode", "")
                venue_loc = venue_info.get("location", {})
                lat = venue_loc.get("latitude")
                lng = venue_loc.get("longitude")
                
                source_url = evt.get("url", "")
                
                if name and date_str and lat and lng:
                    loc_parts = [venue_name, venue_addr, f"{venue_zip} {venue_city}".strip()]
                    location = ", ".join([p for p in loc_parts if p])
                    
                    all_new.append({
                        "_source": "ticketmaster",
                        "title": name,
                        "location": location,
                        "latitude": float(lat),
                        "longitude": float(lng),
                        "date": date_str,
                        "time": time_str[:5] if time_str else None,
                        "source_url": source_url,
                    })
        else:
            print(f"  {city} ({country}): {r.status_code} {r.text[:150]}")
    except Exception as e:
        print(f"  {city} ({country}): {e}")
    time.sleep(1)


# ==========================================================================
# 4. Songkick API (evenements live)
# ==========================================================================
print("\n" + "=" * 70)
print("4. Songkick API")
print("=" * 70)

try:
    # Songkick demo
    r = requests.get("https://api.songkick.com/api/3.0/events.json", params={
        "apikey": "test",  # demo key
        "location": "geo:46.2,6.15",  # Geneva
        "type": "Concert",
    }, headers=HEADERS, timeout=15)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  Data: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}")
    else:
        print(f"  Response: {r.text[:200]}")
except Exception as e:
    print(f"  Erreur: {e}")


# ==========================================================================
# 5. Bandsintown API (gratuit)
# ==========================================================================
print("\n" + "=" * 70)
print("5. Bandsintown API")
print("=" * 70)

# Bandsintown a une API publique pour les artistes
electro_artists = ["Amelie Lens", "Charlotte de Witte", "Nina Kraviz", "Solomun",
                    "Boris Brejcha", "Maceo Plex", "Tale Of Us", "Adriatique",
                    "Stephan Bodzin", "Recondite", "Apparat", "Moderat",
                    "Paul Kalkbrenner", "Joris Voorn", "Dixon"]

for artist in electro_artists[:8]:
    try:
        url = f"https://rest.bandsintown.com/artists/{artist}/events"
        params = {"app_id": "mapeventai", "date": f"{TODAY},2026-12-31"}
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            events = r.json()
            if isinstance(events, list) and events:
                # Filtrer Suisse + France
                ch_fr = [e for e in events if e.get("venue", {}).get("country", "") in ("Switzerland", "France")]
                if ch_fr:
                    print(f"  {artist}: {len(ch_fr)} events CH/FR sur {len(events)} total")
                    for evt in ch_fr:
                        v = evt.get("venue", {})
                        all_new.append({
                            "_source": "bandsintown",
                            "title": f"{artist} live - {v.get('name', '')}",
                            "location": f"{v.get('name', '')}, {v.get('city', '')}, {v.get('country', '')}",
                            "latitude": float(v.get("latitude", 0)),
                            "longitude": float(v.get("longitude", 0)),
                            "date": evt.get("datetime", "")[:10],
                            "time": evt.get("datetime", "")[11:16] if len(evt.get("datetime", "")) > 11 else None,
                            "source_url": evt.get("url", ""),
                        })
                else:
                    print(f"  {artist}: {len(events)} events, 0 CH/FR")
            else:
                print(f"  {artist}: 0 events")
        else:
            print(f"  {artist}: {r.status_code}")
    except Exception as e:
        print(f"  {artist}: {e}")
    time.sleep(1)


# ==========================================================================
# RESULTATS
# ==========================================================================
print("\n" + "=" * 70)
print("RESULTATS")
print("=" * 70)

# Compter par source
sources = {}
for e in all_new:
    src = e.get("_source", "goabase")
    sources[src] = sources.get(src, 0) + 1

print(f"Total events supplementaires: {len(all_new)}")
for src, cnt in sorted(sources.items(), key=lambda x: -x[1]):
    print(f"  {src}: {cnt}")

# Echantillon Ticketmaster
tm = [e for e in all_new if e.get("_source") == "ticketmaster"]
if tm:
    print(f"\nEchantillon Ticketmaster:")
    for e in tm[:10]:
        print(f"  {e['title'][:50]} | {e['date']} | {e['location'][:40]}")

# Echantillon Bandsintown
bit = [e for e in all_new if e.get("_source") == "bandsintown"]
if bit:
    print(f"\nEchantillon Bandsintown:")
    for e in bit[:10]:
        print(f"  {e['title'][:50]} | {e['date']} | {e['location'][:40]}")

# Sauvegarder pour dedup + import ensuite
with open("scraper/extra_electro_raw.json", "w", encoding="utf-8") as f:
    json.dump(all_new, f, ensure_ascii=False, indent=2)

print(f"\nSauvegarde: scraper/extra_electro_raw.json")
