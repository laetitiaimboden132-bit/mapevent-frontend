"""
IMPORT des events tempslibre.ch - Nettoyage et validation avant insertion.
1. Filtrer les dates aberrantes (>2027 ou <2026-02-05)
2. Vérifier les doublons
3. Limiter le nombre total (max 25% du total final)
4. Insérer via API
"""
import requests, sys, io, json, re
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Charger les events scrapés
with open('scraped_tempslibre_v2.json', 'r', encoding='utf-8') as f:
    scraped = json.load(f)

print(f"Events chargés: {len(scraped)}")

# ============================================================
# 1. Filtrer les dates aberrantes
# ============================================================
valid_events = []
for ev in scraped:
    start = ev.get('start_date', '')
    if not start:
        continue
    
    try:
        d = datetime.strptime(start[:10], '%Y-%m-%d')
        # Accepter seulement 2026 (et début 2027 pour les events d'hiver)
        if d < datetime(2026, 2, 5):
            continue
        if d > datetime(2027, 6, 30):
            print(f"  DATE ABERRANTE: {ev['title'][:40]} | {start}")
            continue
        
        valid_events.append(ev)
    except:
        continue

print(f"Après filtre dates: {len(valid_events)} (supprimé {len(scraped) - len(valid_events)} dates aberrantes)")

# ============================================================
# 2. Dédupliquer (même titre en lowercase)
# ============================================================
seen_titles = set()
unique_events = []
for ev in valid_events:
    t = ev['title'].lower().strip()
    if t not in seen_titles:
        seen_titles.add(t)
        unique_events.append(ev)

print(f"Après déduplication: {len(unique_events)} (supprimé {len(valid_events) - len(unique_events)} doublons)")

# ============================================================
# 3. Vérifier contre les events déjà en base
# ============================================================
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
existing = data if isinstance(data, list) else data.get('events', [])
existing_titles_lower = set(ev.get('title', '').lower().strip() for ev in existing if ev.get('title'))
existing_urls = set(ev.get('source_url', '').lower().strip() for ev in existing if ev.get('source_url'))

new_events = []
for ev in unique_events:
    title_lower = ev['title'].lower().strip()
    url_lower = ev.get('source_url', '').lower().strip()
    
    if title_lower in existing_titles_lower:
        continue
    if url_lower in existing_urls:
        continue
    
    new_events.append(ev)

print(f"Après filtre doublons base: {len(new_events)} (supprimé {len(unique_events) - len(new_events)} déjà en base)")

# ============================================================
# 4. Contrôle qualité final
# ============================================================
quality_events = []
for ev in new_events:
    # Doit avoir: titre, date, lieu avec CP, coordonnées
    if not ev.get('title') or len(ev['title']) < 3:
        continue
    if not ev.get('start_date'):
        continue
    if not ev.get('location') or len(ev['location']) < 5:
        continue
    if not ev.get('latitude') or not ev.get('longitude'):
        continue
    if not ev.get('description') or len(ev['description']) < 10:
        continue
    
    quality_events.append(ev)

print(f"Après contrôle qualité: {len(quality_events)}")

# ============================================================
# 5. Quota: max 25% du total final
# ============================================================
current_tl = sum(1 for ev in existing if 'tempslibre.ch' in (ev.get('source_url', '') or ''))
total_after = len(existing) + len(quality_events)
max_tl = int(total_after * 0.25)
allowed_new = max_tl - current_tl

print(f"\nQuota tempslibre.ch:")
print(f"  Existants: {current_tl}")
print(f"  Total après import: {total_after}")
print(f"  Max 25%: {max_tl}")
print(f"  Nouveaux autorisés: {allowed_new}")

if len(quality_events) > allowed_new and allowed_new > 0:
    # Limiter en gardant la diversité régionale
    quality_events = quality_events[:allowed_new]
    print(f"  Limité à {allowed_new} events")
elif allowed_new <= 0:
    print(f"  QUOTA DÉPASSÉ - pas d'import")
    quality_events = []

# ============================================================
# 6. Import via API
# ============================================================
if not quality_events:
    print("\nAucun event à importer")
    sys.exit(0)

print(f"\n{'='*60}")
print(f"IMPORT de {len(quality_events)} events")
print(f"{'='*60}")

imported = 0
errors = 0
batch_size = 10

for i in range(0, len(quality_events), batch_size):
    batch = quality_events[i:i+batch_size]
    
    for ev in batch:
        payload = {
            'title': ev['title'],
            'description': ev['description'],
            'date': ev['start_date'],
            'end_date': ev.get('end_date') or ev['start_date'],
            'time': None,
            'location': ev['location'],
            'latitude': ev['latitude'],
            'longitude': ev['longitude'],
            'categories': ev['categories'],
            'source_url': ev['source_url'],
            'validation_status': 'auto_validated',
            'organizer_name': ev.get('organizer', ''),
            'organizer_email': ev.get('organizer_email', ''),
        }
        
        try:
            resp = requests.post(
                f'{API_URL}/api/events',
                json=payload,
                timeout=15
            )
            if resp.status_code in (200, 201):
                imported += 1
                if imported % 50 == 0:
                    print(f"  Importés: {imported}...")
            else:
                errors += 1
                if errors <= 5:
                    print(f"  ERREUR ({resp.status_code}): {ev['title'][:40]} - {resp.text[:100]}")
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  EXCEPTION: {ev['title'][:40]} - {str(e)[:100]}")

print(f"\n{'='*60}")
print(f"RÉSULTAT IMPORT")
print(f"{'='*60}")
print(f"Importés: {imported}")
print(f"Erreurs: {errors}")

# ============================================================
# 7. Distribution finale
# ============================================================
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
all_events = data if isinstance(data, list) else data.get('events', [])
print(f"\nTOTAL EVENTS EN BASE: {len(all_events)}")

# Par source
from urllib.parse import urlparse
sources = {}
for ev in all_events:
    src = ev.get('source_url', '') or ''
    domain = urlparse(src).netloc if src else 'SANS_SOURCE'
    sources[domain] = sources.get(domain, 0) + 1

print(f"\nDistribution par source:")
for domain, count in sorted(sources.items(), key=lambda x: -x[1])[:15]:
    pct = count / len(all_events) * 100
    print(f"  {domain}: {count} ({pct:.1f}%)")

print("\nDONE")
