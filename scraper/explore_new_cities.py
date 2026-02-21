"""
Explorer de nouvelles villes open data pour des events.
Sources sûres avec licences vérifiables.
"""
import requests
import time
import json

# ============================================================
# 1. VIENNE (Wien) - Open Government Data
# data.gv.at - CC BY 4.0
# ============================================================
def explore_vienna():
    print("=" * 60)
    print("VIENNE - data.wien.gv.at (CC BY 4.0)")
    print("=" * 60)
    
    # Catalog search
    try:
        r = requests.get("https://data.wien.gv.at/daten/geo", params={
            "service": "WFS",
            "request": "GetCapabilities"
        }, timeout=15)
        print(f"  WFS: HTTP {r.status_code}")
    except Exception as e:
        print(f"  WFS: {e}")
    
    # Try OGD portal
    try:
        r = requests.get("https://data.gv.at/katalog/api/3/action/package_search", params={
            "q": "veranstaltungen events",
            "rows": 10,
            "fq": "organization:stadt-wien"
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("result", {}).get("results", [])
            print(f"  Datasets: {len(results)}")
            for ds in results:
                name = ds.get("title", "?")
                res_count = len(ds.get("resources", []))
                print(f"    - {name} ({res_count} resources)")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 2. ZURICH - data.stadt-zuerich.ch
# ============================================================
def explore_zurich():
    print("\n" + "=" * 60)
    print("ZURICH - data.stadt-zuerich.ch")
    print("=" * 60)
    
    try:
        r = requests.get("https://data.stadt-zuerich.ch/api/3/action/package_search", params={
            "q": "events veranstaltungen agenda",
            "rows": 10
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("result", {}).get("results", [])
            print(f"  Datasets: {len(results)}")
            for ds in results:
                name = ds.get("title", "?")
                notes = (ds.get("notes", "") or "")[:100]
                print(f"    - {name}")
                if notes:
                    print(f"      {notes}")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 3. DUBLIN - data.gov.ie
# ============================================================
def explore_dublin():
    print("\n" + "=" * 60)
    print("DUBLIN - data.gov.ie")
    print("=" * 60)
    
    try:
        r = requests.get("https://data.gov.ie/api/3/action/package_search", params={
            "q": "events festivals cultural",
            "rows": 10
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("result", {}).get("results", [])
            print(f"  Datasets: {len(results)}")
            for ds in results:
                name = ds.get("title", "?")
                org = ds.get("organization", {}).get("title", "?") if ds.get("organization") else "?"
                print(f"    - {name} ({org})")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 4. ROME - dati.comune.roma.it
# ============================================================
def explore_rome():
    print("\n" + "=" * 60)
    print("ROME - Open Data Roma")
    print("=" * 60)
    
    try:
        r = requests.get("https://dati.comune.roma.it/catalog/api/3/action/package_search", params={
            "q": "eventi cultura",
            "rows": 10
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("result", {}).get("results", [])
            print(f"  Datasets: {len(results)}")
            for ds in results:
                name = ds.get("title", "?")
                print(f"    - {name}")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 5. STOCKHOLM - stockholm.se/open-data
# ============================================================
def explore_stockholm():
    print("\n" + "=" * 60)
    print("STOCKHOLM - Open Data")
    print("=" * 60)
    
    try:
        r = requests.get("https://dataportalen.stockholm.se/dataportalen/api/1/datasets", timeout=15)
        if r.status_code == 200:
            data = r.json()
            print(f"  Total datasets: {len(data) if isinstance(data, list) else '?'}")
            if isinstance(data, list):
                events_ds = [d for d in data if any(w in str(d).lower() for w in ["event", "evenemang", "kultur"])]
                print(f"  Event-related: {len(events_ds)}")
                for ds in events_ds[:5]:
                    print(f"    - {ds.get('title', ds.get('name', '?'))}")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 6. BRUXELLES Region - opendata.brussels
# ============================================================
def explore_brussels():
    print("\n" + "=" * 60)
    print("BRUXELLES - opendata.bruxelles.be")
    print("=" * 60)
    
    try:
        r = requests.get("https://opendata.brussels.be/api/explore/v2.1/catalog/datasets", params={
            "limit": 50
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            total = data.get("total_count", 0)
            results = data.get("results", [])
            print(f"  Total datasets: {total}")
            events_ds = []
            for ds in results:
                did = ds.get("dataset_id", "?")
                metas = ds.get("metas", {}).get("default", {})
                title = (metas.get("title", "") or "").lower()
                if any(w in title for w in ["event", "agenda", "manifestation", "culture", "festival"]):
                    events_ds.append((did, metas.get("title", "?"), metas.get("records_count", 0)))
            print(f"  Event-related: {len(events_ds)}")
            for did, title, rc in events_ds:
                print(f"    - {did} ({rc}): {title}")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 7. COPENHAGEN - opendata.dk
# ============================================================
def explore_copenhagen():
    print("\n" + "=" * 60)
    print("COPENHAGEN - Open Data")
    print("=" * 60)
    
    try:
        r = requests.get("https://www.opendata.dk/api/3/action/package_search", params={
            "q": "events kultur festival",
            "rows": 10
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("result", {}).get("results", [])
            print(f"  Datasets: {len(results)}")
            for ds in results:
                name = ds.get("title", "?")
                org = ds.get("organization", {}).get("title", "?") if ds.get("organization") else "?"
                print(f"    - {name} ({org})")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 8. MILAN - dati.comune.milano.it
# ============================================================
def explore_milan():
    print("\n" + "=" * 60)
    print("MILAN - Open Data")
    print("=" * 60)
    
    try:
        r = requests.get("https://dati.comune.milano.it/api/3/action/package_search", params={
            "q": "eventi cultura",
            "rows": 10
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("result", {}).get("results", [])
            print(f"  Datasets: {len(results)}")
            for ds in results:
                name = ds.get("title", "?")
                print(f"    - {name}")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 9. AMSTERDAM - data.amsterdam.nl
# ============================================================
def explore_amsterdam():
    print("\n" + "=" * 60)
    print("AMSTERDAM - data.amsterdam.nl")
    print("=" * 60)
    
    try:
        r = requests.get("https://api.data.amsterdam.nl/v1/", timeout=15)
        if r.status_code == 200:
            data = r.json()
            datasets = data.get("datasets", {}) if isinstance(data, dict) else {}
            print(f"  API endpoints: {len(datasets)}")
            for name in sorted(datasets.keys()):
                if any(w in name.lower() for w in ["event", "evenement", "cultuur", "festival"]):
                    print(f"    - {name}")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")
    
    # Try specific events endpoint
    try:
        r = requests.get("https://api.data.amsterdam.nl/v1/evenementen/evenementen/", params={
            "_pageSize": 5
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            total = data.get("page", {}).get("totalElements", 0)
            results = data.get("_embedded", {}).get("evenementen", [])
            print(f"  Events endpoint: {total} total, {len(results)} fetched")
            for ev in results[:3]:
                print(f"    - {ev.get('titel', '?')[:60]}")
        else:
            print(f"  Events: HTTP {r.status_code}")
    except Exception as e:
        print(f"  Events: {e}")


# ============================================================
# 10. LISBON - Lisboa Aberta
# ============================================================
def explore_lisbon():
    print("\n" + "=" * 60)
    print("LISBONNE - Lisboa Aberta")
    print("=" * 60)
    
    try:
        r = requests.get("https://lisboaaberta.cm-lisboa.pt/index.php/pt/dados/catalogo-de-dados-abertos", timeout=15)
        print(f"  Portal: HTTP {r.status_code}")
    except Exception as e:
        print(f"  Portal: {e}")
    
    # Try CKAN API
    try:
        r = requests.get("https://dados.cm-lisboa.pt/api/3/action/package_search", params={
            "q": "eventos cultura",
            "rows": 10
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("result", {}).get("results", [])
            print(f"  Datasets: {len(results)}")
            for ds in results:
                print(f"    - {ds.get('title', '?')}")
        else:
            print(f"  CKAN: HTTP {r.status_code}")
    except Exception as e:
        print(f"  CKAN: {e}")


# ============================================================
# 11. OPENAGENDA - Combien d'events pas encore importés?
# ============================================================
def check_openagenda_potential():
    print("\n" + "=" * 60)
    print("OPENAGENDA - Potentiel restant")
    print("=" * 60)
    
    OA_KEY = "0e3b442455894aa09e7b8acb7d43c69c"
    
    countries = ["FR", "BE", "CH", "DE", "ES", "IT", "NL", "PT", "AT", "GB", "IE", "SE", "DK", "NO", "FI"]
    
    for cc in countries:
        try:
            r = requests.get("https://api.openagenda.com/v2/events", params={
                "key": OA_KEY,
                "location_countrycode": cc,
                "timings[gte]": "2026-02-13",
                "timings[lte]": "2026-12-31",
                "size": 1
            }, timeout=15)
            data = r.json()
            total = data.get("total", 0)
            print(f"  {cc}: {total} events futurs")
            time.sleep(0.5)
        except Exception as e:
            print(f"  {cc}: ERREUR {e}")


if __name__ == "__main__":
    explore_vienna()
    explore_zurich()
    explore_amsterdam()
    explore_brussels()
    explore_dublin()
    explore_copenhagen()
    explore_lisbon()
    explore_rome()
    explore_milan()
    explore_stockholm()
    check_openagenda_potential()
