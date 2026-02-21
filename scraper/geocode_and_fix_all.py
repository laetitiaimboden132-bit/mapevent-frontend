"""
Geocodage precis et correction de TOUS les events Valais importes.
Pour chaque event: geocode l'adresse exacte via Nominatim, corrige coords + source_url.
"""
import requests
import json
import time
import math

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"


def geocode(address, country="ch"):
    """Geocode via Nominatim"""
    try:
        r = requests.get("https://nominatim.openstreetmap.org/search", params={
            "q": address,
            "format": "json",
            "limit": 1,
            "countrycodes": country,
        }, headers={"User-Agent": "MapEventAI-Bot/1.0"}, timeout=15)
        results = r.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"]), results[0].get("display_name", "")
    except Exception as e:
        print(f"    Geocode error: {e}")
    return None, None, ""


def distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


# Tous mes 25 events Valais avec les corrections a appliquer
# Format: (event_id, adresse_precise_pour_geocode, source_url, date_corrections)
VALAIS_EVENTS = [
    # ID:8857 Carnaval du Bourg 2026
    {
        "id": 8857,
        "geocode_address": "Place Centrale, 1920 Martigny, Valais, Switzerland",
        "source_url": "https://www.loisirs.ch/agendas/28821/carnaval-du-bourg-2026-martigny",
    },
    # ID:8859 54e Int. Gommerlauf
    {
        "id": 8859,
        "geocode_address": "Ulrichen, 3988 Obergoms, Valais, Switzerland",
        "source_url": "https://www.valais.ch/fr/evenements/54-int-gommerlauf",
    },
    # ID:8860 Nendaz Freeride Junior
    {
        "id": 8860,
        "geocode_address": "Tracouet, Haute-Nendaz, 1997, Switzerland",
        "source_url": "https://www.valais.ch/fr/evenements/nendaz-freeride-junior-3",
    },
    # ID:8861 Nendaz Freeride Kids
    {
        "id": 8861,
        "geocode_address": "Siviez, Nendaz, 1997, Switzerland",
        "source_url": "https://www.valais.ch/fr/evenements/nendaz-freeride-kids",
    },
    # ID:8862 Les grandes inspirations - Musee d'art du Valais
    {
        "id": 8862,
        "geocode_address": "Place de la Majorie 15, 1950 Sion, Switzerland",
        "source_url": "https://musee-art-valais.ch/exposition-art/les-grandes-inspirations/",
    },
    # ID:8863 J'peux pas j'ai musee !
    {
        "id": 8863,
        "geocode_address": "Rue des Chateaux 14, 1950 Sion, Switzerland",
        "source_url": "https://musee-art-valais.ch/agenda/jpeux-pas-jai-musee/",
    },
    # ID:8864 Junior Days Valais-Wallis 2026
    {
        "id": 8864,
        "geocode_address": "Place Centrale, 1920 Martigny, Switzerland",
        "source_url": "https://www.juniordays.ch/",
    },
    # ID:8865 Lud'eveil a la ludotheque de Villette
    {
        "id": 8865,
        "geocode_address": "Route de Montagnier 9, 1934 Le Chable, Switzerland",
        "source_url": "https://agenda.culturevalais.ch/fr/event/show/41549",
    },
    # ID:8866 Fasnachtsumzug in Wiler
    {
        "id": 8866,
        "geocode_address": "Wiler, 3918 Lotschental, Switzerland",
        "source_url": "https://agenda.culturevalais.ch/fr/event/show/40326",
    },
    # ID:8867 Concert-Spectacle Casse-Noisette
    {
        "id": 8867,
        "geocode_address": "Route de l'Ecosse 1B, 1907 Saxon, Switzerland",
        "source_url": "https://agenda.culturevalais.ch/fr/event/show/42011",
    },
    # ID:8868 Coccicontes
    {
        "id": 8868,
        "geocode_address": "Bibliotheque de Verbier, 1936 Verbier, Switzerland",
        "source_url": "https://agenda.culturevalais.ch/fr/event/show/41748",
    },
    # ID:8869 PRINTEMPS DES MUSEES Martigny
    {
        "id": 8869,
        "geocode_address": "Rue du Manoir 3, 1920 Martigny, Switzerland",
        "source_url": "https://agenda.culturevalais.ch/fr/event/show/41744",
    },
    # ID:8870 Carnaval d'Evolene
    {
        "id": 8870,
        "geocode_address": "Evolene, 1983, Valais, Switzerland",
        "source_url": "https://www.valdherens.ch/fr/le-carnaval-a-evolene-fp49450",
    },
    # ID:8871 Aquaparc Le Bouveret
    {
        "id": 8871,
        "geocode_address": "Route de la Plage 1, 1897 Le Bouveret, Switzerland",
        "source_url": "https://www.aquaparc.ch/preparer-ma-visite/calendrier-et-horaires",
    },
    # ID:8872 Barryland Martigny
    {
        "id": 8872,
        "geocode_address": "Rue du Levant 34, 1920 Martigny, Switzerland",
        "source_url": "https://www.barryland.ch/en/practical-info-552/",
    },
    # ID:8873 Pistes de luge en Valais (multi-lieu -> Fiescheralp, deja fixe)
    {
        "id": 8873,
        "skip_geocode": True,
        "source_url": "https://www.valais.ch/fr/explorer/activites/autres-activites-hivernales/luge",
    },
    # ID:8874 Patinoires en Valais (multi-lieu -> Sion, deja fixe)
    {
        "id": 8874,
        "skip_geocode": True,
        "source_url": "https://www.myswitzerland.com/fr-fr/decouvrir/hiver/patinoires/-/valais/",
    },
    # ID:8875 Bourg et Basilique de Valere
    {
        "id": 8875,
        "geocode_address": "Rue des Chateaux 24, 1950 Sion, Switzerland",
        "source_url": "https://siontourisme.ch/fr/valere",
    },
    # ID:8876 Crans-Montana en famille
    {
        "id": 8876,
        "geocode_address": "Crans-Montana, 3963, Switzerland",
        "source_url": "https://www.crans-montana.ch/fr/famille/activites_famille/",
    },
    # ID:8877 Terrain d'aventure de Kian
    {
        "id": 8877,
        "geocode_address": "Furggstalden, Saas-Almagell, 3905, Switzerland",
        "source_url": "https://www.saas-fee.ch/fr/famille/hiver-pour-la-famille/activites-familiales-en-hiver/le-terrain-daventure-de-kian",
    },
    # ID:8878 Zermatt Wolli Wonderland
    {
        "id": 8878,
        "geocode_address": "Sunnegga, 3920 Zermatt, Switzerland",
        "source_url": "https://zermatt.swiss/fr/activites/familles",
    },
    # ID:8879 Loeche-les-Bains Thermes
    {
        "id": 8879,
        "geocode_address": "Rathausstrasse 32, 3954 Leukerbad, Switzerland",
        "source_url": "https://www.leukerbad-therme.ch/fr/",
        "extra_fixes": {
            "date": "2026-02-14",
            "end_date": "2026-03-31",
            "location": "Leukerbad Therme, Rathausstrasse 32, 3954 Leukerbad",
        }
    },
    # ID:8880 Happyland Granges
    {
        "id": 8880,
        "geocode_address": "Route du Foulon 24, 3977 Granges, Switzerland",
        "source_url": "https://www.martigny.com/fr/activity/happyland-33698/",
    },
    # ID:8882 Raquettes et randonnees (multi-lieu -> deja fixe Zermatt)
    {
        "id": 8882,
        "skip_geocode": True,
        "source_url": "https://www.valais.ch/fr/explorer/activites/randonnees-hivernales/raquettes",
    },
    # ID:8883 Verbier Kids Activity
    {
        "id": 8883,
        "geocode_address": "Place Centrale, 1936 Verbier, Switzerland",
        "source_url": "https://www.verbier.ch/offres/kids-activity-la-tzoumaz-fr-4839093/",
    },
]


def main():
    print("=" * 70)
    print("GEOCODAGE ET CORRECTION DE TOUS LES EVENTS VALAIS")
    print("=" * 70)

    # Warmup
    requests.get(f"{API}/api/health", timeout=30)

    updates = []

    for ev in VALAIS_EVENTS:
        eid = ev["id"]
        print(f"\n--- ID:{eid} ---")

        update = {"id": eid}

        # Source URL
        if ev.get("source_url"):
            update["source_url"] = ev["source_url"]
            print(f"  source_url: {ev['source_url'][:70]}")

        # Extra fixes (dates, location)
        if ev.get("extra_fixes"):
            for k, v in ev["extra_fixes"].items():
                update[k] = v
                print(f"  {k}: {v}")

        # Geocode
        if not ev.get("skip_geocode"):
            addr = ev["geocode_address"]
            print(f"  Geocoding: {addr}")
            lat, lng, display = geocode(addr)
            time.sleep(1.2)

            if lat is None:
                # Retry sans numero de rue
                parts = addr.split(",")
                simpler = ", ".join(parts[1:]).strip() if len(parts) > 1 else addr
                print(f"  Retry: {simpler}")
                lat, lng, display = geocode(simpler)
                time.sleep(1.2)

            if lat is not None:
                update["latitude"] = lat
                update["longitude"] = lng
                print(f"  -> {lat}, {lng}")
                print(f"  -> {display[:80]}")
            else:
                print(f"  ECHEC GEOCODING!")
        else:
            print(f"  (skip geocode - multi-lieu)")

        updates.append(update)

    # Envoyer toutes les corrections
    print(f"\n\n{'=' * 70}")
    print(f"ENVOI DE {len(updates)} CORRECTIONS")
    print(f"{'=' * 70}")

    r = requests.post(
        f"{API}/api/admin/fix-events",
        json={"updates": updates},
        timeout=60
    )
    print(f"Status: {r.status_code}")
    resp = r.json()
    print(f"Updated: {resp.get('updated', '?')}")
    print(f"Errors: {resp.get('errors', [])}")

    # Sauvegarder les updates pour reference
    with open("scraper/applied_fixes.json", "w", encoding="utf-8") as f:
        json.dump(updates, f, ensure_ascii=False, indent=2)
    print("\nCorrections sauvegardees dans scraper/applied_fixes.json")


if __name__ == "__main__":
    main()
