"""
Discover active OpenAgenda agendas with upcoming events.
Uses the internal API (no API key needed).
"""
import requests
import json
import time

HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}
SEARCH_URL = "https://openagenda.com/api/agendas"
EVENTS_URL = "https://openagenda.com/api/agendas/slug/{slug}/events"

def search_agendas(query, size=20, offset=0):
    """Search for agendas."""
    r = requests.get(SEARCH_URL, params={
        "search": query,
        "size": size,
        "from": offset,
        "sort": "eventsCount.desc"  # Try sorting by event count
    }, timeout=15, headers=HEADERS)
    if r.status_code == 200:
        return r.json()
    return None

def count_upcoming_events(slug):
    """Check how many upcoming events an agenda has."""
    url = EVENTS_URL.format(slug=slug)
    r = requests.get(url, params={
        "size": 1,
        "relative[]": ["current", "upcoming"],
        "includeFields[]": ["uid"]
    }, timeout=10, headers=HEADERS)
    if r.status_code == 200:
        data = r.json()
        return data.get("total", 0)
    return 0

# Search strategies: different keywords to find agendas across regions
search_queries = [
    # Major regions and countries
    "france", "suisse", "belgique", "paris", "lyon", "marseille",
    "toulouse", "bordeaux", "nice", "nantes", "lille", "strasbourg",
    "montpellier", "rennes", "geneve", "lausanne", "bruxelles",
    "zurich", "bern", "fribourg",
    # Types of organizations
    "ville de", "mairie", "commune", "office tourisme",
    "musee", "theatre", "bibliotheque", "festival",
    "culture", "agenda", "evenement", "sortir",
    "sport", "concert", "spectacle", "cinema",
    "universite", "association",
    # Regions
    "ile-de-france", "auvergne", "bretagne", "occitanie",
    "normandie", "provence", "aquitaine", "alsace",
    "rhone-alpes", "pays de la loire", "valais", "vaud",
]

all_agendas = {}  # slug -> info

print("=" * 60)
print("DÉCOUVERTE DES AGENDAS OPENAGENDA")
print("=" * 60)

for query in search_queries:
    result = search_agendas(query, size=50)
    if not result:
        continue
    
    agendas = result.get("agendas", [])
    total = result.get("total", 0)
    
    new_count = 0
    for ag in agendas:
        slug = ag.get("slug", "")
        if slug and slug not in all_agendas:
            all_agendas[slug] = {
                "slug": slug,
                "title": ag.get("title", "?"),
                "uid": ag.get("uid"),
                "upcoming_count": ag.get("eventsUpcomingCount", 0),
            }
            new_count += 1
    
    if new_count > 0:
        print(f"  '{query}': {total} total, {new_count} nouveaux agendas ({len(all_agendas)} total)")
    
    time.sleep(0.3)

print(f"\n{len(all_agendas)} agendas uniques découverts")

# Now check which ones actually have upcoming events
print("\nVérification des events à venir...")
active_agendas = []

# Sort by potential (use eventsUpcomingCount if available)
sorted_agendas = sorted(all_agendas.values(), 
                        key=lambda a: a.get("upcoming_count", 0), 
                        reverse=True)

checked = 0
for ag in sorted_agendas:
    if checked >= 300:  # Check max 300 agendas
        break
    
    slug = ag["slug"]
    upcoming = count_upcoming_events(slug)
    
    if upcoming > 0:
        ag["real_upcoming"] = upcoming
        active_agendas.append(ag)
        print(f"  ✓ {slug}: {ag['title'][:40]} - {upcoming} events")
    
    checked += 1
    time.sleep(0.3)

# Sort by event count
active_agendas.sort(key=lambda a: a.get("real_upcoming", 0), reverse=True)

print(f"\n{'=' * 60}")
print(f"RÉSULTAT: {len(active_agendas)} agendas actifs sur {checked} vérifiés")
total_potential = sum(a.get("real_upcoming", 0) for a in active_agendas)
print(f"Total potential events: {total_potential}")
print(f"\nTop 30 agendas:")
for ag in active_agendas[:30]:
    print(f"  {ag['slug']}: {ag['title'][:50]} ({ag['real_upcoming']} events)")

# Save results
with open("oa_active_agendas.json", "w", encoding="utf-8") as f:
    json.dump(active_agendas, f, ensure_ascii=False, indent=2)
print(f"\nSauvegardé dans oa_active_agendas.json")
