"""Explore si les events BCN ont des dates dans from_relationships/to_relationships."""
import requests, json

HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}
url = "https://opendata-ajuntament.barcelona.cat/data/dataset/2767159c-1c98-46b8-a686-2b25b40cb053/resource/59b9c807-f6c1-4c10-ac51-1ace65485079/download"
r = requests.get(url, headers=HEADERS, timeout=30)
data = r.json()

# Regarder 5 events en détail
for item in data[:5]:
    print(f"\n=== {item.get('name')} ===")
    
    # from_relationships
    fr = item.get('from_relationships', [])
    if fr:
        print(f"  from_relationships ({len(fr)}):")
        for rel in fr[:3]:
            print(f"    keys: {list(rel.keys())}")
            print(f"    {json.dumps(rel, indent=4, ensure_ascii=False)[:500]}")
    
    # to_relationships
    tr = item.get('to_relationships', [])
    if tr:
        print(f"  to_relationships ({len(tr)}):")
        for rel in tr[:3]:
            print(f"    keys: {list(rel.keys())}")
            print(f"    {json.dumps(rel, indent=4, ensure_ascii=False)[:500]}")
    
    # entity_types_data
    et = item.get('entity_types_data', [])
    if et:
        print(f"  entity_types_data ({len(et)}):")
        for e in et[:3]:
            print(f"    {json.dumps(e, indent=4, ensure_ascii=False)[:500]}")
    
    # attribute_categories
    ac = item.get('attribute_categories', [])
    if ac:
        print(f"  attribute_categories ({len(ac)}):")
        for a in ac[:3]:
            print(f"    {json.dumps(a, indent=4, ensure_ascii=False)[:500]}")

# Also check keys for date-looking fields
print("\n\nSearching for date-related fields across all events...")
date_keys = set()
for item in data[:50]:
    for key, val in item.items():
        if isinstance(val, str) and ('2025' in val or '2026' in val):
            if key not in ('created', 'modified'):
                date_keys.add(key)
    # Check in values
    for v in item.get('values', []):
        if v.get('datetime_value'):
            print(f"  Found datetime_value in {item.get('name')}: {v.get('datetime_value')}")
    # Check in relationships
    for rel in item.get('from_relationships', []) + item.get('to_relationships', []):
        for k, v in rel.items():
            if isinstance(v, str) and ('2025' in v or '2026' in v):
                date_keys.add(f"rel.{k}")

print(f"Date-related keys found: {date_keys}")
