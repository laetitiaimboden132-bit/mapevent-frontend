import requests, json

# ISO-8601 format required
FROM = "2026-02-13T00:00:00+01:00"

r = requests.get("https://search.uitdatabank.be/events", params={
    "apiKey": "test",
    "limit": 3,
    "embed": "true",
    "availableFrom": FROM,
}, timeout=15)

print(f"Status: {r.status_code}")
if r.status_code != 200:
    print(r.text[:500])
    # Try without availableFrom
    print("\n--- Sans availableFrom ---")
    r = requests.get("https://search.uitdatabank.be/events", params={
        "apiKey": "test",
        "limit": 3,
        "embed": "true",
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
else:
    print("No members")
    print(r.text[:500])

# Try counting
print("\n--- Total events futurs ---")
r2 = requests.get("https://search.uitdatabank.be/events", params={
    "apiKey": "test",
    "limit": 0,
}, timeout=15)
print(f"Status: {r2.status_code}, Total: {r2.json().get('totalItems','?') if r2.status_code == 200 else r2.text[:200]}")
