"""
Import d'événements de toute la France via OpenAgenda (OpenDataSoft).
Source: public.opendatasoft.com/explore/dataset/evenements-publics-openagenda
Licence: Open Data (OpenAgenda public)
"""

import requests
import json
import time
import re
from datetime import datetime, date

API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (open data consumer)"}

# OpenDataSoft API for OpenAgenda public events
ODS_BASE = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"

# Villes françaises à cibler
FRENCH_CITIES = [
    "Paris", "Lyon", "Marseille", "Toulouse", "Nice",
    "Nantes", "Strasbourg", "Montpellier", "Bordeaux", "Lille",
    "Rennes", "Reims", "Saint-Étienne", "Toulon", "Le Havre",
    "Grenoble", "Dijon", "Angers", "Nîmes", "Clermont-Ferrand",
    "Aix-en-Provence", "Brest", "Tours", "Amiens", "Limoges",
    "Perpignan", "Metz", "Besançon", "Orléans", "Rouen",
    "Caen", "Nancy", "Avignon", "Cannes", "La Rochelle"
]

def clean_html(text, max_len=350):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', str(text))
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_len:
        text = text[:max_len].rsplit(' ', 1)[0] + "..."
    return text


def categorize_event(title, description, keywords):
    """Catégorisation intelligente basée sur titre, description et mots-clés."""
    cats = []
    combined = f"{title} {description} {' '.join(keywords)}".lower()
    
    # Musique
    if any(w in combined for w in ["concert", "musique", "musical", "orchestre", "chorale", "récital"]):
        if "jazz" in combined: cats.append("Musique > Jazz")
        elif "classique" in combined or "symphoni" in combined or "opéra" in combined: cats.append("Musique > Classique")
        elif any(w in combined for w in ["electro", "techno", "house", "dj ", "djset"]): cats.append("Musique > Electronic")
        elif "rock" in combined or "metal" in combined: cats.append("Musique > Rock")
        elif any(w in combined for w in ["hip-hop", "hip hop", "rap "]): cats.append("Musique > Hip-Hop")
        elif "chanson" in combined or "variété" in combined: cats.append("Musique > Chanson française")
        elif "reggae" in combined: cats.append("Musique > Reggae")
        elif "blues" in combined: cats.append("Musique > Blues")
        elif "folk" in combined: cats.append("Musique > Folk")
        else: cats.append("Musique > Concert")

    # Spectacle
    if any(w in combined for w in ["théâtre", "theatre", "comédie", "tragédie", "pièce de théâtre"]):
        cats.append("Spectacle > Théâtre")
    if any(w in combined for w in ["danse", "ballet", "chorégraph"]):
        cats.append("Danse")
    if any(w in combined for w in ["cirque", "acrobat"]):
        cats.append("Spectacle > Cirque")
    if any(w in combined for w in ["humour", "one-man", "one-woman", "stand-up", "sketch"]):
        cats.append("Spectacle > Humour")
    if any(w in combined for w in ["magie", "illusionn"]):
        cats.append("Spectacle > Magie")

    # Culture
    if any(w in combined for w in ["exposition", "expo ", "vernissage", "galerie"]):
        cats.append("Culture > Exposition")
    if any(w in combined for w in ["musée", "museum", "patrimoine", "monument"]):
        cats.append("Culture > Musée")
    if any(w in combined for w in ["cinéma", "film ", "projection", "ciné "]):
        cats.append("Culture > Cinéma")
    if any(w in combined for w in ["lecture", "littéra", "livre", "salon du livre", "dédicace", "poésie"]):
        cats.append("Culture > Littérature")

    # Sport
    if any(w in combined for w in ["course à pied", "marathon", "trail", "running", "jogging"]):
        cats.append("Sport > Course à pied")
    if any(w in combined for w in ["football", "foot ", "match "]):
        cats.append("Sport > Football")
    if any(w in combined for w in ["rugby"]):
        cats.append("Sport > Rugby")
    if any(w in combined for w in ["tennis"]):
        cats.append("Sport > Tennis")
    if any(w in combined for w in ["vélo", "cyclisme", "cycliste"]):
        cats.append("Sport > Cyclisme")
    if any(w in combined for w in ["natation", "nage", "piscine"]):
        cats.append("Sport > Natation")
    if any(w in combined for w in ["basket"]):
        cats.append("Sport > Basketball")
    if any(w in combined for w in ["yoga", "pilates", "méditation", "bien-être", "bien être"]):
        cats.append("Sport > Yoga & Bien-être")
    if any(w in combined for w in ["randonnée", "marche", "balade"]):
        cats.append("Sport > Randonnée")

    # Gastronomie
    if any(w in combined for w in ["gastronomie", "dégustation", "vin ", "bière", "food", "culinaire", "cuisine"]):
        cats.append("Gastronomie > Dégustation")
    if any(w in combined for w in ["marché", "brocante", "vide-grenier"]):
        cats.append("Marché & Brocante")

    # Festival
    if "festival" in combined:
        if not cats:
            cats.append("Festival")
    
    # Fête
    if any(w in combined for w in ["fête", "fete", "carnaval", "feu d'artifice", "14 juillet"]):
        cats.append("Fête")

    # Conférence
    if any(w in combined for w in ["conférence", "congrès", "colloque", "séminaire", "débat"]):
        cats.append("Conférence")

    # Atelier
    if any(w in combined for w in ["atelier", "workshop", "stage "]):
        cats.append("Atelier")

    # Enfants
    if any(w in combined for w in ["enfant", "jeune public", "famille", "kid"]):
        if not any("enfant" in c.lower() for c in cats):
            cats.append("Famille & Enfants")

    # Fallback
    if not cats:
        cats.append("Événement")

    return cats[:3]


def fetch_events_for_city(city, limit=50):
    """Fetch events from OpenAgenda/OpenDataSoft for a given city."""
    today_str = date.today().strftime("%Y-%m-%d")
    
    params = {
        "where": f'location_city="{city}" AND firstdate_begin >= "{today_str}"',
        "limit": limit,
        "offset": 0,
        "order_by": "firstdate_begin"
    }
    
    try:
        print(f"  Fetching {city}...")
        resp = requests.get(ODS_BASE, params=params, headers=HEADERS, timeout=30)
        if resp.status_code != 200:
            print(f"  ⚠ {city}: HTTP {resp.status_code}")
            return []
        
        data = resp.json()
        results = data.get("results", [])
        total = data.get("total_count", 0)
        print(f"  {city}: {len(results)} events fetched (total disponible: {total})")
        return results
    except Exception as e:
        print(f"  ❌ {city}: {e}")
        return []


def parse_openagenda_event(record, city):
    """Parse un record OpenAgenda en event MapEvent."""
    fields = record
    
    title = fields.get("title_fr") or fields.get("title") or ""
    if not title:
        return None
    
    # Description
    desc_raw = fields.get("description_fr") or fields.get("description") or ""
    description = clean_html(desc_raw)
    
    # Location
    location_name = fields.get("location_name") or ""
    location_address = fields.get("location_address") or ""
    location_city = fields.get("location_city") or city
    
    location_str = ""
    if location_name:
        location_str = location_name
    if location_address:
        location_str += f", {location_address}" if location_str else location_address
    if location_city and location_city not in location_str:
        location_str += f", {location_city}"
    
    if not location_str:
        location_str = city + ", France"
    
    # Coordinates
    coords = fields.get("location_coordinates")
    if not coords:
        return None
    
    # coords est un dict {"lat": ..., "lon": ...} ou une liste [lat, lon]
    if isinstance(coords, dict):
        lat = coords.get("lat")
        lon = coords.get("lon")
    elif isinstance(coords, list) and len(coords) >= 2:
        lat = coords[0]
        lon = coords[1]
    else:
        return None
    
    if lat is None or lon is None:
        return None
    
    try:
        lat = float(lat)
        lon = float(lon)
    except (ValueError, TypeError):
        return None
    
    # Vérifier que les coordonnées sont en France métropolitaine (approximatif)
    if not (41.0 <= lat <= 51.5 and -5.5 <= lon <= 10.0):
        return None
    
    # Dates - structure OpenAgenda
    first_begin = fields.get("firstdate_begin") or ""
    first_end = fields.get("firstdate_end") or ""
    last_begin = fields.get("lastdate_begin") or ""
    last_end = fields.get("lastdate_end") or ""
    
    event_date = None
    end_date = None
    event_time = None
    end_time = None
    
    # Date de début
    if first_begin:
        try:
            event_date = first_begin[:10]
            # Extraire l'heure si disponible
            if len(first_begin) >= 16 and "T" in first_begin:
                h = first_begin[11:16]
                if h != "00:00":
                    event_time = h
        except:
            pass
    
    # Date de fin (si différente du début)
    if last_end:
        try:
            end_date = last_end[:10]
            if len(last_end) >= 16 and "T" in last_end:
                h = last_end[11:16]
                if h != "00:00":
                    end_time = h
        except:
            pass
    elif first_end:
        try:
            end_date = first_end[:10]
        except:
            pass
    
    if not event_date:
        return None
    
    # Même date = pas de end_date
    if end_date == event_date:
        end_date = None
    
    # Vérifier que l'event est dans le futur
    try:
        check_date = end_date or event_date
        if check_date and datetime.strptime(check_date[:10], "%Y-%m-%d").date() < date.today():
            return None
    except:
        pass
    
    # Keywords pour catégorisation
    keywords = []
    kw_fr = fields.get("keywords_fr")
    if isinstance(kw_fr, str):
        keywords = [k.strip() for k in kw_fr.split(",") if k.strip()]
    elif isinstance(kw_fr, list):
        keywords = kw_fr
    
    # Source URL
    source_url = fields.get("canonicalurl") or fields.get("originagenda_url") or ""
    if not source_url:
        uid = fields.get("uid")
        slug = fields.get("slug")
        if uid and slug:
            source_url = f"https://openagenda.com/events/{uid}"
    
    if not source_url:
        return None  # Pas de source = pas de publication
    
    # Categories
    categories = categorize_event(title, description, keywords)
    
    return {
        "title": title[:200],
        "description": description,
        "date": event_date,
        "end_date": end_date if end_date != event_date else None,
        "time": event_time,
        "end_time": end_time,
        "location": location_str[:300],
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "categories": categories,
        "source_url": source_url,
        "source": f"OpenAgenda - {location_city}",
        "validation_status": "auto_validated"
    }


def send_batch(events):
    """Envoie un batch d'events à l'API MapEvent."""
    if not events:
        return 0
    
    try:
        r = requests.post(
            f"{API_BASE}/events/scraped/batch",
            json={"events": events},
            headers=HEADERS,
            timeout=60
        )
        if r.status_code in (200, 201):
            result = r.json()
            inserted = result.get("inserted", result.get("count", len(events)))
            print(f"  ✅ Batch envoyé: {inserted} events insérés")
            return inserted
        else:
            print(f"  ⚠ Batch erreur HTTP {r.status_code}: {r.text[:200]}")
            return 0
    except Exception as e:
        print(f"  ❌ Batch erreur: {e}")
        return 0


def main():
    print("=" * 60)
    print("IMPORT OPENAGENDA FRANCE - Toutes les grandes villes")
    print("=" * 60)
    
    all_events = []
    seen_titles = set()  # Dédoublonnage par titre+date+ville
    
    for city in FRENCH_CITIES:
        records = fetch_events_for_city(city, limit=50)
        time.sleep(1)  # Respecter le rate limit
        
        city_count = 0
        for record in records:
            event = parse_openagenda_event(record, city)
            if not event:
                continue
            
            # Dédoublonnage
            dedup_key = f"{event['title'].lower()[:50]}|{event['date']}|{event['latitude']:.3f}"
            if dedup_key in seen_titles:
                continue
            seen_titles.add(dedup_key)
            
            all_events.append(event)
            city_count += 1
        
        print(f"  → {city}: {city_count} events uniques parsés")
    
    print(f"\n{'=' * 60}")
    print(f"Total events à importer: {len(all_events)}")
    print(f"{'=' * 60}")
    
    if not all_events:
        print("Aucun event à importer.")
        return
    
    # Envoyer par batchs de 10
    total_inserted = 0
    batch_size = 10
    
    for i in range(0, len(all_events), batch_size):
        batch = all_events[i:i + batch_size]
        inserted = send_batch(batch)
        total_inserted += inserted
        if i + batch_size < len(all_events):
            time.sleep(1)
    
    print(f"\n{'=' * 60}")
    print(f"RÉSULTAT FINAL: {total_inserted} events importés en France")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
