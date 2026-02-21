"""Audit complet des coordonnees de TOUS les events scraped.
Pour chaque event avec source_url, on verifie que les coordonnees
correspondent bien a l'adresse indiquee via Nominatim."""
import requests
import json
import time
import re

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

def geocode(address):
    """Geocode via Nominatim"""
    try:
        r = requests.get("https://nominatim.openstreetmap.org/search", params={
            "q": address,
            "format": "json",
            "limit": 1,
        }, headers={"User-Agent": "MapEventAI-Bot/1.0"}, timeout=15)
        results = r.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"]), results[0].get("display_name", "")
    except Exception as e:
        print(f"  Geocode error: {e}")
    return None, None, ""

def extract_precise_address(location_str):
    """Extrait la partie la plus precise de l'adresse pour geocoder"""
    if not location_str:
        return None
    # Nettoyer les parentheses et descriptions
    # Ex: "Zermatt (Wolli Wonderland a Sunnegga, sentier...)" -> pas geocodable
    # Ex: "Route de la Plage 1, 1897 Le Bouveret" -> geocodable
    # Ex: "Plusieurs stations (Saas-Grund, ...)" -> pas geocodable
    
    multi_keywords = ["plusieurs", "etc.", "et autres", "stations", "brig, martigny"]
    for kw in multi_keywords:
        if kw.lower() in location_str.lower():
            return None  # Multi-lieu, pas geocodable precisement
    
    return location_str

def distance_km(lat1, lon1, lat2, lon2):
    """Distance approximative en km"""
    import math
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def main():
    print("Recuperation de tous les events...")
    r = requests.get(f"{API}/api/events", timeout=60)
    events = r.json()
    print(f"Total events: {len(events)}")
    
    # Filtrer: events avec source_url (= scraped)
    scraped = [e for e in events if e.get("source_url")]
    print(f"Events scraped (avec source_url): {len(scraped)}")
    
    # Verifier chaque event scraped
    issues = []
    checked = 0
    
    for e in scraped:
        eid = e.get("id", "?")
        title = e.get("title", "?")
        location = e.get("location", "")
        lat = float(e.get("latitude", e.get("lat", 0)))
        lng = float(e.get("longitude", e.get("lng", 0)))
        date = e.get("date", "")
        source_url = e.get("source_url", "")
        
        addr = extract_precise_address(location)
        if not addr:
            # Multi-lieu, skip geocoding mais noter
            issues.append({
                "id": eid,
                "title": title,
                "issue": "MULTI-LIEU (pas d'adresse precise)",
                "location": location,
                "current_lat": lat,
                "current_lng": lng
            })
            continue
        
        # Geocode
        new_lat, new_lng, display = geocode(addr)
        time.sleep(1.2)  # Respecter rate limit Nominatim
        checked += 1
        
        if new_lat is None:
            # Essayer avec juste la ville
            parts = addr.split(",")
            if len(parts) > 1:
                city_part = ",".join(parts[-2:]).strip()
                new_lat, new_lng, display = geocode(city_part + ", Switzerland")
                time.sleep(1.2)
        
        if new_lat is None:
            issues.append({
                "id": eid,
                "title": title,
                "issue": "GEOCODING ECHOUE",
                "location": location
            })
            continue
        
        # Calculer la distance
        dist = distance_km(lat, lng, new_lat, new_lng)
        
        if dist > 0.5:  # Plus de 500m de difference
            issues.append({
                "id": eid,
                "title": title,
                "issue": f"COORDS DECALEES de {dist:.1f}km",
                "location": location,
                "current_lat": lat,
                "current_lng": lng,
                "correct_lat": new_lat,
                "correct_lng": new_lng,
                "nominatim_display": display[:100]
            })
            print(f"  DECALE {dist:.1f}km: ID:{eid} {title}")
            print(f"    Actuel: {lat},{lng} -> Nominatim: {new_lat},{new_lng}")
            print(f"    Adresse: {location}")
        else:
            print(f"  OK ({dist:.0f}m): ID:{eid} {title[:50]}")
        
        if checked % 20 == 0:
            print(f"\n--- {checked} verifies ---\n")
    
    # Rapport
    print("\n" + "=" * 70)
    print(f"RAPPORT: {checked} geocodes, {len(issues)} problemes")
    print("=" * 70)
    
    for iss in issues:
        print(f"\n  ID:{iss['id']} | {iss['title']}")
        print(f"    Probleme: {iss['issue']}")
        print(f"    Location: {iss.get('location','')}")
        if "correct_lat" in iss:
            print(f"    Actuel:  {iss['current_lat']}, {iss['current_lng']}")
            print(f"    Correct: {iss['correct_lat']}, {iss['correct_lng']}")
    
    # Sauvegarder les issues en JSON
    with open("scraper/coord_issues.json", "w", encoding="utf-8") as f:
        json.dump(issues, f, ensure_ascii=False, indent=2)
    print(f"\nIssues sauvegardees dans scraper/coord_issues.json")


if __name__ == "__main__":
    main()
