import requests, json

r = requests.get("https://search.uitdatabank.be/events", params={
    "apiKey": "test",
    "limit": 3,
    "embed": "true",
    "availableFrom": "2026-02-13"
}, timeout=15)

print(f"Status: {r.status_code}")
data = r.json()
total = data.get("totalItems", "?")
print(f"Total: {total}")

members = data.get("member", [])
if members:
    ev = members[0]
    print(f"\nKeys: {list(ev.keys())}")
    print(json.dumps(ev, indent=2, ensure_ascii=False)[:3000])
    
    print(f"\n--- Event 2 ---")
    if len(members) > 1:
        print(json.dumps(members[1], indent=2, ensure_ascii=False)[:2000])
else:
    print("No members")
    print(r.text[:500])

# Count by region
print("\n--- Par ville ---")
for city in ["Brussel", "Gent", "Antwerpen", "Brugge", "Leuven", "Namur", "Liege", "Mons", "Charleroi"]:
    try:
        r2 = requests.get("https://search.uitdatabank.be/events", params={
            "apiKey": "test",
            "limit": 0,
            "availableFrom": "2026-02-13",
            "text": city,
        }, timeout=10)
        if r2.status_code == 200:
            print(f"  {city}: {r2.json().get('totalItems', 0)} events")
    except:
        pass
