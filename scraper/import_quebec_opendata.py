"""
Import d'événements du Québec depuis les données ouvertes (CC-BY 4.0)

Sources:
  - Montréal: donnees.montreal.ca/dataset/evenements-publics (GeoJSON, CC-BY 4.0)
  - Données Québec/Longueuil: donneesquebec.ca (CSV, CC-BY 4.0)

Licence: Creative Commons Attribution 4.0 - Utilisation libre avec attribution
"""

import requests
import json
import time
import re
from datetime import datetime, date

API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

# ============================================================================
# CATÉGORISATION
# ============================================================================
def categorize_event(event_type, title, description):
    """Catégorise un événement selon son type et contenu."""
    title_lower = (title or "").lower()
    desc_lower = (description or "").lower()
    event_type_lower = (event_type or "").lower()
    combined = f"{title_lower} {desc_lower} {event_type_lower}"
    
    cats = []
    
    # Musique
    if any(w in combined for w in ["concert", "musique", "musical", "jazz", "symphoni", "orchestre", "chanson", "chant"]):
        if "jazz" in combined:
            cats.append("Musique > Jazz")
        elif "classique" in combined or "symphoni" in combined or "orchestre" in combined:
            cats.append("Musique > Classique")
        elif "rock" in combined:
            cats.append("Musique > Rock")
        elif "hip-hop" in combined or "hip hop" in combined or "rap" in combined:
            cats.append("Musique > Hip-Hop")
        elif "electro" in combined or "dj" in combined:
            cats.append("Musique > Electronic")
        else:
            cats.append("Musique > Concert")
    
    # Spectacle / Théâtre
    if any(w in combined for w in ["spectacle", "théâtre", "theatre", "comédie", "comedie", "humour", "cirque", "marionnette"]):
        if "humour" in combined:
            cats.append("Spectacle > Humour")
        elif "cirque" in combined:
            cats.append("Spectacle > Cirque")
        elif "théâtre" in combined or "theatre" in combined:
            cats.append("Spectacle > Théâtre")
        else:
            cats.append("Spectacle > Spectacle")
    
    # Exposition / Art
    if any(w in combined for w in ["exposition", "expo ", "musée", "musee", "galerie", "art ", "vernissage"]):
        cats.append("Culture > Exposition")
    
    # Danse
    if "danse" in combined or "ballet" in combined:
        cats.append("Danse")
    
    # Festival
    if "festival" in combined or "fête" in combined or "fete" in combined or "carnaval" in combined:
        cats.append("Festival")
    
    # Conférence / Atelier
    if any(w in combined for w in ["conférence", "conference", "colloque", "séminaire", "seminaire"]):
        cats.append("Culture > Conférence")
    if "atelier" in combined:
        cats.append("Culture > Atelier")
    
    # Sport
    if any(w in combined for w in ["sport", "course", "marathon", "vélo", "velo", "hockey", "patinage", "ski"]):
        cats.append("Sport")
    
    # Marché
    if "marché" in combined or "marche" in combined or "bazar" in combined:
        cats.append("Marché")
    
    # Cinéma
    if "cinéma" in combined or "cinema" in combined or "film" in combined or "projection" in combined:
        cats.append("Culture > Cinéma")
    
    # Littérature
    if any(w in combined for w in ["littéra", "littera", "livre", "lecture", "conte ", "conte,", "poésie", "poesie"]):
        cats.append("Culture > Littérature")
    
    # Famille / Enfants
    if any(w in combined for w in ["enfant", "famille", "jeune public", "kids", "jeunesse"]):
        cats.append("Famille")
    
    # Séance publique / consultation
    if any(w in combined for w in ["séance publique", "seance publique", "consultation", "assemblée"]):
        cats.append("Communauté > Réunion publique")
    
    # Défaut
    if not cats:
        if event_type_lower:
            type_map = {
                "spectacle": ["Spectacle > Spectacle"],
                "exposition": ["Culture > Exposition"],
                "atelier": ["Culture > Atelier"],
                "séance publique": ["Communauté > Réunion publique"],
                "marché": ["Marché"],
            }
            for key, val in type_map.items():
                if key in event_type_lower:
                    cats = val
                    break
        if not cats:
            cats = ["Divertissement"]
    
    return cats[:3]  # Max 3 catégories


def clean_description(desc, max_len=300):
    """Nettoie et raccourcit la description (réécriture, pas copier-coller)."""
    if not desc:
        return ""
    # Supprimer les balises HTML
    desc = re.sub(r'<[^>]+>', ' ', desc)
    # Supprimer les espaces multiples
    desc = re.sub(r'\s+', ' ', desc).strip()
    # Tronquer si trop long
    if len(desc) > max_len:
        desc = desc[:max_len].rsplit(' ', 1)[0] + "..."
    return desc


def parse_date(date_str):
    """Parse une date ISO ou autre format."""
    if not date_str:
        return None, None
    try:
        # Format ISO: 2026-02-14T19:00:00
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        date_part = dt.strftime("%Y-%m-%d")
        time_part = dt.strftime("%H:%M") if dt.hour != 0 or dt.minute != 0 else None
        return date_part, time_part
    except:
        try:
            # Format date seule
            dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d"), None
        except:
            return None, None


# ============================================================================
# SOURCE 1: MONTRÉAL - Événements publics (GeoJSON, CC-BY 4.0)
# ============================================================================
def fetch_montreal_events():
    """Fetch les événements publics de Montréal depuis le GeoJSON open data."""
    url = "https://donnees.montreal.ca/dataset/6a4cbf2c-c9b7-413a-86b1-e8f7081e2578/resource/35307457-a00f-4912-9941-8095ead51f6e/download/evenements.geojson"
    
    print("📥 Téléchargement GeoJSON Montréal...")
    headers = {"User-Agent": "MapEventAI-Bot/1.0 (open data consumer)"}
    r = requests.get(url, headers=headers, timeout=30)
    
    if r.status_code != 200:
        print(f"  ❌ Erreur {r.status_code}")
        return []
    
    data = r.json()
    features = data.get("features", [])
    print(f"  📊 {len(features)} événements bruts dans le GeoJSON")
    
    today = date.today()
    events = []
    skipped_past = 0
    skipped_no_coords = 0
    skipped_no_url = 0
    
    for f in features:
        props = f.get("properties", {})
        geom = f.get("geometry", {})
        
        # Coordonnées
        lat = props.get("lat")
        lng = props.get("long")
        
        if not lat or not lng:
            # Essayer depuis la géométrie GeoJSON
            if geom and geom.get("coordinates"):
                coords = geom["coordinates"]
                if coords and len(coords) >= 2:
                    lng, lat = coords[0], coords[1]
                else:
                    skipped_no_coords += 1
                    continue
            else:
                skipped_no_coords += 1
                continue
        
        lat = float(lat)
        lng = float(lng)
        
        # Vérifier que c'est au Québec (lat 44-50, lng -80 à -58)
        if not (44 <= lat <= 50 and -80 <= lng <= -58):
            continue
        
        # Dates
        date_debut = props.get("date_debut")
        date_fin = props.get("date_fin")
        
        start_date, start_time = parse_date(date_debut)
        end_date, end_time = parse_date(date_fin)
        
        # Filtrer les événements passés
        if start_date:
            try:
                event_end = datetime.strptime(end_date or start_date, "%Y-%m-%d").date()
                if event_end < today:
                    skipped_past += 1
                    continue
            except:
                pass
        
        # URL de la fiche (CRITIQUE: doit mener à l'event)
        source_url = props.get("url_fiche")
        if not source_url or not source_url.startswith("http"):
            skipped_no_url += 1
            continue
        
        # Titre et description
        title = props.get("titre", "").strip()
        if not title:
            continue
        
        description = clean_description(props.get("description", ""))
        
        # Adresse
        venue = props.get("titre_adresse", "")
        address = props.get("adresse_principale", "")
        borough = props.get("arrondissement", "")
        location = f"{venue}, {address}, {borough}, Montréal, QC".strip(", ")
        
        # Catégories
        event_type = props.get("type_evenement", "")
        categories = categorize_event(event_type, title, description)
        
        events.append({
            "title": title,
            "description": description,
            "location": location,
            "latitude": lat,
            "longitude": lng,
            "date": start_date,
            "time": start_time,
            "end_date": end_date,
            "end_time": end_time,
            "categories": categories,
            "source_url": source_url,
            "validation_status": "auto_validated",
            "status": "active",
        })
    
    print(f"  ✅ {len(events)} événements futurs avec coordonnées et URL")
    print(f"  ⏭️ {skipped_past} passés, {skipped_no_coords} sans coords, {skipped_no_url} sans URL")
    return events


# ============================================================================
# DÉDUPLICATION
# ============================================================================
def deduplicate_with_existing(new_events):
    """Supprime les doublons avec les events déjà sur la carte."""
    print("\n🔍 Vérification des doublons avec la base existante...")
    
    r = requests.get(f"{API_BASE}/events", timeout=30)
    if r.status_code != 200:
        print("  ⚠️ Impossible de charger les events existants, on continue")
        return new_events
    
    existing = r.json()
    existing_titles = set()
    existing_urls = set()
    
    for e in existing:
        t = (e.get("title") or "").lower().strip()
        if t:
            existing_titles.add(t)
        u = e.get("source_url") or ""
        if u:
            existing_urls.add(u)
    
    unique = []
    dupes = 0
    for ev in new_events:
        title_lower = ev["title"].lower().strip()
        if title_lower in existing_titles or ev["source_url"] in existing_urls:
            dupes += 1
            continue
        unique.append(ev)
    
    print(f"  📊 {dupes} doublons trouvés, {len(unique)} events uniques à importer")
    return unique


# ============================================================================
# IMPORT VIA API
# ============================================================================
def import_events(events, source_name, batch_size=30):
    """Importe les événements via l'API batch."""
    if not events:
        print("  Aucun événement à importer.")
        return
    
    print(f"\n📤 Import de {len(events)} événements ({source_name})...")
    
    total_imported = 0
    for i in range(0, len(events), batch_size):
        batch = events[i:i+batch_size]
        
        payload = {"events": batch}
        
        try:
            r = requests.post(
                f"{API_BASE}/events/scraped/batch",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if r.status_code in (200, 201):
                result = r.json()
                count = result.get("imported", result.get("count", len(batch)))
                total_imported += count
                print(f"  ✅ Batch {i//batch_size + 1}: {count} importés")
            else:
                print(f"  ❌ Batch {i//batch_size + 1}: erreur {r.status_code} - {r.text[:200]}")
        except Exception as e:
            print(f"  ❌ Batch {i//batch_size + 1}: exception {e}")
        
        time.sleep(1)  # Pause entre les batches
    
    print(f"\n🎉 Total importé: {total_imported} événements ({source_name})")
    return total_imported


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🍁 IMPORT ÉVÉNEMENTS QUÉBEC - OPEN DATA (CC-BY 4.0)")
    print("=" * 60)
    
    # 1. Montréal
    print("\n" + "=" * 40)
    print("📍 SOURCE: Ville de Montréal")
    print("   Licence: CC-BY 4.0")
    print("   URL: donnees.montreal.ca")
    print("=" * 40)
    
    mtl_events = fetch_montreal_events()
    
    if mtl_events:
        # Stats par catégorie
        cat_counts = {}
        for e in mtl_events:
            for c in e["categories"]:
                cat_counts[c] = cat_counts.get(c, 0) + 1
        
        print(f"\n📊 Catégories:")
        for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])[:15]:
            print(f"  {cat}: {count}")
        
        # Déduplications
        unique_events = deduplicate_with_existing(mtl_events)
        
        if unique_events:
            # Afficher un aperçu
            print(f"\n📋 Aperçu des 5 premiers:")
            for e in unique_events[:5]:
                print(f"  📅 {e['date']} | {e['title'][:60]}")
                print(f"     📍 {e['location'][:60]}")
                print(f"     🏷️ {e['categories']}")
                print(f"     🔗 {e['source_url'][:80]}")
                print()
            
            # Confirmer avant import
            print(f"\n{'=' * 40}")
            print(f"PRÊT À IMPORTER: {len(unique_events)} événements")
            print(f"{'=' * 40}")
            
            confirm = input("Importer ? (o/n): ").strip().lower()
            if confirm == 'o':
                import_events(unique_events, "Montréal Open Data")
            else:
                print("Import annulé.")
        else:
            print("\nAucun nouvel événement à importer.")
    
    print("\n✅ Terminé!")
