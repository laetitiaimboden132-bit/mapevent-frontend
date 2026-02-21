"""
Suppression de TOUS les events avec dates non confirmées sur la page source.
Conservation uniquement des events vérifiés.
"""
import requests, sys, io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# ============================================================
# IDs à SUPPRIMER : dates non confirmées / page source sans info 2026
# ============================================================
IDS_TO_DELETE = [
    # Geneva - pas de dates 2026 sur leurs sites respectifs
    1169,  # Course de l'Escalade
    1171,  # Fête de la Musique GE
    1173,  # Nuit des Musées GE
    1170,  # Marché de Noël GE
    1185,  # CERN Open Days
    1186,  # Lake Parade
    1174,  # Triathlon de Genève
    1182,  # GIFF
    1179,  # Antigel Festival
    1178,  # Festival de la Bâtie
    1166,  # Bol d'Or Mirabaud
    1183,  # Journées du Patrimoine
    1184,  # Nuit de la Science
    
    # Valais - dates non confirmées
    569,   # Swiss Peaks Trail (site = 2024 seulement)
    505,   # Combat de reines Approz (date 10 mai non confirmée sur source)
    
    # Vaud - sources invalides ou non confirmées
    669,   # Photo Elysée (page 404)
    654,   # Lavaux Passion (redirige vers boutique de vin)
    2140,  # Caribana Festival (site timeout, non vérifié)
    2145,  # Caves Ouvertes Vaudoises (non vérifié)
    1181,  # Marché aux Puces (description générique, récurrent non spécifique)
    
    # vd.leprogramme.ch - dates TOUTES fausses (1er mars au lieu des vraies dates)
    # + descriptions = HTML brut mal parsé
    1148,  # L'Art d'avoir toujours raison (date réelle inconnue, desc garbled)
    1149,  # Open Mic CPO (vraie date: 20 mai, on a: 1er mars, desc garbled)
    1152,  # Mirlitons (vraie date: 17 juin, on a: 1er mars, desc garbled)
    1147,  # Stephan Eicher Seul en scène (vraie date: 19-23 mai, on a: 21 mars, desc garbled)
    
    # vaud.ch - non vérifié
    1158,  # Soirée fondue et luge (site timeout)
]

print(f"Suppression de {len(IDS_TO_DELETE)} events non confirmés...")

r = requests.post(f'{API_URL}/api/events/delete-by-ids', json={'ids': IDS_TO_DELETE}, timeout=30)
if r.status_code == 200:
    data = r.json()
    print(f"✅ Supprimés: {data.get('deleted_count', 0)} events")
    for d in data.get('deleted', []):
        print(f"   - ID {d['id']}: {d['title']}")
else:
    print(f"❌ Erreur: {r.status_code} - {r.text[:300]}")

# ============================================================
# CORRECTION : Salon International des Inventions
# Source Palexpo confirme: 11-15 mars (pas 26-30 mars)
# ============================================================
print("\nCorrection Salon des Inventions...")
fixes = [{
    'id': 1163,
    'title': '51e Salon International des Inventions de Genève',
    'start_date': '2026-03-11',
    'end_date': '2026-03-15',
    'description': "51e Salon International des Inventions de Genève à Palexpo. La plus importante manifestation annuelle consacrée exclusivement à l'invention.",
}]

r = requests.post(f'{API_URL}/api/events/fix-details-batch', json={'fixes': fixes}, timeout=30)
if r.status_code == 200:
    print(f"✅ Salon des Inventions corrigé: {r.json()}")
else:
    print(f"❌ Erreur: {r.status_code} - {r.text[:300]}")

# ============================================================
# RAPPORT FINAL
# ============================================================
print("\n" + "=" * 60)
print("ÉTAT FINAL DU SITE")
print("=" * 60)

r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])
scraped = [e for e in events if e.get('source_url')]

print(f"\nTotal events scrapés restants: {len(scraped)}")

for ev in sorted(scraped, key=lambda e: e.get('date', '')):
    title = ev.get('title', '')[:50]
    date = ev.get('date', '')
    end = ev.get('end_date', '')
    source = (ev.get('source_url', '') or '')
    # Extraire le domaine
    domain = source.split('/')[2] if len(source.split('/')) > 2 else source
    loc = (ev.get('location', '') or '')[:40]
    print(f"  ID {ev['id']:5d} | {date} → {end} | {title:<50} | {domain}")

# Compter par région
valais = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in ['valais', 'sierre', 'monthey', 'sion', 'martigny', 'champéry', 'morgins', 'troistorrents', 'anniviers', 'grimentz', 'nendaz', 'approz', 'grächen', 'bagnes'])]
vaud = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in ['vaud', 'lausanne', 'vevey', 'nyon', 'montreux', 'cully', "l'abbaye", 'bonvillars', 'les mosses'])]
geneve = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in ['genève', 'geneva', 'meyrin', 'le grand-saconnex', 'cologny', 'plainpalais', 'onex'])]

print(f"\n  Valais: {len(valais)}")
print(f"  Vaud: {len(vaud)}")
print(f"  Genève: {len(geneve)}")
print(f"  Total: {len(scraped)}")
