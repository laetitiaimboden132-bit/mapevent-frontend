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
import os
from datetime import date
from urllib.parse import urlparse
from pathlib import Path

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (https://mapevent.world)"}
BLACKLIST_PATH = Path("frontend/scraper/opendata_event_blacklist.json")
SOURCE_REGISTRY_PATH = Path("frontend/scraper/import_source_registry.json")
LEGAL_SOURCE_HOSTS = {"openagenda.com", "www.openagenda.com"}
MIN_RESCAN_DAYS = int(os.getenv("MIN_SOURCE_RESCAN_DAYS", "90"))
FORCE_RESCAN = os.getenv("FORCE_RESCAN", "0") == "1"

# Sous-sources OpenAgenda explicitement exclues (catalogues d'hebergements / non-evenementiels).
BLOCKED_AGENDA_SLUGS = {
    "centre-de-vacances-loisirs-provence-mediterranee-baratier",
    "catalogue-departemental-des-structures-daccueil-et-dhebergement-hautes-alpes",
    "la-part-citoyenne",
    "ville-de-roques",
}

RECRUITMENT_EXCLUDE_RE = re.compile(
    r"(recrut|emploi|poste\b|cdi\b|cdd\b|offre d[' ]emploi|job dating|insertion professionnelle)",
    re.IGNORECASE
)
RENTAL_EXCLUDE_RE = re.compile(
    r"(\bà\s+louer\b|\ba\s+louer\b|location saisonni[èe]re|appartement|immobilier|annonce immobili[èe]re)",
    re.IGNORECASE
)
ACCOMMODATION_TERMS_RE = re.compile(
    r"(\bg[iî]te\b|auberge|h[ôo]tel|chalet|r[ée]sidence|centre de vacances|h[ée]bergement)",
    re.IGNORECASE
)
ACCOMMODATION_CONTEXT_RE = re.compile(
    r"(catalogue|capacit[ée]|nuit[ée]e?s?|couchage|pension|dortoir|camping|r[ée]servation|se loger)",
    re.IGNORECASE
)


def is_non_event_content(title, description):
    text = f"{title} {description}".lower()
    if RECRUITMENT_EXCLUDE_RE.search(text):
        return True
    if RENTAL_EXCLUDE_RE.search(text):
        return True
    # Les mots comme "chalet" / "résidence" peuvent aussi être culturels.
    # On exclut seulement s'il y a un contexte d'hébergement explicite.
    if ACCOMMODATION_TERMS_RE.search(text) and ACCOMMODATION_CONTEXT_RE.search(text):
        return True
    return False


def normalize_url(url):
    if not url:
        return ""
    return str(url).strip().lower().rstrip("/")


def is_legal_source_url(url):
    """
    Sources légales et sûres uniquement:
    - schéma HTTPS
    - host whitelisté
    """
    try:
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower()
        return parsed.scheme == "https" and host in LEGAL_SOURCE_HOSTS
    except Exception:
        return False


def load_blacklist_data():
    blocked_urls = set()
    blocked_slugs = set(BLOCKED_AGENDA_SLUGS)
    if not BLACKLIST_PATH.exists():
        return blocked_urls, blocked_slugs
    try:
        data = json.loads(BLACKLIST_PATH.read_text(encoding="utf-8"))
        for it in data.get("items", []):
            u = normalize_url(it.get("source_url"))
            if u:
                blocked_urls.add(u)
                if "openagenda.com/" in u:
                    slug = u.split("openagenda.com/", 1)[1].split("/events", 1)[0]
                    if slug:
                        blocked_slugs.add(slug)
    except Exception:
        pass
    return blocked_urls, blocked_slugs


def load_source_registry():
    if not SOURCE_REGISTRY_PATH.exists():
        return {"agendas": {}}
    try:
        return json.loads(SOURCE_REGISTRY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"agendas": {}}


def save_source_registry(registry):
    SOURCE_REGISTRY_PATH.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")


def days_since(date_str):
    try:
        y, m, d = [int(x) for x in str(date_str).split("-")]
        old = date(y, m, d)
        return (date.today() - old).days
    except Exception:
        return 9999


def should_scan_slug(slug, registry):
    if FORCE_RESCAN:
        return True
    last_scan = (registry.get("agendas", {}) or {}).get(slug, {}).get("last_scan_date")
    if not last_scan:
        return True
    return days_since(last_scan) >= MIN_RESCAN_DAYS


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
    
    electro_music_signal = any(
        w in text for w in ["dj set", "soirée", "soiree", "concert", "festival", "club", "music", "musique", "live", "rave"]
    )
    techno_context = any(
        w in text for w in ["atelier numérique", "electronique", "technologie", "robotique", "arduino", "coding", "programmation"]
    )
    if any(w in text for w in ["techno", "electronic", "electro", "house music", "trance", "dj set", "rave"]) and electro_music_signal and not techno_context:
        cats.append("Music > Electronic")
    elif any(w in text for w in ["piano", "guitare", "guitar", "violon", "violoncelle", "flûte", "flute", "saxophone", "trompette", "percussion", "harpe", "instrumental"]):
        if not any(w in text for w in ["jazz", "rock", "metal", "rap", "hip hop", "hip-hop", "classique", "classical", "folk", "pop"]):
            cats.append("Music")
    elif any(w in text for w in ["concert", "musique", "musik", "music", "live", "orchest", "récital"]):
        if any(w in text for w in ["jazz", "swing"]): cats.append("Music > Jazz / Soul / Funk")
        elif any(w in text for w in ["rock", "punk", "metal"]): cats.append("Music > Rock / Metal")
        elif any(w in text for w in ["classique", "classical", "klassik", "symphon", "opéra", "opera"]): cats.append("Music > Classique")
        elif any(w in text for w in ["folk", "acoustic"]): cats.append("Music > Folk / Acoustic")
        elif any(w in text for w in ["rap", "hip hop", "hip-hop"]): cats.append("Music > Urban")
        elif any(w in text for w in ["chorale", "chœur", "choeur"]): cats.append("Music > Classique")
        else: cats.append("Music > Pop / Variété")
    
    # Priorité au théâtre/récit scénique avant "musée/exposition"
    if any(w in text for w in ["théâtre", "theater", "theatre", "comédie", "tragédie", "spectacle", "mise en scène", "récit", "temoignage", "témoignage", "compagnie"]):
        cats.append("Arts Vivants > Théâtre")
    elif any(w in text for w in ["exposition", "exhibition", "galerie", "vernissage", "musée", "museum"]):
        cats.append("Culture > Expositions")
    elif any(w in text for w in ["cinéma", "cinema", "film", "projection", "avant-première"]):
        cats.append("Culture > Cinéma & Projections")
    elif any(w in text for w in ["conférence", "conference", "débat", "rencontre", "table ronde"]):
        cats.append("Culture > Conférences & Rencontres")
    elif any(w in text for w in ["atelier", "workshop", "stage", "masterclass"]):
        cats.append("Culture > Ateliers")
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


def parse_oa_events(events, agenda_slug, existing_urls, blocked_urls):
    """Parse OpenAgenda events into our format."""
    if agenda_slug in BLOCKED_AGENDA_SLUGS:
        return []

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

        # Filtre qualite: rejeter les contenus non-evenementiels.
        if is_non_event_content(title, desc):
            continue
        
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
        
        normalized_source = normalize_url(source_url)
        if normalized_source in existing_urls:
            continue
        # Liste noire globale: ne jamais reposer ces events.
        if normalized_source in blocked_urls:
            continue
        # Sources légales seulement
        if not is_legal_source_url(source_url):
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


def fetch_all_events_from_agenda(slug, existing_urls, blocked_urls, max_pages=50):
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
        
        parsed = parse_oa_events(events, slug, existing_urls, blocked_urls)
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
            existing_urls.add(normalize_url(url))
    print(f"  {len(existing_urls)} URLs existantes")

    # Charger blacklist permanente
    blocked_urls, blocked_slugs = load_blacklist_data()
    print(f"  {len(blocked_urls)} URLs blacklistées")
    print(f"  {len(blocked_slugs)} agendas blacklistés")

    # Charger registre de sources déjà scannées récemment
    source_registry = load_source_registry()
    
    # Discover agendas
    agendas = discover_agendas()
    print(f"\n  {len(agendas)} agendas valides trouvés (avant filtres)")
    agendas = [a for a in agendas if a["slug"] not in blocked_slugs and should_scan_slug(a["slug"], source_registry)]
    print(f"  {len(agendas)} agendas retenus (légaux + nouveaux)")
    
    # Fetch events from each agenda
    total_new = 0
    total_imported = 0
    
    for ag in agendas:
        slug = ag["slug"]
        title = ag["title"]
        ag_total = ag["total"]
        
        print(f"\n--- {title} ({ag_total} events) ---")
        events = fetch_all_events_from_agenda(slug, existing_urls, blocked_urls)
        
        if events:
            print(f"  {len(events)} nouveaux events")
            created, skipped = send_batch(events)
            print(f"  Insérés: {created}, Skippés: {skipped}")
            total_imported += created
            
            # Add new URLs to existing set
            for ev in events:
                existing_urls.add(normalize_url(ev["source_url"]))
        else:
            print(f"  0 nouveaux events")

        # Marquer la source comme scannée aujourd'hui pour éviter retri immédiat
        source_registry.setdefault("agendas", {}).setdefault(slug, {})
        source_registry["agendas"][slug]["last_scan_date"] = TODAY
        source_registry["agendas"][slug]["title"] = title
        save_source_registry(source_registry)
        
        total_new += len(events)
    
    print(f"\n{'=' * 60}")
    print(f"RÉSULTAT OPENAGENDA:")
    print(f"  Agendas explorés: {len(agendas)}")
    print(f"  Events candidats: {total_new}")
    print(f"  Events importés: {total_imported}")
    print(f"{'=' * 60}")
