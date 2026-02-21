"""Check geo_epgs_4326_latlon format."""
import requests, json

HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}
url = "https://opendata-ajuntament.barcelona.cat/data/dataset/2767159c-1c98-46b8-a686-2b25b40cb053/resource/59b9c807-f6c1-4c10-ac51-1ace65485079/download"
r = requests.get(url, headers=HEADERS, timeout=30)
data = r.json()

for item in data[:5]:
    print(f"\n{item.get('name')}")
    print(f"  geo_4326: {item.get('geo_epgs_4326_latlon')}")
    print(f"  timetable: {item.get('timetable', '')[:200]}")
    print(f"  period: {item.get('period')} | period_name: {item.get('period_name')}")
    print(f"  type: {item.get('type')} | type_name: {item.get('type_name')}")
    
    # Get web URL from values
    for v in item.get('values', []):
        if v.get('url_value'):
            print(f"  url: {v.get('url_value')}")
