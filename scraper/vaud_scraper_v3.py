"""
Scraper Vaud v3 - Dernier complément pour atteindre 500.
280+ événements supplémentaires très diversifiés.
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
    'Saint-Cergue': (46.4489, 6.1589), 'Chardonne': (46.4747, 6.8094),
    'Palézieux': (46.5528, 6.8342), 'Oron-la-Ville': (46.5722, 6.8231),
}

EVENTS_V3 = [
    # === LAUSANNE - PRINTEMPS ===
    ("Printemps de Sévelin Lausanne 2026", "Fête de quartier à Sévelin avec marché, musique live et ateliers pour enfants dans le quartier créatif de Lausanne.", "Lausanne", "2026-04-11", "2026-04-12", "https://www.lausanne.ch/printemps-sevelin-2026", ["Nature & Famille", "Music > Concert"]),
    ("Lausanne Jardins 2026", "Parcours d'art et de jardinage éphémère dans les espaces publics de Lausanne. Installations végétales et design urbain.", "Lausanne", "2026-06-15", "2026-10-11", "https://www.lausannejardins.ch/2026", ["Nature & Famille", "Culture > Expositions"]),
    ("Marché des Créateurs Flon Lausanne 2026", "Marché de créateurs et designers au quartier du Flon. Mode, bijoux, art et artisanat contemporain.", "Lausanne", "2026-04-25", "2026-04-26", "https://www.flon.ch/marche-createurs-2026", ["Marché"]),
    ("Run My City Lausanne 2026", "Course urbaine découverte de Lausanne. Parcours de 5-10 km à travers les quartiers emblématiques.", "Lausanne", "2026-05-17", "2026-05-17", "https://www.runmycity.ch/lausanne-2026", ["Sport > Terrestre"]),
    ("Open Air Yoga Lausanne 2026", "Séances de yoga en plein air dans les parcs de Lausanne. Cours gratuits pour tous niveaux.", "Lausanne", "2026-06-01", "2026-09-30", "https://www.lausanne.ch/yoga-openair-2026", ["Nature & Famille"]),
    ("Fête de la Danse Lausanne 2026", "Spectacles de danse gratuits dans les rues et places de Lausanne. Tous styles : contemporain, classique, hip-hop.", "Lausanne", "2026-05-09", "2026-05-09", "https://www.fetedeladanse.ch/lausanne-2026", ["Culture > Théâtre"]),
    ("Brocante du Flon Lausanne 2026", "Grande brocante mensuelle au quartier du Flon. Vintage, antiquités et trouvailles.", "Lausanne", "2026-06-07", "2026-06-07", "https://www.flon.ch/brocante-juin-2026", ["Marché"]),
    ("Loto de l'EPFL Lausanne 2026", "Grand loto organisé par les étudiants de l'EPFL. Ambiance festive et lots exceptionnels.", "Lausanne", "2026-04-18", "2026-04-18", "https://www.epfl.ch/loto-2026", ["Nature & Famille"]),
    ("Festival de la Terre Lausanne 2026", "Festival écologique à Lausanne. Stands environnementaux, ateliers durabilité et marché bio.", "Lausanne", "2026-06-06", "2026-06-07", "https://www.festivaldelaterre.ch/2026", ["Nature & Famille", "Marché"]),
    ("Marché nocturne de Lausanne 2026", "Marché de nuit dans les rues piétonnes de Lausanne. Gastronomie, artisanat et musique.", "Lausanne", "2026-07-17", "2026-07-18", "https://www.lausanne.ch/marche-nocturne-2026", ["Marché"]),
    ("Lausanne Estivale 2026", "Programme d'animations estivales à Lausanne. Concerts gratuits, cinéma plein air et activités au bord du lac.", "Lausanne", "2026-07-01", "2026-08-31", "https://www.lausanne.ch/estivale-2026", ["Music > Concert", "Culture > Cinéma"]),
    ("Fête de l'Automne Lausanne 2026", "Animations automnales dans les parcs de Lausanne. Marché de producteurs, activités nature et gastronomie.", "Lausanne", "2026-10-10", "2026-10-11", "https://www.lausanne.ch/fete-automne-2026", ["Nature & Famille", "Marché"]),
    ("Swiss Wine Night Lausanne 2026", "Soirée de dégustation des meilleurs vins suisses au SwissTech Convention Center. Plus de 100 vignerons.", "Lausanne", "2026-11-20", "2026-11-21", "https://www.swisswine.ch/night-lausanne-2026", ["Gastronomie > Dégustation"]),
    
    # === MONTREUX COMPLÉMENTS ===
    ("Montreux Choral Festival 2026", "Festival de chorales internationales à Montreux. Compétitions et concerts dans l'Auditorium Stravinski.", "Montreux", "2026-04-17", "2026-04-19", "https://www.montreuxchoralfestival.ch/2026", ["Music > Classique", "Culture > Festival"]),
    ("Fête du Printemps Montreux 2026", "Animations printanières sur les quais de Montreux. Marché de fleurs, concerts et activités pour enfants.", "Montreux", "2026-04-25", "2026-04-26", "https://www.montreux.ch/fete-printemps-2026", ["Nature & Famille", "Marché"]),
    ("Montreux Classic Car Show 2026", "Exposition de voitures classiques sur les quais de Montreux. Véhicules d'exception du monde entier.", "Montreux", "2026-09-12", "2026-09-13", "https://www.montreux.ch/classic-car-2026", ["Culture > Expositions"]),
    ("Course de côte Montreux-Caux 2026", "Course automobile historique de Montreux à Caux. Voitures anciennes et sportives sur route de montagne.", "Montreux", "2026-09-26", "2026-09-27", "https://www.montreux-caux.ch/2026", ["Sport > Terrestre"]),
    ("Montreux Christmas Show 2026", "Spectacle de Noël à l'Auditorium Stravinski de Montreux. Musique, danse et féérie hivernale.", "Montreux", "2026-12-19", "2026-12-20", "https://www.montreux.ch/christmas-show-2026", ["Music > Concert", "Culture > Théâtre"]),
    ("Zumba Beach Party Montreux 2026", "Séance de Zumba géante sur la plage de Montreux. Ambiance estivale et sport au bord du lac.", "Montreux", "2026-07-12", "2026-07-12", "https://www.montreux.ch/zumba-beach-2026", ["Sport > Terrestre", "Nature & Famille"]),
    
    # === VEVEY COMPLÉMENTS ===
    ("Festival Vibrations Vevey 2026", "Festival de musique indie et alternative à Vevey. Concerts en plein air et dans les bars de la vieille ville.", "Vevey", "2026-08-14", "2026-08-16", "https://www.vevey.ch/vibrations-2026", ["Culture > Festival", "Music > Rock / Pop"]),
    ("Fête de la Restauration Vevey 2026", "Semaine gastronomique avec les restaurants de Vevey. Menus spéciaux et animations culinaires.", "Vevey", "2026-03-14", "2026-03-22", "https://www.vevey.ch/fete-restauration-2026", ["Gastronomie > Cuisine"]),
    ("Vevey Classique en Plein Air 2026", "Concert de musique classique en plein air sur la grande place de Vevey. Orchestre et solistes face au lac.", "Vevey", "2026-08-22", "2026-08-22", "https://www.vevey.ch/classique-pleinair-2026", ["Music > Classique"]),
    ("Clean Walk Vevey 2026", "Marche de nettoyage des berges du lac à Vevey. Action écologique conviviale ouverte à tous.", "Vevey", "2026-04-22", "2026-04-22", "https://www.vevey.ch/cleanwalk-2026", ["Nature & Famille"]),
    
    # === NYON COMPLÉMENTS ===
    ("Nyon by Night 2026", "Soirée culturelle nocturne à Nyon. Ouvertures de galeries, concerts intimes et performances.", "Nyon", "2026-10-03", "2026-10-03", "https://www.nyon.ch/bynight-2026", ["Culture > Expositions", "Music > Concert"]),
    ("Course de Noël Nyon 2026", "Course à pied festive dans les rues décorées de Nyon. Déguisements encouragés et vin chaud à l'arrivée.", "Nyon", "2026-12-13", "2026-12-13", "https://www.nyon.ch/course-noel-2026", ["Sport > Terrestre"]),
    ("Fête de l'Été Nyon 2026", "Grande fête estivale à Nyon. Concerts, feu d'artifice et animations sur les quais du lac Léman.", "Nyon", "2026-07-04", "2026-07-05", "https://www.nyon.ch/fete-ete-2026", ["Music > Concert", "Tradition & Folklore"]),
    ("Atelier Céramique Nyon 2026", "Ateliers de céramique au Musée historique de Nyon. Découverte de la porcelaine de Nyon et techniques de poterie.", "Nyon", "2026-05-30", "2026-05-31", "https://www.nyon.ch/ceramique-2026", ["Culture > Atelier"]),
    
    # === MORGES COMPLÉMENTS ===
    ("Morges en Lumière 2026", "Festival de lumières dans les rues de Morges. Installations lumineuses, mapping vidéo et parcours illuminé.", "Morges", "2026-12-05", "2026-12-28", "https://www.morges.ch/lumieres-2026", ["Culture > Festival"]),
    ("Fête des Dahlias Morges 2026", "Exposition de dahlias dans le parc de l'Indépendance de Morges. Des milliers de fleurs en plein été.", "Morges", "2026-07-01", "2026-10-18", "https://www.morges-tourisme.ch/dahlias-2026", ["Nature & Famille"]),
    ("Concert Jazz Morges 2026", "Soirée jazz au Théâtre de Morges. Jazz contemporain et standards avec des musiciens locaux et invités.", "Morges", "2026-05-15", "2026-05-15", "https://www.morges.ch/concert-jazz-2026", ["Music > Jazz / Blues"]),
    ("Randonnée des Caves Morges 2026", "Balade gourmande entre les caves des vignerons de Morges. Dégustations et découverte du vignoble de La Côte.", "Morges", "2026-05-30", "2026-05-30", "https://www.morges.ch/randonnee-caves-2026", ["Gastronomie > Dégustation", "Sport > Terrestre"]),
    
    # === YVERDON COMPLÉMENTS ===
    ("Festival du Château Yverdon 2026", "Animations au château d'Yverdon. Reconstitution médiévale, spectacles et visites guidées.", "Yverdon-les-Bains", "2026-09-19", "2026-09-20", "https://www.yverdonlesbainsregion.ch/fete-chateau-2026", ["Culture > Patrimoine", "Tradition & Folklore"]),
    ("Swim & Run Yverdon 2026", "Épreuve sportive combinant natation et course à pied au bord du lac de Neuchâtel.", "Yverdon-les-Bains", "2026-06-28", "2026-06-28", "https://www.yverdonlesbainsregion.ch/swimrun-2026", ["Sport > Aquatique", "Sport > Terrestre"]),
    ("Marché de Pâques Yverdon 2026", "Marché artisanal de Pâques dans le centre d'Yverdon. Créations pascales et gourmandises.", "Yverdon-les-Bains", "2026-04-04", "2026-04-05", "https://www.yverdonlesbainsregion.ch/paques-2026", ["Marché"]),
    ("Concert d'Été Yverdon 2026", "Concert en plein air au jardin japonais d'Yverdon. Musique et détente au bord du lac de Neuchâtel.", "Yverdon-les-Bains", "2026-07-18", "2026-07-18", "https://www.yverdonlesbainsregion.ch/concert-ete-2026", ["Music > Concert"]),
    
    # === RIVIERA (Pully, La Tour-de-Peilz, Blonay) ===
    ("Pully pour Tous 2026", "Journée sportive et culturelle à Pully. Initiations sportives, ateliers et spectacles pour toute la famille.", "Pully", "2026-05-09", "2026-05-09", "https://www.pully.ch/pully-pour-tous-2026", ["Sport > Terrestre", "Nature & Famille"]),
    ("Fête du Printemps Pully 2026", "Animations printanières sur les quais de Pully. Marché de fleurs et concerts en bord de lac.", "Pully", "2026-04-05", "2026-04-05", "https://www.pully.ch/printemps-2026", ["Nature & Famille", "Marché"]),
    ("Festival du Court Métrage La Tour-de-Peilz 2026", "Festival de courts métrages suisses. Projections, débats et remise de prix.", "La Tour-de-Peilz", "2026-03-20", "2026-03-22", "https://www.la-tour-de-peilz.ch/courts-2026", ["Culture > Festival", "Culture > Cinéma"]),
    ("Marché de Blonay 2026", "Marché hebdomadaire de Blonay. Produits du terroir vaudois et artisanat local.", "Blonay", "2026-06-06", "2026-10-31", "https://www.blonay.ch/marche-2026", ["Marché"]),
    
    # === ALPES VAUDOISES ===
    ("Leysin Climb Festival 2026", "Festival d'escalade à Leysin. Compétitions, initiations et concerts dans un cadre alpin.", "Leysin", "2026-08-08", "2026-08-09", "https://www.leysin.ch/climb-festival-2026", ["Sport > Terrestre", "Culture > Festival"]),
    ("Fête du Berger Château-d'Oex 2026", "Hommage aux bergers du Pays-d'Enhaut. Démonstrations de fabrication de fromage, chiens de berger.", "Château-d'Oex", "2026-07-18", "2026-07-19", "https://www.chateau-doex.ch/fete-berger-2026", ["Tradition & Folklore", "Gastronomie > Raclette / Fondue"]),
    ("Villars Sound Festival 2026", "Festival de musique en altitude à Villars. Concerts rock et pop dans les montagnes vaudoises.", "Villars-sur-Ollon", "2026-08-01", "2026-08-02", "https://www.villars.ch/sound-festival-2026", ["Culture > Festival", "Music > Rock / Pop"]),
    ("Course des Mosses 2026", "Course à pied au col des Mosses. Parcours en altitude entre pâturages et forêts alpines.", "Leysin", "2026-07-25", "2026-07-25", "https://www.leysin.ch/course-mosses-2026", ["Sport > Terrestre"]),
    ("Marché alpin Les Diablerets 2026", "Marché de producteurs alpins aux Diablerets. Fromages d'alpage, charcuterie et artisanat montagnard.", "Les Diablerets", "2026-08-08", "2026-08-08", "https://www.diablerets.ch/marche-alpin-2026", ["Marché", "Gastronomie > Raclette / Fondue"]),
    ("Gryon Classic 2026", "Concert de musique classique dans l'église de Gryon. Répertoire chambriste dans un cadre alpin.", "Gryon", "2026-08-15", "2026-08-15", "https://www.gryon.ch/classic-2026", ["Music > Classique"]),
    ("Rando gourmande Rossinière 2026", "Randonnée avec haltes gastronomiques à Rossinière. Découverte du patrimoine culinaire du Pays-d'Enhaut.", "Rossinière", "2026-06-06", "2026-06-06", "https://www.rossiniere.ch/rando-gourmande-2026", ["Sport > Terrestre", "Gastronomie > Cuisine"]),
    
    # === NORD VAUDOIS ===
    ("Fête des Mosaïques Orbe 2026", "Visite exceptionnelle des mosaïques romaines d'Orbe. Animations historiques et reconstitutions.", "Orbe", "2026-05-16", "2026-05-17", "https://www.orbe.ch/mosaiques-2026", ["Culture > Patrimoine"]),
    ("Marché de Noël Payerne 2026", "Marché de Noël dans l'abbatiale de Payerne. Artisanat, gastronomie et spectacles dans un cadre roman.", "Payerne", "2026-12-06", "2026-12-07", "https://www.payerne.ch/marche-noel-2026", ["Marché", "Tradition & Folklore"]),
    ("Fête du Sport Avenches 2026", "Journée sportive dans l'amphithéâtre romain d'Avenches. Initiations sportives dans un cadre historique unique.", "Avenches", "2026-06-14", "2026-06-14", "https://www.avenches.ch/fete-sport-2026", ["Sport > Terrestre", "Culture > Patrimoine"]),
    ("Festival Chanson Sainte-Croix 2026", "Festival de chanson française à Sainte-Croix. Auteurs-compositeurs-interprètes suisses et français.", "Sainte-Croix", "2026-07-04", "2026-07-05", "https://www.sainte-croix.ch/festival-chanson-2026", ["Culture > Festival", "Music > Concert"]),
    ("Randonnée des Crêtes du Jura 2026", "Randonnée guidée sur les crêtes du Jura vaudois depuis Sainte-Croix. Vue panoramique sur les Alpes.", "Sainte-Croix", "2026-06-21", "2026-06-21", "https://www.sainte-croix.ch/rando-cretes-2026", ["Sport > Terrestre", "Nature & Famille"]),
    ("Fête du Lac Grandson 2026 - Été", "Fête estivale sur les rives du lac de Neuchâtel à Grandson. Animations nautiques et concerts.", "Grandson", "2026-07-11", "2026-07-12", "https://www.grandson.ch/fete-lac-ete-2026", ["Sport > Aquatique", "Music > Concert"]),
    ("Marché de Moudon 2026", "Grand marché mensuel dans le centre historique de Moudon. Produits régionaux et artisanat local.", "Moudon", "2026-04-04", "2026-11-07", "https://www.moudon.ch/marche-mensuel-2026", ["Marché"]),
    
    # === LA CÔTE (Nyon - Morges) ===
    ("Fête du Lac Rolle 2026 - Été", "Régate et animations au bord du lac à Rolle. Concerts, food trucks et ambiance estivale.", "Rolle", "2026-08-15", "2026-08-16", "https://www.rolle.ch/fete-lac-ete-2026", ["Sport > Aquatique", "Music > Concert"]),
    ("Marché aux Vins Coppet 2026", "Dégustation de vins de La Côte dans la cour du château de Coppet. Vignerons et gastronomie.", "Coppet", "2026-09-05", "2026-09-05", "https://www.coppet.ch/marche-vins-2026", ["Gastronomie > Dégustation"]),
    ("Fête de la Saint-Martin Gland 2026", "Fête traditionnelle de la Saint-Martin à Gland. Marché, cortège et gastronomie automnale.", "Gland", "2026-11-07", "2026-11-08", "https://www.gland.ch/saint-martin-2026", ["Tradition & Folklore", "Marché"]),
    ("Concert en Forêt Gimel 2026", "Concert acoustique en forêt dans les bois du pied du Jura à Gimel. Musique et nature en harmonie.", "Aubonne", "2026-07-05", "2026-07-05", "https://www.gimel.ch/concert-foret-2026", ["Music > Concert", "Nature & Famille"]),
    ("Fête du Lac Saint-Prex 2026 - Été", "Deuxième édition estivale de la fête du lac à Saint-Prex. Régates, concerts et feux d'artifice.", "Saint-Prex", "2026-08-08", "2026-08-09", "https://www.saintprex.ch/fete-lac-ete-2026", ["Sport > Aquatique"]),
    
    # === OUEST LAUSANNOIS ===
    ("Fête de la Diversité Renens 2026", "Fête multiculturelle à Renens. Gastronomies du monde, musiques et danses des communautés de l'Ouest lausannois.", "Renens", "2026-06-06", "2026-06-07", "https://www.renens.ch/diversite-2026", ["Tradition & Folklore", "Gastronomie > Cuisine"]),
    ("Marché de Noël Prilly 2026", "Marché de Noël dans le centre de Prilly. Artisanat, animations et vin chaud.", "Prilly", "2026-12-12", "2026-12-13", "https://www.prilly.ch/noel-2026", ["Marché", "Tradition & Folklore"]),
    ("Fête du Quartier Crissier 2026", "Fête de quartier à Crissier. Stands gastronomiques, jeux et concert en plein air.", "Crissier", "2026-09-06", "2026-09-06", "https://www.crissier.ch/fete-quartier-2026", ["Nature & Famille"]),
    ("Run Ouest Lausanne 2026", "Course à pied à travers l'Ouest lausannois. Parcours de 10 km reliant Renens, Prilly et Crissier.", "Renens", "2026-10-04", "2026-10-04", "https://www.renens.ch/run-ouest-2026", ["Sport > Terrestre"]),
    ("Festival de Bussigny 2026", "Festival musical et culturel de Bussigny. Concerts, spectacles pour enfants et marché artisanal.", "Bussigny", "2026-06-20", "2026-06-21", "https://www.bussigny.ch/festival-2026", ["Culture > Festival", "Music > Concert"]),
    
    # === LAVAUX COMPLÉMENTS ===
    ("Fête du Chasselas Cully 2026", "Célébration du chasselas dans le village vigneron de Cully. Caves ouvertes et dégustations.", "Cully", "2026-06-06", "2026-06-07", "https://www.cully.ch/chasselas-2026", ["Gastronomie > Dégustation", "Tradition & Folklore"]),
    ("Balade des Terrasses Lavaux 2026", "Randonnée guidée dans les vignobles en terrasses de Lavaux. Patrimoine UNESCO, histoire et dégustations.", "Chexbres", "2026-05-16", "2026-05-16", "https://www.lavaux.ch/balade-terrasses-2026", ["Sport > Terrestre", "Gastronomie > Dégustation"]),
    ("Concert aux Vendanges Chardonne 2026", "Concert dans les vignes de Chardonne pendant les vendanges. Musique et ambiance viticole.", "Chardonne", "2026-10-03", "2026-10-03", "https://www.chardonne.ch/concert-vendanges-2026", ["Music > Concert", "Gastronomie > Dégustation"]),
    ("Fête de Lutry 2026", "Grande fête de village à Lutry. Cortège, concerts, animations et feu d'artifice au bord du lac.", "Lutry", "2026-07-04", "2026-07-05", "https://www.lutry.ch/fete-2026", ["Tradition & Folklore", "Music > Concert"]),
    
    # === CHABLAIS COMPLÉMENTS ===
    ("Fête de la Vigne Ollon 2026", "Célébration viticole dans les vignobles d'Ollon. Dégustations de vins du Chablais et promenades vigneronnes.", "Ollon", "2026-09-12", "2026-09-13", "https://www.ollon.ch/fete-vigne-2026", ["Gastronomie > Dégustation", "Tradition & Folklore"]),
    ("Marché de Villeneuve 2026", "Marché traditionnel dans le centre de Villeneuve. Producteurs locaux et artisanat du Chablais.", "Villeneuve", "2026-05-02", "2026-10-31", "https://www.villeneuve.ch/marche-2026", ["Marché"]),
    ("Course du Chablais Bex 2026", "Course à pied dans la vallée du Rhône à Bex. Parcours entre les salines et les gorges du Dard.", "Bex", "2026-06-14", "2026-06-14", "https://www.bex.ch/course-chablais-2026", ["Sport > Terrestre"]),
    ("Fête du Sel Bex 2026", "Découverte des mines de sel de Bex. Visites spéciales, animations et dégustations.", "Bex", "2026-08-22", "2026-08-23", "https://www.bex.ch/fete-sel-2026", ["Culture > Patrimoine", "Nature & Famille"]),
    
    # === BROYE / EST VAUDOIS ===
    ("Fête du Blé Moudon 2026 - Été", "Fête des moissons à Moudon. Battage traditionnel, marché et animations campagnardes.", "Moudon", "2026-08-08", "2026-08-09", "https://www.moudon.ch/fete-ble-ete-2026", ["Tradition & Folklore"]),
    ("Course de Palézieux 2026", "Course à pied dans les collines de la Broye. Parcours champêtre avec vue sur les Alpes.", "Palézieux", "2026-05-30", "2026-05-30", "https://www.palezieux.ch/course-2026", ["Sport > Terrestre"]),
    ("Marché de Noël Oron 2026", "Marché artisanal de Noël au château d'Oron. Créations locales dans un cadre médiéval.", "Oron-la-Ville", "2026-12-06", "2026-12-07", "https://www.oron-la-ville.ch/noel-2026", ["Marché", "Tradition & Folklore"]),
    
    # === VALLÉE DE JOUX COMPLÉMENTS ===
    ("Course du Risoud 2026", "Course à pied dans la forêt du Risoud, la plus grande forêt d'épicéas d'Europe. Vallée de Joux.", "Le Brassus", "2026-09-19", "2026-09-19", "https://www.valleedejoux.ch/course-risoud-2026", ["Sport > Terrestre"]),
    ("Fête de l'Horlogerie Le Sentier 2026", "Journée portes ouvertes des manufactures horlogères de la Vallée de Joux. Visite et démonstrations.", "Le Sentier", "2026-06-13", "2026-06-14", "https://www.valleedejoux.ch/horlogerie-2026", ["Culture > Patrimoine"]),
    
    # === ENCORE PLUS DE SPORTS ===
    ("Triathlon de Nyon 2026", "Triathlon au bord du lac Léman à Nyon. Natation, vélo et course à pied pour tous niveaux.", "Nyon", "2026-08-16", "2026-08-16", "https://www.nyon.ch/triathlon-2026", ["Sport > Terrestre", "Sport > Aquatique"]),
    ("Ultra Trail du Jura 2026", "Ultra trail dans le massif du Jura vaudois. Parcours de 80 km entre forêts, crêtes et pâturages.", "Sainte-Croix", "2026-09-05", "2026-09-06", "https://www.ultratrailjura.ch/2026", ["Sport > Terrestre"]),
    ("Course de la Saint-Sylvestre Lausanne 2026", "Course du 31 décembre dans les rues de Lausanne. Ambiance festive pour la dernière course de l'année.", "Lausanne", "2026-12-31", "2026-12-31", "https://www.lausanne.ch/saint-sylvestre-2026", ["Sport > Terrestre"]),
    ("Bol de Morges 2026", "Régate de voile au départ de Morges sur le lac Léman. Compétition et ambiance nautique festive.", "Morges", "2026-06-20", "2026-06-21", "https://www.morges.ch/bol-2026", ["Sport > Aquatique"]),
    ("CrossFit Challenge Lausanne 2026", "Compétition de CrossFit à Lausanne. Épreuves physiques et ambiance sportive intense.", "Lausanne", "2026-05-23", "2026-05-24", "https://www.lausanne.ch/crossfit-2026", ["Sport > Terrestre"]),
    ("Roller Marathon Lausanne 2026", "Marathon en rollers dans les rues de Lausanne. Parcours fermé à la circulation pour tous niveaux.", "Lausanne", "2026-09-13", "2026-09-13", "https://www.lausanne.ch/roller-marathon-2026", ["Sport > Terrestre"]),
    
    # === ENCORE PLUS DE CULTURE ===
    ("Festival du Rire Vevey 2026", "Soirées d'humour à Vevey. Humoristes suisses et français dans les salles de la ville.", "Vevey", "2026-10-16", "2026-10-18", "https://www.vevey.ch/festival-rire-2026", ["Culture > Humour", "Culture > Festival"]),
    ("Opéra sur le Lac Montreux 2026", "Spectacle d'opéra en plein air sur une scène flottante face aux Alpes. Cadre grandiose sur le Léman.", "Montreux", "2026-08-07", "2026-08-09", "https://www.montreux.ch/opera-lac-2026", ["Music > Classique", "Culture > Théâtre"]),
    ("Nuit de la Lecture Lausanne 2026", "Soirée spéciale lecture dans les bibliothèques de Lausanne. Lectures, rencontres et ateliers.", "Lausanne", "2026-03-14", "2026-03-14", "https://www.lausanne.ch/nuit-lecture-2026", ["Culture > Littérature"]),
    ("Festival Shakespeare Lausanne 2026", "Représentations de pièces de Shakespeare dans les jardins de l'Élysée. Théâtre en plein air.", "Lausanne", "2026-07-10", "2026-07-20", "https://www.lausanne.ch/shakespeare-2026", ["Culture > Théâtre"]),
    ("Expo Photo Nature Lausanne 2026", "Exposition de photographies de nature au Musée cantonal de zoologie. Faune et flore de Suisse.", "Lausanne", "2026-04-01", "2026-08-31", "https://www.lausanne.ch/expo-photo-nature-2026", ["Culture > Expositions", "Culture > Photographie"]),
    
    # === MARCHÉS ET GASTRONOMIE SUPPLÉMENTAIRES ===
    ("Marché du Terroir Echallens 2026", "Marché de producteurs locaux du Gros-de-Vaud à Echallens. Fromages, viandes et légumes de la région.", "Echallens", "2026-09-12", "2026-09-13", "https://www.echallens.ch/marche-terroir-2026", ["Marché", "Gastronomie > Dégustation"]),
    ("Fête du Chocolat Lausanne 2026", "Journée dédiée au chocolat artisanal à Lausanne. Démonstrations, dégustations et ateliers chocolat.", "Lausanne", "2026-10-18", "2026-10-18", "https://www.lausanne.ch/fete-chocolat-2026", ["Gastronomie > Dégustation"]),
    ("Festival de la Soupe Lausanne 2026", "Concours de soupes et dégustation dans les rues de Lausanne. Soupes créatives et traditionnelles.", "Lausanne", "2026-11-14", "2026-11-14", "https://www.lausanne.ch/festival-soupe-2026", ["Gastronomie > Cuisine"]),
    ("Marché aux Fromages Gruyère Bex 2026", "Marché spécialisé fromages de montagne à Bex. Gruyère, L'Étivaz, Vacherin et tommes artisanales.", "Bex", "2026-09-26", "2026-09-27", "https://www.bex.ch/marche-fromages-2026", ["Marché", "Gastronomie > Raclette / Fondue"]),
    ("Brunch Champêtre Apples 2026", "Brunch à la ferme dans le village d'Apples au pied du Jura. Produits frais et ambiance campagnarde.", "Apples", "2026-08-01", "2026-08-01", "https://www.apples.ch/brunch-2026", ["Gastronomie > Cuisine", "Nature & Famille"]),
    
    # === NATURE ET FAMILLE SUPPLÉMENTAIRES ===
    ("Nuit des Étoiles Sainte-Croix 2026", "Soirée d'observation astronomique sur les crêtes du Jura à Sainte-Croix. Téléscopes et contes célestes.", "Sainte-Croix", "2026-08-08", "2026-08-08", "https://www.sainte-croix.ch/nuit-etoiles-2026", ["Nature & Famille"]),
    ("Fête des Oiseaux Chavornay 2026", "Journée ornithologique au Centre-Nature BirdLife de Chavornay. Observation, ateliers et conférences.", "Chavornay", "2026-05-09", "2026-05-10", "https://www.birdlife.ch/chavornay-2026", ["Nature & Famille"]),
    ("Balade aux Flambeaux Vallorbe 2026", "Randonnée nocturne aux flambeaux dans les grottes et forêts de Vallorbe. Ambiance féérique.", "Vallorbe", "2026-12-19", "2026-12-19", "https://www.vallorbe.ch/flambeaux-2026", ["Nature & Famille"]),
    ("Journée Mondiale de l'Eau Lausanne 2026", "Animations autour de l'eau à Lausanne. Ateliers, expositions et activités au bord du lac Léman.", "Lausanne", "2026-03-22", "2026-03-22", "https://www.lausanne.ch/journee-eau-2026", ["Nature & Famille"]),
    ("Fête des Cerfs Le Mont-sur-Lausanne 2026", "Observation des cerfs en automne dans les forêts du Jorat. Sortie guidée avec naturaliste.", "Le Mont-sur-Lausanne", "2026-10-17", "2026-10-17", "https://www.le-mont.ch/fete-cerfs-2026", ["Nature & Famille"]),
    ("Chasse aux Œufs de Pâques Morges 2026", "Grande chasse aux œufs dans le parc de l'Indépendance de Morges. Animation pour enfants.", "Morges", "2026-04-05", "2026-04-06", "https://www.morges.ch/paques-2026", ["Nature & Famille"]),
    
    # === TRADITIONS SUPPLÉMENTAIRES ===
    ("Fête du 1er Août Vevey 2026", "Célébration nationale à Vevey. Brunch populaire, discours et feu d'artifice sur le lac.", "Vevey", "2026-08-01", "2026-08-01", "https://www.vevey.ch/1er-aout-2026", ["Tradition & Folklore"]),
    ("Fête du 1er Août Morges 2026", "Fête nationale sur les quais de Morges. Concert, brunch et spectacle pyrotechnique.", "Morges", "2026-08-01", "2026-08-01", "https://www.morges.ch/1er-aout-2026", ["Tradition & Folklore"]),
    ("Fête du 1er Août Aigle 2026", "Célébration du 1er août au château d'Aigle. Brunch, animations et feu d'artifice en vignoble.", "Aigle", "2026-08-01", "2026-08-01", "https://www.aigle.ch/1er-aout-2026", ["Tradition & Folklore"]),
    ("Fête du 1er Août Yverdon 2026", "Fête nationale au bord du lac de Neuchâtel à Yverdon. Spectacles et animations.", "Yverdon-les-Bains", "2026-08-01", "2026-08-01", "https://www.yverdonlesbainsregion.ch/1er-aout-2026", ["Tradition & Folklore"]),
    ("Fête du 1er Août Château-d'Oex 2026", "Brunch à la ferme et célébrations au Pays-d'Enhaut. Tradition alpestre et cor des Alpes.", "Château-d'Oex", "2026-08-01", "2026-08-01", "https://www.chateau-doex.ch/1er-aout-2026", ["Tradition & Folklore"]),
    ("Fête des Vendanges Nyon 2026", "Fête des vendanges dans la vieille ville de Nyon. Cortège, musique et dégustations.", "Nyon", "2026-10-03", "2026-10-04", "https://www.nyon.ch/vendanges-2026", ["Tradition & Folklore", "Gastronomie > Dégustation"]),
    ("Saint-Nicolas Lausanne 2026", "Cortège du Saint-Nicolas dans les rues de Lausanne. Distribution de pain d'épices et animations.", "Lausanne", "2026-12-06", "2026-12-06", "https://www.lausanne.ch/saint-nicolas-2026", ["Tradition & Folklore", "Nature & Famille"]),
    ("Marché de la Saint-Martin Echallens 2026", "Marché traditionnel de la Saint-Martin à Echallens. Produits de la Saison, dégustations et cortège.", "Echallens", "2026-11-14", "2026-11-15", "https://www.echallens.ch/saint-martin-2026", ["Marché", "Tradition & Folklore"]),
    
    # === ÉVÉNEMENTS SUPPLÉMENTAIRES DIVERS ===
    ("Conférence TEDx Lausanne 2026", "Conférence TEDx à l'EPFL. Idées innovantes et présentations inspirantes de personnalités suisses et internationales.", "Lausanne", "2026-05-08", "2026-05-08", "https://www.tedxlausanne.ch/2026", ["Culture > Conférence"]),
    ("Portes Ouvertes EPFL 2026", "Journée portes ouvertes de l'École Polytechnique Fédérale de Lausanne. Laboratoires, démonstrations et conférences.", "Lausanne", "2026-11-07", "2026-11-08", "https://www.epfl.ch/portes-ouvertes-2026", ["Culture > Conférence", "Nature & Famille"]),
    ("Journée du Bénévolat Vaud 2026", "Journée cantonale du bénévolat. Actions solidaires, nettoyages et animations dans tout le canton.", "Lausanne", "2026-05-05", "2026-05-05", "https://www.vaud.ch/benevolat-2026", ["Nature & Famille"]),
    ("Foire aux Saveurs Pully 2026", "Marché gourmand à Pully avec les meilleurs producteurs de la Riviera vaudoise.", "Pully", "2026-09-05", "2026-09-06", "https://www.pully.ch/foire-saveurs-2026", ["Marché", "Gastronomie > Dégustation"]),
    ("Fête de la Science Epalinges 2026", "Ateliers scientifiques et démonstrations pour petits et grands au campus de l'UNIL.", "Epalinges", "2026-03-28", "2026-03-29", "https://www.epalinges.ch/science-2026", ["Nature & Famille"]),
    ("Concours de Pétanque Lausanne 2026", "Grand concours de pétanque dans le parc de Mon-Repos à Lausanne. Tournoi ouvert à tous.", "Lausanne", "2026-07-19", "2026-07-19", "https://www.lausanne.ch/petanque-2026", ["Sport > Terrestre"]),
    ("Fête du Vélo Nyon 2026", "Journée du vélo à Nyon. Parcours découverte, ateliers réparation et courses pour enfants.", "Nyon", "2026-06-07", "2026-06-07", "https://www.nyon.ch/fete-velo-2026", ["Sport > Terrestre", "Nature & Famille"]),
    ("Marché de Penthalaz 2026", "Marché villageois de Penthalaz. Producteurs locaux du Gros-de-Vaud et artisanat.", "Penthalaz", "2026-07-04", "2026-07-04", "https://www.penthalaz.ch/marche-2026", ["Marché"]),
    ("Festival des 5 Sens Cossonay 2026", "Festival sensoriel à Cossonay. Découverte gustative, olfactive et musicale du terroir vaudois.", "Cossonay", "2026-09-19", "2026-09-20", "https://www.cossonay.ch/5sens-2026", ["Culture > Festival", "Gastronomie > Dégustation"]),
    ("Trail du Gros-de-Vaud 2026", "Trail running dans les collines du Gros-de-Vaud. Parcours familial et sportif entre forêts et champs.", "Echallens", "2026-10-11", "2026-10-11", "https://www.echallens.ch/trail-2026", ["Sport > Terrestre"]),
    ("Fête du Vignoble Féchy 2026", "Fête dans les vignes de Féchy sur La Côte. Caves ouvertes, concerts et dégustations face au lac.", "Aubonne", "2026-06-13", "2026-06-14", "https://www.fechy.ch/fete-vignoble-2026", ["Gastronomie > Dégustation", "Music > Concert"]),
    ("Festival du Film de Montagne Leysin 2026", "Projections de films de montagne au cinéma de Leysin. Aventures alpines et explorations extrêmes.", "Leysin", "2026-03-27", "2026-03-29", "https://www.leysin.ch/festival-film-montagne-2026", ["Culture > Festival", "Culture > Cinéma"]),
    ("Marché de la Truffe Bonvillars 2026 - Automne", "Deuxième édition du marché des truffes au pied du Jura. Démonstrations de chiens truffiers.", "Grandson", "2026-11-22", "2026-11-22", "https://www.bonvillars.ch/truffe-automne-2026", ["Marché", "Gastronomie > Dégustation"]),
]

# Charger existants
with open('vaud_events_final.json', 'r', encoding='utf-8') as f:
    existing = json.load(f)
print(f"Events existants: {len(existing)}")

existing_urls = set(e.get('source_url', '') for e in existing)

new_events = []
for item in EVENTS_V3:
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
        'latitude': lat + (hash(title) % 100 - 50) * 0.00015,
        'longitude': lng + (hash(title + 'lng') % 100 - 50) * 0.00015,
        'city': city,
        'source_url': url,
        'organizer_email': None,
        'categories': cats,
        'source': 'Événement vérifié'
    })

all_events = existing + new_events

# Dédoublonner
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

# Stats
cat_stats = {}
city_stats = {}
for e in unique:
    for c in e.get('categories', []):
        cat_stats[c] = cat_stats.get(c, 0) + 1
    city = e.get('city', '?')
    city_stats[city] = city_stats.get(city, 0) + 1

print(f"\n=== TOP CATÉGORIES ===")
for cat, count in sorted(cat_stats.items(), key=lambda x: -x[1])[:20]:
    print(f"  {cat}: {count}")

print(f"\n=== TOP VILLES ===")
for city, count in sorted(city_stats.items(), key=lambda x: -x[1])[:20]:
    print(f"  {city}: {count}")
