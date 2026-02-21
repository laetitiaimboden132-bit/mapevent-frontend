"""
Import propre des events morges.ch avec format correct.
Filtre: seulement les events intéressants (pas "boxe éducative" ni "bibliothèque").
Time: NULL au lieu de --:--
"""
import requests, sys, io, json

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Charger les events scrapés
with open('scraped_new_sources.json', 'r', encoding='utf-8') as f:
    events = json.load(f)

print(f"Events scrapés: {len(events)}")

# Filtrer: garder seulement morges.ch et les events de qualité
# Exclure les petites activités communautaires peu intéressantes
skip_keywords = ['boxe éducative', 'cours de danse', 'jeux à la bibliothèque', 'pages les plus visitées']

good_events = []
for ev in events:
    title_lower = ev['title'].lower()
    
    # Skip montreux "Pages les plus visitées" - c'est pas un event
    if 'pages les plus visitées' in title_lower:
        print(f"  SKIP (pas un event): {ev['title']}")
        continue
    
    # Skip petites activités
    if any(kw in title_lower for kw in skip_keywords):
        print(f"  SKIP (petite activité): {ev['title']}")
        continue
    
    # Corriger le format time (NULL au lieu de --:--)
    ev['time'] = None
    ev['end_time'] = None
    
    # Utiliser 'date' au lieu de 'start_date' pour le backend
    if 'start_date' in ev:
        ev['date'] = ev.pop('start_date')
    if 'start_time' in ev:
        ev.pop('start_time')
    
    good_events.append(ev)
    print(f"  OK: {ev['title']} | {ev['date']} | {ev['location']}")

print(f"\nEvents à importer: {len(good_events)}")

if good_events:
    # Import
    payload = {'events': good_events}
    resp = requests.post(f'{API_URL}/api/events/scraped/batch', json=payload, timeout=30)
    result = resp.json()
    print(f"\nRésultat import: {json.dumps(result, indent=2)}")
else:
    print("\nAucun event de qualité à importer.")

print("\nDONE")
