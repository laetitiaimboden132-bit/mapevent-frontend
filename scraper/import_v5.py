"""
Import des événements scrapés V5 SANS envoi d'emails
"""

import json
import requests
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

def main():
    print("📂 Lecture de valais_events_v5.json...")
    with open("valais_events_v5.json", "r", encoding="utf-8") as f:
        events = json.load(f)
    
    print(f"📋 {len(events)} événements à importer\n")
    
    # Préparer pour l'API batch (max 100 par batch)
    batch_events = []
    for ev in events:
        if not ev.get("start_date"):
            continue
        batch_events.append({
            "title": ev["title"],
            "description": ev["description"][:500],
            "location": ev["location"],
            "latitude": ev["latitude"],
            "longitude": ev["longitude"],
            "date": ev["start_date"],
            "end_date": ev.get("end_date") or ev["start_date"],
            "time": "00:00:00",
            "categories": ev.get("categories", []),
            "source_url": ev["source_url"],
            "organizer_name": ev.get("organizer_name", ""),
            "organizer_email": ev.get("organizer_email", "")
        })
    
    print(f"🚀 Import de {len(batch_events)} événements SANS envoi d'emails...\n")
    
    response = requests.post(
        f"{API_URL}/api/events/scraped/batch",
        json={
            "events": batch_events,
            "send_emails": False
        },
        headers={"Content-Type": "application/json"},
        timeout=120
    )
    
    print(f"📡 Réponse API: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCÈS!")
        print(f"   Événements créés: {result.get('results', {}).get('created', 0)}")
        print(f"   Événements skippés: {result.get('results', {}).get('skipped', 0)}")
        print(f"   Événements échoués: {result.get('results', {}).get('failed', 0)}")
        
        if result.get('results', {}).get('errors'):
            print(f"\n⚠️ Erreurs:")
            for err in result['results']['errors'][:5]:
                print(f"   - {err}")
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(response.text[:500])


if __name__ == "__main__":
    main()
