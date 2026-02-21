"""
Recatégoriser TOUS les events electro qui utilisent l'ancien format de catégories.
Formats à corriger:
- 'Musique > Electronic' -> 'Music > Electronic'
- 'Musique > Électronique' -> 'Music > Electronic'
- 'Musique > Techno' -> 'Music > Electronic > Techno'
- 'Musique > House' -> 'Music > Electronic > House'
- 'Musique > Trance' -> 'Music > Electronic > Trance'
- 'Musique > Electro' -> 'Music > Electronic'
- 'Musique > Dub' -> 'Music > Electronic'
- 'Musique > Musique electronique' -> 'Music > Electronic'
- 'Technologie' -> SUPPRIMER (faux positif!)

Méthode: delete + re-insert via batch API.
SANS toucher aux events Goabase (déjà recatégorisés).
"""
import requests
import time
import json
import re

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

# Mapping ancien format -> nouveau format
OLD_TO_NEW = {
    "Musique > Electronic": "Music > Electronic",
    "Musique > Électronique": "Music > Electronic",
    "Musique > Electro": "Music > Electronic",
    "Musique > Musique electronique": "Music > Electronic",
    "Musique > Techno": "Music > Electronic > Techno",
    "Musique > Musique electronique > Techno": "Music > Electronic > Techno",
    "Musique > House": "Music > Electronic > House",
    "Musique > Musique electronique > Deep House": "Music > Electronic > House > Deep House",
    "Musique > Trance": "Music > Electronic > Trance",
    "Musique > Dub": "Music > Electronic",
    "Musique > Drum & Bass": "Music > Electronic > Drum & Bass",
    "Électronique": "Music > Electronic",
}

# Catégories à SUPPRIMER (faux positifs)
FALSE_POSITIVE_CATS = ["Technologie"]

# Genre detection for better recategorization
GENRE_MAP = {
    "acid techno": "Music > Electronic > Techno > Acid Techno",
    "minimal techno": "Music > Electronic > Techno > Minimal Techno",
    "hard techno": "Music > Electronic > Techno > Hard Techno",
    "melodic techno": "Music > Electronic > Techno > Melodic Techno",
    "dub techno": "Music > Electronic > Techno > Dub Techno",
    "techno": "Music > Electronic > Techno",
    "deep house": "Music > Electronic > House > Deep House",
    "tech house": "Music > Electronic > House > Tech House",
    "afro house": "Music > Electronic > House > Afro House",
    "house music": "Music > Electronic > House",
    "house": "Music > Electronic > House",
    "psytrance": "Music > Electronic > Trance > Psytrance",
    "goa trance": "Music > Electronic > Trance > Goa",
    "goa": "Music > Electronic > Trance > Goa",
    "trance": "Music > Electronic > Trance",
    "drum and bass": "Music > Electronic > Drum & Bass",
    "drum & bass": "Music > Electronic > Drum & Bass",
    "dnb": "Music > Electronic > Drum & Bass",
    "dubstep": "Music > Electronic > Bass Music > Dubstep",
    "hardstyle": "Music > Electronic > Hard Music > Hardstyle",
    "hardcore": "Music > Electronic > Hard Music > Hardcore",
    "ambient": "Music > Electronic > Chill / Ambient > Ambient",
    "chillout": "Music > Electronic > Chill / Ambient > Chillout",
    "dj set": "Music > Electronic",
    "dj": "Music > Electronic",
    "electronic music": "Music > Electronic",
    "electro": "Music > Electronic",
}


def detect_better_category(title, description):
    """Try to detect a more specific electro subcategory."""
    text = f"{title} {description}".lower()
    
    matches = []
    for keyword, category in GENRE_MAP.items():
        if keyword in text:
            matches.append((len(category) + len(keyword), category))
    
    if matches:
        matches.sort(key=lambda x: -x[0])
        return matches[0][1]
    
    return None


def main():
    print("=" * 60)
    print("RECATÉGORISATION - Events electro non-Goabase")
    print("=" * 60)
    
    # Step 1: Get all events with details
    print("\nRécupération de tous les events...")
    r = requests.get(f"{API}/api/events", timeout=60)
    events = r.json()
    if isinstance(events, dict):
        events = events.get("events", [])
    print(f"  Total: {len(events)}")
    
    # Step 2: Find events with old electro categories (NOT Goabase)
    to_fix = []
    false_positives = []
    
    for ev in events:
        url = (ev.get("source_url") or "").lower()
        if "goabase" in url:
            continue  # Already fixed
        
        cats = ev.get("categories", [])
        if not isinstance(cats, list):
            continue
        
        needs_fix = False
        has_false_positive = False
        
        for c in cats:
            if c in OLD_TO_NEW:
                needs_fix = True
            if c in FALSE_POSITIVE_CATS:
                has_false_positive = True
        
        if has_false_positive:
            false_positives.append(ev)
        elif needs_fix:
            to_fix.append(ev)
    
    print(f"\n  Events avec vieilles catégories electro: {len(to_fix)}")
    print(f"  Events avec faux positifs 'Technologie': {len(false_positives)}")
    
    # Step 3: Get full details for events to fix
    print("\nRécupération des détails...")
    detailed_to_fix = []
    for i, ev in enumerate(to_fix):
        eid = ev["id"]
        try:
            rd = requests.get(f"{API}/api/events/{eid}", timeout=10)
            if rd.status_code == 200:
                data = rd.json()
                if isinstance(data, dict) and "event" in data:
                    data = data["event"]
                detailed_to_fix.append(data)
            else:
                detailed_to_fix.append(ev)
        except:
            detailed_to_fix.append(ev)
        
        if (i+1) % 30 == 0:
            print(f"  {i+1}/{len(to_fix)}...")
        time.sleep(0.1)
    
    # Step 4: Build new category mappings
    print("\nCalcul des nouvelles catégories...")
    updates = []
    
    for ev in detailed_to_fix:
        title = (ev.get("title") or "").strip()
        desc = (ev.get("description") or "").strip()
        old_cats = ev.get("categories", [])
        if isinstance(old_cats, str):
            try:
                old_cats = json.loads(old_cats)
            except:
                old_cats = [old_cats]
        
        # Map old categories to new ones
        new_cats = []
        for c in old_cats:
            if c in OLD_TO_NEW:
                mapped = OLD_TO_NEW[c]
                if mapped not in new_cats:
                    new_cats.append(mapped)
            elif c not in FALSE_POSITIVE_CATS:
                if c not in new_cats:
                    new_cats.append(c)
        
        # Try to get a more specific subcategory from title/description
        better = detect_better_category(title, desc)
        if better and better != "Music > Electronic":
            # Replace generic with specific
            if "Music > Electronic" in new_cats:
                idx = new_cats.index("Music > Electronic")
                new_cats[idx] = better
            elif len(new_cats) < 3 and better not in new_cats:
                new_cats.insert(0, better)
        
        # Deduplicate and limit to 3
        seen = set()
        final_cats = []
        for c in new_cats:
            if c not in seen:
                seen.add(c)
                final_cats.append(c)
                if len(final_cats) >= 3:
                    break
        
        if final_cats != old_cats:
            updates.append({
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
                "new_cats": final_cats,
                "validation_status": ev.get("validation_status", "auto_validated"),
                "country": ev.get("country", ""),
                "source": ev.get("source", ""),
            })
    
    print(f"\n  Events à recatégoriser: {len(updates)}")
    for ev in updates[:15]:
        print(f"    {ev['title'][:45]}: {ev['old_cats']} -> {ev['new_cats']}")
    
    if not updates:
        print("  Rien à changer!")
        return
    
    # Step 5: Delete + re-insert
    ids_to_delete = [ev["id"] for ev in updates if ev.get("id")]
    
    print(f"\n--- Suppression de {len(ids_to_delete)} events ---")
    deleted = 0
    for i in range(0, len(ids_to_delete), 50):
        batch = ids_to_delete[i:i+50]
        try:
            r = requests.post(f"{API}/api/events/delete-by-ids", 
                            json={"ids": batch}, timeout=30)
            resp = r.json()
            d = resp.get("deleted_count", 0)
            deleted += d
            print(f"  Batch {i//50+1}: {d} supprimés")
        except Exception as e:
            print(f"  Batch {i//50+1} ERREUR: {e}")
        time.sleep(0.5)
    
    print(f"  Total supprimés: {deleted}")
    
    # Re-insert
    print(f"\n--- Ré-insertion avec catégories corrigées ---")
    reimport = []
    for ev in updates:
        if not ev.get("latitude") or not ev.get("longitude"):
            continue
        if not ev.get("date"):
            continue
        
        reimport.append({
            "title": ev["title"],
            "description": ev["description"] or ev["title"],
            "date": str(ev["date"])[:10] if ev["date"] else None,
            "time": str(ev["time"])[:5] if ev.get("time") and str(ev["time"]) != "None" else None,
            "end_date": str(ev["end_date"])[:10] if ev.get("end_date") and str(ev["end_date"]) != "None" else None,
            "end_time": str(ev["end_time"])[:5] if ev.get("end_time") and str(ev["end_time"]) != "None" else None,
            "location": ev["location"] or "Unknown",
            "latitude": float(ev["latitude"]),
            "longitude": float(ev["longitude"]),
            "categories": ev["new_cats"],
            "source_url": ev["source_url"],
            "source": ev.get("source", ""),
            "validation_status": "auto_validated",
        })
    
    created = 0
    skipped = 0
    for i in range(0, len(reimport), 10):
        batch = reimport[i:i+10]
        try:
            r = requests.post(f"{API}/api/events/scraped/batch", 
                            json={"events": batch}, timeout=30)
            resp = r.json()
            results = resp.get("results", resp)
            c = results.get("created", 0) or results.get("inserted", 0)
            s = results.get("skipped", 0) + results.get("failed", 0)
            created += c
            skipped += s
            print(f"  Batch {i//10+1}: +{c} insérés, {s} skippés")
        except Exception as e:
            print(f"  Batch {i//10+1} ERREUR: {e}")
        time.sleep(0.5)
    
    # Step 6: Handle false positives (remove 'Technologie' category)
    if false_positives:
        print(f"\n--- Faux positifs 'Technologie' ({len(false_positives)}) ---")
        print("  Ces events ne sont PAS de l'electro, on les laisse tranquilles")
        print("  (ils sont catégorisés 'Technologie' = ateliers informatique)")
        for ev in false_positives[:5]:
            print(f"    {ev.get('title', '?')[:60]}")
    
    print(f"\n{'=' * 60}")
    print(f"RÉSULTAT:")
    print(f"  Supprimés: {deleted}")
    print(f"  Ré-insérés: {created}")
    print(f"  Skippés: {skipped}")
    print(f"  Faux positifs ignorés: {len(false_positives)}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
