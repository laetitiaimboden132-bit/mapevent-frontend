"""Import missing Haute-Savoie events with unique source_urls"""
import requests, time, json

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Events with UNIQUE source_urls (appending #fragment to differentiate)
events = [
    {
        "title": "Bombino - Blues Touareg au Brise Glace",
        "description": "Figure majeure du blues touareg, le musicien nigerien Bombino revient au Brise Glace d'Annecy. Sa musique mele traditions sahariennes, rythmes africains et influences rock, racontant la vie du desert et les luttes du peuple touareg.",
        "location": "Le Brise Glace, 54 bis Rue des Marquisats, 74000 Annecy",
        "latitude": 45.8917,
        "longitude": 6.1335,
        "date": "2026-03-31",
        "time": "20:30:00",
        "end_date": "2026-03-31",
        "categories": ["Musique", "Concert", "Festival"],
        "source_url": "https://www.lac-in-blue.com/#bombino-31-mars",
        "organizer_email": "contact@lac-in-blue.com",
        "organizer_name": "Lac in Blue"
    },
    {
        "title": "La Nuit du Jazz - Congo Square",
        "description": "Voyage a travers 100 ans d'histoire du jazz avec Jean Gobinet et le Large Ensemble de la HEMU de Lausanne. Premiere partie par les eleves du pole jazz du conservatoire d'Annecy. Duree 3h avec entracte.",
        "location": "Salle Pierre Lamy, 12 Rue de la Republique, 74000 Annecy",
        "latitude": 45.8989,
        "longitude": 6.1271,
        "date": "2026-04-02",
        "time": "19:00:00",
        "end_date": "2026-04-02",
        "categories": ["Musique", "Concert", "Musique > Jazz", "Festival"],
        "source_url": "https://www.lac-in-blue.com/#congo-square-2-avril",
        "organizer_email": "contact@lac-in-blue.com",
        "organizer_name": "Lac in Blue"
    },
    {
        "title": "Joran Cariou Trio - Lac in Blue",
        "description": "Entre ecriture raffinee et spontaneite creative, le Joran Cariou Trio devoile un repertoire melant nouvelles creations et rythmes d'Afrique, d'Andalousie et de jazz traditionnel, nourri de l'heritage classique.",
        "location": "Conservatoire, 10 Rue Jean-Jacques Rousseau, 74000 Annecy",
        "latitude": 45.9020,
        "longitude": 6.1240,
        "date": "2026-04-03",
        "time": "12:30:00",
        "end_date": "2026-04-03",
        "categories": ["Musique", "Concert", "Musique > Jazz", "Festival"],
        "source_url": "https://www.lac-in-blue.com/#joran-cariou-3-avril",
        "organizer_email": "contact@lac-in-blue.com",
        "organizer_name": "Lac in Blue"
    },
    {
        "title": "Jermaine Landsberger Trio feat. Stephane Belmondo",
        "description": "Pianiste d'exception a l'avant-garde de la scene manouche europeenne, Jermaine Landsberger s'associe au trompettiste Stephane Belmondo pour un concert au Chateau d'Annecy. Un dialogue entre jazz manouche et trompette moderne.",
        "location": "Chateau d'Annecy, Place du Chateau, 74000 Annecy",
        "latitude": 45.8988,
        "longitude": 6.1242,
        "date": "2026-04-03",
        "time": "20:30:00",
        "end_date": "2026-04-03",
        "categories": ["Musique", "Concert", "Musique > Jazz", "Festival"],
        "source_url": "https://www.lac-in-blue.com/#landsberger-belmondo-3-avril",
        "organizer_email": "contact@lac-in-blue.com",
        "organizer_name": "Lac in Blue"
    },
    {
        "title": "Mohs - Apero-Concert Jazz aux Carres",
        "description": "Le talentueux quartet suisse Mohs presente son troisieme opus Baine, melant instruments acoustiques et effets electroniques. Des paysages sonores finement ciseles aux multiples references stylistiques, au pied des Alpes.",
        "location": "Les Carres, Avenue des Carres, 74940 Annecy-le-Vieux",
        "latitude": 45.9233,
        "longitude": 6.1403,
        "date": "2026-04-04",
        "time": "19:00:00",
        "end_date": "2026-04-04",
        "categories": ["Musique", "Concert", "Musique > Jazz", "Festival"],
        "source_url": "https://www.lac-in-blue.com/#mohs-4-avril",
        "organizer_email": "contact@lac-in-blue.com",
        "organizer_name": "Lac in Blue"
    },
    {
        "title": "Le Pas du monde - Collectif XY au Bonlieu",
        "description": "Spectacle de cirque acrobatique par le Collectif XY, compagnie emblematique du cirque contemporain francais. Un spectacle a voir en famille, melant acrobatie, portes et emotion, au Bonlieu Scene nationale d'Annecy.",
        "location": "Bonlieu Scene nationale, 1 Rue Jean Jaures, 74000 Annecy",
        "latitude": 45.8995,
        "longitude": 6.1299,
        "date": "2026-03-10",
        "time": "20:00:00",
        "end_date": "2026-03-14",
        "categories": ["Spectacle", "Cirque", "Culture"],
        "source_url": "https://bonlieu-annecy.com/la-saison#le-pas-du-monde",
        "organizer_email": "contact@bonlieu-annecy.com",
        "organizer_name": "Bonlieu Scene nationale"
    }
]

print(f"Importing {len(events)} events...")

r = requests.post(
    f'{API_URL}/api/events/scraped/batch',
    json={"events": events, "send_emails": False},
    timeout=30
)

print(f"Status: {r.status_code}")
result = r.json()
print(f"Result: {json.dumps(result, indent=2)}")

# Verify
time.sleep(2)
r2 = requests.get(f'{API_URL}/api/events', timeout=30)
data = r2.json()
all_events = data if isinstance(data, list) else data.get('events', [])
print(f"\nNew total: {len(all_events)} events")

# Count Haute-Savoie
hs = [e for e in all_events if 'annecy' in (e.get('location','') or '').lower() or 'thonon' in (e.get('location','') or '').lower()]
print(f"Haute-Savoie events: {len(hs)}")
for e in hs:
    print(f"  ID {e['id']}: {e['title'][:60]}")
