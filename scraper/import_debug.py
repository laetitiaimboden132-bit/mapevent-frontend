"""Debug import - test avec 1 seul événement"""
import requests, json, sys, io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

# Test avec 1 event simple
test_event = {
    "title": "Test Import Vaud Debug",
    "description": "Description test pour debug import Vaud",
    "location": "Lausanne, Vaud, Suisse",
    "latitude": 46.5197,
    "longitude": 6.6323,
    "date": "2026-06-15",
    "end_date": "2026-06-15",
    "source_url": "https://test-debug-vaud-import-12345.ch/test",
    "categories": ["Événement"],
    "organizer_email": None,
    "organizer_name": ""
}

payload = {"events": [test_event], "send_emails": False}

print("Envoi test event...")
print(f"Payload size: {len(json.dumps(payload))} bytes")

r = requests.post(
    f"{API_URL}/api/events/scraped/batch",
    json=payload,
    headers={"Content-Type": "application/json"},
    timeout=30
)

print(f"Status: {r.status_code}")
print(f"Response: {r.text}")

# Maintenant essayer avec un event réel du fichier
with open("vaud_events_final.json", "r", encoding="utf-8") as f:
    events = json.load(f)

first = events[0]
first_copy = dict(first)
if 'date' not in first_copy and 'start_date' in first_copy:
    first_copy['date'] = first_copy['start_date']

print(f"\nEvent 1 keys: {sorted(first_copy.keys())}")
print(f"Title: {first_copy.get('title')}")
print(f"Source URL: {first_copy.get('source_url')}")
print(f"Date: {first_copy.get('date')}")
print(f"Location: {first_copy.get('location')}")
print(f"Categories: {first_copy.get('categories')}")

payload2 = {"events": [first_copy], "send_emails": False}
print(f"\nEnvoi event reel #1...")
print(f"Payload size: {len(json.dumps(payload2))} bytes")

r2 = requests.post(
    f"{API_URL}/api/events/scraped/batch",
    json=payload2,
    headers={"Content-Type": "application/json"},
    timeout=30
)
print(f"Status: {r2.status_code}")
print(f"Response: {r2.text}")
