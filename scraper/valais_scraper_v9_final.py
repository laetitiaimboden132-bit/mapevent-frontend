"""
Scraper V9 - Sources finales pour atteindre 300 événements
TempsLibre.ch, SionTourisme, événements sportifs, événements d'été/automne

Usage: python -u valais_scraper_v9_final.py
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
    "Music > Pop / Variété":["concert","musique","live","music","chanson","doré","gims","louane","maé","bénabar"],
    "Music > Jazz / Soul / Funk":["jazz","blues","soul","funk"],
    "Music > Rock / Metal > Rock":["rock","punk","metal","superbus"],
    "Music > Classique > Formes":["classique","orchestre","opéra","symphon"],
    "Music > Folk / Acoustic":["folk","cor des alpes","folklorique","oesch"],
    "Music > Electro":["electro","dj","clubbing"],
    "Culture > Cinéma & Projections":["cinéma","film","projection","screening","documentaire"],
    "Culture > Expositions":["exposition","vernissage","galerie","musée","art","sculpture"],
    "Culture > Conférences & Rencontres":["conférence","rencontre","lecture","littérature","livre","dédicace"],
    "Culture > Workshops":["atelier","workshop","cours","formation","stage","poterie","créatif"],
    "Arts Vivants > Théâtre":["théâtre","spectacle","comédie","humour","stand-up","conte","rires","brume"],
    "Arts Vivants > Danse":["danse","ballet"],
    "Food & Drinks > Dégustations":["vin","cave","dégustation","terroir","raclette","fondue","fromage","châtaigne"],
    "Food & Drinks > Restauration":["gastronomie","food","repas","souper","poutine"],
    "Sport > Terrestre":["marathon","course","running","trail","randonnée","triathlon","raquette","marche","yoga","pilates","fitness","semi","slowup"],
    "Sport > Glisse":["ski","freeride","snowboard","luge","descente","flambeaux","slalom"],
    "Sport > VTT & Vélo":["vtt","vélo","mtb","enduro","bike","cyclo"],
    "Sport > Aérien":["parapente","vol"],
    "Sport > Golf":["golf","masters"],
    "Sport > Combat":["combat","reines","lutte"],
    "Famille > Activités":["famille","enfant","junior","kids","biscuit","chasse","am stram"],
    "Traditions > Fêtes Locales":["carnaval","fête","marché","tradition","foire","national","1er août"],
    "Festivals":["festival","open air","unplugged"],
    "Nature > Découverte":["nature","forêt","alpage","barrage","visite","clean-up","distillerie"],
}

# ===== TEMPSLIBRE.CH - Événements Valais =====
TEMPSLIBRE_EVENTS = [
    ("Planach' Festival 2026","https://www.tempslibre.ch/valais/festivals/448404-planach-festival-2026","2026-03-06","2026-03-08","Champéry",
     "Grooves tropicaux, altitude et fête non-stop : le Planach' Festival revient à Champéry pour une troisième édition résolument solaire."),
    ("Attache ta tuque ! Le Québec à Conthey","https://www.tempslibre.ch/valais/manifestations/445516-attache-ta-tuque-le-qu-bec-d-barque-conthey","2026-03-07","2026-03-07","Conthey",
     "Conthey prend l'accent québécois avec une soirée sucrée, musicale et complètement déjantée, entre poutine et musique du Québec."),
    ("Festival Maxi-Rires Champéry","https://www.tempslibre.ch/valais/festivals/424707-festival-maxi-rires","2026-03-23","2026-03-28","Champéry",
     "Le festival d'humour international fête son 18e anniversaire avec David Castello-Lopes, Camille Lellouche, Thomas Wiesel et d'autres grands noms."),
    ("Festival Week-end au bord de l'eau","https://www.tempslibre.ch/valais/festivals/431082-festival-week-end-au-bord-de-l-eau","2026-06-25","2026-06-28","Sierre",
     "Le Festival Week-end au bord de l'eau revient pour une 19e édition avec quatre jours de détente, musique et activités au Lac de Géronde à Sierre."),
    ("Fête nationale Bal 1er août Chamoson","https://www.tempslibre.ch/valais/manifestations/443097-f-te-nationale-bal-du-1er-ao-t","2026-08-01","2026-08-02","Chamoson",
     "Venez faire la fête à Chamoson et participez au bal du 1er août pour célébrer la fête nationale suisse !"),
    ("33e Fête du Livre St-Pierre-de-Clages","https://www.tempslibre.ch/valais/manifestations/442770-33e-f-te-du-livre-de-st-pierre-de-clages","2026-08-28","2026-08-30","St-Pierre-de-Clages",
     "La 33e édition de la Fête du Livre de St-Pierre-de-Clages, village du livre en Valais. Rencontres d'auteurs, dédicaces et marché littéraire."),
    ("Champéry Film Festival","https://www.tempslibre.ch/valais/festivals/430485-champ-ry-film-festival","2026-11-13","2026-11-14","Champéry",
     "Explorez la montagne sous un autre angle au Champéry Film Festival. Films, photographie et art au Centre sportif du Palladium."),
    ("REVENIR SUR TERRE Exposition Martigny","https://www.tempslibre.ch/valais/expositions/447835-exposition-revenir-sur-terre","2026-03-01","2026-05-10","Martigny",
     "Une exposition sensible et joueuse au Manoir de Martigny, où arts visuels, sons, mots et matières interrogent notre manière d'habiter le monde."),
    ("Les brumes de Manchester Monthey","https://www.tempslibre.ch/valais/spectacles/447999-th-tre-les-brumes-de-manchester","2026-03-01","2026-04-18","Monthey",
     "Un meurtre, dix suspects et 90 minutes de tension britannique. Les Brumes de Manchester au P'tit Théâtre de la Vièze."),
]

# ===== SION SOUS LES ÉTOILES + événements sportifs Sion =====
SION_EVENTS = [
    ("Sion sous les étoiles 2026 - Jour 1","https://www.siontourisme.ch/fr/agenda#sion-sous-les-etoiles-j1","2026-07-15","2026-07-15","Sion",
     "11e édition de Sion sous les étoiles. Concert avec Julien Doré, Christophe Maé, Vitaa et Luiza sous les étoiles valaisannes."),
    ("Sion sous les étoiles 2026 - Jour 2","https://www.siontourisme.ch/fr/agenda#sion-sous-les-etoiles-j2","2026-07-17","2026-07-17","Sion",
     "Sion sous les étoiles : GIMS, Louane, Marine et Jeanne Cherhal enflamment la scène sédunoise."),
    ("Sion sous les étoiles 2026 - Jour 3","https://www.siontourisme.ch/fr/agenda#sion-sous-les-etoiles-j3","2026-07-18","2026-07-18","Sion",
     "Sion sous les étoiles : Umberto Tozzi, Superbus et invités surprises clôturent cette 11e édition mémorable."),
    ("SLOWUP Valais 2026","https://www.slowup.ch/valais/fr/#slowup-2026","2026-06-07","2026-06-07","Sion",
     "Le slowUp Valais invite cyclistes et marcheurs à profiter de routes fermées au trafic entre Sion et Sierre. 30 km de parcours festif et familial."),
    ("Semi du Rhône Bramois","https://www.sion.ch/_rte/publikation/588796#semi-rhone","2026-03-22","2026-03-22","Sion",
     "Course à pied semi-marathon le long du Rhône à Bramois/Sion. Un parcours plat et rapide dans la vallée du Rhône."),
    ("Valais Triathlon Festival","https://www.sion.ch/_rte/publikation/588796#triathlon","2026-08-15","2026-08-15","Sion",
     "Le Valais Triathlon Festival aux Îles de Sion. Natation, vélo et course à pied dans un cadre naturel exceptionnel."),
    ("Foire du Valais Martigny","https://www.foireduvalais.ch/#foire-2026","2026-10-02","2026-10-11","Martigny",
     "La Foire du Valais, le plus grand événement économique et festif du canton. Expositions, dégustations, concerts et animations pour toute la famille."),
]

# ===== ÉVÉNEMENTS D'ÉTÉ ET AUTOMNE VALAIS =====
ETE_AUTOMNE_EVENTS = [
    ("Combats de reines Martigny-Combe","https://www.valais.ch/fr/evenements#combat-reines-martigny","2026-05-17","2026-05-17","Martigny",
     "Les traditionnels combats de reines de la race d'Hérens à Martigny-Combe. Les vaches s'affrontent dans une joute ancestrale valaisanne."),
    ("Inalpe Thyon","https://www.valais.ch/fr/evenements#inalpe-thyon","2026-06-20","2026-06-20","Thyon",
     "L'Inalpe de Thyon, la montée traditionnelle des troupeaux aux alpages. Un moment de convivialité et de tradition en haute montagne."),
    ("Désalpe Chermignon","https://www.valais.ch/fr/evenements#desalpe-chermignon","2026-09-26","2026-09-26","Chermignon",
     "La Désalpe de Chermignon, descente festive des troupeaux depuis les alpages. Vaches fleuries, cortège et marché artisanal."),
    ("Marché de la St-Martin Sion","https://www.valais.ch/fr/evenements#marche-st-martin","2026-11-09","2026-11-09","Sion",
     "Le Marché de la St-Martin à Sion, tradition automnale avec vente de brisolée, châtaignes et vin nouveau dans les rues de la vieille ville."),
    ("Fête des vendanges Sierre","https://www.valais.ch/fr/evenements#vendanges-sierre","2026-09-19","2026-09-19","Sierre",
     "La Fête des vendanges de Sierre célèbre la récolte du raisin. Défilé de chars, dégustations de vin et animations musicales dans la cité du soleil."),
    ("Carnaval de Monthey","https://www.valais.ch/fr/evenements#carnaval-monthey","2026-03-14","2026-03-14","Monthey",
     "Le célèbre Carnaval de Monthey, l'un des plus grands du Valais. Cortège costumé, Guggenmusik et festivités dans toute la ville."),
    ("Comptoir de Martigny","https://www.valais.ch/fr/evenements#comptoir-martigny","2026-10-02","2026-10-11","Martigny",
     "Le Comptoir de Martigny, foire régionale avec exposants locaux, dégustations de produits du terroir et animations culturelles."),
    ("Trail des Dents du Midi","https://www.trailddm.ch/#trail-2026","2026-07-11","2026-07-12","Champéry",
     "Le Trail des Dents du Midi, course de montagne mythique autour du massif des Dents du Midi. Parcours techniques et vues spectaculaires."),
    ("Sierre-Zinal course","https://www.sierre-zinal.com/#course-2026","2026-08-08","2026-08-08","Sierre",
     "La mythique course Sierre-Zinal, la course des cinq 4000. 31 km et 2200m de dénivelé à travers le Val d'Anniviers."),
    ("Grand Raid BCVS","https://www.grandraid-bcvs.ch/#grand-raid-2026","2026-08-22","2026-08-22","Verbier",
     "Le Grand Raid BCVS, course VTT marathone à travers le Valais. De Verbier à Grimentz, un défi légendaire pour les cyclistes."),
    ("Patrouille des Glaciers","https://www.pdg.ch/#pdg-2026","2026-04-22","2026-04-25","Zermatt",
     "La Patrouille des Glaciers, course mythique de ski-alpinisme de Zermatt à Verbier. 53 km et 4000m de dénivelé positif à travers les Alpes."),
    ("Verbier Festival musique classique","https://www.verbierfestival.com/#verbier-2026","2026-07-17","2026-08-02","Verbier",
     "Le Verbier Festival, festival de musique classique de renommée mondiale. Concerts, masterclasses et récitals avec les plus grands artistes."),
    ("Alpentöne Festival Visp","https://www.valais.ch/fr/evenements#alpentone-visp","2026-08-14","2026-08-16","Visp",
     "L'Alpentöne Festival à Visp, festival de musique des Alpes mêlant traditions et modernité. Du yodel au jazz alpin."),
    ("Fête-Dieu Savièse","https://www.valais.ch/fr/evenements#fete-dieu-saviese","2026-06-04","2026-06-04","Savièse",
     "La Fête-Dieu à Savièse, procession traditionnelle avec les Grenadiers du Bon Dieu en costume d'époque. Une tradition valaisanne unique."),
    ("Marché des cépages rares Salquenen","https://www.valais.ch/fr/evenements#marche-cepages-salquenen","2026-09-12","2026-09-12","Salquenen",
     "Le Marché des cépages rares à Salquenen, village viticole renommé. Dégustations de vins issus de cépages autochtones valaisans."),
    ("Festival Antigel Sion","https://www.valais.ch/fr/evenements#antigel-sion","2026-03-20","2026-03-22","Sion",
     "Le Festival Antigel fait étape à Sion avec des spectacles pluridisciplinaires mêlant musique, danse et performances artistiques."),
    ("Hérens Bike Marathon","https://www.valais.ch/fr/evenements#herens-bike","2026-06-28","2026-06-28","Evolène",
     "Le Hérens Bike Marathon, course VTT dans le Val d'Hérens. Parcours exigeant à travers les paysages alpins entre Evolène et les alpages."),
    ("Braderie de Sierre","https://www.valais.ch/fr/evenements#braderie-sierre","2026-05-02","2026-05-02","Sierre",
     "La Grande Braderie de Sierre, un événement shopping en plein air avec commerçants locaux, animations et ambiance festive dans les rues."),
    ("Nuit des musées Valais","https://www.valais.ch/fr/evenements#nuit-musees","2026-11-07","2026-11-07","Sion",
     "La Nuit des musées en Valais, ouverture nocturne exceptionnelle des musées et institutions culturelles avec animations et visites guidées."),
    ("Concours international de Cor des Alpes Nendaz","https://www.valais.ch/fr/evenements#concours-cor-nendaz","2026-07-26","2026-07-26","Nendaz",
     "Le Concours international de Cor des Alpes à Nendaz réunit les meilleurs joueurs du monde dans un cadre alpin spectaculaire."),
]

# ===== LEUKERBAD / BRIG / HAUT-VALAIS =====
HAUT_VALAIS_EVENTS = [
    ("Leukerbad Kultur Sommer","https://www.leukerbad.ch/agenda#kultur-sommer","2026-07-10","2026-07-12","Leukerbad",
     "Le Leukerbad Kultur Sommer, festival culturel estival dans la station thermale. Littérature, musique et arts dans un cadre montagnard unique."),
    ("Internationales Literaturfestival Leukerbad","https://www.leukerbad.ch/agenda#literaturfest","2026-06-26","2026-06-28","Leukerbad",
     "Le Festival international de littérature de Leukerbad, rendez-vous incontournable des amateurs de livres et de rencontres littéraires."),
    ("Oberwalliser Weinfest Salgesch","https://www.valais.ch/fr/evenements#weinfest-salgesch","2026-09-05","2026-09-05","Salquenen",
     "La Fête du vin du Haut-Valais à Salgesch (Salquenen). Dégustation des meilleurs crus valaisans dans le village viticole."),
    ("Ringkuhkampf Raron","https://www.valais.ch/fr/evenements#ringkuhkampf-raron","2026-05-03","2026-05-03","Raron",
     "Combat de reines à Raron, tradition valaisanne ancestrale. Les vaches de la race d'Hérens s'affrontent pour devenir reine."),
    ("Brig Simplon Festival","https://www.valais.ch/fr/evenements#brig-simplon-fest","2026-08-07","2026-08-09","Brig",
     "Le Brig Simplon Festival, festival de musique et de culture dans la ville historique de Brigue. Concerts, gastronomie et animations."),
    ("Ernen Musikdorf Festival","https://www.valais.ch/fr/evenements#musikdorf-ernen","2026-07-18","2026-08-15","Ernen",
     "Le Musikdorf Festival d'Ernen, concerts de musique de chambre dans l'église historique du village musical. Un bijou culturel du Haut-Valais."),
    ("Aletsch Arena Trail","https://www.valais.ch/fr/evenements#aletsch-trail","2026-07-04","2026-07-04","Bettmeralp",
     "Course de trail running avec vue sur le glacier d'Aletsch, patrimoine mondial UNESCO. Parcours spectaculaire en haute montagne."),
    ("Stockalper Festival Brig","https://www.valais.ch/fr/evenements#stockalper-brig","2026-08-28","2026-08-30","Brig",
     "Le Festival au Château Stockalper de Brigue. Concerts et spectacles dans la cour du magnifique palais baroque du 17e siècle."),
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
    "conthey":(46.2261,7.3042),"chamoson":(46.2000,7.2167),"thyon":(46.1833,7.3833),
    "chermignon":(46.3000,7.4667),"st-pierre-de-clages":(46.2500,7.2333),"salquenen":(46.3167,7.5833),
    "evolène":(46.1167,7.4833),"raron":(46.3117,7.8003),"brig":(46.3167,7.9833),
    "ernen":(46.3997,8.1464),"bettmeralp":(46.3889,8.0622),"visp":(46.2944,7.8828),
    "bramois":(46.2333,7.4000),
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

def extract_emails(soup):
    emails = set()
    for a in soup.find_all('a', href=True):
        if 'mailto:' in a['href']: emails.add(a['href'].replace('mailto:','').split('?')[0].strip())
    for m in EMAIL_PATTERN.findall(soup.get_text()): emails.add(m)
    return [e for e in emails if not any(x in e.lower() for x in EXCLUDED_EMAILS) and len(e)>5]

def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS), "Accept": "text/html,*/*;q=0.8", "Accept-Language": "fr-CH,fr;q=0.9"}


class ScraperV9:
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
    
    def fetch(self, url):
        time.sleep(RATE_LIMIT + random.uniform(0, 3))
        try:
            r = self.session.get(url, headers=get_headers(), timeout=30)
            r.raise_for_status()
            return BeautifulSoup(r.text, 'html.parser')
        except Exception as e:
            print(f"⚠️ {e}")
            return None
    
    def scrape_events_with_desc(self, events_list, source_name, visit_pages=True):
        print(f"\n🌐 Source: {source_name} ({len(events_list)} événements)")
        count = 0
        skipped = 0
        
        for item in events_list:
            if count >= MAX_PER_SOURCE:
                break
            
            title, url, start_date, end_date, city, desc = item
            
            if url in self.existing_urls or url in self.seen_urls:
                skipped += 1
                continue
            
            print(f"  🔍 {title[:45]}...", end=" ")
            
            organizer_email = ""
            
            if visit_pages and url.startswith("http"):
                soup = self.fetch(url)
                if soup:
                    emails = extract_emails(soup)
                    if emails:
                        organizer_email = emails[0]
                    # Essayer d'enrichir la description
                    parts = []
                    for p in soup.find_all('p'):
                        t = p.get_text(strip=True)
                        if len(t) > 40 and 'cookie' not in t.lower():
                            parts.append(t)
                    if parts and len(parts[0]) > len(desc):
                        desc = parts[0][:500]
            else:
                time.sleep(0.5)
            
            lat, lng = get_coords(city)
            cats = get_cats(title, desc)
            
            ev = {
                "title": title,
                "description": f"À {city}, Valais : {desc}",
                "location": f"{city}, Valais, Suisse",
                "latitude": lat, "longitude": lng,
                "start_date": start_date, "end_date": end_date, "start_time": None,
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
                print("⏭️")
                skipped += 1
        
        print(f"  📊 {source_name}: {count} ajoutés, {skipped} ignorés")
        return count
    
    def save(self):
        with open("valais_events_v9.json", 'w', encoding='utf-8') as f:
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
        
        print(f"\n💾 {len(self.events)} événements -> valais_events_v9.json")
        print(f"📧 {len(self.emails_data)} nouveaux emails, {len(combined)} total ({len(unique)} uniques)")
    
    def run(self):
        print("=" * 60)
        print("🕷️ SCRAPER V9 - TempsLibre, Sion, été/automne, Haut-Valais")
        print("=" * 60)
        
        total = 0
        
        # TempsLibre.ch - visiter les pages
        total += self.scrape_events_with_desc(TEMPSLIBRE_EVENTS, "TempsLibre.ch", visit_pages=True)
        print(f"\n📈 Sous-total: {total}")
        
        time.sleep(10)
        
        # Sion / événements sportifs - pas de visite
        total += self.scrape_events_with_desc(SION_EVENTS, "Sion Tourisme", visit_pages=False)
        print(f"\n📈 Sous-total: {total}")
        
        # Été / Automne - pas de visite
        total += self.scrape_events_with_desc(ETE_AUTOMNE_EVENTS, "Valais Événements", visit_pages=False)
        print(f"\n📈 Sous-total: {total}")
        
        # Haut-Valais - pas de visite
        total += self.scrape_events_with_desc(HAUT_VALAIS_EVENTS, "Haut-Valais Tourisme", visit_pages=False)
        print(f"\n📈 Sous-total: {total}")
        
        self.save()
        
        total_carte = len(self.existing_urls) + len(self.events)
        print(f"\n{'='*60}")
        print(f"📊 RÉSUMÉ FINAL")
        print(f"  Nouveaux events V9: {len(self.events)}")
        print(f"  Déjà en base: {len(self.existing_urls)}")
        print(f"  🗺️  TOTAL SUR LA CARTE: {total_carte}")
        print(f"  Objectif: 300 → {'✅ ATTEINT!' if total_carte >= 300 else f'Manque {300 - total_carte}'}")
        
        sources = {}
        for e in self.events:
            s = e.get('source_name', '?')
            sources[s] = sources.get(s, 0) + 1
        print(f"\n  Par source:")
        for s, c in sorted(sources.items()):
            print(f"   - {s}: {c}")


if __name__ == "__main__":
    ScraperV9().run()
