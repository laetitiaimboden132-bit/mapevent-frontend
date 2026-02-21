"""
État actuel: combien d'events, quelles sources, quels problèmes restants.
"""
import requests, sys, io, json, re
from urllib.parse import urlparse

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])

print(f"TOTAL EVENTS: {len(events)}")

# Par région
regions = {'Valais': 0, 'Vaud': 0, 'Genève': 0, 'Autre': 0}
for ev in events:
    loc = (ev.get('location', '') or '').lower()
    if any(x in loc for x in ['valais', 'sion', 'sierre', 'martigny', 'monthey', 'visp', 'brig', 'nendaz', 'zermatt', 'verbier', 'crans-montana', 'leukerbad', 'champéry', 'gryon', 'st-pierre-de-clages', 'conthey', 'saillon', 'riddes', 'troistorrents', 'saint-maurice', 'le châble', 'wiler']):
        regions['Valais'] += 1
    elif any(x in loc for x in ['genève', 'carouge', 'cologny', 'lancy', 'vernier', 'meyrin']):
        regions['Genève'] += 1
    elif any(x in loc for x in ['vaud', 'lausanne', 'morges', 'nyon', 'montreux', 'vevey', 'aigle', 'yverdon', 'payerne', 'pully', 'prilly', 'etoy', 'villars', 'château-d\'oex', 'cully', 'prangins', 'lavey', 'la tour-de-peilz', 'le brassus', 'fribourg', 'rossinière', 'veytaux', 'puidoux']):
        regions['Vaud'] += 1
    else:
        regions['Autre'] += 1

print(f"\nPar région:")
for r, c in regions.items():
    print(f"  {r}: {c}")

# Par source
sources = {}
for ev in events:
    src = ev.get('source_url', '') or ''
    domain = urlparse(src).netloc if src else 'SANS_SOURCE'
    sources[domain] = sources.get(domain, 0) + 1

print(f"\nPar source ({len(sources)}):")
for domain, count in sorted(sources.items(), key=lambda x: -x[1]):
    pct = count / len(events) * 100
    print(f"  {domain}: {count} ({pct:.1f}%)")

# Events avec problèmes
problems = 0
for ev in events:
    loc = ev.get('location', '') or ''
    date = ev.get('date', '') or ''
    lat = ev.get('latitude', 0) or 0
    lon = ev.get('longitude', 0) or 0
    
    if not loc or len(loc) < 5:
        problems += 1
    elif lat == 0 or lon == 0:
        problems += 1
    elif not date:
        problems += 1

print(f"\nProblèmes: {problems}/{len(events)}")
print(f"Score: {round((1 - problems/len(events)) * 100)}%")
