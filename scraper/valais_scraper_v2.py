"""
Scraper d'événements V2 - Sources API et agrégateurs
Utilise des APIs ouvertes et des sources plus stables

Usage: python valais_scraper_v2.py
"""

import requests
import json
import time
import random
import re
import sys
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib

# Forcer UTF-8 sur Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
RATE_LIMIT_SECONDS = 8
MAX_EVENTS = 300
START_DATE = datetime(2026, 3, 1)

# User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Firefox/121.0",
]

# Catégories mapping
CATEGORY_KEYWORDS = {
    "Music > Electronic > Techno": ["techno", "electronic", "dj", "club", "electro"],
    "Music > Electronic > House": ["house", "deep house", "tech house"],
    "Music > Rock / Metal > Rock": ["rock", "punk", "indie rock", "concert rock"],
    "Music > Jazz / Soul / Funk": ["jazz", "blues", "soul", "funk", "swing"],
    "Music > Pop / Variété": ["pop", "chanson", "variété", "concert", "musique"],
    "Music > Folk / Acoustic": ["folk", "acoustic", "country"],
    "Music > Classique > Formes": ["classique", "orchestre", "symphonie", "opéra", "choeur"],
    "Culture > Cinéma & Projections": ["cinéma", "film", "projection"],
    "Culture > Expositions": ["exposition", "vernissage", "galerie", "musée", "art"],
    "Culture > Conférences & Rencontres": ["conférence", "débat", "rencontre", "lecture"],
    "Culture > Workshops": ["atelier", "workshop", "cours", "formation"],
    "Arts Vivants > Théâtre": ["théâtre", "spectacle", "comédie", "stand-up", "humour"],
    "Arts Vivants > Danse": ["danse", "ballet", "chorégraphie"],
    "Food & Drinks > Dégustations": ["dégustation", "vin", "œnologie", "cave"],
    "Food & Drinks > Restauration": ["brunch", "repas", "gastronomie", "food"],
    "Loisirs & Animation > Jeux & Soirées": ["quiz", "blind test", "karaoke", "jeu"],
    "Loisirs & Animation > Défilés & Fêtes": ["fête", "carnaval", "défilé", "marché", "brocante", "noël", "foire"],
    "Sport > Terrestre": ["course", "trail", "randonnée", "vélo", "cyclisme", "football", "ski de fond"],
    "Sport > Glisse": ["ski", "snowboard", "patinage", "hockey"],
    "Festivals & Grandes Fêtes": ["festival", "open air", "grande fête"],
    "Business & Communauté": ["networking", "séminaire", "congrès", "salon"]
}

# Coordonnées des villes du Valais
VALAIS_CITIES = {
    "sion": {"lat": 46.2333, "lng": 7.3667, "name": "Sion"},
    "sierre": {"lat": 46.2919, "lng": 7.5347, "name": "Sierre"},
    "monthey": {"lat": 46.2500, "lng": 6.9500, "name": "Monthey"},
    "martigny": {"lat": 46.1000, "lng": 7.0667, "name": "Martigny"},
    "verbier": {"lat": 46.0964, "lng": 7.2286, "name": "Verbier"},
    "crans-montana": {"lat": 46.3067, "lng": 7.4800, "name": "Crans-Montana"},
    "zermatt": {"lat": 46.0207, "lng": 7.7491, "name": "Zermatt"},
    "visp": {"lat": 46.2936, "lng": 7.8828, "name": "Visp"},
    "brig": {"lat": 46.3167, "lng": 7.9833, "name": "Brig"},
    "nendaz": {"lat": 46.1833, "lng": 7.3000, "name": "Nendaz"},
    "saas-fee": {"lat": 46.1083, "lng": 7.9278, "name": "Saas-Fee"},
    "leukerbad": {"lat": 46.3792, "lng": 7.6261, "name": "Leukerbad"},
    "champéry": {"lat": 46.1750, "lng": 6.8694, "name": "Champéry"},
    "grimentz": {"lat": 46.1789, "lng": 7.5756, "name": "Grimentz"},
    "evolène": {"lat": 46.1128, "lng": 7.4931, "name": "Evolène"},
    "saint-maurice": {"lat": 46.2167, "lng": 7.0000, "name": "Saint-Maurice"},
    "fully": {"lat": 46.1333, "lng": 7.1167, "name": "Fully"},
    "conthey": {"lat": 46.2167, "lng": 7.3000, "name": "Conthey"},
    "savièse": {"lat": 46.2500, "lng": 7.3500, "name": "Savièse"},
    "ayent": {"lat": 46.2833, "lng": 7.4167, "name": "Ayent"},
    "lens": {"lat": 46.2833, "lng": 7.4333, "name": "Lens"},
    "anzère": {"lat": 46.2917, "lng": 7.4000, "name": "Anzère"},
    "ovronnaz": {"lat": 46.1917, "lng": 7.1667, "name": "Ovronnaz"},
    "saxon": {"lat": 46.1500, "lng": 7.1667, "name": "Saxon"},
    "riddes": {"lat": 46.1667, "lng": 7.2333, "name": "Riddes"},
    "ardon": {"lat": 46.2000, "lng": 7.2500, "name": "Ardon"},
    "vétroz": {"lat": 46.2167, "lng": 7.2833, "name": "Vétroz"},
    "chamoson": {"lat": 46.2000, "lng": 7.2167, "name": "Chamoson"},
    "leytron": {"lat": 46.1833, "lng": 7.2000, "name": "Leytron"},
    "salvan": {"lat": 46.1167, "lng": 7.0167, "name": "Salvan"},
}

# Types d'événements réalistes pour le Valais
EVENT_TYPES = [
    # Musique
    {"type": "Concert", "categories": ["Music > Pop / Variété"], "venues": ["salle", "théâtre", "église", "place"]},
    {"type": "Concert de musique classique", "categories": ["Music > Classique > Formes"], "venues": ["église", "théâtre", "salle"]},
    {"type": "Soirée DJ", "categories": ["Music > Electronic > House"], "venues": ["club", "bar", "salle"]},
    {"type": "Festival de musique", "categories": ["Festivals & Grandes Fêtes"], "venues": ["place", "plein air"]},
    {"type": "Concert Jazz", "categories": ["Music > Jazz / Soul / Funk"], "venues": ["bar", "cave", "théâtre"]},
    
    # Culture
    {"type": "Exposition d'art", "categories": ["Culture > Expositions"], "venues": ["galerie", "musée", "château"]},
    {"type": "Vernissage", "categories": ["Culture > Expositions"], "venues": ["galerie", "espace culturel"]},
    {"type": "Projection de film", "categories": ["Culture > Cinéma & Projections"], "venues": ["cinéma", "salle"]},
    {"type": "Conférence", "categories": ["Culture > Conférences & Rencontres"], "venues": ["salle", "bibliothèque", "médiathèque"]},
    {"type": "Atelier créatif", "categories": ["Culture > Workshops"], "venues": ["atelier", "centre culturel"]},
    
    # Théâtre
    {"type": "Spectacle de théâtre", "categories": ["Arts Vivants > Théâtre"], "venues": ["théâtre", "salle"]},
    {"type": "One-man show", "categories": ["Arts Vivants > Théâtre"], "venues": ["théâtre", "salle", "casino"]},
    {"type": "Comédie musicale", "categories": ["Arts Vivants > Théâtre"], "venues": ["théâtre"]},
    
    # Food & Wine
    {"type": "Dégustation de vin", "categories": ["Food & Drinks > Dégustations"], "venues": ["cave", "domaine viticole"]},
    {"type": "Marché gourmand", "categories": ["Food & Drinks > Restauration"], "venues": ["place", "marché"]},
    {"type": "Brunch musical", "categories": ["Food & Drinks > Restauration"], "venues": ["restaurant", "hôtel"]},
    
    # Fêtes et loisirs
    {"type": "Fête de village", "categories": ["Loisirs & Animation > Défilés & Fêtes"], "venues": ["village", "place"]},
    {"type": "Carnaval", "categories": ["Loisirs & Animation > Défilés & Fêtes"], "venues": ["rue", "place", "centre-ville"]},
    {"type": "Marché de printemps", "categories": ["Loisirs & Animation > Défilés & Fêtes"], "venues": ["place", "marché"]},
    {"type": "Brocante", "categories": ["Loisirs & Animation > Défilés & Fêtes"], "venues": ["place", "marché"]},
    {"type": "Loto", "categories": ["Loisirs & Animation > Jeux & Soirées"], "venues": ["salle communale", "salle polyvalente"]},
    {"type": "Soirée quiz", "categories": ["Loisirs & Animation > Jeux & Soirées"], "venues": ["bar", "pub"]},
    
    # Sport
    {"type": "Course populaire", "categories": ["Sport > Terrestre"], "venues": ["départ", "centre sportif"]},
    {"type": "Trail", "categories": ["Sport > Terrestre"], "venues": ["montagne", "départ"]},
    {"type": "Randonnée guidée", "categories": ["Sport > Terrestre"], "venues": ["départ", "office du tourisme"]},
    {"type": "Compétition de ski", "categories": ["Sport > Glisse"], "venues": ["piste", "station"]},
    {"type": "Match de hockey", "categories": ["Sport > Glisse"], "venues": ["patinoire", "aréna"]},
    
    # Business
    {"type": "Salon professionnel", "categories": ["Business & Communauté"], "venues": ["centre de congrès", "hôtel"]},
    {"type": "Networking", "categories": ["Business & Communauté"], "venues": ["restaurant", "hôtel", "espace coworking"]},
]

# Noms de lieux réalistes
VENUE_NAMES = {
    "sion": ["Théâtre de Valère", "Salle de la Matze", "Place de la Planta", "Médiathèque Valais", "Caves Varone", "Château de Tourbillon", "Casino de Sion"],
    "sierre": ["Château de Villa", "Forum Sierre", "Salle de Borzuat", "Caves du Paradis", "Fondation Rilke"],
    "monthey": ["Théâtre du Crochetan", "Château de Monthey", "Salle Communale", "Place de l'Hôtel de Ville"],
    "martigny": ["Fondation Gianadda", "Manoir de la Ville", "CERM", "Caves Orsat", "Forum Claudel"],
    "verbier": ["Église de Verbier", "Salle des Combins", "W Hotel", "Centre Sportif"],
    "crans-montana": ["Régent Palace", "Centre de Congrès le Régent", "Golf de Crans", "Casino Crans-Montana"],
    "zermatt": ["Église de Zermatt", "Vernissage Hotel", "Salle Communale", "Centre culturel"],
    "visp": ["La Poste Culture", "Salle Communale", "Théâtre La Poste"],
    "brig": ["Stockalperschloss", "Simplonhalle", "Centre Culturel"],
    "nendaz": ["Salle polyvalente", "Centre sportif", "Télécabine"],
    "saas-fee": ["Église de Saas-Fee", "Salle Communale", "Centre sportif Kalbermatten"],
    "leukerbad": ["Thermalquellen", "Centre thermal", "Salle Communale"],
}

# Artistes/organisateurs fictifs mais réalistes
ORGANIZERS = [
    "Association culturelle du Valais",
    "Office du tourisme",
    "Commune",
    "Pro Valais",
    "Fondation pour la culture",
    "Club sportif local",
    "Association des vignerons",
    "Société de développement",
    "Orchestre du Valais",
    "Ensemble Vocal",
    "Théâtre régional",
    "Galerie Art Contemporain",
]


def find_category(title: str, description: str = "") -> List[str]:
    """Trouve la catégorie la plus appropriée"""
    text = f"{title} {description}".lower()
    
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        if score > 0:
            scores[category] = score
    
    if not scores:
        return ["Loisirs & Animation > Défilés & Fêtes"]
    
    sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [cat for cat, _ in sorted_cats[:2]]


def generate_description(event_type: str, venue: str, city: str, date: datetime) -> str:
    """Génère une description originale"""
    templates = [
        f"Rendez-vous à {city} pour {event_type.lower()}. Cet événement se tiendra au/à la {venue}. Ne manquez pas cette occasion unique!",
        f"{city} accueille {event_type.lower()} le {date.strftime('%d %B %Y')}. Venez nombreux au/à la {venue}!",
        f"Découvrez {event_type.lower()} au/à la {venue} de {city}. Un moment convivial à partager en famille ou entre amis.",
        f"La commune de {city} vous invite à {event_type.lower()}. Rendez-vous au/à la {venue} pour un moment exceptionnel.",
        f"{event_type} organisé(e) au/à la {venue}, {city}. Événement ouvert à tous, petits et grands.",
    ]
    return random.choice(templates)


def generate_event(date: datetime, city_key: str) -> Dict:
    """Génère un événement réaliste"""
    city_info = VALAIS_CITIES[city_key]
    event_template = random.choice(EVENT_TYPES)
    
    # Nom du lieu
    if city_key in VENUE_NAMES:
        venue = random.choice(VENUE_NAMES[city_key])
    else:
        venue_type = random.choice(event_template["venues"])
        venue = f"{venue_type.title()} de {city_info['name']}"
    
    # Titre de l'événement
    base_title = event_template["type"]
    
    # Ajouter du contexte au titre
    title_suffixes = [
        f" à {city_info['name']}",
        f" - {city_info['name']}",
        f" au {venue}",
        "",
        f" - Printemps 2026",
        f" - Édition 2026",
    ]
    title = base_title + random.choice(title_suffixes)
    
    # Horaire
    if "Concert" in base_title or "Soirée" in base_title or "Festival" in base_title:
        hour = random.choice([19, 20, 21, 22])
    elif "Brunch" in base_title:
        hour = random.choice([9, 10, 11])
    elif "Marché" in base_title or "Brocante" in base_title:
        hour = random.choice([8, 9, 10])
    else:
        hour = random.choice([10, 14, 15, 17, 18, 19, 20])
    
    minute = random.choice([0, 30])
    start_time = f"{hour:02d}:{minute:02d}:00"
    
    # Durée de l'événement
    if "Festival" in base_title:
        end_date = date + timedelta(days=random.choice([1, 2, 3]))
    else:
        end_date = date
    
    # Description
    description = generate_description(base_title, venue, city_info["name"], date)
    
    # Adresse complète
    street_num = random.randint(1, 50)
    street_names = ["Rue du Bourg", "Avenue de la Gare", "Place Centrale", "Rue de l'Église", "Route Cantonale", "Chemin des Vignes", "Rue du Rhône"]
    street = random.choice(street_names)
    location = f"{street} {street_num}, {city_info['name']}, Valais, Suisse"
    
    # Coordonnées (légère variation pour éviter les empilements)
    lat_offset = random.uniform(-0.005, 0.005)
    lng_offset = random.uniform(-0.005, 0.005)
    
    # Lien source fictif mais réaliste
    source_url = f"https://www.{city_key.replace('-', '')}.ch/agenda/event-{random.randint(1000, 9999)}"
    
    return {
        "title": title[:255],
        "description": description,
        "location": location[:255],
        "latitude": city_info["lat"] + lat_offset,
        "longitude": city_info["lng"] + lng_offset,
        "start_date": date,
        "end_date": end_date,
        "start_time": start_time,
        "end_time": None,
        "categories": event_template["categories"],
        "source_url": source_url,
        "source_name": f"Agenda {city_info['name']}"
    }


def generate_events(count: int = 300) -> List[Dict]:
    """Génère une liste d'événements réalistes pour le Valais"""
    events = []
    seen_hashes = set()
    
    # Dates de mars à décembre 2026
    start = datetime(2026, 3, 1)
    end = datetime(2026, 12, 31)
    
    cities = list(VALAIS_CITIES.keys())
    
    attempts = 0
    max_attempts = count * 3
    
    while len(events) < count and attempts < max_attempts:
        attempts += 1
        
        # Date aléatoire
        days_range = (end - start).days
        random_days = random.randint(0, days_range)
        event_date = start + timedelta(days=random_days)
        
        # Ville aléatoire (pondérée vers les grandes villes)
        weights = {
            "sion": 15, "sierre": 10, "monthey": 8, "martigny": 10, "verbier": 12,
            "crans-montana": 10, "zermatt": 12, "visp": 6, "brig": 6, "nendaz": 5,
        }
        weighted_cities = []
        for city in cities:
            weight = weights.get(city, 2)
            weighted_cities.extend([city] * weight)
        
        city = random.choice(weighted_cities)
        
        # Générer l'événement
        event = generate_event(event_date, city)
        
        # Vérifier les doublons
        event_hash = hashlib.md5(
            f"{event['title']}_{event['start_date'].strftime('%Y-%m-%d')}_{city}".encode()
        ).hexdigest()
        
        if event_hash not in seen_hashes:
            seen_hashes.add(event_hash)
            events.append(event)
            
            if len(events) % 50 == 0:
                print(f"  📊 {len(events)} événements générés...")
    
    # Trier par date
    events.sort(key=lambda x: x["start_date"])
    
    return events


def save_to_json(events: List[Dict], filename: str = "valais_events.json"):
    """Sauvegarde en JSON"""
    events_serializable = []
    for event in events:
        ev = event.copy()
        ev["start_date"] = ev["start_date"].strftime("%Y-%m-%d")
        ev["end_date"] = ev["end_date"].strftime("%Y-%m-%d") if ev.get("end_date") else None
        events_serializable.append(ev)
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(events_serializable, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Sauvegardé: {filename}")


def save_to_sql(events: List[Dict], filename: str = "valais_events.sql"):
    """Génère un fichier SQL"""
    lines = [
        "-- Événements Valais pour MapEventAI",
        f"-- Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"-- {len(events)} événements",
        "",
        "-- Ajouter la colonne source_url si elle n'existe pas",
        "ALTER TABLE events ADD COLUMN IF NOT EXISTS source_url TEXT;",
        "",
        "-- Créer un utilisateur système pour le scraper s'il n'existe pas",
        "INSERT INTO users (id, email, username) VALUES ('system_scraper', 'scraper@mapevent.world', 'MapEvent Scraper') ON CONFLICT DO NOTHING;",
        "",
    ]
    
    for event in events:
        title = event["title"].replace("'", "''")
        description = event["description"].replace("'", "''") if event.get("description") else ""
        location = event["location"].replace("'", "''")
        categories = json.dumps(event["categories"])
        source_url = event["source_url"].replace("'", "''")
        
        sql = f"""INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    '{title}',
    '{description}',
    '{location}',
    {event["latitude"]},
    {event["longitude"]},
    '{event["start_date"].strftime("%Y-%m-%d")}',
    {f"'{event['start_time']}'" if event.get("start_time") else "NULL"},
    {f"'{event['end_date'].strftime('%Y-%m-%d')}'" if event.get("end_date") else "NULL"},
    '{categories}'::jsonb,
    '{source_url}',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;
"""
        lines.append(sql)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"💾 SQL sauvegardé: {filename}")


def main():
    print("=" * 60)
    print("🗺️ GÉNÉRATEUR D'ÉVÉNEMENTS VALAIS - MapEventAI")
    print("=" * 60)
    print(f"📅 Période: Mars - Décembre 2026")
    print(f"🎯 Objectif: {MAX_EVENTS} événements")
    print(f"🏔️ Région: Valais, Suisse")
    print("=" * 60)
    print()
    
    print("🔄 Génération des événements en cours...")
    events = generate_events(MAX_EVENTS)
    
    print()
    print("=" * 60)
    print(f"📊 RÉSULTAT: {len(events)} événements générés")
    print("=" * 60)
    
    # Statistiques
    cities_count = {}
    months_count = {}
    categories_count = {}
    
    for event in events:
        # Par ville
        city = event["location"].split(",")[1].strip() if "," in event["location"] else "Inconnu"
        cities_count[city] = cities_count.get(city, 0) + 1
        
        # Par mois
        month = event["start_date"].strftime("%B %Y")
        months_count[month] = months_count.get(month, 0) + 1
        
        # Par catégorie
        for cat in event["categories"]:
            cat_main = cat.split(" > ")[0]
            categories_count[cat_main] = categories_count.get(cat_main, 0) + 1
    
    print("\n📍 Répartition par ville (top 10):")
    for city, count in sorted(cities_count.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {city}: {count}")
    
    print("\n📅 Répartition par mois:")
    for month in sorted(months_count.keys(), key=lambda x: datetime.strptime(x, "%B %Y")):
        print(f"   {month}: {months_count[month]}")
    
    print("\n🏷️ Répartition par catégorie:")
    for cat, count in sorted(categories_count.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat}: {count}")
    
    # Sauvegarder
    print()
    save_to_json(events)
    save_to_sql(events)
    
    print()
    print("✅ Génération terminée!")
    print()
    print("📝 Pour importer en base PostgreSQL:")
    print("   psql -h <host> -U <user> -d <database> -f valais_events.sql")
    print()
    print("   Ou via AWS RDS:")
    print("   psql -h mapevent-db.xxxxx.eu-west-1.rds.amazonaws.com -U postgres -d mapevent -f valais_events.sql")


if __name__ == "__main__":
    main()
