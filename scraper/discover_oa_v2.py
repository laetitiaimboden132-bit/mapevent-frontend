"""
Discover active OpenAgenda agendas v2.
1. Collect agenda slugs from search (without sort)
2. Check each one for upcoming events
3. Build list of active agendas
"""
import requests
import json
import time

HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}
SEARCH_URL = "https://openagenda.com/api/agendas"
EVENTS_URL = "https://openagenda.com/api/agendas/slug/{slug}/events"


def search_agendas(query, size=50, offset=0):
    """Search for agendas without sort."""
    try:
        r = requests.get(SEARCH_URL, params={
            "search": query,
            "size": size,
            "from": offset,
        }, timeout=15, headers=HEADERS)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None


def count_upcoming(slug):
    """Quickly check if agenda has upcoming events."""
    try:
        url = EVENTS_URL.format(slug=slug)
        r = requests.get(url, params={
            "size": 0,
            "relative[]": ["current", "upcoming"]
        }, timeout=8, headers=HEADERS)
        if r.status_code == 200:
            return r.json().get("total", 0)
    except:
        pass
    return 0


# Phase 1: Collect unique agenda slugs
queries = [
    # Countries/Regions
    "france", "suisse", "belgique", "quebec",
    # French cities
    "paris", "lyon", "marseille", "toulouse", "bordeaux",
    "nice", "nantes", "lille", "strasbourg", "montpellier",
    "rennes", "rouen", "grenoble", "dijon", "angers",
    "tours", "reims", "clermont-ferrand", "orleans", "metz",
    "caen", "brest", "limoges", "amiens", "perpignan",
    "besancon", "poitiers", "avignon",
    # Swiss cities
    "geneve", "lausanne", "zurich", "bern", "bale",
    "neuchatel", "sion", "fribourg",
    # Belgian cities
    "bruxelles", "liege", "namur", "charleroi", "mons",
    # Types
    "mairie", "ville", "commune", "metropole",
    "musee", "theatre", "cinema", "galerie",
    "festival", "concert", "spectacle",
    "bibliotheque", "universite",
    "culture", "tourisme", "office",
    "sport", "association",
    # Regions
    "ile-de-france", "bretagne", "normandie", "provence",
    "occitanie", "auvergne", "aquitaine", "rhone-alpes",
    "pays loire", "grand est",
]

all_slugs = {}  # slug -> title

print("=" * 60)
print("PHASE 1: Collecte des agendas")
print("=" * 60)

for q in queries:
    result = search_agendas(q, size=50)
    if not result:
        continue
    
    total = result.get("total", 0)
    agendas = result.get("agendas", [])
    new = 0
    
    for ag in agendas:
        slug = ag.get("slug", "")
        if slug and slug not in all_slugs:
            all_slugs[slug] = ag.get("title", "?")
            new += 1
    
    if new > 0:
        print(f"  '{q}': +{new} ({len(all_slugs)} total)")
    
    # Also fetch page 2 if lots of results
    if total > 50:
        result2 = search_agendas(q, size=50, offset=50)
        if result2:
            for ag in result2.get("agendas", []):
                slug = ag.get("slug", "")
                if slug and slug not in all_slugs:
                    all_slugs[slug] = ag.get("title", "?")
        time.sleep(0.2)
    
    time.sleep(0.2)

print(f"\nTotal: {len(all_slugs)} agendas uniques")

# Phase 2: Check which ones have events
print(f"\n{'=' * 60}")
print("PHASE 2: Vérification des events")
print("=" * 60)

active = []
checked = 0
batch_size = 20

slugs_list = list(all_slugs.keys())

for i in range(0, len(slugs_list), batch_size):
    batch = slugs_list[i:i+batch_size]
    
    for slug in batch:
        n = count_upcoming(slug)
        checked += 1
        if n > 0:
            active.append({"slug": slug, "title": all_slugs[slug], "events": n})
            print(f"  ✓ {slug}: {all_slugs[slug][:45]} ({n} events)")
    
    # Progress every 100
    if checked % 100 == 0:
        print(f"  ... {checked}/{len(slugs_list)} vérifiés, {len(active)} actifs")
    
    time.sleep(0.3)

# Sort by events count
active.sort(key=lambda a: a["events"], reverse=True)

print(f"\n{'=' * 60}")
print(f"RÉSULTAT: {len(active)} agendas actifs / {checked} vérifiés")
total_events = sum(a["events"] for a in active)
print(f"Total events potentiels: {total_events}")
print(f"\nTop 50:")
for a in active[:50]:
    print(f"  {a['slug']}: {a['title'][:50]} ({a['events']})")

# Save
with open("oa_active_agendas.json", "w", encoding="utf-8") as f:
    json.dump(active, f, ensure_ascii=False, indent=2)
print(f"\nSauvegardé: oa_active_agendas.json")
