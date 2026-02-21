"""
Import d'événements en Suisse depuis des sources vérifiées:

1. OpenAgenda (Licence Ouverte v1.0) - 913 events CH
2. Goabase API (publique, gratuite, attribution requise: backlink goabase.net)
   - Events électro/festivals en Suisse

Toutes les données sont légalement réutilisables.
"""
import requests
import time
import re
from datetime import date, datetime

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
TODAY = date.today().isoformat()


def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&nbsp;|&amp;|&lt;|&gt;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:1000]


def categorize(title, desc, keywords=None):
    text = f"{title} {desc} {' '.join(keywords or [])}".lower()
    cats = []
    if any(w in text for w in ["concert", "musique", "music", "jazz", "rock", "orchestre", "chorale"]):
        cats.append("Musique > Concert")
    if any(w in text for w in ["techno", "house", "electro", "trance", "drum", "bass", "dj", "rave"]):
        cats.append("Musique > Électronique")
    if any(w in text for w in ["exposition", "expo", "museum", "musée", "galerie", "art"]):
        cats.append("Culture > Exposition")
    if any(w in text for w in ["théâtre", "spectacle", "danse", "ballet", "cirque"]):
        cats.append("Culture > Spectacle")
    if any(w in text for w in ["festival"]):
        cats.append("Culture > Festival")
    if any(w in text for w in ["conférence", "atelier", "workshop", "formation"]):
        cats.append("Éducation > Atelier")
    if any(w in text for w in ["sport", "course", "marathon", "vélo"]):
        cats.append("Sport")
    if any(w in text for w in ["marché", "brocante", "foire"]):
        cats.append("Marché & Brocante")
    if any(w in text for w in ["enfant", "famille", "kids"]):
        cats.append("Famille")
    if not cats:
        cats.append("Événement")
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


# ================================================================
# SOURCE 1: OpenAgenda - Events Suisse (Licence Ouverte v1.0)
# ================================================================
def fetch_openagenda_swiss():
    print("\n--- OpenAgenda Suisse (Licence Ouverte v1.0) ---")
    BASE = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"
    
    all_events = []
    offset = 0
    
    while True:
        r = requests.get(BASE, params={
            "where": f'location_countrycode="CH" AND lastdate_end>="{TODAY}"',
            "select": "uid,title_fr,description_fr,longdescription_fr,firstdate_begin,lastdate_end,"
                      "location_coordinates,location_address,location_city,location_postalcode,"
                      "location_name,canonicalurl,keywords_fr",
            "limit": 100,
            "offset": offset,
            "order_by": "firstdate_begin",
        }, timeout=30)
        
        data = r.json()
        results = data.get("results", [])
        total = data.get("total_count", 0)
        
        if offset == 0:
            print(f"  Total disponible: {total}")
        
        if not results:
            break
        
        for rec in results:
            coords = rec.get("location_coordinates")
            if not coords or not coords.get("lat") or not coords.get("lon"):
                continue
            
            lat, lon = float(coords["lat"]), float(coords["lon"])
            if not (45.8 <= lat <= 47.8 and 5.9 <= lon <= 10.5):
                continue
            
            title = (rec.get("title_fr") or "").strip()
            source_url = rec.get("canonicalurl", "")
            if not title or not source_url:
                continue
            
            desc = clean_html(rec.get("longdescription_fr") or rec.get("description_fr") or "")
            keywords = rec.get("keywords_fr") or []
            
            start_str = rec.get("firstdate_begin", "")
            end_str = rec.get("lastdate_end", "")
            
            location_parts = [p for p in [
                rec.get("location_name"), rec.get("location_address"),
                rec.get("location_postalcode"), rec.get("location_city")
            ] if p]
            
            all_events.append({
                "title": title,
                "description": desc[:500] if desc else f"Événement à {rec.get('location_city', 'Suisse')}",
                "date": start_str[:10] if start_str else None,
                "end_date": end_str[:10] if end_str else None,
                "time": start_str[11:16] if start_str and len(start_str) > 15 and start_str[11:16] != "00:00" else None,
                "end_time": None,
                "location": ", ".join(location_parts) or "Suisse",
                "latitude": lat,
                "longitude": lon,
                "categories": categorize(title, desc, keywords),
                "source_url": source_url,
                "source": "OpenAgenda",
                "validation_status": "auto_validated",
                "country": "CH",
            })
        
        offset += len(results)
        if offset >= total:
            break
        time.sleep(0.5)
    
    print(f"  Parsés: {len(all_events)} events")
    return all_events


# ================================================================
# SOURCE 2: Goabase API (publique, attribution: backlink goabase.net)
# Events électro/festivals en Suisse
# ================================================================
def classify_goabase(name, lineup, event_type, keywords=""):
    text = f"{name} {lineup} {event_type} {keywords}".lower()
    cats = []
    
    # Sous-catégories précises de musique électronique
    if any(w in text for w in ["techno", "industrial", "acid"]):
        cats.append("Musique > Techno")
    elif any(w in text for w in ["trance", "psytrance", "goa", "progressive"]):
        cats.append("Musique > Trance")
    elif any(w in text for w in ["house", "deep house", "minimal"]):
        cats.append("Musique > House")
    elif any(w in text for w in ["drum", "bass", "dnb", "jungle"]):
        cats.append("Musique > Drum & Bass")
    elif any(w in text for w in ["dub", "reggae", "dancehall"]):
        cats.append("Musique > Dub")
    else:
        cats.append("Musique > Électronique")
    
    if event_type in ["festival", "openair"]:
        cats.append("Culture > Festival")
    
    return cats[:3]


def fetch_goabase_swiss():
    print("\n--- Goabase API - Suisse (attribution: backlink goabase.net) ---")
    BASE = "https://www.goabase.net/api/party/json/"
    
    all_events = []
    seen_ids = set()
    
    # Fetch events en Suisse
    try:
        r = requests.get(BASE, params={
            "country": "CH",
            "limit": 500,
        }, headers={"User-Agent": "MapEventAI-Bot/1.0"}, timeout=30)
        
        data = r.json()
        parties = data if isinstance(data, list) else data.get("results", data.get("events", []))
        
        if isinstance(data, dict) and "itemListElement" in data:
            parties = data["itemListElement"]
        
        print(f"  Reçu: {len(parties)} events")
        
        for p in parties:
            pid = p.get("id") or p.get("PID") or p.get("urlEventSlug", "")
            if not pid or pid in seen_ids:
                continue
            seen_ids.add(pid)
            
            name = p.get("nameParty") or p.get("name") or ""
            if not name:
                continue
            
            # Coordonnées
            lat = p.get("geoLat") or p.get("latitude")
            lon = p.get("geoLon") or p.get("longitude")
            
            if not lat or not lon:
                geo = p.get("geo") or p.get("location", {}).get("geo", {})
                if isinstance(geo, dict):
                    lat = geo.get("latitude") or geo.get("geoLat")
                    lon = geo.get("longitude") or geo.get("geoLon")
            
            if not lat or not lon:
                continue
            
            lat, lon = float(lat), float(lon)
            if not (45.8 <= lat <= 47.8 and 5.9 <= lon <= 10.5):
                continue
            
            # Dates
            start = p.get("dateStart") or p.get("startDate") or ""
            end = p.get("dateEnd") or p.get("endDate") or ""
            
            # Filtrer: événements futurs uniquement
            if start:
                try:
                    start_date = datetime.fromisoformat(start.replace("Z", "+00:00")).date()
                    if start_date < date.today():
                        continue
                except:
                    pass
            
            # Source URL
            source_url = f"https://www.goabase.net/party/{pid}"
            
            # Description
            info = p.get("urlOrganiser") or p.get("description") or ""
            lineup = p.get("nameLineUp") or p.get("performers") or ""
            event_type = p.get("nameType") or p.get("eventType") or ""
            keywords = p.get("keywords") or ""
            
            desc_parts = []
            if lineup:
                desc_parts.append(f"Line-up: {lineup[:200]}")
            if info and not info.startswith("http"):
                desc_parts.append(clean_html(info)[:200])
            desc = ". ".join(desc_parts) if desc_parts else f"Événement électro à {p.get('nameTown', 'Suisse')}"
            
            # Location
            town = p.get("nameTown") or p.get("addressLocality") or ""
            country = p.get("nameCountry") or "Switzerland"
            location_name = p.get("nameLocation") or p.get("locationName") or ""
            location = f"{location_name}, {town}" if location_name and town else (town or "Suisse")
            
            categories = classify_goabase(name, str(lineup), event_type, str(keywords))
            
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
                "country": "CH",
            })
    
    except Exception as e:
        print(f"  ERREUR: {e}")
    
    print(f"  Parsés: {len(all_events)} events CH futurs")
    return all_events


def main():
    print("=" * 60)
    print("IMPORT ÉVÉNEMENTS SUISSE")
    print(f"Date: {TODAY}")
    print("=" * 60)
    
    # 1. OpenAgenda
    oa_events = fetch_openagenda_swiss()
    
    # 2. Goabase
    goa_events = fetch_goabase_swiss()
    
    # Dédupliquer par source_url
    seen = set()
    all_events = []
    for ev in oa_events + goa_events:
        if ev["source_url"] not in seen:
            seen.add(ev["source_url"])
            all_events.append(ev)
    
    print(f"\n{'=' * 60}")
    print(f"TOTAL SUISSE: {len(all_events)} events")
    print(f"  OpenAgenda: {len(oa_events)}")
    print(f"  Goabase: {len(goa_events)}")
    print(f"  Après dédup: {len(all_events)}")
    print(f"{'=' * 60}")
    
    if not all_events:
        print("Aucun event!")
        return
    
    # Stats
    city_counts = {}
    for ev in all_events:
        loc = ev.get("location", "")
        city = loc.split(",")[-1].strip() if "," in loc else loc
        city_counts[city] = city_counts.get(city, 0) + 1
    
    print(f"\nTop villes:")
    for city, count in sorted(city_counts.items(), key=lambda x: -x[1])[:15]:
        print(f"  {city}: {count}")
    
    # Envoi
    print(f"\nEnvoi au serveur...")
    created, skipped = send_batch(all_events)
    
    print(f"\n{'=' * 60}")
    print(f"RÉSULTAT FINAL SUISSE:")
    print(f"  Insérés: {created}")
    print(f"  Skippés (doublons): {skipped}")
    print(f"{'=' * 60}")
    print(f"\nSources & licences:")
    print(f"  OpenAgenda: Licence Ouverte v1.0")
    print(f"  Goabase: API publique, attribution backlink goabase.net")


if __name__ == "__main__":
    main()
