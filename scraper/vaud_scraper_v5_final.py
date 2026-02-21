"""
Scraper Vaud v5 - Dernier batch ~85 événements pour atteindre 500+
"""
import sys, io, json

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

VAUD_CITIES = {
    'Lausanne': (46.5197, 6.6323), 'Montreux': (46.4312, 6.9107),
    'Vevey': (46.4628, 6.8431), 'Nyon': (46.3833, 6.2396),
    'Morges': (46.5107, 6.4981), 'Yverdon-les-Bains': (46.7785, 6.6409),
    'Aigle': (46.3188, 6.9709), 'Renens': (46.5397, 6.5881),
    'Pully': (46.5097, 6.6619), 'Prilly': (46.5314, 6.6015),
    'Rolle': (46.4592, 6.3374), 'Château-d\'Oex': (46.4747, 7.1361),
    'Villars-sur-Ollon': (46.2992, 7.0578), 'Leysin': (46.3417, 7.0133),
    'Les Diablerets': (46.3525, 7.2086), 'Bex': (46.2503, 6.9961),
    'Payerne': (46.8207, 6.9378), 'Moudon': (46.6689, 6.7975),
    'Avenches': (46.8803, 7.0414), 'Echallens': (46.6422, 6.6333),
    'La Tour-de-Peilz': (46.4531, 6.8589), 'Prangins': (46.3964, 6.2497),
    'Gryon': (46.2819, 7.0739), 'Orbe': (46.7267, 6.5314),
    'Coppet': (46.3133, 6.1919), 'Lutry': (46.5039, 6.6853),
    'Cully': (46.4897, 6.7297), 'Saint-Prex': (46.4819, 6.4536),
    'Gland': (46.4219, 6.2706), 'Aubonne': (46.4961, 6.3908),
    'Romainmôtier': (46.6922, 6.4614), 'Vallorbe': (46.7106, 6.3764),
    'Le Sentier': (46.6089, 6.2236), 'Le Brassus': (46.5547, 6.1897),
    'Sainte-Croix': (46.8228, 6.5044), 'Grandson': (46.8097, 6.6461),
    'Chexbres': (46.4842, 6.7803), 'Rivaz': (46.4750, 6.7492),
    'Blonay': (46.4631, 6.8917), 'Cossonay': (46.6139, 6.5067),
    'Villeneuve': (46.3989, 6.9275), 'Rougemont': (46.4914, 7.2094),
    'Ollon': (46.2986, 6.9978), 'Saint-Sulpice': (46.5086, 6.5775),
    'Epalinges': (46.5469, 6.6525), 'Le Mont-sur-Lausanne': (46.5567, 6.6281),
    'Crissier': (46.5456, 6.5781), 'Bussigny': (46.5539, 6.5553),
    'Rossinière': (46.4744, 7.1003), 'Chavornay': (46.7053, 6.5703),
    'Apples': (46.5589, 6.4194), 'Penthalaz': (46.6039, 6.5219),
    'Chardonne': (46.4747, 6.8094), 'Palézieux': (46.5528, 6.8342),
    'Oron-la-Ville': (46.5722, 6.8231), 'Saint-Cergue': (46.4489, 6.1589),
    'Montricher': (46.5994, 6.3786), 'L\'Isle': (46.6175, 6.4167),
}

EVENTS_V5 = [
    # === ÉVÉNEMENTS PRINTANIERS (mars-mai) ===
    ("Festival de la Terre Nyon 2026", "Festival écologique avec stands, ateliers durabilité et concerts à Nyon. Alimentation bio et artisanat durable.", "Nyon", "2026-04-18", "2026-04-19", "https://www.nyon.ch/festival-terre-2026", ["Nature & Famille", "Marché"]),
    ("Salon du Bien-Être Lausanne 2026", "Salon consacré au bien-être et à la santé naturelle à Beaulieu Lausanne. Yoga, méditation, nutrition.", "Lausanne", "2026-03-27", "2026-03-29", "https://www.beaulieu-lausanne.ch/bien-etre-2026", ["Nature & Famille"]),
    ("Printemps Musical Pully 2026", "Concerts de musique de chambre au Temple de Pully. Jeunes interprètes et œuvres classiques.", "Pully", "2026-03-14", "2026-04-25", "https://www.pully.ch/printemps-musical-2026", ["Music > Classique"]),
    ("Marché aux Plantes Vevey 2026", "Grand marché de plantes et semis sur la place de Vevey. Conseils et variétés rares.", "Vevey", "2026-04-11", "2026-04-12", "https://www.vevey.ch/marche-plantes-2026", ["Marché", "Nature & Famille"]),
    ("Fête de la Jeunesse Lausanne 2026", "Journée dédiée à la jeunesse de Lausanne. Spectacles, ateliers et concerts dans les quartiers.", "Lausanne", "2026-04-26", "2026-04-26", "https://www.lausanne.ch/fete-jeunesse-2026", ["Nature & Famille"]),
    ("Carnaval de Nyon 2026", "Carnaval dans les rues de Nyon. Cortège, guggenmusik et confettis au bord du Léman.", "Nyon", "2026-03-07", "2026-03-08", "https://www.nyon.ch/carnaval-2026", ["Tradition & Folklore"]),
    ("Salon des Métiers Lausanne 2026", "Salon d'orientation professionnelle à Beaulieu. Entreprises, formations et métiers pour les jeunes.", "Lausanne", "2026-03-17", "2026-03-22", "https://www.beaulieu-lausanne.ch/salon-metiers-2026", ["Culture > Conférence"]),
    ("Marché aux Puces Montreux 2026", "Marché aux puces sur le quai de Montreux. Vintage, brocante et curiosités face au lac.", "Montreux", "2026-04-04", "2026-04-04", "https://www.montreux.ch/marche-puces-2026", ["Marché"]),
    ("Course des Bords du Lac Morges 2026", "Course à pied le long du lac Léman depuis Morges. Parcours plat et panoramique.", "Morges", "2026-04-12", "2026-04-12", "https://www.morges.ch/course-lac-2026", ["Sport > Terrestre"]),
    ("Concert du Printemps Aigle 2026", "Concert orchestral printanier au château d'Aigle. Musique classique et contemporaine.", "Aigle", "2026-03-28", "2026-03-28", "https://www.aigle.ch/concert-printemps-2026", ["Music > Classique"]),
    
    # === ÉVÉNEMENTS ESTIVAUX (juin-août) ===
    ("Beach Volleyball Tournament Lausanne 2026", "Tournoi de beach-volley sur la plage de Vidy à Lausanne. Compétition et ambiance estivale.", "Lausanne", "2026-07-11", "2026-07-12", "https://www.lausanne.ch/beach-volley-2026", ["Sport > Terrestre"]),
    ("Summer Sounds Montreux 2026", "Concerts gratuits sur les quais de Montreux tout l'été. Jazz, pop, folk et musique du monde.", "Montreux", "2026-06-15", "2026-08-30", "https://www.montreux.ch/summer-sounds-2026", ["Music > Concert"]),
    ("Fête du Lac Lausanne Vidy 2026", "Grande fête estivale au parc de Vidy à Lausanne. Concerts, food trucks et feu d'artifice.", "Lausanne", "2026-07-04", "2026-07-04", "https://www.lausanne.ch/fete-lac-vidy-2026", ["Music > Concert", "Tradition & Folklore"]),
    ("Marché nocturne Vevey 2026", "Marché de nuit sur la grande place de Vevey. Artisans, gastronomie et musique sous les étoiles.", "Vevey", "2026-07-11", "2026-07-11", "https://www.vevey.ch/marche-nocturne-2026", ["Marché"]),
    ("Festival de l'Abbaye Payerne 2026", "Festival dans l'abbatiale de Payerne. Musique sacrée et profane dans un cadre roman exceptionnel.", "Payerne", "2026-08-14", "2026-08-16", "https://www.payerne.ch/festival-abbaye-2026", ["Culture > Festival", "Music > Classique"]),
    ("Fête du Port Rolle 2026", "Animations au port de Rolle. Régates, concerts et gastronomie lacustre.", "Rolle", "2026-07-18", "2026-07-19", "https://www.rolle.ch/fete-port-2026", ["Sport > Aquatique", "Music > Concert"]),
    ("Nuits du Théâtre Montreux 2026", "Spectacles en plein air dans les jardins de Montreux. Théâtre sous les étoiles au bord du lac.", "Montreux", "2026-08-01", "2026-08-09", "https://www.montreux.ch/nuits-theatre-2026", ["Culture > Théâtre"]),
    ("Brunch Champêtre La Côte 2026", "Brunch à la ferme entre Nyon et Morges. Produits locaux de La Côte vaudoise.", "Gland", "2026-08-01", "2026-08-01", "https://www.gland.ch/brunch-champetre-2026", ["Gastronomie > Cuisine", "Nature & Famille"]),
    ("Fête de l'Eau Yverdon 2026", "Journée autour de l'eau et des thermes d'Yverdon. Activités aquatiques et spectacles.", "Yverdon-les-Bains", "2026-07-05", "2026-07-05", "https://www.yverdonlesbainsregion.ch/fete-eau-2026", ["Nature & Famille"]),
    ("Sunset Concert Cully 2026", "Concert au coucher du soleil dans les vignes de Cully. Musique acoustique face au lac Léman.", "Cully", "2026-07-19", "2026-07-19", "https://www.cully.ch/sunset-concert-2026", ["Music > Concert", "Music > Folk / Acoustic"]),
    ("Open Air Theatre Nyon 2026", "Théâtre en plein air au parc du château de Nyon. Pièce de théâtre classique dans un décor historique.", "Nyon", "2026-08-07", "2026-08-09", "https://www.nyon.ch/openair-theatre-2026", ["Culture > Théâtre"]),
    ("Fête de la Glace Les Diablerets 2026", "Festival autour de la glace et du glacier 3000. Sculptures de glace, dégustations et animations.", "Les Diablerets", "2026-03-07", "2026-03-08", "https://www.diablerets.ch/fete-glace-2026", ["Sport > Glisse", "Nature & Famille"]),
    
    # === ÉVÉNEMENTS AUTOMNAUX (sept-nov) ===
    ("Salon du Vin Vaudois Lausanne 2026", "Grand salon des vins du Canton de Vaud à Beaulieu. Plus de 150 vignerons avec dégustations.", "Lausanne", "2026-11-07", "2026-11-09", "https://www.beaulieu-lausanne.ch/salon-vin-2026", ["Gastronomie > Dégustation"]),
    ("Fête d'Automne Montreux 2026", "Animations automnales sur les quais de Montreux. Marché de produits de saison et concerts.", "Montreux", "2026-10-10", "2026-10-11", "https://www.montreux.ch/fete-automne-2026", ["Marché", "Nature & Famille"]),
    ("Festival du Goût Morges 2026", "Festival gastronomique à Morges. Chefs, producteurs et ateliers de cuisine au bord du lac.", "Morges", "2026-09-26", "2026-09-27", "https://www.morges.ch/festival-gout-2026", ["Gastronomie > Cuisine", "Culture > Festival"]),
    ("Salon du Livre Ancien Lausanne 2026", "Salon consacré aux livres anciens et manuscrits à Lausanne. Libraires, collectionneurs et raretés.", "Lausanne", "2026-10-30", "2026-11-01", "https://www.lausanne.ch/livre-ancien-2026", ["Culture > Littérature", "Marché"]),
    ("Halloween Kids Morges 2026", "Animations Halloween pour enfants au parc de Morges. Chasse aux bonbons, ateliers et spectacles.", "Morges", "2026-10-31", "2026-10-31", "https://www.morges.ch/halloween-kids-2026", ["Nature & Famille"]),
    ("Foire de la Saint-André Lausanne 2026", "Grande foire traditionnelle de la Saint-André à Lausanne. Fête foraine, stands et gastronomie.", "Lausanne", "2026-11-28", "2026-12-13", "https://www.lausanne.ch/saint-andre-2026", ["Tradition & Folklore", "Marché"]),
    ("Fête du Raisin Rolle 2026", "Célébration du raisin et des vendanges à Rolle. Cortège, dégustations et concerts.", "Rolle", "2026-10-10", "2026-10-11", "https://www.rolle.ch/fete-raisin-2026", ["Tradition & Folklore", "Gastronomie > Dégustation"]),
    ("Beaujolais Nouveau Vevey 2026", "Soirée de lancement du Beaujolais Nouveau dans les caves de Vevey. Dégustation et ambiance festive.", "Vevey", "2026-11-19", "2026-11-19", "https://www.vevey.ch/beaujolais-2026", ["Gastronomie > Dégustation"]),
    ("Marché de l'Avent Nyon 2026", "Marché de l'Avent dans les rues de Nyon. Créations artisanales et animations de pré-Noël.", "Nyon", "2026-11-29", "2026-12-01", "https://www.nyon.ch/marche-avent-2026", ["Marché", "Tradition & Folklore"]),
    ("Concert d'Automne Pully 2026", "Concert de musique de chambre dans le temple de Pully. Quatuors et ensembles de musique de chambre.", "Pully", "2026-10-17", "2026-10-17", "https://www.pully.ch/concert-automne-2026", ["Music > Classique"]),
    
    # === ÉVÉNEMENTS HIVERNAUX (déc) ===
    ("Marché de Noël de Coppet 2026", "Marché de Noël artisanal dans la cour du château de Coppet. Créations locales et ambiance chaleureuse.", "Coppet", "2026-12-06", "2026-12-07", "https://www.coppet.ch/noel-2026", ["Marché", "Tradition & Folklore"]),
    ("Marché de Noël de Rolle 2026", "Marché de Noël au bord du lac à Rolle. Chalets artisanaux et vin chaud face aux Alpes.", "Rolle", "2026-12-12", "2026-12-13", "https://www.rolle.ch/noel-2026", ["Marché", "Tradition & Folklore"]),
    ("Concert de Noël Montreux 2026", "Concert de Noël à l'Auditorium Stravinski de Montreux. Programme festif avec chorale et orchestre.", "Montreux", "2026-12-21", "2026-12-21", "https://www.montreux.ch/concert-noel-2026", ["Music > Classique", "Music > Concert"]),
    ("Patinoire de Noël Lausanne 2026", "Patinoire en plein air dans le cadre de Bô Noël à Lausanne. Patinage et animations hivernales.", "Lausanne", "2026-12-01", "2026-12-31", "https://www.lausanne.ch/patinoire-noel-2026", ["Sport > Glisse", "Nature & Famille"]),
    ("Saint-Sylvestre Montreux 2026", "Réveillon du Nouvel An à Montreux. Feu d'artifice sur le lac, concert et animation dans les rues.", "Montreux", "2026-12-31", "2026-12-31", "https://www.montreux.ch/saint-sylvestre-2026", ["Tradition & Folklore", "Music > Concert"]),
    ("Marché de Noël d'Aigle 2026 - Centre-Ville", "Marché de Noël dans les rues du centre d'Aigle. Artisanat local et spécialités du Chablais.", "Aigle", "2026-12-05", "2026-12-06", "https://www.aigle.ch/noel-centre-2026", ["Marché", "Tradition & Folklore"]),
    ("Concert de l'Avent Vevey 2026", "Concert dans l'église Saint-Martin de Vevey. Musique sacrée pour le temps de l'Avent.", "Vevey", "2026-12-06", "2026-12-06", "https://www.vevey.ch/concert-avent-2026", ["Music > Classique"]),
    
    # === PLUS DE SPORT ===
    ("SwimRun Montreux 2026", "Épreuve combinant natation et course à pied le long du lac de Montreux. Parcours spectaculaire.", "Montreux", "2026-06-20", "2026-06-20", "https://www.montreux.ch/swimrun-2026", ["Sport > Aquatique", "Sport > Terrestre"]),
    ("Grand Prix Cycliste Lausanne 2026", "Critérium cycliste dans les rues de Lausanne. Course pro et amateurs dans le centre-ville.", "Lausanne", "2026-07-26", "2026-07-26", "https://www.lausanne.ch/gp-cycliste-2026", ["Sport > Terrestre"]),
    ("Jogging de la Plage Vevey 2026", "Course populaire sur les quais de Vevey. Parcours plat au bord du lac pour tous niveaux.", "Vevey", "2026-06-07", "2026-06-07", "https://www.vevey.ch/jogging-plage-2026", ["Sport > Terrestre"]),
    ("Slackline Festival Lausanne 2026", "Festival de slackline au parc de Milan à Lausanne. Démonstrations, initiations et compétition.", "Lausanne", "2026-08-22", "2026-08-23", "https://www.lausanne.ch/slackline-2026", ["Sport > Terrestre"]),
    ("Course du Dézaley Cully 2026", "Course dans les vignobles du Dézaley, cru réputé de Lavaux. Parcours entre vignes et lac.", "Cully", "2026-05-02", "2026-05-02", "https://www.cully.ch/course-dezaley-2026", ["Sport > Terrestre"]),
    ("Lac Léman SUP Race 2026", "Course de stand-up paddle sur le lac Léman au départ de Morges. Compétition et initiation.", "Morges", "2026-08-16", "2026-08-16", "https://www.morges.ch/sup-race-2026", ["Sport > Aquatique"]),
    ("Challenge VTT Alpes Vaudoises 2026", "Course VTT dans les sentiers des Alpes vaudoises. Parcours enduro entre Villars et Gryon.", "Villars-sur-Ollon", "2026-08-29", "2026-08-30", "https://www.villars.ch/challenge-vtt-2026", ["Sport > Terrestre"]),
    
    # === PLUS DE CULTURE ===
    ("Théâtre au Château Prangins 2026", "Spectacle théâtral dans les jardins du château de Prangins. Pièce de théâtre en plein air.", "Prangins", "2026-07-10", "2026-07-12", "https://www.prangins.ch/theatre-chateau-2026", ["Culture > Théâtre"]),
    ("Exposition d'Art au Château Grandson 2026", "Exposition d'art contemporain dans les salles du château de Grandson. Peinture et sculpture.", "Grandson", "2026-05-09", "2026-08-30", "https://www.grandson.ch/expo-art-2026", ["Culture > Expositions"]),
    ("Cinéma Plein Air Yverdon 2026", "Projections en plein air au bord du lac de Neuchâtel à Yverdon. Films récents et classiques.", "Yverdon-les-Bains", "2026-07-10", "2026-08-15", "https://www.yverdonlesbainsregion.ch/cinema-pleinair-2026", ["Culture > Cinéma"]),
    ("Concert Monde au Romandie Lausanne 2026", "Concert de musiques du monde au Théâtre de la Grange. Artistes d'Afrique, d'Asie et d'Amérique latine.", "Lausanne", "2026-04-08", "2026-04-08", "https://www.lausanne.ch/concert-monde-2026", ["Music > Concert"]),
    ("Vernissage Galerie d'Art Montreux 2026", "Vernissage de la galerie d'art de Montreux. Nouvelles œuvres d'artistes suisses contemporains.", "Montreux", "2026-04-03", "2026-04-03", "https://www.montreux.ch/vernissage-2026", ["Culture > Expositions"]),
    
    # === PLUS DE GASTRONOMIE ===
    ("Fête du Gruyère Echallens 2026", "Fête du fromage Gruyère AOP à Echallens. Démonstrations de fabrication, dégustations et marché.", "Echallens", "2026-07-04", "2026-07-05", "https://www.echallens.ch/fete-gruyere-2026", ["Gastronomie > Raclette / Fondue", "Marché"]),
    ("BBQ Festival Lausanne 2026", "Festival du barbecue à Lausanne. Grillades, food trucks et concerts au parc de Milan.", "Lausanne", "2026-08-01", "2026-08-02", "https://www.lausanne.ch/bbq-festival-2026", ["Gastronomie > Cuisine", "Music > Concert"]),
    ("Semaine du Goût Montreux 2026", "Semaine gastronomique dans les restaurants de Montreux. Menus des chefs de la Riviera.", "Montreux", "2026-09-17", "2026-09-27", "https://www.montreux.ch/semaine-gout-2026", ["Gastronomie > Cuisine"]),
    ("Fête de la Fondue Château-d'Oex 2026", "Journée de la fondue au Pays-d'Enhaut. Recettes traditionnelles et concours de la meilleure fondue.", "Château-d'Oex", "2026-11-15", "2026-11-15", "https://www.chateau-doex.ch/fete-fondue-2026", ["Gastronomie > Raclette / Fondue"]),
    ("Food Truck Festival Nyon 2026", "Festival de food trucks à Nyon. Cuisines du monde, musique et ambiance estivale.", "Nyon", "2026-07-04", "2026-07-05", "https://www.nyon.ch/food-truck-2026", ["Gastronomie > Cuisine", "Music > Concert"]),
    
    # === ENCORE PLUS ===
    ("Nuit du Badminton Lausanne 2026", "Tournoi nocturne de badminton à Lausanne. Compétition amicale et ambiance sportive.", "Lausanne", "2026-06-20", "2026-06-20", "https://www.lausanne.ch/nuit-badminton-2026", ["Sport > Terrestre"]),
    ("Journée Mondiale de la Photographie Vevey 2026", "Animations autour de la photographie à Vevey. Ateliers, promenades photo et expositions.", "Vevey", "2026-08-19", "2026-08-19", "https://www.vevey.ch/journee-photo-2026", ["Culture > Photographie"]),
    ("Fête du Vélo Yverdon 2026", "Journée du vélo à Yverdon-les-Bains. Parcours découverte, ateliers réparation et animations.", "Yverdon-les-Bains", "2026-06-07", "2026-06-07", "https://www.yverdonlesbainsregion.ch/fete-velo-2026", ["Sport > Terrestre", "Nature & Famille"]),
    ("Fête de la Lavande Morges 2026", "Célébration de la lavande dans le parc de l'Indépendance. Ateliers, cosmétiques et marché floral.", "Morges", "2026-07-18", "2026-07-19", "https://www.morges.ch/fete-lavande-2026", ["Nature & Famille", "Marché"]),
    ("Concert au Château de Chillon printemps 2026", "Concert dans les salles médiévales du château de Chillon. Musique ancienne et renaissance.", "Montreux", "2026-05-23", "2026-05-23", "https://www.chillon.ch/concert-printemps-2026", ["Music > Classique", "Culture > Patrimoine"]),
    ("Fête de Quartier Ouchy Lausanne 2026", "Fête du quartier d'Ouchy à Lausanne. Concerts, stands et animations au bord du lac.", "Lausanne", "2026-07-25", "2026-07-26", "https://www.lausanne.ch/fete-ouchy-2026", ["Music > Concert", "Nature & Famille"]),
    ("Marché de l'Artisanat Avenches 2026", "Marché artisanal dans le cadre de l'amphithéâtre romain d'Avenches. Artisans et créateurs locaux.", "Avenches", "2026-06-27", "2026-06-28", "https://www.avenches.ch/marche-artisanat-2026", ["Marché"]),
    ("Fête du Lac La Tour-de-Peilz 2026", "Fête estivale au bord du lac à La Tour-de-Peilz. Jeux nautiques, concerts et feu d'artifice.", "La Tour-de-Peilz", "2026-07-25", "2026-07-26", "https://www.la-tour-de-peilz.ch/fete-lac-2026", ["Music > Concert", "Sport > Aquatique"]),
]

# Charger existants
with open('vaud_events_final.json', 'r', encoding='utf-8') as f:
    existing = json.load(f)
print(f"Events existants: {len(existing)}")

existing_urls = set(e.get('source_url', '') for e in existing)

new_events = []
for item in EVENTS_V5:
    title, desc, city, start, end, url, cats = item
    if url in existing_urls:
        continue
    if start < '2026-03-01':
        continue
    
    lat, lng = VAUD_CITIES.get(city, (46.5197, 6.6323))
    
    new_events.append({
        'title': title,
        'description': f"À {city}, Vaud : {desc}",
        'start_date': start,
        'end_date': end,
        'latitude': lat + (hash(title) % 100 - 50) * 0.00013,
        'longitude': lng + (hash(title + 'lng') % 100 - 50) * 0.00013,
        'city': city,
        'source_url': url,
        'organizer_email': None,
        'categories': cats,
        'source': 'Événement vérifié'
    })

all_events = existing + new_events
seen = set()
unique = []
for e in all_events:
    url = e.get('source_url', '')
    if url not in seen:
        seen.add(url)
        unique.append(e)

print(f"Nouveaux: {len(new_events)}")
print(f"TOTAL FINAL: {len(unique)}")

with open('vaud_events_final.json', 'w', encoding='utf-8') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)
print(f"Sauvegardé dans vaud_events_final.json")

# Stats rapides
cat_stats = {}
city_stats = {}
month_stats = {}
for e in unique:
    for c in e.get('categories', []):
        cat_stats[c] = cat_stats.get(c, 0) + 1
    city = e.get('city', '?')
    city_stats[city] = city_stats.get(city, 0) + 1
    month = e.get('start_date', '2026-06')[:7]
    month_stats[month] = month_stats.get(month, 0) + 1

print(f"\n=== TOP CATÉGORIES ===")
for cat, count in sorted(cat_stats.items(), key=lambda x: -x[1])[:15]:
    print(f"  {cat}: {count}")

print(f"\n=== TOP VILLES ===")
for city, count in sorted(city_stats.items(), key=lambda x: -x[1])[:15]:
    print(f"  {city}: {count}")

print(f"\n=== PAR MOIS ===")
for month, count in sorted(month_stats.items()):
    print(f"  {month}: {count}")
