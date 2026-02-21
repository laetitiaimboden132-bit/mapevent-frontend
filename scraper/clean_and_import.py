"""
Nettoyage strict + dedup + import des events open data.
1. Charge les events fetchés
2. Nettoie les categories (classifieur strict)
3. Verifie les doublons avec la DB existante
4. Importe par batch
"""
import requests
import json
import time
import sys
import re
from datetime import date

sys.stdout.reconfigure(line_buffering=True)

TODAY = date.today().isoformat()
API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

# 1. Charger les events
print("=" * 70)
print("CHARGEMENT DES EVENTS")
print("=" * 70)

with open("scraper/opendata_events_batch.json", "r", encoding="utf-8") as f:
    events = json.load(f)

print(f"Events charges: {len(events)}")


# 2. Charger les events existants pour dedup
print("\nChargement events existants...")
r = requests.get(f"{API}/api/events", timeout=60)
existing = r.json()
print(f"Events existants en DB: {len(existing)}")

# Index par titre normalise pour dedup
existing_titles = set()
for e in existing:
    t = re.sub(r'\s+', ' ', (e.get("title") or "").lower().strip())
    existing_titles.add(t)

# Index par source_url pour dedup
existing_urls = set()
for e in existing:
    url = (e.get("source_url") or "").strip()
    if url:
        existing_urls.add(url)

print(f"Titres existants: {len(existing_titles)}")
print(f"Source URLs existantes: {len(existing_urls)}")


# 3. Classifieur strict
def classify_strict(title, description):
    """Classifieur strict - ne classifie electro que si VRAIMENT electro"""
    text_lower = f"{title} {description}".lower()
    title_lower = title.lower()
    cats = []
    
    # --- MUSIQUE ELECTRONIQUE (strict) ---
    # Mots-cles qui sont UNIQUEMENT electroniques
    strict_electro = ["techno", "house music", "drum and bass", "drum'n'bass", "dnb",
                       "trance", "psytrance", "dubstep", "hardstyle", "hardcore techno",
                       "gabber", "acid house", "deep house", "minimal techno",
                       "progressive house", "tech house"]
    
    # Mots-cles qui sont electro DANS un contexte musical
    electro_context = ["dj set", "dj mix", "clubbing", "afterparty", "after party",
                        "rave party", "rave ", "b2b dj", "soundsystem"]
    
    # "electro" seul ne suffit pas (trop de faux positifs) - il faut "musique electro" ou "soiree electro"
    electro_phrases = ["musique electro", "soiree electro", "soirée electro", "nuit electro",
                        "festival electro", "electro party", "electro club",
                        "musique electronique", "musique électronique"]
    
    is_electro = False
    subgenre = None
    
    for kw in strict_electro:
        if kw in text_lower:
            is_electro = True
            if "techno" in kw and "minimal" in kw: subgenre = "Minimal Techno"
            elif "techno" in kw and "hardcore" not in kw: subgenre = "Techno"
            elif "deep house" in kw: subgenre = "Deep House"
            elif "tech house" in kw: subgenre = "Tech House"
            elif "house" in kw: subgenre = "House"
            elif "drum" in kw or "dnb" in kw: subgenre = "Drum and Bass"
            elif "trance" in kw: subgenre = "Trance"
            elif "psytrance" in kw: subgenre = "Psytrance"
            elif "dubstep" in kw: subgenre = "Dubstep"
            elif "hardstyle" in kw: subgenre = "Hardstyle"
            elif "acid" in kw: subgenre = "Acid House"
            break
    
    if not is_electro:
        for kw in electro_context:
            if kw in text_lower:
                is_electro = True
                break
    
    if not is_electro:
        for ph in electro_phrases:
            if ph in text_lower:
                is_electro = True
                break
    
    if is_electro:
        if subgenre:
            cats.append(f"Musique > Musique electronique > {subgenre}")
        else:
            cats.append("Musique > Musique electronique")
    
    # --- AUTRES GENRES MUSICAUX ---
    music_indicators = ["concert", "live ", "recital", "orchestre", "en concert", "showcase"]
    is_music = any(k in text_lower for k in music_indicators) or is_electro
    
    if is_music and not is_electro:
        if "jazz" in text_lower: cats.append("Musique > Jazz")
        elif re.search(r'\b(classique|symphoni|philharmon|chambre)\b', text_lower): cats.append("Musique > Classique")
        elif re.search(r'\brock\b', text_lower): cats.append("Musique > Rock")
        elif re.search(r'\b(hip.?hop|rap\b)', text_lower): cats.append("Musique > Hip-Hop / Rap")
        elif "reggae" in text_lower: cats.append("Musique > Reggae")
        elif "blues" in text_lower: cats.append("Musique > Blues")
        elif re.search(r'\b(pop|chanson|variete|variété)\b', text_lower): cats.append("Musique > Pop")
        elif re.search(r'\bmetal\b', text_lower): cats.append("Musique > Metal")
        elif re.search(r'\b(world|musiques? du monde)\b', text_lower): cats.append("Musique > World")
        elif re.search(r'\b(opera|lyrique|opéra)\b', text_lower): cats.append("Musique > Opera")
        else: cats.append("Musique > Concert")
    
    # --- FESTIVAL ---
    if re.search(r'\bfestival\b', text_lower) and not cats:
        cats.append("Festival")
    
    # --- SPECTACLE / THEATRE ---
    if re.search(r'\b(spectacle|théâtre|theatre|comédie|comedie|pièce)\b', text_lower):
        if re.search(r'\b(humour|stand.?up|humoriste|one.?man|one.?woman|comique)\b', text_lower):
            cats.append("Culture > Humour / Stand-up")
        else:
            cats.append("Culture > Theatre / Spectacle")
    
    # --- DANSE ---
    if re.search(r'\b(danse|ballet|choregraph|chorégraph)\b', text_lower) and not any("Danse" in c for c in cats):
        cats.append("Culture > Danse")
    
    # --- EXPOSITION / ART ---
    if re.search(r'\b(exposition|vernissage|galerie|art contemporain|beaux.?arts|photographie|sculpture|peinture|musée|musee)\b', text_lower):
        cats.append("Culture > Exposition / Art")
    
    # --- ENFANTS / FAMILLE ---
    if re.search(r'\b(enfant|famille|kid|jeune public|tout.?petit|maternelle|atelier.+enfant|conte|marionnette)\b', text_lower):
        cats.append("Famille / Enfants")
    
    # --- SPORT ---
    if re.search(r'\b(course|marathon|trail|sport|fitness|yoga|running|vélo|velo|cyclisme|natation|tennis|football|basket)\b', text_lower):
        cats.append("Sport")
    
    # --- GASTRONOMIE ---
    if re.search(r'\b(gastronomie|dégustation|degustation|cuisine|food|vin|bière|biere|brunch|marché.+gourmand)\b', text_lower):
        cats.append("Gastronomie")
    
    # --- CONFERENCE ---
    if re.search(r'\b(conférence|conference|débat|debat|colloque|table.?ronde|séminaire|seminaire)\b', text_lower):
        cats.append("Culture > Conference")
    
    # --- CINEMA ---
    if re.search(r'\b(cinéma|cinema|film|projection|séance|seance|avant.?première)\b', text_lower):
        cats.append("Culture > Cinema")
    
    # --- MARCHE ---
    if re.search(r'\b(brocante|vide.?grenier|puces|marché aux|marche aux)\b', text_lower):
        cats.append("Marche / Brocante")
    
    # --- ATELIER ---
    if re.search(r'\b(atelier|workshop|stage|masterclass)\b', text_lower) and not any("Famille" in c for c in cats):
        cats.append("Atelier / Workshop")
    
    # --- CARNAVAL ---
    if re.search(r'\b(carnaval|carnival|cortège|cortege|défilé|defile)\b', text_lower):
        cats.append("Fete / Carnaval")
    
    # --- CIRQUE ---
    if re.search(r'\b(cirque|acrobat|jongl)\b', text_lower):
        cats.append("Culture > Cirque")
    
    if not cats:
        cats.append("Evenement")
    
    return cats[:3]


# 4. Nettoyage + dedup + validation
print("\n" + "=" * 70)
print("NETTOYAGE + DEDUP + VALIDATION")
print("=" * 70)

clean_events = []
stats = {"total": 0, "dup_title": 0, "dup_url": 0, "no_source": 0, "bad_date": 0, "imported": 0}

for e in events:
    stats["total"] += 1
    title = e.get("title", "").strip()
    
    # Dedup par titre
    title_key = re.sub(r'\s+', ' ', title.lower().strip())
    if title_key in existing_titles:
        stats["dup_title"] += 1
        continue
    
    # Dedup par source_url
    source_url = (e.get("source_url") or "").strip()
    if source_url and source_url in existing_urls:
        stats["dup_url"] += 1
        continue
    
    # Date future obligatoire
    event_date = e.get("date", "")
    if not event_date or event_date < TODAY:
        stats["bad_date"] += 1
        continue
    
    # Source URL recommandee mais pas bloquante pour Paris (ils ont des URLs)
    if not source_url:
        stats["no_source"] += 1
        # On garde quand meme si c'est Paris OpenData car les donnees sont fiables
    
    # Reclassifier strictement
    desc = e.get("description", "")
    categories = classify_strict(title, desc)
    
    event = {
        "title": title,
        "description": desc[:500] if desc else "",
        "location": e.get("location", ""),
        "latitude": e.get("latitude"),
        "longitude": e.get("longitude"),
        "date": event_date,
        "time": e.get("time"),
        "end_date": e.get("end_date"),
        "end_time": e.get("end_time"),
        "categories": json.dumps(categories),
        "source_url": source_url,
        "validation_status": "auto_validated",
        "status": "active",
    }
    
    clean_events.append(event)
    
    # Ajouter au set pour eviter doublons internes
    existing_titles.add(title_key)
    if source_url:
        existing_urls.add(source_url)

print(f"\nStats nettoyage:")
print(f"  Total events traites: {stats['total']}")
print(f"  Doublons par titre: {stats['dup_title']}")
print(f"  Doublons par URL: {stats['dup_url']}")
print(f"  Date passee: {stats['bad_date']}")
print(f"  Sans source URL: {stats['no_source']}")
print(f"  Events propres a importer: {len(clean_events)}")

# Stats categories apres nettoyage
cat_counts = {}
electro_events = []
for e in clean_events:
    cats = json.loads(e["categories"])
    for c in cats:
        cat_counts[c] = cat_counts.get(c, 0) + 1
    if any("lectronique" in c or "Techno" in c or "House" in c or "Trance" in c or "Dubstep" in c or "Drum" in c for c in cats):
        electro_events.append(e)

print(f"\nEvents electro (classifieur strict): {len(electro_events)}")
print("\nTop 20 categories (strict):")
for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])[:20]:
    print(f"  {cat}: {count}")

print(f"\nEchantillon electro strict:")
for e in electro_events[:15]:
    print(f"  [{json.loads(e['categories'])[0]}] {e['title'][:65]}")
    print(f"    {e['date']} | {e['location'][:55]}")


# 5. Import par batch via l'API events/publish
print("\n" + "=" * 70)
print(f"IMPORT DE {len(clean_events)} EVENTS")
print("=" * 70)

BATCH_SIZE = 5
imported = 0
failed = 0
errors = []

for i in range(0, len(clean_events), BATCH_SIZE):
    batch = clean_events[i:i+BATCH_SIZE]
    
    for event in batch:
        try:
            # L'endpoint publish attend categories en JSON string dans le body
            payload = {
                "title": event["title"],
                "description": event["description"],
                "location": event["location"],
                "latitude": float(event["latitude"]),
                "longitude": float(event["longitude"]),
                "date": event["date"],
                "time": event["time"],
                "end_date": event["end_date"],
                "end_time": event["end_time"],
                "categories": json.loads(event["categories"]),
                "source_url": event["source_url"],
                "validation_status": "auto_validated",
            }
            
            r = requests.post(f"{API}/api/events/scraped/batch", json={"events": [payload]}, timeout=30)
            
            if r.status_code == 200 or r.status_code == 201:
                resp = r.json()
                inserted = resp.get("inserted", 0)
                imported += inserted
            else:
                # Essayer l'endpoint publish individuel
                r2 = requests.post(f"{API}/api/events/publish", json=payload, timeout=30)
                if r2.status_code in (200, 201):
                    imported += 1
                else:
                    failed += 1
                    if len(errors) < 5:
                        errors.append(f"{event['title'][:40]}: {r2.status_code} {r2.text[:100]}")
        except Exception as e:
            failed += 1
            if len(errors) < 5:
                errors.append(f"{event['title'][:40]}: {str(e)[:80]}")
    
    if (i // BATCH_SIZE) % 20 == 0:
        print(f"  Progress: {i+len(batch)}/{len(clean_events)} (imported: {imported}, failed: {failed})")
    
    time.sleep(0.5)

print(f"\n{'=' * 70}")
print(f"RESULTAT FINAL")
print(f"  Importes: {imported}")
print(f"  Echoues: {failed}")
if errors:
    print(f"  Premieres erreurs:")
    for err in errors:
        print(f"    {err}")

print(f"\nTotal events electro importes: {len(electro_events)}")
print("DONE!")
