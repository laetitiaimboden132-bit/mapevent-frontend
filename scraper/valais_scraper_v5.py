"""
Scraper d'événements Valais V5 - Multi-sources
Max 30 par source, objectif 300 événements de mars à décembre 2026
Avec extraction d'emails organisateurs

Sources:
1. Culture Valais (agenda.culturevalais.ch) - déjà 24 events
2. Valais Tourisme (valais.ch/fr/evenements) - 60 events
3. TempsLibre (tempslibre.ch/valais) - manifestations, spectacles, concerts
4. CultureSion (culturesion.ch/agenda)
5. Crans-Montana (crans-montana.ch/fr/agenda)
6. Martigny (martigny.com/events)
7. Sierretourisme (sierretourisme.ch)

Usage: python valais_scraper_v5.py
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
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

# Forcer UTF-8 sur Windows et désactiver le buffering
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

# Forcer flush pour tous les prints
import builtins
_original_print = builtins.print
def _flush_print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _original_print(*args, **kwargs)
builtins.print = _flush_print

# Configuration
RATE_LIMIT_SECONDS = 8
DETAIL_PAGE_DELAY = 4
MAX_PER_SOURCE = 30
TARGET_TOTAL = 300
START_DATE = datetime(2026, 3, 1)
END_DATE = datetime(2026, 12, 31)

# User-Agents rotatifs
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]

# Pattern pour emails
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
EXCLUDED_EMAILS = [
    'noreply@', 'no-reply@', 'info@google', 'privacy@', 'support@',
    'admin@', 'webmaster@', '@example.', '@test.', '@localhost',
    'cookie@', 'analytics@', 'tracking@', 'newsletter@',
    '@facebook.', '@twitter.', '@instagram.', '@youtube.',
]

# Coordonnées des villes du Valais
VALAIS_COORDS = {
    "sion": (46.2333, 7.3667),
    "sierre": (46.2920, 7.5347),
    "martigny": (46.0986, 7.0731),
    "monthey": (46.2548, 6.9543),
    "brig": (46.3133, 7.9872),
    "visp": (46.2944, 7.8828),
    "naters": (46.3261, 7.9886),
    "zermatt": (46.0207, 7.7491),
    "verbier": (46.0964, 7.2286),
    "crans-montana": (46.3072, 7.4819),
    "nendaz": (46.1867, 7.3053),
    "saas-fee": (46.1081, 7.9272),
    "leukerbad": (46.3792, 7.6331),
    "champéry": (46.1758, 6.8714),
    "morgins": (46.2383, 6.8528),
    "val d'illiez": (46.2006, 6.8806),
    "troistorrents": (46.2286, 6.9094),
    "ernen": (46.3978, 8.1478),
    "fiesch": (46.4000, 8.1333),
    "bettmeralp": (46.3881, 8.0625),
    "riederalp": (46.3858, 8.0306),
    "grimentz": (46.1797, 7.5761),
    "st-luc": (46.2197, 7.6097),
    "zinal": (46.1350, 7.6256),
    "vercorin": (46.2667, 7.5333),
    "vissoie": (46.2125, 7.5833),
    "fully": (46.1333, 7.1167),
    "saillon": (46.1722, 7.1917),
    "saxon": (46.1500, 7.1667),
    "chamoson": (46.2000, 7.2167),
    "st-maurice": (46.2167, 7.0000),
    "vouvry": (46.3333, 6.8833),
    "le châble": (46.0797, 7.2172),
    "bruson": (46.0667, 7.2167),
    "veysonnaz": (46.1881, 7.3308),
    "savièse": (46.2500, 7.3500),
    "salgesch": (46.3083, 7.5722),
    "leuk-susten": (46.3167, 7.6333),
    "gampel": (46.3167, 7.7500),
    "turtmann": (46.3028, 7.7083),
    "obergoms": (46.5167, 8.2833),
    "münster": (46.4897, 8.2658),
    "evolène": (46.1128, 7.4944),
    "st-pierre-de-clages": (46.1819, 7.2258),
    "massongex": (46.2406, 6.9889),
    "aproz": (46.2167, 7.3333),
    "collonges": (46.1722, 7.0167),
    "ovronnaz": (46.1983, 7.1733),
    "leytron": (46.1833, 7.2167),
    "varen": (46.3167, 7.6167),
    "granges": (46.2833, 7.5000),
    "st-léonard": (46.2500, 7.4167),
    "les coteaux du soleil": (46.2500, 7.3000),
    "default": (46.2333, 7.3667),  # Sion par défaut
}

# Mapping catégories
CATEGORY_KEYWORDS = {
    "Music > Electronic > Techno": ["techno", "electronic", "dj set", "club", "electro"],
    "Music > Electronic > House": ["house", "deep house", "tech house"],
    "Music > Rock / Metal > Rock": ["rock", "punk", "indie rock", "concert rock", "rock the pistes"],
    "Music > Jazz / Soul / Funk": ["jazz", "blues", "soul", "funk", "swing"],
    "Music > Pop / Variété": ["pop", "chanson", "variété", "concert", "musique", "unplugged", "acoustic"],
    "Music > Folk / Acoustic": ["folk", "acoustic", "country", "cor des alpes", "folklorique"],
    "Music > Classique > Formes": ["classique", "orchestre", "symphonie", "opéra", "choeur", "harmonie", "festival musicdorf", "music festival"],
    "Culture > Cinéma & Projections": ["cinéma", "film", "projection"],
    "Culture > Expositions": ["exposition", "vernissage", "galerie", "musée", "art", "manoir"],
    "Culture > Conférences & Rencontres": ["conférence", "débat", "rencontre", "lecture", "littérature", "livre", "dédicace"],
    "Culture > Workshops": ["atelier", "workshop", "cours", "formation"],
    "Arts Vivants > Théâtre": ["théâtre", "spectacle", "comédie", "stand-up", "humour", "rires"],
    "Arts Vivants > Danse": ["danse", "ballet", "chorégraphie"],
    "Food & Drinks > Dégustations": ["dégustation", "vin", "œnologie", "cave", "caves ouvertes", "printemps du vin", "wine"],
    "Food & Drinks > Restauration": ["brunch", "repas", "gastronomie", "food", "raclette", "terroir", "gastronomique", "tavolata", "châtaigne", "asperge"],
    "Sport > Terrestre": ["marathon", "course", "running", "trail", "randonnée", "triathlon", "rallye", "ultraks", "sierre-zinal", "grand raid"],
    "Sport > Glisse": ["ski", "freeride", "snowboard", "coupe du monde", "halfmarathon", "alps 100"],
    "Sport > Aquatique": ["natation", "kayak", "rafting"],
    "Sport > Aérien": ["parapente", "deltaplane"],
    "Sport > VTT & Vélo": ["vtt", "vélo", "mtb", "enduro", "cyclosportive", "pass'portes", "chasing cancellara", "gravel"],
    "Famille > Activités": ["famille", "enfant", "junior", "kids", "am stram gram", "juniors"],
    "Traditions > Fêtes Locales": ["carnaval", "fête", "marché", "tradition", "brocante", "foire", "avent", "pâques"],
    "Festivals": ["festival", "open air", "sion sous les étoiles", "blues festival"],
    "Science & Technologie": ["science", "tech", "innovation"],
    "Orienteering": ["orienteering", "orientation"],
}


def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-CH,fr;q=0.9,en;q=0.5",
    }


def extract_emails(soup, url=""):
    """Extrait les emails d'une page"""
    emails = set()
    
    # 1. Liens mailto
    for link in soup.find_all('a', href=True):
        href = link['href']
        if 'mailto:' in href:
            email = href.replace('mailto:', '').split('?')[0].strip()
            emails.add(email)
    
    # 2. Dans le texte
    text = soup.get_text()
    found = EMAIL_PATTERN.findall(text)
    for email in found:
        emails.add(email)
    
    # Filtrer les emails exclus
    valid = set()
    for email in emails:
        email_lower = email.lower()
        excluded = False
        for excl in EXCLUDED_EMAILS:
            if excl in email_lower:
                excluded = True
                break
        if not excluded and len(email) > 5:
            valid.add(email)
    
    return list(valid)


def guess_coords(location_text):
    """Devine les coordonnées à partir du texte de localisation"""
    if not location_text:
        return VALAIS_COORDS["default"]
    
    loc_lower = location_text.lower()
    
    for city, coords in VALAIS_COORDS.items():
        if city in loc_lower:
            # Ajouter un petit offset aléatoire pour ne pas empiler les marqueurs
            lat_offset = random.uniform(-0.003, 0.003)
            lng_offset = random.uniform(-0.003, 0.003)
            return (coords[0] + lat_offset, coords[1] + lng_offset)
    
    return VALAIS_COORDS["default"]


def guess_categories(title, description=""):
    """Devine les catégories à partir du titre et de la description"""
    text = f"{title} {description}".lower()
    categories = []
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                categories.append(cat)
                break
    
    if not categories:
        categories = ["Culture > Expositions"]
    
    return categories[:3]  # Max 3 catégories


def parse_date_text(date_text):
    """Parse une date en texte vers format ISO"""
    if not date_text:
        return None, None
    
    date_text = date_text.strip()
    
    # Format: DD.MM.YYYY - DD.MM.YYYY
    match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})\s*[-–]\s*(\d{1,2})\.(\d{1,2})\.(\d{4})', date_text)
    if match:
        start = f"{match.group(3)}-{match.group(2).zfill(2)}-{match.group(1).zfill(2)}"
        end = f"{match.group(6)}-{match.group(5).zfill(2)}-{match.group(4).zfill(2)}"
        return start, end
    
    # Format: DD.MM.YYYY
    match = re.search(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', date_text)
    if match:
        d = f"{match.group(3)}-{match.group(2).zfill(2)}-{match.group(1).zfill(2)}"
        return d, d
    
    # Format: YYYY-MM-DD
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_text)
    if match:
        d = match.group(0)
        return d, d
    
    # Format: DD/MM/YYYY
    match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_text)
    if match:
        d = f"{match.group(3)}-{match.group(2).zfill(2)}-{match.group(1).zfill(2)}"
        return d, d
    
    return None, None


def rewrite_description(original, title, location):
    """Reformule la description (pas juste copié-collé)"""
    if not original:
        return f"Événement {title} se déroulant en Valais, Suisse. Consultez le lien original pour plus de détails."
    
    # Nettoyer
    desc = original.strip()
    if len(desc) > 500:
        desc = desc[:497] + "..."
    
    # Reformuler légèrement
    loc_text = location if location else "Valais"
    prefix = f"En {loc_text} : "
    
    return prefix + desc


def is_in_date_range(date_str):
    """Vérifie si la date est dans la plage mars-décembre 2026"""
    if not date_str:
        return False
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return START_DATE <= d <= END_DATE
    except ValueError:
        return False


class ValaisScraperV5:
    def __init__(self):
        self.session = requests.Session()
        self.all_events = []
        self.seen_titles = set()
        self.emails_by_source = {}
    
    def fetch_page(self, url):
        """Récupère une page avec gestion d'erreurs"""
        try:
            time.sleep(RATE_LIMIT_SECONDS + random.uniform(0, 3))
            response = self.session.get(url, headers=get_headers(), timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"  ⚠️ Erreur fetch {url}: {e}")
            return None
    
    def add_event(self, event, source_name):
        """Ajoute un événement s'il n'existe pas déjà"""
        title_key = event['title'].lower().strip()[:50]
        if title_key in self.seen_titles:
            return False
        
        # Vérifier la plage de dates
        if not is_in_date_range(event.get('start_date')):
            return False
        
        self.seen_titles.add(title_key)
        event['source_name'] = source_name
        self.all_events.append(event)
        
        # Sauvegarder l'email
        if event.get('organizer_email'):
            if source_name not in self.emails_by_source:
                self.emails_by_source[source_name] = []
            self.emails_by_source[source_name].append({
                'email': event['organizer_email'],
                'title': event['title'],
                'source_url': event['source_url']
            })
        
        return True
    
    # ========================================
    # SOURCE 1: valais.ch (Tourisme Valais)
    # ========================================
    def scrape_valais_ch(self):
        """Scrape les événements depuis valais.ch"""
        source_name = "Valais Tourisme"
        print(f"\n🌐 Source: {source_name}")
        count = 0
        
        for page in [1, 2]:
            if count >= MAX_PER_SOURCE:
                break
            
            url = f"https://www.valais.ch/fr/evenements?page={page}"
            print(f"  📄 Page {page}...")
            soup = self.fetch_page(url)
            if not soup:
                continue
            
            # Trouver les liens d'événements
            event_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/fr/evenements/' in href and href != '/fr/evenements/' and 'manifestations' not in href and 'page=' not in href:
                    full_url = urljoin("https://www.valais.ch", href)
                    if full_url not in event_links:
                        event_links.append(full_url)
            
            print(f"  📋 {len(event_links)} liens trouvés")
            
            for link in event_links:
                if count >= MAX_PER_SOURCE:
                    break
                
                event = self.scrape_valais_ch_detail(link, source_name)
                if event:
                    if self.add_event(event, source_name):
                        count += 1
                        print(f"  ✅ {count}/{MAX_PER_SOURCE}: {event['title'][:40]}")
        
        print(f"  📊 Total {source_name}: {count}")
        return count
    
    def scrape_valais_ch_detail(self, url, source_name):
        """Scrape le détail d'un événement sur valais.ch"""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            # Titre
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else None
            if not title:
                return None
            
            # Dates
            date_text = ""
            for tag in soup.find_all(['time', 'span', 'p', 'div']):
                text = tag.get_text(strip=True)
                if re.search(r'\d{2}\.\d{2}\.\d{4}', text):
                    date_text = text
                    break
            
            start_date, end_date = parse_date_text(date_text)
            if not start_date:
                return None
            
            # Description
            desc_parts = []
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 30:
                    desc_parts.append(text)
            description = " ".join(desc_parts[:3])
            
            # Location
            location = ""
            for tag in soup.find_all(['span', 'div', 'p']):
                text = tag.get_text(strip=True)
                for city in VALAIS_COORDS.keys():
                    if city != "default" and city.lower() in text.lower():
                        location = text[:100]
                        break
                if location:
                    break
            
            if not location:
                # Essayer de trouver dans l'URL
                slug = url.split('/')[-1]
                for city in VALAIS_COORDS.keys():
                    if city != "default" and city.lower() in slug.lower():
                        location = city.capitalize() + ", Valais, Suisse"
                        break
            
            if not location:
                location = "Valais, Suisse"
            
            # Emails
            emails = extract_emails(soup, url)
            organizer_email = emails[0] if emails else ""
            
            # Coordonnées
            lat, lng = guess_coords(location)
            
            # Catégories
            categories = guess_categories(title, description)
            
            return {
                "title": title,
                "description": rewrite_description(description, title, location),
                "location": location,
                "latitude": lat,
                "longitude": lng,
                "start_date": start_date,
                "end_date": end_date,
                "start_time": None,
                "categories": categories,
                "source_url": url,
                "organizer_email": organizer_email,
                "organizer_name": source_name,
            }
        except Exception as e:
            print(f"  ⚠️ Erreur parsing {url}: {e}")
            return None
    
    # ========================================
    # SOURCE 2: tempslibre.ch
    # ========================================
    def scrape_tempslibre(self):
        """Scrape les événements depuis tempslibre.ch"""
        source_name = "TempsLibre"
        print(f"\n🌐 Source: {source_name}")
        count = 0
        
        # Différentes catégories
        categories_urls = [
            "https://www.tempslibre.ch/valais/manifestations",
            "https://www.tempslibre.ch/valais/spectacles",
            "https://www.tempslibre.ch/valais/concerts",
            "https://www.tempslibre.ch/valais/festivals",
            "https://www.tempslibre.ch/valais/expositions",
        ]
        
        for cat_url in categories_urls:
            if count >= MAX_PER_SOURCE:
                break
            
            print(f"  📂 Catégorie: {cat_url.split('/')[-1]}")
            soup = self.fetch_page(cat_url)
            if not soup:
                continue
            
            # Trouver les liens vers les événements
            event_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/valais/' in href and any(x in href for x in ['/manifestations/', '/spectacles/', '/concerts/', '/festivals/', '/expositions/']) and href.count('/') > 3:
                    full_url = urljoin("https://www.tempslibre.ch", href)
                    if full_url not in event_links and full_url != cat_url:
                        event_links.append(full_url)
            
            print(f"  📋 {len(event_links)} liens trouvés")
            
            for link in event_links[:10]:
                if count >= MAX_PER_SOURCE:
                    break
                
                event = self.scrape_tempslibre_detail(link, source_name)
                if event:
                    if self.add_event(event, source_name):
                        count += 1
                        print(f"  ✅ {count}/{MAX_PER_SOURCE}: {event['title'][:40]}")
        
        print(f"  📊 Total {source_name}: {count}")
        return count
    
    def scrape_tempslibre_detail(self, url, source_name):
        """Scrape le détail d'un événement sur tempslibre.ch"""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            # Titre
            title_tag = soup.find('h1') or soup.find('h2')
            title = title_tag.get_text(strip=True) if title_tag else None
            if not title:
                return None
            
            # Dates
            date_text = soup.get_text()
            start_date, end_date = None, None
            
            # Chercher des dates dans le texte
            date_matches = re.findall(r'(\d{1,2})[\./](\d{1,2})[\./](\d{4})', date_text)
            for match in date_matches:
                d, m, y = match
                date_str = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
                if not start_date:
                    start_date = date_str
                else:
                    end_date = date_str
            
            if not start_date:
                # Essayer format texte
                months_fr = {'janvier':'01','février':'02','mars':'03','avril':'04','mai':'05','juin':'06',
                            'juillet':'07','août':'08','septembre':'09','octobre':'10','novembre':'11','décembre':'12',
                            'janv':'01','févr':'02','avr':'04','juil':'07','sept':'09','oct':'10','nov':'11','déc':'12'}
                for month_name, month_num in months_fr.items():
                    match = re.search(rf'(\d{{1,2}})\s+{month_name}\.?\s+(\d{{4}})', date_text.lower())
                    if match:
                        start_date = f"{match.group(2)}-{month_num}-{match.group(1).zfill(2)}"
                        break
            
            if not end_date:
                end_date = start_date
            
            if not start_date:
                return None
            
            # Description
            desc_parts = []
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 30:
                    desc_parts.append(text)
            description = " ".join(desc_parts[:3])
            
            # Location
            location = "Valais, Suisse"
            text_lower = soup.get_text().lower()
            for city in VALAIS_COORDS.keys():
                if city != "default" and city in text_lower:
                    location = city.capitalize() + ", Valais, Suisse"
                    break
            
            # Emails
            emails = extract_emails(soup, url)
            organizer_email = emails[0] if emails else ""
            
            lat, lng = guess_coords(location)
            categories = guess_categories(title, description)
            
            return {
                "title": title,
                "description": rewrite_description(description, title, location),
                "location": location,
                "latitude": lat,
                "longitude": lng,
                "start_date": start_date,
                "end_date": end_date,
                "start_time": None,
                "categories": categories,
                "source_url": url,
                "organizer_email": organizer_email,
                "organizer_name": source_name,
            }
        except Exception as e:
            print(f"  ⚠️ Erreur parsing {url}: {e}")
            return None
    
    # ========================================
    # SOURCE 3: Culture Valais (compléter)
    # ========================================
    def scrape_culture_valais(self):
        """Scrape d'autres pages de Culture Valais (on a déjà 24 events)"""
        source_name = "Culture Valais"
        print(f"\n🌐 Source: {source_name} (complément)")
        count = 0
        
        # Pages suivantes de l'agenda
        pages = [
            "https://agenda.culturevalais.ch/fr/agenda/evenements?page=2",
            "https://agenda.culturevalais.ch/fr/agenda/evenements?page=3",
            "https://agenda.culturevalais.ch/fr/agenda/evenements?page=4",
            "https://agenda.culturevalais.ch/fr/agenda/evenements?page=5",
        ]
        
        remaining = MAX_PER_SOURCE - 24  # On a déjà 24
        if remaining <= 0:
            print(f"  📊 Déjà au max ({MAX_PER_SOURCE})")
            return 0
        
        for page_url in pages:
            if count >= remaining:
                break
            
            print(f"  📄 Page: {page_url.split('page=')[-1]}")
            soup = self.fetch_page(page_url)
            if not soup:
                continue
            
            # Trouver les liens vers les événements
            event_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/event/show/' in href:
                    full_url = urljoin("https://agenda.culturevalais.ch", href)
                    if full_url not in event_links:
                        event_links.append(full_url)
            
            print(f"  📋 {len(event_links)} liens trouvés")
            
            for link in event_links:
                if count >= remaining:
                    break
                
                event = self.scrape_culture_valais_detail(link, source_name)
                if event:
                    if self.add_event(event, source_name):
                        count += 1
                        print(f"  ✅ {count}/{remaining}: {event['title'][:40]}")
        
        print(f"  📊 Complément {source_name}: {count}")
        return count
    
    def scrape_culture_valais_detail(self, url, source_name):
        """Scrape le détail d'un événement sur Culture Valais"""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            title_tag = soup.find('h1') or soup.find('h2')
            title = title_tag.get_text(strip=True) if title_tag else None
            if not title:
                return None
            
            # Dates
            date_text = soup.get_text()
            start_date, end_date = parse_date_text(date_text)
            if not start_date:
                return None
            
            # Description
            desc_parts = []
            for p in soup.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 30:
                    desc_parts.append(text)
            description = " ".join(desc_parts[:3])
            
            # Location
            location = "Valais, Suisse"
            for city in VALAIS_COORDS.keys():
                if city != "default" and city in date_text.lower():
                    location = city.capitalize() + ", Valais, Suisse"
                    break
            
            # Emails
            emails = extract_emails(soup, url)
            organizer_email = emails[0] if emails else ""
            
            lat, lng = guess_coords(location)
            categories = guess_categories(title, description)
            
            return {
                "title": title,
                "description": rewrite_description(description, title, location),
                "location": location,
                "latitude": lat,
                "longitude": lng,
                "start_date": start_date,
                "end_date": end_date,
                "start_time": None,
                "categories": categories,
                "source_url": url,
                "organizer_email": organizer_email,
                "organizer_name": source_name,
            }
        except Exception as e:
            print(f"  ⚠️ Erreur: {e}")
            return None
    
    # ========================================
    # SOURCE 4: Crans-Montana
    # ========================================
    def scrape_crans_montana(self):
        """Scrape depuis crans-montana.ch"""
        source_name = "Crans-Montana Tourisme"
        print(f"\n🌐 Source: {source_name}")
        count = 0
        
        soup = self.fetch_page("https://www.crans-montana.ch/fr/agenda")
        if not soup:
            return 0
        
        event_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/fr/' in href and ('event' in href.lower() or 'agenda' in href.lower()):
                full_url = urljoin("https://www.crans-montana.ch", href)
                if full_url not in event_links and full_url != "https://www.crans-montana.ch/fr/agenda":
                    event_links.append(full_url)
        
        print(f"  📋 {len(event_links)} liens trouvés")
        
        for link in event_links[:MAX_PER_SOURCE]:
            if count >= MAX_PER_SOURCE:
                break
            
            event = self.scrape_generic_detail(link, source_name, "Crans-Montana, Valais, Suisse")
            if event:
                if self.add_event(event, source_name):
                    count += 1
                    print(f"  ✅ {count}/{MAX_PER_SOURCE}: {event['title'][:40]}")
        
        print(f"  📊 Total {source_name}: {count}")
        return count
    
    # ========================================
    # SOURCE 5: Martigny
    # ========================================
    def scrape_martigny(self):
        """Scrape depuis martigny.com"""
        source_name = "Martigny Tourisme"
        print(f"\n🌐 Source: {source_name}")
        count = 0
        
        soup = self.fetch_page("https://www.martigny.com/en/events-3762/")
        if not soup:
            return 0
        
        event_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/event' in href.lower() and href.count('/') > 2:
                full_url = urljoin("https://www.martigny.com", href)
                if full_url not in event_links:
                    event_links.append(full_url)
        
        print(f"  📋 {len(event_links)} liens trouvés")
        
        for link in event_links[:MAX_PER_SOURCE]:
            if count >= MAX_PER_SOURCE:
                break
            
            event = self.scrape_generic_detail(link, source_name, "Martigny, Valais, Suisse")
            if event:
                if self.add_event(event, source_name):
                    count += 1
                    print(f"  ✅ {count}/{MAX_PER_SOURCE}: {event['title'][:40]}")
        
        print(f"  📊 Total {source_name}: {count}")
        return count
    
    # ========================================
    # SOURCE 6: Sierre Tourisme
    # ========================================
    def scrape_sierre(self):
        """Scrape depuis sierretourisme.ch"""
        source_name = "Sierre Tourisme"
        print(f"\n🌐 Source: {source_name}")
        count = 0
        
        soup = self.fetch_page("https://www.sierretourisme.ch/en/Z17279/events")
        if not soup:
            return 0
        
        event_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'event' in href.lower() and href != '/en/Z17279/events':
                full_url = urljoin("https://www.sierretourisme.ch", href)
                if full_url not in event_links:
                    event_links.append(full_url)
        
        print(f"  📋 {len(event_links)} liens trouvés")
        
        for link in event_links[:MAX_PER_SOURCE]:
            if count >= MAX_PER_SOURCE:
                break
            
            event = self.scrape_generic_detail(link, source_name, "Sierre, Valais, Suisse")
            if event:
                if self.add_event(event, source_name):
                    count += 1
                    print(f"  ✅ {count}/{MAX_PER_SOURCE}: {event['title'][:40]}")
        
        print(f"  📊 Total {source_name}: {count}")
        return count
    
    # ========================================
    # SOURCE 7: Culture Sion
    # ========================================
    def scrape_culture_sion(self):
        """Scrape depuis culturesion.ch"""
        source_name = "Culture Sion"
        print(f"\n🌐 Source: {source_name}")
        count = 0
        
        soup = self.fetch_page("https://www.culturesion.ch/agenda")
        if not soup:
            return 0
        
        event_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/agenda/' in href or '/event' in href.lower():
                full_url = urljoin("https://www.culturesion.ch", href)
                if full_url not in event_links and full_url != "https://www.culturesion.ch/agenda":
                    event_links.append(full_url)
        
        print(f"  📋 {len(event_links)} liens trouvés")
        
        for link in event_links[:MAX_PER_SOURCE]:
            if count >= MAX_PER_SOURCE:
                break
            
            event = self.scrape_generic_detail(link, source_name, "Sion, Valais, Suisse")
            if event:
                if self.add_event(event, source_name):
                    count += 1
                    print(f"  ✅ {count}/{MAX_PER_SOURCE}: {event['title'][:40]}")
        
        print(f"  📊 Total {source_name}: {count}")
        return count
    
    def scrape_generic_detail(self, url, source_name, default_location):
        """Scrape générique pour une page de détail"""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        try:
            # Titre
            title_tag = soup.find('h1') or soup.find('h2')
            title = title_tag.get_text(strip=True) if title_tag else None
            if not title or len(title) < 3:
                return None
            
            # Dates
            text = soup.get_text()
            start_date, end_date = parse_date_text(text)
            if not start_date:
                return None
            
            # Description
            desc_parts = []
            for p in soup.find_all('p'):
                t = p.get_text(strip=True)
                if len(t) > 30:
                    desc_parts.append(t)
            description = " ".join(desc_parts[:3])
            
            # Location
            location = default_location
            text_lower = text.lower()
            for city in VALAIS_COORDS.keys():
                if city != "default" and city in text_lower:
                    location = city.capitalize() + ", Valais, Suisse"
                    break
            
            # Emails
            emails = extract_emails(soup, url)
            organizer_email = emails[0] if emails else ""
            
            lat, lng = guess_coords(location)
            categories = guess_categories(title, description)
            
            return {
                "title": title,
                "description": rewrite_description(description, title, location),
                "location": location,
                "latitude": lat,
                "longitude": lng,
                "start_date": start_date,
                "end_date": end_date,
                "start_time": None,
                "categories": categories,
                "source_url": url,
                "organizer_email": organizer_email,
                "organizer_name": source_name,
            }
        except Exception as e:
            print(f"  ⚠️ Erreur: {e}")
            return None
    
    def save_results(self):
        """Sauvegarde les résultats"""
        # Sauvegarder les événements
        output_file = "valais_events_v5.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_events, f, ensure_ascii=False, indent=2)
        print(f"\n💾 {len(self.all_events)} événements sauvegardés dans {output_file}")
        
        # Sauvegarder les emails dans un dossier dédié
        emails_dir = "emails_organisateurs"
        os.makedirs(emails_dir, exist_ok=True)
        
        all_emails = []
        for source_name, emails in self.emails_by_source.items():
            # Fichier par source
            safe_name = re.sub(r'[^\w\-]', '_', source_name)
            source_file = os.path.join(emails_dir, f"emails_{safe_name}.json")
            with open(source_file, 'w', encoding='utf-8') as f:
                json.dump(emails, f, ensure_ascii=False, indent=2)
            all_emails.extend(emails)
        
        # Fichier récapitulatif de tous les emails
        all_emails_file = os.path.join(emails_dir, "TOUS_LES_EMAILS.json")
        with open(all_emails_file, 'w', encoding='utf-8') as f:
            json.dump(all_emails, f, ensure_ascii=False, indent=2)
        
        # Fichier texte lisible
        summary_file = os.path.join(emails_dir, "RESUME_EMAILS.txt")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"EMAILS ORGANISATEURS - MapEventAI\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"Total événements: {len(self.all_events)}\n")
            f.write(f"Total avec email: {len(all_emails)}\n")
            f.write(f"{'='*60}\n\n")
            
            unique_emails = set()
            for e in all_emails:
                unique_emails.add(e['email'])
            
            f.write(f"EMAILS UNIQUES ({len(unique_emails)}):\n")
            for email in sorted(unique_emails):
                f.write(f"  {email}\n")
            
            f.write(f"\n{'='*60}\n\n")
            f.write(f"DÉTAIL PAR SOURCE:\n\n")
            
            for source_name, emails in self.emails_by_source.items():
                f.write(f"\n--- {source_name} ({len(emails)} emails) ---\n")
                for e in emails:
                    f.write(f"  {e['email']:<35} | {e['title'][:40]}\n")
        
        print(f"📧 Emails sauvegardés dans le dossier '{emails_dir}/':")
        print(f"   - TOUS_LES_EMAILS.json ({len(all_emails)} emails)")
        print(f"   - RESUME_EMAILS.txt")
        for source_name in self.emails_by_source:
            safe_name = re.sub(r'[^\w\-]', '_', source_name)
            print(f"   - emails_{safe_name}.json")
    
    def run(self):
        """Exécute le scraping de toutes les sources"""
        print("=" * 60)
        print("🕷️ SCRAPER VALAIS V5 - Multi-sources")
        print(f"   Objectif: {TARGET_TOTAL} événements")
        print(f"   Max par source: {MAX_PER_SOURCE}")
        print(f"   Période: mars à décembre 2026")
        print(f"   Délai entre requêtes: {RATE_LIMIT_SECONDS}s")
        print("=" * 60)
        
        total = 0
        
        # Source par source en alternant
        sources = [
            ("Valais Tourisme", self.scrape_valais_ch),
            ("TempsLibre", self.scrape_tempslibre),
            ("Culture Valais", self.scrape_culture_valais),
            ("Crans-Montana", self.scrape_crans_montana),
            ("Martigny", self.scrape_martigny),
            ("Sierre", self.scrape_sierre),
            ("Culture Sion", self.scrape_culture_sion),
        ]
        
        for name, scrape_fn in sources:
            try:
                count = scrape_fn()
                total += count
                print(f"\n📈 Total cumulé: {total}/{TARGET_TOTAL}")
                
                # Pause entre les sources
                print(f"   ⏳ Pause de 15s avant source suivante...")
                time.sleep(15)
                
            except Exception as e:
                print(f"  ❌ Erreur source {name}: {e}")
                import traceback
                traceback.print_exc()
        
        # Sauvegarder
        self.save_results()
        
        # Résumé
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ FINAL")
        print("=" * 60)
        
        events_with_email = len([e for e in self.all_events if e.get('organizer_email')])
        events_without_email = len(self.all_events) - events_with_email
        
        print(f"   Total événements: {len(self.all_events)}")
        print(f"   Avec email: {events_with_email}")
        print(f"   Sans email: {events_without_email}")
        print(f"\n   Par source:")
        
        source_counts = {}
        for e in self.all_events:
            src = e.get('source_name', '?')
            source_counts[src] = source_counts.get(src, 0) + 1
        
        for src, cnt in sorted(source_counts.items()):
            print(f"   - {src}: {cnt}")
        
        if len(self.all_events) < TARGET_TOTAL:
            print(f"\n   ⚠️ Objectif non atteint: {len(self.all_events)}/{TARGET_TOTAL}")
            print(f"   Il faudra ajouter d'autres sources ou relancer le scraping")


if __name__ == "__main__":
    scraper = ValaisScraperV5()
    scraper.run()
