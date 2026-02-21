"""
Import des vrais événements scrapés vers l'API
"""

import json
import requests
import sys
import io

# Forcer UTF-8 sur Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

API_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

def main():
    # Lire les événements
    with open("valais_events_v3.json", "r", encoding="utf-8") as f:
        events = json.load(f)
    
    # Filtrer les événements valides
    valid_events = []
    for ev in events:
        # Exclure les calendriers (titres commençant par LuMaMeJe)
        if ev.get("title", "").startswith("LuMaMeJe"):
            continue
        # Exclure ceux sans date
        if not ev.get("start_date"):
            continue
        valid_events.append(ev)
    
    print(f"📋 {len(valid_events)} événements valides à importer")
    
    # Préparer pour l'API batch
    batch_events = []
    for ev in valid_events:
        batch_events.append({
            "title": ev["title"],
            "description": ev["description"],
            "location": ev["location"],
            "latitude": ev["latitude"],
            "longitude": ev["longitude"],
            "date": ev["start_date"],
            "end_date": ev.get("end_date") or ev["start_date"],
            "time": "00:00:00",
            "categories": ev.get("categories", []),
            "source_url": ev["source_url"],
            "organizer_name": ev.get("organizer_name", "")
            # Pas d'organizer_email car non disponible
        })
    
    # Envoyer à l'API
    print(f"📤 Envoi vers l'API...")
    
    response = requests.post(
        f"{API_URL}/api/events/scraped/batch",
        json={
            "events": batch_events,
            "send_emails": False  # Pas d'emails car pas d'adresses
        },
        headers={"Content-Type": "application/json"},
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Succès!")
        print(f"   Créés: {result.get('results', {}).get('created', 0)}")
        print(f"   Skippés: {result.get('results', {}).get('skipped', 0)}")
        print(f"   Échoués: {result.get('results', {}).get('failed', 0)}")
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    main()
