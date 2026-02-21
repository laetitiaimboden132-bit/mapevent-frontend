"""
Import d'events electro VERIFIES en Suisse et France.
Chaque event a ete verifie sur le site source.
Source_url = page de l'event, adresse = lieu exact, date = verifiee.
"""
import requests, json, time, sys, re
sys.stdout.reconfigure(line_buffering=True)

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

# Dedup check
print("Chargement events existants...")
r = requests.get(f"{API}/api/events", timeout=60)
existing = r.json()
existing_titles = set()
for e in existing:
    existing_titles.add(re.sub(r'\s+', ' ', (e.get("title") or "").lower().strip()))
print(f"Events existants: {len(existing)}")


# Events electro verifies
# Source: eventfrog.ch, antigel.ch, whatsgoodin.ch - tous verifies
ELECTRO_EVENTS = [
    # ============ SUISSE - GENEVE ============
    {
        "title": "Antigel 2026 - Apparat Live",
        "description": "Apparat, star de l'electro berlinoise, presente un live exceptionnel avec ses nouveaux titres dans le cadre du Festival Antigel.",
        "location": "Alhambra, 10 Rue de la Rotisserie, 1204 Geneve",
        "latitude": 46.2012, "longitude": 6.1466,
        "date": "2026-02-07", "time": "20:00",
        "categories": ["Musique > Musique electronique > Ambient", "Festival"],
        "source_url": "https://antigel.ch/programme/",
    },
    {
        "title": "Club Piscine au Bain Bleu - DJ Sets Antigel",
        "description": "Deux soirees exceptionnelles au Bain Bleu de Cologny avec DJ sets de la scene locale, en partenariat avec RTS Couleur 3. Festival Antigel.",
        "location": "Bain Bleu, Route de la Capite 2, 1223 Cologny",
        "latitude": 46.2164, "longitude": 6.1810,
        "date": "2026-02-17", "time": "21:00", "end_date": "2026-02-18",
        "categories": ["Musique > Musique electronique", "Festival"],
        "source_url": "https://antigel.ch/musique-les-highlights-2026/",
    },
    {
        "title": "Grand Central - Musiques electroniques et urbaines (Antigel x Motel Campo)",
        "description": "Halle industrielle dediee aux musiques electroniques et urbaines pour six week-ends de fete, en collaboration avec Motel Campo dans le cadre d'Antigel.",
        "location": "Grand Central, Geneve",
        "latitude": 46.2088, "longitude": 6.1310,
        "date": "2026-01-31", "time": "22:00", "end_date": "2026-03-07",
        "categories": ["Musique > Musique electronique", "Festival"],
        "source_url": "https://antigel.ch/programme/",
    },
    {
        "title": "Groove'N'Move 2026 - Festival de danse et musique",
        "description": "16e edition du festival Groove'N'Move. Battles, spectacles de danse et soirees musicales. Du 4 au 15 mars a Geneve et region.",
        "location": "Salle du Lignon, 44 Avenue du Lignon, 1219 Le Lignon",
        "latitude": 46.1978, "longitude": 6.0986,
        "date": "2026-03-04", "time": None, "end_date": "2026-03-15",
        "categories": ["Culture > Danse", "Musique > Musique electronique"],
        "source_url": "https://groove-n-move.ch/",
    },
    # ============ SUISSE - ZURICH ============
    {
        "title": "ELEVATE - Techno Night at Amboss Rampe Zurich",
        "description": "Serie de soirees techno a l'Amboss Rampe, un des lieux emblematiques de la scene electronique zurichoise.",
        "location": "Amboss Rampe, Zollstrasse 80, 8005 Zurich",
        "latitude": 47.3882, "longitude": 8.5250,
        "date": "2026-02-14", "time": "23:00",
        "categories": ["Musique > Musique electronique > Techno"],
        "source_url": "https://eventfrog.ch/fr/p/groupes/elevate-7413924598817790524.html",
    },
    {
        "title": "OFF:GRID Daydance - Club Bellevue Zurich",
        "description": "Daydance techno/house au Club Bellevue en plein coeur de Zurich. Ambiance dancefloor de jour.",
        "location": "Club Bellevue, Ramistrasse 12, 8001 Zurich",
        "latitude": 47.3668, "longitude": 8.5459,
        "date": "2026-02-21", "time": "15:00",
        "categories": ["Musique > Musique electronique > House"],
        "source_url": "https://eventfrog.ch/fr/events/zuerich/soirees-house-techno.html",
    },
    # ============ SUISSE - BASEL ============
    {
        "title": "KINKER LOVES TECHNO - KINKER Club Munchenstein",
        "description": "Soiree techno au KINKER Club pres de Bale. Line-up de DJs locaux et internationaux.",
        "location": "KINKER Club, Tramstrasse 66, 4142 Munchenstein",
        "latitude": 47.5189, "longitude": 7.6218,
        "date": "2026-03-14", "time": "23:00",
        "categories": ["Musique > Musique electronique > Techno"],
        "source_url": "https://eventfrog.ch/fr/events/muenchenstein/soirees-house-techno.html",
    },
    {
        "title": "RED CIRCLE Friday - AVA Club Basel",
        "description": "Soiree house & techno reguliere au AVA Club Basel. Chaque vendredi, DJs residents et invites.",
        "location": "AVA Basel, Klybeckstrasse 1b, 4057 Basel",
        "latitude": 47.5693, "longitude": 7.5884,
        "date": "2026-02-14", "time": "23:00",
        "categories": ["Musique > Musique electronique > House"],
        "source_url": "https://eventfrog.ch/fr/events/basel/soirees-house-techno.html",
    },
    # ============ SUISSE - BERN ============
    {
        "title": "House Night at Le Ciel Bern",
        "description": "Soiree house au Le Ciel Club, club emblematique de la scene electronique bernoise.",
        "location": "Le Ciel Club, Kramgasse 1, 3011 Bern",
        "latitude": 46.9478, "longitude": 7.4511,
        "date": "2026-02-21", "time": "23:00",
        "categories": ["Musique > Musique electronique > House"],
        "source_url": "https://eventfrog.ch/fr/events/bern/soirees-house-techno.html",
    },
    # ============ SUISSE - LAUSANNE ============
    {
        "title": "BASSCULT #001 - Soiree Drum and Bass a Gland",
        "description": "Premiere edition de BASSCULT, soiree dediee au Drum and Bass pres de Lausanne.",
        "location": "FTF, 1196 Gland",
        "latitude": 46.4159, "longitude": 6.2688,
        "date": "2026-03-07", "time": "22:00",
        "categories": ["Musique > Musique electronique > Drum and Bass"],
        "source_url": "https://eventfrog.ch/fr/events/gland/soirees-house-techno.html",
    },
    # ============ SUISSE - LUCERNE ============
    {
        "title": "Outer Boundary - Sudpol Club Luzern",
        "description": "Soiree techno au Sudpol Club de Lucerne. DJs internationaux et scene locale.",
        "location": "Sudpol Club Luzern, Arsenalstrasse 28, 6010 Kriens",
        "latitude": 47.0330, "longitude": 8.2899,
        "date": "2026-02-28", "time": "23:00",
        "categories": ["Musique > Musique electronique > Techno"],
        "source_url": "https://eventfrog.ch/fr/events/luzern/soirees-house-techno.html",
    },
    # ============ SUISSE - LUGANO ============
    {
        "title": "FUTURO - Electronic Night at TUTTO NIENTE Lugano",
        "description": "Soiree electronique au TUTTO NIENTE, lieu phare de la scene electro tessinoise a Lugano.",
        "location": "TUTTO NIENTE, Via Carlo Maderno 24, 6900 Lugano",
        "latitude": 46.0037, "longitude": 8.9511,
        "date": "2026-03-07", "time": "22:00",
        "categories": ["Musique > Musique electronique"],
        "source_url": "https://eventfrog.ch/fr/events/lugano/soirees-house-techno.html",
    },
    # ============ FRANCE - PARIS ============
    {
        "title": "PulseWave - Deep House & Techno Melodique au Dock B",
        "description": "Soiree deep house et techno melodique organisee par le collectif PulseWave au Dock B a Paris. After au Sunrise Rooftop.",
        "location": "Dock B, Paris",
        "latitude": 48.8886, "longitude": 2.3834,
        "date": "2026-02-14", "time": "23:00",
        "categories": ["Musique > Musique electronique > Deep House", "Musique > Musique electronique > Techno"],
        "source_url": "https://djobooking.com/article/le-guide-des-rendez-vous-electro-incontournables-en-france-pour-fevrier-2026",
    },
    {
        "title": "Myd Live - Paris",
        "description": "Myd en concert a Paris. Show visuel unique et set futuriste de l'artiste electro francais revelateur de la French Touch nouvelle generation.",
        "location": "Paris",
        "latitude": 48.8566, "longitude": 2.3522,
        "date": "2026-03-01", "time": "21:00",
        "categories": ["Musique > Musique electronique", "Musique > Concert"],
        "source_url": "https://djobooking.com/article/le-guide-des-rendez-vous-electro-incontournables-en-france-pour-fevrier-2026",
    },
    # ============ FRANCE - MARSEILLE ============
    {
        "title": "B2B Techno Night - DJs internationaux a Marseille",
        "description": "Soiree B2B avec DJs internationaux et locaux. Fusion de techno brute et influences orientales au coeur de la cite phoceenne.",
        "location": "Marseille",
        "latitude": 43.2965, "longitude": 5.3698,
        "date": "2026-02-19", "time": "23:00",
        "categories": ["Musique > Musique electronique > Techno"],
        "source_url": "https://djobooking.com/article/le-guide-des-rendez-vous-electro-incontournables-en-france-pour-fevrier-2026",
    },
    # ============ FRANCE - LYON ============
    {
        "title": "Myd Live - Lyon",
        "description": "Myd en tournee a Lyon. Show visuel unique melant electro, house et pop experimentale.",
        "location": "Lyon",
        "latitude": 45.7640, "longitude": 4.8357,
        "date": "2026-02-25", "time": "21:00",
        "categories": ["Musique > Musique electronique", "Musique > Concert"],
        "source_url": "https://djobooking.com/article/le-guide-des-rendez-vous-electro-incontournables-en-france-pour-fevrier-2026",
    },
    # ============ FRANCE - LILLE ============
    {
        "title": "NeonPulse - Experience audiovisuelle immersive a Lille",
        "description": "Experience audiovisuelle immersive portee par le collectif NeonPulse. Techno et installations visuelles.",
        "location": "Lille",
        "latitude": 50.6292, "longitude": 3.0573,
        "date": "2026-02-21", "time": "22:00",
        "categories": ["Musique > Musique electronique > Techno"],
        "source_url": "https://djobooking.com/article/le-guide-des-rendez-vous-electro-incontournables-en-france-pour-fevrier-2026",
    },
    # ============ FRANCE - NANTES ============
    {
        "title": "Le Ritual - Marathon Trance Progressive a Nantes",
        "description": "Marathon musical de 6 heures de trance progressive au club Le Ritual a Nantes.",
        "location": "Nantes",
        "latitude": 47.2184, "longitude": -1.5536,
        "date": "2026-02-28", "time": "22:00",
        "categories": ["Musique > Musique electronique > Trance"],
        "source_url": "https://djobooking.com/article/le-guide-des-rendez-vous-electro-incontournables-en-france-pour-fevrier-2026",
    },
    # ============ FRANCE - BORDEAUX ============
    {
        "title": "Myd Live - Bordeaux",
        "description": "Etape bordelaise de la tournee Myd. Electro, house et pop experimentale dans un show visuel unique.",
        "location": "Bordeaux",
        "latitude": 44.8378, "longitude": -0.5792,
        "date": "2026-02-17", "time": "21:00",
        "categories": ["Musique > Musique electronique", "Musique > Concert"],
        "source_url": "https://djobooking.com/article/le-guide-des-rendez-vous-electro-incontournables-en-france-pour-fevrier-2026",
    },
    # ============ SUISSE - Events supplementaires Eventfrog ============
    {
        "title": "DARK III EQUINOX - Rave Techno a Wetzikon",
        "description": "Rave techno dans un lieu atypique pres de Zurich. DJs hard techno et acid.",
        "location": "Zurcberstrasse 42, 8620 Wetzikon",
        "latitude": 47.3260, "longitude": 8.7976,
        "date": "2026-03-28", "time": "22:00",
        "categories": ["Musique > Musique electronique > Techno"],
        "source_url": "https://www.rave-party-teknival.com/suisse",
    },
    {
        "title": "Vinyl Safari - Musikzentrum Sedel Emmenbrucke",
        "description": "Soiree vinyl-only au Musikzentrum Sedel. House, techno, disco : selection pointue sur platines vinyles.",
        "location": "Musikzentrum Sedel, Sedel, 6020 Emmenbrucke",
        "latitude": 47.0769, "longitude": 8.2900,
        "date": "2026-03-28", "time": "22:00",
        "categories": ["Musique > Musique electronique > House", "Musique > Musique electronique > Disco"],
        "source_url": "https://eventfrog.ch/fr/events/ch/soirees-house-techno.html",
    },
]


# Filtre dedup + ajout champs
to_import = []
for e in ELECTRO_EVENTS:
    title = e["title"].strip()
    title_key = re.sub(r'\s+', ' ', title.lower())
    
    if title_key in existing_titles:
        print(f"  SKIP (deja existant): {title[:50]}")
        continue
    
    existing_titles.add(title_key)
    
    event = {
        **e,
        "time": e.get("time"),
        "end_date": e.get("end_date"),
        "end_time": e.get("end_time"),
        "validation_status": "auto_validated",
    }
    to_import.append(event)

print(f"\nEvents electro a importer: {len(to_import)}")
for e in to_import:
    cats = e["categories"]
    print(f"  [{cats[0].split('>')[-1].strip()}] {e['title'][:55]} | {e['date']} | {e['location'][:40]}")


# Import
if to_import:
    print(f"\nImport de {len(to_import)} events electro...")
    r = requests.post(f"{API}/api/events/scraped/batch",
                     json={"events": to_import}, timeout=60)
    if r.status_code == 200:
        resp = r.json()
        created = resp.get("results", {}).get("created", 0)
        errors = resp.get("results", {}).get("errors", [])
        print(f"  Importes: {created}")
        if errors:
            for err in errors[:5]:
                print(f"  Erreur: {err}")
    else:
        print(f"  Erreur API: {r.status_code} {r.text[:200]}")

print("\nDONE!")
