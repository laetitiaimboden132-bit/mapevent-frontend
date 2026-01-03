#!/usr/bin/env python3
"""
Script pour géocoder les événements et les convertir en GeoJSON
Utilise Nominatim (OpenStreetMap) pour le géocodage gratuit
"""

import json
import time
import requests
from typing import Dict, List, Optional, Tuple

# Configuration
INPUT_FILE = "public/events_raw_data.json"
OUTPUT_FILE = "public/events_france_geocoded.geojson"

# Coordonnées prédéfinies pour les lieux célèbres (pour accélérer)
KNOWN_PLACES = {
    "marathon de paris": (2.320388, 48.865784, "Avenue des Champs-Élysées, Paris, France"),
    "roland-garros": (2.248418, 48.846869, "Stade Roland-Garros, Paris, France"),
    "24 heures du mans": (0.212505, 47.957801, "Circuit des 24 Heures du Mans, Le Mans, France"),
    "palais des festivals": (7.017658, 43.550685, "Palais des Festivals et des Congrès, Cannes, France"),
    "porte de versailles": (2.287854, 48.832462, "Paris Expo Porte de Versailles, Paris, France"),
    "hellfest": (-1.281742, 47.087722, "Clisson, France"),
    "palais des papes": (4.807287, 43.950631, "Palais des Papes, Avignon, France"),
    "lyon": (4.8357, 45.7640, "Lyon, France"),
    "francofolies": (-1.157911, 46.155480, "Esplanade Saint-Jean d'Acre, La Rochelle, France"),
    "citadelle arras": (2.7783, 50.2945, "Citadelle d'Arras, Arras, France"),
    "malsaucy": (6.8944, 47.7297, "Lac de Malsaucy, Sermamagny, France"),
    "nice": (7.237476, 43.685989, "Promenade des Anglais, Nice, France"),
    "angoulême": (0.1536, 45.6500, "Angoulême, France"),
    "saint-tropez": (6.637973, 43.271910, "Port de Saint-Tropez, Saint-Tropez, France"),
    "vienne": (4.8733, 45.5256, "Théâtre Antique, Vienne, France"),
    "bruz": (-1.7526, 48.0249, "Parc Expo Rennes Aéroport, Bruz, France"),
    "longchamp": (2.232981, 48.857738, "Hippodrome de Longchamp, Paris, France"),
    "pau": (-0.3708, 43.2951, "Circuit de Pau-Ville, Pau, France"),
    "bordeaux": (-0.5792, 44.8378, "Bordeaux, France"),
    "clermont-ferrand": (3.0870, 45.7772, "Clermont-Ferrand, France"),
    "toulouse": (1.4442, 43.6047, "Place du Capitole, Toulouse, France"),
    "villepinte": (2.5181, 48.9625, "Paris Nord Villepinte, Villepinte, France"),
    "strasbourg": (7.7521, 48.5734, "Place Kléber, Strasbourg, France"),
    "dijon": (5.0415, 47.3220, "Circuit Dijon-Prenois, Prenois, France"),
    "fourvière": (4.8223, 45.7617, "Théâtres Romains de Fourvière, Lyon, France"),
    "blagnac": (1.3874, 43.6332, "Blagnac, France"),
}

def geocode_address(address: str) -> Optional[Tuple[float, float, str]]:
    """
    Géocode une adresse en utilisant Nominatim (OpenStreetMap)
    Retourne (longitude, latitude, place_name) ou None
    """
    # Nettoyer l'adresse
    address_clean = address.strip()
    
    # Créer plusieurs variantes pour essayer
    variants = []
    
    # Variante 1: adresse complète avec "France"
    if ", France" not in address_clean.lower():
        variants.append(address_clean + ", France")
    else:
        variants.append(address_clean)
    
    # Variante 2: extraire juste la rue et la ville (sans les détails avant)
    # Exemple: "Départ Champs-Élysées / Arrivée Avenue Foch, 75008 / 75016 Paris" -> "Avenue Foch, 75016 Paris, France"
    import re
    # Chercher un code postal et une ville
    cp_match = re.search(r'(\d{5})\s+([A-Za-zÀ-ÿ\s\-]+)', address_clean)
    if cp_match:
        cp = cp_match.group(1)
        city = cp_match.group(2).strip().split(',')[0].strip()
        # Chercher une rue/nom de lieu
        # Prendre le dernier élément avant le code postal
        parts = address_clean.split(cp)
        if len(parts) > 0:
            street_part = parts[0].strip().split('/')[-1].strip()
            if street_part:
                variants.append(f"{street_part}, {cp} {city}, France")
        variants.append(f"{city}, {cp}, France")
        variants.append(f"{city}, France")
    
    # Variante 3: chercher un nom de lieu célèbre
    famous_places = {
        "Champs-Élysées": "Avenue des Champs-Élysées, Paris, France",
        "Roland-Garros": "Stade Roland-Garros, Paris, France",
        "Circuit des 24 Heures": "Circuit des 24 Heures du Mans, Le Mans, France",
        "Palais des Festivals": "Palais des Festivals et des Congrès, Cannes, France",
        "Hippodrome de Longchamp": "Hippodrome de Longchamp, Paris, France",
        "Circuit de Pau-Ville": "Circuit de Pau-Ville, Pau, France",
        "Presqu'île du Malsaucy": "Lac de Malsaucy, Sermamagny, France",
        "Citadelle d'Arras": "Citadelle d'Arras, Arras, France",
        "Port de Saint-Tropez": "Port de Saint-Tropez, Saint-Tropez, France",
        "Théâtre Antique de Vienne": "Théâtre Antique, Vienne, France",
        "Parc Expo Rennes Aéroport": "Parc des Expositions, Bruz, France",
        "Centre de Congrès / Cité de la BD": "Cité internationale de la bande dessinée, Angoulême, France",
        "Site du Hellfest": "Clisson, France",
        "Dans toute la Ville de Lyon": "Lyon, France",
        "Place du Capitole": "Place du Capitole, Toulouse, France",
        "Place Kléber": "Place Kléber, Strasbourg, France",
        "Circuit Dijon-Prenois": "Circuit de Dijon-Prenois, Prenois, France"
    }
    
    for key, place in famous_places.items():
        if key.lower() in address_clean.lower():
            variants.insert(0, place)  # Prioriser les lieux célèbres
    
    # URL de l'API Nominatim
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "MapEventAI Geocoder/1.0"  # Requis par Nominatim
    }
    
    # D'abord, vérifier si on a des coordonnées prédéfinies
    address_lower = address_clean.lower()
    for key, coords in KNOWN_PLACES.items():
        if key in address_lower:
            lon, lat, place_name = coords
            print(f"   ✅ Utilisation de coordonnées prédéfinies pour: {key}")
            return (lon, lat, place_name)
    
    # Essayer chaque variante
    for variant in variants:
        if not variant or not variant.strip():
            continue
            
        params = {
            "q": variant,
            "format": "json",
            "addressdetails": 1,
            "limit": 1,
            "countrycodes": "fr"  # Limiter à la France
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            # Respecter la limite de taux (1 requête/seconde)
            time.sleep(1.1)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    result = data[0]
                    lon = float(result["lon"])
                    lat = float(result["lat"])
                    place_name = result.get("display_name", variant)
                    return (lon, lat, place_name)
        except Exception as e:
            continue  # Essayer la variante suivante
    
    print(f"⚠️  Aucun résultat pour aucune variante de: {address_clean}")
    return None

def extract_city(address: str) -> str:
    """
    Extrait le nom de la ville depuis l'adresse
    """
    # Chercher le code postal (5 chiffres) et la ville qui suit
    import re
    match = re.search(r'\b(\d{5})\s+([A-Za-zÀ-ÿ\s\-]+),?\s*France?', address, re.IGNORECASE)
    if match:
        return match.group(2).strip()
    
    # Fallback: chercher une ville connue
    cities = ["Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes", "Strasbourg", 
              "Montpellier", "Bordeaux", "Lille", "Rennes", "Reims", "Le Havre",
              "Saint-Étienne", "Toulon", "Grenoble", "Dijon", "Angers", "Villeurbanne",
              "Le Mans", "Aix-en-Provence", "Clermont-Ferrand", "Brest", "Limoges",
              "Tours", "Amiens", "Perpignan", "Metz", "Besançon", "Boulogne-Billancourt",
              "Orléans", "Mulhouse", "Caen", "Rouen", "Nancy", "Saint-Denis", "Argenteuil",
              "Montreuil", "Roubaix", "Tourcoing", "Nanterre", "Avignon", "Créteil",
              "Dunkirk", "Poitiers", "Asnières-sur-Seine", "Versailles", "Courbevoie",
              "Vitry-sur-Seine", "Colombes", "Aulnay-sous-Bois", "La Rochelle", "Champigny-sur-Marne",
              "Rueil-Malmaison", "Antibes", "Saint-Maur-des-Fossés", "Cannes", "Bourges",
              "Drancy", "Mérignac", "Saint-Nazaire", "Colmar", "Issy-les-Moulineaux",
              "Noisy-le-Grand", "Évry", "Villeneuve-d'Ascq", "Pessac", "Valence",
              "Antony", "Cergy", "La Seyne-sur-Mer", "Clichy", "Ivry-sur-Seine",
              "Troyes", "Montauban", "Neuilly-sur-Seine", "Chambéry", "Pantin",
              "Niort", "Le Blanc-Mesnil", "Haguenau", "Lorient", "La Courneuve",
              "Bayonne", "Fontenay-sous-Bois", "Sartrouville", "Épinay-sur-Seine",
              "Belfort", "Évry-Courcouronnes", "Vincennes", "Sevran", "Clamart",
              "Bourg-en-Bresse", "Montrouge", "Bastia", "Saint-Ouen-sur-Seine",
              "Meaux", "Brive-la-Gaillarde", "Cholet", "Chartres", "Saint-Quentin",
              "Chalon-sur-Saône", "Narbonne", "Évreux", "Vannes", "Arles", "Gennevilliers",
              "Les Abymes", "Biarritz", "Thionville", "Massy", "Calais", "Talence",
              "Blois", "Puteaux", "Angoulême", "Douai", "Wattrelos", "Albi", "Mantes-la-Jolie",
              "Béziers", "Le Cannet", "Roanne", "Cagnes-sur-Mer", "Rochefort", "Tarbes",
              "Villepinte", "Saint-Priest", "Villeneuve-sur-Lot", "Bergerac", "Cognac",
              "Saint-Malo", "Clisson", "Arras", "Bruz", "Sermamagny", "Blagnac", "Pau",
              "Prenois", "Avignon", "Vienne", "Angoulême", "Le Mans", "Cannes"]
    
    for city in cities:
        if city.lower() in address.lower():
            return city
    
    return "Inconnu"

def convert_to_geojson(events: List[Dict]) -> Dict:
    """
    Convertit une liste d'événements en GeoJSON
    """
    features = []
    
    print(f"\n🔄 Géocodage de {len(events)} événements...\n")
    
    for i, event in enumerate(events, 1):
        titre = event.get("Titre de l'événement", "Sans titre")
        adresse = event.get("Adresse Complète (Lieu/Rue/CP/Ville)", "")
        lien = event.get("Lien de la Publication d'Origine", "")
        
        print(f"[{i}/{len(events)}] Géocodage: {titre}")
        print(f"   Adresse: {adresse}")
        
        # Géocoder l'adresse
        geocode_result = geocode_address(adresse)
        
        if geocode_result:
            lon, lat, place_name = geocode_result
            print(f"   ✅ Coordonnées: {lat:.6f}, {lon:.6f}")
            print(f"   📍 Lieu: {place_name[:80]}...")
            
            # Extraire la ville
            city = extract_city(adresse)
            
            # Créer la feature GeoJSON
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]  # GeoJSON: [longitude, latitude]
                },
                "properties": {
                    "Titre": titre,
                    "Adresse": adresse,
                    "Date Début": event.get("Date Début", ""),
                    "Heure Début": event.get("Heure Début", ""),
                    "Date Fin": event.get("Date Fin", ""),
                    "Heure Fin": event.get("Heure Fin", ""),
                    "Catégorie": event.get("Catégorie", ""),
                    "Lien": lien,  # Lien de la Publication d'Origine
                    "Lien de la Publication d'Origine": lien,  # Doublé pour compatibilité
                    "Email": event.get("Adresse Email Organisateur (Publique)", ""),
                    "city": city,
                    "place_name": place_name,
                    "geo_score": 1.0  # Score de confiance (1.0 = réussi)
                }
            }
            features.append(feature)
        else:
            print(f"   ❌ Échec du géocodage - événement ignoré")
        
        print()
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return geojson

def main():
    """
    Fonction principale
    """
    print("=" * 60)
    print("🗺️  GÉOCODAGE DES ÉVÉNEMENTS")
    print("=" * 60)
    
    # Charger les données brutes
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            events = json.load(f)
        print(f"\n✅ {len(events)} événements chargés depuis {INPUT_FILE}")
    except Exception as e:
        print(f"\n❌ Erreur lors du chargement de {INPUT_FILE}: {e}")
        return
    
    # Convertir en GeoJSON
    geojson = convert_to_geojson(events)
    
    # Sauvegarder le GeoJSON
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(geojson, f, ensure_ascii=False, indent=2)
        print(f"\n✅ GeoJSON sauvegardé dans {OUTPUT_FILE}")
        print(f"   {len(geojson['features'])} événements géocodés avec succès")
    except Exception as e:
        print(f"\n❌ Erreur lors de la sauvegarde de {OUTPUT_FILE}: {e}")
        return
    
    print("\n" + "=" * 60)
    print("✨ TERMINÉ")
    print("=" * 60)

if __name__ == "__main__":
    main()

