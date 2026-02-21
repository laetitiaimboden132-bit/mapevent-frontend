"""
Recherche d'events electro sur les sources open data.
Phase 1: Explorer ce qui est disponible.
"""
import requests
import time
import json

# ============================================================
# SOURCE 1: OpenAgenda - Recherche par mots-clés electro
# Licence Ouverte v1.0 (compatible CC BY)
# ============================================================
OA_KEY = "0e3b442455894aa09e7b8acb7d43c69c"
OA_BASE = "https://api.openagenda.com/v2"

def search_openagenda_electro():
    """Chercher des events electro sur OpenAgenda avec des mots-clés."""
    keywords = ["techno", "electronic music", "house music", "DJ set", "rave", 
                "drum and bass", "trance party", "electro", "clubbing"]
    
    all_events = []
    seen_uids = set()
    
    for kw in keywords:
        print(f"\n  Recherche OpenAgenda: '{kw}'...")
        try:
            r = requests.get(f"{OA_BASE}/events", params={
                "key": OA_KEY,
                "search": kw,
                "timings[gte]": "2026-02-12",
                "timings[lte]": "2026-12-31",
                "size": 100,
                "sort": "timingsStart.asc"
            }, timeout=30)
            data = r.json()
            events = data.get("events", [])
            total = data.get("total", 0)
            print(f"    -> {total} résultats (page 1: {len(events)})")
            
            for ev in events:
                uid = ev.get("uid")
                if uid and uid not in seen_uids:
                    seen_uids.add(uid)
                    all_events.append(ev)
            
            time.sleep(1)
        except Exception as e:
            print(f"    ERREUR: {e}")
    
    print(f"\n  Total events uniques OpenAgenda electro: {len(all_events)}")
    return all_events

# ============================================================
# SOURCE 2: Berlin kulturdaten.berlin - Events musique/club
# Open Data
# ============================================================
def search_berlin_electro():
    """Chercher des events electro sur kulturdaten.berlin."""
    print("\n  Recherche Berlin kulturdaten.berlin (events musique/club)...")
    
    base = "https://www.kulturdaten.berlin/api/v1"
    electro_events = []
    
    # Fetch events with music/club tags
    try:
        r = requests.get(f"{base}/events", params={
            "page[size]": 100,
            "filter[tags]": "music,club,electronic,techno,dj"
        }, timeout=30)
        if r.status_code == 200:
            data = r.json()
            events = data.get("data", [])
            print(f"    -> {len(events)} events tagged music/club")
            electro_events.extend(events)
    except Exception as e:
        print(f"    Tags search error: {e}")
    
    # Also try category filter
    try:
        r = requests.get(f"{base}/events", params={
            "page[size]": 100,
            "filter[category]": "MUSIC"
        }, timeout=30)
        if r.status_code == 200:
            data = r.json()
            events = data.get("data", [])
            print(f"    -> {len(events)} events catégorie MUSIC")
    except Exception as e:
        print(f"    Category search error: {e}")
    
    return electro_events

# ============================================================
# SOURCE 3: Helsinki LinkedEvents - Musique
# CC BY 4.0
# ============================================================
def search_helsinki_electro():
    """Chercher des events musique sur Helsinki LinkedEvents."""
    print("\n  Recherche Helsinki LinkedEvents (events musique)...")
    
    base = "https://api.hel.fi/linkedevents/v1"
    electro_events = []
    
    # keyword "music" = yso:p1808
    try:
        r = requests.get(f"{base}/event/", params={
            "keyword": "yso:p1808",  # music
            "start": "2026-02-12",
            "end": "2026-12-31",
            "page_size": 100,
            "sort": "start_time"
        }, timeout=30)
        if r.status_code == 200:
            data = r.json()
            events = data.get("data", [])
            total = data.get("meta", {}).get("count", 0)
            print(f"    -> {total} events musique (page 1: {len(events)})")
            electro_events.extend(events)
    except Exception as e:
        print(f"    Error: {e}")
    
    return electro_events

# ============================================================
# SOURCE 4: OpenAgenda - Agendas spécialisés musique
# ============================================================
def search_openagenda_music_agendas():
    """Chercher des agendas spécialisés musique sur OpenAgenda."""
    print("\n  Recherche agendas spécialisés musique sur OpenAgenda...")
    
    kws = ["electronic music", "techno", "club", "nightlife", "DJ"]
    agendas_found = []
    
    for kw in kws:
        try:
            r = requests.get(f"{OA_BASE}/agendas", params={
                "key": OA_KEY,
                "search": kw,
                "size": 20
            }, timeout=30)
            data = r.json()
            agendas = data.get("agendas", [])
            print(f"    '{kw}': {len(agendas)} agendas")
            for ag in agendas:
                uid = ag.get("uid")
                name = ag.get("title", "?")
                count = ag.get("eventCount", 0) or ag.get("events", {}).get("total", 0)
                if count > 0:
                    print(f"      - {name} (uid={uid}, {count} events)")
                    agendas_found.append(ag)
            time.sleep(1)
        except Exception as e:
            print(f"    Error: {e}")
    
    return agendas_found

# ============================================================
# SOURCE 5: Madrid Open Data - Events musique
# ============================================================
def search_madrid_electro():
    """Chercher des events musique/concert sur Madrid open data."""
    print("\n  Recherche Madrid Open Data (events musique)...")
    
    url = "https://datos.madrid.es/egob/catalogo/206974-0-agenda-eventos-702702.json"
    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            data = r.json()
            graph = data.get("@graph", [])
            music_count = 0
            electro_kw = ["electrónica", "techno", "dj", "electro", "house", "club", "dance"]
            for ev in graph:
                title = (ev.get("title", "") or "").lower()
                desc = (ev.get("description", "") or "").lower()
                if any(kw in title or kw in desc for kw in electro_kw):
                    music_count += 1
            print(f"    -> Total events Madrid: {len(graph)}, electro keywords: {music_count}")
    except Exception as e:
        print(f"    Error: {e}")

# ============================================================
# SOURCE 6: Barcelona Open Data
# ============================================================
def search_barcelona_electro():
    """Chercher des events sur Barcelona open data."""
    print("\n  Recherche Barcelona Open Data...")
    
    url = "https://opendata-ajuntament.barcelona.cat/data/api/action/datastore_search"
    try:
        r = requests.get(url, params={
            "resource_id": "877ccb1f-0be0-41b1-a662-292b4ce45c8e",
            "q": "electrònica OR techno OR DJ OR club OR dance",
            "limit": 100
        }, timeout=30)
        if r.status_code == 200:
            data = r.json()
            records = data.get("result", {}).get("records", [])
            total = data.get("result", {}).get("total", 0)
            print(f"    -> {total} events electro Barcelona")
    except Exception as e:
        print(f"    Error: {e}")

# ============================================================
# SOURCE 7: Nantes Open Data
# ============================================================
def search_nantes_electro():
    """Events musique Nantes."""
    print("\n  Recherche Nantes Open Data (events musique)...")
    url = "https://data.nantesmetropole.fr/api/explore/v2.1/catalog/datasets/244400404_agenda-evenements-702702-702702/records"
    try:
        r = requests.get(url, params={
            "where": "titre LIKE '%electro%' OR titre LIKE '%techno%' OR titre LIKE '%DJ%' OR titre LIKE '%club%'",
            "limit": 100
        }, timeout=30)
        if r.status_code == 200:
            data = r.json()
            total = data.get("total_count", 0)
            results = data.get("results", [])
            print(f"    -> {total} events electro Nantes")
    except Exception as e:
        print(f"    Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("RECHERCHE EVENTS ELECTRO - SOURCES OPEN DATA")
    print("=" * 60)
    
    # 1. OpenAgenda - agendas spécialisés
    agendas = search_openagenda_music_agendas()
    
    # 2. OpenAgenda - recherche directe
    oa_events = search_openagenda_electro()
    
    # Analyser les pays des events OpenAgenda
    print("\n--- OpenAgenda electro par pays ---")
    country_counts = {}
    for ev in oa_events:
        loc = ev.get("location", {}) or {}
        country = loc.get("countryCode", "?")
        country_counts[country] = country_counts.get(country, 0) + 1
    for c, count in sorted(country_counts.items(), key=lambda x: -x[1])[:15]:
        print(f"  {c}: {count}")
    
    # 3. Berlin
    search_berlin_electro()
    
    # 4. Helsinki
    search_helsinki_electro()
    
    # 5. Madrid
    search_madrid_electro()
    
    # 6. Barcelona
    search_barcelona_electro()
    
    # 7. Nantes
    search_nantes_electro()
    
    print("\n" + "=" * 60)
    print("EXPLORATION TERMINÉE")
