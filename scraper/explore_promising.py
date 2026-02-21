"""
Creuser les sources open data prometteuses.
1. Lisbonne - Agenda Cultural
2. Amsterdam - Events
3. OpenAgenda - debug pourquoi 0
4. Vienne - trouver le bon endpoint
"""
import requests
import time
import json

OA_KEY = "0e3b442455894aa09e7b8acb7d43c69c"

# ============================================================
# 1. LISBONNE - Agenda Cultural
# ============================================================
def explore_lisbon_agenda():
    print("=" * 60)
    print("LISBONNE - Agenda Cultural")
    print("=" * 60)
    
    # Get dataset details
    try:
        r = requests.get("https://dados.cm-lisboa.pt/api/3/action/package_show", params={
            "id": "agenda-cultural-de-lisboa"
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            ds = data.get("result", {})
            print(f"  Title: {ds.get('title', '?')}")
            print(f"  License: {ds.get('license_title', '?')}")
            print(f"  Resources:")
            for res in ds.get("resources", []):
                fmt = res.get("format", "?")
                url = res.get("url", "?")
                name = res.get("name", "?")
                print(f"    - [{fmt}] {name}: {url[:100]}")
                
                # Try to fetch first resource
                if fmt.upper() in ["JSON", "CSV", "GEOJSON"]:
                    try:
                        r2 = requests.get(url, timeout=15)
                        if r2.status_code == 200:
                            if fmt.upper() == "JSON":
                                jdata = r2.json()
                                if isinstance(jdata, list):
                                    print(f"      -> {len(jdata)} records")
                                    if jdata:
                                        print(f"      -> Keys: {list(jdata[0].keys())[:10]}")
                                        print(f"      -> Sample: {json.dumps(jdata[0], ensure_ascii=False)[:200]}")
                                elif isinstance(jdata, dict):
                                    print(f"      -> Keys: {list(jdata.keys())[:10]}")
                            else:
                                print(f"      -> {len(r2.text)} bytes")
                        else:
                            print(f"      -> HTTP {r2.status_code}")
                    except Exception as e2:
                        print(f"      -> Fetch error: {e2}")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 2. AMSTERDAM - Events detail
# ============================================================
def explore_amsterdam_detail():
    print("\n" + "=" * 60)
    print("AMSTERDAM - Events (CC0)")
    print("=" * 60)
    
    try:
        r = requests.get("https://api.data.amsterdam.nl/v1/evenementen/evenementen/", params={
            "_pageSize": 50
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            total = data.get("page", {}).get("totalElements", 0)
            results = data.get("_embedded", {}).get("evenementen", [])
            print(f"  Total: {total}, Fetched: {len(results)}")
            
            if results:
                print(f"  Keys: {list(results[0].keys())[:15]}")
                for ev in results[:5]:
                    title = ev.get("titel", "?")
                    start = ev.get("startdatum", ev.get("datumStart", "?"))
                    end = ev.get("einddatum", ev.get("datumEinde", "?"))
                    loc = ev.get("locatie", "?")
                    geo = ev.get("geometry", {})
                    print(f"    [{start}] {title[:60]}")
                    print(f"      loc={loc}, geo={geo}")
        else:
            print(f"  HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 3. OPENAGENDA - Debug: pourquoi 0?
# ============================================================
def debug_openagenda():
    print("\n" + "=" * 60)
    print("OPENAGENDA - Debug")
    print("=" * 60)
    
    # Test basic search
    tests = [
        ("No filter", {}),
        ("FR upcoming", {"location_countrycode": "FR", "relative[]": "upcoming", "size": 3}),
        ("FR current", {"location_countrycode": "FR", "relative[]": "current", "size": 3}),
        ("FR timings", {"location_countrycode": "FR", "timings[gte]": "2026-02-13", "size": 3}),
        ("No country upcoming", {"relative[]": "upcoming", "size": 3}),
        ("No country current", {"relative[]": "current", "size": 3}),
        ("Search paris", {"search": "paris", "size": 3}),
    ]
    
    for name, params in tests:
        params["key"] = OA_KEY
        try:
            r = requests.get("https://api.openagenda.com/v2/events", params=params, timeout=15)
            data = r.json()
            total = data.get("total", 0)
            events = data.get("events", [])
            if events:
                first = events[0]
                title = first.get("title", {}).get("fr", "") or first.get("title", {}).get("en", "?")
                print(f"  {name}: total={total}, first='{title[:40]}'")
            else:
                error = data.get("message", "")
                print(f"  {name}: total={total}, events={len(events)}, msg={error}")
        except Exception as e:
            print(f"  {name}: ERREUR {e}")
        time.sleep(0.5)
    
    # Test agendas search too
    print("\n  --- Agendas ---")
    try:
        r = requests.get("https://api.openagenda.com/v2/agendas", params={
            "key": OA_KEY,
            "size": 5,
            "sort": "updatedAt.desc"
        }, timeout=15)
        data = r.json()
        total = data.get("total", 0)
        agendas = data.get("agendas", [])
        print(f"  Total agendas: {total}")
        for ag in agendas:
            name = ag.get("title", "?")
            uid = ag.get("uid")
            upcoming = ag.get("eventsUpcomingCount", 0) or 0
            print(f"    - {name} (uid={uid}, upcoming={upcoming})")
    except Exception as e:
        print(f"  Agendas ERREUR: {e}")


# ============================================================
# 4. VIENNE - try wien.gv.at CKAN
# ============================================================
def explore_vienna_detail():
    print("\n" + "=" * 60)
    print("VIENNE - Open Government Data")
    print("=" * 60)
    
    # Try the CKAN catalog
    try:
        r = requests.get("https://www.data.gv.at/katalog/api/3/action/package_search", params={
            "q": "veranstaltungen",
            "fq": "organization:stadt-wien",
            "rows": 10
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("result", {}).get("results", [])
            print(f"  Wien datasets: {len(results)}")
            for ds in results:
                title = ds.get("title", "?")
                for res in ds.get("resources", [])[:2]:
                    fmt = res.get("format", "?")
                    url = res.get("url", "?")[:80]
                    print(f"    - {title} [{fmt}] {url}")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")
    
    # Try broader search
    try:
        r = requests.get("https://www.data.gv.at/katalog/api/3/action/package_search", params={
            "q": "events kultur veranstaltung",
            "rows": 10
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("result", {}).get("results", [])
            print(f"\n  Broader search: {len(results)}")
            for ds in results:
                title = ds.get("title", "?")
                org = ds.get("organization", {}).get("title", "?") if ds.get("organization") else "?"
                print(f"    - {title} ({org})")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 5. BRUXELLES - try visit.brussels or agenda.brussels
# ============================================================ 
def explore_brussels_events():
    print("\n" + "=" * 60)
    print("BRUXELLES - agenda.brussels")
    print("=" * 60)
    
    # Check if agenda.brussels has an API
    try:
        r = requests.get("https://www.agenda.brussels/api/events", params={
            "limit": 5
        }, timeout=15, headers={"Accept": "application/json"})
        print(f"  agenda.brussels: HTTP {r.status_code}")
        if r.status_code == 200:
            print(f"  Content: {r.text[:300]}")
    except Exception as e:
        print(f"  agenda.brussels: {e}")
    
    # Try visit.brussels
    try:
        r = requests.get("https://visit.brussels/api/events", timeout=15, 
                         headers={"Accept": "application/json"})
        print(f"  visit.brussels: HTTP {r.status_code}")
    except Exception as e:
        print(f"  visit.brussels: {e}")


# ============================================================
# 6. London - data.london.gov.uk
# ============================================================
def explore_london():
    print("\n" + "=" * 60)
    print("LONDON - data.london.gov.uk")
    print("=" * 60)
    
    try:
        r = requests.get("https://data.london.gov.uk/api/3/action/package_search", params={
            "q": "events cultural festivals",
            "rows": 10
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("result", {}).get("results", [])
            print(f"  Datasets: {len(results)}")
            for ds in results:
                title = ds.get("title", "?")
                print(f"    - {title}")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")


if __name__ == "__main__":
    explore_lisbon_agenda()
    explore_amsterdam_detail()
    debug_openagenda()
    explore_vienna_detail()
    explore_brussels_events()
    explore_london()
