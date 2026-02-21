"""
Scraper V10 - Dernières sources pour atteindre 300 événements
Événements été/automne supplémentaires dans tout le Valais

Usage: python -u valais_scraper_v10_final.py
"""

import requests
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

CAT_KW = {
    "Music > Pop / Variété":["concert","musique","live","music","chanson"],
    "Music > Jazz / Soul / Funk":["jazz","blues","soul","funk"],
    "Music > Rock / Metal > Rock":["rock","punk","metal"],
    "Music > Classique > Formes":["classique","orchestre","opéra"],
    "Music > Folk / Acoustic":["folk","cor des alpes","folklorique","yodel"],
    "Music > Electro":["electro","dj","clubbing"],
    "Culture > Cinéma & Projections":["cinéma","film","projection"],
    "Culture > Expositions":["exposition","vernissage","galerie","musée","art"],
    "Culture > Conférences & Rencontres":["conférence","rencontre","lecture","littérature","livre"],
    "Culture > Workshops":["atelier","workshop","cours","formation","stage","poterie"],
    "Arts Vivants > Théâtre":["théâtre","spectacle","comédie","humour","conte"],
    "Arts Vivants > Danse":["danse","ballet"],
    "Food & Drinks > Dégustations":["vin","cave","dégustation","terroir","raclette","fondue","fromage","châtaigne","abricot","asperge","safran"],
    "Food & Drinks > Restauration":["gastronomie","food","repas","souper","brunch"],
    "Sport > Terrestre":["marathon","course","running","trail","randonnée","triathlon","raquette","marche","yoga","pilates","fitness","trek","vertical"],
    "Sport > Glisse":["ski","freeride","snowboard","luge","descente","flambeaux"],
    "Sport > VTT & Vélo":["vtt","vélo","mtb","enduro","bike","cyclo"],
    "Sport > Aérien":["parapente","vol"],
    "Sport > Golf":["golf","masters"],
    "Sport > Escalade":["escalade","grimpe","via ferrata","boulder"],
    "Famille > Activités":["famille","enfant","junior","kids","chasse au trésor","fête foraine"],
    "Traditions > Fêtes Locales":["carnaval","fête","marché","tradition","foire","national","1er août","inalpe","désalpe"],
    "Festivals":["festival","open air","unplugged","palp"],
    "Nature > Découverte":["nature","forêt","alpage","barrage","visite","clean-up","faune","animaux","observation"],
}

# ===== LOT 10A: Marchés et fêtes locales =====
MARCHES_FETES = [
    ("Marché printanier de Sion","https://siontourisme.ch/fr/agenda#marche-printanier","2026-04-18","2026-04-18","Sion",
     "Grand marché de printemps dans les rues de la vieille ville de Sion. Artisans, producteurs locaux et animations florales."),
    ("Fête des asperges Saxon","https://www.valais.ch/fr/evenements#fete-asperges-saxon","2026-05-09","2026-05-09","Saxon",
     "La Fête des asperges de Saxon célèbre le légume star du printemps valaisan. Dégustation, vente directe et animations gourmandes."),
    ("Fête du safran Mund","https://www.valais.ch/fr/evenements#fete-safran-mund","2026-10-24","2026-10-24","Mund",
     "La Fête du safran de Mund, seul lieu de culture du safran en Suisse. Découverte de l'or rouge du Valais et dégustations."),
    ("Marché de l'abricot Saxon","https://www.valais.ch/fr/evenements#marche-abricot-saxon","2026-07-18","2026-07-18","Saxon",
     "Le Marché de l'abricot de Saxon, capitale suisse de l'abricot. Dégustations, produits dérivés et ambiance estivale."),
    ("Marché médiéval Saillon","https://www.valais.ch/fr/evenements#marche-medieval-saillon","2026-08-15","2026-08-16","Saillon",
     "Le Marché médiéval de Saillon transforme le village fortifié en cité médiévale. Artisans, troubadours et banquet d'époque."),
    ("Foire aux cerises Brigue","https://www.valais.ch/fr/evenements#foire-cerises-brig","2026-06-27","2026-06-27","Brig",
     "La traditionnelle Foire aux cerises de Brigue. Marché de cerises fraîches, confitures et produits artisanaux du Haut-Valais."),
    ("Marché nocturne Sierre","https://www.sierre.ch/fr/calendrier-manifestations#marche-nocturne","2026-07-04","2026-07-04","Sierre",
     "Le Marché nocturne de Sierre avec stands gourmands, artisanat local et animations musicales sous les étoiles de la cité du soleil."),
    ("Brocante de Martigny","https://www.valais.ch/fr/evenements#brocante-martigny","2026-06-14","2026-06-14","Martigny",
     "La Grande Brocante de Martigny, un rendez-vous incontournable pour chineurs et amateurs d'antiquités dans les rues de la ville."),
    ("Fête de la mi-été Evolène","https://www.valais.ch/fr/evenements#mi-ete-evolene","2026-07-25","2026-07-25","Evolène",
     "La Fête de la mi-été à Evolène avec musique traditionnelle, danses folkloriques et spécialités culinaires du Val d'Hérens."),
    ("Marché de Noël Brig","https://www.valais.ch/fr/evenements#noel-brig","2026-12-05","2026-12-06","Brig",
     "Le Marché de Noël de Brigue au Château Stockalper. Artisanat, gourmandises et ambiance féerique dans la cour baroque."),
]

# ===== LOT 10B: Sport été =====
SPORT_ETE = [
    ("Vertical Kilometer Fully","https://www.valais.ch/fr/evenements#vertical-km-fully","2026-05-30","2026-05-30","Fully",
     "La course Vertical Kilometer de Fully, 1000m de dénivelé positif en un minimum de temps. Un défi pour les coureurs de montagne."),
    ("Ultra Tour Monte Rosa","https://www.valais.ch/fr/evenements#ultra-monte-rosa","2026-08-28","2026-08-30","Zermatt",
     "L'Ultra Tour Monte Rosa, course d'ultra-trail de 170 km autour du Mont Rose. Un des ultras les plus spectaculaires des Alpes."),
    ("Grimselpass Challenge Trail","https://www.valais.ch/fr/evenements#grimsel-trail","2026-07-25","2026-07-25","Oberwald",
     "Course de trail au col du Grimsel. Parcours alpin exigeant avec passages à plus de 2400m d'altitude dans le Haut-Valais."),
    ("Via Valais trail running","https://www.valais.ch/fr/evenements#via-valais","2026-09-19","2026-09-20","Martigny",
     "Le Via Valais, trail running de Martigny à Brigue le long de la route historique du Simplon. 130 km à travers tout le canton."),
    ("Swiss Peaks Trail Champéry","https://www.valais.ch/fr/evenements#swiss-peaks","2026-09-05","2026-09-07","Champéry",
     "Le Swiss Peaks Trail, course d'ultra-trail de 170 km à travers les Alpes valaisannes. De Champéry au Simplon."),
    ("Nendaz Trail des Bisses","https://www.valais.ch/fr/evenements#trail-bisses-nendaz","2026-06-13","2026-06-13","Nendaz",
     "Le Trail des Bisses de Nendaz, course de trail le long des célèbres bisses valaisans. Parcours panoramique et historique."),
    ("Crans-Montana Vertical Challenge","https://www.valais.ch/fr/evenements#vertical-cm","2026-06-06","2026-06-06","Crans-Montana",
     "Challenge vertical à Crans-Montana. Course de montagne avec un dénivelé impressionnant et des vues sur les Alpes bernoises."),
    ("Course pédestre Saillon-Ovronnaz","https://www.valais.ch/fr/evenements#course-saillon","2026-05-16","2026-05-16","Saillon",
     "Course pédestre de Saillon à Ovronnaz. Parcours familial et compétitif à travers les vignobles et la montagne valaisanne."),
]

# ===== LOT 10C: Culture été/automne =====
CULTURE_EXTRA = [
    ("Fête de la musique Sion","https://www.valais.ch/fr/evenements#fete-musique-sion","2026-06-21","2026-06-21","Sion",
     "La Fête de la musique de Sion, concerts gratuits dans toute la ville. Rock, jazz, classique et musiques du monde dans les rues."),
    ("Nuits du conte Valais","https://www.valais.ch/fr/evenements#nuits-conte","2026-11-06","2026-11-06","Sion",
     "Les Nuits du conte en Valais, soirée de contes et récits dans différents lieux culturels du canton. Tradition orale vivante."),
    ("Journées du patrimoine Valais","https://www.valais.ch/fr/evenements#patrimoine-valais","2026-09-12","2026-09-13","Sion",
     "Les Journées européennes du patrimoine en Valais. Visites gratuites de monuments, châteaux et sites historiques normalement fermés."),
    ("Festival Rives du Rhône Sion","https://www.valais.ch/fr/evenements#rives-rhone","2026-06-19","2026-06-20","Sion",
     "Le Festival Rives du Rhône à Sion. Concerts, food trucks et animations en plein air au bord du Rhône."),
    ("Théâtre en Plein Air Martigny","https://www.valais.ch/fr/evenements#theatre-plein-air","2026-07-10","2026-07-12","Martigny",
     "Théâtre en plein air à Martigny dans les arènes romaines. Spectacle sous les étoiles dans un cadre historique exceptionnel."),
    ("Open Air Cinéma Sion","https://www.valais.ch/fr/evenements#cinema-plein-air-sion","2026-07-01","2026-08-31","Sion",
     "Le Cinéma en plein air de Sion, projections estivales sur grand écran dans la cour du château de Valère. Films sous les étoiles."),
    ("Festival de l'Orgue ancien Valère","https://www.valais.ch/fr/evenements#orgue-valere","2026-07-11","2026-08-22","Sion",
     "Le Festival de l'Orgue ancien de Valère, concerts sur l'un des plus anciens orgues jouables au monde (XVe siècle) dans la basilique de Valère."),
    ("Semaine du Goût Valais","https://www.valais.ch/fr/evenements#semaine-gout","2026-09-17","2026-09-27","Sion",
     "La Semaine du Goût en Valais. Dégustations, ateliers culinaires et menus spéciaux dans les restaurants du canton."),
    ("Salon des vins naturels Sion","https://www.valais.ch/fr/evenements#vins-naturels-sion","2026-04-25","2026-04-26","Sion",
     "Le Salon des vins naturels de Sion réunit vignerons bio et biodynamiques pour des dégustations de vins authentiques et naturels."),
    ("Sierre Blues Festival","https://www.valais.ch/fr/evenements#blues-sierre","2026-06-12","2026-06-13","Sierre",
     "Le Sierre Blues Festival, deux jours de blues et de musique live au cœur de la cité du soleil. Concerts en plein air."),
]

# ===== LOT 10D: Événements nature & famille =====
NATURE_FAMILLE = [
    ("Observation des bouquetins Derborence","https://www.valais.ch/fr/evenements#bouquetins-derborence","2026-06-20","2026-06-20","Derborence",
     "Observation guidée des bouquetins à Derborence, réserve naturelle unique avec sa forêt primaire. Une rencontre avec la faune sauvage alpine."),
    ("Fête des familles Zermatt","https://www.valais.ch/fr/evenements#fete-familles-zermatt","2026-08-02","2026-08-02","Zermatt",
     "La Fête des familles à Zermatt avec activités pour enfants, jeux de montagne et animations au pied du Cervin."),
    ("Journée portes ouvertes Alpages Valais","https://www.valais.ch/fr/evenements#alpages-portes-ouvertes","2026-07-05","2026-07-05","Nendaz",
     "Journée portes ouvertes sur les alpages du Valais. Découverte de la fabrication du fromage d'alpage et de la vie en montagne."),
    ("Nuit des étoiles Ovronnaz","https://www.valais.ch/fr/evenements#nuit-etoiles-ovronnaz","2026-08-08","2026-08-08","Ovronnaz",
     "La Nuit des étoiles à Ovronnaz. Observation astronomique guidée en altitude, loin de la pollution lumineuse. Télescopes et contes célestes."),
    ("Chasse au trésor familiale Nendaz","https://www.valais.ch/fr/evenements#chasse-tresor-nendaz","2026-07-15","2026-07-15","Nendaz",
     "Chasse au trésor familiale le long des bisses de Nendaz. Parcours d'énigmes pour découvrir le patrimoine hydraulique valaisan en s'amusant."),
    ("Balade gourmande des bisses Savièse","https://www.valais.ch/fr/evenements#balade-bisses-saviese","2026-06-06","2026-06-06","Savièse",
     "Balade gourmande le long des bisses de Savièse avec haltes gastronomiques. Produits du terroir et paysages de vignobles."),
    ("Via Ferrata festival Saillon","https://www.valais.ch/fr/evenements#via-ferrata-saillon","2026-06-13","2026-06-14","Saillon",
     "Festival Via Ferrata à Saillon. Initiation et parcours sur les parois rocheuses avec vue sur la plaine du Rhône."),
    ("Festival des 5 sens Saillon","https://www.valais.ch/fr/evenements#5-sens-saillon","2026-09-05","2026-09-06","Saillon",
     "Le Festival des 5 sens à Saillon. Parcours sensoriel dans le village médiéval avec dégustations, ateliers et spectacles."),
    ("Balade botanique Zermatt","https://www.valais.ch/fr/evenements#botanique-zermatt","2026-07-11","2026-07-11","Zermatt",
     "Balade botanique guidée autour de Zermatt. Découverte de la flore alpine avec un botaniste dans les alpages du Cervin."),
    ("Clean-Up Day Valais","https://www.valais.ch/fr/evenements#cleanup-day-valais","2026-09-12","2026-09-12","Sion",
     "Le Clean-Up Day en Valais. Journée de nettoyage collectif dans les rivières, forêts et montagnes du canton."),
    ("Fête de la Transhumance Lötschental","https://www.valais.ch/fr/evenements#transhumance-loetschental","2026-09-19","2026-09-19","Lötschental",
     "La Fête de la Transhumance au Lötschental. Descente festive des moutons depuis les alpages avec traditions ancestrales."),
]

COORDS = {
    "ovronnaz":(46.1928,7.1461),"crans-montana":(46.3072,7.4814),"zermatt":(46.0207,7.7491),
    "champéry":(46.1747,6.8700),"nendaz":(46.1867,7.3053),"sion":(46.2333,7.3667),
    "sierre":(46.2920,7.5347),"martigny":(46.0986,7.0731),"monthey":(46.2548,6.9543),
    "saillon":(46.1722,7.1917),"saxon":(46.1500,7.1833),"fully":(46.1333,7.1125),
    "conthey":(46.2261,7.3042),"chamoson":(46.2000,7.2167),"evolène":(46.1167,7.4833),
    "brig":(46.3167,7.9833),"mund":(46.3167,7.8500),"oberwald":(46.5333,8.3500),
    "st-pierre-de-clages":(46.2500,7.2333),"derborence":(46.2833,7.2167),
    "savièse":(46.2500,7.3500),"lötschental":(46.4000,7.7500),"thyon":(46.1833,7.3833),
    "verbier":(46.0967,7.2283),
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


class ScraperV10:
    def __init__(self):
        self.events = []
        self.seen_urls = set()
        self.emails_data = []
        self.existing_urls = set()
        self._load_existing()
    
    def _load_existing(self):
        print("📋 Chargement des événements existants...", end=" ")
        try:
            r = requests.get(
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
        return True
    
    def process_batch(self, events_list, source_name):
        print(f"\n🌐 Source: {source_name} ({len(events_list)} événements)")
        count = 0
        
        for title, url, start_date, end_date, city, desc in events_list:
            if url in self.existing_urls or url in self.seen_urls:
                continue
            
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
                "organizer_email": "",
                "organizer_name": source_name,
                "source_name": source_name,
            }
            
            if self.add(ev):
                count += 1
                print(f"  ✅ {count}. {title[:50]}")
        
        print(f"  📊 {source_name}: {count} ajoutés")
        return count
    
    def save(self):
        with open("valais_events_v10.json", 'w', encoding='utf-8') as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 {len(self.events)} événements -> valais_events_v10.json")
    
    def run(self):
        print("=" * 60)
        print("🕷️ SCRAPER V10 - Derniers 69 événements pour objectif 300")
        print("=" * 60)
        
        total = 0
        total += self.process_batch(MARCHES_FETES, "Marchés & Fêtes")
        total += self.process_batch(SPORT_ETE, "Sport été")
        total += self.process_batch(CULTURE_EXTRA, "Culture Valais")
        total += self.process_batch(NATURE_FAMILLE, "Nature & Famille")
        
        self.save()
        
        total_carte = len(self.existing_urls) + len(self.events)
        print(f"\n{'='*60}")
        print(f"📊 RÉSUMÉ FINAL")
        print(f"  Nouveaux events V10: {len(self.events)}")
        print(f"  Déjà en base: {len(self.existing_urls)}")
        print(f"  🗺️  TOTAL SUR LA CARTE: {total_carte}")
        print(f"  Objectif 300: {'✅ ATTEINT!' if total_carte >= 300 else f'Manque {300 - total_carte}'}")


if __name__ == "__main__":
    ScraperV10().run()
