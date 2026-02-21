"""
Scraper Valais V5b - Approche ciblée par URLs connues
Utilise les URLs exactes des événements trouvés sur valais.ch
+ Culture Valais pages profondes + TempsLibre pages d'événements individuels

Usage: python valais_scraper_v5b.py
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

# Forcer UTF-8 + flush
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

import builtins
_orig_print = builtins.print
def _fp(*a, **kw):
    kw.setdefault('flush', True)
    _orig_print(*a, **kw)
builtins.print = _fp

# Config
RATE_LIMIT = 8
MAX_PER_SOURCE = 30
START_DATE = datetime(2026, 3, 1)
END_DATE = datetime(2026, 12, 31)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
EXCLUDED_EMAILS = ['noreply@','no-reply@','privacy@','cookie@','analytics@','@example.','@test.','@localhost','@facebook','@twitter','@google']

# Coordonnées villes Valais
COORDS = {
    "sion":(46.2333,7.3667),"sierre":(46.2920,7.5347),"martigny":(46.0986,7.0731),
    "monthey":(46.2548,6.9543),"brig":(46.3133,7.9872),"visp":(46.2944,7.8828),
    "zermatt":(46.0207,7.7491),"verbier":(46.0964,7.2286),"crans-montana":(46.3072,7.4819),
    "nendaz":(46.1867,7.3053),"saas-fee":(46.1081,7.9272),"leukerbad":(46.3792,7.6331),
    "champéry":(46.1758,6.8714),"morgins":(46.2383,6.8528),"ernen":(46.3978,8.1478),
    "fiesch":(46.4000,8.1333),"bettmeralp":(46.3881,8.0625),"grimentz":(46.1797,7.5761),
    "st-luc":(46.2197,7.6097),"zinal":(46.1350,7.6256),"fully":(46.1333,7.1167),
    "saillon":(46.1722,7.1917),"saxon":(46.1500,7.1667),"chamoson":(46.2000,7.2167),
    "st-maurice":(46.2167,7.0000),"veysonnaz":(46.1881,7.3308),"savièse":(46.2500,7.3500),
    "salgesch":(46.3083,7.5722),"obergoms":(46.5167,8.2833),"evolène":(46.1128,7.4944),
    "gampel":(46.3167,7.7500),"leuk":(46.3167,7.6333),"turtmann":(46.3028,7.7083),
    "val d'illiez":(46.2006,6.8806),"troistorrents":(46.2286,6.9094),
    "st-pierre-de-clages":(46.1819,7.2258),"ovronnaz":(46.1983,7.1733),
    "leytron":(46.1833,7.2167),"randa":(46.0986,7.7833),"täsch":(46.0672,7.7792),
    "conthey":(46.2167,7.3000),"ardon":(46.2097,7.2583),"aproz":(46.2167,7.3333),
}

# Catégories
CAT_KW = {
    "Music > Pop / Variété":["concert","musique","unplugged","acoustic","music festival","frauenstimmen"],
    "Music > Jazz / Soul / Funk":["jazz","blues","soul","funk","swing","blues festival"],
    "Music > Rock / Metal > Rock":["rock","punk","rock the pistes"],
    "Music > Classique > Formes":["classique","orchestre","symphonie","opéra","musikdorf","zermatt music"],
    "Music > Folk / Acoustic":["folk","country","cor des alpes","folklorique"],
    "Culture > Cinéma & Projections":["cinéma","film","projection"],
    "Culture > Expositions":["exposition","vernissage","galerie","musée","art"],
    "Culture > Conférences & Rencontres":["conférence","rencontre","lecture","littérature","livre","fête du livre"],
    "Culture > Workshops":["atelier","workshop","cours","formation"],
    "Arts Vivants > Théâtre":["théâtre","spectacle","comédie","humour","rires","maxi-rires"],
    "Arts Vivants > Danse":["danse","ballet"],
    "Food & Drinks > Dégustations":["vin","cave","caves ouvertes","printemps du vin","wine","tavolata","dégustation"],
    "Food & Drinks > Restauration":["gastronomie","food","raclette","terroir","châtaigne","asperge","rando'clette","brunch","gastronomique","epicurialpes"],
    "Sport > Terrestre":["marathon","course","running","trail","randonnée","triathlon","ultraks","sierre-zinal","grand raid","semi du rhône"],
    "Sport > Glisse":["ski","freeride","snowboard","coupe du monde","gommerlauf","alpin"],
    "Sport > VTT & Vélo":["vtt","vélo","mtb","enduro","cyclosportive","pass'portes","chasing cancellara","gravel"],
    "Famille > Activités":["famille","enfant","junior","kids","am stram gram"],
    "Traditions > Fêtes Locales":["carnaval","fête","marché","tradition","foire","avent","pâques","taille","gilihüsine"],
    "Festivals":["festival","open air","sion sous les étoiles"],
    "Sport > Course Orientation":["orienteering","orientation"],
}

# URLs connues des événements valais.ch (mars-déc 2026)
VALAIS_CH_EVENTS = [
    # Page 1
    ("Défi des Faverges","https://www.valais.ch/fr/evenements/defi-des-faverges","2026-03-14","Crans-Montana"),
    ("FESTIVAL ROCK THE PISTES 2026","https://www.valais.ch/fr/evenements/festival-rock-the-pistes-2026","2026-03-15","Morgins"),
    ("Rando'clette","https://www.valais.ch/fr/evenements/rando-clette","2026-03-21","Grimentz"),
    ("Maxi-Rires Festival","https://www.valais.ch/fr/evenements/maxi-rires-festival","2026-03-23","Champéry"),
    ("YETI Xtreme Verbier","https://www.valais.ch/fr/evenements/yeti-xtreme-verbier","2026-03-27","Verbier"),
    ("Fête de la Taille à Chamoson","https://www.valais.ch/fr/evenements/fete-de-la-taille-a-chamoson","2026-03-28","Chamoson"),
    ("Zermatt Unplugged 2026","https://www.valais.ch/fr/evenements/zermatt-unplugged-2026","2026-04-07","Zermatt"),
    ("Marché de Pâques","https://www.valais.ch/fr/evenements/marche-de-paques","2026-04-08","Brig"),
    ("Nendaz Snow Vibes Festival","https://www.valais.ch/fr/evenements/nendaz-snow-vibes-festival","2026-04-11","Nendaz"),
    ("Printemps du vin","https://www.valais.ch/fr/evenements/printemps-du-vin","2026-04-25","Salgesch"),
    ("Fête de l'asperge 2026","https://www.valais.ch/fr/evenements/fete-de-l-asperge-2026","2026-05-02","Saillon"),
    ("Wine & Brunch Tavolata","https://www.valais.ch/fr/evenements/wine-brunch-tavolata","2026-05-14","Salgesch"),
    ("Jardin des vins","https://www.valais.ch/fr/evenements/jardin-des-vins","2026-05-14","Sion"),
    ("Les caves ouvertes du Valais","https://www.valais.ch/fr/evenements/les-caves-ouvertes-du-valais-celebrent-leur-20e-edition","2026-05-14","Sion"),
    ("Marathon des Terroirs du Valais","https://www.valais.ch/fr/evenements/marathon-des-terroirs-du-valais-bcvs-2026","2026-05-23","Martigny"),
    ("Frauenstimmen Festival","https://www.valais.ch/fr/evenements/frauenstimmen-festival","2026-05-29","Brig"),
    ("Festival Musikdorf Ernen","https://www.valais.ch/fr/evenements/festival-musikdorf-ernen","2026-06-07","Ernen"),
    ("Sierre Blues Festival","https://www.valais.ch/fr/evenements/sierre-blues-festival","2026-06-18","Sierre"),
    ("Festival Week-end au bord de l'eau","https://www.valais.ch/fr/evenements/19-festival-week-end-au-bord-de-l-eau","2026-06-25","Sierre"),
    ("Festival int. de littérature","https://www.valais.ch/fr/evenements/festival-int-de-litterature","2026-06-26","Leukerbad"),
    ("Festival Les 5 Continents","https://www.valais.ch/fr/evenements/festival-les-5-continents","2026-06-26","Martigny"),
    ("PASS'PORTES 2026","https://www.valais.ch/fr/evenements/pass-portes-2026","2026-06-26","Morgins"),
    ("Aletsch Halbmarathon","https://www.valais.ch/fr/evenements/aletsch-halbmarathon-weekend","2026-06-27","Bettmeralp"),
    # Page 2
    ("Gornergrat Zermatt Marathon","https://www.valais.ch/fr/evenements/gornergrat-zermatt-marathon","2026-07-04","Zermatt"),
    ("Am Stram Gram","https://www.valais.ch/fr/evenements/am-stram-gram","2026-07-09","Crans-Montana"),
    ("Swiss Orienteering Week","https://www.valais.ch/fr/evenements/swiss-orienteering-week-2026-portes-du-soleil","2026-07-11","Morgins"),
    ("Verbier Festival","https://www.valais.ch/fr/evenements/verbier-festival","2026-07-16","Verbier"),
    ("Sion sous les étoiles","https://www.valais.ch/fr/evenements/sion-sous-les-etoiles","2026-07-16","Sion"),
    ("UCI Mountainbike Enduro Weltcup","https://www.valais.ch/fr/evenements/uci-mountainbike-enduro-weltcup","2026-07-16","Fiesch"),
    ("Cyclosportive & Running du Valais","https://www.valais.ch/fr/evenements/cyclosportive-running-du-valais","2026-07-31","Sion"),
    ("Sierre-Zinal","https://www.valais.ch/fr/evenements/sierre-zinal","2026-08-07","Sierre"),
    ("Swiss Alps 100","https://www.valais.ch/fr/evenements/swiss-alps-100","2026-08-07","Fiesch"),
    ("Festival folklorique","https://www.valais.ch/fr/evenements/festival-folklorique","2026-08-09","Zermatt"),
    ("Open Air Gampel","https://www.valais.ch/fr/evenements/open-air-gampel","2026-08-19","Gampel"),
    ("Matterhorn Ultraks 2026","https://www.valais.ch/fr/evenements/matterhorn-ultraks-2026","2026-08-21","Zermatt"),
    ("Grand Raid BCVS","https://www.valais.ch/fr/evenements/grand-raid-bcvs","2026-08-22","Nendaz"),
    ("33ème Fête du Livre","https://www.valais.ch/fr/evenements/33eme-fete-du-livre","2026-08-28","St-Pierre-de-Clages"),
    ("Omega European Masters","https://www.valais.ch/fr/evenements/omega-european-masters","2026-09-03","Crans-Montana"),
    ("Parcours Gastronomique Nostalgique","https://www.valais.ch/fr/evenements/parcours-gastronomique-nostalgique","2026-09-06","Saas-Fee"),
    ("Rencontre de musique folklorique","https://www.valais.ch/fr/evenements/rencontre-de-musique-folklorique","2026-09-04","Leukerbad"),
    ("Wildstrubel by UTMB","https://www.valais.ch/fr/evenements/wildstrubel-by-utmb","2026-09-10","Crans-Montana"),
    ("Zermatt Music Festival & Academy","https://www.valais.ch/fr/evenements/zermatt-music-festival-academy","2026-09-11","Zermatt"),
    ("Chasing Cancellara","https://www.valais.ch/fr/evenements/chasing-cancellara-zuerich-zermatt","2026-09-12","Zermatt"),
    ("Gilihüsine","https://www.valais.ch/fr/evenements/gilihuesine","2026-09-20","Bettmeralp"),
    ("Marché Püru-Märt Cultura Turtmann","https://www.valais.ch/fr/evenements/marche-pueru-maert-cultura-turtmann","2026-09-26","Turtmann"),
    ("66e Foire du Valais","https://www.valais.ch/fr/evenements/66e-foire-du-valais","2026-10-02","Martigny"),
    ("Epicurialpes","https://www.valais.ch/fr/evenements/epicurialpes","2026-10-09","Grimentz"),
    ("Marché automnal Lonza-Märt","https://www.valais.ch/fr/evenements/marche-automnal-lonza-maert","2026-10-10","Gampel"),
    ("32e Fête de la Châtaigne","https://www.valais.ch/fr/evenements/32e-fete-de-la-chataigne","2026-10-17","Fully"),
    ("Course de montagne de Jeizinen","https://www.valais.ch/fr/evenements/course-de-montagne-de-jeizinen","2026-10-18","Gampel"),
    ("Rallye International du Valais","https://www.valais.ch/fr/evenements/rallye-international-du-valais","2026-10-29","Martigny"),
    ("Marché de l'Avent de Conches","https://www.valais.ch/fr/evenements/marche-de-l-avent-de-conches","2026-11-20","Fiesch"),
]


def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-CH,fr;q=0.9,en;q=0.5",
    }

def extract_emails(soup):
    emails = set()
    for link in soup.find_all('a', href=True):
        if 'mailto:' in link['href']:
            emails.add(link['href'].replace('mailto:','').split('?')[0].strip())
    for m in EMAIL_PATTERN.findall(soup.get_text()):
        emails.add(m)
    return [e for e in emails if not any(ex in e.lower() for ex in EXCLUDED_EMAILS) and len(e) > 5]

def get_coords(city):
    c = city.lower().strip()
    for k, v in COORDS.items():
        if k in c:
            return (v[0] + random.uniform(-0.003,0.003), v[1] + random.uniform(-0.003,0.003))
    return (46.2333 + random.uniform(-0.01,0.01), 7.3667 + random.uniform(-0.01,0.01))

def get_cats(title, desc=""):
    t = f"{title} {desc}".lower()
    cats = []
    for cat, kws in CAT_KW.items():
        for kw in kws:
            if kw in t:
                cats.append(cat)
                break
    return cats[:3] if cats else ["Culture > Expositions"]


class ScraperV5b:
    def __init__(self):
        self.session = requests.Session()
        self.events = []
        self.seen = set()
        self.emails_data = []
    
    def fetch(self, url):
        time.sleep(RATE_LIMIT + random.uniform(0, 3))
        try:
            r = self.session.get(url, headers=get_headers(), timeout=30)
            r.raise_for_status()
            return BeautifulSoup(r.text, 'html.parser')
        except Exception as e:
            print(f"  ⚠️ Erreur: {url}: {e}")
            return None
    
    def add(self, ev):
        key = ev['title'].lower()[:50]
        if key in self.seen:
            return False
        self.seen.add(key)
        self.events.append(ev)
        if ev.get('organizer_email'):
            self.emails_data.append({
                'email': ev['organizer_email'],
                'title': ev['title'],
                'source_url': ev['source_url'],
                'source_name': ev['source_name']
            })
        return True
    
    def scrape_valais_ch(self):
        """Scrape les 52 événements connus de valais.ch"""
        source = "Valais Tourisme"
        print(f"\n🌐 Source: {source} ({len(VALAIS_CH_EVENTS)} événements)")
        count = 0
        
        for title, url, date, city in VALAIS_CH_EVENTS:
            if count >= MAX_PER_SOURCE:
                break
            
            print(f"  🔍 {title[:40]}...", end=" ")
            soup = self.fetch(url)
            
            # Extraire description et email de la page de détail
            description = ""
            organizer_email = ""
            
            if soup:
                # Description
                parts = []
                for p in soup.find_all('p'):
                    t = p.get_text(strip=True)
                    if len(t) > 40 and 'cookie' not in t.lower() and 'privacy' not in t.lower():
                        parts.append(t)
                if parts:
                    description = parts[0][:500]
                
                # Emails
                emails = extract_emails(soup)
                if emails:
                    organizer_email = emails[0]
            
            if not description:
                description = f"Événement en Valais : {title}. Se déroulant à {city}, cet événement fait partie du calendrier officiel valaisan."
            else:
                # Reformuler
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
                "organizer_name": source,
                "source_name": source,
            }
            
            if self.add(ev):
                count += 1
                email_icon = "📧" if organizer_email else "  "
                print(f"✅ {count} {email_icon}")
            else:
                print("⏭️ doublon")
        
        print(f"  📊 Total {source}: {count}")
        return count
    
    def scrape_culture_valais_deep(self):
        """Scrape les pages profondes de Culture Valais"""
        source = "Culture Valais"
        print(f"\n🌐 Source: {source} (pages 2-20)")
        count = 0
        
        for page_num in range(2, 21):
            if count >= MAX_PER_SOURCE:
                break
            
            url = f"https://agenda.culturevalais.ch/fr/agenda/evenements?page={page_num}"
            print(f"  📄 Page {page_num}...", end=" ")
            soup = self.fetch(url)
            if not soup:
                print("❌")
                continue
            
            # Trouver les liens vers les détails
            links = []
            for a in soup.find_all('a', href=True):
                if '/event/show/' in a['href']:
                    full = urljoin("https://agenda.culturevalais.ch", a['href'])
                    if full not in links:
                        links.append(full)
            
            print(f"{len(links)} liens")
            
            for link in links:
                if count >= MAX_PER_SOURCE:
                    break
                
                ev = self.scrape_cv_detail(link, source)
                if ev:
                    if self.add(ev):
                        count += 1
                        email_icon = "📧" if ev.get('organizer_email') else "  "
                        print(f"  ✅ {count}/{MAX_PER_SOURCE}: {ev['title'][:35]} {email_icon}")
            
            if not links:
                print(f"  (fin des pages)")
                break
        
        print(f"  📊 Total {source}: {count}")
        return count
    
    def scrape_cv_detail(self, url, source):
        soup = self.fetch(url)
        if not soup:
            return None
        
        try:
            title_tag = soup.find('h1') or soup.find('h2')
            title = title_tag.get_text(strip=True) if title_tag else None
            if not title or len(title) < 3:
                return None
            
            # Dates
            text = soup.get_text()
            start_date, end_date = None, None
            
            # Chercher les dates
            matches = re.findall(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', text)
            for m in matches:
                d_str = f"{m[2]}-{m[1].zfill(2)}-{m[0].zfill(2)}"
                try:
                    d = datetime.strptime(d_str, "%Y-%m-%d")
                    if START_DATE <= d <= END_DATE:
                        if not start_date:
                            start_date = d_str
                        else:
                            end_date = d_str
                except:
                    pass
            
            if not start_date:
                return None
            if not end_date:
                end_date = start_date
            
            # Description
            parts = []
            for p in soup.find_all('p'):
                t = p.get_text(strip=True)
                if len(t) > 30:
                    parts.append(t)
            description = " ".join(parts[:2])[:500] if parts else ""
            
            # Location
            location = "Valais, Suisse"
            for city in COORDS:
                if city in text.lower():
                    location = f"{city.capitalize()}, Valais, Suisse"
                    break
            
            emails = extract_emails(soup)
            lat, lng = get_coords(location)
            cats = get_cats(title, description)
            
            return {
                "title": title,
                "description": f"En {location} : {description}" if description else f"Événement culturel en Valais : {title}",
                "location": location,
                "latitude": lat,
                "longitude": lng,
                "start_date": start_date,
                "end_date": end_date,
                "start_time": None,
                "categories": cats,
                "source_url": url,
                "organizer_email": emails[0] if emails else "",
                "organizer_name": source,
                "source_name": source,
            }
        except Exception as e:
            print(f"  ⚠️ {e}")
            return None
    
    def save(self):
        # Sauvegarder les événements
        with open("valais_events_v5.json", 'w', encoding='utf-8') as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)
        
        # Créer le dossier emails
        edir = "emails_organisateurs"
        os.makedirs(edir, exist_ok=True)
        
        with open(os.path.join(edir, "TOUS_LES_EMAILS.json"), 'w', encoding='utf-8') as f:
            json.dump(self.emails_data, f, ensure_ascii=False, indent=2)
        
        # Résumé texte
        unique = set(e['email'] for e in self.emails_data)
        with open(os.path.join(edir, "RESUME_EMAILS.txt"), 'w', encoding='utf-8') as f:
            f.write(f"EMAILS ORGANISATEURS - MapEventAI\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"Total événements: {len(self.events)}\n")
            f.write(f"Avec email: {len(self.emails_data)}\n")
            f.write(f"Emails uniques: {len(unique)}\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"EMAILS UNIQUES ({len(unique)}):\n")
            for e in sorted(unique):
                f.write(f"  {e}\n")
            f.write(f"\n{'='*60}\n\nDÉTAIL:\n")
            for e in self.emails_data:
                f.write(f"  {e['email']:<35} | {e['title'][:40]} | {e['source_name']}\n")
        
        # Fichier CSV pour import facile
        with open(os.path.join(edir, "emails.csv"), 'w', encoding='utf-8') as f:
            f.write("email,titre,source_url,source\n")
            for e in self.emails_data:
                title_clean = e['title'].replace('"','').replace(',',';')
                f.write(f"{e['email']},{title_clean},{e['source_url']},{e['source_name']}\n")
        
        print(f"\n💾 {len(self.events)} événements -> valais_events_v5.json")
        print(f"📧 {len(self.emails_data)} emails ({len(unique)} uniques) -> emails_organisateurs/")
    
    def run(self):
        print("=" * 60)
        print("🕷️ SCRAPER VALAIS V5b - Multi-sources ciblé")
        print(f"   Max par source: {MAX_PER_SOURCE}")
        print(f"   Période: mars à décembre 2026")
        print("=" * 60)
        
        total = 0
        
        # 1. Valais.ch - 30 événements max (52 disponibles)
        total += self.scrape_valais_ch()
        print(f"\n📈 Total: {total}")
        time.sleep(15)
        
        # 2. Culture Valais - 30 max
        total += self.scrape_culture_valais_deep()
        print(f"\n📈 Total: {total}")
        
        self.save()
        
        # Résumé
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ")
        print("=" * 60)
        with_email = len([e for e in self.events if e.get('organizer_email')])
        print(f"   Total: {len(self.events)}")
        print(f"   Avec email: {with_email}")
        print(f"   Sans email: {len(self.events) - with_email}")
        
        sources = {}
        for e in self.events:
            s = e.get('source_name','?')
            sources[s] = sources.get(s,0) + 1
        for s,c in sorted(sources.items()):
            print(f"   - {s}: {c}")


if __name__ == "__main__":
    scraper = ScraperV5b()
    scraper.run()
