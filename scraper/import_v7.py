"""Import V7 events - sans envoi de mails"""
import requests, json, sys, io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

with open("valais_events_v7.json", "r", encoding="utf-8") as f:
    events = json.load(f)

print(f"📦 {len(events)} événements V7 à importer")

payload = {"events": events, "send_emails": False}
print("📡 Envoi vers l'API...", flush=True)

r = requests.post(
    f"{API_URL}/api/events/scraped/batch",
    json=payload,
    headers={"Content-Type": "application/json"},
    timeout=120
)

print(f"Status: {r.status_code}")
try:
    data = r.json()
    print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
except:
    print(r.text[:500])
