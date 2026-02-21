"""
Import OpenAgenda events WITHOUT API key.
Extract from __NEXT_DATA__ embedded in HTML pages.
Licence: Licence Ouverte v1.0 (compatible CC BY)

Strategy:
1. Find popular agendas via search pages
2. Extract events from each agenda's HTML
3. Handle pagination via page parameter
4. Import new events that aren't already in our DB
"""
import requests
import json
import re
import time
from datetime import date
from urllib.parse import urlparse

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (https://mapevent.world)"}


def extract_agenda_data(slug, page=1):
    """Extract agenda and events data from an OpenAgenda HTML page."""
    url = f"https://openagenda.com/fr/{slug}"
    params = {}
    if page > 1:
        params["offset"] = (page - 1) * 20  # OpenAgenda uses 20 per page by default
    
    r = requests.get(url, params=params, timeout=15, headers=HEADERS)
    if r.status_code != 200:
        return None
    
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        r.text, re.DOTALL
    )
    if not match:
        return None
    
    try:
        data = json.loads(match.group(1))
    except:
        return None
    
    pp = data.get("props", {}).get("pageProps", {})
    agenda = pp.get("agenda", {})
    events_data = pp.get("events", pp.get("initialEvents", {}))
    
    if isinstance(events_data, dict):
        total = events_data.get("total", 0)
        events = events_data.get("events", [])
    elif isinstance(events_data, list):
        total = len(events_data)
        events = events_data
    else:
        total = 0
        events = []
    
    return {
        "agenda_title": agenda.get("title", "?"),
        "agenda_uid": agenda.get("uid", "?"),
        "agenda_slug": slug,
        "total": total,
        "events": events
    }


def categorize_oa_event(title, description, tags=None):
    """Categorize an OpenAgenda event."""
    text = f"{title} {description} {' '.join(tags or [])}".lower()
    cats = []
    
    if any(w in text for w in ["techno", "electronic", "electro", "house music", "trance", "dj set", "rave"]):
        cats.append("Music > Electronic")
    elif any(w in text for w in ["concert", "musique", "musik", "music", "live", "orchest", "récital"]):
        if any(w in text for w in ["jazz", "swing"]): cats.append("Music > Jazz / Soul / Funk")
        elif any(w in text for w in ["rock", "punk", "metal"]): cats.append("Music > Rock / Metal")
        elif any(w in text for w in ["classique", "classical", "klassik", "symphon", "opéra", "opera"]): cats.append("Music > Classique")
        elif any(w in text for w in ["folk", "acoustic"]): cats.append("Music > Folk / Acoustic")
        elif any(w in text for w in ["rap", "hip hop", "hip-hop"]): cats.append("Music > Urban")
        elif any(w in text for w in ["chorale", "chœur", "choeur"]): cats.append("Music > Classique")
        else: cats.append("Music > Pop / Variété")
    
    if any(w in text for w in ["exposition", "exhibition", "galerie", "vernissage", "musée", "museum"]):
        cats.append("Culture > Expositions")
    elif any(w in text for w in ["théâtre", "theater", "theatre", "comédie", "tragédie"]):
        cats.append("Arts Vivants > Théâtre")
    elif any(w in text for w in ["cinéma", "cinema", "film", "projection", "avant-première"]):
        cats.append("Culture > Cinéma & Projections")
    elif any(w in text for w in ["conférence", "conference", "débat", "rencontre", "table ronde"]):
        cats.append("Culture > Conférences & Rencontres")
    elif any(w in text for w in ["atelier", "workshop", "stage", "masterclass"]):
        cats.append("Culture > Workshops")
    elif any(w in text for w in ["lecture", "conte", "littéra", "dédicace", "poésie", "slam"]):
        cats.append("Culture > Littérature & Conte")
    elif any(w in text for w in ["humour", "humor", "stand-up", "one-man", "one man"]):
        cats.append("Culture > Humour")
    elif any(w in text for w in ["visite guidée", "visite", "patrimoine", "guided tour"]):
        cats.append("Culture > Visites & Patrimoine")
    
    if any(w in text for w in ["danse", "dance", "ballet", "chorégraph"]):
        cats.append("Arts Vivants > Danse")
    if any(w in text for w in ["sport", "fitness", "marathon", "yoga", "course", "randonnée"]):
        cats.append("Sport")
    if any(w in text for w in ["festival", "open air"]):
        cats.append("Festivals & Grandes Fêtes")
    if any(w in text for w in ["enfant", "jeune public", "famille", "kids", "tout-petit"]):
        cats.append("Famille & Enfants")
    if any(w in text for w in ["dégustation", "brunch", "food", "cuisine", "gastro", "vin"]):
        cats.append("Food & Drinks")
    if any(w in text for w in ["marché", "brocante", "foire", "vide-grenier"]):
        cats.append("Loisirs & Animation > Défilés & Fêtes")
    if any(w in text for w in ["nature", "jardin", "botanique", "plein air"]):
        cats.append("Nature & Plein Air")
    
    if not cats:
        cats.append("Culture > Conférences & Rencontres")
    return cats[:3]


def parse_oa_events(events, agenda_slug, existing_urls):
    """Parse OpenAgenda events into our format."""
    parsed = []
    
    for ev in events:
        # Title
        title_dict = ev.get("title", {})
        if isinstance(title_dict, dict):
            title = title_dict.get("fr", "") or title_dict.get("en", "") or title_dict.get("de", "")
        else:
            title = str(title_dict)
        if not title:
            continue
        
        # Description
        desc_dict = ev.get("description", ev.get("longDescription", {}))
        if isinstance(desc_dict, dict):
            desc = desc_dict.get("fr", "") or desc_dict.get("en", "")
        else:
            desc = str(desc_dict) if desc_dict else ""
        desc = re.sub(r'<[^>]+>', '', desc).strip()
        
        # Location
        location = ev.get("location", {}) or {}
        lat = location.get("latitude")
        lng = location.get("longitude")
        loc_name = location.get("name", "")
        loc_address = location.get("address", "")
        loc_city = location.get("city", "")
        loc_country = location.get("countryCode", "")
        
        if not lat or not lng:
            continue
        
        # Source URL
        slug_ev = ev.get("slug", "")
        uid_ev = ev.get("uid", "")
        source_url = f"https://openagenda.com/fr/{agenda_slug}/events/{slug_ev or uid_ev}"
        
        if source_url.lower().strip().rstrip("/") in existing_urls:
            continue
        
        # Timings
        first_timing = ev.get("firstTiming", {}) or {}
        last_timing = ev.get("lastTiming", {}) or {}
        
        begin = first_timing.get("begin", "")
        end = last_timing.get("end", first_timing.get("end", ""))
        
        date_str = begin[:10] if begin else None
        time_str = begin[11:16] if begin and len(begin) > 11 else None
        end_date = end[:10] if end else None
        end_time = end[11:16] if end and len(end) > 11 else None
        
        if not date_str:
            continue
        # Skip past events
        if date_str < TODAY:
            continue
        
        # Tags/keywords for categorization
        tags = []
        for kw in ev.get("keywords", {}).get("fr", []) if isinstance(ev.get("keywords"), dict) else []:
            tags.append(kw)
        
        cats = categorize_oa_event(title, desc, tags)
        
        if len(desc) > 500:
            desc = desc[:497] + "..."
        
        location_str = f"{loc_name}, {loc_address}" if loc_address else loc_name
        if loc_city and loc_city not in location_str:
            location_str += f", {loc_city}"
        
        parsed.append({
            "title": title[:200],
            "description": desc or title,
            "date": date_str,
            "time": time_str,
            "end_date": end_date,
            "end_time": end_time,
            "location": location_str or "Unknown",
            "latitude": float(lat),
            "longitude": float(lng),
            "categories": cats,
            "source_url": source_url,
            "source": "OpenAgenda",
            "validation_status": "auto_validated",
            "country": loc_country or ""
        })
    
    return parsed


def send_batch(events, batch_size=10):
    if not events: return 0, 0
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
        except Exception as e:
            print(f"  Batch ERREUR: {e}")
        time.sleep(0.3)
    return total_created, total_skipped


def discover_agendas():
    """Find popular agendas by browsing OpenAgenda search pages."""
    print("Découverte des agendas populaires...")
    
    # Known agendas from various sources
    known_agendas = [
        # Genève (from opendata.swiss)
        "grand-theatre-geneve",
        "victoria-hall",
        "bm-geneve",
        "bibliotheque-geneve",
        "ariana-ville-geneve",
        # France - major cities
        "ville-de-paris",
        "quefaireaparis",
        "mairie-de-lyon",
        "mairie-de-marseille",
        "ville-de-bordeaux",
        "ville-de-toulouse",
        "ville-de-nantes",
        "ville-de-lille",
        "ville-de-strasbourg",
        "ville-de-rennes",
        "ville-de-montpellier",
        "ville-de-nice",
        "metropole-de-lyon",
        # Belgium
        "ville-de-bruxelles",
        "visit-brussels",
        "bruxelles",
        # Switzerland
        "ville-de-geneve",
        "ville-de-lausanne",
        "ville-de-bern",
        "ville-de-zurich",
        "ville-de-fribourg",
        # Cultural venues
        "philharmonie-de-paris",
        "centre-pompidou",
        "musee-du-louvre",
        "cite-des-sciences",
        "bnf",
        "chatelet",
        "opera-de-paris",
        "theatre-de-la-ville",
        "la-villette",
        "gaite-lyrique",
        "mac-lyon",
        "mucem",
        "opera-de-lyon",
    ]
    
    # Test each agenda
    valid_agendas = []
    for slug in known_agendas:
        try:
            data = extract_agenda_data(slug)
            if data and data["total"] > 0:
                valid_agendas.append({
                    "slug": slug,
                    "title": data["agenda_title"],
                    "uid": data["agenda_uid"],
                    "total": data["total"]
                })
                print(f"  ✓ {slug}: {data['agenda_title']} ({data['total']} events)")
            else:
                pass  # Silently skip 404s
            time.sleep(1)  # Rate limit - be polite
        except Exception as e:
            pass
    
    return valid_agendas


def fetch_all_events_from_agenda(slug, existing_urls, max_pages=50):
    """Fetch all events from an agenda, handling pagination."""
    all_events = []
    page = 1
    
    while page <= max_pages:
        data = extract_agenda_data(slug, page=page)
        if not data:
            break
        
        events = data["events"]
        if not events:
            break
        
        parsed = parse_oa_events(events, slug, existing_urls)
        all_events.extend(parsed)
        
        # Check if we've got all
        if len(events) < 15:  # Less than a full page = last page
            break
        
        page += 1
        time.sleep(1.5)  # Rate limit
    
    return all_events


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("OPENAGENDA - Import sans clé API")
    print(f"Date: {TODAY}")
    print("=" * 60)
    
    # Get existing URLs
    print("\nRécupération des events existants...")
    r = requests.get(f"{API}/api/events", timeout=60)
    events = r.json()
    if isinstance(events, dict):
        events = events.get("events", [])
    existing_urls = set()
    for ev in events:
        url = ev.get("source_url", "")
        if url:
            existing_urls.add(url.lower().strip().rstrip("/"))
    print(f"  {len(existing_urls)} URLs existantes")
    
    # Discover agendas
    agendas = discover_agendas()
    print(f"\n  {len(agendas)} agendas valides trouvés")
    
    # Fetch events from each agenda
    total_new = 0
    total_imported = 0
    
    for ag in agendas:
        slug = ag["slug"]
        title = ag["title"]
        ag_total = ag["total"]
        
        print(f"\n--- {title} ({ag_total} events) ---")
        events = fetch_all_events_from_agenda(slug, existing_urls)
        
        if events:
            print(f"  {len(events)} nouveaux events")
            created, skipped = send_batch(events)
            print(f"  Insérés: {created}, Skippés: {skipped}")
            total_imported += created
            
            # Add new URLs to existing set
            for ev in events:
                existing_urls.add(ev["source_url"].lower().strip().rstrip("/"))
        else:
            print(f"  0 nouveaux events")
        
        total_new += len(events)
    
    print(f"\n{'=' * 60}")
    print(f"RÉSULTAT OPENAGENDA:")
    print(f"  Agendas explorés: {len(agendas)}")
    print(f"  Events candidats: {total_new}")
    print(f"  Events importés: {total_imported}")
    print(f"{'=' * 60}")
