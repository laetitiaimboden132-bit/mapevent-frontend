"""
Import d'événements belges depuis des sources OPEN DATA vérifiées.

Sources:
1. OpenAgenda (Licence Ouverte v1.0) - events en Belgique
2. data.stad.gent (Open Data) - events touristiques de Gand

TOUTES ces sources sont sous licence ouverte. Aucun risque légal.
"""
import requests
import time
import re
from datetime import date, datetime

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
TODAY = date.today().isoformat()


def clean_html(text):
    """Nettoie le HTML d'une description."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:1000]


def categorize_event(title, desc, keywords):
    """Catégorise un event en fonction du titre, description et mots-clés."""
    text = f"{title} {desc} {' '.join(keywords)}".lower()
    cats = []
    
    if any(w in text for w in ["concert", "musique", "music", "jazz", "rock", "electro", "dj", "orchestre"]):
        cats.append("Musique > Concert")
    if any(w in text for w in ["exposition", "expo", "galerie", "museum", "musée", "art", "peinture", "sculpture"]):
        cats.append("Culture > Exposition")
    if any(w in text for w in ["théâtre", "theater", "spectacle", "comédie", "danse", "ballet"]):
        cats.append("Culture > Spectacle")
    if any(w in text for w in ["festival"]):
        cats.append("Culture > Festival")
    if any(w in text for w in ["film", "cinéma", "cinema", "projection"]):
        cats.append("Culture > Cinéma")
    if any(w in text for w in ["marché", "markt", "brocante", "foire"]):
        cats.append("Marché & Brocante")
    if any(w in text for w in ["sport", "course", "running", "marathon", "vélo", "cycling"]):
        cats.append("Sport")
    if any(w in text for w in ["atelier", "workshop", "formation", "conférence", "conference", "lezing"]):
        cats.append("Éducation > Atelier")
    if any(w in text for w in ["enfant", "kids", "kinderen", "famille", "family"]):
        cats.append("Famille")
    if any(w in text for w in ["gastronomie", "food", "dégustation", "cuisine", "bière", "vin"]):
        cats.append("Gastronomie")
    
    if not cats:
        cats.append("Événement")
    
    return cats[:3]


# ================================================================
# SOURCE 1: OpenAgenda (Belgique)
# Licence: Licence Ouverte v1.0 (https://www.etalab.gouv.fr/licence-ouverte-open-licence)
# ================================================================

def fetch_openagenda_belgium():
    """Fetch events belges depuis OpenAgenda via OpenDataSoft."""
    print("\n--- Source 1: OpenAgenda (Licence Ouverte v1.0) ---")
    
    BASE = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"
    
    all_events = []
    offset = 0
    
    while True:
        r = requests.get(BASE, params={
            "where": f'location_countrycode="BE" AND lastdate_end>="{TODAY}"',
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
            
            lat = float(coords["lat"])
            lon = float(coords["lon"])
            
            # Vérifier que c'est en Belgique
            if not (49.5 <= lat <= 51.5 and 2.5 <= lon <= 6.5):
                continue
            
            title = rec.get("title_fr", "").strip()
            if not title:
                continue
            
            source_url = rec.get("canonicalurl", "")
            if not source_url:
                continue
            
            desc = clean_html(rec.get("longdescription_fr") or rec.get("description_fr") or "")
            keywords = rec.get("keywords_fr", []) or []
            
            # Dates
            start_str = rec.get("firstdate_begin", "")
            end_str = rec.get("lastdate_end", "")
            start_date = start_str[:10] if start_str else None
            end_date = end_str[:10] if end_str else None
            start_time = start_str[11:16] if start_str and len(start_str) > 15 else None
            
            location_parts = []
            if rec.get("location_name"):
                location_parts.append(rec["location_name"])
            if rec.get("location_address"):
                location_parts.append(rec["location_address"])
            if rec.get("location_postalcode"):
                location_parts.append(rec["location_postalcode"])
            if rec.get("location_city"):
                location_parts.append(rec["location_city"])
            
            location = ", ".join(location_parts) if location_parts else f"{rec.get('location_city', 'Belgique')}"
            
            categories = categorize_event(title, desc, keywords)
            
            all_events.append({
                "title": title,
                "description": desc[:500] if desc else f"Événement à {rec.get('location_city', 'Belgique')}",
                "date": start_date,
                "end_date": end_date,
                "time": start_time if start_time and start_time != "00:00" else None,
                "end_time": None,
                "location": location,
                "latitude": lat,
                "longitude": lon,
                "categories": categories,
                "source_url": source_url,
                "source": "OpenAgenda",
                "validation_status": "auto_validated",
                "country": "BE",
            })
        
        offset += len(results)
        if offset >= total:
            break
        time.sleep(0.5)
    
    print(f"  Parsés: {len(all_events)} events valides")
    return all_events


# ================================================================
# SOURCE 2: data.stad.gent (Gand Open Data)
# Licence: Open Data (Linked Open Data Gand)
# ================================================================

def fetch_gent_events():
    """Fetch events touristiques de Gand via data.stad.gent."""
    print("\n--- Source 2: data.stad.gent (Open Data Gand) ---")
    
    r = requests.get(
        "https://data.stad.gent/api/explore/v2.1/catalog/datasets/toeristische-evenementen-visit-gent/records",
        params={"limit": 100},
        timeout=30
    )
    
    data = r.json()
    results = data.get("results", [])
    total = data.get("total_count", 0)
    print(f"  Total disponible: {total}")
    
    all_events = []
    
    for rec in results:
        title = rec.get("name_nl") or rec.get("name_fr") or rec.get("name_en") or ""
        title = title.strip()
        if not title:
            continue
        
        # Dates
        start_str = rec.get("date_start", "")
        end_str = rec.get("date_end", "")
        
        # Filtrer: garder que les events futurs ou en cours
        if end_str:
            try:
                end_d = datetime.strptime(end_str[:10], "%Y-%m-%d").date()
                if end_d < date.today():
                    continue
            except:
                pass
        
        # URL
        url = rec.get("url", "")
        if not url:
            continue
        
        # Coordonnées
        lat = rec.get("lat")
        lon = rec.get("long")
        
        # Si pas de coords directes, essayer de géocoder avec l'adresse
        if not lat or not lon:
            address = rec.get("address", "")
            postal = rec.get("postal", "")
            city = rec.get("local", "Gent")
            
            if address or postal:
                try:
                    query = f"{address}, {postal} {city}, Belgium" if address else f"{postal} {city}, Belgium"
                    nr = requests.get("https://nominatim.openstreetmap.org/search", params={
                        "q": query, "format": "json", "limit": 1, "countrycodes": "be",
                    }, headers={"User-Agent": "MapEventAI-Bot/1.0"}, timeout=10)
                    if nr.status_code == 200 and nr.json():
                        lat = float(nr.json()[0]["lat"])
                        lon = float(nr.json()[0]["lon"])
                    time.sleep(1.1)
                except:
                    pass
        
        if not lat or not lon:
            continue
        
        lat = float(lat)
        lon = float(lon)
        
        # Vérifier Belgique
        if not (49.5 <= lat <= 51.5 and 2.5 <= lon <= 6.5):
            continue
        
        desc_nl = rec.get("description_nl", "")
        desc = clean_html(desc_nl)
        
        location_parts = [rec.get("ctcname_nl", "")]
        if rec.get("address"):
            location_parts.append(rec["address"])
        if rec.get("postal"):
            location_parts.append(rec["postal"])
        if rec.get("local"):
            location_parts.append(rec["local"])
        location = ", ".join([p for p in location_parts if p])
        
        categories = categorize_event(title, desc, [])
        
        all_events.append({
            "title": title,
            "description": desc[:500] if desc else f"Événement touristique à Gand",
            "date": start_str[:10] if start_str else None,
            "end_date": end_str[:10] if end_str else None,
            "time": None,
            "end_time": None,
            "location": location or "Gand, Belgique",
            "latitude": lat,
            "longitude": lon,
            "categories": categories,
            "source_url": url,
            "source": "data.stad.gent",
            "validation_status": "auto_validated",
            "country": "BE",
        })
    
    print(f"  Parsés: {len(all_events)} events valides (futurs)")
    return all_events


def send_batch(events, batch_size=10):
    """Envoie les events par batch."""
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
    print("IMPORT ÉVÉNEMENTS BELGIQUE - OPEN DATA UNIQUEMENT")
    print(f"Date: {TODAY}")
    print("=" * 60)
    
    # 1. OpenAgenda
    oa_events = fetch_openagenda_belgium()
    
    # 2. data.stad.gent
    gent_events = fetch_gent_events()
    
    # Dédupliquer par source_url
    seen_urls = set()
    all_events = []
    for ev in oa_events + gent_events:
        if ev["source_url"] not in seen_urls:
            seen_urls.add(ev["source_url"])
            all_events.append(ev)
    
    print(f"\n{'=' * 60}")
    print(f"TOTAL BELGIQUE OPEN DATA: {len(all_events)} events")
    print(f"  OpenAgenda: {len(oa_events)}")
    print(f"  data.stad.gent: {len(gent_events)}")
    print(f"  Après dédup: {len(all_events)}")
    print(f"{'=' * 60}")
    
    if not all_events:
        print("Aucun event à importer!")
        return
    
    # Stats par ville
    city_counts = {}
    for ev in all_events:
        city = ev.get("location", "").split(",")[-1].strip() if "," in ev.get("location", "") else "?"
        city_counts[city] = city_counts.get(city, 0) + 1
    
    print(f"\nRépartition:")
    for city, count in sorted(city_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {city}: {count}")
    
    # Envoi
    print(f"\nEnvoi au serveur...")
    created, skipped = send_batch(all_events)
    
    print(f"\n{'=' * 60}")
    print(f"RÉSULTAT FINAL:")
    print(f"  Insérés: {created}")
    print(f"  Skippés (doublons): {skipped}")
    print(f"{'=' * 60}")
    print(f"\nLicences:")
    print(f"  OpenAgenda: Licence Ouverte v1.0 (100% légal)")
    print(f"  data.stad.gent: Open Data Gand (100% légal)")


if __name__ == "__main__":
    main()
