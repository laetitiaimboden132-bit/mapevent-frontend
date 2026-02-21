"""Import des evenements Valais famille/enfants fevrier-mars 2026"""
import requests
import json
import time

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

# 8 premiers events
BATCH1 = [
    {"title":"Carnaval du Bourg 2026","description":"Carnaval de Martigny : corteges de chars, guggenmusiks, concours de masques pour enfants. Journee des familles. Entree gratuite.","location":"Quartier du Bourg, 1920 Martigny","latitude":46.102,"longitude":7.072,"date":"2026-02-14","end_date":"2026-02-17","categories":["Loisirs & Animation > Defiles & Fetes > Carnaval","Famille & Enfants"],"source_url":"https://www.loisirs.ch/agendas/28821/carnaval-du-bourg-2026-martigny","validation_status":"auto_validated"},
    {"title":"153e Carnaval de Monthey","description":"Six jours de carnaval : masques, chars, guggenmusiks, cortege du dimanche. Ambiance familiale et festive.","location":"Centre-ville, 1870 Monthey","latitude":46.255,"longitude":6.954,"date":"2026-02-14","end_date":"2026-02-17","categories":["Loisirs & Animation > Defiles & Fetes > Carnaval"],"source_url":"https://carnavaldemonthey.com/","validation_status":"auto_validated"},
    {"title":"54e Int. Gommerlauf + Mini-Gommerlauf","description":"Course populaire de ski de fond : classique et libre le samedi, marathon et Mini-Gommerlauf enfants le dimanche.","location":"3988 Ulrichen, Obergoms","latitude":46.506,"longitude":8.310,"date":"2026-02-21","end_date":"2026-02-22","categories":["Sport > Glisse > Ski","Famille & Enfants"],"source_url":"https://www.valais.ch/fr/evenements/54-int-gommerlauf","validation_status":"auto_validated"},
    {"title":"Nendaz Freeride Junior 3*","description":"Epreuve 3 etoiles du Freeride Junior Tour pour les 14-18 ans. Village Nendaz Freeride avec big airbag et apres-ski.","location":"Tracouet, 1997 Haute-Nendaz","latitude":46.187,"longitude":7.305,"date":"2026-02-21","categories":["Sport > Glisse > Ski"],"source_url":"https://www.valais.ch/fr/evenements/nendaz-freeride-junior-3","validation_status":"auto_validated"},
    {"title":"Nendaz Freeride Kids","description":"Journee initiation freeride et securite pour les 7-14 ans : atelier DVA, mini-run, demo chiens avalanche. Diplome et cadeau.","location":"Plan du Fou, 1997 Siviez (Nendaz)","latitude":46.169,"longitude":7.305,"date":"2026-02-28","categories":["Sport > Glisse > Ski","Famille & Enfants"],"source_url":"https://www.valais.ch/fr/evenements/nendaz-freeride-kids","validation_status":"auto_validated"},
    {"title":"Les grandes inspirations - Musee d'art du Valais","description":"Nouveau cycle d'expositions. Visites famille avec jeu Inspiro, espace de creation et parcours litteraire.","location":"Place de la Majorie, 1950 Sion","latitude":46.233,"longitude":7.362,"date":"2026-02-28","end_date":"2027-01-31","categories":["Culture","Famille & Enfants"],"source_url":"https://musee-art-valais.ch/exposition-art/les-grandes-inspirations/","validation_status":"auto_validated"},
    {"title":"J'peux pas j'ai musee !","description":"Entree gratuite dans les trois musees cantonaux le premier week-end du mois. Atelier tout public le dimanche apres-midi.","location":"Musees cantonaux, 1950 Sion","latitude":46.233,"longitude":7.362,"date":"2026-03-07","end_date":"2026-03-08","categories":["Culture","Famille & Enfants"],"source_url":"https://musee-art-valais.ch/agenda/jpeux-pas-jai-musee/","validation_status":"auto_validated"},
    {"title":"Junior Days Valais-Wallis 2026","description":"Week-end activites pour les 4-14 ans : ateliers creatifs, initiations sportives, quiz et concours. Restauration sur place.","location":"1920 Martigny","latitude":46.102,"longitude":7.072,"date":"2026-03-14","end_date":"2026-03-15","categories":["Famille & Enfants","Loisirs & Animation"],"source_url":"https://www.juniordays.ch/","validation_status":"auto_validated"},
]

def load_extra():
    """Charger les 19 events supplementaires depuis le JSON"""
    with open("valais_family_events_feb_mar_2026.json", "r", encoding="utf-8") as f:
        extra = json.load(f)
    
    events = []
    for e in extra:
        dates_str = e.get("dates", "")
        date_val = None
        end_date_val = None
        
        if "14" in dates_str and "17" in dates_str and "vrier" in dates_str:
            date_val = "2026-02-14"; end_date_val = "2026-02-17"
        elif "14 f" in dates_str:
            date_val = "2026-02-14"
        elif "15 f" in dates_str:
            date_val = "2026-02-15"
        elif "16 f" in dates_str:
            date_val = "2026-02-16"
        elif "21 mars" in dates_str:
            date_val = "2026-03-21"
        elif "19 mars" in dates_str:
            date_val = "2026-03-19"
        elif "12 f" in dates_str and "14 juin" in dates_str:
            date_val = "2026-02-14"; end_date_val = "2026-06-14"
        elif "7" in dates_str and "8 mars" in dates_str:
            date_val = "2026-03-07"; end_date_val = "2026-03-08"
        else:
            date_val = "2026-02-14"  # ouvert tout l'hiver -> debut vacances
        
        ev = {
            "title": e["title"],
            "description": e["description"],
            "location": e["location"],
            "latitude": e["lat"],
            "longitude": e["lng"],
            "date": date_val,
            "categories": e["categories"],
            "source_url": e["source_url"],
            "validation_status": "auto_validated"
        }
        if end_date_val:
            ev["end_date"] = end_date_val
        events.append(ev)
    
    return events


def main():
    print("Import events Valais famille/enfants")
    print("=" * 50)
    
    # Warmup Lambda
    print("Warmup Lambda...")
    requests.get(f"{API}/api/events", timeout=60)
    time.sleep(2)
    
    extra = load_extra()
    
    # Deduplicate
    batch1_titles = set(e["title"].lower() for e in BATCH1)
    extra_unique = [e for e in extra if e["title"].lower() not in batch1_titles]
    
    all_events = BATCH1 + extra_unique
    print(f"Total: {len(all_events)} events a importer\n")
    
    created = 0
    errors = 0
    
    for ev in all_events:
        try:
            r = requests.post(f"{API}/api/events/publish", json=ev, timeout=15)
            if r.status_code in (200, 201):
                created += 1
                print(f"  OK: {ev['title']}")
            else:
                errors += 1
                print(f"  ERREUR {r.status_code}: {ev['title']} - {r.text[:100]}")
        except Exception as ex:
            errors += 1
            print(f"  EXCEPTION: {ev['title']} - {ex}")
        time.sleep(0.3)
    
    print(f"\n{'=' * 50}")
    print(f"Resultat: {created} crees, {errors} erreurs")


if __name__ == "__main__":
    main()
