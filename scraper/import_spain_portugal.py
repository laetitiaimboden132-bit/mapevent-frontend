"""
Import d'événements Espagne et Portugal depuis données ouvertes.

Sources:
  - Madrid: datos.madrid.es (Agenda actividades culturales, JSON)
  - Barcelone: opendata-ajuntament.barcelona.cat  
  - Portugal: dados.gov.pt / Lisboa dados abertos

Toutes sous licences CC-BY ou équivalentes ouvertes.
"""

import requests
import json
import time
import re
from datetime import datetime, date

API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (open data consumer)"}

# ============================================================================
# CATÉGORISATION
# ============================================================================
def categorize_event_es(titulo, descripcion, tipo=""):
    """Catégorise un événement espagnol/portugais."""
    combined = f"{titulo} {descripcion} {tipo}".lower()
    cats = []
    
    if any(w in combined for w in ["concierto", "concert", "música", "musica", "jazz", "orquesta", "sinfon", "ópera", "opera", "flamenco"]):
        if "jazz" in combined: cats.append("Musique > Jazz")
        elif "flamenco" in combined: cats.append("Musique > Flamenco")
        elif "clásic" in combined or "sinfon" in combined or "orquesta" in combined: cats.append("Musique > Classique")
        elif "electr" in combined or "techno" in combined: cats.append("Musique > Electronic")
        elif "rock" in combined: cats.append("Musique > Rock")
        else: cats.append("Musique > Concert")
    
    if any(w in combined for w in ["exposición", "exposicao", "exposicion", "museo", "museu", "galería", "galeria", "arte"]):
        cats.append("Culture > Exposition")
    
    if any(w in combined for w in ["teatro", "theatre", "comedia", "comédia", "humor"]):
        cats.append("Spectacle > Théâtre")
    
    if any(w in combined for w in ["danza", "dança", "ballet"]):
        cats.append("Danse")
    
    if any(w in combined for w in ["festival", "fiesta", "festa", "feria", "carnaval"]):
        cats.append("Festival")
    
    if any(w in combined for w in ["cine", "cinema", "película", "filme"]):
        cats.append("Culture > Cinéma")
    
    if any(w in combined for w in ["conferencia", "conferência", "taller", "oficina", "workshop"]):
        cats.append("Culture > Conférence")
    
    if any(w in combined for w in ["deporte", "desporto", "maratón", "maraton", "fútbol", "futebol"]):
        cats.append("Sport")
    
    if any(w in combined for w in ["mercado", "mercadillo", "feira"]):
        cats.append("Marché")
    
    if any(w in combined for w in ["niños", "crianças", "familia", "infantil"]):
        cats.append("Famille")
    
    if not cats:
        cats = ["Divertissement"]
    
    return cats[:3]


def clean_html(text, max_len=300):
    if not text: return ""
    text = re.sub(r'<[^>]+>', ' ', str(text))
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_len:
        text = text[:max_len].rsplit(' ', 1)[0] + "..."
    return text


def parse_date_flex(date_str):
    if not date_str: return None, None
    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"]:
        try:
            dt = datetime.strptime(date_str[:len(fmt.replace('%','').replace('Y','0000').replace('m','00').replace('d','00').replace('H','00').replace('M','00').replace('S','00'))], fmt)
            d = dt.strftime("%Y-%m-%d")
            t = dt.strftime("%H:%M") if dt.hour or dt.minute else None
            return d, t
        except: continue
    try:
        dt = datetime.fromisoformat(date_str.replace('Z','+00:00'))
        return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M") if dt.hour or dt.minute else None
    except:
        return None, None


# ============================================================================
# MADRID - Agenda de actividades y eventos
# ============================================================================
def fetch_madrid_events():
    """Fetch événements de Madrid via datos.madrid.es."""
    # URL connue de l'agenda des activités culturelles et de loisirs de Madrid
    urls_to_try = [
        "https://datos.madrid.es/egob/catalogo/300107-0-agenda-actividades-eventos.json",
        "https://datos.madrid.es/egob/catalogo/206974-0-agenda-eventos-702702.json",
        "https://datos.madrid.es/egob/catalogo/200164-0-actividades-702702.json",
    ]
    
    print("📥 Téléchargement données Madrid...")
    
    data = None
    for url in urls_to_try:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                data = r.json()
                print(f"  ✅ Source trouvée: {url}")
                break
            else:
                print(f"  ❌ {url} -> {r.status_code}")
        except Exception as e:
            print(f"  ❌ {url} -> {e}")
    
    if not data:
        print("  ⚠️ Aucune source Madrid trouvée, essai catalogue...")
        # Essayer le catalogue CKAN
        try:
            r = requests.get("https://datos.madrid.es/egob/catalogo/206974-0-agenda-eventos-702702.json", headers=HEADERS, timeout=15)
            if r.status_code == 200:
                data = r.json()
        except: pass
    
    if not data:
        print("  ❌ Impossible de charger les données Madrid")
        return []
    
    # Le format peut être {"@graph": [...]} ou directement une liste
    records = data.get("@graph", data) if isinstance(data, dict) else data
    if not isinstance(records, list):
        records = [data]
    
    print(f"  📊 {len(records)} records bruts")
    
    today = date.today()
    events = []
    
    for rec in records:
        title = rec.get("title", rec.get("titulo", ""))
        if not title: continue
        
        # Coordonnées
        location_data = rec.get("location", {})
        lat = None
        lng = None
        
        if isinstance(location_data, dict):
            lat = location_data.get("latitude")
            lng = location_data.get("longitude")
        
        if not lat:
            lat = rec.get("latitud") or rec.get("latitude")
        if not lng:
            lng = rec.get("longitud") or rec.get("longitude")
        
        if not lat or not lng:
            # Coordonnées par défaut Madrid centre si adresse présente
            address = rec.get("address", rec.get("direccion", ""))
            if isinstance(address, dict):
                address = address.get("street-address", "")
            if address and "madrid" in str(address).lower():
                lat, lng = 40.4168, -3.7038  # Centre Madrid
            else:
                continue
        
        lat, lng = float(lat), float(lng)
        
        # Vérifier Espagne (lat 35-44, lng -10 à 5)
        if not (35 <= lat <= 44 and -10 <= lng <= 5):
            continue
        
        # Dates
        dtstart = rec.get("dtstart", rec.get("fecha-inicio", rec.get("date_start", "")))
        dtend = rec.get("dtend", rec.get("fecha-fin", rec.get("date_end", "")))
        
        start_date, start_time = parse_date_flex(str(dtstart) if dtstart else "")
        end_date, end_time = parse_date_flex(str(dtend) if dtend else "")
        
        if start_date:
            try:
                ed = datetime.strptime(end_date or start_date, "%Y-%m-%d").date()
                if ed < today:
                    continue
            except: pass
        
        # URL source
        source_url = rec.get("link", rec.get("url", rec.get("relation", "")))
        if isinstance(source_url, dict):
            source_url = source_url.get("@id", "")
        if not source_url or not str(source_url).startswith("http"):
            # Essayer id comme URL
            rid = rec.get("@id", rec.get("id", ""))
            if str(rid).startswith("http"):
                source_url = rid
            else:
                continue
        
        description = clean_html(rec.get("description", rec.get("descripcion", "")))
        
        # Adresse
        address = rec.get("address", rec.get("direccion", ""))
        if isinstance(address, dict):
            addr_parts = [address.get("street-address", ""), address.get("locality", "Madrid")]
            address = ", ".join([p for p in addr_parts if p])
        location_str = f"{address}, Madrid, Espagne" if address else "Madrid, Espagne"
        
        categories = categorize_event_es(title, description, rec.get("type", ""))
        
        events.append({
            "title": str(title).strip(),
            "description": description,
            "location": location_str,
            "latitude": lat,
            "longitude": lng,
            "date": start_date,
            "time": start_time,
            "end_date": end_date,
            "end_time": end_time,
            "categories": categories,
            "source_url": str(source_url),
            "validation_status": "auto_validated",
            "status": "active",
        })
    
    print(f"  ✅ {len(events)} événements futurs Madrid")
    return events


# ============================================================================
# BARCELONE - Open Data BCN
# ============================================================================
def fetch_barcelona_events():
    """Fetch événements de Barcelone."""
    urls_to_try = [
        "https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show?id=agenda-cultural",
        "https://opendata-ajuntament.barcelona.cat/data/api/3/action/datastore_search?resource_id=agenda-cultural&limit=1000",
    ]
    
    print("\n📥 Téléchargement données Barcelone...")
    
    # Essayer l'API CKAN
    for url in urls_to_try:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                data = r.json()
                if data.get("success"):
                    print(f"  ✅ API CKAN Barcelone OK")
                    # Extraire les ressources
                    result = data.get("result", {})
                    if isinstance(result, dict) and "resources" in result:
                        for res in result["resources"]:
                            if "json" in res.get("format", "").lower():
                                json_url = res.get("url")
                                if json_url:
                                    print(f"  📥 Téléchargement: {json_url}")
                                    r2 = requests.get(json_url, headers=HEADERS, timeout=30)
                                    if r2.status_code == 200:
                                        return parse_barcelona_json(r2.json())
                    elif isinstance(result, dict) and "records" in result:
                        return parse_barcelona_records(result["records"])
        except Exception as e:
            print(f"  ❌ {url} -> {e}")
    
    print("  ⚠️ API Barcelone non accessible, utilisation de données alternatives")
    return []


def parse_barcelona_json(data):
    """Parse les données JSON de Barcelone."""
    records = data if isinstance(data, list) else data.get("features", data.get("results", []))
    print(f"  📊 {len(records)} records bruts Barcelone")
    # TODO: parser selon le format réel
    return []


def parse_barcelona_records(records):
    """Parse les records CKAN de Barcelone."""
    print(f"  📊 {len(records)} records")
    events = []
    today = date.today()
    
    for rec in records:
        title = rec.get("nom", rec.get("name", rec.get("titulo", "")))
        if not title: continue
        
        lat = rec.get("latitud", rec.get("latitude"))
        lng = rec.get("longitud", rec.get("longitude"))
        if not lat or not lng:
            lat, lng = 41.3874, 2.1686  # Centre Barcelone
        
        source_url = rec.get("url", rec.get("link", ""))
        if not str(source_url).startswith("http"):
            continue
        
        events.append({
            "title": str(title).strip(),
            "description": clean_html(rec.get("descripcio", rec.get("description", ""))),
            "location": f"Barcelona, Espagne",
            "latitude": float(lat),
            "longitude": float(lng),
            "date": None,
            "time": None,
            "end_date": None,
            "end_time": None,
            "categories": categorize_event_es(title, "", ""),
            "source_url": str(source_url),
            "validation_status": "auto_validated",
            "status": "active",
        })
    
    print(f"  ✅ {len(events)} événements Barcelone")
    return events


# ============================================================================
# LISBONNE - Open Data
# ============================================================================
def fetch_lisboa_events():
    """Fetch événements de Lisbonne."""
    urls_to_try = [
        "https://lisboaaberta.cm-lisboa.pt/index.php/pt/dados/conjuntos-de-dados",
        "https://dados.gov.pt/api/1/datasets/?tag=eventos&format=json",
    ]
    
    print("\n📥 Recherche données Lisbonne/Portugal...")
    
    for url in urls_to_try:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                print(f"  ✅ {url} accessible")
                data = r.json() if 'json' in r.headers.get('content-type', '') else None
                if data:
                    # Parser selon le format
                    results = data.get("data", data.get("results", []))
                    print(f"  📊 {len(results)} datasets trouvés")
                    for ds in results[:5]:
                        print(f"    - {ds.get('title', ds.get('name', '?'))}")
            else:
                print(f"  ❌ {url} -> {r.status_code}")
        except Exception as e:
            print(f"  ❌ {url} -> {e}")
    
    return []


# ============================================================================
# DÉDUPLICATION & IMPORT
# ============================================================================
def deduplicate_with_existing(new_events):
    print("\n🔍 Vérification des doublons...")
    r = requests.get(f"{API_BASE}/events", timeout=30)
    if r.status_code != 200:
        return new_events
    
    existing = r.json()
    existing_titles = set((e.get("title") or "").lower().strip() for e in existing)
    existing_urls = set(e.get("source_url") or "" for e in existing)
    
    unique = [ev for ev in new_events 
              if ev["title"].lower().strip() not in existing_titles 
              and ev["source_url"] not in existing_urls]
    
    print(f"  📊 {len(new_events) - len(unique)} doublons, {len(unique)} uniques")
    return unique


def import_events(events, source_name, batch_size=30):
    if not events:
        print("  Aucun événement à importer.")
        return 0
    
    print(f"\n📤 Import {len(events)} événements ({source_name})...")
    total = 0
    for i in range(0, len(events), batch_size):
        batch = events[i:i+batch_size]
        try:
            r = requests.post(f"{API_BASE}/events/scraped/batch", json={"events": batch}, 
                            headers={"Content-Type": "application/json"}, timeout=30)
            if r.status_code in (200, 201):
                count = r.json().get("imported", len(batch))
                total += count
                print(f"  ✅ Batch {i//batch_size + 1}: {count}")
            else:
                print(f"  ❌ Batch {i//batch_size + 1}: {r.status_code}")
        except Exception as e:
            print(f"  ❌ Batch {i//batch_size + 1}: {e}")
        time.sleep(1)
    
    print(f"🎉 Total: {total} ({source_name})")
    return total


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🇪🇸🇵🇹 IMPORT ÉVÉNEMENTS ESPAGNE & PORTUGAL - OPEN DATA")
    print("=" * 60)
    
    all_events = []
    
    # 1. Madrid
    print("\n" + "=" * 40)
    print("📍 MADRID")
    print("=" * 40)
    madrid = fetch_madrid_events()
    all_events.extend(madrid)
    
    # 2. Barcelone
    print("\n" + "=" * 40)
    print("📍 BARCELONE")
    print("=" * 40)
    barcelona = fetch_barcelona_events()
    all_events.extend(barcelona)
    
    # 3. Lisbonne
    print("\n" + "=" * 40)
    print("📍 LISBONNE / PORTUGAL")
    print("=" * 40)
    lisboa = fetch_lisboa_events()
    all_events.extend(lisboa)
    
    if all_events:
        unique = deduplicate_with_existing(all_events)
        if unique:
            print(f"\nAperçu (5 premiers):")
            for e in unique[:5]:
                print(f"  {e['date']} | {e['title'][:60]}")
                print(f"     📍 lat={e['latitude']:.4f} lng={e['longitude']:.4f}")
                print(f"     🔗 {e['source_url'][:80]}")
                print()
            
            import_events(unique, "Espagne & Portugal Open Data")
    
    print("\n✅ Terminé!")
