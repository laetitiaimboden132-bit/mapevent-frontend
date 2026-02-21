"""
Dernière recherche d'events electro:
1. OSM Calendar (autorisé dans AGENTS.md)
2. OpenAgenda - chercher avec d'autres params
3. Kulturdaten.berlin - events musique avec tags spécifiques
4. Récapitulatif final
"""
import requests
import time
import json
import re

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

# ============================================================
# 1. OSM Calendar (community calendar, open data)
# ============================================================
def search_osm_calendar():
    """Search OpenStreetMap calendar for events."""
    print("=" * 60)
    print("OSM CALENDAR")
    print("=" * 60)
    
    url = "https://osmcal.org/api/v2/events/"
    try:
        r = requests.get(url, timeout=15, headers={"Accept": "application/json"})
        if r.status_code == 200:
            events = r.json()
            print(f"  Total events OSM: {len(events)}")
            # These are OpenStreetMap mapping events, not music events
            for ev in events[:5]:
                name = ev.get("name", "?")
                print(f"    - {name}")
            print("  >> Ce sont des events OSM (cartographie), pas de musique")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 2. OpenAgenda - approach par agendas populaires
# ============================================================
def search_openagenda_popular():
    """Search OpenAgenda popular music agendas."""
    print("\n" + "=" * 60)
    print("OPENAGENDA - Top agendas avec events")  
    print("=" * 60)
    
    OA_KEY = "0e3b442455894aa09e7b8acb7d43c69c"
    
    # Get popular agendas (no geo filter)
    try:
        r = requests.get("https://api.openagenda.com/v2/agendas", params={
            "key": OA_KEY,
            "size": 100,
            "sort": "eventsUpcomingCount.desc"  # Most active first
        }, timeout=20)
        data = r.json()
        agendas = data.get("agendas", [])
        total = data.get("total", 0)
        print(f"  Total agendas: {total}, fetched: {len(agendas)}")
        
        music_agendas = []
        for ag in agendas:
            title = (ag.get("title") or "").lower()
            desc = (ag.get("description") or "").lower()
            text = f"{title} {desc}"
            upcoming = ag.get("eventsUpcomingCount", 0) or 0
            
            if any(w in text for w in ["musique", "music", "concert", "club", "electro", 
                                       "techno", "dj", "festival", "soirée", "nightlife",
                                       "party", "dance", "salle", "scène"]):
                if upcoming > 0:
                    music_agendas.append(ag)
        
        print(f"  Agendas musique avec events upcoming: {len(music_agendas)}")
        for ag in music_agendas[:15]:
            name = ag.get("title", "?")
            uid = ag.get("uid")
            upcoming = ag.get("eventsUpcomingCount", 0)
            print(f"    [{upcoming} upcoming] {name} (uid={uid})")
        
        return music_agendas
    except Exception as e:
        print(f"  ERREUR: {e}")
        return []


def fetch_electro_from_agenda(agenda_uid, agenda_title):
    """Fetch electro events from a specific agenda."""
    OA_KEY = "0e3b442455894aa09e7b8acb7d43c69c"
    
    electro_kw = ["techno", "electro", "house", "trance", "dj set", "dj night",
                  "rave", "bass", "dubstep", "electronic", "club night", "after party",
                  "minimal", "acid", "deep house", "hardstyle", "jungle", "dnb",
                  "drum and bass", "neurofunk"]
    
    try:
        r = requests.get(f"https://api.openagenda.com/v2/agendas/{agenda_uid}/events", params={
            "key": OA_KEY,
            "relative[]": "upcoming",
            "size": 300,
        }, timeout=20)
        data = r.json()
        events = data.get("events", [])
        total = data.get("total", 0)
        
        electro = []
        for ev in events:
            title = (ev.get("title", {}).get("fr", "") or ev.get("title", {}).get("en", "") or "").lower()
            desc = (ev.get("description", {}).get("fr", "") or ev.get("description", {}).get("en", "") or "").lower()
            text = f"{title} {desc}"
            
            if any(kw in text for kw in electro_kw):
                electro.append(ev)
        
        return electro, total
    except Exception as e:
        return [], 0


# ============================================================
# 3. Kulturdaten.berlin - MUSIC category events
# ============================================================
def search_berlin_music_detailed():
    """Search Berlin kulturdaten for specific music/club events."""
    print("\n" + "=" * 60)
    print("BERLIN - kulturdaten.berlin MUSIC category")
    print("=" * 60)
    
    # Try the attractions endpoint for venues
    try:
        r = requests.get("https://www.kulturdaten.berlin/api/v1/attractions", params={
            "page[size]": 20,
            "filter[type]": "MUSIC"
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            results = data.get("data", [])
            print(f"  Music attractions: {len(results)}")
            for att in results[:5]:
                attrs = att.get("attributes", {})
                title = attrs.get("title", "?")
                print(f"    - {title}")
        else:
            print(f"  Attractions: HTTP {r.status_code}")
    except Exception as e:
        print(f"  Attractions: ERREUR {e}")
    
    # Try tags endpoint
    try:
        r = requests.get("https://www.kulturdaten.berlin/api/v1/tags", timeout=15)
        if r.status_code == 200:
            data = r.json()
            tags = data.get("data", [])
            music_tags = [t for t in tags if any(w in (t.get("attributes", {}).get("title", "") or "").lower() 
                         for w in ["music", "club", "electro", "techno", "dj", "dance", "concert"])]
            print(f"  Music-related tags: {len(music_tags)}")
            for t in music_tags:
                print(f"    - {t.get('attributes', {}).get('title', '?')} (id={t.get('id')})")
        else:
            print(f"  Tags: HTTP {r.status_code}")
    except Exception as e:
        print(f"  Tags: ERREUR {e}")


# ============================================================
# 4. RECAP: Combien d'events electro on a maintenant
# ============================================================
def count_current_electro():
    """Count current electro events on the map."""
    print("\n" + "=" * 60)
    print("ÉTAT ACTUEL - Events electro sur la carte")
    print("=" * 60)
    
    r = requests.get(f"{API}/api/events", timeout=60)
    events = r.json()
    if isinstance(events, dict):
        events = events.get("events", [])
    
    print(f"Total events: {len(events)}")
    
    # Count by category match
    electro_cats = {}
    electro_events = []
    
    for ev in events:
        cats = ev.get("categories", [])
        if not isinstance(cats, list):
            continue
        
        for c in cats:
            cl = c.lower()
            if any(w in cl for w in ["electronic", "techno", "house", "trance", 
                                      "drum & bass", "bass music", "hard music",
                                      "chill / ambient", "électronique", "electro"]):
                electro_cats[c] = electro_cats.get(c, 0) + 1
                electro_events.append(ev)
                break
    
    print(f"\nEvents avec catégorie electro: {len(electro_events)}")
    print(f"\nCatégories electro:")
    for c, count in sorted(electro_cats.items(), key=lambda x: -x[1]):
        print(f"  {c}: {count}")
    
    # Par source
    from urllib.parse import urlparse
    source_counts = {}
    for ev in electro_events:
        url = ev.get("source_url", "") or ""
        try:
            domain = urlparse(url).netloc
        except:
            domain = "?"
        source_counts[domain] = source_counts.get(domain, 0) + 1
    
    print(f"\nPar source:")
    for s, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"  {s}: {count}")


if __name__ == "__main__":
    # 1. OSM Calendar
    search_osm_calendar()
    
    # 2. OpenAgenda popular agendas
    music_agendas = search_openagenda_popular()
    
    # 3. Fetch electro events from promising agendas
    if music_agendas:
        print("\n--- Fetch events electro des agendas musique ---")
        total_electro_found = 0
        for ag in music_agendas:
            uid = ag.get("uid")
            title = ag.get("title", "?")
            upcoming = ag.get("eventsUpcomingCount", 0) or 0
            if upcoming >= 10:  # Only check agendas with enough events
                electro_evts, total = fetch_electro_from_agenda(uid, title)
                if electro_evts:
                    print(f"  [{title[:40]}] {total} upcoming, {len(electro_evts)} electro")
                    for ev in electro_evts[:3]:
                        t = ev.get("title", {}).get("fr", "") or ev.get("title", {}).get("en", "?")
                        print(f"    - {t[:60]}")
                    total_electro_found += len(electro_evts)
                time.sleep(0.5)
        print(f"\n  Total events electro OpenAgenda: {total_electro_found}")
    
    # 4. Berlin
    search_berlin_music_detailed()
    
    # 5. Current state
    count_current_electro()
