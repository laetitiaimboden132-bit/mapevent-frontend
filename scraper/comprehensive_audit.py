"""
AUDIT GLOBAL COMPLET ET STRICT de TOUS les events.
Vérifie: adresses, coordonnées, dates, cohérence.
Aussi: corrige des events spécifiques signalés.
"""
import requests, sys, io, json, time, re, math

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])

print(f"TOTAL EVENTS: {len(events)}\n")

# =============================================
# CORRECTIONS IMMÉDIATES (user feedback)
# =============================================
immediate_fixes = []

# 1. Attache ta tuque - Salle polyvalente, Rue des Industries 11, 1964 Conthey
for ev in events:
    if ev['id'] == 512:
        immediate_fixes.append({
            'id': 512,
            'location': 'Salle polyvalente, Rue des Industries 11, 1964 Conthey',
            'start_date': '2026-03-07',
            'end_date': '2026-03-07'
        })
        print(f"FIX ID 512: Attache ta tuque -> Salle polyvalente, Rue des Industries 11, 1964 Conthey")
        break

# 2. Combat de reines Approz - ajuster le location
for ev in events:
    if ev['id'] == 505:
        immediate_fixes.append({
            'id': 505,
            'location': 'Arène des combats de reines, Route d\'Approz, 1994 Aproz (Nendaz)'
        })
        print(f"FIX ID 505: Combat de reines -> Arène, Route d'Approz, 1994 Aproz (Nendaz)")
        break

if immediate_fixes:
    resp = requests.post(
        f'{API_URL}/api/events/fix-details-batch',
        json={'fixes': immediate_fixes},
        timeout=30
    )
    if resp.status_code == 200:
        print(f"  Fixes immédiats: {resp.json().get('updated', 0)} mis à jour\n")

# =============================================
# AUDIT COMPLET
# =============================================

issues = {
    'no_address': [],
    'generic_address': [],
    'no_street_number': [],
    'coords_outside_switzerland': [],
    'coords_zero': [],
    'date_past': [],
    'date_invalid': [],
    'no_date': [],
    'duplicate_title': [],
    'short_description': [],
    'boilerplate_description': [],
}

# Limites géographiques de la Suisse romande + Valais
CH_LAT_MIN, CH_LAT_MAX = 45.8, 47.9
CH_LON_MIN, CH_LON_MAX = 5.8, 10.5

title_count = {}
for ev in events:
    title = ev.get('title', '').strip().lower()
    title_count[title] = title_count.get(title, 0) + 1

for ev in events:
    eid = ev['id']
    title = ev.get('title', '') or ''
    loc = ev.get('location', '') or ''
    lat = ev.get('latitude', 0) or 0
    lon = ev.get('longitude', 0) or 0
    date = ev.get('date', '') or ''
    end_date = ev.get('end_date', '') or ''
    desc = ev.get('description', '') or ''
    source = ev.get('source_url', '') or ''
    
    # Adresse
    if not loc or len(loc) < 5:
        issues['no_address'].append(f"ID {eid}: {title[:40]}")
    elif not re.search(r'\d', loc):
        # Pas de numéro ni code postal
        issues['generic_address'].append(f"ID {eid}: {title[:40]} -> {loc[:50]}")
    
    # Coordonnées
    if lat == 0 or lon == 0:
        issues['coords_zero'].append(f"ID {eid}: {title[:40]}")
    elif lat < CH_LAT_MIN or lat > CH_LAT_MAX or lon < CH_LON_MIN or lon > CH_LON_MAX:
        issues['coords_outside_switzerland'].append(f"ID {eid}: {title[:40]} ({lat:.3f}, {lon:.3f})")
    
    # Dates
    if not date:
        issues['no_date'].append(f"ID {eid}: {title[:40]}")
    elif date < '2026-01-01':
        issues['date_past'].append(f"ID {eid}: {title[:40]} -> {date}")
    
    # Description
    if len(desc) < 20:
        issues['short_description'].append(f"ID {eid}: {title[:40]} -> '{desc[:30]}'")
    
    # Boilerplate
    boilerplate_patterns = ['Learning cross-country', 'Fermer la fenêtre', 'ThéâtreAccueil', 
                           'MusiqueAccueil', 'VivreDécouvrir', 'DOUBLON']
    for bp in boilerplate_patterns:
        if bp.lower() in desc.lower():
            issues['boilerplate_description'].append(f"ID {eid}: {title[:40]} -> contient '{bp}'")
            break
    
    # Doublons
    if title_count.get(title.strip().lower(), 0) > 1:
        issues['duplicate_title'].append(f"ID {eid}: {title[:40]}")

# =============================================
# RAPPORT
# =============================================
print(f"\n{'='*60}")
print(f"RAPPORT D'AUDIT COMPLET")
print(f"{'='*60}")

total_issues = 0
for category, items in issues.items():
    if items:
        print(f"\n[{category.upper()}] ({len(items)} problèmes)")
        for item in items[:10]:
            print(f"  - {item}")
        if len(items) > 10:
            print(f"  ... et {len(items)-10} de plus")
        total_issues += len(items)

print(f"\n{'='*60}")
print(f"TOTAL: {total_issues} problèmes trouvés sur {len(events)} events")

# Score
score = max(0, 100 - (total_issues * 2))
print(f"SCORE QUALITÉ: {score}/100")

# =============================================
# DÉTAILS: Events par source
# =============================================
source_stats = {}
for ev in events:
    src = ev.get('source_url', '') or ''
    if src:
        from urllib.parse import urlparse
        domain = urlparse(src).netloc
    else:
        domain = 'AUCUNE_SOURCE'
    source_stats[domain] = source_stats.get(domain, 0) + 1

print(f"\n{'='*60}")
print(f"RÉPARTITION PAR SOURCE")
print(f"{'='*60}")
for domain, count in sorted(source_stats.items(), key=lambda x: -x[1]):
    pct = count / len(events) * 100
    print(f"  {domain}: {count} ({pct:.1f}%)")

# =============================================
# VÉRIFIER TOUTES LES DATES CULTUREVALAIS CORRIGÉES
# =============================================
print(f"\n{'='*60}")
print(f"DATES CULTUREVALAIS.CH (vérification)")
print(f"{'='*60}")
for ev in events:
    if 'culturevalais.ch' in (ev.get('source_url', '') or ''):
        print(f"  ID {ev['id']}: {ev.get('title','')[:40]} | date: {ev.get('date','')[:10]} | end: {ev.get('end_date','')[:10]} | loc: {ev.get('location','')[:50]}")
