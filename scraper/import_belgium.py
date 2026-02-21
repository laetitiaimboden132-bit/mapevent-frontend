"""
Import des événements belges depuis UiTdatabank (89 000+ events).
Source: search.uitdatabank.be (API publique avec apiKey=test)

Max 500 events pour respecter les quotas.
Couvre: Bruxelles, Gand, Anvers, Bruges, Liège, Namur, Mons, Charleroi, Leuven
"""
import requests
import json
import re
import time
import hashlib
import sys
from datetime import datetime

sys.stdout.reconfigure(line_buffering=True)

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (https://mapevent.world)"}
TODAY = datetime.now().strftime("%Y-%m-%d")
TODAY_ISO = f"{TODAY}T00:00:00+01:00"

# Coordonnées GPS des principales villes belges
CITY_COORDS = {
    "brussel": (50.8503, 4.3517),
    "bruxelles": (50.8503, 4.3517),
    "brussels": (50.8503, 4.3517),
    "gent": (51.0543, 3.7174),
    "gand": (51.0543, 3.7174),
    "antwerpen": (51.2194, 4.4025),
    "anvers": (51.2194, 4.4025),
    "brugge": (51.2093, 3.2247),
    "bruges": (51.2093, 3.2247),
    "leuven": (50.8798, 4.7005),
    "louvain": (50.8798, 4.7005),
    "liège": (50.6292, 5.5797),
    "liege": (50.6292, 5.5797),
    "luik": (50.6292, 5.5797),
    "namur": (50.4674, 4.8720),
    "namen": (50.4674, 4.8720),
    "mons": (50.4541, 3.9523),
    "bergen": (50.4541, 3.9523),
    "charleroi": (50.4108, 4.4446),
    "mechelen": (51.0259, 4.4777),
    "hasselt": (50.9307, 5.3322),
    "kortrijk": (50.8279, 3.2649),
    "courtrai": (50.8279, 3.2649),
    "tournai": (50.6058, 3.3883),
    "doornik": (50.6058, 3.3883),
    "aalst": (50.9373, 4.0397),
    "sint-niklaas": (51.1575, 4.1439),
    "genk": (50.9649, 5.5016),
    "la louvière": (50.4774, 4.1890),
    "roeselare": (50.9444, 3.1258),
    "mouscron": (50.7436, 3.2206),
    "verviers": (50.5877, 5.8625),
    "ostende": (51.2254, 2.9170),
    "oostende": (51.2254, 2.9170),
    "wavre": (50.7177, 4.6100),
    "arlon": (49.6839, 5.8101),
    "ixelles": (50.8261, 4.3744),
    "schaerbeek": (50.8665, 4.3732),
    "anderlecht": (50.8333, 4.3097),
    "uccle": (50.7992, 4.3372),
    "etterbeek": (50.8377, 4.3896),
    "forest": (50.8106, 4.3247),
    "saint-gilles": (50.8281, 4.3464),
    "molenbeek": (50.8570, 4.3280),
    "jette": (50.8793, 4.3244),
    "woluwe-saint-lambert": (50.8417, 4.4289),
    "watermael-boitsfort": (50.7989, 4.4125),
}

def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:500]

# Cache de géocodage : clé = adresse normalisée, valeur = (lat, lon)
# Évite de re-géocoder la même adresse (beaucoup d'events au même lieu)
_geocode_cache = {}

def geocode_address(street, postal_code, city, country="BE"):
    """
    Géocode une adresse PRÉCISE via Nominatim (OpenStreetMap).
    Retourne (lat, lon) au numéro de rue près, ou None si introuvable.
    Respecte le rate limit Nominatim (1 req/sec) et cache les résultats.
    """
    if not city:
        return None, None
    
    # Clé de cache normalisée
    cache_key = f"{street}|{postal_code}|{city}".lower().strip()
    if cache_key in _geocode_cache:
        return _geocode_cache[cache_key]
    
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    
    # Stratégie: essayer du plus précis au moins précis
    queries = []
    
    # 1) Adresse complète avec numéro de rue
    if street and postal_code:
        queries.append(f"{street}, {postal_code} {city}, Belgium")
    
    # 2) Adresse sans code postal
    if street:
        queries.append(f"{street}, {city}, Belgium")
    
    # 3) Code postal + ville (précis au quartier)
    if postal_code:
        queries.append(f"{postal_code} {city}, Belgium")
    
    # 4) Ville seule (dernier recours - on n'accepte PAS ça, on skip l'event)
    # On ne met PAS la ville seule car l'user veut la précision
    
    for query in queries:
        try:
            r = requests.get(NOMINATIM_URL, params={
                "q": query,
                "format": "json",
                "limit": 1,
                "countrycodes": "be",
            }, headers={
                "User-Agent": "MapEventAI-Bot/1.0 (https://mapevent.world; mapevent777@gmail.com)"
            }, timeout=10)
            
            if r.status_code == 200 and r.json():
                result = r.json()[0]
                lat = float(result["lat"])
                lon = float(result["lon"])
                
                # Vérifier que c'est bien en Belgique
                if 49.5 <= lat <= 51.5 and 2.5 <= lon <= 6.5:
                    _geocode_cache[cache_key] = (lat, lon)
                    return lat, lon
            
            time.sleep(1.1)  # Respecter le rate limit Nominatim (1 req/sec)
        except Exception:
            time.sleep(1.1)
            continue
    
    # Pas trouvé → skip cet event (on ne veut pas d'approximation)
    _geocode_cache[cache_key] = (None, None)
    return None, None

def categorize_uit(terms, title, desc):
    """Catégorise un event UiT basé sur les terms et le contenu."""
    cats = []
    
    # Utiliser les terms de UiTdatabank
    term_labels = [t.get("label", "").lower() for t in (terms or [])]
    term_text = " ".join(term_labels)
    text = f"{title} {desc} {term_text}".lower()
    
    if any(w in text for w in ["concert", "muziek", "music", "jazz", "rock", "pop", "classical", "orkest", "koor", "chanson"]):
        if "jazz" in text: cats.append("Jazz")
        elif "rock" in text: cats.append("Rock")
        elif "klassiek" in text or "classical" in text: cats.append("Classique")
        elif "pop" in text: cats.append("Pop")
        else: cats.append("Concert")
    
    if any(w in text for w in ["theater", "theatre", "toneel", "komedie", "drama", "voorstelling"]):
        cats.append("Théâtre")
    
    if any(w in text for w in ["dans", "dance", "ballet", "choreogra"]):
        cats.append("Danse")
    
    if any(w in text for w in ["tentoonstelling", "exposition", "museum", "galerie", "gallery", "kunst", "art "]):
        cats.append("Exposition")
    
    if any(w in text for w in ["film", "cinema", "bioscoop"]):
        cats.append("Cinéma")
    
    if any(w in text for w in ["festival", "feest", "fête", "kermis", "carnaval"]):
        cats.append("Festival")
    
    if any(w in text for w in ["sport", "voetbal", "running", "wandel", "fietsen", "zwemmen", "tennis"]):
        cats.append("Sport")
    
    if any(w in text for w in ["lezing", "conferentie", "debat", "talk", "lecture", "congres"]):
        cats.append("Conférence")
    
    if any(w in text for w in ["workshop", "cursus", "les ", "atelier", "creatief"]):
        cats.append("Atelier")
    
    if any(w in text for w in ["kinderen", "kids", "familie", "gezin", "jeugd"]):
        cats.append("Famille")
    
    if any(w in text for w in ["markt", "marché", "brocante", "rommel"]):
        cats.append("Marché")
    
    if any(w in text for w in ["wandeling", "rondleiding", "gids", "visite"]):
        cats.append("Visite guidée")
    
    if not cats:
        cats.append("Événement culturel")
    
    return cats[:3]


def fetch_uit_events(start=0, limit=50):
    """Fetch events from UiTdatabank."""
    r = requests.get("https://search.uitdatabank.be/events", params={
        "apiKey": "test",
        "start": start,
        "limit": limit,
        "embed": "true",
        "availableFrom": TODAY_ISO,
        "workflowStatus": "APPROVED,READY_FOR_VALIDATION",
    }, headers=HEADERS, timeout=20)
    
    if r.status_code != 200:
        return [], 0
    
    data = r.json()
    return data.get("member", []), data.get("totalItems", 0)


def parse_uit_event(ev):
    """Parse un event UiTdatabank en format MapEvent."""
    try:
        # Titre (préférer FR, sinon NL, sinon EN)
        names = ev.get("name", {})
        title = names.get("fr") or names.get("nl") or names.get("en") or ""
        title = title.strip()
        if not title or len(title) < 3:
            return None
        
        # Dates
        start_date = ev.get("startDate", "")
        if not start_date:
            return None
        event_date = start_date[:10]
        
        if event_date < TODAY:
            return None
        
        end_date = ev.get("endDate", "")
        end_date = end_date[:10] if end_date else None
        
        # Heure
        event_time = None
        if len(start_date) >= 16 and "T" in start_date:
            t = start_date.split("T")[1][:5]
            if t != "00:00":
                event_time = t
        
        # Location
        location = ev.get("location", {})
        if not isinstance(location, dict):
            return None
        
        venue_name = ""
        loc_names = location.get("name", {})
        if isinstance(loc_names, dict):
            venue_name = loc_names.get("fr") or loc_names.get("nl") or loc_names.get("en") or ""
        
        # Adresse
        address = location.get("address", {})
        addr_data = {}
        if isinstance(address, dict):
            addr_data = address.get("fr") or address.get("nl") or address.get("en") or {}
        
        city = addr_data.get("addressLocality", "") if isinstance(addr_data, dict) else ""
        postal = addr_data.get("postalCode", "") if isinstance(addr_data, dict) else ""
        street = addr_data.get("streetAddress", "") if isinstance(addr_data, dict) else ""
        country = addr_data.get("addressCountry", "BE") if isinstance(addr_data, dict) else "BE"
        
        if country != "BE":
            return None
        
        # Coordonnées - d'abord vérifier si UiTdatabank fournit des coords
        geo = location.get("geo", {})
        lat, lon = None, None
        if isinstance(geo, dict) and geo.get("latitude") and geo.get("longitude"):
            lat = float(geo["latitude"])
            lon = float(geo["longitude"])
        
        # Sinon, géocoder l'adresse PRÉCISÉMENT via Nominatim
        if not lat or not lon:
            lat, lon = geocode_address(street, postal, city)
        
        # Pas de coordonnées précises → on SKIP (pas d'approximation)
        if not lat or not lon:
            return None
        
        # Vérifier que c'est bien en Belgique
        if not (49.5 <= lat <= 51.5 and 2.5 <= lon <= 6.5):
            return None
        
        # Location string
        parts = [p for p in [venue_name, street, f"{postal} {city}".strip()] if p]
        location_str = ", ".join(parts) if parts else "Belgique"
        
        # Source URL
        same_as = ev.get("sameAs", [])
        source_url = ""
        if isinstance(same_as, list) and same_as:
            source_url = same_as[0]
        elif isinstance(same_as, str):
            source_url = same_as
        
        if not source_url:
            event_id = ev.get("@id", "")
            if event_id:
                uid = event_id.split("/")[-1]
                source_url = f"https://www.uitinvlaanderen.be/agenda/e/-/{uid}"
            else:
                return None
        
        # Description
        descriptions = ev.get("description", {})
        desc = ""
        if isinstance(descriptions, dict):
            desc = descriptions.get("fr") or descriptions.get("nl") or descriptions.get("en") or ""
        desc = clean_html(desc)
        if not desc:
            desc = f"Événement à {city}, Belgique." if city else "Événement en Belgique."
        
        # Catégories
        terms = ev.get("terms", [])
        cats = categorize_uit(terms, title, desc)
        
        # Prix
        price_info = ev.get("priceInfo", [])
        is_free = False
        if isinstance(price_info, list):
            for p in price_info:
                if isinstance(p, dict):
                    cat = p.get("category", "").lower()
                    price = p.get("price", 0)
                    if cat == "base" and price == 0:
                        is_free = True
        
        # Organizer
        org = ev.get("organizer", {})
        org_name = ""
        if isinstance(org, dict):
            org_names = org.get("name", {})
            if isinstance(org_names, dict):
                org_name = org_names.get("fr") or org_names.get("nl") or ""
        
        return {
            "title": title,
            "description": desc,
            "date": event_date,
            "end_date": end_date,
            "time": event_time,
            "end_time": None,
            "location": location_str,
            "latitude": lat,
            "longitude": lon,
            "source_url": source_url,
            "categories": cats,
            "price": "Gratuit" if is_free else None,
            "organizer": org_name,
            "validation_status": "auto_validated",
        }
    except Exception as e:
        return None


def main():
    print("=" * 60)
    print("IMPORT ÉVÉNEMENTS BELGIQUE (UiTdatabank)")
    print(f"Date: {TODAY}")
    print("=" * 60)
    
    MAX_EVENTS = 2000
    START_OFFSET = 650  # Sauter les events déjà importés (pages 1-13)
    MAX_OFFSET = 15000
    all_events = []
    seen_urls = set()
    offset = START_OFFSET
    page_size = 50
    skipped_no_geo = 0
    skipped_other = 0
    geocoded_count = 0
    
    print(f"\nFetch des events (max {MAX_EVENTS}, offset start={START_OFFSET})...")
    print(f"  Géocodage PRÉCIS via Nominatim (au numéro de rue)")
    print(f"  Events sans adresse géocodable seront ignorés\n")
    
    while len(all_events) < MAX_EVENTS and offset < MAX_OFFSET:
        members, total = fetch_uit_events(start=offset, limit=page_size)
        
        if not members:
            print(f"  Page {offset//page_size + 1}: aucun résultat, arrêt")
            break
        
        if offset == 0:
            print(f"  Total disponible dans UiTdatabank: {total}")
        
        for ev in members:
            if len(all_events) >= MAX_EVENTS:
                break
            
            # Vérifier si l'adresse est présente avant de tenter le parsing
            loc = ev.get("location", {})
            addr = loc.get("address", {}) if isinstance(loc, dict) else {}
            addr_data = addr.get("fr") or addr.get("nl") or addr.get("en") or {} if isinstance(addr, dict) else {}
            has_street = bool(addr_data.get("streetAddress")) if isinstance(addr_data, dict) else False
            has_geo = bool(loc.get("geo", {}).get("latitude")) if isinstance(loc, dict) else False
            
            if not has_street and not has_geo:
                skipped_other += 1
                continue
            
            parsed = parse_uit_event(ev)
            if parsed and parsed["source_url"] not in seen_urls:
                seen_urls.add(parsed["source_url"])
                all_events.append(parsed)
                if not has_geo:
                    geocoded_count += 1
            elif parsed is None and has_street:
                skipped_no_geo += 1
        
        cached = len(_geocode_cache)
        print(f"  Page {offset//page_size + 1}: {len(all_events)} valides | {skipped_no_geo} sans géo | {cached} adresses en cache")
        
        if len(all_events) >= MAX_EVENTS:
            break
        
        offset += page_size
        time.sleep(0.5)  # Petite pause entre les pages API
    
    all_events = all_events[:MAX_EVENTS]
    
    # Stats par ville
    city_counts = {}
    for ev in all_events:
        city = ev["location"].split(",")[-1].strip() if "," in ev["location"] else "?"
        city_counts[city] = city_counts.get(city, 0) + 1
    
    print(f"\nRépartition par zone:")
    for city, count in sorted(city_counts.items(), key=lambda x: -x[1])[:15]:
        print(f"  {city}: {count} events")
    
    print(f"\n{'=' * 60}")
    print(f"TOTAL: {len(all_events)} events à envoyer")
    print(f"{'=' * 60}")
    
    if not all_events:
        print("Aucun event!")
        return
    
    # ENVOI
    print("\nEnvoi par batches de 10...")
    total_sent = 0
    total_failed = 0
    
    for i in range(0, len(all_events), 10):
        batch = all_events[i:i+10]
        try:
            r = requests.post(f"{API}/api/events/scraped/batch", json={"events": batch}, timeout=30)
            resp = r.json()
            results = resp.get("results", resp)
            s = results.get("created", 0) or results.get("inserted", 0)
            f_count = results.get("skipped", 0) + results.get("failed", 0)
            total_sent += s
            total_failed += f_count
            print(f"  Batch {i//10+1}/{(len(all_events)+9)//10}: +{s} insérés, {f_count} skippés")
        except Exception as e:
            print(f"  Batch {i//10+1} ERREUR: {e}")
            total_failed += len(batch)
        time.sleep(1)
    
    print(f"\n{'=' * 60}")
    print(f"RÉSULTAT FINAL BELGIQUE:")
    print(f"  Insérés: {total_sent}")
    print(f"  Skippés/Erreurs: {total_failed}")
    print(f"  Total traités: {total_sent + total_failed}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
