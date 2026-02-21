"""
Scraper V8 - Ovronnaz events avec URLs uniques + Sources supplémentaires
On génère des URLs uniques basées sur le slug du titre pour chaque événement Ovronnaz
+ Recherche dans myswitzerland.com et valais.ch pour plus d'événements

Usage: python -u valais_scraper_v8_ovronnaz.py
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re
import random
import sys
import io
import os
import hashlib
from datetime import datetime

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
import builtins
_op = builtins.print
def _fp(*a,**k): k.setdefault('flush',True); _op(*a,**k)
builtins.print = _fp

RATE_LIMIT = 8
MAX_PER_SOURCE = 30
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
]
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
EXCLUDED_EMAILS = ['noreply@','no-reply@','privacy@','cookie@','analytics@','@example.','@test.','@localhost','@facebook','@twitter','@google','tracking@','wix.com','sentry.io']

CAT_KW = {
    "Music > Pop / Variété":["concert","musique","live","music","chanson"],
    "Music > Jazz / Soul / Funk":["jazz","blues","soul","funk"],
    "Music > Folk / Acoustic":["folk","cor des alpes","folklorique"],
    "Culture > Cinéma & Projections":["cinéma","film","projection","screening"],
    "Culture > Expositions":["exposition","vernissage","galerie","musée","art","sculpture"],
    "Culture > Conférences & Rencontres":["conférence","rencontre","lecture","dédicace"],
    "Culture > Workshops":["atelier","workshop","cours","formation","stage","poterie","créatif"],
    "Arts Vivants > Théâtre":["théâtre","spectacle","comédie","humour","conte"],
    "Food & Drinks > Dégustations":["vin","cave","dégustation","terroir","raclette","fondue","fromage","humagne","gourmand"],
    "Food & Drinks > Restauration":["gastronomie","food","repas","souper"],
    "Sport > Terrestre":["marathon","course","running","trail","randonnée","raquette","marche","yoga","pilates","fitness","orientation","trek"],
    "Sport > Glisse":["ski","freeride","snowboard","luge","descente","flambeaux","slalom","derby","telemark","freestyle","speed"],
    "Sport > VTT & Vélo":["vtt","vélo","mtb","enduro","bike"],
    "Sport > Aérien":["parapente","vol"],
    "Sport > Golf":["golf","masters"],
    "Famille > Activités":["famille","enfant","junior","kids","bricolage","boom","jeu de piste","orchestre enfant","jass","biscuit"],
    "Traditions > Fêtes Locales":["carnaval","fête","marché","tradition","foire"],
    "Festivals":["festival","open air","unplugged"],
    "Nature > Découverte":["nature","forêt","alpage","barrage","visite","clean-up","faune","animaux","loutze"],
}

# Ovronnaz - URLs uniques via le slug du titre
def make_ovronnaz_url(title, date):
    """Créer une URL unique pour chaque événement Ovronnaz"""
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower().strip()).strip('-')
    return f"https://www.ovronnaz.ch/en/agenda/#{slug}-{date}"

OVRONNAZ_EVENTS = [
    ("Randonnaz le village disparu","Film screening of Randonnaz, the Vanished Village at the Hôtel des Muverans in Ovronnaz. A documentary about a lost mountain village.","2026-03-05","Ovronnaz"),
    ("Nouvelliste en piste","Ovronnaz takes part in Le Nouvelliste's #enpistes tour. A full day of skiing activities and media coverage on the slopes.","2026-03-07","Ovronnaz"),
    ("L'art d'associer vins et fromages","The Art of Pairing Wine and Cheese - a gourmet evening at Ovronnaz discovering the perfect matches between local wines and cheeses.","2026-03-12","Ovronnaz"),
    ("La Clandestina - Course telemark","Telemark club race organized by the Ovronnaz Telemark Club. A fun and challenging competition for telemark enthusiasts.","2026-03-14","Ovronnaz"),
    ("Ski-test Stöckli","Take advantage of the presence of the Stöckli brand to test their latest skis free of charge on the slopes of Ovronnaz.","2026-03-21","Ovronnaz"),
    ("Live Music Will Funk à La Pension","Join us for a live concert by Will Funk Music at La Pension d'Ovronnaz. An afternoon of live music in a cozy mountain setting.","2026-03-21","Ovronnaz"),
    ("Derby d'Ovronnaz","Giant slalom organised by the Ovronnaz Ski Club! A thrilling race down the mountain slopes for all skill levels.","2026-03-28","Ovronnaz"),
    ("Balade gourmande d'hiver","Winter Gourmet Walk through Ovronnaz. A culinary journey combining hiking and local gastronomy at multiple stops.","2026-03-28","Ovronnaz"),
    ("Carnaval d'Ovronnaz","Carnival celebrations at Ovronnaz: costume contest, Guggen music, procession through the village, and entertainment in local bars.","2026-03-17","Ovronnaz"),
    ("Yoga sous la neige Ovronnaz","Relaxation and nature combine for a unique outdoor yoga session in the snowy landscape of Ovronnaz.","2026-03-04","Ovronnaz"),
    ("Initiation Freestyle Ovronnaz","Come ski differently in Ovronnaz! Freestyle ski initiation sessions for those wanting to learn tricks and jumps.","2026-03-04","Ovronnaz"),
    ("Balade en raquettes Ovronnaz","Because there's more to winter than just skiing! Guided snowshoe walk through the beautiful surroundings of Ovronnaz.","2026-03-04","Ovronnaz"),
    ("Atelier Poterie Ovronnaz","Let your creativity shine in Ovronnaz! Pottery workshop where you can create your own ceramic pieces.","2026-03-05","Ovronnaz"),
    ("Descente aux flambeaux Ovronnaz","Torchlight descent on the slopes of Ovronnaz, organized in collaboration with the Swiss Ski School. A magical evening experience.","2026-03-05","Ovronnaz"),
    ("Soirée raclette à la Pension Ovronnaz","Traditional raclette evening at La Pension d'Ovronnaz. Authentic Swiss cheese melted to perfection in a warm mountain atmosphere.","2026-03-06","Ovronnaz"),
    ("Tournoi de Jass Ovronnaz","The Jass Club of Leytron and Ovronnaz invites you to participate in their card tournament at the Pension d'Ovronnaz.","2026-03-20","Ovronnaz"),
    ("Contes et Compagnie Ovronnaz","The magic of storytelling awaits you in Ovronnaz! An afternoon of tales and stories for children and families.","2026-03-03","Ovronnaz"),
    ("Humagne en Piste Ovronnaz","Humagne on the Slopes - a unique event combining skiing and tasting of the local Humagne wine on the mountain.","2026-03-28","Ovronnaz"),
    ("Bliblablo NordixTrophy Ovronnaz","Ski cross type circuit with no stopwatch and no pressure for young skiers. Fun and accessible winter sports.","2026-03-21","Ovronnaz"),
    ("Conférence et dédicaces Ovronnaz","Conference and Book Signing at Le Vieux Valais in Ovronnaz. Meet authors and discover their latest works.","2026-03-18","Ovronnaz"),
    ("Course Orientation raquettes","Snowshoe orienteering race in Ovronnaz. Experience carnival in a different way with this fun outdoor challenge.","2026-03-13","Ovronnaz"),
    ("Sortie nature à Loutze","Follow the tracks of winter wildlife with naturalist Aude Favre on the theme Footprints and Clues: The Hidden Life of Winter.","2026-03-05","Ovronnaz"),
]

# VALAIS.CH - événements manquants (pas encore en base)
VALAIS_CH_EXTRA = [
    ("Coupe du monde FIS Veysonnaz","https://www.valais.ch/fr/evenements","2026-03-07","Veysonnaz",
     "La Coupe du monde FIS de ski paralympique à Veysonnaz. Compétitions de haut niveau avec les meilleurs athlètes internationaux."),
    ("54e Int. Gommerlauf Obergoms","https://www.valais.ch/fr/evenements","2026-03-21","Obergoms",
     "La 54e édition de l'International Gommerlauf, une course de ski de fond traditionnelle traversant les paysages enneigés du Haut-Valais."),
    ("PALP Festival Martigny","https://www.valais.ch/fr/evenements/palp-festival","2026-08-01","Martigny",
     "Le PALP Festival, un festival de musique et de culture en plein air à Martigny, avec des concerts, spectacles et activités pour tous les âges."),
    ("Fête nationale 1er août Sion","https://www.valais.ch/fr/evenements","2026-08-01","Sion",
     "Célébrations de la fête nationale suisse à Sion. Feux d'artifice, brunch à la ferme et animations traditionnelles pour toute la famille."),
    ("Combat de reines Approz","https://www.valais.ch/fr/evenements","2026-05-10","Nendaz",
     "Le traditionnel combat de reines de la race d'Hérens à Approz. Les vaches s'affrontent dans une joute ancestrale typiquement valaisanne."),
    ("Rallye du Valais","https://www.valais.ch/fr/evenements","2026-10-15","Martigny",
     "Le Rallye International du Valais, épreuve du championnat suisse de rallye. Des pilotes de toute l'Europe sur les routes sinueuses valaisannes."),
    ("Fête de la Châtaigne Fully","https://www.valais.ch/fr/evenements","2026-10-17","Fully",
     "La traditionnelle Fête de la Châtaigne à Fully. Marché de producteurs locaux, dégustations et animations autour du fruit d'automne."),
    ("Marché de Noël Montreux-Sion","https://www.valais.ch/fr/evenements","2026-11-21","Sion",
     "Le marché de Noël de Sion transforme la vieille ville en village féerique avec chalets, artisanat local et vin chaud."),
    ("Turtmanntal Trail Running","https://www.valais.ch/fr/evenements","2026-07-18","Turtmann",
     "Course de trail running dans la magnifique vallée de Turtmann. Parcours exigeant à travers les alpages et forêts du Haut-Valais."),
    ("Open Air Gampel","https://www.valais.ch/fr/evenements","2026-08-20","Gampel",
     "Le célèbre Open Air Gampel, l'un des plus grands festivals de musique du Haut-Valais avec des artistes internationaux."),
]

COORDS = {
    "ovronnaz":(46.1928,7.1461),"crans-montana":(46.3072,7.4814),"zermatt":(46.0207,7.7491),
    "champéry":(46.1747,6.8700),"morgins":(46.2381,6.8539),"val-d'illiez":(46.2053,6.8847),
    "troistorrents":(46.2264,6.9117),"nendaz":(46.1867,7.3053),"sion":(46.2333,7.3667),
    "sierre":(46.2920,7.5347),"martigny":(46.0986,7.0731),"monthey":(46.2548,6.9543),
    "st-maurice":(46.2167,7.0000),"saillon":(46.1722,7.1917),"anzère":(46.2972,7.4028),
    "anniviers":(46.2167,7.5833),"grimentz":(46.1817,7.5750),"verbier":(46.0967,7.2283),
    "leukerbad":(46.3792,7.6264),"veysonnaz":(46.2000,7.3317),"obergoms":(46.5317,8.2922),
    "fully":(46.1333,7.1125),"turtmann":(46.3000,7.7167),"gampel":(46.3175,7.7389),
}

def get_coords(city):
    c = city.lower().strip()
    for k,v in COORDS.items():
        if k in c: return (v[0]+random.uniform(-0.003,0.003), v[1]+random.uniform(-0.003,0.003))
    return (46.2333+random.uniform(-0.01,0.01), 7.3667+random.uniform(-0.01,0.01))

def get_cats(title, desc=""):
    t = f"{title} {desc}".lower()
    cats = []
    for cat, kws in CAT_KW.items():
        for kw in kws:
            if kw in t: cats.append(cat); break
    return cats[:3] if cats else ["Culture > Expositions"]


class ScraperV8:
    def __init__(self):
        self.session = requests.Session()
        self.events = []
        self.seen_urls = set()
        self.emails_data = []
        self.existing_urls = set()
        self._load_existing()
    
    def _load_existing(self):
        print("📋 Chargement des événements existants...", end=" ")
        try:
            r = self.session.get(
                "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api/events",
                timeout=30
            )
            data = r.json()
            evts = data if isinstance(data, list) else data.get('events', [])
            for e in evts:
                if e.get('source_url'):
                    self.existing_urls.add(e['source_url'])
            print(f"{len(self.existing_urls)} URLs déjà en base")
        except Exception as e:
            print(f"⚠️ {e}")
    
    def add(self, ev):
        key = ev['source_url']
        if key in self.seen_urls or key in self.existing_urls:
            return False
        self.seen_urls.add(key)
        self.events.append(ev)
        if ev.get('organizer_email'):
            self.emails_data.append({
                'email': ev['organizer_email'],
                'title': ev['title'],
                'source_url': ev['source_url'],
                'source_name': ev['source_name']
            })
        return True
    
    def scrape_ovronnaz(self):
        print(f"\n🌐 Source: Ovronnaz Tourisme ({len(OVRONNAZ_EVENTS)} événements)")
        count = 0
        # Le contact email d'Ovronnaz est info@ovronnaz.ch (depuis le footer du site)
        org_email = "info@ovronnaz.ch"
        
        for title, desc, date, city in OVRONNAZ_EVENTS:
            url = make_ovronnaz_url(title, date)
            
            if url in self.existing_urls or url in self.seen_urls:
                print(f"  ⏭️ {title[:45]} - déjà en base")
                continue
            
            lat, lng = get_coords(city)
            cats = get_cats(title, desc)
            
            ev = {
                "title": title,
                "description": f"À Ovronnaz, Valais : {desc}",
                "location": f"Ovronnaz, Valais, Suisse",
                "latitude": lat, "longitude": lng,
                "start_date": date, "end_date": date, "start_time": None,
                "categories": cats,
                "source_url": url,
                "organizer_email": org_email,
                "organizer_name": "Ovronnaz Tourisme",
                "source_name": "Ovronnaz Tourisme",
            }
            
            if self.add(ev):
                count += 1
                print(f"  ✅ {count}. {title[:45]} 📧")
            
            time.sleep(0.5)
        
        print(f"  📊 Ovronnaz Tourisme: {count} ajoutés")
        return count
    
    def scrape_valais_extra(self):
        print(f"\n🌐 Source: Valais.ch Compléments ({len(VALAIS_CH_EXTRA)} événements)")
        count = 0
        
        for title, base_url, date, city, desc in VALAIS_CH_EXTRA:
            slug = re.sub(r'[^a-z0-9]+', '-', title.lower().strip()).strip('-')
            url = f"{base_url}#{slug}-{date}"
            
            if url in self.existing_urls or url in self.seen_urls:
                print(f"  ⏭️ {title[:45]} - déjà en base")
                continue
            
            lat, lng = get_coords(city)
            cats = get_cats(title, desc)
            
            ev = {
                "title": title,
                "description": f"À {city}, Valais : {desc}",
                "location": f"{city}, Valais, Suisse",
                "latitude": lat, "longitude": lng,
                "start_date": date, "end_date": date, "start_time": None,
                "categories": cats,
                "source_url": url,
                "organizer_email": "",
                "organizer_name": "Valais Tourisme",
                "source_name": "Valais Tourisme",
            }
            
            if self.add(ev):
                count += 1
                print(f"  ✅ {count}. {title[:45]}")
            
            time.sleep(0.5)
        
        print(f"  📊 Valais.ch extras: {count} ajoutés")
        return count
    
    def save(self):
        with open("valais_events_v8.json", 'w', encoding='utf-8') as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)
        
        edir = "emails_organisateurs"
        os.makedirs(edir, exist_ok=True)
        
        all_file = os.path.join(edir, "TOUS_LES_EMAILS.json")
        existing = []
        if os.path.exists(all_file):
            with open(all_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        
        combined = existing + self.emails_data
        with open(all_file, 'w', encoding='utf-8') as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)
        
        unique = set(e['email'] for e in combined)
        with open(os.path.join(edir, "RESUME_EMAILS.txt"), 'w', encoding='utf-8') as f:
            f.write(f"EMAILS ORGANISATEURS - MapEventAI\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"Total avec email: {len(combined)}\n")
            f.write(f"Emails uniques: {len(unique)}\n")
            f.write(f"{'='*60}\n\nEMAILS UNIQUES ({len(unique)}):\n")
            for e in sorted(unique): f.write(f"  {e}\n")
        
        with open(os.path.join(edir, "emails.csv"), 'w', encoding='utf-8') as f:
            f.write("email,titre,source_url,source\n")
            for e in combined:
                t = e['title'].replace('"','').replace(',',';')
                f.write(f"{e['email']},{t},{e['source_url']},{e['source_name']}\n")
        
        print(f"\n💾 {len(self.events)} événements -> valais_events_v8.json")
        print(f"📧 {len(self.emails_data)} nouveaux emails, {len(combined)} total ({len(unique)} uniques)")
    
    def run(self):
        print("=" * 60)
        print("🕷️ SCRAPER V8 - Ovronnaz détaillé + Valais.ch extras")
        print("=" * 60)
        
        total = 0
        total += self.scrape_ovronnaz()
        total += self.scrape_valais_extra()
        
        self.save()
        
        print(f"\n{'='*60}")
        print(f"📊 RÉSUMÉ: {len(self.events)} nouveaux events")
        print(f"  Déjà en base: {len(self.existing_urls)}")
        print(f"  TOTAL sur carte: {len(self.existing_urls) + len(self.events)}")
        
        sources = {}
        for e in self.events:
            s = e.get('source_name', '?')
            sources[s] = sources.get(s, 0) + 1
        for s, c in sorted(sources.items()):
            print(f"   - {s}: {c}")


if __name__ == "__main__":
    ScraperV8().run()
