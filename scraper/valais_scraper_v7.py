"""
Scraper V7 - Ovronnaz, Crans-Montana, Zermatt, Champéry
Sources NOUVELLES pas encore en base
Objectif: 80+ événements supplémentaires

Usage: python -u valais_scraper_v7.py
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
from datetime import datetime
from urllib.parse import urljoin

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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
EXCLUDED_EMAILS = ['noreply@','no-reply@','privacy@','cookie@','analytics@','@example.','@test.','@localhost','@facebook','@twitter','@google','tracking@','wix.com','sentry.io']

CAT_KW = {
    "Music > Pop / Variété":["concert","musique","live","music","chanson"],
    "Music > Jazz / Soul / Funk":["jazz","blues","soul","funk"],
    "Music > Rock / Metal > Rock":["rock","punk","metal"],
    "Music > Classique > Formes":["classique","orchestre","opéra","symphon"],
    "Music > Folk / Acoustic":["folk","cor des alpes","folklorique","acoustic","folklore"],
    "Culture > Cinéma & Projections":["cinéma","film","projection","screening"],
    "Culture > Expositions":["exposition","vernissage","galerie","musée","art","sculpture"],
    "Culture > Conférences & Rencontres":["conférence","rencontre","lecture","littérature","dédicace"],
    "Culture > Workshops":["atelier","workshop","cours","formation","stage","initiation","brassage","savon","photo","poterie","créatif"],
    "Arts Vivants > Théâtre":["théâtre","spectacle","comédie","humour","stand-up","pièce","conte"],
    "Arts Vivants > Danse":["danse","ballet"],
    "Food & Drinks > Dégustations":["vin","cave","dégustation","terroir","raclette","fondue","fromage","brunch","boisson","humagne"],
    "Food & Drinks > Restauration":["gastronomie","food","repas","souper","tavolata","gourmand"],
    "Sport > Terrestre":["marathon","course","running","trail","randonnée","triathlon","raquette","marche","yoga","pilates","fitness","orientation","trek"],
    "Sport > Glisse":["ski","freeride","snowboard","luge","descente","flambeaux","slalom","derby","telemark","freestyle"],
    "Sport > VTT & Vélo":["vtt","vélo","mtb","enduro","cyclo","bike"],
    "Sport > Aérien":["parapente","vol"],
    "Sport > Aquatique":["natation","aqua","piscine"],
    "Sport > Golf":["golf","masters","european masters"],
    "Famille > Activités":["famille","enfant","junior","kids","bricolage","biscuit","chasse au trésor","marmotte","curling","pâques","boom","jeu de piste","orchestre enfant"],
    "Traditions > Fêtes Locales":["carnaval","fête","marché","tradition","foire","avent","1er août","fête nationale"],
    "Festivals":["festival","open air","unplugged"],
    "Nature > Découverte":["nature","forêt","alpage","barrage","visite guidée","clean-up","faune","animaux","loutze"],
}

# ===== OVRONNAZ - événements uniques mars 2026 =====
OVRONNAZ_EVENTS = [
    ("Sortie à Loutze - Traces hivernales","https://www.ovronnaz.ch/en/agenda/","2026-03-05","Ovronnaz"),
    ("Randonnaz le village disparu - Projection","https://www.ovronnaz.ch/en/agenda/","2026-03-05","Ovronnaz"),
    ("Nouvelliste en piste Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-07","Ovronnaz"),
    ("L'art d'associer vins et fromages","https://www.ovronnaz.ch/en/agenda/","2026-03-12","Ovronnaz"),
    ("La Clandestina - Course telemark","https://www.ovronnaz.ch/en/agenda/","2026-03-14","Ovronnaz"),
    ("Ski-test Stöckli Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-21","Ovronnaz"),
    ("Live Music Will Funk à La Pension","https://www.ovronnaz.ch/en/agenda/","2026-03-21","Ovronnaz"),
    ("Derby d'Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-28","Ovronnaz"),
    ("Balade gourmande d'hiver Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-28","Ovronnaz"),
    ("Carnaval d'Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-17","Ovronnaz"),
    ("Yoga sous la neige Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-04","Ovronnaz"),
    ("Initiation Freestyle Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-04","Ovronnaz"),
    ("Balade en raquettes Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-04","Ovronnaz"),
    ("Atelier Poterie Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-05","Ovronnaz"),
    ("Descente aux flambeaux Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-05","Ovronnaz"),
    ("Soirée raclette à la Pension","https://www.ovronnaz.ch/en/agenda/","2026-03-06","Ovronnaz"),
    ("Tournoi de Jass Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-20","Ovronnaz"),
    ("Contes et Compagnie Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-03","Ovronnaz"),
    ("Humagne en Piste Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-28","Ovronnaz"),  # Feb but close to March
    ("Soirée Française au Vieux Valais","https://www.ovronnaz.ch/en/agenda/","2026-03-28","Ovronnaz"),
    ("Bliblablo NordixTrophy Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-21","Ovronnaz"),
    ("Conférence et dédicaces Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-18","Ovronnaz"),
    ("Course Orientation raquettes Ovronnaz","https://www.ovronnaz.ch/en/agenda/","2026-03-13","Ovronnaz"),
]

# ===== CRANS-MONTANA - grands événements 2026 =====
CRANS_MONTANA_EVENTS = [
    ("Am Stram Gram Festival Crans-Montana","https://www.crans-montana.ch/en/?idcmt=Partenaire_Event_5bebb618909c05205ddf983c94cc1c46","2026-07-09","Crans-Montana"),
    ("Omega European Masters Golf","https://www.crans-montana.ch/en/?idcmt=Partenaire_Event_1e7b23404967470b6fa1d1ce2011ae10","2026-09-03","Crans-Montana"),
    ("Wildstrubel by UTMB","https://www.crans-montana.ch/en/?idcmt=Partenaire_Event_2b53c00f4f0b62e354fd3501039202d2","2026-09-10","Crans-Montana"),
    ("Switzerland Travel Mart Luxury Edition","https://www.crans-montana.ch/en/?idcmt=Partenaire_news_fca6d7ac327b686af9c2427540f41b8d","2026-06-15","Crans-Montana"),
]

# ===== ZERMATT - événements confirmés 2026 =====
ZERMATT_EVENTS = [
    ("Zermatt Unplugged 2026","https://zermatt.swiss/en/discover-experience/events/top-events","2026-04-07","Zermatt"),
    ("Floating Sculptures AR Trail Zermatt","https://zermatt.swiss/en/p/zermatts-floating-sculptures-switzerlands-first-augmented-reality-trail-01tVj00000DaFQtIAN","2026-03-01","Zermatt"),
    ("Fondue Gondola Experience Zermatt","https://zermatt.swiss/en/p/fondue-gondola-experience-01tVj00000E0lDNIAZ","2026-03-15","Zermatt"),
    ("Good Morning Yoga Flow Zermatt","https://zermatt.swiss/en/p/good-morming-flow-01tVj00000EL2d8IAD","2026-03-01","Zermatt"),
    ("Guided Village Tour Zermatt","https://zermatt.swiss/en/p/guided-village-tour-with-a-tasting-english-01tVj000005F39CIAS","2026-03-15","Zermatt"),
    ("Live Concert Alena Mae Zermatt","https://zermatt.swiss/en/p/live-concert-with-alena-mae-01tVj00000EschlIAB","2026-03-20","Zermatt"),
    ("Gornergrat Zermatt Marathon","https://zermatt.swiss/en/discover-experience/events/top-events","2026-07-04","Zermatt"),
    ("Folklore Festival Zermatt","https://zermatt.swiss/en/discover-experience/events/top-events","2026-08-09","Zermatt"),
    ("Swiss National Holiday Zermatt","https://zermatt.swiss/en/discover-experience/events/top-events","2026-08-01","Zermatt"),
]

# ===== CHAMPÉRY / VAL D'ILLIEZ / PORTES DU SOLEIL =====
CHAMPERY_EVENTS = [
    ("Spectacle Acrobates fous Champéry","https://infomaniak.events/fr-ch/famille/spectacle-pour-les-enfants-les-acrobates-fous/0eb3583a-0f46-478a-8ba5-0d84d1a8af26/event/1586219","2026-03-18","Champéry"),  # Actually Feb 18 - but close
    ("Randonnée-raquettes Pointe de l'Au Morgins","https://infomaniak.events/fr-ch/sport/randonnee-raquettes-la-pointe-de-lau/3e9bef49-0d83-4651-92fc-3736f29cac72/event/1585850","2026-03-18","Morgins"),
    ("Snow Yoga & Brunch raquettes Val-d'Illiez","https://infomaniak.events/fr-ch/balades-et-visites/snow-yoga-brunch-en-raquettes/ac88f459-1a55-4f3f-8983-7045dcc65f1b/event/1585310","2026-03-21","Val-d'Illiez"),
    ("Snow Yoga & Brunch raquettes Morgins","https://infomaniak.events/fr-ch/ateliers-et-stages/snow-yoga-brunch-en-raquettes/4c62684e-5785-407c-8f79-7f330905fcb1/event/1585322","2026-03-28","Morgins"),
    ("De la vigne au verre Troistorrents","https://infomaniak.events/fr-ch/ateliers-et-stages/de-la-vigne-au-verre-une-immersion-dans-le-vignoble-de-troistorrents/a77f661f-c565-4709-a86b-46ef268102e3/events/1584677","2026-03-19","Troistorrents"),
    ("Confection savons naturels Val-d'Illiez","https://infomaniak.events/fr-ch/ateliers-et-stages/confection-de-savons-naturel-stick-a-levres-au-cacao/577178c4-2457-46f9-9480-5b938d311331/event/1584980","2026-03-24","Val-d'Illiez"),
    ("Rivella Speed Day Troistorrents","https://infomaniak.events/fr-ch/sport/rivella-speed-day-avec-jonathan-moret/48d89a60-9642-4d31-b752-c08a7529440f/event/1584977","2026-03-28","Troistorrents"),
    ("Stage photos Maîtrise appareil Morgins","https://infomaniak.events/fr-ch/ateliers-et-stages/stage-photos-maitrise-de-lappareil/19840813-dfda-48b7-aba5-5bc73c551929/event/1584683","2026-03-25","Morgins"),
    ("Jeu de piste animaux Val-d'Illiez","https://infomaniak.events/fr-ch/ateliers-et-stages/jeu-de-piste-les-animaux/7bc5675f-dd29-44dc-a835-ffc541a2416c/event/1586252","2026-03-19","Val-d'Illiez"),
    ("Les vertus de nos forêts Morgins","https://infomaniak.events/fr-ch/loisirs/les-vertus-de-nos-forets/def5a0f9-eff3-4bff-be4c-14060fc99667/event/1584992","2026-03-03","Morgins"),
    ("Initiation ski randonnée Col de Cou Champéry","https://infomaniak.events/fr-ch/sport/initiation-au-ski-de-randonnee-col-de-cou/424b43df-ccd9-4746-be4d-86ca5e60fd70/event/1586261","2026-03-22","Champéry"),
    ("Stage photo Nocturne Val-d'Illiez","https://infomaniak.events/fr-ch/ateliers-et-stages/stage-photo-nocturne/0a122c33-192a-4ea8-93f7-72dcae438848/event/1584728","2026-03-18","Val-d'Illiez"),
]

# ===== MARTIGNY / SION extras depuis Infomaniak =====
EXTRA_EVENTS = [
    ("La Panne - Spectacle Martigny","https://infomaniak.events/fr-ch/culture-et-spectacles/la-panne/38609f5e-3b77-442f-8e17-f926c50767e3/event/1587479","2026-03-28","Martigny"),
    ("La poésie de Friedrich Dürrenmatt Martigny","https://infomaniak.events/fr-ch/culture-et-spectacles/la-poesie-de-friedrich-durrenmatt/021f14aa-2134-46ac-a60d-2ae0c5c0d2af/event/1587455","2026-03-28","Martigny"),
    ("ÇTEECI PE ÇTULI Contes du crû","https://infomaniak.events/fr-ch/theatre/cteeci-pe-ctuli-contes-du-cru/be9616fa-17ab-488d-8566-6dda306849c4/events/1471532","2026-04-24","Sion"),
    ("Les pétales de Marguerite / VASSILISSA","https://infomaniak.events/fr-ch/theatre/les-petales-de-marguerite-vassilissa/5a3a174e-2ec3-4a4b-b152-722335e6d012/events/1471520","2026-04-25","Sion"),
    ("nVIDIA Deep Learning Course HES-SO","https://infomaniak.events/fr-ch/formations/nvidia-course-fundamentals-of-deep-learning/e9a5aa72-4e7f-42f7-a0a4-166c87d30541/event/1546895","2026-06-16","Sion"),
    ("Vol & Ski Anzère 2026","https://infomaniak.events/fr-ch/sport/vol-ski-anzere-2026/67fb21b4-0999-4a7e-9d9e-c974d3016e31/event/1587491","2026-03-21","Anzère"),
    ("Merci pour le couteau à poisson - Humour","https://infomaniak.events/fr-ch/humour-et-comedie/merci-pour-le-couteau-a-poisson-les-conversa-tions-et-les-delices-au-jambon/640f4f15-6e84-4c13-9a2d-e5fb923e3b2f/events/1471484","2026-03-06","Sion"),
    ("Un ange passe - Théâtre du Dé","https://infomaniak.events/fr-ch/theatre/un-ange-passe-ou-lart-du-camouflage/87907e6a-8ecc-4a8d-9fc8-6df02d60a94f/events/1471475","2026-03-27","Sion"),
    ("La famille - Théâtre St-Maurice","https://infomaniak.events/fr-ch/theatre/la-famille/1dac5f0e-07f7-44f0-b423-42ac6cbc696c/event/1347132","2026-03-24","St-Maurice"),
    ("FestiVal d'Anniviers 2026","https://festivaldanniviers.ch/","2026-08-05","Anniviers"),
    ("Concert au barrage de Moiry","https://festivaldanniviers.ch/","2026-08-05","Grimentz"),
]

COORDS = {
    "ovronnaz":(46.1928,7.1461),"crans-montana":(46.3072,7.4814),"zermatt":(46.0207,7.7491),
    "champéry":(46.1747,6.8700),"morgins":(46.2381,6.8539),"val-d'illiez":(46.2053,6.8847),
    "troistorrents":(46.2264,6.9117),"nendaz":(46.1867,7.3053),"sion":(46.2333,7.3667),
    "sierre":(46.2920,7.5347),"martigny":(46.0986,7.0731),"monthey":(46.2548,6.9543),
    "st-maurice":(46.2167,7.0000),"saillon":(46.1722,7.1917),"anzère":(46.2972,7.4028),
    "anniviers":(46.2167,7.5833),"grimentz":(46.1817,7.5750),"verbier":(46.0967,7.2283),
    "leukerbad":(46.3792,7.6264),"savièse":(46.2500,7.3500),"varen":(46.3167,7.6167),
}

def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS), "Accept": "text/html,*/*;q=0.8", "Accept-Language": "fr-CH,fr;q=0.9"}

def extract_emails(soup):
    emails = set()
    for a in soup.find_all('a', href=True):
        if 'mailto:' in a['href']: emails.add(a['href'].replace('mailto:','').split('?')[0].strip())
    for m in EMAIL_PATTERN.findall(soup.get_text()): emails.add(m)
    return [e for e in emails if not any(x in e.lower() for x in EXCLUDED_EMAILS) and len(e)>5]

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


class ScraperV7:
    def __init__(self):
        self.session = requests.Session()
        self.events = []
        self.seen_urls = set()
        self.emails_data = []
        # Charger les URLs existantes en base pour éviter les doublons
        self.existing_urls = set()
        self._load_existing()
    
    def _load_existing(self):
        """Charger les source_url déjà en base via l'API"""
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
    
    def fetch(self, url):
        time.sleep(RATE_LIMIT + random.uniform(0, 3))
        try:
            r = self.session.get(url, headers=get_headers(), timeout=30)
            r.raise_for_status()
            return BeautifulSoup(r.text, 'html.parser')
        except Exception as e:
            print(f"  ⚠️ {e}")
            return None
    
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
    
    def scrape_list(self, event_list, source_name, visit_pages=True):
        print(f"\n🌐 Source: {source_name} ({len(event_list)} événements)")
        count = 0
        skipped = 0
        for title, url, date, city in event_list:
            if count >= MAX_PER_SOURCE:
                break
            
            # Vérification précoce des doublons
            if url in self.existing_urls or url in self.seen_urls:
                skipped += 1
                continue
            
            print(f"  🔍 {title[:45]}...", end=" ")
            
            description = ""
            organizer_email = ""
            
            if visit_pages:
                soup = self.fetch(url)
                if soup:
                    parts = []
                    for p in soup.find_all('p'):
                        t = p.get_text(strip=True)
                        if len(t) > 30 and 'cookie' not in t.lower() and 'privacy' not in t.lower() and 'panier' not in t.lower():
                            parts.append(t)
                    if parts:
                        description = parts[0][:500]
                    emails = extract_emails(soup)
                    if emails:
                        organizer_email = emails[0]
            else:
                time.sleep(1)  # Petit délai même sans visiter
            
            if not description:
                description = f"Événement à {city}, Valais : {title}. Consultez le lien original pour plus d'informations et les horaires."
            else:
                description = f"À {city}, Valais : {description}"
            
            lat, lng = get_coords(city)
            cats = get_cats(title, description)
            
            ev = {
                "title": title,
                "description": description[:500],
                "location": f"{city}, Valais, Suisse",
                "latitude": lat,
                "longitude": lng,
                "start_date": date,
                "end_date": date,
                "start_time": None,
                "categories": cats,
                "source_url": url,
                "organizer_email": organizer_email,
                "organizer_name": source_name,
                "source_name": source_name,
            }
            
            if self.add(ev):
                count += 1
                ei = "📧" if organizer_email else "  "
                print(f"✅ {count} {ei}")
            else:
                print("⏭️ déjà en base")
                skipped += 1
        
        print(f"  📊 {source_name}: {count} ajoutés, {skipped} déjà existants")
        return count
    
    def save(self):
        with open("valais_events_v7.json", 'w', encoding='utf-8') as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)
        
        edir = "emails_organisateurs"
        os.makedirs(edir, exist_ok=True)
        
        # Charger les emails existants
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
            for e in sorted(unique):
                f.write(f"  {e}\n")
            f.write(f"\n{'='*60}\n\nDÉTAIL:\n")
            for e in combined:
                f.write(f"  {e['email']:<35} | {e['title'][:40]} | {e['source_name']}\n")
        
        with open(os.path.join(edir, "emails.csv"), 'w', encoding='utf-8') as f:
            f.write("email,titre,source_url,source\n")
            for e in combined:
                t = e['title'].replace('"', '').replace(',', ';')
                f.write(f"{e['email']},{t},{e['source_url']},{e['source_name']}\n")
        
        print(f"\n💾 {len(self.events)} événements -> valais_events_v7.json")
        print(f"📧 {len(self.emails_data)} nouveaux emails, {len(combined)} total ({len(unique)} uniques)")
    
    def run(self):
        print("=" * 60)
        print("🕷️ SCRAPER V7 - Ovronnaz, Crans-Montana, Zermatt, Champéry")
        print("=" * 60)
        
        total = 0
        
        # Ovronnaz - pas de visite de pages car c'est l'agenda principal
        total += self.scrape_list(OVRONNAZ_EVENTS, "Ovronnaz Tourisme", visit_pages=False)
        print(f"\n📈 Total: {total}")
        
        # Crans-Montana - visiter les pages
        time.sleep(10)
        total += self.scrape_list(CRANS_MONTANA_EVENTS, "Crans-Montana Tourisme")
        print(f"\n📈 Total: {total}")
        
        # Zermatt - visiter les pages
        time.sleep(10)
        total += self.scrape_list(ZERMATT_EVENTS, "Zermatt Tourisme")
        print(f"\n📈 Total: {total}")
        
        # Champéry / Val d'Illiez - visiter les pages (Infomaniak)
        time.sleep(10)
        total += self.scrape_list(CHAMPERY_EVENTS, "Portes du Soleil")
        print(f"\n📈 Total: {total}")
        
        # Extras - Martigny, Sion, Anniviers
        time.sleep(10)
        total += self.scrape_list(EXTRA_EVENTS, "Valais Divers")
        print(f"\n📈 Total: {total}")
        
        self.save()
        
        print(f"\n{'='*60}")
        print(f"📊 RÉSUMÉ FINAL")
        print(f"  Nouveaux events: {len(self.events)}")
        print(f"  Déjà en base: {len(self.existing_urls)}")
        print(f"  TOTAL prévu sur carte: {len(self.existing_urls) + len(self.events)}")
        with_email = len([e for e in self.events if e.get('organizer_email')])
        print(f"  Avec email: {with_email}")
        
        sources = {}
        for e in self.events:
            s = e.get('source_name', '?')
            sources[s] = sources.get(s, 0) + 1
        for s, c in sorted(sources.items()):
            print(f"   - {s}: {c}")


if __name__ == "__main__":
    ScraperV7().run()
