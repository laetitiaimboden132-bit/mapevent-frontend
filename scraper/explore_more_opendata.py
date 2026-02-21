"""
Explore additional open data event sources in parallel with OpenAgenda discovery.
Focus on: data.gouv.fr, data.europa.eu, opendatasoft portals
"""
import requests
import json
import time

HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}

print("=" * 60)
print("EXPLORATION SOURCES OPEN DATA SUPPLÉMENTAIRES")
print("=" * 60)

# ============================================================
# 1. data.gouv.fr - French Open Data portal
# ============================================================
print("\n=== 1. data.gouv.fr ===")
try:
    # Search for event-related datasets
    for q in ["evenements", "agenda", "manifestations culturelles", "spectacles"]:
        r = requests.get("https://www.data.gouv.fr/api/1/datasets/", params={
            "q": q,
            "page_size": 10,
            "sort": "-created"
        }, timeout=15, headers=HEADERS)
        if r.status_code == 200:
            data = r.json()
            total = data.get("total", 0)
            datasets = data.get("data", [])
            print(f"\n  Recherche '{q}': {total} résultats")
            for ds in datasets[:5]:
                title = ds.get("title", "?")
                org = ds.get("organization", {})
                org_name = org.get("name", "?") if org else "?"
                resources = ds.get("resources", [])
                # Check for API/JSON resources
                has_api = any("api" in (r.get("format", "") or "").lower() or 
                            "json" in (r.get("format", "") or "").lower()
                            for r in resources)
                format_info = "API/JSON" if has_api else f"{len(resources)} res"
                print(f"    [{format_info}] {title[:60]} ({org_name[:30]})")
                
                # Show resource URLs for JSON/API resources
                for res in resources[:3]:
                    fmt = (res.get("format", "") or "").lower()
                    if "json" in fmt or "api" in fmt or "csv" in fmt:
                        print(f"      → {res.get('url', '?')[:80]} ({fmt})")
        time.sleep(0.5)
except Exception as e:
    print(f"  Erreur: {e}")

# ============================================================
# 2. OpenDataSoft public portals with events
# ============================================================
print("\n\n=== 2. OpenDataSoft portals ===")
ods_portals = [
    ("data.iledefrance.fr", "evenements"),
    ("data.iledefrance.fr", "agenda"),
    ("opendata.paris.fr", "evenements"),
    ("opendata.paris.fr", "que-faire-a-paris"),
    ("data.nantesmetropole.fr", "evenements"),
    ("data.grandlyon.com", "evenements"),
    ("data.grandlyon.com", "agenda"),
    ("data.toulouse-metropole.fr", "evenements"),
    ("opendata.bordeaux-metropole.fr", "evenements"),
    ("data.strasbourg.eu", "evenements"),
    ("opendata.lillemetropole.fr", "evenements"),
    ("data.montpellier3m.fr", "evenements"),
    ("data.rennesmetropole.fr", "evenements"),
    ("data.culture.gouv.fr", "evenements"),
]

for portal, query in ods_portals:
    try:
        # Try to search datasets
        url = f"https://{portal}/api/datasets/1.0/search/"
        r = requests.get(url, params={"q": query, "rows": 5}, timeout=10, headers=HEADERS)
        if r.status_code == 200:
            data = r.json()
            datasets = data.get("datasets", [])
            if datasets:
                print(f"\n  {portal} ('{query}'): {len(datasets)} datasets")
                for ds in datasets:
                    meta = ds.get("metas", {})
                    title = meta.get("default", {}).get("title", "?")
                    ds_id = ds.get("dataset_id", "?") if isinstance(ds, dict) else "?"
                    records = meta.get("default", {}).get("records_count", 0)
                    print(f"    [{records} records] {title[:60]} (id={ds_id[:40]})")
        else:
            # Try v2 API
            url2 = f"https://{portal}/api/explore/v2.1/catalog/datasets"
            r2 = requests.get(url2, params={"where": f"search('{query}')", "limit": 5}, timeout=10, headers=HEADERS)
            if r2.status_code == 200:
                data2 = r2.json()
                results = data2.get("results", [])
                if results:
                    print(f"\n  {portal} v2 ('{query}'): {len(results)} datasets")
                    for ds in results:
                        title = ds.get("metas", {}).get("default", {}).get("title", "?")
                        ds_id = ds.get("dataset_id", "?")
                        print(f"    {title[:60]} (id={ds_id[:40]})")
    except Exception as e:
        pass
    time.sleep(0.3)

# ============================================================
# 3. "Que faire à Paris" - specific Paris events API
# ============================================================
print("\n\n=== 3. Paris Open Data - Que faire à Paris ===")
try:
    # Known dataset ID for Paris events
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records"
    r = requests.get(url, params={"limit": 5}, timeout=15, headers=HEADERS)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        total = data.get("total_count", 0)
        results = data.get("results", [])
        print(f"  Total: {total} events")
        for ev in results[:3]:
            title = ev.get("title", "?")
            date_start = ev.get("date_start", "?")
            addr = ev.get("address_street", "?")
            lat = ev.get("lat_lon", {})
            print(f"    [{date_start[:10] if date_start else '?'}] {title[:50]} @ {str(addr)[:30]}")
    else:
        # Try alternative dataset IDs
        for ds_id in ["que-faire-a-paris", "evenements-a-paris", "agenda-evenements-paris"]:
            url2 = f"https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/{ds_id}/records"
            r2 = requests.get(url2, params={"limit": 3}, timeout=10, headers=HEADERS)
            if r2.status_code == 200:
                print(f"  Found: {ds_id} ({r2.json().get('total_count', 0)} records)")
                break
except Exception as e:
    print(f"  Erreur: {e}")

# ============================================================
# 4. European Data Portal
# ============================================================
print("\n\n=== 4. data.europa.eu ===")
try:
    url = "https://data.europa.eu/api/hub/search/datasets"
    r = requests.get(url, params={
        "q": "events agenda",
        "locale": "fr",
        "limit": 10,
        "filter": "country=fr,ch,be"
    }, timeout=15, headers=HEADERS)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        results = data.get("result", {}).get("results", [])
        total = data.get("result", {}).get("count", 0)
        print(f"  Total: {total}")
        for ds in results[:5]:
            title = ds.get("title", {}).get("fr", ds.get("title", {}).get("en", "?"))
            print(f"    {title[:70]}")
except Exception as e:
    print(f"  Erreur: {e}")

# ============================================================
# 5. Swiss Open Data (opendata.swiss)
# ============================================================
print("\n\n=== 5. opendata.swiss ===")
try:
    url = "https://ckan.opendata.swiss/api/3/action/package_search"
    r = requests.get(url, params={
        "q": "events veranstaltungen agenda",
        "rows": 10,
    }, timeout=15, headers=HEADERS)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        results = data.get("result", {}).get("results", [])
        print(f"  Found: {len(results)} datasets")
        for ds in results[:10]:
            title = ds.get("title", {})
            if isinstance(title, dict):
                title = title.get("fr", title.get("de", title.get("en", "?")))
            org = ds.get("organization", {}).get("title", {})
            if isinstance(org, dict):
                org = org.get("fr", org.get("de", "?"))
            resources = ds.get("resources", [])
            api_res = [r for r in resources if "api" in (r.get("format", "") or "").lower() or "json" in (r.get("format", "") or "").lower()]
            print(f"    {title[:60]} ({org[:30]}) [{len(api_res)} API/JSON res]")
            for ar in api_res[:2]:
                print(f"      → {ar.get('url', '?')[:80]}")
except Exception as e:
    print(f"  Erreur: {e}")

# ============================================================
# 6. Madrid Open Data
# ============================================================
print("\n\n=== 6. Madrid Open Data ===")
try:
    url = "https://datos.madrid.es/egob/catalogo/300107-0-agenda-actividades-eventos.json"
    r = requests.get(url, timeout=15, headers=HEADERS)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        graph = data.get("@graph", [])
        print(f"  Events: {len(graph)}")
        for ev in graph[:3]:
            title = ev.get("title", "?")
            loc = ev.get("location", {})
            lat = loc.get("latitude", "?")
            lng = loc.get("longitude", "?")
            dtstart = ev.get("dtstart", "?")
            print(f"    [{dtstart[:10] if dtstart else '?'}] {title[:50]} ({lat}, {lng})")
except Exception as e:
    print(f"  Erreur: {e}")

# ============================================================
# 7. Barcelona Open Data
# ============================================================
print("\n\n=== 7. Barcelona Open Data ===")
try:
    url = "https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_search"
    r = requests.get(url, params={"q": "events activitats agenda", "rows": 5}, timeout=15, headers=HEADERS)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        results = data.get("result", {}).get("results", [])
        for ds in results[:5]:
            title = ds.get("title", "?")
            resources = ds.get("resources", [])
            json_res = [r for r in resources if "json" in (r.get("format", "") or "").lower()]
            print(f"    {title[:60]} [{len(json_res)} JSON res]")
            for jr in json_res[:2]:
                print(f"      → {jr.get('url', '?')[:80]}")
except Exception as e:
    print(f"  Erreur: {e}")

# ============================================================
# 8. Wien (Vienna) Open Data
# ============================================================
print("\n\n=== 8. Wien Open Data ===")
try:
    url = "https://data.wien.gv.at/daten/geo"
    r = requests.get(url, params={
        "service": "WFS",
        "request": "GetFeature",
        "version": "1.1.0",
        "typeName": "ogdwien:VERANSTALTUNGENOGD",
        "srsName": "EPSG:4326",
        "outputFormat": "json",
        "maxFeatures": 5
    }, timeout=15, headers=HEADERS)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        features = data.get("features", [])
        print(f"  Features: {len(features)}")
        for f in features[:3]:
            props = f.get("properties", {})
            geom = f.get("geometry", {})
            coords = geom.get("coordinates", [])
            print(f"    {props.get('BEZEICHNUNG', '?')[:50]} ({coords})")
    else:
        print(f"  Response: {r.text[:200]}")
except Exception as e:
    print(f"  Erreur: {e}")

print("\n" + "=" * 60)
print("EXPLORATION TERMINÉE")
print("=" * 60)
