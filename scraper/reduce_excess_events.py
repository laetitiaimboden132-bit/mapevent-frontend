"""
Réduire les events excédentaires de tempslibre.ch et haute-savoie-tourisme.org
pour respecter le quota de 25%.
Stratégie: supprimer en priorité les events les moins intéressants:
- Ateliers récurrents
- Cours hebdomadaires
- Events sans description riche
"""
import requests, sys, io, json
from urllib.parse import urlparse

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])
total = len(events)
print(f"Total events: {total}")

# Séparer par source
tl_events = [ev for ev in events if 'tempslibre.ch' in (ev.get('source_url', '') or '')]
hs_events = [ev for ev in events if 'haute-savoie-tourisme.org' in (ev.get('source_url', '') or '')]

print(f"tempslibre.ch: {len(tl_events)}")
print(f"haute-savoie: {len(hs_events)}")

# Objectif: max 25% chacun
# Après suppression, le total diminue aussi
# TL: max = total * 0.25
# Si on supprime N events TL: (len(tl) - N) / (total - N) <= 0.25
# len(tl) - N <= 0.25 * (total - N)
# len(tl) - N <= 0.25*total - 0.25*N
# len(tl) - 0.25*total <= N - 0.25*N = 0.75*N
# N >= (len(tl) - 0.25*total) / 0.75

tl_to_remove = max(0, int((len(tl_events) - 0.25 * total) / 0.75) + 1)
hs_to_remove = max(0, int((len(hs_events) - 0.25 * total) / 0.75) + 1)

print(f"\nTL à supprimer: {tl_to_remove}")
print(f"HS à supprimer: {hs_to_remove}")

# Mots-clés de faible intérêt
LOW_PRIORITY_KEYWORDS = [
    'atelier', 'cours ', 'cours de', 'stage', 'méditation', 'yoga',
    'café ', 'permanence', 'bibliothèque', 'heure du conte',
    'visite guidée', 'balade', 'promenade', 'randonnée',
    'pot d\'accueil', 'pot de', 'marché', 'brocante',
    'jeu de piste', 'escape game', 'formation',
    'don du sang', 'biberonage', 'maquillage',
]

def priority_score(ev):
    """Score de priorité: plus bas = moins intéressant (à supprimer en premier)"""
    title = (ev.get('title', '') or '').lower()
    desc = (ev.get('description', '') or '').lower()
    text = f"{title} {desc}"
    
    score = 100
    
    # Pénaliser les mots-clés de faible intérêt
    for kw in LOW_PRIORITY_KEYWORDS:
        if kw in text:
            score -= 15
    
    # Bonus pour les festivals, concerts
    if 'festival' in text: score += 30
    if 'concert' in text: score += 20
    if 'exposition' in text: score += 10
    if 'spectacle' in text: score += 10
    
    # Bonus pour la longueur de description
    desc_len = len(ev.get('description', '') or '')
    if desc_len > 200: score += 10
    if desc_len < 50: score -= 20
    
    return score

# Trier TL events par priorité et supprimer les moins intéressants
if tl_to_remove > 0:
    tl_scored = [(priority_score(ev), ev) for ev in tl_events]
    tl_scored.sort(key=lambda x: x[0])
    
    tl_ids_to_delete = [ev['id'] for score, ev in tl_scored[:tl_to_remove]]
    print(f"\nSuppression de {len(tl_ids_to_delete)} events TL de faible priorité:")
    for score, ev in tl_scored[:min(5, tl_to_remove)]:
        print(f"  Score={score} | {ev['title'][:50]}")
    if tl_to_remove > 5:
        print(f"  ... et {tl_to_remove - 5} autres")
    
    # Supprimer par lots
    for i in range(0, len(tl_ids_to_delete), 50):
        batch = tl_ids_to_delete[i:i+50]
        resp = requests.post(f'{API_URL}/api/events/delete-by-ids', json={'ids': batch}, timeout=30)
        if resp.status_code == 200:
            print(f"  Lot {i//50+1}: supprimé {resp.json().get('deleted_count', 0)}")

# Trier HS events par priorité et supprimer les moins intéressants
if hs_to_remove > 0:
    hs_scored = [(priority_score(ev), ev) for ev in hs_events]
    hs_scored.sort(key=lambda x: x[0])
    
    hs_ids_to_delete = [ev['id'] for score, ev in hs_scored[:hs_to_remove]]
    print(f"\nSuppression de {len(hs_ids_to_delete)} events HS de faible priorité:")
    for score, ev in hs_scored[:min(5, hs_to_remove)]:
        print(f"  Score={score} | {ev['title'][:50]}")
    if hs_to_remove > 5:
        print(f"  ... et {hs_to_remove - 5} autres")
    
    for i in range(0, len(hs_ids_to_delete), 50):
        batch = hs_ids_to_delete[i:i+50]
        resp = requests.post(f'{API_URL}/api/events/delete-by-ids', json={'ids': batch}, timeout=30)
        if resp.status_code == 200:
            print(f"  Lot {i//50+1}: supprimé {resp.json().get('deleted_count', 0)}")

# Vérification finale
import time
time.sleep(2)
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])
total = len(events)

sources = {}
for ev in events:
    src = ev.get('source_url', '') or ''
    domain = urlparse(src).netloc if src else 'SANS_SOURCE'
    sources[domain] = sources.get(domain, 0) + 1

print(f"\nAPRÈS RÉDUCTION: {total} events")
for domain, count in sorted(sources.items(), key=lambda x: -x[1])[:10]:
    pct = count / total * 100
    print(f"  {domain}: {count} ({pct:.1f}%)")

print("\nDONE")
