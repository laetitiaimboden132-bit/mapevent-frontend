"""
Scraper V6 - Nendaz + Infomaniak Events
Objectif: 60 événements supplémentaires (30 par source)

Usage: python -u valais_scraper_v6_nendaz.py
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
START_DATE = datetime(2026, 3, 1)
END_DATE = datetime(2026, 12, 31)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
EXCLUDED_EMAILS = ['noreply@','no-reply@','privacy@','cookie@','analytics@','@example.','@test.','@localhost','@facebook','@twitter','@google','tracking@']

CAT_KW = {
    "Music > Pop / Variété":["concert","musique","live","music"],
    "Music > Jazz / Soul / Funk":["jazz","blues","soul","funk"],
    "Music > Rock / Metal > Rock":["rock","punk"],
    "Music > Classique > Formes":["classique","orchestre","opéra"],
    "Music > Folk / Acoustic":["folk","cor des alpes","folklorique","acoustic"],
    "Culture > Cinéma & Projections":["cinéma","film","projection"],
    "Culture > Expositions":["exposition","vernissage","galerie","musée","art"],
    "Culture > Conférences & Rencontres":["conférence","rencontre","lecture","littérature"],
    "Culture > Workshops":["atelier","workshop","cours","formation","stage","initiation","brassage","savon","photo"],
    "Arts Vivants > Théâtre":["théâtre","spectacle","comédie","humour","stand-up","pièce"],
    "Arts Vivants > Danse":["danse","ballet"],
    "Food & Drinks > Dégustations":["vin","cave","dégustation","terroir","raclette","fondue","fromage","brunch","boisson"],
    "Food & Drinks > Restauration":["gastronomie","food","repas","souper","tavolata"],
    "Sport > Terrestre":["marathon","course","running","trail","randonnée","triathlon","raquette","marche","yoga","pilates","body","spinning","biathlon"],
    "Sport > Glisse":["ski","freeride","snowboard","luge","descente","flambeaux","speed day"],
    "Sport > VTT & Vélo":["vtt","vélo","mtb","enduro","cyclo"],
    "Sport > Aérien":["parapente","vol"],
    "Famille > Activités":["famille","enfant","junior","kids","bricolage","biscuit","chasse au trésor","marmotte","curling","pâques"],
    "Traditions > Fêtes Locales":["carnaval","fête","marché","tradition","foire","avent"],
    "Festivals":["festival","open air"],
    "Nature > Découverte":["nature","forêt","alpage","barrage","visite guidée","clean-up"],
}

# Événements Nendaz uniques (mars-décembre 2026, dédupliqués)
NENDAZ_EVENTS = [
    ("Les Folies de Tortin","https://www.nendaz.ch/fr/P89194/les-folies-de-tortin","2026-03-14","Nendaz"),
    ("Grand Prix Migros","https://www.nendaz.ch/fr/P76646/grand-prix-migros","2026-03-21","Nendaz"),
    ("Raquettes et raclette","https://www.nendaz.ch/fr/P76638/raquettes-et-raclette","2026-03-05","Nendaz"),
    ("Ski de randonnée nocturne","https://www.nendaz.ch/fr/P91045/ski-de-randonnee-nocturne","2026-03-04","Nendaz"),
    ("Full Moon Party Nendaz","https://www.nendaz.ch/fr/P77039/full-moon-party","2026-03-28","Nendaz"),
    ("Stage initiation cor des Alpes","https://www.nendaz.ch/fr/P76804/stage-d-initiation-au-cor-des-alpes","2026-04-03","Nendaz"),
    ("Girls Powder","https://www.nendaz.ch/fr/P153906/girls-powder","2026-04-04","Nendaz"),
    ("Pâques en folie à Nendaz","https://www.nendaz.ch/fr/P76852/paques-en-folie-a-nendaz","2026-04-05","Nendaz"),
    ("Spectacle Les Prototypes de Geppetto","https://www.nendaz.ch/fr/P205437/spectacle-les-prototypes-de-geppetto","2026-04-18","Nendaz"),
    ("Conférence Nos fourmis","https://www.nendaz.ch/fr/P205439/conference-nos-fourmis","2026-04-18","Nendaz"),
    ("Spectacle Les 4 sans voix","https://www.nendaz.ch/fr/P205441/spectacle-les-4-sans-voix-y-vont-franco","2026-05-09","Nendaz"),
    ("Atelier planification de randonnée","https://www.nendaz.ch/fr/P207747/atelier-planification-de-randonnee","2026-05-09","Nendaz"),
    ("Le réveil des marmottes","https://www.nendaz.ch/fr/P77895/le-reveil-des-marmottes","2026-05-23","Nendaz"),
    ("Leur chant d'automne","https://www.nendaz.ch/fr/P209240/leur-chant-d-automne","2026-05-29","Nendaz"),
    ("Visite guidée vieux village","https://www.nendaz.ch/fr/P91530/visite-guidee-du-vieux-village","2026-05-06","Nendaz"),
    ("Visite du barrage de Cleuson","https://www.nendaz.ch/fr/P76717/visite-du-barrage-de-cleuson","2026-06-26","Nendaz"),
    ("Clean-Up Tour Siviez","https://www.nendaz.ch/fr/P78551/clean-up-tour-siviez","2026-06-27","Nendaz"),
    ("Nuit de la randonnée","https://www.nendaz.ch/fr/P76546/nuit-de-la-randonnee","2026-06-27","Nendaz"),
    ("Venez jouer du cor des Alpes","https://www.nendaz.ch/fr/P91531/venez-jouer-du-cor-des-alpes","2026-07-01","Nendaz"),
    ("La vie sur l'alpage","https://www.nendaz.ch/fr/P76666/la-vie-sur-l-alpage","2026-07-07","Nendaz"),
    ("Festival Int. Cor des Alpes","https://www.nendaz.ch/fr/P76549/festival-international-du-cor-des-alpes","2026-07-24","Nendaz"),
    ("Raclette à l'étable","https://www.nendaz.ch/fr/P108575/raclette-a-l-etable","2026-03-05","Nendaz"),
    ("La vie à l'étable","https://www.nendaz.ch/fr/P108354/la-vie-a-l-etable","2026-04-08","Nendaz"),
    ("Ice disco Nendaz","https://www.nendaz.ch/fr/P91048/ice-disco","2026-03-04","Nendaz"),
    ("Descente aux flambeaux Siviez","https://www.nendaz.ch/fr/P76645/descente-aux-flambeaux","2026-04-06","Nendaz"),
]

# Événements Infomaniak Events Valais (extraits de la page)
INFOMANIAK_EVENTS = [
    ("Calogero - Un soir dans les théâtres","https://infomaniak.events/fr-ch/concerts/calogero-un-soir-dans-les-theatres/9c1b56f0-391f-419d-b570-fb4ec5edfa24/event/1355820","2026-04-17","St-Maurice"),
    ("Brassage de bière","https://infomaniak.events/fr-ch/ateliers-et-stages/brassage-de-biere/95322477-8202-4a6c-9fb2-c94b83f27b44/event/1506395","2026-05-09","Monthey"),
    ("Sauces et condiments végétaux","https://infomaniak.events/fr-ch/ateliers-et-stages/sauces-et-condiments-vegetaux/c83d4667-e23a-4f41-91b0-b71e81b34bb8/event/1506404","2026-03-12","Monthey"),
    ("Les cuissons du végétal","https://infomaniak.events/fr-ch/ateliers-et-stages/les-cuissons-du-vegetal/788cb4f8-7273-4edc-a92d-34954dc25040/event/1506407","2026-04-09","Monthey"),
    ("La couleur des émotions","https://infomaniak.events/fr-ch/famille/la-couleur-des-emotions/dc67e5a3-0f92-4c4e-8b24-0a26ec39872d/event/1504739","2026-04-19","Sion"),
    ("Les trois petites louves","https://infomaniak.events/fr-ch/famille/les-trois-petites-louves/39101fff-41c3-4b38-a043-7e55bb41cfac/event/1504736","2026-03-08","Sion"),
    ("Souper de soutien du FC Saillon","https://infomaniak.events/fr-ch/loisirs/souper-de-soutien-du-fc-saillon/066e1148-cb98-49f7-8095-608248e49dac/event/1574564","2026-03-06","Saillon"),
    ("Atelier Accords vins et fromages valaisans","https://infomaniak.events/fr-ch/loisirs/26022026-atelier-du-terroir-accords-subtils-entre-les-vins-et-les-fromages-valaisans/10b51515-8a20-4ccd-8e2d-867155db6071/event/1544375","2026-03-26","Sion"),
    ("Mon jour de chance","https://infomaniak.events/fr-ch/theatre/mon-jour-de-chance/7eb274fa-839c-4d91-a876-6078fe4315c2/event/1347138","2026-04-23","St-Maurice"),
    ("A qui la faute ?","https://infomaniak.events/fr-ch/theatre/a-qui-la-faute/410edaae-ad10-44c9-a96b-ad7d20ff8855/event/1398309","2026-05-09","St-Maurice"),
    ("Tavolata Parc naturel Pfyn-Finges","https://infomaniak.events/fr-ch/loisirs/tavolata-parc-naturel-pfyn-finges/87f96497-6a3f-4a58-aace-81bd21dbb21b/event/1560758","2026-08-22","Varen"),
    ("Finale Nationale Race d'Hérens","https://infomaniak.events/fr-ch/culture-et-spectacles/finale-nationale-de-la-race-dherens-samedi/a32f3f3c-6da4-4f76-82bd-299b1e2a8f7d/event/1574834","2026-05-09","Sion"),
    ("Oesch's die Dritten","https://infomaniak.events/fr-ch/concerts/oeschs-die-dritten/a72bfc71-8370-42e7-af34-637940a51a91/event/1578854","2026-08-21","Savièse"),
    ("Atelier Initiation dégustation vins valaisans","https://infomaniak.events/fr-ch/loisirs/26032026-atelier-du-terroir-initiation-a-la-degustation-des-vins-valaisans/99a78530-6a4d-42e3-9136-ac79d2604f69/event/1544168","2026-03-26","Sion"),
    ("PHANEE DE POOL entre ciel et scène","https://infomaniak.events/fr-ch/concerts/phanee-de-pool-entre-ciel-et-scene/fc217613-8a86-4394-bbc6-f59ac5cc4b84/event/1560602","2026-03-26","Sion"),
    ("Sylvie Bourban entre ciel et scène","https://infomaniak.events/fr-ch/concerts/sylvie-bourban-entre-ciel-et-scene/ad529aa3-9efd-4e0a-882d-6ab1c19c2f54/event/1562279","2026-03-27","Sion"),
    ("Atelier Boissons fermentées","https://infomaniak.events/fr-ch/loisirs/30042026-atelier-du-terroir-apprenez-a-creer-vos-propres-boissons-fermentees-avec-melanie-vouillamoz-et-johanna-dayer/9e5e965f-2824-4682-b41e-2744613db5da/event/1573217","2026-04-30","Sion"),
    ("Au bout de la laisse - Cie Alsand","https://infomaniak.events/fr-ch/theatre/au-bout-de-la-laisse-cie-alsand/ebfc8e04-6235-4bb1-b797-668e7ba15091/events/1453715","2026-05-20","Sion"),
    ("Guinness Irish Festival 2026","https://infomaniak.events/fr-ch/festivals/guinness-irish-festival-2026/11a7eb8a-a759-4d88-b9d1-3710111dc62b/events/1546547","2026-08-06","Sion"),
    ("Louis Jucker / Kevin Galland","https://infomaniak.events/fr-ch/concerts/louis-jucker-kevin-galland/75c88a56-86de-4ad9-a5cc-06975a20e829/event/1584044","2026-03-21","Sion"),
    ("Andrina Bollinger","https://infomaniak.events/fr-ch/concerts/andrina-bollinger/b11a4d04-868b-458a-9b39-788136e48e26/event/1584050","2026-04-11","Sion"),
    ("Valentin Liechti Trio","https://infomaniak.events/fr-ch/concerts/valentin-liechti-trio/a765bc33-0eea-483f-b3b5-beca3cca3222/event/1584056","2026-05-16","Sion"),
    ("Raclette du Valais AOP avec Eddy Baillifard","https://infomaniak.events/fr-ch/loisirs/04032026-nouveau-format-le-raclette-du-valais-aop-et-lart-de-racler-avec-eddy-baillifard/3db3adcf-4dd1-4a81-a555-9568875c4474/event/1544381","2026-03-04","Sion"),
    ("Cash-Cash!","https://infomaniak.events/fr-ch/humour-et-comedie/cash-cash/9a8fad90-a93d-403c-9902-d2c5523664a5/events/1586114","2026-03-27","Sion"),
    ("Bénabar","https://infomaniak.events/fr-ch/concerts/benabar/52a93cbb-102a-448d-a18e-dbe5515afa9e/event/1579388","2026-11-27","St-Maurice"),
    ("Haroun Bonjour quand même","https://infomaniak.events/fr-ch/humour-et-comedie/haroun-bonjour-quand-meme/b7d5127a-ac0f-45a5-a417-36082efc8d52/event/1421499","2026-10-04","St-Maurice"),
    ("Le Soir des Lions","https://infomaniak.events/fr-ch/culture-et-spectacles/le-soir-des-lions/9ae3d432-bebb-4861-83e3-4081d596b2c9/event/1587713","2026-03-27","Martigny"),
    ("Zone avec de la boue","https://infomaniak.events/fr-ch/culture-et-spectacles/zone-avec-de-la-boue/35ca6b61-dcc7-4865-a6f5-b5d51db17134/event/1587449","2026-03-27","Martigny"),
    ("Tangram - PAN ! La compagnie","https://infomaniak.events/fr-ch/theatre/tangram-pan-la-compagnie/54bd18d4-c3e9-430d-8c67-0f93eccabefb/event/1453589","2026-03-28","Sion"),
    ("Nous ne sommes qu'en surface","https://infomaniak.events/fr-ch/culture-et-spectacles/nous-ne-sommes-quen-surface/91beaafe-3b06-44f6-8815-2f4e31473bc1/event/1587446","2026-03-26","Martigny"),
]

COORDS = {
    "nendaz":(46.1867,7.3053),"sion":(46.2333,7.3667),"sierre":(46.2920,7.5347),
    "martigny":(46.0986,7.0731),"monthey":(46.2548,6.9543),"st-maurice":(46.2167,7.0000),
    "saillon":(46.1722,7.1917),"savièse":(46.2500,7.3500),"varen":(46.3167,7.6167),
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


class ScraperV6:
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
            print(f"  ⚠️ {e}")
            return None
    
    def add(self, ev):
        key = ev['title'].lower()[:50]
        if key in self.seen: return False
        self.seen.add(key)
        self.events.append(ev)
        if ev.get('organizer_email'):
            self.emails_data.append({'email':ev['organizer_email'],'title':ev['title'],'source_url':ev['source_url'],'source_name':ev['source_name']})
        return True
    
    def scrape_list(self, event_list, source_name):
        print(f"\n🌐 Source: {source_name} ({len(event_list)} événements)")
        count = 0
        for title, url, date, city in event_list:
            if count >= MAX_PER_SOURCE: break
            print(f"  🔍 {title[:40]}...", end=" ")
            
            soup = self.fetch(url)
            description = ""
            organizer_email = ""
            
            if soup:
                parts = []
                for p in soup.find_all('p'):
                    t = p.get_text(strip=True)
                    if len(t)>30 and 'cookie' not in t.lower() and 'privacy' not in t.lower() and 'panier' not in t.lower():
                        parts.append(t)
                if parts: description = parts[0][:500]
                emails = extract_emails(soup)
                if emails: organizer_email = emails[0]
            
            if not description:
                description = f"Événement à {city}, Valais : {title}. Consultez le lien original pour plus d'informations."
            else:
                description = f"À {city}, Valais : {description}"
            
            lat, lng = get_coords(city)
            cats = get_cats(title, description)
            
            ev = {
                "title": title, "description": description[:500],
                "location": f"{city}, Valais, Suisse",
                "latitude": lat, "longitude": lng,
                "start_date": date, "end_date": date, "start_time": None,
                "categories": cats, "source_url": url,
                "organizer_email": organizer_email,
                "organizer_name": source_name, "source_name": source_name,
            }
            
            if self.add(ev):
                count += 1
                ei = "📧" if organizer_email else "  "
                print(f"✅ {count} {ei}")
            else:
                print("⏭️")
        
        print(f"  📊 Total {source_name}: {count}")
        return count
    
    def save(self):
        with open("valais_events_v6.json", 'w', encoding='utf-8') as f:
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
        
        # Mettre à jour le résumé
        unique = set(e['email'] for e in combined)
        with open(os.path.join(edir, "RESUME_EMAILS.txt"), 'w', encoding='utf-8') as f:
            f.write(f"EMAILS ORGANISATEURS - MapEventAI\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"Total avec email: {len(combined)}\n")
            f.write(f"Emails uniques: {len(unique)}\n")
            f.write(f"{'='*60}\n\nEMAILS UNIQUES ({len(unique)}):\n")
            for e in sorted(unique): f.write(f"  {e}\n")
            f.write(f"\n{'='*60}\n\nDÉTAIL:\n")
            for e in combined:
                f.write(f"  {e['email']:<35} | {e['title'][:40]} | {e['source_name']}\n")
        
        # CSV
        with open(os.path.join(edir, "emails.csv"), 'w', encoding='utf-8') as f:
            f.write("email,titre,source_url,source\n")
            for e in combined:
                t = e['title'].replace('"','').replace(',',';')
                f.write(f"{e['email']},{t},{e['source_url']},{e['source_name']}\n")
        
        print(f"\n💾 {len(self.events)} événements -> valais_events_v6.json")
        print(f"📧 {len(self.emails_data)} nouveaux emails, {len(combined)} total ({len(unique)} uniques)")
    
    def run(self):
        print("=" * 60)
        print("🕷️ SCRAPER V6 - Nendaz + Infomaniak Events")
        print("=" * 60)
        
        total = 0
        total += self.scrape_list(NENDAZ_EVENTS, "Nendaz Tourisme")
        print(f"\n📈 Total: {total}")
        time.sleep(15)
        
        total += self.scrape_list(INFOMANIAK_EVENTS, "Infomaniak Events")
        print(f"\n📈 Total: {total}")
        
        self.save()
        
        with_email = len([e for e in self.events if e.get('organizer_email')])
        print(f"\n{'='*60}")
        print(f"📊 RÉSUMÉ: {len(self.events)} events, {with_email} avec email")
        sources = {}
        for e in self.events:
            s = e.get('source_name','?')
            sources[s] = sources.get(s,0)+1
        for s,c in sorted(sources.items()): print(f"   - {s}: {c}")


if __name__ == "__main__":
    ScraperV6().run()
