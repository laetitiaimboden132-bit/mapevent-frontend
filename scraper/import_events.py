"""
Import des événements scrapés via l'API batch
"""
import json
import requests
import sys
import io

# Forcer UTF-8 sur Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

def import_events(json_file: str, batch_size: int = 50, send_emails: bool = False):
    """
    Importe les événements depuis un fichier JSON via l'API batch
    
    Args:
        json_file: Chemin vers le fichier JSON
        batch_size: Nombre d'événements par batch (max 100)
        send_emails: Envoyer les emails de validation aux organisateurs
    """
    print(f"\n{'='*60}")
    print(f"IMPORT D'ÉVÉNEMENTS VERS MAPEVENT")
    print(f"{'='*60}")
    
    # Charger les événements
    with open(json_file, 'r', encoding='utf-8') as f:
        events = json.load(f)
    
    print(f"Fichier: {json_file}")
    print(f"Événements à importer: {len(events)}")
    print(f"Taille des batchs: {batch_size}")
    print(f"Envoi emails: {'Oui' if send_emails else 'Non'}")
    print(f"{'='*60}\n")
    
    total_created = 0
    total_skipped = 0
    total_failed = 0
    
    # Importer par batchs
    for i in range(0, len(events), batch_size):
        batch = events[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(events) + batch_size - 1) // batch_size
        
        print(f"Batch {batch_num}/{total_batches} ({len(batch)} événements)...", end=" ")
        
        # Préparer les événements pour l'API
        api_events = []
        for event in batch:
            api_event = {
                "title": event.get("title", "")[:255],
                "description": event.get("description", "")[:2000],
                "location": event.get("location", "Valais, Suisse")[:255],
                "latitude": event.get("latitude", 46.2333),
                "longitude": event.get("longitude", 7.3667),
                "date": event.get("start_date") or event.get("date"),
                "end_date": event.get("end_date"),
                "time": event.get("start_time") or event.get("time"),
                "categories": event.get("categories", []),
                "source_url": event.get("source_url", ""),
                "organizer_name": event.get("organizer_name") or event.get("source_name", ""),
                "organizer_email": event.get("organizer_email")
            }
            api_events.append(api_event)
        
        try:
            response = requests.post(
                f"{API_BASE}/api/events/scraped/batch",
                json={
                    "events": api_events,
                    "send_emails": send_emails
                },
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                results = result.get("results", {})
                created = results.get("created", 0)
                skipped = results.get("skipped", 0)
                failed = results.get("failed", 0)
                
                total_created += created
                total_skipped += skipped
                total_failed += failed
                
                print(f"OK (créés: {created}, ignorés: {skipped}, échoués: {failed})")
            else:
                print(f"ERREUR HTTP {response.status_code}")
                print(f"  Réponse: {response.text[:200]}")
                total_failed += len(batch)
                
        except Exception as e:
            print(f"ERREUR: {e}")
            total_failed += len(batch)
    
    print(f"\n{'='*60}")
    print(f"RÉSULTAT FINAL")
    print(f"{'='*60}")
    print(f"Créés:   {total_created}")
    print(f"Ignorés: {total_skipped} (doublons)")
    print(f"Échoués: {total_failed}")
    print(f"{'='*60}\n")
    
    return total_created, total_skipped, total_failed


if __name__ == "__main__":
    # Importer les événements V2 (300 événements générés)
    import_events("valais_events.json", batch_size=50, send_emails=False)
