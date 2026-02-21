"""
NETTOYAGE COMPLET : supprimer events inventés, corriger dates/organisateurs faux.
Basé sur l'audit du 9 février 2026.
"""
import requests, sys, io, json

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# ============================================================
# ÉTAPE 1 : SUPPRIMER les events avec données clairement inventées
# ============================================================
IDS_TO_DELETE = [
    2137,  # Polymanga 2026 - site montre 2024, "Cyprien" inventé, dates devinées
    2138,  # Montreux Jazz 2026 - site montre 2025, aucune date 2026 confirmée
    1164,  # Geneva Lux - dates FAUSSES (réel: 16 jan-1er fév, on a: 12-22 mars), event passé
]

print("=" * 60)
print("ÉTAPE 1 : Suppression des events inventés")
print("=" * 60)

for eid in IDS_TO_DELETE:
    r = requests.delete(f'{API_URL}/api/events/delete-by-ids', json={'ids': [eid]}, timeout=30)
    if r.status_code == 200:
        print(f"  ✅ ID {eid} supprimé")
    else:
        print(f"  ❌ ID {eid} erreur: {r.status_code} - {r.text[:200]}")

# ============================================================
# ÉTAPE 2 : CORRIGER les events avec dates/organisateurs faux
# ============================================================
print("\n" + "=" * 60)
print("ÉTAPE 2 : Correction des dates et organisateurs")
print("=" * 60)

corrections = [
    {
        'id': 532,
        'title': 'Carnaval de Monthey',
        'start_date': '2026-02-12',  # source: 12 février
        'end_date': '2026-02-17',    # source: 17 février
        'description': "153e Carnaval de Monthey. Pendant six jours, la ville de Monthey se métamorphose en un théâtre à ciel ouvert, vibrant de couleurs, de sons et d'émotions. Cortège costumé, concours de masques, Guggenmusik et festivités populaires. Le cortège défile le dimanche. Festival gratuit et ouvert à tous.",
        'organizer_name': 'Carnaval de Monthey',  # était "Valais Événements" (inventé)
    },
    {
        'id': 566,
        'title': 'Ultra Tour Monte Rosa',
        'start_date': '2026-09-02',  # source: 2 September 2026
        'end_date': '2026-09-05',    # source: 5 September 2026
        'organizer_name': 'KORA Explore GmbH',  # était "Sport été" (inventé)
        'description': "Ultra Tour Monte Rosa, course d'ultra-trail de 170 km le long du Tour de Monte Rosa. Course en étapes (4 jours) ou ultra d'un seul tenant. Départ de Grächen. Le parcours encercle 29 sommets de plus de 4000m autour du massif du Mont Rose.",
        'location': 'Dorfplatz, 3925 Grächen, Valais, Suisse',
    },
    {
        'id': 2134,
        'title': "FestiVal d'Anniviers - Concert au Barrage de Moiry",
        'start_date': '2026-08-05',  # OK
        'end_date': '2026-08-05',    # Le concert au barrage est le 5 août uniquement
        # Le festival complet va du 5 au 9 août mais notre event est spécifiquement le concert au barrage
    },
    {
        'id': 503,
        'organizer_name': 'PALP Festival / Association Grand Mirific',  # était "Valais Tourisme"
    },
    {
        'id': 505,
        'title': 'Combat de reines Approz',
        'organizer_name': 'Fédération Suisse d\'élevage de la Race d\'Hérens',  # était "Valais Tourisme"
        # Note: la date du 10 mai à Approz n'est pas confirmée sur la page source
        # La page source mentionne un combat qualificatif le 22 mars 2026 (pas à Approz)
        # On garde l'event mais on corrige l'organisateur
    },
    {
        'id': 569,
        'title': 'Swiss Peaks Trail',
        'organizer_name': 'SwissPeaks Trail',  # était "Sport été" (inventé)
        # Note: site montre 2024 (26 août - 8 sept 2024), pas de dates 2026 confirmées
        # Dates probables mais non confirmées
    },
]

# Préparer le batch update
batch_updates = []
for fix in corrections:
    update = {'id': fix['id']}
    for key in ['title', 'start_date', 'end_date', 'description', 'location', 'organizer_name', 'categories']:
        if key in fix:
            update[key] = fix[key]
    batch_updates.append(update)

r = requests.post(f'{API_URL}/api/events/fix-details-batch', json={'events': batch_updates}, timeout=30)
if r.status_code == 200:
    data = r.json()
    print(f"  ✅ Batch update: {data}")
else:
    print(f"  ❌ Batch update erreur: {r.status_code} - {r.text[:300]}")

# ============================================================
# ÉTAPE 3 : Supprimer Bonvillars & Truffe (date Oct 2026 fausse)
# L'event finit le 22 fév 2026 et notre date dit Oct 2026
# ============================================================
print("\n" + "=" * 60)
print("ÉTAPE 3 : Correction Bonvillars & Truffe")
print("=" * 60)

# Corriger la date plutôt que supprimer - l'event est réel mais la date est fausse
bonvillars_fix = [{
    'id': 1157,
    'start_date': '2026-02-14',  # Prochaine date réelle : Sam. 14 février
    'end_date': '2026-02-22',    # Dernière date: Dim. 22 février
    'description': "Cours de cavage à la truffe et atelier cuisine à La Sauvageraie de Bonvillars. Balade en forêt d'environ 2 heures avec des chiens truffiers, puis préparation d'un repas avec la récolte. Menu de 3 apéritifs, 5 plats, 1 fromage et 1 dessert, tous à base de truffes. Max 10 participants, inscription en ligne obligatoire.",
    'location': 'La Sauvageraie, Cour de Bonvillars, 1427 Bonvillars, Vaud',
}]

r = requests.post(f'{API_URL}/api/events/fix-details-batch', json={'events': bonvillars_fix}, timeout=30)
if r.status_code == 200:
    print(f"  ✅ Bonvillars corrigé: {r.json()}")
else:
    print(f"  ❌ Erreur: {r.status_code} - {r.text[:300]}")

# ============================================================
# RAPPORT FINAL
# ============================================================
print("\n" + "=" * 60)
print("RAPPORT FINAL")
print("=" * 60)

r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])
scraped = [e for e in events if e.get('source_url')]
print(f"  Total events scrapés restants: {len(scraped)}")

# Compter par région
valais = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in ['valais', 'sierre', 'monthey', 'sion', 'martigny', 'champéry', 'morgins', 'troistorrents', 'anniviers', 'grimentz', 'nendaz', 'approz', 'grächen'])]
vaud = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in ['vaud', 'lausanne', 'vevey', 'nyon', 'montreux', 'cully', "l'abbaye", 'bonvillars', 'les mosses'])]
geneve = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in ['genève', 'geneva', 'meyrin', 'le grand-saconnex', 'cologny', 'plainpalais', 'onex'])]
print(f"  Valais: {len(valais)}")
print(f"  Vaud: {len(vaud)}")
print(f"  Genève: {len(geneve)}")
