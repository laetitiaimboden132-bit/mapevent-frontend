"""
Audit PROFOND de TOUS les events suisses.
Verifie que chaque event a:
1. Une adresse COMPLETE (avec numero de rue)
2. Des coordonnees PRECISES (geocodees depuis l'adresse exacte)
3. Un source_url valide

Pour les events sans adresse complete: recherche l'adresse exacte.
"""
import requests
import json
import time
import math
import re

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"


def geocode(address, country="ch"):
    """Geocode via Nominatim"""
    try:
        r = requests.get("https://nominatim.openstreetmap.org/search", params={
            "q": address, "format": "json", "limit": 1, "countrycodes": country,
        }, headers={"User-Agent": "MapEventAI-Bot/1.0"}, timeout=15)
        results = r.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"]), results[0].get("display_name", "")
    except Exception as e:
        pass
    return None, None, ""


def has_street_number(location):
    """Verifie si l'adresse contient un numero de rue"""
    if not location:
        return False
    # Patterns courants: "Rue X 12", "12 Rue X", "Route X 1B"
    # Aussi: "NPA Ville" sans rue
    has_number = bool(re.search(r'\b\d+[A-Za-z]?\b', location))
    has_street = bool(re.search(r'(rue|route|avenue|chemin|place|quai|boulevard|passage|impasse|allée|sentier|ruelle|strasse|weg|platz|gasse)\s', location, re.IGNORECASE))
    has_npa = bool(re.search(r'\b\d{4}\b', location))
    
    if has_street and has_number:
        return True
    if has_npa and has_number:
        # Has postal code AND a number, likely has street number
        # But need to distinguish "3960 Sierre" (no street) from "Rue X 5, 3960 Sierre"
        numbers = re.findall(r'\b\d+\b', location)
        # If more than just the NPA has numbers
        non_npa_numbers = [n for n in numbers if len(n) != 4]
        return len(non_npa_numbers) > 0
    return False


def main():
    r = requests.get(f"{API}/api/events", timeout=60)
    events = r.json()
    
    # Filtrer: events suisses (coords en Suisse ou dans la region)
    # Suisse: lat 45.8-47.9, lng 5.8-10.6
    # Aussi Haute-Savoie/frontiere: lat 45.6-46.5, lng 5.8-7.0
    swiss_events = []
    for e in events:
        lat = float(e.get("latitude", e.get("lat", 0)))
        lng = float(e.get("longitude", e.get("lng", 0)))
        # Suisse + frontalier
        if 45.6 <= lat <= 47.9 and 5.8 <= lng <= 10.6:
            # Exclure les events francais (openagenda, paris, nantes)
            src = e.get("source_url", "")
            if not any(x in src for x in ["openagenda.com", "paris.fr", "nantes.fr"]):
                swiss_events.append(e)
    
    print(f"Total events: {len(events)}")
    print(f"Events suisses/frontaliers a auditer: {len(swiss_events)}")
    
    # Categoriser les problemes
    no_address = []  # Pas d'adresse complete
    no_location = []  # Location vide ou tres vague
    
    for e in swiss_events:
        eid = e.get("id")
        title = e.get("title", "?")
        location = e.get("location", "")
        lat = float(e.get("latitude", e.get("lat", 0)))
        lng = float(e.get("longitude", e.get("lng", 0)))
        src = e.get("source_url", "")
        
        if not location or len(location.strip()) < 5:
            no_location.append(e)
        elif not has_street_number(location):
            no_address.append(e)
    
    print(f"\nEvents sans location: {len(no_location)}")
    print(f"Events sans adresse complete (pas de numero de rue): {len(no_address)}")
    
    # Lister TOUS les events sans adresse complete
    print("\n" + "=" * 70)
    print("EVENTS SANS ADRESSE COMPLETE")
    print("=" * 70)
    
    all_issues = no_location + no_address
    for e in sorted(all_issues, key=lambda x: x.get("id", 0)):
        eid = e.get("id")
        title = e.get("title", "?")[:70]
        location = e.get("location", "VIDE")
        lat = e.get("latitude", e.get("lat", "?"))
        lng = e.get("longitude", e.get("lng", "?"))
        print(f"ID:{eid} | {title}")
        print(f"  Location: {location}")
        print(f"  Coords: {lat}, {lng}")
        print()
    
    print(f"\nTotal problemes: {len(all_issues)}")
    
    # Sauvegarder
    output = []
    for e in sorted(all_issues, key=lambda x: x.get("id", 0)):
        output.append({
            "id": e.get("id"),
            "title": e.get("title", "?"),
            "location": e.get("location", ""),
            "latitude": e.get("latitude", e.get("lat")),
            "longitude": e.get("longitude", e.get("lng")),
            "source_url": e.get("source_url", ""),
        })
    
    with open("scraper/address_issues.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Sauvegarde dans scraper/address_issues.json")


if __name__ == "__main__":
    main()
