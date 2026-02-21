"""
Recherche d'events electro supplémentaires sur des sources encore non exploitées.
1. OpenAgenda - chercher des agendas de salles de musique (par localisation)
2. Amsterdam Open Data
3. Zurich/Swiss cities open data
4. Lyon Open Data
5. Bruxelles Open Data
"""
import requests
import time
import json

OA_KEY = "0e3b442455894aa09e7b8acb7d43c69c"

# ============================================================
# 1. OpenAgenda - Agendas par localisation (grandes villes electro)
# ============================================================
def search_openagenda_agendas_by_location():
    """Search for music agendas in major European cities."""
    print("=" * 60)
    print("OPENAGENDA - Agendas musique par ville")
    print("=" * 60)
    
    cities = [
        ("Paris", 48.8566, 2.3522),
        ("Berlin", 52.5200, 13.4050),
        ("Amsterdam", 52.3676, 4.9041),
        ("Bruxelles", 50.8503, 4.3517),
        ("Genève", 46.2044, 6.1432),
        ("Lyon", 45.7640, 4.8357),
        ("Marseille", 43.2965, 5.3698),
        ("Toulouse", 43.6047, 1.4442),
        ("Bordeaux", 44.8378, -0.5792),
        ("Zürich", 47.3769, 8.5417),
    ]
    
    all_agendas = []
    
    for city_name, lat, lng in cities:
        try:
            r = requests.get("https://api.openagenda.com/v2/agendas", params={
                "key": OA_KEY,
                "geo[lat]": lat,
                "geo[lng]": lng,
                "geo[radius]": 30000,  # 30km
                "size": 50,
            }, timeout=20)
            data = r.json()
            agendas = data.get("agendas", [])
            total = data.get("total", 0)
            
            # Filter for music-related agendas
            music_agendas = []
            for ag in agendas:
                title = (ag.get("title") or "").lower()
                desc = (ag.get("description") or "").lower()
                slug = (ag.get("slug") or "").lower()
                text = f"{title} {desc} {slug}"
                
                music_words = ["musique", "music", "concert", "club", "electro", "techno",
                              "dj", "festival", "soirée", "nightlife", "party", "dance",
                              "scène", "salle", "spectacle", "live"]
                if any(w in text for w in music_words):
                    music_agendas.append(ag)
            
            if music_agendas:
                print(f"\n  {city_name}: {total} agendas total, {len(music_agendas)} musique-related")
                for ag in music_agendas[:5]:
                    name = ag.get("title", "?")
                    uid = ag.get("uid")
                    count = ag.get("eventsTotalCount", 0) or 0
                    upcoming = ag.get("eventsUpcomingCount", 0) or 0
                    print(f"    - {name} (uid={uid}, total={count}, upcoming={upcoming})")
                    all_agendas.append(ag)
            else:
                print(f"\n  {city_name}: {total} agendas total, 0 musique-related")
            
            time.sleep(1)
        except Exception as e:
            print(f"\n  {city_name}: ERREUR {e}")
    
    return all_agendas


# ============================================================
# 2. OpenAgenda - Fetch events from music agendas
# ============================================================
def fetch_agenda_electro_events(agenda_uid, agenda_title):
    """Fetch electro events from a specific OpenAgenda agenda."""
    electro_kw = ["techno", "electro", "house", "trance", "dj", "rave", "bass",
                  "dubstep", "electronic", "club night", "after party", "minimal",
                  "acid", "deep house", "hardstyle", "jungle", "dnb", "neurofunk"]
    
    try:
        r = requests.get(f"https://api.openagenda.com/v2/agendas/{agenda_uid}/events", params={
            "key": OA_KEY,
            "relative[]": "upcoming",
            "size": 100,
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
        
        if electro:
            print(f"    {agenda_title[:40]}: {total} upcoming, {len(electro)} electro")
            for ev in electro[:3]:
                t = ev.get("title", {}).get("fr", "") or ev.get("title", {}).get("en", "?")
                print(f"      - {t[:60]}")
        
        return electro
    except Exception as e:
        return []


# ============================================================
# 3. Amsterdam Open Data
# ============================================================
def search_amsterdam():
    """Search Amsterdam open data for events."""
    print("\n" + "=" * 60)
    print("AMSTERDAM - Open Data Events")
    print("=" * 60)
    
    # Amsterdam open data portal
    url = "https://api.data.amsterdam.nl/v1/evenementen/evenementen/"
    try:
        r = requests.get(url, params={"_pageSize": 100}, timeout=20)
        if r.status_code == 200:
            data = r.json()
            results = data.get("_embedded", {}).get("evenementen", [])
            total = data.get("page", {}).get("totalElements", 0)
            print(f"  Total: {total}, Page: {len(results)}")
            
            electro_kw = ["techno", "electro", "house", "dj", "rave", "club", "dance",
                         "bass", "trance", "electronic"]
            electro = []
            for ev in results:
                title = (ev.get("titel", "") or "").lower()
                desc = (ev.get("omschrijving", "") or "").lower()
                if any(kw in title or kw in desc for kw in electro_kw):
                    electro.append(ev)
            
            print(f"  Electro: {len(electro)}")
            for ev in electro[:5]:
                print(f"    - {ev.get('titel', '?')[:60]}")
            return electro
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")
    
    # Try alternative Amsterdam API
    try:
        url2 = "https://data.amsterdam.nl/api/3/action/datastore_search"
        r = requests.get(url2, params={"resource_id": "evenementen", "limit": 5}, timeout=15)
        print(f"  Alt API: {r.status_code}")
    except Exception as e:
        print(f"  Alt API error: {e}")
    
    return []


# ============================================================
# 4. Lyon Open Data
# ============================================================
def search_lyon():
    """Search Lyon open data for events."""
    print("\n" + "=" * 60)
    print("LYON - Open Data Events")
    print("=" * 60)
    
    url = "https://data.grandlyon.com/api/explore/v2.1/catalog/datasets/evenements-grand-lyon/records"
    try:
        r = requests.get(url, params={
            "where": "date_debut >= '2026-02-12'",
            "limit": 100,
            "order_by": "date_debut"
        }, timeout=20)
        
        if r.status_code == 200:
            data = r.json()
            total = data.get("total_count", 0)
            results = data.get("results", [])
            print(f"  Total: {total}, Fetched: {len(results)}")
            
            electro_kw = ["techno", "electro", "house", "dj", "rave", "club",
                         "electronic", "bass", "trance"]
            electro = []
            for ev in results:
                title = (ev.get("titre", "") or "").lower()
                desc = (ev.get("description", "") or "").lower()
                if any(kw in title or kw in desc for kw in electro_kw):
                    electro.append(ev)
            
            print(f"  Electro: {len(electro)}")
            for ev in electro[:5]:
                print(f"    - {ev.get('titre', '?')[:60]}")
        else:
            print(f"  HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 5. Toulouse Open Data
# ============================================================
def search_toulouse():
    """Search Toulouse/Occitanie open data for events."""
    print("\n" + "=" * 60)
    print("TOULOUSE - Open Data Events")
    print("=" * 60)
    
    url = "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/agenda-des-manifestations-702702/records"
    try:
        r = requests.get(url, params={
            "where": "date_debut >= '2026-02-12'",
            "limit": 100,
        }, timeout=20)
        
        if r.status_code == 200:
            data = r.json()
            total = data.get("total_count", 0)
            results = data.get("results", [])
            print(f"  Total: {total}, Fetched: {len(results)}")
            
            electro = [ev for ev in results 
                       if any(kw in (ev.get("titre", "") or "").lower() + " " + (ev.get("descriptif", "") or "").lower()
                              for kw in ["techno", "electro", "house", "dj", "rave", "electronic", "bass", "club night"])]
            print(f"  Electro: {len(electro)}")
            for ev in electro[:5]:
                print(f"    - {ev.get('titre', '?')[:60]}")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 6. Bruxelles Open Data
# ============================================================
def search_bruxelles():
    """Search Brussels open data for events."""
    print("\n" + "=" * 60)
    print("BRUXELLES - Open Data Events")
    print("=" * 60)
    
    url = "https://data.gov.be/api/3/action/package_search"
    try:
        r = requests.get(url, params={"q": "evenementen events agenda", "rows": 10}, timeout=20)
        if r.status_code == 200:
            data = r.json()
            results = data.get("result", {}).get("results", [])
            print(f"  Datasets trouvés: {len(results)}")
            for ds in results[:5]:
                name = ds.get("title", "?")
                org = ds.get("organization", {}).get("title", "?")
                print(f"    - {name} ({org})")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 7. Bordeaux Open Data
# ============================================================
def search_bordeaux():
    """Search Bordeaux open data for events."""
    print("\n" + "=" * 60)
    print("BORDEAUX - Open Data Events")
    print("=" * 60)
    
    url = "https://opendata.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/bor_manifestation/records"
    try:
        r = requests.get(url, params={
            "limit": 100,
            "order_by": "datedebut"
        }, timeout=20)
        
        if r.status_code == 200:
            data = r.json()
            total = data.get("total_count", 0)
            results = data.get("results", [])
            print(f"  Total: {total}, Fetched: {len(results)}")
            
            electro = [ev for ev in results 
                       if any(kw in (ev.get("nom", "") or "").lower() + " " + (ev.get("descriptif", "") or "").lower()
                              for kw in ["techno", "electro", "house", "dj", "electronic", "club"])]
            print(f"  Electro: {len(electro)}")
        else:
            print(f"  HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  ERREUR: {e}")


# ============================================================
# 8. Strasbourg Open Data
# ============================================================
def search_strasbourg():
    """Search Strasbourg open data for events."""
    print("\n" + "=" * 60)
    print("STRASBOURG - Open Data Events")
    print("=" * 60)
    
    url = "https://data.strasbourg.eu/api/explore/v2.1/catalog/datasets/lieux-de-culture-702702/records"
    try:
        r = requests.get(url, params={"limit": 5}, timeout=15)
        print(f"  Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"  Total: {data.get('total_count', '?')}")
    except Exception as e:
        print(f"  ERREUR: {e}")


if __name__ == "__main__":
    # 1. OpenAgenda agendas
    music_agendas = search_openagenda_agendas_by_location()
    
    # 2. Fetch events from promising agendas
    if music_agendas:
        print("\n--- Fetch events des agendas musique ---")
        total_electro = 0
        for ag in music_agendas:
            uid = ag.get("uid")
            title = ag.get("title", "?")
            upcoming = ag.get("eventsUpcomingCount", 0) or 0
            if upcoming > 5:
                evts = fetch_agenda_electro_events(uid, title)
                total_electro += len(evts)
                time.sleep(0.5)
        print(f"\n  Total events electro OpenAgenda: {total_electro}")
    
    # 3-8. Other city APIs
    search_amsterdam()
    search_lyon()
    search_toulouse()
    search_bordeaux()
    search_bruxelles()
    
    print("\n" + "=" * 60)
    print("EXPLORATION TERMINÉE")
    print("=" * 60)
