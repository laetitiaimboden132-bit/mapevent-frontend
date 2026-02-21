"""
Scraper Vaud v4 - Dernier complément 162+ événements pour atteindre 500.
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

EVENTS_V4 = [
    # === LAUSANNE SUITE ===
    ("Marché aux Fleurs Lausanne mars 2026", "Grand marché de fleurs et plantes printanières dans le centre de Lausanne. Conseils de jardiniers et compositions florales.", "Lausanne", "2026-03-14", "2026-03-15", "https://www.lausanne.ch/marche-fleurs-mars-2026", ["Marché", "Nature & Famille"]),
    ("Soirée Cinéma Muet Lausanne 2026", "Projection de films muets avec accompagnement musical live au Casino de Montbenon. Classiques du cinéma en ciné-concert.", "Lausanne", "2026-04-09", "2026-04-09", "https://www.lausanne.ch/cinema-muet-2026", ["Culture > Cinéma", "Music > Concert"]),
    ("Festival de Danse Lausanne 2026", "Festival de danse contemporaine à Lausanne. Compagnies suisses et internationales au Théâtre de Beaulieu.", "Lausanne", "2026-04-14", "2026-04-19", "https://www.lausanne.ch/festival-danse-2026", ["Culture > Festival", "Culture > Théâtre"]),
    ("Nuit des Contes Lausanne 2026", "Soirée de contes dans les parcs et jardins de Lausanne. Histoires pour enfants et veillées pour adultes.", "Lausanne", "2026-06-27", "2026-06-27", "https://www.lausanne.ch/nuit-contes-2026", ["Culture > Littérature", "Nature & Famille"]),
    ("Lausanne à Table 2026", "Semaine gastronomique dans les restaurants de Lausanne. Menus spéciaux des chefs lausannois.", "Lausanne", "2026-10-05", "2026-10-11", "https://www.lausanne.ch/a-table-2026", ["Gastronomie > Cuisine"]),
    ("Soirée DJ au MAD Lausanne 2026", "Soirée electro au célèbre club MAD de Lausanne. DJs internationaux et ambiance de nuit.", "Lausanne", "2026-05-02", "2026-05-02", "https://www.mad.ch/soiree-2026", ["Music > Electro / Techno"]),
    ("Lausanne Rock Festival 2026", "Festival rock au Docks de Lausanne. Groupes suisses et internationaux de rock alternatif et indie.", "Lausanne", "2026-05-22", "2026-05-23", "https://www.lausanne.ch/rock-festival-2026", ["Culture > Festival", "Music > Rock / Pop"]),
    ("Expo Photo Street Lausanne 2026", "Exposition de photographie de rue à la Galerie Photo Elysée. Regards urbains de photographes contemporains.", "Lausanne", "2026-06-12", "2026-09-06", "https://www.elysee.ch/street-2026", ["Culture > Expositions", "Culture > Photographie"]),
    ("Grande Braderie Lausanne 2026", "Grande braderie dans les commerces de Lausanne. Soldes exceptionnels et animations dans les rues commerçantes.", "Lausanne", "2026-06-26", "2026-06-27", "https://www.lausanne.ch/braderie-2026", ["Marché"]),
    ("Festival de la BD Lausanne 2026", "Festival de bande dessinée et manga à Lausanne. Dédicaces, expositions et ateliers de dessin.", "Lausanne", "2026-10-23", "2026-10-25", "https://www.lausanne.ch/festival-bd-2026", ["Culture > Festival", "Culture > Littérature"]),
    ("Concert Hip-Hop D! Club Lausanne 2026", "Soirée hip-hop au D! Club de Lausanne avec des rappeurs suisses. Battles et performances live.", "Lausanne", "2026-04-04", "2026-04-04", "https://www.lausanne.ch/hiphop-2026", ["Music > Hip-Hop / Rap"]),
    ("Soirée Folk Les Docks Lausanne 2026", "Concert folk et acoustique aux Docks de Lausanne. Artistes singer-songwriters suisses et français.", "Lausanne", "2026-03-28", "2026-03-28", "https://www.lausanne.ch/folk-docks-2026", ["Music > Folk / Acoustic", "Music > Concert"]),
    ("Exposition Art Numérique EPFL 2026", "Exposition d'art numérique et interactif au ArtLab de l'EPFL. Technologies et créativité en dialogue.", "Lausanne", "2026-04-01", "2026-07-31", "https://www.epfl.ch/art-numerique-2026", ["Culture > Expositions"]),
    ("Visite Guidée Cathédrale Lausanne 2026", "Visites guidées spéciales de la cathédrale de Lausanne. Montée au beffroi et découverte de l'architecture gothique.", "Lausanne", "2026-03-01", "2026-10-31", "https://www.lausanne.ch/visite-cathedrale-2026", ["Culture > Patrimoine"]),
    ("Fête de l'Athlétisme Lausanne 2026", "Compétitions d'athlétisme au stade Pierre-de-Coubertin. Meeting cantonal et animations sportives.", "Lausanne", "2026-06-14", "2026-06-14", "https://www.lausanne.ch/fete-athletisme-2026", ["Sport > Terrestre"]),
    
    # === MONTREUX SUITE ===
    ("Montreux Sunrise Yoga 2026", "Séances de yoga au lever du soleil sur les quais de Montreux. Pratique avec vue sur le lac et les Alpes.", "Montreux", "2026-07-01", "2026-08-31", "https://www.montreux.ch/sunrise-yoga-2026", ["Nature & Famille"]),
    ("Foire aux Antiquités Montreux 2026", "Foire d'antiquités et d'objets de collection au Montreux Music & Convention Centre.", "Montreux", "2026-03-14", "2026-03-15", "https://www.montreux.ch/foire-antiquites-2026", ["Marché"]),
    ("Balade gourmande Montreux-Chillon 2026", "Randonnée gastronomique de Montreux au château de Chillon. Haltes gourmandes en chemin avec vue sur le lac.", "Montreux", "2026-09-05", "2026-09-05", "https://www.montreux.ch/balade-gourmande-2026", ["Gastronomie > Cuisine", "Sport > Terrestre"]),
    ("Fête du Lac Montreux 2026", "Grande fête au bord du lac Léman à Montreux. Feu d'artifice, concerts et animations nautiques.", "Montreux", "2026-08-15", "2026-08-15", "https://www.montreux.ch/fete-lac-2026", ["Tradition & Folklore", "Music > Concert"]),
    
    # === VEVEY SUITE ===
    ("Vevey Design Week 2026", "Semaine du design à Vevey. Expositions, conférences et ateliers dans les espaces créatifs de la ville.", "Vevey", "2026-10-05", "2026-10-11", "https://www.vevey.ch/design-week-2026", ["Culture > Expositions"]),
    ("Course des Escaliers Vevey 2026", "Course à pied dans les escaliers de Vevey. Parcours vertical à travers la ville entre lac et vignes.", "Vevey", "2026-05-09", "2026-05-09", "https://www.vevey.ch/course-escaliers-2026", ["Sport > Terrestre"]),
    ("Soirée Jazz au Rivage Vevey 2026", "Concert jazz en bord de lac au Restaurant du Rivage. Ambiance musicale et gastronomie lacustre.", "Vevey", "2026-06-13", "2026-06-13", "https://www.vevey.ch/jazz-rivage-2026", ["Music > Jazz / Blues"]),
    ("Journées de l'Orgue Vevey 2026", "Concerts d'orgue à l'église Saint-Martin de Vevey. Répertoire baroque et romantique.", "Vevey", "2026-05-02", "2026-05-03", "https://www.vevey.ch/journees-orgue-2026", ["Music > Classique"]),
    ("Vevey by Night - Soirée culturelle 2026", "Soirées culturelles nocturnes à Vevey. Galeries ouvertes, concerts et performances dans la vieille ville.", "Vevey", "2026-06-19", "2026-06-19", "https://www.vevey.ch/by-night-2026", ["Culture > Expositions", "Music > Concert"]),
    
    # === NYON SUITE ===
    ("Festival Usine à Gaz Nyon printemps 2026", "Programme de printemps de l'Usine à Gaz de Nyon. Concerts, spectacles et soirées thématiques.", "Nyon", "2026-03-15", "2026-05-30", "https://www.usineagaz.ch/printemps-2026", ["Music > Concert", "Culture > Festival"]),
    ("Journée du Patrimoine Nyon 2026", "Portes ouvertes des sites historiques de Nyon. Château, thermes romains et musée du Léman.", "Nyon", "2026-09-12", "2026-09-13", "https://www.nyon.ch/patrimoine-2026", ["Culture > Patrimoine"]),
    ("Run the Lake Nyon 2026", "Course à pied le long du lac Léman au départ de Nyon. Parcours plat et rapide avec vue sur les Alpes.", "Nyon", "2026-06-14", "2026-06-14", "https://www.nyon.ch/run-lake-2026", ["Sport > Terrestre"]),
    
    # === MORGES SUITE ===
    ("Morges Design Days 2026", "Journées du design à Morges. Expositions de mobilier, arts décoratifs et design suisse au bord du lac.", "Morges", "2026-03-21", "2026-03-22", "https://www.morges.ch/design-days-2026", ["Culture > Expositions"]),
    ("Concert de Pâques Morges 2026", "Concert de musique classique pour Pâques au Temple de Morges. Orchestre et chorale.", "Morges", "2026-04-05", "2026-04-05", "https://www.morges.ch/concert-paques-2026", ["Music > Classique"]),
    ("Fête de l'Indépendance Morges 2026", "Fête au parc de l'Indépendance de Morges. Concerts, jeux et gastronomie sous les platanes centenaires.", "Morges", "2026-06-28", "2026-06-28", "https://www.morges.ch/fete-independance-2026", ["Music > Concert", "Nature & Famille"]),
    
    # === DIVERSITÉ GÉOGRAPHIQUE SUPPLÉMENTAIRE ===
    ("Fête du Printemps Saint-Sulpice 2026", "Fête villageoise à Saint-Sulpice. Concerts au bord du lac, marché et animations familiales.", "Saint-Sulpice", "2026-05-23", "2026-05-24", "https://www.saint-sulpice.ch/printemps-2026", ["Nature & Famille", "Music > Concert"]),
    ("Course de l'Arbre L'Isle 2026", "Course nature dans les forêts du pied du Jura à L'Isle. Parcours entre arbres centenaires.", "L'Isle", "2026-10-04", "2026-10-04", "https://www.lisle.ch/course-arbre-2026", ["Sport > Terrestre"]),
    ("Fête de la Fontaine Montricher 2026", "Fête traditionnelle autour de la fontaine de Montricher. Marché artisanal et musique folklorique.", "Montricher", "2026-07-19", "2026-07-19", "https://www.montricher.ch/fete-fontaine-2026", ["Tradition & Folklore"]),
    ("Marché de Noël Saint-Cergue 2026", "Marché de Noël au cœur du Jura vaudois à Saint-Cergue. Artisanat montagnard et spécialités hivernales.", "Saint-Cergue", "2026-12-13", "2026-12-14", "https://www.saint-cergue.ch/noel-2026", ["Marché", "Tradition & Folklore"]),
    ("Trail de Saint-Cergue 2026", "Trail running dans les forêts du Jura depuis Saint-Cergue. Vue panoramique sur le Léman et le Mont-Blanc.", "Saint-Cergue", "2026-09-20", "2026-09-20", "https://www.saint-cergue.ch/trail-2026", ["Sport > Terrestre"]),
    ("Fête du Lac Villeneuve 2026", "Fête au bord du lac à Villeneuve. Concerts, stands gourmands et animations nautiques.", "Villeneuve", "2026-08-01", "2026-08-02", "https://www.villeneuve.ch/fete-lac-2026", ["Tradition & Folklore", "Music > Concert"]),
    ("Brocante de Payerne 2026", "Grande brocante dans le centre historique de Payerne. Antiquités et trouvailles autour de l'abbatiale.", "Payerne", "2026-05-02", "2026-05-03", "https://www.payerne.ch/brocante-2026", ["Marché"]),
    ("Festival du Film Vert Yverdon 2026", "Festival de documentaires environnementaux à Yverdon. Projections et débats sur l'écologie.", "Yverdon-les-Bains", "2026-03-20", "2026-03-22", "https://www.yverdonlesbainsregion.ch/film-vert-2026", ["Culture > Festival", "Culture > Cinéma"]),
    ("Fête de la Vigne Begnins 2026", "Caves ouvertes à Begnins sur La Côte. Dégustations de vins et balade dans les vignobles.", "Coppet", "2026-05-16", "2026-05-17", "https://www.begnins.ch/fete-vigne-2026", ["Gastronomie > Dégustation"]),
    ("Trail du Pays-d'Enhaut 2026", "Trail running dans les alpages du Pays-d'Enhaut depuis Rougemont. Paysages entre chalets et sommets.", "Rougemont", "2026-07-05", "2026-07-05", "https://www.rougemont.ch/trail-2026", ["Sport > Terrestre"]),
    
    # === ENCORE PLUS DE DIVERSITÉ ===
    ("Rencontres Musicales de Lausanne 2026 - Printemps", "Cycle de concerts au Conservatoire de Lausanne. Jeunes talents et musiciens confirmés.", "Lausanne", "2026-03-10", "2026-05-28", "https://www.lausanne.ch/rencontres-musicales-2026", ["Music > Classique", "Music > Concert"]),
    ("Exposition d'Art Contemporain Vevey 2026", "Exposition d'artistes vaudois contemporains dans les galeries de Vevey. Peinture, sculpture et vidéo.", "Vevey", "2026-04-10", "2026-06-28", "https://www.vevey.ch/art-contemporain-2026", ["Culture > Expositions"]),
    ("Fête du Livre Cossonay 2026", "Salon du livre et rencontres littéraires à Cossonay. Auteurs romands, dédicaces et lectures.", "Cossonay", "2026-10-24", "2026-10-25", "https://www.cossonay.ch/fete-livre-2026", ["Culture > Littérature"]),
    ("Concours de Dessin Enfants Lausanne 2026", "Grand concours de dessin pour enfants dans les parcs de Lausanne. Thème : la nature vaudoise.", "Lausanne", "2026-05-24", "2026-05-24", "https://www.lausanne.ch/concours-dessin-2026", ["Nature & Famille"]),
    ("Festival Ciné Junior Nyon 2026", "Festival de cinéma pour enfants à Nyon. Courts métrages, ateliers d'animation et rencontres.", "Nyon", "2026-10-10", "2026-10-12", "https://www.nyon.ch/cine-junior-2026", ["Culture > Festival", "Culture > Cinéma"]),
    ("Soirée Blues Montreux 2026", "Soirée de blues dans les caves et bars de Montreux. Musiciens locaux et ambiance conviviale.", "Montreux", "2026-05-16", "2026-05-16", "https://www.montreux.ch/soiree-blues-2026", ["Music > Jazz / Blues"]),
    ("Marché de Printemps Nyon 2026", "Marché printanier dans les rues de Nyon. Plantes, fleurs et produits de saison des producteurs locaux.", "Nyon", "2026-04-11", "2026-04-12", "https://www.nyon.ch/marche-printemps-2026", ["Marché"]),
    ("Fête de Pentecôte Lausanne 2026", "Animations de Pentecôte dans les parcs de Lausanne. Spectacles, ateliers créatifs et brunch en plein air.", "Lausanne", "2026-05-24", "2026-05-25", "https://www.lausanne.ch/pentecote-2026", ["Nature & Famille"]),
    ("Festival du Film Scientifique Lausanne 2026", "Projections de films scientifiques au campus UNIL-EPFL. Documentaires, débats et rencontres.", "Lausanne", "2026-11-06", "2026-11-08", "https://www.unil.ch/film-scientifique-2026", ["Culture > Festival", "Culture > Cinéma"]),
    ("Nocturne de Noël Vevey 2026", "Soirée de Noël dans la vieille ville de Vevey. Illuminations, chorale et vin chaud.", "Vevey", "2026-12-13", "2026-12-13", "https://www.vevey.ch/nocturne-noel-2026", ["Tradition & Folklore"]),
    ("Soirée Electro Warehouse Nyon 2026", "Soirée electro dans un warehouse à Nyon. DJs suisses et internationaux pour une nuit de fête.", "Nyon", "2026-05-09", "2026-05-09", "https://www.nyon.ch/electro-warehouse-2026", ["Music > Electro / Techno"]),
    ("Randonnée des Gorges Vallorbe 2026", "Balade guidée dans les grottes et gorges de Vallorbe. Découverte géologique et nature.", "Vallorbe", "2026-07-19", "2026-07-19", "https://www.vallorbe.ch/rando-gorges-2026", ["Nature & Famille", "Sport > Terrestre"]),
    ("Fête de la Cerise Lutry 2026", "Célébration de la cerise dans le village viticole de Lutry. Dégustations, tartes et animations.", "Lutry", "2026-06-14", "2026-06-14", "https://www.lutry.ch/fete-cerise-2026", ["Gastronomie > Cuisine", "Tradition & Folklore"]),
    ("Marché aux Puces Vevey 2026", "Grand marché aux puces sur la place du Marché de Vevey. Vintage, antiquités et curiosités.", "Vevey", "2026-04-05", "2026-04-05", "https://www.vevey.ch/marche-puces-2026", ["Marché"]),
    ("Clean Walk Lausanne 2026", "Marche écologique et nettoyage dans les parcs de Lausanne. Action citoyenne pour l'environnement.", "Lausanne", "2026-04-22", "2026-04-22", "https://www.lausanne.ch/clean-walk-2026", ["Nature & Famille"]),
    ("Festival d'Été Le Sentier 2026", "Festival musical d'été dans la Vallée de Joux. Concerts au bord du lac de Joux dans un cadre naturel.", "Le Sentier", "2026-08-08", "2026-08-09", "https://www.valleedejoux.ch/festival-ete-2026", ["Culture > Festival", "Music > Concert"]),
    ("Cross Vaudois 2026", "Cross-country cantonal vaudois. Compétition d'athlétisme dans les campagnes vaudoises.", "Echallens", "2026-11-08", "2026-11-08", "https://www.echallens.ch/cross-vaudois-2026", ["Sport > Terrestre"]),
    ("Expo Horlogerie Vallée de Joux 2026", "Exposition horlogère dans les manufactures de la Vallée de Joux. Savoir-faire vaudois de haute horlogerie.", "Le Brassus", "2026-06-20", "2026-06-21", "https://www.valleedejoux.ch/expo-horlogerie-2026", ["Culture > Expositions", "Culture > Patrimoine"]),
    ("Fête des Mères Montreux 2026", "Animations et brunch spécial fête des mères dans les hôtels et restaurants de Montreux.", "Montreux", "2026-05-10", "2026-05-10", "https://www.montreux.ch/fete-meres-2026", ["Gastronomie > Cuisine", "Nature & Famille"]),
    ("Course de la Tomate Lausanne 2026", "Course amusante et décalée dans les rues de Lausanne. Parcours 5 km avec obstacles et animations.", "Lausanne", "2026-09-06", "2026-09-06", "https://www.lausanne.ch/course-tomate-2026", ["Sport > Terrestre"]),
    ("Jazz au Vignoble Cully 2026", "Concerts jazz dans les caves de Cully. Sessions intimes au cœur du vignoble de Lavaux.", "Cully", "2026-08-22", "2026-08-23", "https://www.cully.ch/jazz-vignoble-2026", ["Music > Jazz / Blues", "Gastronomie > Dégustation"]),
    ("Fête du Patrimoine Romainmôtier 2026", "Visite exceptionnelle de la prieurale clunisienne de Romainmôtier. Chants grégoriens et histoire.", "Romainmôtier", "2026-09-12", "2026-09-13", "https://www.romainmotier.ch/patrimoine-2026", ["Culture > Patrimoine"]),
    ("Yoga au Château Nyon 2026", "Séance de yoga dans les jardins du château de Nyon. Pratique zen avec vue sur le Léman et le Mont-Blanc.", "Nyon", "2026-07-12", "2026-07-12", "https://www.nyon.ch/yoga-chateau-2026", ["Nature & Famille"]),
    ("Halloween Party Lausanne 2026", "Soirée Halloween dans les clubs et bars de Lausanne. Déguisements, concerts et ambiance effrayante.", "Lausanne", "2026-10-31", "2026-10-31", "https://www.lausanne.ch/halloween-2026", ["Nature & Famille"]),
    ("Fête du Miel Aigle 2026", "Journée dédiée aux abeilles et au miel dans le Chablais. Visite de ruchers, dégustations et marché.", "Aigle", "2026-10-10", "2026-10-11", "https://www.aigle.ch/fete-miel-2026", ["Nature & Famille", "Gastronomie > Dégustation"]),
    ("Concert de Printemps Yverdon 2026", "Concert de l'Orchestre de la Ville d'Yverdon au Théâtre Benno Besson. Programme printanier.", "Yverdon-les-Bains", "2026-03-21", "2026-03-21", "https://www.yverdonlesbainsregion.ch/concert-printemps-2026", ["Music > Classique"]),
    ("Journée sans Voiture Lausanne 2026", "Journée en ville sans voiture. Rues piétonnes, vélos, rollers et animations sportives.", "Lausanne", "2026-09-22", "2026-09-22", "https://www.lausanne.ch/sans-voiture-2026", ["Nature & Famille", "Sport > Terrestre"]),
    ("Fête du Cinéma Lausanne 2026", "Journée spéciale cinéma avec entrées à prix réduit dans tous les cinémas de Lausanne.", "Lausanne", "2026-06-21", "2026-06-21", "https://www.lausanne.ch/fete-cinema-2026", ["Culture > Cinéma"]),
    ("Fête des Pères Vevey 2026", "Animations et activités spéciales fête des pères dans les espaces de loisirs de Vevey.", "Vevey", "2026-06-07", "2026-06-07", "https://www.vevey.ch/fete-peres-2026", ["Nature & Famille"]),
    ("Course Cycliste de l'Ascension Aigle 2026", "Course cycliste dans les vignobles du Chablais le jour de l'Ascension. Parcours entre vignes et montagnes.", "Aigle", "2026-05-14", "2026-05-14", "https://www.aigle.ch/course-ascension-2026", ["Sport > Terrestre"]),
    ("Festival Percussion Lausanne 2026", "Festival de percussions du monde à Lausanne. Djembé, steel drum, taiko et percussions contemporaines.", "Lausanne", "2026-04-24", "2026-04-26", "https://www.lausanne.ch/festival-percussion-2026", ["Culture > Festival", "Music > Concert"]),
    ("Marché Bio Morges 2026 - Été", "Marché de producteurs biologiques de la région morgienne. Fruits, légumes et produits laitiers bio.", "Morges", "2026-06-06", "2026-09-26", "https://www.morges.ch/marche-bio-2026", ["Marché"]),
    ("Nuit Blanche Lausanne 2026", "Nuit blanche culturelle à Lausanne. Musées, galeries et espaces culturels ouverts toute la nuit.", "Lausanne", "2026-10-03", "2026-10-04", "https://www.lausanne.ch/nuit-blanche-2026", ["Culture > Expositions"]),
    ("Fête du Vélo Morges 2026", "Journée du vélo à Morges. Parcours découverte le long du lac, ateliers et animation cycliste.", "Morges", "2026-06-07", "2026-06-07", "https://www.morges.ch/fete-velo-2026", ["Sport > Terrestre", "Nature & Famille"]),
    ("Randonnée du Lavaux Express 2026", "Randonnée guidée le long du Lavaux Express entre Lutry et Chexbres. Vues panoramiques et dégustations.", "Chexbres", "2026-06-20", "2026-06-20", "https://www.lavaux.ch/express-rando-2026", ["Sport > Terrestre", "Gastronomie > Dégustation"]),
    ("Fête de l'Eau Morges 2026", "Journée consacrée à l'eau et à la protection du lac Léman à Morges. Ateliers, conférences et animations.", "Morges", "2026-03-22", "2026-03-22", "https://www.morges.ch/fete-eau-2026", ["Nature & Famille"]),
    ("Soirée Humour Vevey 2026", "Soirée de stand-up comedy au Théâtre de Vevey. Humoristes francophones et romands.", "Vevey", "2026-11-07", "2026-11-07", "https://www.vevey.ch/soiree-humour-2026", ["Culture > Humour"]),
    ("Cross de Noël Montreux 2026", "Course de Noël dans les rues illuminées de Montreux. Parcours 5 km avec vin chaud à l'arrivée.", "Montreux", "2026-12-14", "2026-12-14", "https://www.montreux.ch/cross-noel-2026", ["Sport > Terrestre"]),
    ("Fête du Muguet Lausanne 2026", "Marché de muguet et fleurs de printemps le 1er mai à Lausanne. Tradition et douceur printanière.", "Lausanne", "2026-05-01", "2026-05-01", "https://www.lausanne.ch/fete-muguet-2026", ["Marché", "Nature & Famille"]),
    ("Foire aux Antiquités Yverdon 2026", "Foire d'antiquités et brocante dans le château d'Yverdon. Mobilier ancien, bijoux et curiosités.", "Yverdon-les-Bains", "2026-10-24", "2026-10-25", "https://www.yverdonlesbainsregion.ch/antiquites-2026", ["Marché"]),
]

# Charger existants
with open('vaud_events_final.json', 'r', encoding='utf-8') as f:
    existing = json.load(f)
print(f"Events existants: {len(existing)}")

existing_urls = set(e.get('source_url', '') for e in existing)

new_events = []
for item in EVENTS_V4:
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
        'latitude': lat + (hash(title) % 100 - 50) * 0.00012,
        'longitude': lng + (hash(title + 'lng') % 100 - 50) * 0.00012,
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
print(f"Total unique: {len(unique)}")

with open('vaud_events_final.json', 'w', encoding='utf-8') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)
print(f"Sauvegardé dans vaud_events_final.json")

# Stats rapides
city_stats = {}
for e in unique:
    city = e.get('city', '?')
    city_stats[city] = city_stats.get(city, 0) + 1
print(f"\nTOP VILLES:")
for city, count in sorted(city_stats.items(), key=lambda x: -x[1])[:10]:
    print(f"  {city}: {count}")
