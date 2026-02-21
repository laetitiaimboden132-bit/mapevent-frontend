"""
Import d'événements de Barcelone depuis Open Data BCN.
Source: opendata-ajuntament.barcelona.cat
Licence: Creative Commons Attribution 4.0 (CC-BY 4.0)
"""

import requests
import json
import time
import re
from datetime import datetime, date

API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (open data consumer)"}
BCN_URL = "https://opendata-ajuntament.barcelona.cat/data/dataset/2767159c-1c98-46b8-a686-2b25b40cb053/resource/59b9c807-f6c1-4c10-ac51-1ace65485079/download"

def clean_html(text, max_len=300):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', str(text))
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_len:
        text = text[:max_len].rsplit(' ', 1)[0] + "..."
    return text


def categorize_bcn(classifications, name):
    """Catégorise à partir des classifications BCN."""
    cats = []
    combined = " ".join([c.get("name", "") for c in classifications] + [name]).lower()
    
    # Mapping des types BCN vers nos catégories
    if any(w in combined for w in ["concert", "música", "musica"]):
        if "jazz" in combined: cats.append("Musique > Jazz")
        elif "flamenc" in combined: cats.append("Musique > Flamenco")
        elif "clàssic" in combined or "simfònic" in combined: cats.append("Musique > Classique")
        elif "electrònic" in combined or "techno" in combined or "dance" in combined: cats.append("Musique > Electronic")
        elif "rock" in combined or "pop" in combined: cats.append("Musique > Rock")
        elif "hip-hop" in combined or "rap" in combined: cats.append("Musique > Hip-Hop")
        else: cats.append("Musique > Concert")
    
    if any(w in combined for w in ["exposició", "exposicio"]):
        cats.append("Culture > Exposition")
    
    if any(w in combined for w in ["teatre", "teatro", "comèdia"]):
        cats.append("Spectacle > Théâtre")
    
    if any(w in combined for w in ["dansa", "danza", "ballet"]):
        cats.append("Danse")
    
    if any(w in combined for w in ["festival", "festa", "feria", "carnaval"]):
        cats.append("Festival")
    
    if any(w in combined for w in ["cinema", "cine", "projecció"]):
        cats.append("Culture > Cinéma")
    
    if any(w in combined for w in ["conferència", "taller", "xerrada", "curs"]):
        cats.append("Culture > Conférence")
    
    if any(w in combined for w in ["esport", "marató", "atletisme"]):
        cats.append("Sport")
    
    if any(w in combined for w in ["mercat", "fira"]):
        cats.append("Marché")
    
    if any(w in combined for w in ["infantil", "família", "nens"]):
        cats.append("Famille")
    
    if any(w in combined for w in ["visita", "ruta"]):
        cats.append("Culture > Visite guidée")
    
    if not cats:
        cats = ["Divertissement"]
    
    return cats[:3]


def get_source_url(item):
    """Extract the best source URL for an event."""
    # Try values (Web, ticket URL)
    for v in item.get("values", []):
        url_val = v.get("url_value")
        if url_val and url_val.startswith("http"):
            attr_name = v.get("attribute_name", "").lower()
            # Prefer "Web" over "Web venda d'entrades"
            if "web" in attr_name and "venda" not in attr_name:
                return url_val
    
    # Fallback to any URL in values
    for v in item.get("values", []):
        url_val = v.get("url_value")
        if url_val and url_val.startswith("http"):
            return url_val
    
    return None


def fetch_barcelona_events():
    print("📥 Téléchargement données Barcelone (CC-BY 4.0)...")
    r = requests.get(BCN_URL, headers=HEADERS, timeout=60)
    if r.status_code != 200:
        print(f"  ❌ Erreur: {r.status_code}")
        return []
    
    data = r.json()
    print(f"  📊 {len(data)} events bruts")
    
    today = date.today()
    events = []
    no_geo = 0
    no_date = 0
    no_url = 0
    past = 0
    
    for item in data:
        name = item.get("name")
        if not name:
            continue
        
        # Status check
        if item.get("status") != "published":
            continue
        
        # Geo
        geo = item.get("geo_epgs_4326_latlon")
        if not geo:
            no_geo += 1
            continue
        
        lat = geo.get("lat")
        lon = geo.get("lon")
        if not lat or not lon:
            no_geo += 1
            continue
        
        # Validate Barcelona area (roughly)
        if not (41.3 <= lat <= 41.5 and 2.0 <= lon <= 2.3):
            continue
        
        # Dates
        start_str = item.get("start_date")
        end_str = item.get("end_date")
        
        if not start_str:
            no_date += 1
            continue
        
        try:
            start_dt = datetime.fromisoformat(start_str)
            start_date = start_dt.strftime("%Y-%m-%d")
            start_time = start_dt.strftime("%H:%M") if start_dt.hour or start_dt.minute else None
        except:
            no_date += 1
            continue
        
        end_date = None
        end_time = None
        if end_str:
            try:
                end_dt = datetime.fromisoformat(end_str)
                end_date = end_dt.strftime("%Y-%m-%d")
                end_time = end_dt.strftime("%H:%M") if end_dt.hour or end_dt.minute else None
            except:
                pass
        
        # Vérifier que l'event est futur
        check_date = end_date or start_date
        try:
            if datetime.strptime(check_date, "%Y-%m-%d").date() < today:
                past += 1
                continue
        except:
            pass
        
        # Source URL
        source_url = get_source_url(item)
        if not source_url:
            no_url += 1
            continue
        
        # Description
        body = item.get("body", "")
        description = clean_html(body)
        
        # Location
        addrs = item.get("addresses", [])
        location_parts = []
        if addrs:
            addr = addrs[0]
            place = addr.get("place", "")
            if place:
                location_parts.append(place)
            street = addr.get("address_name", "")
            num = addr.get("start_street_number", "")
            if street:
                if num:
                    location_parts.append(f"{street} {num}")
                else:
                    location_parts.append(street)
            district = addr.get("district_name", "")
            if district:
                location_parts.append(district)
        location_parts.append("Barcelona, Espagne")
        location = ", ".join(location_parts)
        
        # Categories
        classifications = item.get("classifications_data", [])
        categories = categorize_bcn(classifications, name)
        
        events.append({
            "title": name.strip(),
            "description": description,
            "location": location,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "date": start_date,
            "time": start_time,
            "end_date": end_date,
            "end_time": end_time,
            "categories": categories,
            "source_url": source_url,
            "validation_status": "auto_validated",
            "status": "active",
        })
    
    print(f"  Statistiques:")
    print(f"    ✅ {len(events)} événements futurs avec données complètes")
    print(f"    ❌ {no_geo} sans coordonnées")
    print(f"    ❌ {no_date} sans date")
    print(f"    ❌ {no_url} sans URL source")
    print(f"    ❌ {past} passés")
    
    return events


def deduplicate_with_existing(new_events):
    print("\n🔍 Vérification des doublons...")
    r = requests.get(f"{API_BASE}/events", timeout=30)
    if r.status_code != 200:
        return new_events
    
    existing = r.json()
    existing_titles = set((e.get("title") or "").lower().strip() for e in existing)
    existing_urls = set(e.get("source_url") or "" for e in existing)
    
    unique = []
    dupes = 0
    for ev in new_events:
        if ev["title"].lower().strip() in existing_titles or ev["source_url"] in existing_urls:
            dupes += 1
        else:
            unique.append(ev)
    
    print(f"  📊 {dupes} doublons, {len(unique)} uniques")
    return unique


def import_events(events, batch_size=30):
    if not events:
        print("  Aucun événement à importer.")
        return 0
    
    print(f"\n📤 Import {len(events)} événements Barcelone...")
    total = 0
    for i in range(0, len(events), batch_size):
        batch = events[i:i+batch_size]
        try:
            r = requests.post(f"{API_BASE}/events/scraped/batch", json={"events": batch},
                            headers={"Content-Type": "application/json"}, timeout=30)
            if r.status_code in (200, 201):
                count = r.json().get("imported", len(batch))
                total += count
                print(f"  ✅ Batch {i//batch_size + 1}: {count}")
            else:
                print(f"  ❌ Batch {i//batch_size + 1}: {r.status_code} - {r.text[:100]}")
        except Exception as e:
            print(f"  ❌ Batch {i//batch_size + 1}: {e}")
        time.sleep(1)
    
    print(f"🎉 Total importé: {total}")
    return total


if __name__ == "__main__":
    print("=" * 60)
    print("🇪🇸 IMPORT ÉVÉNEMENTS BARCELONE - OPEN DATA BCN")
    print("   Licence: CC-BY 4.0")
    print("=" * 60)
    
    events = fetch_barcelona_events()
    
    if events:
        print(f"\nAperçu (5 premiers):")
        for e in events[:5]:
            print(f"  {e['date']} | {e['title'][:50]}")
            print(f"    📍 {e['latitude']:.4f}, {e['longitude']:.4f}")
            print(f"    🔗 {e['source_url'][:70]}")
            print(f"    📂 {e['categories']}")
        
        unique = deduplicate_with_existing(events)
        
        if unique:
            import_events(unique)
    
    print("\n✅ Terminé!")
