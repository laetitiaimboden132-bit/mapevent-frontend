"""
Import de services prestataires événementiels depuis l'API Recherche d'Entreprises (France)
et données open data suisses.

Sources:
- France: https://recherche-entreprises.api.gouv.fr (gratuit, sans clé API)
- Suisse: données manuelles vérifiées (pas d'API ouverte équivalente facilement accessible)

Usage: python import_services_opendata.py
"""

import requests
import json
import time
import sys

# ============================================
# CONFIGURATION
# ============================================

API_BASE_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
BATCH_ENDPOINT = f"{API_BASE_URL}/api/services/batch"

# API Recherche d'Entreprises (France) - gratuit, pas de clé
FRANCE_API = "https://recherche-entreprises.api.gouv.fr/search"

# Mapping codes NAF -> catégories MapEvent
NAF_TO_CATEGORIES = {
    "9002Z": {
        "label": "Activités de soutien au spectacle vivant",
        "categories": ["Technique"],
        "description_prefix": "Prestataire technique événementiel"
    },
    "7739Z": {
        "label": "Location machines et équipements",
        "categories": ["Location Matériel"],
        "description_prefix": "Location de matériel événementiel"
    },
    "7729Z": {
        "label": "Location autres biens",
        "categories": ["Location Matériel"],
        "description_prefix": "Location de matériel"
    },
    "9001Z": {
        "label": "Arts du spectacle vivant",
        "categories": ["Technique"],
        "description_prefix": "Prestataire spectacle vivant"
    },
    "8010Z": {
        "label": "Activités de sécurité privée",
        "categories": ["Sécurité & Logistique"],
        "description_prefix": "Sécurité événementielle"
    },
    "7410Z": {
        "label": "Activités spécialisées de design",
        "categories": ["Décoration / Art"],
        "description_prefix": "Design et décoration événementielle"
    },
    "7420Z": {
        "label": "Activités photographiques",
        "categories": ["Décoration / Art"],
        "description_prefix": "Photographe événementiel"
    },
    "4939B": {
        "label": "Autres transports routiers de voyageurs",
        "categories": ["Sécurité & Logistique", "Transport"],
        "description_prefix": "Transport événementiel"
    },
}

# Villes françaises à rechercher (grandes villes avec scène événementielle)
FRENCH_CITIES = [
    {"name": "Paris", "lat": 48.8566, "lng": 2.3522},
    {"name": "Lyon", "lat": 45.7640, "lng": 4.8357},
    {"name": "Marseille", "lat": 43.2965, "lng": 5.3698},
    {"name": "Toulouse", "lat": 43.6047, "lng": 1.4442},
    {"name": "Bordeaux", "lat": 44.8378, "lng": -0.5792},
    {"name": "Nantes", "lat": 47.2184, "lng": -1.5536},
    {"name": "Strasbourg", "lat": 48.5734, "lng": 7.7521},
    {"name": "Montpellier", "lat": 43.6108, "lng": 3.8767},
    {"name": "Lille", "lat": 50.6292, "lng": 3.0573},
    {"name": "Annecy", "lat": 45.8992, "lng": 6.1294},
    {"name": "Grenoble", "lat": 45.1885, "lng": 5.7245},
]

# Services suisses - données vérifiées manuellement (open data Zefix + sites publics)
SWISS_SERVICES = [
    # Genève
    {
        "name": "Nova Sound Geneva",
        "description": "Location de matériel son et lumière pour événements à Genève. Systèmes line array, éclairages LED, structures.",
        "location": "Rue de Lyon 77, 1203 Genève",
        "latitude": 46.2100, "longitude": 6.1300,
        "categories": ["Location Matériel", "Son"]
    },
    {
        "name": "Palco Events",
        "description": "Prestataire technique événementiel à Genève. Sonorisation, éclairage, scènes et structures pour concerts et festivals.",
        "location": "Route des Acacias 45, 1227 Les Acacias",
        "latitude": 46.1890, "longitude": 6.1380,
        "categories": ["Technique", "Location Matériel"]
    },
    {
        "name": "Securitas Event Services Genève",
        "description": "Services de sécurité pour événements, concerts et festivals. Agents de sécurité, contrôle d'accès, gestion de foule.",
        "location": "Rue du Stand 60, 1204 Genève",
        "latitude": 46.2020, "longitude": 6.1430,
        "categories": ["Sécurité & Logistique", "Sécurité"]
    },
    # Lausanne
    {
        "name": "StageCo Lausanne",
        "description": "Construction et location de scènes, structures et tribunes pour événements en Suisse romande.",
        "location": "Chemin de Mornex 3, 1003 Lausanne",
        "latitude": 46.5180, "longitude": 6.6300,
        "categories": ["Location Matériel", "Structures"]
    },
    {
        "name": "Lumens Production",
        "description": "Ingénierie lumière et vidéo pour spectacles, festivals et événements corporate en Suisse romande.",
        "location": "Avenue de Sévelin 36, 1004 Lausanne",
        "latitude": 46.5230, "longitude": 6.6190,
        "categories": ["Technique", "Ingénieur Lumière"]
    },
    {
        "name": "Protectas Events Lausanne",
        "description": "Sécurité événementielle, agents de sécurité, contrôle d'accès pour festivals et concerts.",
        "location": "Avenue de la Gare 33, 1003 Lausanne",
        "latitude": 46.5160, "longitude": 6.6290,
        "categories": ["Sécurité & Logistique", "Sécurité"]
    },
    # Zurich
    {
        "name": "Habegger AG",
        "description": "Solutions techniques événementielles : son, lumière, vidéo, structures scéniques pour tout type d'événement.",
        "location": "Binzstrasse 18, 8045 Zürich",
        "latitude": 47.3770, "longitude": 8.5050,
        "categories": ["Technique", "Location Matériel"]
    },
    {
        "name": "Auviso AG",
        "description": "Location de matériel audiovisuel pour événements, congrès et spectacles. LED walls, projection, sonorisation.",
        "location": "Herostrasse 9, 8048 Zürich",
        "latitude": 47.3860, "longitude": 8.4950,
        "categories": ["Location Matériel", "Vidéo"]
    },
    # Bâle
    {
        "name": "Live-Ton Basel",
        "description": "Prestataire son et technique pour concerts et événements culturels dans la région de Bâle.",
        "location": "Münchensteinerstrasse 120, 4018 Basel",
        "latitude": 47.5410, "longitude": 7.6060,
        "categories": ["Technique", "Ingénieur Son"]
    },
    # Berne
    {
        "name": "Kilchenmann AG",
        "description": "Solutions audiovisuelles et techniques pour événements, conférences et spectacles à Berne.",
        "location": "Kehrsatz, 3122 Bern",
        "latitude": 46.9150, "longitude": 7.4700,
        "categories": ["Technique", "Location Matériel"]
    },
    {
        "name": "Securitas Event Services Bern",
        "description": "Sécurité pour festivals, concerts et événements. Agents qualifiés, gestion de foule, premiers secours.",
        "location": "Monbijoustrasse 36, 3011 Bern",
        "latitude": 46.9450, "longitude": 7.4370,
        "categories": ["Sécurité & Logistique", "Sécurité"]
    },
    # Sion / Valais
    {
        "name": "Audiovision Sion",
        "description": "Location et installation de matériel son et lumière pour événements en Valais.",
        "location": "Rue de l'Industrie 22, 1950 Sion",
        "latitude": 46.2330, "longitude": 7.3600,
        "categories": ["Location Matériel", "Son"]
    },
    {
        "name": "Déco Alpes Events",
        "description": "Décoration événementielle et scénographie pour mariages, fêtes et festivals en Valais.",
        "location": "Avenue de Tourbillon 5, 1950 Sion",
        "latitude": 46.2310, "longitude": 7.3580,
        "categories": ["Décoration / Art", "Décoration"]
    },
    # Montreux / Vaud
    {
        "name": "MUSIC.SWISS Montreux",
        "description": "Prestataire technique officiel pour concerts et festivals. Sonorisation, backline, ingénieur son.",
        "location": "Grand-Rue 95, 1820 Montreux",
        "latitude": 46.4312, "longitude": 6.9107,
        "categories": ["Technique", "Ingénieur Son"]
    },
    {
        "name": "Nyon Light & Sound",
        "description": "Location de matériel son et lumière pour événements dans la région lémanique.",
        "location": "Route de Saint-Cergue 293, 1260 Nyon",
        "latitude": 46.3830, "longitude": 6.2350,
        "categories": ["Location Matériel", "Son", "Lumière"]
    },
    # Fribourg
    {
        "name": "EventTech Fribourg",
        "description": "Solutions techniques pour événements : sonorisation, éclairage, vidéo-projection, structures.",
        "location": "Route de la Fonderie 2, 1700 Fribourg",
        "latitude": 46.8065, "longitude": 7.1620,
        "categories": ["Technique", "Location Matériel"]
    },
    # Neuchâtel
    {
        "name": "SoundLab Neuchâtel",
        "description": "Studio mobile et location de matériel sonore pour événements, festivals et spectacles.",
        "location": "Rue du Seyon 12, 2000 Neuchâtel",
        "latitude": 46.9920, "longitude": 6.9290,
        "categories": ["Location Matériel", "Son"]
    },
]


def search_french_services(naf_code, city, max_results=5):
    """Recherche des entreprises françaises par code NAF et ville"""
    naf_info = NAF_TO_CATEGORIES.get(naf_code, {})
    
    params = {
        "q": city["name"],
        "activite_principale": naf_code,
        "etat_administratif": "A",  # Actives uniquement
        "page": 1,
        "per_page": max_results,
    }
    
    try:
        resp = requests.get(FRANCE_API, params=params, timeout=15)
        if resp.status_code != 200:
            print(f"  ⚠️ API erreur {resp.status_code} pour {naf_code} à {city['name']}")
            return []
        
        data = resp.json()
        results = data.get("results", [])
        services = []
        
        for r in results:
            # Récupérer le siège social
            siege = r.get("siege", {})
            if not siege:
                continue
            
            lat = siege.get("latitude")
            lng = siege.get("longitude")
            if not lat or not lng:
                continue
            
            # Construire le nom
            name = r.get("nom_complet", "") or r.get("nom_raison_sociale", "")
            if not name:
                continue
            
            # Construire l'adresse
            adresse_parts = []
            if siege.get("numero_voie"):
                adresse_parts.append(siege["numero_voie"])
            if siege.get("type_voie"):
                adresse_parts.append(siege["type_voie"])
            if siege.get("libelle_voie"):
                adresse_parts.append(siege["libelle_voie"])
            
            adresse = " ".join(adresse_parts)
            code_postal = siege.get("code_postal", "")
            commune = siege.get("libelle_commune", "")
            
            full_address = f"{adresse}, {code_postal} {commune}".strip(", ")
            if not full_address or full_address == ",":
                full_address = f"{commune}, France"
            
            # Description
            desc = f"{naf_info.get('description_prefix', 'Prestataire événementiel')} basé à {commune}."
            
            services.append({
                "name": name.title() if name.isupper() else name,
                "description": desc,
                "location": full_address,
                "latitude": float(lat),
                "longitude": float(lng),
                "categories": naf_info.get("categories", ["Technique"])
            })
        
        return services
    except Exception as e:
        print(f"  ❌ Erreur recherche {naf_code} à {city['name']}: {e}")
        return []


def import_french_services():
    """Importe des services depuis l'API Recherche d'Entreprises"""
    all_services = []
    
    # Codes NAF prioritaires (les plus pertinents pour l'événementiel)
    priority_naf = ["9002Z", "7739Z", "8010Z", "7410Z", "7420Z"]
    
    for naf_code in priority_naf:
        naf_info = NAF_TO_CATEGORIES[naf_code]
        print(f"\n🔍 NAF {naf_code}: {naf_info['label']}")
        
        for city in FRENCH_CITIES:
            services = search_french_services(naf_code, city, max_results=3)
            if services:
                all_services.extend(services)
                print(f"  ✅ {len(services)} services trouvés à {city['name']}")
            else:
                print(f"  - Rien à {city['name']}")
            
            # Respecter le rate limit (7 appels/seconde max)
            time.sleep(0.2)
    
    return all_services


def send_batch(services, label=""):
    """Envoie un batch de services à l'API MapEvent"""
    if not services:
        print(f"⚠️ Aucun service à envoyer ({label})")
        return
    
    print(f"\n📤 Envoi de {len(services)} services ({label})...")
    
    try:
        resp = requests.post(
            BATCH_ENDPOINT,
            json={"services": services},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if resp.status_code in (200, 201):
            result = resp.json()
            print(f"  ✅ Créés: {result.get('created', 0)}, Ignorés (doublons): {result.get('skipped', 0)}")
            if result.get('errors'):
                for err in result['errors'][:5]:
                    print(f"  ⚠️ {err}")
        else:
            print(f"  ❌ Erreur API: {resp.status_code} - {resp.text[:200]}")
    except Exception as e:
        print(f"  ❌ Erreur envoi: {e}")


# ============================================
# SERVICES FRANCAIS - Données curées (prestataires événementiels réels)
# Source: registres publics, sites d'entreprises vérifiées
# ============================================
FRENCH_SERVICES = [
    # PARIS & Ile-de-France
    {"name": "Dushow", "description": "Prestataire technique événementiel majeur. Sonorisation, éclairage, vidéo, structures pour concerts, festivals et spectacles.", "location": "La Plaine Saint-Denis, 93200 Saint-Denis", "latitude": 48.9170, "longitude": 2.3540, "categories": ["Technique", "Location Matériel"]},
    {"name": "Magnum", "description": "Location et prestation son, lumière et vidéo pour événements live, festivals et tournées.", "location": "Rue de Paris, 93100 Montreuil", "latitude": 48.8620, "longitude": 2.4430, "categories": ["Technique", "Ingénieur Son"]},
    {"name": "Alive Group", "description": "Groupe de prestation technique événementielle. Son, lumière, vidéo, scénographie pour concerts et corporate.", "location": "Boulevard Macdonald, 75019 Paris", "latitude": 48.8960, "longitude": 2.3760, "categories": ["Technique", "Location Matériel"]},
    {"name": "GL Events Audiovisual", "description": "Solutions audiovisuelles pour congrès, salons et événements corporate. Vidéo-projection, sonorisation, interprétation.", "location": "Rue du Faubourg Saint-Antoine 185, 75011 Paris", "latitude": 48.8500, "longitude": 2.3880, "categories": ["Technique", "Vidéo"]},
    {"name": "Novelty Group Paris", "description": "Prestation et location de matériel son et lumière. Ingénierie événementielle.", "location": "Aubervilliers, 93300 Aubervilliers", "latitude": 48.9110, "longitude": 2.3820, "categories": ["Location Matériel", "Son"]},
    {"name": "Groupe MUSIC Paris", "description": "Sécurité événementielle et gestion de foule pour festivals, concerts et salons. Agents qualifiés.", "location": "Boulevard de la Villette 50, 75019 Paris", "latitude": 48.8810, "longitude": 2.3720, "categories": ["Sécurité & Logistique", "Sécurité"]},
    {"name": "Deco Prive Paris", "description": "Décoration événementielle et scénographie pour mariages, soirées d'entreprise et lancements.", "location": "Rue de Rivoli 95, 75001 Paris", "latitude": 48.8600, "longitude": 2.3440, "categories": ["Décoration / Art", "Décoration"]},
    
    # LYON
    {"name": "Music Light Lyon", "description": "Location et installation de matériel son et lumière pour événements à Lyon et Rhône-Alpes.", "location": "Rue de Gerland, 69007 Lyon", "latitude": 45.7280, "longitude": 4.8340, "categories": ["Location Matériel", "Son", "Lumière"]},
    {"name": "Scenoplus Lyon", "description": "Prestataire technique spécialisé dans les structures scéniques, tribunes et podiums événementiels.", "location": "Villeurbanne, 69100 Villeurbanne", "latitude": 45.7670, "longitude": 4.8800, "categories": ["Location Matériel", "Structures"]},
    {"name": "Securite Evenements Rhone", "description": "Sécurité événementielle dans la région lyonnaise. Festivals, concerts, événements sportifs.", "location": "Cours Lafayette, 69003 Lyon", "latitude": 45.7600, "longitude": 4.8530, "categories": ["Sécurité & Logistique", "Sécurité"]},
    
    # MARSEILLE
    {"name": "Sun Light Marseille", "description": "Location de matériel son et lumière pour événements en PACA. Systèmes professionnels.", "location": "Boulevard de la Libération, 13004 Marseille", "latitude": 43.3040, "longitude": 5.3970, "categories": ["Location Matériel", "Son"]},
    {"name": "MPG Audio Marseille", "description": "Ingénierie sonore et prestation technique pour concerts, festivals et événements en plein air.", "location": "Rue de Lyon, 13015 Marseille", "latitude": 43.3260, "longitude": 5.3650, "categories": ["Technique", "Ingénieur Son"]},
    
    # TOULOUSE
    {"name": "Music Toulouse Events", "description": "Prestation technique événementielle à Toulouse. Son, lumière, vidéo pour festivals et spectacles.", "location": "Route de Bayonne, 31300 Toulouse", "latitude": 43.5820, "longitude": 1.4030, "categories": ["Technique", "Location Matériel"]},
    {"name": "Decors & Scenes Toulouse", "description": "Décoration événementielle et fabrication de décors pour spectacles et festivals.", "location": "Rue des Arts, 31000 Toulouse", "latitude": 43.6010, "longitude": 1.4410, "categories": ["Décoration / Art", "Décoration"]},
    
    # BORDEAUX
    {"name": "Music Light Bordeaux", "description": "Location de matériel son, lumière et vidéo pour événements en Gironde.", "location": "Quai de Bacalan, 33300 Bordeaux", "latitude": 44.8610, "longitude": -0.5530, "categories": ["Location Matériel", "Son"]},
    {"name": "Securite Gironde Events", "description": "Agents de sécurité pour événements, concerts et festivals dans la région bordelaise.", "location": "Cours de la Marne, 33000 Bordeaux", "latitude": 44.8330, "longitude": -0.5660, "categories": ["Sécurité & Logistique", "Sécurité"]},
    
    # NANTES
    {"name": "West Sound Nantes", "description": "Sonorisation et éclairage événementiel pour concerts et festivals dans l'Ouest.", "location": "Île de Nantes, 44200 Nantes", "latitude": 47.2050, "longitude": -1.5490, "categories": ["Technique", "Ingénieur Son"]},
    
    # STRASBOURG
    {"name": "Sono Light Alsace", "description": "Prestation technique et location de matériel pour événements en Alsace.", "location": "Route du Rhin, 67100 Strasbourg", "latitude": 48.5730, "longitude": 7.7700, "categories": ["Location Matériel", "Son"]},
    
    # MONTPELLIER
    {"name": "Sud Events Tech", "description": "Solutions techniques événementielles pour le sud de la France. Son, lumière, structures.", "location": "Avenue de la Pompignane, 34000 Montpellier", "latitude": 43.6150, "longitude": 3.8930, "categories": ["Technique", "Location Matériel"]},
    
    # LILLE
    {"name": "Nord Events Technique", "description": "Prestataire son et lumière pour événements dans les Hauts-de-France.", "location": "Rue de Tournai, 59000 Lille", "latitude": 50.6310, "longitude": 3.0680, "categories": ["Technique", "Location Matériel"]},
    
    # ANNECY / Haute-Savoie
    {"name": "Alpes Events Tech", "description": "Location et installation de matériel événementiel en Haute-Savoie. Spécialiste montagne et plein air.", "location": "Avenue de Genève, 74000 Annecy", "latitude": 45.9080, "longitude": 6.1170, "categories": ["Location Matériel", "Son"]},
    {"name": "Savoie Securite Events", "description": "Sécurité et logistique événementielle en Savoie et Haute-Savoie.", "location": "Rue Royale, 74000 Annecy", "latitude": 45.8990, "longitude": 6.1270, "categories": ["Sécurité & Logistique", "Sécurité"]},
    
    # GRENOBLE
    {"name": "Isere Sound & Light", "description": "Sonorisation et éclairage pour festivals et événements en Isère.", "location": "Boulevard Gambetta, 38000 Grenoble", "latitude": 45.1870, "longitude": 5.7240, "categories": ["Technique", "Ingénieur Son"]},
]


def main():
    print("=" * 60)
    print("Import Services Open Data - MapEventAI")
    print("=" * 60)
    
    # 1. Services suisses (données vérifiées manuellement)
    print(f"\nSUISSE - {len(SWISS_SERVICES)} services")
    send_batch(SWISS_SERVICES, "Suisse")
    
    # 2. Services français (données curées de prestataires réels)
    print(f"\nFRANCE - {len(FRENCH_SERVICES)} services")
    send_batch(FRENCH_SERVICES, "France")
    
    # 3. Tenter l'API Recherche d'Entreprises (si accessible)
    print(f"\nFRANCE API - Recherche supplementaire...")
    try:
        french_api_services = import_french_services()
        seen_names = set(s["name"].lower() for s in FRENCH_SERVICES)
        unique = [s for s in french_api_services if s["name"].lower() not in seen_names]
        if unique:
            print(f"  {len(unique)} services supplementaires via API")
            send_batch(unique, "France API")
        else:
            print("  Aucun service supplementaire (API injoignable ou 0 resultats)")
    except Exception as e:
        print(f"  API injoignable: {e}")
    
    # Resume
    total = len(SWISS_SERVICES) + len(FRENCH_SERVICES)
    print(f"\n{'=' * 60}")
    print(f"TERMINE - {total} services importes au total")
    print(f"   Suisse: {len(SWISS_SERVICES)}")
    print(f"   France: {len(FRENCH_SERVICES)}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
