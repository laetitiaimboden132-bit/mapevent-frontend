"""
MASSIVE OpenAgenda import from all 996 discovered active agendas.
Processes them in order of event count (biggest first).
Uses internal API (no API key needed).
"""
import requests
import json
import re
import time
from datetime import date

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}
OA_API = "https://openagenda.com/api/agendas/slug/{slug}/events"


def categorize(title, desc, tags=None):
    text = f"{title} {desc} {' '.join(tags or [])}".lower()
    cats = []
    
    # Music
    if any(w in text for w in ["techno", "house music", "dj set", "electronic", "electro", "rave", "trance"]):
        if not any(w in text for w in ["technolog", "informatique", "electroménager"]):
            cats.append("Music > Electronic")
    elif any(w in text for w in ["jazz", "swing", "blues", "fado"]): cats.append("Music > Jazz / Soul / Funk")
    elif any(w in text for w in ["rock", "punk", "metal"]): cats.append("Music > Rock / Metal")
    elif any(w in text for w in ["classique", "classical", "symphon", "opéra", "opera", "orchestre"]): cats.append("Music > Classique")
    elif any(w in text for w in ["rap", "hip hop", "hip-hop"]): cats.append("Music > Urban")
    elif any(w in text for w in ["folk", "acoustic", "acoustique"]): cats.append("Music > Folk / Acoustic")
    elif any(w in text for w in ["concert", "musique", "musik", "music", "récital", "chorale", "choeur"]): cats.append("Music > Pop / Variété")
    
    # Culture
    if any(w in text for w in ["exposition", "exhibition", "galerie", "vernissage"]): cats.append("Culture > Expositions")
    elif any(w in text for w in ["théâtre", "theater", "theatre", "comédie"]): cats.append("Arts Vivants > Théâtre")
    elif any(w in text for w in ["cinéma", "cinema", "film", "projection"]): cats.append("Culture > Cinéma & Projections")
    elif any(w in text for w in ["conférence", "conference", "débat", "table ronde", "rencontre"]): cats.append("Culture > Conférences & Rencontres")
    elif any(w in text for w in ["atelier", "workshop", "masterclass"]): cats.append("Culture > Workshops")
    elif any(w in text for w in ["humour", "stand-up", "one-man"]): cats.append("Culture > Humour")
    elif any(w in text for w in ["visite guidée", "visite", "patrimoine"]): cats.append("Culture > Visites & Patrimoine")
    elif any(w in text for w in ["musée", "museum"]): cats.append("Culture > Expositions")
    elif any(w in text for w in ["lecture", "conte", "littéra", "poésie", "dédicace"]): cats.append("Culture > Littérature & Conte")
    
    # Other categories
    if any(w in text for w in ["danse", "dance", "ballet", "chorégraph"]): cats.append("Arts Vivants > Danse")
    if any(w in text for w in ["sport", "fitness", "marathon", "yoga", "randonnée", "course"]): cats.append("Sport")
    if any(w in text for w in ["festival", "open air"]): cats.append("Festivals & Grandes Fêtes")
    if any(w in text for w in ["enfant", "jeune public", "famille", "tout-petit"]): cats.append("Famille & Enfants")
    if any(w in text for w in ["dégustation", "brunch", "food", "cuisine", "gastro", "vin"]): cats.append("Food & Drinks")
    if any(w in text for w in ["marché", "brocante", "foire", "vide-grenier"]): cats.append("Loisirs & Animation > Défilés & Fêtes")
    if any(w in text for w in ["nature", "jardin", "botanique", "plein air"]): cats.append("Nature & Plein Air")
    if any(w in text for w in ["emploi", "recrutement", "job", "formation professionnelle"]): cats.append("Business & Networking")
    
    if not cats: cats.append("Culture > Conférences & Rencontres")
    seen = set()
    return [c for c in cats if not (c in seen or seen.add(c))][:3]


def send_batch(events_list, batch_size=20):
    if not events_list: return 0, 0
    total_c, total_s = 0, 0
    total_batches = (len(events_list) + batch_size - 1) // batch_size
    for i in range(0, len(events_list), batch_size):
        batch = events_list[i:i+batch_size]
        try:
            r = requests.post(f"{API}/api/events/scraped/batch", json={"events": batch}, timeout=60)
            resp = r.json()
            res = resp.get("results", resp)
            total_c += res.get("created", 0) or res.get("inserted", 0)
            total_s += res.get("skipped", 0) + res.get("failed", 0)
        except Exception as e:
            pass
        time.sleep(0.15)
    return total_c, total_s


def fetch_agenda(slug, existing_urls, max_events=2000):
    """Fetch all upcoming events from an agenda."""
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
                td = ev.get("title", {})
                title = (td.get("fr", "") or td.get("en", "") or td.get("de", "")) if isinstance(td, dict) else str(td)
                if not title: continue
                
                dd = ev.get("description", {})
                desc = (dd.get("fr", "") or dd.get("en", "")) if isinstance(dd, dict) else (str(dd) if dd else "")
                desc = re.sub(r'<[^>]+>', '', desc).strip()
                if len(desc) > 500: desc = desc[:497] + "..."
                
                loc = ev.get("location", {}) or {}
                lat, lng = loc.get("latitude"), loc.get("longitude")
                if not lat or not lng: continue
                
                ev_slug = ev.get("slug", "")
                ev_uid = ev.get("uid", "")
                source_url = f"https://openagenda.com/fr/{slug}/events/{ev_slug or ev_uid}"
                
                if source_url.lower().strip().rstrip("/") in existing_urls:
                    continue
                
                timing = ev.get("nextTiming", {}) or ev.get("lastTiming", {}) or {}
                begin = timing.get("begin", "")
                end = timing.get("end", "")
                
                date_str = begin[:10] if begin else None
                if not date_str or date_str < TODAY: continue
                time_str = begin[11:16] if begin and len(begin) > 11 else None
                end_date = end[:10] if end else None
                end_time = end[11:16] if end and len(end) > 11 else None
                
                loc_str = loc.get("name", "") or ""
                if loc.get("address"): loc_str += f", {loc['address']}" if loc_str else loc["address"]
                if loc.get("city") and loc["city"] not in loc_str: loc_str += f", {loc['city']}"
                
                kw = ev.get("keywords", {})
                tags = []
                if isinstance(kw, dict):
                    for v in kw.values():
                        if isinstance(v, list): tags.extend(v)
                
                cats = categorize(title, desc, tags)
                
                all_events.append({
                    "title": title[:200],
                    "description": desc or title,
                    "date": date_str,
                    "time": time_str,
                    "end_date": end_date,
                    "end_time": end_time,
                    "location": loc_str[:200] or "France",
                    "latitude": float(lat),
                    "longitude": float(lng),
                    "categories": cats,
                    "source_url": source_url,
                    "source": "OpenAgenda",
                    "validation_status": "auto_validated",
                })
            
            offset += len(events)
            if offset >= total: break
            time.sleep(0.3)
        except:
            break
    
    return all_events


# ============================================================
# MAIN
# ============================================================
print("=" * 60, flush=True)
print(f"IMPORT MASSIF OPENAGENDA - {TODAY}", flush=True)
print("=" * 60, flush=True)

# Get existing
print("Récupération events existants...", flush=True)
r = requests.get(f"{API}/api/events", timeout=60)
evts = r.json()
if isinstance(evts, dict): evts = evts.get("events", [])
existing_urls = set()
for ev in evts:
    u = ev.get("source_url", "")
    if u: existing_urls.add(u.lower().strip().rstrip("/"))
print(f"  {len(existing_urls)} URLs existantes", flush=True)

# Load discovered agendas
with open("oa_active_agendas.json", "r", encoding="utf-8") as f:
    agendas = json.load(f)

# Sort by event count descending
agendas.sort(key=lambda a: a.get("events", a.get("real_upcoming", 0)), reverse=True)

print(f"  {len(agendas)} agendas à traiter", flush=True)

total_imported = 0
total_processed = 0
total_new_events = 0

for ag in agendas:
    slug = ag.get("slug", "")
    name = ag.get("title", slug)[:45]
    expected = ag.get("events", ag.get("real_upcoming", 0))
    
    total_processed += 1
    
    events = fetch_agenda(slug, existing_urls)
    
    if events:
        total_new_events += len(events)
        created, skipped = send_batch(events)
        
        if created > 0:
            total_imported += created
            print(f"  [{total_processed}/{len(agendas)}] ✓ {name}: +{created} new ({expected} total)", flush=True)
        
        # Update existing URLs
        for ev in events:
            existing_urls.add(ev["source_url"].lower().strip().rstrip("/"))
    
    # Progress report every 50
    if total_processed % 50 == 0:
        print(f"  --- {total_processed}/{len(agendas)} traités, {total_imported} importés, {total_new_events} candidats ---", flush=True)
    
    time.sleep(0.2)

print(f"\n{'=' * 60}", flush=True)
print(f"RÉSULTAT MASSIF OPENAGENDA:", flush=True)
print(f"  Agendas traités: {total_processed}/{len(agendas)}", flush=True)
print(f"  Events candidats: {total_new_events}", flush=True)
print(f"  Events importés: {total_imported}", flush=True)
print(f"{'=' * 60}", flush=True)
