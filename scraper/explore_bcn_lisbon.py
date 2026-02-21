"""Explore le format des données Barcelone et Lisbonne."""
import requests, json

HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}

# === BARCELONE ===
print("=" * 60)
print("BARCELONE - Exploration")
print("=" * 60)

# On sait que package_show a marché, explorons la structure
r = requests.get("https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show?id=agenda-cultural", headers=HEADERS, timeout=15)
data = r.json()
result = data.get("result", {})
print(f"Nom: {result.get('title', result.get('name'))}")
print(f"License: {result.get('license_title', result.get('license_id'))}")
resources = result.get("resources", [])
print(f"Resources: {len(resources)}")
for res in resources:
    print(f"  - {res.get('name', '?')} | format={res.get('format')} | url={res.get('url', '')[:100]}")

# Télécharger le JSON resource
json_resources = [r for r in resources if 'json' in (r.get('format') or '').lower()]
if json_resources:
    url = json_resources[0].get("url")
    print(f"\n📥 Téléchargement: {url}")
    r2 = requests.get(url, headers=HEADERS, timeout=30)
    print(f"Status: {r2.status_code}")
    raw = r2.json()
    
    if isinstance(raw, list):
        print(f"Type: list, len={len(raw)}")
        if raw:
            sample = raw[0]
            print(f"Clés: {list(sample.keys())[:20]}")
            print(f"Sample: {json.dumps(sample, indent=2, ensure_ascii=False)[:1500]}")
    elif isinstance(raw, dict):
        print(f"Type: dict, clés={list(raw.keys())[:10]}")
        for k in ['features', 'results', 'data', 'records', '@graph']:
            if k in raw:
                items = raw[k]
                print(f"  {k}: {type(items).__name__}, len={len(items)}")
                if isinstance(items, list) and items:
                    print(f"  Sample keys: {list(items[0].keys())[:20]}")
                    print(f"  Sample: {json.dumps(items[0], indent=2, ensure_ascii=False)[:1500]}")
                break
        else:
            print(f"  Content: {json.dumps(raw, indent=2, ensure_ascii=False)[:2000]}")

# === LISBONNE ===
print("\n" + "=" * 60)
print("LISBONNE / PORTUGAL - Exploration")
print("=" * 60)

# Agenda Cultural de Lisboa
r = requests.get("https://dados.gov.pt/api/1/datasets/?tag=eventos&format=json", headers=HEADERS, timeout=15)
data = r.json()
datasets = data.get("data", [])
for ds in datasets:
    print(f"\n📦 {ds.get('title')}")
    print(f"   License: {ds.get('license')}")
    resources = ds.get("resources", [])
    for res in resources[:3]:
        print(f"   - {res.get('title', '?')} | format={res.get('format')} | url={res.get('url', '')[:120]}")

# Aussi essayer Agenda Cultural Lisboa directement
print("\n📍 Recherche Agenda Cultural Lisboa...")
r = requests.get("https://dados.gov.pt/api/1/datasets/?q=agenda+cultural+lisboa", headers=HEADERS, timeout=15)
data = r.json()
for ds in data.get("data", []):
    print(f"  📦 {ds.get('title')}")
    for res in ds.get("resources", [])[:3]:
        fmt = res.get("format", "?")
        url = res.get("url", "")[:120]
        print(f"     - [{fmt}] {url}")
