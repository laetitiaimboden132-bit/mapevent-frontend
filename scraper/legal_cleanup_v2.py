"""
Nettoyage légal V2:
1. SUPPRIMER TOUT de valais.ch et geneve.ch (niveaux 1+2 restants)
2. GARDER 30% de TOUS les niveaux 3+4
"""
import requests, sys, io, json
from urllib.parse import urlparse

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Récupérer tous les events
print("=== ÉTAT ACTUEL ===")
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])
print(f"Total events actuels: {len(events)}")

# Classer par domaine source
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
# ÉTAPE 1: Supprimer TOUT de valais.ch et geneve.ch (niveau 1+2)
# ======================================================
print("\n=== ÉTAPE 1: Suppression totale valais.ch + geneve.ch (niveau 1+2) ===")

delete_all_domains = ['www.valais.ch', 'valais.ch', 'www.geneve.ch', 'geneve.ch']

ids_delete_all = []
for ev in events:
    src = ev.get('source_url', '') or ''
    domain = urlparse(src).netloc if src else ''
    if domain in delete_all_domains:
        ids_delete_all.append(ev['id'])
        
print(f"Events à supprimer (niveaux 1+2 restants): {len(ids_delete_all)}")

# ======================================================
# ÉTAPE 2: Garder 30% de TOUS les autres sites (niveaux 3+4)
# ======================================================
print("\n=== ÉTAPE 2: Réduction à 30% - tous niveaux 3+4 ===")

# On exclut les domaines déjà supprimés totalement
excluded_domains = set(delete_all_domains)

# Regrouper tous les events restants par domaine
remaining_by_source = {}
for ev in events:
    src = ev.get('source_url', '') or ''
    domain = urlparse(src).netloc if src else 'SANS_SOURCE'
    if domain in excluded_domains:
        continue
    if domain not in remaining_by_source:
        remaining_by_source[domain] = []
    remaining_by_source[domain].append(ev)

def quality_score(ev):
    """Score de qualité pour garder les meilleurs events"""
    score = 0
    desc = ev.get('description', '') or ''
    loc = ev.get('location', '') or ''
    title = ev.get('title', '') or ''
    cats = ev.get('categories', '') or ''
    
    # Description riche
    if len(desc) > 150:
        score += 3
    elif len(desc) > 80:
        score += 2
    elif len(desc) > 30:
        score += 1
    
    # Adresse précise
    if ',' in loc and len(loc) > 25:
        score += 3
    elif len(loc) > 15:
        score += 1
    
    # Coordonnées GPS
    if ev.get('latitude') and ev.get('longitude'):
        lat = float(ev.get('latitude', 0))
        lon = float(ev.get('longitude', 0))
        if lat != 0 and lon != 0:
            score += 1
    
    # Catégories
    if cats and len(cats) > 3:
        score += 1
    
    # Titre significatif
    if len(title) > 10:
        score += 1
    
    # Source URL valide
    if ev.get('source_url') and 'http' in (ev.get('source_url') or ''):
        score += 1
    
    return score

ids_delete_30pct = []

for domain, domain_events in sorted(remaining_by_source.items(), key=lambda x: -len(x[1])):
    total = len(domain_events)
    keep_count = max(1, round(total * 0.30))
    delete_count = total - keep_count
    
    if delete_count == 0:
        print(f"  {domain}: {total} events → garder tout (1 seul event)")
        continue
    
    # Trier par qualité (meilleurs en premier)
    domain_events.sort(key=quality_score, reverse=True)
    
    events_to_keep = domain_events[:keep_count]
    events_to_delete = domain_events[keep_count:]
    
    print(f"\n  {domain}: {total} → garder {keep_count}, supprimer {delete_count}")
    print(f"    Gardés:")
    for ev in events_to_keep:
        print(f"      + {ev.get('title', '?')[:55]}")
    
    for ev in events_to_delete:
        ids_delete_30pct.append(ev['id'])

# ======================================================
# RÉSUMÉ
# ======================================================
all_ids = ids_delete_all + ids_delete_30pct
print(f"\n=== RÉSUMÉ ===")
print(f"Suppression niveaux 1+2 (total): {len(ids_delete_all)}")
print(f"Suppression niveaux 3+4 (70%): {len(ids_delete_30pct)}")
print(f"TOTAL à supprimer: {len(all_ids)}")
print(f"Events restants estimé: {len(events) - len(all_ids)}")

# ======================================================
# EXÉCUTION
# ======================================================
print(f"\n=== EXÉCUTION ===")
deleted = 0
for i in range(0, len(all_ids), 25):
    batch = all_ids[i:i+25]
    try:
        resp = requests.post(f'{API_URL}/api/events/delete-by-ids', json={'ids': batch}, timeout=30)
        if resp.status_code == 200:
            deleted += len(batch)
            print(f"  Lot {i//25 + 1}: {len(batch)} supprimés OK")
        else:
            print(f"  Lot {i//25 + 1}: ERREUR {resp.status_code}")
    except Exception as e:
        print(f"  Lot {i//25 + 1}: EXCEPTION - {e}")

print(f"\nTotal supprimés: {deleted}")

# ======================================================
# VÉRIFICATION
# ======================================================
print(f"\n=== VÉRIFICATION FINALE ===")
r2 = requests.get(f'{API_URL}/api/events', timeout=30)
data2 = r2.json()
events2 = data2 if isinstance(data2, list) else data2.get('events', [])
print(f"Total events confirmé: {len(events2)}")

sources2 = {}
for ev in events2:
    src = ev.get('source_url', '') or ''
    domain = urlparse(src).netloc if src else 'SANS_SOURCE'
    sources2[domain] = sources2.get(domain, 0) + 1

print(f"\nDistribution finale:")
for domain, count in sorted(sources2.items(), key=lambda x: -x[1]):
    print(f"  {domain}: {count}")
