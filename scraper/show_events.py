import json
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open("valais_events_v4.json", "r", encoding="utf-8") as f:
    events = json.load(f)

print(f"📋 {len(events)} événements scrapés:\n")
for e in events:
    title = e.get("title", "?")[:40]
    email = e.get("organizer_email", "-")
    date = e.get("start_date", "?")
    print(f"  {title:40} | {email:30} | {date}")
