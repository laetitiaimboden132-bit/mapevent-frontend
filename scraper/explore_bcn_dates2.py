"""Find BCN events with actual dates."""
import requests, json

HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}
url = "https://opendata-ajuntament.barcelona.cat/data/dataset/2767159c-1c98-46b8-a686-2b25b40cb053/resource/59b9c807-f6c1-4c10-ac51-1ace65485079/download"
r = requests.get(url, headers=HEADERS, timeout=30)
data = r.json()

# Check top-level start_date/end_date
has_dates = 0
no_dates = 0
has_ical = 0
for item in data:
    sd = item.get('start_date')
    ed = item.get('end_date')
    ical = item.get('ical')
    if sd or ed:
        has_dates += 1
        if has_dates <= 3:
            print(f"HAS DATE: {item.get('name')}")
            print(f"  start_date={sd}, end_date={ed}")
            if ical:
                print(f"  ical={ical[:200]}")
    else:
        no_dates += 1
    if ical:
        has_ical += 1
        if has_ical <= 3 and not (sd or ed):
            print(f"HAS ICAL (no date): {item.get('name')}")
            print(f"  ical={ical[:300]}")

print(f"\nStats: {has_dates} with dates, {no_dates} without, {has_ical} with ical")

# Check all keys
print("\nAll top-level keys across events:")
all_keys = set()
for item in data[:100]:
    all_keys.update(item.keys())
print(sorted(all_keys))
