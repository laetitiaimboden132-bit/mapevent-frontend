"""
Suppression des events provenant de sources NON open data.
- ra.co / es.ra.co : Resident Advisor (commercial)
- goabase.net : Goabase (party database, commercial)  
- eventfrog.ch : Eventfrog (billetterie commerciale)
"""
import requests
from urllib.parse import urlparse

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

# Domaines NON open data à supprimer
NON_OPENDATA_DOMAINS = [
    "ra.co",
    "es.ra.co",
    "www.ra.co",
    "goabase.net",
    "www.goabase.net",
    "eventfrog.ch",
    "www.eventfrog.ch",
]

def main():
    print("=" * 60)
    print("SUPPRESSION EVENTS NON OPEN DATA")
    print("=" * 60)
    
    # Fetch tous les events
    print("\nFetch de tous les events...")
    r = requests.get(f"{API}/api/events", timeout=60)
    events = r.json()
    if isinstance(events, dict):
        events = events.get("events", [])
    print(f"  Total sur la carte: {len(events)}")
    
    # Identifier les events non open data
    to_delete = []
    for ev in events:
        url = (ev.get("source_url") or "").lower().strip()
        if not url:
            continue
        try:
            domain = urlparse(url).netloc
        except:
            continue
        
        if domain in NON_OPENDATA_DOMAINS:
            to_delete.append(ev)
    
    print(f"\n  Events NON open data trouvés: {len(to_delete)}")
    
    # Stats par domaine
    domain_counts = {}
    for ev in to_delete:
        url = ev.get("source_url", "")
        domain = urlparse(url).netloc
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
        print(f"    {domain}: {count} events")
    
    if not to_delete:
        print("\n  Rien à supprimer!")
        return
    
    # Exemples
    print(f"\n  Exemples:")
    for ev in to_delete[:5]:
        print(f"    ID={ev.get('id')} | {ev.get('title', '')[:50]} | {ev.get('source_url', '')[:60]}")
    
    # SUPPRESSION
    ids = [ev["id"] for ev in to_delete if ev.get("id")]
    print(f"\n  Suppression de {len(ids)} events...")
    
    total_deleted = 0
    batch_size = 50
    for i in range(0, len(ids), batch_size):
        batch = ids[i:i+batch_size]
        try:
            r = requests.post(f"{API}/api/events/delete-by-ids",
                            json={"ids": batch}, timeout=30)
            resp = r.json()
            deleted = resp.get("deleted_count", 0)
            total_deleted += deleted
            print(f"    Batch {i//batch_size+1}: {deleted} supprimés")
        except Exception as e:
            print(f"    Batch {i//batch_size+1} ERREUR: {e}")
    
    print(f"\n{'=' * 60}")
    print(f"TOTAL SUPPRIMÉS: {total_deleted}")
    print(f"Events restants: ~{len(events) - total_deleted}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
