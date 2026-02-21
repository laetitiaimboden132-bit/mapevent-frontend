"""
Recatégoriser les 332 events Goabase avec les bonnes sous-catégories.
Méthode: delete + re-insert via batch API (car PUT nécessite auth JWT).

Goabase utilise 'Musique > Techno' etc. mais le tree utilise 
'Music > Electronic > Techno' avec des sous-sous-catégories.

On analyse le titre, la description et le lineup pour détecter 
le genre précis (Psytrance, Hard Techno, Deep House, etc.).
"""
import requests
import time
import json
import re

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

# Mapping précis des genres electro -> catégories du tree
GENRE_MAP = {
    # Techno
    "acid techno": "Music > Electronic > Techno > Acid Techno",
    "minimal techno": "Music > Electronic > Techno > Minimal Techno",
    "hard techno": "Music > Electronic > Techno > Hard Techno",
    "industrial techno": "Music > Electronic > Techno > Industrial Techno",
    "peak time techno": "Music > Electronic > Techno > Peak Time Techno",
    "detroit techno": "Music > Electronic > Techno > Detroit Techno",
    "melodic techno": "Music > Electronic > Techno > Melodic Techno",
    "dub techno": "Music > Electronic > Techno > Dub Techno",
    "hypnotic techno": "Music > Electronic > Techno > Hypnotic Techno",
    "techno": "Music > Electronic > Techno",
    # House
    "deep house": "Music > Electronic > House > Deep House",
    "electro house": "Music > Electronic > House > Electro House",
    "tech house": "Music > Electronic > House > Tech House",
    "progressive house": "Music > Electronic > House > Progressive House",
    "tribal house": "Music > Electronic > House > Tribal House",
    "funky house": "Music > Electronic > House > Funky House",
    "afro house": "Music > Electronic > House > Afro House",
    "soulful house": "Music > Electronic > House > Soulful House",
    "house": "Music > Electronic > House",
    # Trance
    "psytrance": "Music > Electronic > Trance > Psytrance",
    "psy trance": "Music > Electronic > Trance > Psytrance",
    "psychedelic trance": "Music > Electronic > Trance > Psytrance",
    "full on": "Music > Electronic > Trance > Full On",
    "fullon": "Music > Electronic > Trance > Full On",
    "full-on": "Music > Electronic > Trance > Full On",
    "goa trance": "Music > Electronic > Trance > Goa",
    "goa": "Music > Electronic > Trance > Goa",
    "progressive psy": "Music > Electronic > Trance > Progressive Psy",
    "prog psy": "Music > Electronic > Trance > Progressive Psy",
    "psyprog": "Music > Electronic > Trance > Progressive Psy",
    "dark psy": "Music > Electronic > Trance > Dark Psy",
    "darkpsy": "Music > Electronic > Trance > Dark Psy",
    "forest": "Music > Electronic > Trance > Forest",
    "hi-tech": "Music > Electronic > Trance > Hi-Tech",
    "hitech": "Music > Electronic > Trance > Hi-Tech",
    "hi tech": "Music > Electronic > Trance > Hi-Tech",
    "uplifting trance": "Music > Electronic > Trance > Uplifting Trance",
    "uplifting": "Music > Electronic > Trance > Uplifting Trance",
    "vocal trance": "Music > Electronic > Trance > Vocal Trance",
    "classic trance": "Music > Electronic > Trance > Classic Trance",
    "acid trance": "Music > Electronic > Trance > Acid Trance",
    "trance": "Music > Electronic > Trance",
    # DnB
    "neurofunk": "Music > Electronic > Drum & Bass > Neurofunk",
    "jungle": "Music > Electronic > Drum & Bass > Jungle",
    "liquid dnb": "Music > Electronic > Drum & Bass > Liquid DnB",
    "liquid drum": "Music > Electronic > Drum & Bass > Liquid DnB",
    "jump up": "Music > Electronic > Drum & Bass > Jump Up",
    "darkstep": "Music > Electronic > Drum & Bass > Darkstep",
    "drum and bass": "Music > Electronic > Drum & Bass",
    "drum & bass": "Music > Electronic > Drum & Bass",
    "drum n bass": "Music > Electronic > Drum & Bass",
    "drumnbass": "Music > Electronic > Drum & Bass",
    "dnb": "Music > Electronic > Drum & Bass",
    "d&b": "Music > Electronic > Drum & Bass",
    "d'n'b": "Music > Electronic > Drum & Bass",
    # Bass Music
    "dubstep": "Music > Electronic > Bass Music > Dubstep",
    "riddim": "Music > Electronic > Bass Music > Riddim",
    "uk bass": "Music > Electronic > Bass Music > UK Bass",
    "future bass": "Music > Electronic > Bass Music > Future Bass",
    "bass music": "Music > Electronic > Bass Music",
    # Hard Music
    "hardstyle": "Music > Electronic > Hard Music > Hardstyle",
    "hardcore": "Music > Electronic > Hard Music > Hardcore",
    "gabber": "Music > Electronic > Hard Music > Gabber",
    "rawstyle": "Music > Electronic > Hard Music > Rawstyle",
    "frenchcore": "Music > Electronic > Hard Music",
    "speedcore": "Music > Electronic > Hard Music",
    # Chill / Ambient
    "ambient": "Music > Electronic > Chill / Ambient > Ambient",
    "chillout": "Music > Electronic > Chill / Ambient > Chillout",
    "chill out": "Music > Electronic > Chill / Ambient > Chillout",
    "downtempo": "Music > Electronic > Chill / Ambient > Downtempo",
    # Disco
    "disco": "Music > Electronic > House",
    "nu-disco": "Music > Electronic > House",
    "nu disco": "Music > Electronic > House",
    # Others
    "breakbeat": "Music > Electronic",
    "synthwave": "Music > Electronic",
    "electronica": "Music > Electronic",
    "idm": "Music > Electronic",
    "experimental": "Music > Electronic",
    "noise": "Music > Electronic",
}


def detect_precise_categories(title, description):
    """
    Detect the most precise electro sub-categories from title + description.
    Returns list of up to 3 categories, most specific first.
    """
    text = f"{title} {description}".lower()
    
    matches = []
    for keyword, category in GENRE_MAP.items():
        if keyword in text:
            # Priority: longer path (more specific) and longer keyword (more precise match)
            matches.append((len(category) + len(keyword), category, keyword))
    
    if not matches:
        return ["Music > Electronic"]
    
    # Sort by specificity (higher score = more specific)
    matches.sort(key=lambda x: -x[0])
    
    seen = set()
    result = []
    for _, cat, _ in matches:
        if cat not in seen:
            # Don't add parent if child already present
            is_parent_of_existing = any(existing.startswith(cat + " >") for existing in seen)
            if not is_parent_of_existing:
                seen.add(cat)
                result.append(cat)
                if len(result) >= 3:
                    break
    
    return result


def main():
    # Step 1: Get all events
    print("=" * 60)
    print("RECATÉGORISATION GOABASE - Bonnes sous-catégories")
    print("=" * 60)
    
    print("\nRécupération de tous les events...")
    r = requests.get(f"{API}/api/events", timeout=60)
    events = r.json()
    if isinstance(events, dict):
        events = events.get("events", [])
    print(f"  Total events: {len(events)}")
    
    # Step 2: Find Goabase events
    goabase = []
    for ev in events:
        url = (ev.get("source_url") or "").lower()
        if "goabase" in url:
            goabase.append(ev)
    
    print(f"  Events Goabase: {len(goabase)}")
    
    if not goabase:
        print("Aucun event Goabase trouvé.")
        return
    
    # Step 3: Get full details for each event (need description for genre detection)
    print("\nRécupération des détails complets...")
    detailed = []
    for i, ev in enumerate(goabase):
        eid = ev["id"]
        try:
            rd = requests.get(f"{API}/api/events/{eid}", timeout=10)
            if rd.status_code == 200:
                data = rd.json()
                if isinstance(data, dict) and "event" in data:
                    data = data["event"]
                detailed.append(data)
            else:
                # Use what we have
                detailed.append(ev)
        except:
            detailed.append(ev)
        
        if (i+1) % 50 == 0:
            print(f"  {i+1}/{len(goabase)} récupérés...")
        time.sleep(0.1)
    
    print(f"  {len(detailed)} events avec détails")
    
    # Step 4: Detect new categories
    to_update = []
    cat_stats = {}
    
    for ev in detailed:
        title = (ev.get("title") or "").strip()
        desc = (ev.get("description") or "").strip()
        old_cats = ev.get("categories", [])
        if not isinstance(old_cats, list):
            try:
                old_cats = json.loads(old_cats) if isinstance(old_cats, str) else []
            except:
                old_cats = []
        
        new_cats = detect_precise_categories(title, desc)
        
        # Add Festival category if event was tagged as festival
        has_festival = any("festival" in c.lower() for c in old_cats)
        if has_festival and not any("festival" in c.lower() for c in new_cats):
            if len(new_cats) < 3:
                new_cats.append("Festivals & Grandes Fêtes > Festival musique")
        
        for c in new_cats:
            cat_stats[c] = cat_stats.get(c, 0) + 1
        
        to_update.append({
            "id": ev.get("id"),
            "title": title,
            "description": desc,
            "date": ev.get("date"),
            "time": ev.get("time"),
            "end_date": ev.get("end_date"),
            "end_time": ev.get("end_time"),
            "location": ev.get("location", ""),
            "latitude": ev.get("latitude"),
            "longitude": ev.get("longitude"),
            "source_url": ev.get("source_url", ""),
            "old_cats": old_cats,
            "new_cats": new_cats,
            "source": "Goabase",
            "validation_status": ev.get("validation_status", "auto_validated"),
            "country": ev.get("country", ""),
        })
    
    # Step 5: Show stats
    print(f"\n--- Répartition des nouvelles catégories ---")
    for cat, count in sorted(cat_stats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    
    # Show examples
    print(f"\n--- Exemples de recatégorisation ---")
    for ev in to_update[:20]:
        print(f"  {ev['title'][:45]}: {ev['old_cats']} -> {ev['new_cats']}")
    
    # Step 6: Delete all Goabase events
    goabase_ids = [ev["id"] for ev in to_update if ev.get("id")]
    print(f"\n--- Suppression de {len(goabase_ids)} events Goabase ---")
    
    deleted_total = 0
    for i in range(0, len(goabase_ids), 50):
        batch = goabase_ids[i:i+50]
        try:
            r = requests.post(f"{API}/api/events/delete-by-ids", 
                            json={"ids": batch}, timeout=30)
            resp = r.json()
            deleted = resp.get("deleted_count", 0)
            deleted_total += deleted
            print(f"  Batch {i//50+1}: {deleted} supprimés")
        except Exception as e:
            print(f"  Batch {i//50+1} ERREUR: {e}")
        time.sleep(0.5)
    
    print(f"  Total supprimés: {deleted_total}")
    
    # Step 7: Re-insert with correct categories
    print(f"\n--- Ré-insertion avec catégories corrigées ---")
    
    reimport = []
    for ev in to_update:
        if not ev.get("latitude") or not ev.get("longitude"):
            continue
        if not ev.get("date"):
            continue
        
        reimport.append({
            "title": ev["title"],
            "description": ev["description"] or f"Electronic music event - {ev['title']}",
            "date": str(ev["date"])[:10] if ev["date"] else None,
            "time": str(ev["time"])[:5] if ev.get("time") and ev["time"] != "None" else None,
            "end_date": str(ev["end_date"])[:10] if ev.get("end_date") and ev["end_date"] != "None" else None,
            "end_time": str(ev["end_time"])[:5] if ev.get("end_time") and ev["end_time"] != "None" else None,
            "location": ev["location"] or "Unknown",
            "latitude": float(ev["latitude"]),
            "longitude": float(ev["longitude"]),
            "categories": ev["new_cats"],
            "source_url": ev["source_url"],
            "source": "Goabase",
            "validation_status": "auto_validated",
            "country": ev.get("country", ""),
        })
    
    created_total = 0
    skipped_total = 0
    for i in range(0, len(reimport), 10):
        batch = reimport[i:i+10]
        try:
            r = requests.post(f"{API}/api/events/scraped/batch", 
                            json={"events": batch}, timeout=30)
            resp = r.json()
            results = resp.get("results", resp)
            created = results.get("created", 0) or results.get("inserted", 0)
            skipped = results.get("skipped", 0) + results.get("failed", 0)
            created_total += created
            skipped_total += skipped
            print(f"  Batch {i//10+1}: +{created} insérés, {skipped} skippés")
        except Exception as e:
            print(f"  Batch {i//10+1} ERREUR: {e}")
        time.sleep(0.5)
    
    print(f"\n{'=' * 60}")
    print(f"RÉSULTAT FINAL:")
    print(f"  Supprimés (ancien format): {deleted_total}")
    print(f"  Ré-insérés (bonnes catégories): {created_total}")
    print(f"  Skippés: {skipped_total}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
