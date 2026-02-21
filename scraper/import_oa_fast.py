"""
Fast OpenAgenda import with better progress tracking.
Uses internal API (no API key needed).
"""
import requests
import json
import re
import time
import sys
from datetime import date

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}
OA_API = "https://openagenda.com/api/agendas/slug/{slug}/events"


def categorize_event(title, desc, tags=None):
    text = f"{title} {desc} {' '.join(tags or [])}".lower()
    cats = []
    
    if any(w in text for w in ["techno", "house music", "dj set", "electronic", "electro", "rave", "trance"]):
        if not any(w in text for w in ["technolog", "informatique", "electroménager"]):
            cats.append("Music > Electronic")
    elif any(w in text for w in ["jazz", "swing", "blues"]):
        cats.append("Music > Jazz / Soul / Funk")
    elif any(w in text for w in ["rock", "punk", "metal"]):
        cats.append("Music > Rock / Metal")
    elif any(w in text for w in ["classique", "classical", "symphon", "opéra", "opera", "orchestre"]):
        cats.append("Music > Classique")
    elif any(w in text for w in ["rap", "hip hop", "hip-hop"]):
        cats.append("Music > Urban")
    elif any(w in text for w in ["concert", "musique", "musik", "music", "récital"]):
        cats.append("Music > Pop / Variété")
    
    if any(w in text for w in ["exposition", "exhibition", "galerie", "vernissage"]):
        cats.append("Culture > Expositions")
    elif any(w in text for w in ["théâtre", "theater", "theatre"]):
        cats.append("Arts Vivants > Théâtre")
    elif any(w in text for w in ["cinéma", "cinema", "film", "projection"]):
        cats.append("Culture > Cinéma & Projections")
    elif any(w in text for w in ["conférence", "conference", "débat", "table ronde"]):
        cats.append("Culture > Conférences & Rencontres")
    elif any(w in text for w in ["atelier", "workshop", "masterclass"]):
        cats.append("Culture > Workshops")
    elif any(w in text for w in ["humour", "stand-up"]):
        cats.append("Culture > Humour")
    elif any(w in text for w in ["visite guidée", "visite", "patrimoine"]):
        cats.append("Culture > Visites & Patrimoine")
    elif any(w in text for w in ["musée", "museum"]):
        cats.append("Culture > Expositions")
    elif any(w in text for w in ["lecture", "conte", "littéra", "poésie"]):
        cats.append("Culture > Littérature & Conte")
    
    if any(w in text for w in ["danse", "dance", "ballet"]):
        cats.append("Arts Vivants > Danse")
    if any(w in text for w in ["sport", "fitness", "marathon", "yoga", "randonnée"]):
        cats.append("Sport")
    if any(w in text for w in ["festival", "open air", "fête"]):
        cats.append("Festivals & Grandes Fêtes")
    if any(w in text for w in ["enfant", "jeune public", "famille"]):
        cats.append("Famille & Enfants")
    if any(w in text for w in ["dégustation", "brunch", "food", "cuisine", "gastro", "vin"]):
        cats.append("Food & Drinks")
    if any(w in text for w in ["marché", "brocante", "foire"]):
        cats.append("Loisirs & Animation > Défilés & Fêtes")
    if any(w in text for w in ["emploi", "recrutement", "job", "carrière", "formation professionnelle"]):
        cats.append("Business & Networking")
    
    if not cats:
        cats.append("Culture > Conférences & Rencontres")
    
    seen = set()
    unique = []
    for c in cats:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique[:3]


def send_batch(events_list, batch_size=20):
    if not events_list:
        return 0, 0
    total_created = 0
    total_skipped = 0
    total_batches = (len(events_list) + batch_size - 1) // batch_size
    
    for i in range(0, len(events_list), batch_size):
        batch_num = i // batch_size + 1
        batch = events_list[i:i+batch_size]
        try:
            r = requests.post(f"{API}/api/events/scraped/batch", json={"events": batch}, timeout=60)
            resp = r.json()
            results = resp.get("results", resp)
            created = results.get("created", 0) or results.get("inserted", 0)
            skipped = results.get("skipped", 0) + results.get("failed", 0)
            total_created += created
            total_skipped += skipped
            
            if batch_num % 20 == 0 or batch_num == total_batches:
                print(f"    Batch {batch_num}/{total_batches}: +{total_created} insérés, {total_skipped} skippés", flush=True)
        except Exception as e:
            print(f"    Batch {batch_num} erreur: {e}", flush=True)
        time.sleep(0.2)
    
    return total_created, total_skipped


def fetch_oa_agenda(slug, existing_urls, max_events=10000):
    """Fetch all upcoming events from an OpenAgenda agenda."""
    all_events = []
    offset = 0
    
    while offset < max_events:
        try:
            r = requests.get(OA_API.format(slug=slug), params={
                "size": 50,
                "from": offset,
                "relative[]": ["current", "upcoming"],
                "sort": "lastTimingWithFeatured.asc",
                "includeFields[]": [
                    "uid", "slug", "title", "description",
                    "nextTiming", "lastTiming", "keywords",
                    "location.name", "location.address", "location.city",
                    "location.postalCode", "location.countryCode",
                    "location.latitude", "location.longitude",
                ]
            }, timeout=15, headers=HEADERS)
            
            if r.status_code != 200:
                break
            
            data = r.json()
            events = data.get("events", [])
            total = data.get("total", 0)
            
            if not events:
                break
            
            for ev in events:
                title_dict = ev.get("title", {})
                title = title_dict.get("fr", "") or title_dict.get("en", "") or title_dict.get("de", "") if isinstance(title_dict, dict) else str(title_dict)
                if not title:
                    continue
                
                desc_dict = ev.get("description", {})
                desc = desc_dict.get("fr", "") or desc_dict.get("en", "") if isinstance(desc_dict, dict) else (str(desc_dict) if desc_dict else "")
                desc = re.sub(r'<[^>]+>', '', desc).strip()
                if len(desc) > 500:
                    desc = desc[:497] + "..."
                
                loc = ev.get("location", {}) or {}
                lat = loc.get("latitude")
                lng = loc.get("longitude")
                if not lat or not lng:
                    continue
                
                ev_slug = ev.get("slug", "")
                ev_uid = ev.get("uid", "")
                source_url = f"https://openagenda.com/fr/{slug}/events/{ev_slug or ev_uid}"
                
                if source_url.lower().strip().rstrip("/") in existing_urls:
                    continue
                
                timing = ev.get("nextTiming", {}) or ev.get("lastTiming", {}) or {}
                begin = timing.get("begin", "")
                end = timing.get("end", "")
                
                date_str = begin[:10] if begin else None
                time_str = begin[11:16] if begin and len(begin) > 11 else None
                end_date = end[:10] if end else None
                end_time = end[11:16] if end and len(end) > 11 else None
                
                if not date_str or date_str < TODAY:
                    continue
                
                loc_name = loc.get("name", "") or ""
                loc_addr = loc.get("address", "") or ""
                loc_city = loc.get("city", "") or ""
                location_str = loc_name
                if loc_addr:
                    location_str += f", {loc_addr}" if location_str else loc_addr
                if loc_city and loc_city not in location_str:
                    location_str += f", {loc_city}"
                
                kw = ev.get("keywords", {})
                tags = []
                if isinstance(kw, dict):
                    for lang_kw in kw.values():
                        if isinstance(lang_kw, list):
                            tags.extend(lang_kw)
                
                cats = categorize_event(title, desc, tags)
                
                all_events.append({
                    "title": title[:200],
                    "description": desc or title,
                    "date": date_str,
                    "time": time_str,
                    "end_date": end_date,
                    "end_time": end_time,
                    "location": location_str[:200] or "France",
                    "latitude": float(lat),
                    "longitude": float(lng),
                    "categories": cats,
                    "source_url": source_url,
                    "source": "OpenAgenda",
                    "validation_status": "auto_validated",
                })
            
            offset += len(events)
            if offset >= total:
                break
            
            time.sleep(0.3)
        except Exception as e:
            print(f"    Erreur page {offset}: {e}", flush=True)
            break
    
    return all_events


# ============================================================
# MAIN
# ============================================================
print("=" * 60, flush=True)
print(f"IMPORT OPENAGENDA + PARIS - {TODAY}", flush=True)
print("=" * 60, flush=True)

# Get existing URLs
print("Récupération des events existants...", flush=True)
r = requests.get(f"{API}/api/events", timeout=60)
events = r.json()
if isinstance(events, dict):
    events = events.get("events", [])
existing_urls = set()
for ev in events:
    url = ev.get("source_url", "")
    if url:
        existing_urls.add(url.lower().strip().rstrip("/"))
print(f"  {len(existing_urls)} URLs existantes", flush=True)

# All agendas to import (discovered + top candidates)
agendas = [
    # Top agendas from discovery
    ("francetravail", "Mes événements France Travail"),
    ("ile-de-france", "OpenAgenda Île-de-France"),
    ("scare", "SCARE - Cinémas"),
    ("cmf", "Confédération Musicale de France"),
    ("hello-lille", "Hello Lille"),
    ("semainepetiteenfance", "Semaine Petite Enfance"),
    ("lerif", "Le RIF"),
    ("sites-cites", "Sites & Cités"),
    ("dioceseparis", "Diocèse de Paris"),
    ("tableau-de-bord", "Théâtre Drac IDF"),
    ("agenda-temps-libres", "Agenda Temps Libres"),
    ("roissy-pays-de-france", "Roissy Pays de France"),
    ("freres-de-saint-jean-en-france", "Frères de Saint-Jean"),
    ("marseille-alive", "Live Massila"),
    ("francenum", "France Num"),
    ("rof", "Réunion des Opéras de France"),
    ("universite-paris-saclay", "Paris-Saclay"),
    ("europeenfrance", "Europe en France"),
    ("saint-marcel", "Saint-Marcel"),
    ("seineouest", "Grand Paris Seine Ouest"),
    ("acp-la-manufacture-chanson", "Manufacture Chanson"),
    ("info-jeunes-france", "Info Jeunes France"),
    ("montreuil", "Montreuil"),
    ("calendrier-musique", "Calendrier Musique"),
    ("france-belgique-calendrier", "France-Belgique"),
    ("jassclub-paris", "JASS CLUB Paris"),
    ("grand-theatre-geneve", "Grand Théâtre Genève"),
    ("ariana-ville-geneve", "Musée Ariana Genève"),
    ("chateau-de-voltaire-a-ferney", "Château de Voltaire"),
    ("orchestre-de-la-suisse-romande", "OSR"),
    ("music-line-productions-saison", "Music Line"),
    ("eurometropolis-lille-kortrijk-tournai", "Eurometropolis"),
    ("musique-sacree-a-notre-dame-de-paris", "Musique Notre-Dame"),
    ("conservatoires", "Conservatoires GPSO"),
    ("librairie-le-divan", "Librairies Le Divan"),
]

total_imported = 0

for slug, name in agendas:
    print(f"\n--- {name} ({slug}) ---", flush=True)
    
    events = fetch_oa_agenda(slug, existing_urls)
    
    if events:
        print(f"  {len(events)} events candidats", flush=True)
        created, skipped = send_batch(events)
        print(f"  Résultat: {created} insérés, {skipped} skippés", flush=True)
        total_imported += created
        for ev in events:
            existing_urls.add(ev["source_url"].lower().strip().rstrip("/"))
    else:
        print(f"  0 events", flush=True)

# Also check the OpenAgenda discovery results if available
try:
    with open("oa_active_agendas.json", "r", encoding="utf-8") as f:
        discovered = json.load(f)
    
    # Filter for agendas with >10 events that we haven't processed yet
    already_done = {slug for slug, _ in agendas}
    extra = [a for a in discovered if a["slug"] not in already_done and a.get("events", 0) > 10]
    extra.sort(key=lambda a: a.get("events", 0), reverse=True)
    
    if extra:
        print(f"\n{'=' * 60}", flush=True)
        print(f"AGENDAS SUPPLÉMENTAIRES ({len(extra)} avec >10 events)", flush=True)
        print("=" * 60, flush=True)
        
        for ag in extra[:50]:  # Max 50 additional agendas
            slug = ag["slug"]
            name = ag["title"]
            print(f"\n--- {name[:40]} ({slug}) ---", flush=True)
            
            events = fetch_oa_agenda(slug, existing_urls)
            
            if events:
                print(f"  {len(events)} events candidats", flush=True)
                created, skipped = send_batch(events)
                print(f"  Résultat: {created} insérés, {skipped} skippés", flush=True)
                total_imported += created
                for ev in events:
                    existing_urls.add(ev["source_url"].lower().strip().rstrip("/"))
            else:
                print(f"  0 events", flush=True)
except FileNotFoundError:
    print("\n  Pas de fichier oa_active_agendas.json", flush=True)
except Exception as e:
    print(f"\n  Erreur lecture discovered: {e}", flush=True)

print(f"\n{'=' * 60}", flush=True)
print(f"RÉSULTAT FINAL: {total_imported} events importés", flush=True)
print("=" * 60, flush=True)
