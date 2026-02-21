"""
Explore en détail les APIs Madrid + Barcelona pour comprendre la structure des données.
"""
import requests
import json
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (https://mapevent.world)"}

# ============================================
# 1. MADRID - Structure détaillée
# ============================================
print("=" * 60)
print("MADRID - Structure des événements")
print("=" * 60)
url = "https://datos.madrid.es/egob/catalogo/300107-0-agenda-actividades-702702.json"
r = requests.get(url, headers=HEADERS, timeout=20)
data = r.json()
graph = data.get("@graph", [])
print(f"Total events: {len(graph)}")

# Show 3 complete events
for i, ev in enumerate(graph[:3]):
    print(f"\n--- Event {i+1} ---")
    print(json.dumps(ev, indent=2, ensure_ascii=False)[:1500])

# Count events with location/coordinates
with_loc = sum(1 for ev in graph if ev.get("location", {}).get("latitude"))
with_addr = sum(1 for ev in graph if ev.get("address", {}).get("street-address"))
with_link = sum(1 for ev in graph if ev.get("link"))
future = sum(1 for ev in graph if ev.get("dtstart", "") >= TODAY)
print(f"\nStats Madrid:")
print(f"  Avec latitude/longitude: {with_loc}")
print(f"  Avec adresse: {with_addr}")
print(f"  Avec lien web: {with_link}")
print(f"  Futurs (>= {TODAY}): {future}")

# Check available fields
if graph:
    print(f"\n  Champs disponibles: {list(graph[0].keys())}")

# ============================================
# 2. BARCELONA - Agenda Cultural (JSON)
# ============================================
print("\n" + "=" * 60)
print("BARCELONA - Agenda Cultural")
print("=" * 60)

# Get the resource URL
url = "https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show"
r = requests.get(url, params={"id": "agenda-cultural"}, headers=HEADERS, timeout=15)
ds = r.json().get("result", {})
json_resources = [res for res in ds.get("resources", []) if res.get("format", "").upper() == "JSON"]
for res in json_resources:
    res_url = res.get("url", "")
    print(f"Resource JSON: {res_url}")
    
    # Try to fetch the actual data
    try:
        r2 = requests.get(res_url, headers=HEADERS, timeout=20)
        print(f"  Status: {r2.status_code}")
        if r2.status_code == 200:
            bdata = r2.json()
            if isinstance(bdata, list):
                print(f"  Events (list): {len(bdata)}")
                for ev in bdata[:2]:
                    print(f"    {json.dumps(ev, indent=2, ensure_ascii=False)[:800]}")
            elif isinstance(bdata, dict):
                print(f"  Keys: {list(bdata.keys())}")
                # Try common patterns
                for key in ["results", "result", "data", "records", "@graph", "items", "features"]:
                    if key in bdata:
                        items = bdata[key]
                        print(f"  [{key}]: {len(items)} items")
                        if items:
                            print(f"    Premier: {json.dumps(items[0], indent=2, ensure_ascii=False)[:800]}")
                        break
                else:
                    print(f"  Structure: {json.dumps(bdata, ensure_ascii=False)[:500]}")
    except Exception as e:
        print(f"  Exception: {e}")

# ============================================
# 2b. BARCELONA - Agenda diaria
# ============================================
print("\n" + "=" * 60)
print("BARCELONA - Agenda Diaria")
print("=" * 60)
url = "https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show"
r = requests.get(url, params={"id": "agenda-diaria"}, headers=HEADERS, timeout=15)
ds = r.json().get("result", {})
for res in ds.get("resources", []):
    fmt = res.get("format", "?")
    res_url = res.get("url", "")
    print(f"Resource {fmt}: {res_url[:100]}")
    
    if fmt.upper() == "JSON":
        try:
            r2 = requests.get(res_url, headers=HEADERS, timeout=20)
            print(f"  Status: {r2.status_code}")
            if r2.status_code == 200:
                bdata = r2.json()
                if isinstance(bdata, list):
                    print(f"  Events: {len(bdata)}")
                    for ev in bdata[:2]:
                        print(f"    {json.dumps(ev, indent=2, ensure_ascii=False)[:800]}")
                elif isinstance(bdata, dict):
                    print(f"  Keys: {list(bdata.keys())}")
                    for key in ["results", "result", "data", "records", "@graph", "items"]:
                        if key in bdata:
                            items = bdata[key]
                            print(f"  [{key}]: {len(items) if isinstance(items, list) else type(items).__name__}")
                            if isinstance(items, list) and items:
                                print(f"    Premier: {json.dumps(items[0], indent=2, ensure_ascii=False)[:800]}")
                            break
        except Exception as e:
            print(f"  Exception: {e}")

# ============================================
# 3. BARCELONA - Try datastore_search on resources
# ============================================
print("\n" + "=" * 60)
print("BARCELONA - Datastore search")
print("=" * 60)
# Get resource IDs
url = "https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show"
r = requests.get(url, params={"id": "agenda-cultural"}, headers=HEADERS, timeout=15)
ds = r.json().get("result", {})
for res in ds.get("resources", []):
    res_id = res.get("id", "")
    fmt = res.get("format", "?")
    print(f"\nResource ID: {res_id} ({fmt})")
    
    # Try datastore_search
    try:
        url2 = "https://opendata-ajuntament.barcelona.cat/data/api/3/action/datastore_search"
        r2 = requests.get(url2, params={"resource_id": res_id, "limit": 3}, headers=HEADERS, timeout=15)
        print(f"  Datastore status: {r2.status_code}")
        if r2.status_code == 200:
            ds_data = r2.json()
            result = ds_data.get("result", {})
            total = result.get("total", 0)
            records = result.get("records", [])
            fields = result.get("fields", [])
            print(f"  Total records: {total}")
            print(f"  Fields: {[f.get('id') for f in fields]}")
            for rec in records[:2]:
                print(f"    {json.dumps(rec, indent=2, ensure_ascii=False)[:600]}")
    except Exception as e:
        print(f"  Exception: {e}")

print("\n" + "=" * 60)
print("FIN EXPLORATION")
print("=" * 60)
