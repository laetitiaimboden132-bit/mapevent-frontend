"""
Import events Goabase (API publique, attribution: backlink goabase.net)
- Events électro/festivals dans tous les pays disponibles
- 358 events dans 38 pays
"""
import requests
import time
import re
from datetime import date, datetime

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (https://mapevent.world)"}
BASE = "https://www.goabase.net/api/party/json/"


def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:1000]


def classify_goabase(name, lineup, event_type, keywords=""):
    text = f"{name} {lineup} {event_type} {keywords}".lower()
    cats = []
    
    if any(w in text for w in ["techno", "industrial", "acid techno"]):
        cats.append("Musique > Techno")
    elif any(w in text for w in ["psytrance", "goa trance", "goa", "progressive trance"]):
        cats.append("Musique > Trance")
    elif any(w in text for w in ["house", "deep house", "minimal"]):
        cats.append("Musique > House")
    elif any(w in text for w in ["drum and bass", "drum & bass", "dnb", "jungle"]):
        cats.append("Musique > Drum & Bass")
    elif any(w in text for w in ["dub", "reggae"]):
        cats.append("Musique > Dub")
    elif any(w in text for w in ["trance"]):
        cats.append("Musique > Trance")
    else:
        cats.append("Musique > Électronique")
    
    if event_type.lower() in ["festival", "openair", "open air"]:
        cats.append("Culture > Festival")
    
    return cats[:3]


def send_batch(events, batch_size=10):
    total_created = 0
    total_skipped = 0
    for i in range(0, len(events), batch_size):
        batch = events[i:i+batch_size]
        try:
            r = requests.post(f"{API}/api/events/scraped/batch", json={"events": batch}, timeout=30)
            resp = r.json()
            results = resp.get("results", resp)
            created = results.get("created", 0) or results.get("inserted", 0)
            skipped = results.get("skipped", 0) + results.get("failed", 0)
            total_created += created
            total_skipped += skipped
            print(f"  Batch {i//batch_size+1}: +{created} insérés, {skipped} skippés")
        except Exception as e:
            print(f"  Batch {i//batch_size+1} ERREUR: {e}")
            total_skipped += len(batch)
        time.sleep(0.5)
    return total_created, total_skipped


def main():
    print("=" * 60)
    print("IMPORT GOABASE - TOUS LES PAYS")
    print(f"Source: goabase.net API (publique, backlink requis)")
    print(f"Date: {TODAY}")
    print("=" * 60)
    
    # Fetch tous les events (limit=500 = max)
    print("\nFetch de tous les events...")
    r = requests.get(BASE, params={"limit": 500}, headers=HEADERS, timeout=30)
    data = r.json()
    parties = data.get("partylist", [])
    print(f"  Reçu: {len(parties)} events")
    
    all_events = []
    seen_ids = set()
    country_counts = {}
    
    for p in parties:
        pid = p.get("id")
        if not pid or pid in seen_ids:
            continue
        seen_ids.add(pid)
        
        name = p.get("nameParty", "").strip()
        if not name:
            continue
        
        lat = p.get("geoLat")
        lon = p.get("geoLon")
        if not lat or not lon:
            continue
        lat, lon = float(lat), float(lon)
        
        # Dates
        start = p.get("dateStart", "")
        end = p.get("dateEnd", "")
        
        # Filtrer passés
        if start:
            try:
                sd = datetime.fromisoformat(start).date()
                if sd < date.today():
                    continue
            except:
                pass
        
        country = p.get("isoCountry", "?")
        country_name = p.get("nameCountry", "?")
        town = p.get("nameTown", "")
        event_type = p.get("nameType", "")
        organizer = p.get("nameOrganizer", "")
        
        source_url = f"https://www.goabase.net/party/{pid}"
        
        # Fetch détails pour le lineup
        lineup = ""
        try:
            rd = requests.get(f"{BASE}{pid}", headers=HEADERS, timeout=10)
            detail = rd.json()
            party_detail = detail.get("party", {})
            lineup = party_detail.get("nameLineUp", "") or ""
            time.sleep(0.3)
        except:
            pass
        
        desc_parts = []
        if lineup:
            desc_parts.append(f"Line-up: {clean_html(lineup)[:300]}")
        if organizer:
            desc_parts.append(f"Organisateur: {organizer}")
        if event_type:
            desc_parts.append(f"Type: {event_type}")
        desc = ". ".join(desc_parts) if desc_parts else f"Événement électro à {town or country_name}"
        
        location = f"{town}, {country_name}" if town else country_name
        categories = classify_goabase(name, lineup, event_type)
        
        country_counts[country] = country_counts.get(country, 0) + 1
        
        all_events.append({
            "title": name,
            "description": desc[:500],
            "date": start[:10] if start else None,
            "end_date": end[:10] if end else None,
            "time": start[11:16] if start and len(start) > 15 else None,
            "end_time": end[11:16] if end and len(end) > 15 else None,
            "location": location,
            "latitude": lat,
            "longitude": lon,
            "categories": categories,
            "source_url": source_url,
            "source": "Goabase",
            "validation_status": "auto_validated",
            "country": country,
        })
    
    print(f"\nParsés: {len(all_events)} events futurs")
    
    # Stats par pays
    print(f"\nPar pays:")
    for c, count in sorted(country_counts.items(), key=lambda x: -x[1]):
        print(f"  {c}: {count}")
    
    if not all_events:
        print("Aucun event à importer!")
        return
    
    # Envoi
    print(f"\nEnvoi au serveur ({len(all_events)} events)...")
    created, skipped = send_batch(all_events)
    
    print(f"\n{'=' * 60}")
    print(f"RÉSULTAT GOABASE:")
    print(f"  Insérés: {created}")
    print(f"  Skippés (doublons): {skipped}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
