"""
NETTOYAGE COMPLET v2 : supprimer events inventés, corriger dates/organisateurs faux.
Corrigé : POST pour delete, 'fixes' pour batch update, organizer_name ajouté au backend.
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

# DELETE endpoint uses POST method
r = requests.post(f'{API_URL}/api/events/delete-by-ids', json={'ids': IDS_TO_DELETE}, timeout=30)
if r.status_code == 200:
    data = r.json()
    print(f"  ✅ Supprimés: {data.get('deleted_count', 0)} events")
    for d in data.get('deleted', []):
        print(f"     - ID {d['id']}: {d['title']}")
else:
    print(f"  ❌ Erreur: {r.status_code} - {r.text[:300]}")

# ============================================================
# ÉTAPE 2 : CORRIGER les events avec dates/organisateurs faux
# Key: 'fixes' (not 'events')
# ============================================================
print("\n" + "=" * 60)
print("ÉTAPE 2 : Correction des dates et organisateurs")
print("=" * 60)

fixes = [
    # Carnaval de Monthey - dates complètement fausses (14 mars → 12-17 fév)
    {
        'id': 532,
        'title': 'Carnaval de Monthey',
        'start_date': '2026-02-12',
        'end_date': '2026-02-17',
        'description': "153e Carnaval de Monthey. Pendant six jours, la ville de Monthey se métamorphose en un théâtre à ciel ouvert, vibrant de couleurs, de sons et d'émotions. Cortège costumé, concours de masques, Guggenmusik et festivités populaires. Le cortège défile le dimanche.",
        'organizer_name': 'Carnaval de Monthey',
    },
    # Ultra Tour Monte Rosa - dates fausses (28-30 août → 2-5 sept)
    {
        'id': 566,
        'start_date': '2026-09-02',
        'end_date': '2026-09-05',
        'organizer_name': 'KORA Explore GmbH',
        'description': "Ultra Tour Monte Rosa, course d'ultra-trail de 170 km le long du Tour de Monte Rosa. Course en étapes (4 jours) ou ultra d'un seul tenant autour du massif du Mont Rose. Départ de Grächen. Le parcours encercle 29 sommets de plus de 4000m.",
        'location': 'Dorfplatz, 3925 Grächen, Valais, Suisse',
    },
    # PALP Festival - organizer faux
    {
        'id': 503,
        'organizer_name': 'PALP Festival / Association Grand Mirific',
    },
    # Combat de reines - organizer faux
    {
        'id': 505,
        'organizer_name': "Fédération Suisse d'élevage de la Race d'Hérens",
    },
    # Swiss Peaks Trail - organizer faux
    {
        'id': 569,
        'organizer_name': 'SwissPeaks Trail',
    },
    # Bonvillars & Truffe - date fausse (Oct 2026 → Fév 2026)
    {
        'id': 1157,
        'start_date': '2026-02-14',
        'end_date': '2026-02-22',
        'description': "Cours de cavage à la truffe et atelier cuisine à La Sauvageraie de Bonvillars. Balade en forêt d'environ 2 heures avec des chiens truffiers, puis préparation d'un repas avec la récolte du jour. Menu de 3 apéritifs, 5 plats, 1 fromage et 1 dessert, tous à base de truffes. Max 10 participants.",
        'location': 'La Sauvageraie, Cour de Bonvillars, 1427 Bonvillars, Vaud',
    },
    # Marathon de Genève - start_date manque le 9
    {
        'id': 1165,
        'start_date': '2026-05-09',
        'end_date': '2026-05-10',
        'description': "20e édition du Generali Genève Marathon. Week-end de course à pied avec Marathon, Semi-Marathon, Marathon Relais, 10 km, 5 km et courses juniors. Parcours entre campagne et ville avec vue sur le lac Léman et le Jet d'Eau. Inscriptions ouvertes.",
    },
    # Sion sous les étoiles - "Christophe" → "Christophe Maé"
    {
        'id': 2136,
        'description': "Festival de musique en plein air à la Plaine de Tourbillon, au cœur de Sion. 3 soirées du 16 au 18 juillet 2026 avec Julien Doré, Christophe Maé, Vitaa, Luiza (jeudi), GIMS, Louane, Marine, Jeanne Cherhal (vendredi), Stephan Eicher, Star Academy, Umberto Tozzi, Superbus, Loris Mittaz (samedi).",
    },
]

r = requests.post(f'{API_URL}/api/events/fix-details-batch', json={'fixes': fixes}, timeout=30)
if r.status_code == 200:
    data = r.json()
    print(f"  ✅ Corrigés: {data}")
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

# Vérification des corrections
check_ids = [532, 566, 503, 505, 569, 1157, 1165, 2136]
for eid in check_ids:
    ev = next((e for e in events if e.get('id') == eid), None)
    if ev:
        print(f"\n  ID {eid}: {ev.get('title', '')}")
        print(f"    Date: {ev.get('date', '')} → {ev.get('end_date', '')}")
        print(f"    Lieu: {ev.get('location', '')}")
        print(f"    Org: {ev.get('organizer_name', '')}")
