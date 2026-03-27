"""
Filter widget JSON files to keep ONLY events from verified open data sources.
Non-open-data events stay on the main MapEvent site, just removed from widgets.
"""
import json, os, sys
from urllib.parse import urlparse

DATA_DIR = r"c:\MapEventAI_NEW\frontend\public\widget-data"

OPEN_DATA_DOMAINS = {
    "openagenda.com",
    "kulturdaten.berlin",
    "linkedevents.hel.fi",
    "data.bs.ch",
    "paris.fr",
    "opendata.paris.fr",
    "metropole.nantes.fr",
    "osmcal.org",
}

MIN_EVENTS = 3

def is_open_data(src_url):
    if not src_url:
        return False
    try:
        domain = urlparse(src_url).netloc.replace("www.", "")
    except Exception:
        return False
    return any(domain == od or domain.endswith("." + od) for od in OPEN_DATA_DOMAINS)


dry_run = "--apply" not in sys.argv

if dry_run:
    print("=" * 60)
    print("  DRY-RUN  --  ajouter --apply pour appliquer")
    print("=" * 60)

removed_cities = []
filtered_cities = []

for f in sorted(os.listdir(DATA_DIR)):
    if not f.endswith(".json"):
        continue
    city = f.replace(".json", "")
    path = os.path.join(DATA_DIR, f)
    d = json.load(open(path, "r", encoding="utf-8"))
    events = d.get("events", [])
    total = len(events)

    kept = [e for e in events if is_open_data(e.get("src", ""))]
    removed = total - len(kept)

    if len(kept) < MIN_EVENTS:
        removed_cities.append((city, total, len(kept)))
        tag = "SUPPRIMER"
    elif removed > 0:
        filtered_cities.append((city, total, len(kept), removed))
        tag = f"FILTRER (-{removed})"
    else:
        tag = "OK"

    if removed > 0 or len(kept) < MIN_EVENTS:
        print(f"  {city:25s} {total:5d} -> {len(kept):5d}  {tag}")

    if not dry_run:
        if len(kept) < MIN_EVENTS:
            os.remove(path)
        elif removed > 0:
            d["events"] = kept
            with open(path, "w", encoding="utf-8") as fout:
                json.dump(d, fout, ensure_ascii=False)

print()
print(f"Villes sans changement: {60 - len(removed_cities) - len(filtered_cities)}")
print(f"Villes filtrées:        {len(filtered_cities)}")
print(f"Villes supprimées (<{MIN_EVENTS} events open data): {len(removed_cities)}")
for c, t, k in removed_cities:
    print(f"  - {c} ({t} events, {k} open data)")

if dry_run:
    print()
    print("--apply pour appliquer les changements.")
