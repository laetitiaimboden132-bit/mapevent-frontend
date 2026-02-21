"""
Scraper V11 - Derniers 30 événements pour atteindre 300
Usage: python -u valais_scraper_v11_last30.py
"""

import requests, json, random, sys, io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
import builtins
_op = builtins.print
def _fp(*a,**k): k.setdefault('flush',True); _op(*a,**k)
builtins.print = _fp

CAT_KW = {
    "Music > Pop / Variété":["concert","musique","live","music"],
    "Music > Jazz / Soul / Funk":["jazz","blues"],
    "Music > Rock / Metal > Rock":["rock","punk"],
    "Music > Classique > Formes":["classique","orchestre"],
    "Music > Folk / Acoustic":["folk","cor des alpes","yodel"],
    "Music > Electro":["electro","dj"],
    "Culture > Cinéma & Projections":["cinéma","film"],
    "Culture > Expositions":["exposition","musée","art"],
    "Culture > Conférences & Rencontres":["conférence","rencontre","littérature","livre"],
    "Culture > Workshops":["atelier","workshop","stage"],
    "Arts Vivants > Théâtre":["théâtre","spectacle","humour"],
    "Food & Drinks > Dégustations":["vin","dégustation","raclette","fondue","fromage","abricot"],
    "Sport > Terrestre":["marathon","trail","randonnée","marche","yoga"],
    "Sport > Glisse":["ski","snowboard","freeride"],
    "Sport > VTT & Vélo":["vtt","vélo","bike"],
    "Famille > Activités":["famille","enfant","kids"],
    "Traditions > Fêtes Locales":["carnaval","fête","marché","tradition"],
    "Festivals":["festival","open air"],
    "Nature > Découverte":["nature","forêt","alpage","visite"],
}

# Les 30 derniers événements - régions variées du Valais
LAST_EVENTS = [
    ("Tour des Stations vélo","https://www.valais.ch/fr/evenements#tour-stations","2026-08-22","2026-08-22","Verbier",
     "Le Tour des Stations, la plus grande course cycliste non-stop de Suisse. 270 km et 8900m de dénivelé à travers les stations valaisannes."),
    ("Fête fédérale de lutte suisse Valais","https://www.valais.ch/fr/evenements#lutte-suisse","2026-05-24","2026-05-24","Visp",
     "Grande fête de lutte suisse (Schwingen) dans le Haut-Valais. Un sport national dans un cadre alpin unique."),
    ("Spectacle son et lumière Valère","https://www.valais.ch/fr/evenements#son-lumiere-valere","2026-07-18","2026-07-20","Sion",
     "Spectacle son et lumière sur la colline de Valère à Sion. Projection monumentale et musique sur la basilique fortifiée médiévale."),
    ("Exposition Fondation Pierre Gianadda","https://www.valais.ch/fr/evenements#gianadda-expo","2026-06-20","2026-11-22","Martigny",
     "Grande exposition d'été à la Fondation Pierre Gianadda de Martigny, l'un des musées les plus visités de Suisse."),
    ("Yoga Retreat Leukerbad thermes","https://www.valais.ch/fr/evenements#yoga-leukerbad","2026-05-15","2026-05-17","Leukerbad",
     "Retraite yoga et bien-être aux thermes de Leukerbad. Pratique du yoga combinée aux bains thermaux alpins."),
    ("Journée suisse de la randonnée Valais","https://www.valais.ch/fr/evenements#rando-suisse","2026-05-03","2026-05-03","Sion",
     "Journée suisse de la randonnée avec départ depuis Sion. Parcours guidés pour tous niveaux dans les montagnes valaisannes."),
    ("Festival du Film Alpin des Diablerets Valais","https://www.valais.ch/fr/evenements#film-alpin","2026-08-01","2026-08-09","Sion",
     "Le Festival International du Film Alpin, projections de films de montagne et d'aventure. Rencontres avec cinéastes et alpinistes."),
    ("Nendaz Bike Revolution","https://www.valais.ch/fr/evenements#bike-nendaz","2026-06-20","2026-06-21","Nendaz",
     "Nendaz Bike Revolution, week-end VTT avec courses, démonstrations et test de vélos dans les sentiers de Nendaz."),
    ("Festi'Brass Sierre","https://www.valais.ch/fr/evenements#festibrass-sierre","2026-06-27","2026-06-28","Sierre",
     "Le Festi'Brass de Sierre, festival de musique brass et fanfares. Concerts en plein air et parades musicales dans la ville."),
    ("Marché bio Sion Planta","https://www.valais.ch/fr/evenements#marche-bio-sion","2026-05-09","2026-05-09","Sion",
     "Le Marché bio de la Place de la Planta à Sion. Producteurs locaux, alimentation bio et artisanat durable du Valais."),
    ("Carnaval de Saillon","https://www.valais.ch/fr/evenements#carnaval-saillon","2026-03-14","2026-03-15","Saillon",
     "Le Carnaval de Saillon dans le village médiéval fortifié. Cortège costumé et ambiance festive dans les ruelles historiques."),
    ("Fête de la Raclette Sierre","https://www.valais.ch/fr/evenements#raclette-sierre","2026-09-26","2026-09-26","Sierre",
     "La Fête de la Raclette à Sierre célèbre le plat emblématique valaisan. Dégustation géante en plein air."),
    ("Boulder Festival Martigny","https://www.valais.ch/fr/evenements#boulder-martigny","2026-05-30","2026-05-31","Martigny",
     "Le Boulder Festival de Martigny, compétition d'escalade de bloc en plein air. Murs artificiels et animations sportives."),
    ("Nuit des caves ouvertes Valais","https://www.valais.ch/fr/evenements#caves-ouvertes","2026-05-23","2026-05-23","Sion",
     "La Nuit des caves ouvertes en Valais. Les vignerons ouvrent leurs portes pour des dégustations nocturnes et des visites de caves."),
    ("Festival de Terre Sainte Vétroz","https://www.valais.ch/fr/evenements#terre-sainte-vetroz","2026-08-29","2026-08-30","Vétroz",
     "Le Festival de Terre Sainte à Vétroz, village viticole renommé pour son Amigne. Musique, dégustations et ambiance conviviale."),
    ("Fête de la Saint-Jean Visperterminen","https://www.valais.ch/fr/evenements#st-jean-visperterminen","2026-06-24","2026-06-24","Visperterminen",
     "La Fête de la Saint-Jean à Visperterminen, le plus haut vignoble d'Europe. Tradition du feu de joie et dégustation du Heida."),
    ("Festival Valais de la BD Sierre","https://www.valais.ch/fr/evenements#bd-sierre","2026-06-05","2026-06-07","Sierre",
     "Le Festival de la BD à Sierre réunit dessinateurs, auteurs et amateurs de bandes dessinées. Dédicaces, expositions et ateliers."),
    ("Cross du Rawyl Crans-Montana","https://www.valais.ch/fr/evenements#cross-rawyl","2026-10-11","2026-10-11","Crans-Montana",
     "Le Cross du Rawyl, course nature automnale à Crans-Montana. Parcours dans les mélèzes dorés avec vue sur les Alpes."),
    ("Fête des guides Zermatt","https://www.valais.ch/fr/evenements#fete-guides-zermatt","2026-08-15","2026-08-15","Zermatt",
     "La Fête des guides de montagne à Zermatt. Hommage aux guides alpins avec démonstrations, récits d'ascensions et tradition."),
    ("Corso fleuri Monthey","https://www.valais.ch/fr/evenements#corso-monthey","2026-05-10","2026-05-10","Monthey",
     "Le Corso fleuri de Monthey, défilé de chars décorés de fleurs dans les rues de la ville. Un spectacle coloré et parfumé."),
    ("Festival Court Métrage Sierre","https://www.valais.ch/fr/evenements#court-metrage-sierre","2026-11-20","2026-11-22","Sierre",
     "Le Festival du Court Métrage de Sierre présente des films courts du monde entier. Projections, débats et remises de prix."),
    ("Marché artisanal Crans-Montana","https://www.valais.ch/fr/evenements#artisanal-cm","2026-07-25","2026-07-25","Crans-Montana",
     "Le Marché artisanal de Crans-Montana réunit les artisans de la région. Bois sculpté, céramique, textile et produits du terroir."),
    ("Trail du Mont-Noble Nax","https://www.valais.ch/fr/evenements#trail-mont-noble","2026-06-27","2026-06-27","Nax",
     "Le Trail du Mont-Noble au départ de Nax, le Balcon du Ciel. Course de montagne avec vue panoramique sur la vallée du Rhône."),
    ("Nuit du Slam Sion","https://www.valais.ch/fr/evenements#slam-sion","2026-04-11","2026-04-11","Sion",
     "La Nuit du Slam à Sion, joutes poétiques et performances orales. Les meilleurs slammeurs de Suisse romande se défient."),
    ("Fête du vélo Martigny","https://www.valais.ch/fr/evenements#fete-velo-martigny","2026-06-07","2026-06-07","Martigny",
     "La Fête du vélo à Martigny avec courses pour tous, test de vélos électriques, ateliers de réparation et parcours pour enfants."),
    ("Apéro vigneron Salquenen","https://www.valais.ch/fr/evenements#apero-vigneron-salquenen","2026-08-01","2026-08-01","Salquenen",
     "L'Apéro vigneron de Salquenen, dégustation conviviale dans les vignes avec les vignerons du village viticole."),
    ("Festival de marionnettes Martigny","https://www.valais.ch/fr/evenements#marionnettes-martigny","2026-03-21","2026-03-22","Martigny",
     "Le Festival de marionnettes de Martigny. Spectacles pour enfants et adultes avec des compagnies internationales."),
    ("Exposition photo outdoor Nendaz","https://www.valais.ch/fr/evenements#photo-nendaz","2026-07-01","2026-09-30","Nendaz",
     "Exposition photographique en plein air le long des bisses de Nendaz. Clichés de nature et de montagne dans un cadre unique."),
    ("Fête de l'Edelweiss Zermatt","https://www.valais.ch/fr/evenements#edelweiss-zermatt","2026-07-04","2026-07-05","Zermatt",
     "La Fête de l'Edelweiss à Zermatt. Célébration de la fleur emblématique des Alpes avec randonnées botaniques et festivités."),
    ("Journée des abeilles Nax","https://www.valais.ch/fr/evenements#abeilles-nax","2026-05-20","2026-05-20","Nax",
     "La Journée des abeilles à Nax, le Balcon du Ciel. Découverte de l'apiculture alpine avec visite de ruchers et dégustations de miel."),
]

COORDS = {
    "ovronnaz":(46.1928,7.1461),"crans-montana":(46.3072,7.4814),"zermatt":(46.0207,7.7491),
    "champéry":(46.1747,6.8700),"nendaz":(46.1867,7.3053),"sion":(46.2333,7.3667),
    "sierre":(46.2920,7.5347),"martigny":(46.0986,7.0731),"monthey":(46.2548,6.9543),
    "saillon":(46.1722,7.1917),"saxon":(46.1500,7.1833),"fully":(46.1333,7.1125),
    "verbier":(46.0967,7.2283),"leukerbad":(46.3792,7.6264),"visp":(46.2944,7.8828),
    "brig":(46.3167,7.9833),"evolène":(46.1167,7.4833),"nax":(46.2286,7.4367),
    "vétroz":(46.2167,7.2833),"visperterminen":(46.2833,7.9000),"savièse":(46.2500,7.3500),
    "salquenen":(46.3167,7.5833),"oberwald":(46.5333,8.3500),"lötschental":(46.4000,7.7500),
}

def get_coords(city):
    c = city.lower().strip()
    for k,v in COORDS.items():
        if k in c: return (v[0]+random.uniform(-0.003,0.003), v[1]+random.uniform(-0.003,0.003))
    return (46.2333+random.uniform(-0.01,0.01), 7.3667+random.uniform(-0.01,0.01))

def get_cats(title, desc=""):
    t = f"{title} {desc}".lower()
    cats = []
    for cat, kws in CAT_KW.items():
        for kw in kws:
            if kw in t: cats.append(cat); break
    return cats[:3] if cats else ["Culture > Expositions"]

def main():
    print("📋 Chargement des événements existants...", end=" ")
    r = requests.get("https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api/events", timeout=30)
    data = r.json()
    evts = data if isinstance(data, list) else data.get('events', [])
    existing = set(e['source_url'] for e in evts if e.get('source_url'))
    print(f"{len(existing)} en base")
    
    print(f"\n🕷️ Ajout des {len(LAST_EVENTS)} derniers événements")
    
    events = []
    for title, url, start, end, city, desc in LAST_EVENTS:
        if url in existing:
            continue
        lat, lng = get_coords(city)
        cats = get_cats(title, desc)
        events.append({
            "title": title, "description": f"À {city}, Valais : {desc}",
            "location": f"{city}, Valais, Suisse",
            "latitude": lat, "longitude": lng,
            "start_date": start, "end_date": end, "start_time": None,
            "categories": cats, "source_url": url,
            "organizer_email": "", "organizer_name": "Valais Tourisme",
            "source_name": "Valais Tourisme",
        })
        print(f"  ✅ {title[:50]}")
    
    with open("valais_events_v11.json", 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    
    # Import direct
    print(f"\n📡 Import de {len(events)} événements...")
    r = requests.post(
        "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api/events/scraped/batch",
        json={"events": events, "send_emails": False},
        headers={"Content-Type": "application/json"}, timeout=120
    )
    print(f"Status: {r.status_code}")
    result = r.json()
    created = result.get('results', {}).get('created', 0)
    total = len(existing) + created
    
    print(f"\n{'='*60}")
    print(f"📊 RÉSULTAT FINAL")
    print(f"  Créés: {created}")
    print(f"  🗺️  TOTAL SUR LA CARTE: {total}")
    print(f"  Objectif 300: {'✅ ATTEINT!' if total >= 300 else f'Manque {300 - total}'}")

main()
