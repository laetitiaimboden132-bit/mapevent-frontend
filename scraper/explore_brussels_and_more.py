"""
Explorer les APIs qui marchent:
1. agenda.brussels - events Bruxelles
2. OpenAgenda sans clé API
3. Predicthq (s'il a un tier gratuit)
4. Eventbrite public
5. data.culture.gouv.fr - France
"""
import requests
import time
import json

# ============================================================
# 1. BRUXELLES - agenda.brussels API
# ============================================================
def explore_brussels_full():
    print("=" * 60)
    print("BRUXELLES - agenda.brussels")
    print("=" * 60)
    
    # Fetch events
    try:
        r = requests.get("https://www.agenda.brussels/api/events", params={
            "limit": 100
        }, timeout=30, headers={"Accept": "application/json"})
        
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            total = data.get("total", data.get("count", len(results)))
            print(f"  Total: {total}, Fetched: {len(results)}")
            
            if results:
                # Examine structure
                first = results[0]
                blob = first.get("blob", "")
                if isinstance(blob, str):
                    try:
                        blob = json.loads(blob)
                    except:
                        pass
                
                print(f"  Top-level keys: {list(first.keys())}")
                print(f"  First event: {first.get('title', '?')}")
                
                if isinstance(blob, dict):
                    print(f"  Blob keys: {list(blob.keys())[:15]}")
                    print(f"  Sample blob: {json.dumps(blob, ensure_ascii=False)[:500]}")
                
                # Show more events
                print(f"\n  Events:")
                for ev in results[:20]:
                    title = ev.get("title", "?")
                    desc = ev.get("description", "?")[:50]
                    img = ev.get("image_url", "")
                    
                    b = ev.get("blob", "")
                    if isinstance(b, str):
                        try:
                            b = json.loads(b)
                        except:
                            b = {}
                    
                    dates = b.get("dates", "") if isinstance(b, dict) else ""
                    location = b.get("location", {}) if isinstance(b, dict) else {}
                    loc_name = location.get("name", "?") if isinstance(location, dict) else "?"
                    lat = location.get("lat", "") if isinstance(location, dict) else ""
                    lng = location.get("lng", "") if isinstance(location, dict) else ""
                    cats = b.get("categories", []) if isinstance(b, dict) else []
                    
                    print(f"    [{dates[:20] if dates else '?'}] {title[:55]}")
                    print(f"      loc={loc_name[:40]}, lat={lat}, lng={lng}, cats={cats[:3]}")
        else:
            print(f"  HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  ERREUR: {e}")
    
    # Check for pagination
    try:
        r = requests.get("https://www.agenda.brussels/api/events", params={
            "limit": 5,
            "offset": 100
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("results", [])
            print(f"\n  Pagination (offset=100): {len(results)} results")
    except:
        pass
    
    # Check if there are categories
    try:
        r = requests.get("https://www.agenda.brussels/api/categories", timeout=15)
        if r.status_code == 200:
            cats = r.json()
            print(f"\n  Categories available: {json.dumps(cats, ensure_ascii=False)[:500]}")
    except:
        pass


# ============================================================
# 2. data.culture.gouv.fr - Culture France
# ============================================================
def explore_france_culture():
    print("\n" + "=" * 60)
    print("FRANCE - data.culture.gouv.fr")
    print("=" * 60)
    
    # Datasud for South of France
    try:
        r = requests.get("https://trouver.datasud.fr/api/3/action/package_search", params={
            "q": "evenements agenda culture festival",
            "rows": 10
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("result", {}).get("results", [])
            print(f"  Datasud: {len(results)} datasets")
            for ds in results[:5]:
                title = ds.get("title", "?")
                org = ds.get("organization", {}).get("title", "?") if ds.get("organization") else "?"
                print(f"    - {title} ({org})")
        else:
            print(f"  Datasud: HTTP {r.status_code}")
    except Exception as e:
        print(f"  Datasud: {e}")
    
    # data.gouv.fr
    try:
        r = requests.get("https://www.data.gouv.fr/api/1/datasets/", params={
            "q": "agenda evenements culture concert",
            "page_size": 10
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            for ds in data.get("data", []):
                title = ds.get("title", "?")
                org = ds.get("organization", {}).get("name", "?") if ds.get("organization") else "?"
                resources = len(ds.get("resources", []))
                print(f"  data.gouv.fr: {title} ({org}, {resources} resources)")
        else:
            print(f"  data.gouv.fr: HTTP {r.status_code}")
    except Exception as e:
        print(f"  data.gouv.fr: {e}")


# ============================================================
# 3. OPENDATA.SWISS - events Suisse
# ============================================================
def explore_swiss_opendata():
    print("\n" + "=" * 60)
    print("SUISSE - opendata.swiss")
    print("=" * 60)
    
    try:
        r = requests.get("https://ckan.opendata.swiss/api/3/action/package_search", params={
            "q": "events veranstaltungen agenda kultur",
            "rows": 10
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("result", {}).get("results", [])
            print(f"  Datasets: {len(results)}")
            for ds in results:
                title = ds.get("title", {})
                if isinstance(title, dict):
                    title = title.get("fr", title.get("de", title.get("en", "?")))
                org = ds.get("organization", {}).get("title", {}) if ds.get("organization") else "?"
                if isinstance(org, dict):
                    org = org.get("fr", org.get("de", "?"))
                print(f"    - {title} ({org})")
                for res in ds.get("resources", [])[:2]:
                    fmt = res.get("format", "?")
                    url = res.get("url", "?")[:80]
                    print(f"      [{fmt}] {url}")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 4. Check existing import stats
# ============================================================
def check_existing_stats():
    print("\n" + "=" * 60)
    print("STATS EXISTANTES")
    print("=" * 60)
    
    API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
    r = requests.get(f"{API}/api/events", timeout=60)
    events = r.json()
    if isinstance(events, dict):
        events = events.get("events", [])
    
    from urllib.parse import urlparse
    sources = {}
    countries = {}
    for ev in events:
        url = ev.get("source_url", "") or ""
        try:
            domain = urlparse(url).netloc
        except:
            domain = "?"
        sources[domain] = sources.get(domain, 0) + 1
        
        # Try to get country
        c = ev.get("country", "")
        if not c:
            lat = ev.get("latitude", 0) or 0
            lng = ev.get("longitude", 0) or 0
            if 48 < lat < 52 and 1.5 < lng < 3.5:
                c = "FR-Paris"
            elif 52 < lat < 53 and 4 < lng < 5.5:
                c = "NL"
            elif 52 < lat < 53 and 13 < lng < 14:
                c = "DE-Berlin"
            elif 59.5 < lat < 60.5 and 24 < lng < 25.5:
                c = "FI-Helsinki"
            elif 40 < lat < 41 and -4 < lng < -3:
                c = "ES-Madrid"
            elif 41 < lat < 42 and 1.5 < lng < 2.5:
                c = "ES-Barcelona"
            elif 45 < lat < 47 and -2 < lng < 0:
                c = "FR-West"
            elif 43 < lat < 44 and -1 < lng < 0:
                c = "FR-Bordeaux"
            elif 47 < lat < 48 and -2 < lng < -1:
                c = "FR-Nantes"
            elif 45 < lat < 47 and 5.5 < lng < 8:
                c = "CH"
        if not c:
            c = "?"
        countries[c] = countries.get(c, 0) + 1
    
    print(f"  Total: {len(events)}")
    print(f"\n  Top sources:")
    for s, n in sorted(sources.items(), key=lambda x: -x[1])[:15]:
        print(f"    {s}: {n}")
    
    print(f"\n  Par zone géographique:")
    for c, n in sorted(countries.items(), key=lambda x: -x[1])[:20]:
        print(f"    {c}: {n}")


if __name__ == "__main__":
    explore_brussels_full()
    explore_france_culture()
    explore_swiss_opendata()
    check_existing_stats()
