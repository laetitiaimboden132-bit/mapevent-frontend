"""Explore UiTdatabank API structure for Belgian events."""
import requests
import json
from datetime import datetime

TODAY = datetime.now().strftime("%Y-%m-%d")
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}

print("=" * 60)
print("UITDATABANK - Exploration")
print("=" * 60)

# 1. Search events - get detailed structure
url = "https://search.uitdatabank.be/events/"
params = {
    "apiKey": "test",
    "limit": 3,
    "availableFrom": TODAY,
    "embed": "true",  # Get full event details
}
r = requests.get(url, params=params, headers=HEADERS, timeout=15)
print(f"Status: {r.status_code}")
data = r.json()
print(f"Total items: {data.get('totalItems', '?')}")

members = data.get("member", [])
for i, ev in enumerate(members[:2]):
    print(f"\n--- Event {i+1} ---")
    print(json.dumps(ev, indent=2, ensure_ascii=False)[:2000])

# 2. Check what fields are available
if members:
    print(f"\n--- Champs disponibles ---")
    print(list(members[0].keys()))

# 3. Try filtering by region
print(f"\n--- Par région ---")
for region in ["gem-bruxelles", "gem-gent", "gem-antwerpen", "gem-liege", "gem-namur", "gem-charleroi", "gem-brugge", "gem-leuven", "gem-mons"]:
    params2 = {
        "apiKey": "test",
        "limit": 0,
        "availableFrom": TODAY,
        "regions": region,
    }
    r2 = requests.get(url, params=params2, headers=HEADERS, timeout=10)
    if r2.status_code == 200:
        total = r2.json().get("totalItems", 0)
        print(f"  {region}: {total} events")

# 4. Try with workflowStatus
print(f"\n--- Avec embed + workflowStatus ---")
params3 = {
    "apiKey": "test", 
    "limit": 2,
    "availableFrom": TODAY,
    "embed": "true",
    "workflowStatus": "APPROVED,READY_FOR_VALIDATION",
}
r3 = requests.get(url, params=params3, headers=HEADERS, timeout=15)
print(f"Status: {r3.status_code}")
if r3.status_code == 200:
    d3 = r3.json()
    print(f"Total: {d3.get('totalItems', '?')}")
    for ev in d3.get("member", [])[:1]:
        # Show key fields
        name = ev.get("name", {})
        loc = ev.get("location", {})
        geo = loc.get("geo", {}) if isinstance(loc, dict) else {}
        addr = loc.get("address", {}) if isinstance(loc, dict) else {}
        print(f"  Name: {name}")
        print(f"  Location name: {loc.get('name', '?') if isinstance(loc, dict) else '?'}")
        print(f"  Geo: {geo}")
        print(f"  Address: {json.dumps(addr, ensure_ascii=False)[:200]}")
        print(f"  StartDate: {ev.get('startDate', '?')}")
        print(f"  EndDate: {ev.get('endDate', '?')}")
        print(f"  Terms: {[t.get('label') for t in ev.get('terms', []) if t.get('label')]}")
        print(f"  URL: {ev.get('sameAs', '?')}")

print("\n" + "=" * 60)
