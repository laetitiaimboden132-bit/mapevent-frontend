"""
Nettoyage légal: suppression des events de sites à risque.
1. SUPPRIMER TOUT: tempslibre.ch, haute-savoie-tourisme.org, morges.ch
2. GARDER 30%: valais.ch, geneve.ch
"""
import requests, sys, io, json, random
from urllib.parse import urlparse

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Récupérer tous les events
print("=== ÉTAPE 0: Récupération de tous les events ===")
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])
print(f"Total events actuels: {len(events)}")

# Classer par source
by_source = {}
for ev in events:
    src = ev.get('source_url', '') or ''
    domain = urlparse(src).netloc if src else 'SANS_SOURCE'
    if domain not in by_source:
        by_source[domain] = []
    by_source[domain].append(ev)

print(f"\nDistribution actuelle:")
for domain, evts in sorted(by_source.items(), key=lambda x: -len(x[1])):
    print(f"  {domain}: {len(evts)}")

# ======================================================
# ÉTAPE 1: Supprimer TOUT de tempslibre.ch, haute-savoie-tourisme.org, morges.ch
# ======================================================
print("\n=== ÉTAPE 1: Suppression totale - sites DANGER CRITIQUE ===")

delete_all_domains = [
    'www.tempslibre.ch',
    'www.haute-savoie-tourisme.org',
    'haute-savoie-tourisme.org',
    'www.morges.ch',
    'morges.ch',
    'tempslibre.ch',
]

ids_to_delete_step1 = []
for ev in events:
    src = ev.get('source_url', '') or ''
    domain = urlparse(src).netloc if src else ''
    if domain in delete_all_domains:
        ids_to_delete_step1.append(ev['id'])

print(f"Events à supprimer (sites danger critique): {len(ids_to_delete_step1)}")

# ======================================================
# ÉTAPE 2: Garder 30% de valais.ch et geneve.ch
# ======================================================
print("\n=== ÉTAPE 2: Réduction à 30% - sites RISQUE ÉLEVÉ ===")

reduce_domains = {
    'www.valais.ch': 0.30,
    'valais.ch': 0.30,
    'www.geneve.ch': 0.30,
    'geneve.ch': 0.30,
}

ids_to_delete_step2 = []

for domain_key in ['www.valais.ch', 'www.geneve.ch']:
    domain_events = by_source.get(domain_key, [])
    # Aussi checker sans www
    alt_key = domain_key.replace('www.', '')
    domain_events += by_source.get(alt_key, [])
    
    if not domain_events:
        continue
    
    total = len(domain_events)
    keep_count = max(1, round(total * 0.30))
    delete_count = total - keep_count
    
    # Garder les events avec les meilleures données (description longue, location précise)
    def quality_score(ev):
        score = 0
        desc = ev.get('description', '') or ''
        loc = ev.get('location', '') or ''
        if len(desc) > 100:
            score += 2
        if len(desc) > 50:
            score += 1
        if ',' in loc and len(loc) > 20:
            score += 2
        if ev.get('latitude') and ev.get('longitude'):
            score += 1
        return score
    
    # Trier par qualité (meilleurs en premier)
    domain_events.sort(key=quality_score, reverse=True)
    
    events_to_keep = domain_events[:keep_count]
    events_to_delete = domain_events[keep_count:]
    
    print(f"\n  {domain_key}: {total} total → garder {keep_count}, supprimer {delete_count}")
    print(f"  Events gardés:")
    for ev in events_to_keep:
        print(f"    - {ev.get('title', '?')[:60]}")
    
    for ev in events_to_delete:
        ids_to_delete_step2.append(ev['id'])

# ======================================================
# RÉSUMÉ et EXÉCUTION
# ======================================================
all_ids_to_delete = ids_to_delete_step1 + ids_to_delete_step2
print(f"\n=== RÉSUMÉ ===")
print(f"Suppression sites danger critique: {len(ids_to_delete_step1)}")
print(f"Suppression réduction 30%: {len(ids_to_delete_step2)}")
print(f"TOTAL à supprimer: {len(all_ids_to_delete)}")
print(f"Events restants après nettoyage: {len(events) - len(all_ids_to_delete)}")

# Supprimer par lots de 25
print(f"\n=== EXÉCUTION DES SUPPRESSIONS ===")
deleted = 0
for i in range(0, len(all_ids_to_delete), 25):
    batch = all_ids_to_delete[i:i+25]
    try:
        resp = requests.post(f'{API_URL}/api/events/delete-by-ids', json={'ids': batch}, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            batch_deleted = result.get('deleted', len(batch))
            deleted += batch_deleted
            print(f"  Lot {i//25 + 1}: {batch_deleted} supprimés")
        else:
            print(f"  Lot {i//25 + 1}: ERREUR {resp.status_code} - {resp.text[:200]}")
    except Exception as e:
        print(f"  Lot {i//25 + 1}: EXCEPTION - {e}")

print(f"\n=== RÉSULTAT FINAL ===")
print(f"Total supprimés: {deleted}")
print(f"Events restants estimé: {len(events) - deleted}")

# Vérification finale
print(f"\n=== VÉRIFICATION ===")
r2 = requests.get(f'{API_URL}/api/events', timeout=30)
data2 = r2.json()
events2 = data2 if isinstance(data2, list) else data2.get('events', [])
print(f"Total events confirmé: {len(events2)}")

# Distribution après nettoyage
sources2 = {}
for ev in events2:
    src = ev.get('source_url', '') or ''
    domain = urlparse(src).netloc if src else 'SANS_SOURCE'
    sources2[domain] = sources2.get(domain, 0) + 1

print(f"\nDistribution après nettoyage:")
for domain, count in sorted(sources2.items(), key=lambda x: -x[1]):
    print(f"  {domain}: {count}")
