"""
Import des événements scrapés V4 avec envoi d'emails aux organisateurs
"""

import json
import requests
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

API_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

def main():
    # 1. Lire les événements
    print("📂 Lecture du fichier valais_events_v4.json...")
    with open("valais_events_v4.json", "r", encoding="utf-8") as f:
        events = json.load(f)
    
    # 2. Filtrer les événements valides (avec date et email)
    valid_events = []
    for ev in events:
        # Exclure ceux sans date
        if not ev.get("start_date"):
            print(f"  ⏭️ Sans date: {ev.get('title', '?')[:30]}")
            continue
        # Exclure ceux sans email
        if not ev.get("organizer_email"):
            print(f"  ⏭️ Sans email: {ev.get('title', '?')[:30]}")
            continue
        # Corriger les emails mal formés
        email = ev.get("organizer_email", "")
        if email.endswith(".chre"):
            email = email[:-1]  # Corriger .chre -> .chr... non, .ch
            email = email.replace(".chre", ".ch")
            ev["organizer_email"] = email
        valid_events.append(ev)
    
    print(f"\n📋 {len(valid_events)} événements valides avec email\n")
    
    # 3. Préparer pour l'API batch
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
            "organizer_name": ev.get("organizer_name", ""),
            "organizer_email": ev["organizer_email"]
        })
    
    # 4. Afficher un résumé avant envoi
    print("📧 Emails qui vont recevoir une notification:")
    unique_emails = set(e["organizer_email"] for e in batch_events)
    for email in sorted(unique_emails):
        count = sum(1 for e in batch_events if e["organizer_email"] == email)
        print(f"  • {email} ({count} événement(s))")
    
    print(f"\n🚀 Envoi de {len(batch_events)} événements avec send_emails=true...")
    
    # 5. Envoyer à l'API
    response = requests.post(
        f"{API_URL}/api/events/scraped/batch",
        json={
            "events": batch_events,
            "send_emails": True  # ENVOI DES EMAILS ACTIVÉ
        },
        headers={"Content-Type": "application/json"},
        timeout=120
    )
    
    print(f"\n📡 Réponse API: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCÈS!")
        print(f"   Événements créés: {result.get('results', {}).get('created', 0)}")
        print(f"   Événements skippés: {result.get('results', {}).get('skipped', 0)}")
        print(f"   Événements échoués: {result.get('results', {}).get('failed', 0)}")
        print(f"   📧 Emails envoyés: {result.get('results', {}).get('emails_sent', 0)}")
        
        if result.get('results', {}).get('errors'):
            print(f"\n⚠️ Erreurs:")
            for err in result['results']['errors'][:5]:
                print(f"   - {err}")
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(response.text[:500])


if __name__ == "__main__":
    main()
