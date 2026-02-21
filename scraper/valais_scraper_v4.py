"""
Scraper d'événements Valais V4 - Avec extraction d'emails
Va chercher l'email de contact sur chaque page de détail

Usage: python valais_scraper_v4.py
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re
import random
import sys
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import hashlib

# Forcer UTF-8 sur Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
RATE_LIMIT_SECONDS = 8
DETAIL_PAGE_DELAY = 3  # Délai entre chaque page de détail
MAX_EVENTS = 50  # Limité car on visite chaque page de détail
START_DATE = datetime(2026, 2, 1)  # Accepter dès février pour avoir plus d'événements

# User-Agents rotatifs
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

# Pattern pour détecter les emails
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

# Emails à exclure (génériques, noreply, etc.)
EXCLUDED_EMAILS = [
    'noreply@', 'no-reply@', 'info@google', 'privacy@', 
    'support@', 'admin@', 'webmaster@', 'example@',
    '@example.com', '@test.com', '@localhost'
]

# Sources d'événements
SOURCES = [
    {
        "name": "Culture Valais",
        "url": "https://agenda.culturevalais.ch/fr/agenda/evenements",
        "type": "html",
        "selectors": {
            "event_list": ".event-item, .agenda-item, article, .card",
            "title": "h2, h3, .title, .event-title, .card-title",
            "date": ".date, time, [datetime], .event-date",
            "location": ".location, .lieu, address, .venue",
            "link": "a[href]"
        }
    }
]

# Mapping catégories
CATEGORY_KEYWORDS = {
    "Music > Electronic > Techno": ["techno", "electronic", "dj", "club", "electro"],
    "Music > Electronic > House": ["house", "deep house", "tech house"],
    "Music > Rock / Metal > Rock": ["rock", "punk", "indie rock", "concert rock"],
    "Music > Jazz / Soul / Funk": ["jazz", "blues", "soul", "funk", "swing"],
    "Music > Pop / Variété": ["pop", "chanson", "variété", "concert", "musique"],
    "Music > Folk / Acoustic": ["folk", "acoustic", "country"],
    "Music > Classique > Formes": ["classique", "orchestre", "symphonie", "opéra", "choeur", "harmonie"],
    "Culture > Cinéma & Projections": ["cinéma", "film", "projection"],
    "Culture > Expositions": ["exposition", "vernissage", "galerie", "musée", "art"],
    "Culture > Conférences & Rencontres": ["conférence", "débat", "rencontre", "lecture"],
    "Culture > Workshops": ["atelier", "workshop", "cours", "formation"],
    "Arts Vivants > Théâtre": ["théâtre", "spectacle", "comédie", "stand-up", "humour"],
    "Arts Vivants > Danse": ["danse", "ballet", "chorégraphie"],
    "Food & Drinks > Dégustations": ["dégustation", "vin", "œnologie", "cave"],
    "Food & Drinks > Restauration": ["brunch", "repas", "gastronomie", "food", "raclette"],
    "Loisirs & Animation > Jeux & Soirées": ["quiz", "blind test", "karaoke", "jeu", "loto"],
    "Loisirs & Animation > Défilés & Fêtes": ["fête", "carnaval", "défilé", "marché", "brocante", "noël", "foire"],
    "Sport > Terrestre": ["course", "trail", "randonnée", "vélo", "cyclisme", "football", "ski de fond", "raquettes"],
    "Sport > Glisse": ["ski", "snowboard", "patinage", "hockey", "freeride"],
    "Festivals & Grandes Fêtes": ["festival", "open air", "grande fête"],
    "Business & Communauté": ["networking", "séminaire", "congrès", "salon"]
}

# Coordonnées des villes du Valais
VALAIS_CITIES = {
    "sion": (46.2333, 7.3667),
    "sierre": (46.2919, 7.5347),
    "monthey": (46.2500, 6.9500),
    "martigny": (46.1000, 7.0667),
    "verbier": (46.0964, 7.2286),
    "crans-montana": (46.3067, 7.4800),
    "crans montana": (46.3067, 7.4800),
    "zermatt": (46.0207, 7.7491),
    "visp": (46.2936, 7.8828),
    "brig": (46.3167, 7.9833),
    "nendaz": (46.1833, 7.3000),
    "saas-fee": (46.1083, 7.9278),
    "leukerbad": (46.3792, 7.6261),
    "valais": (46.2333, 7.3667),
}


def get_headers():
    """Retourne des headers avec User-Agent rotatif"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr-CH,fr;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }


def extract_emails_from_page(soup: BeautifulSoup, url: str) -> List[str]:
    """Extrait tous les emails d'une page"""
    emails = set()
    
    # 1. Chercher les liens mailto:
    mailto_links = soup.select('a[href^="mailto:"]')
    for link in mailto_links:
        href = link.get('href', '')
        if href.startswith('mailto:'):
            email = href.replace('mailto:', '').split('?')[0].strip().lower()
            if email and '@' in email:
                emails.add(email)
    
    # 2. Chercher dans le texte de la page
    page_text = soup.get_text()
    found_emails = EMAIL_PATTERN.findall(page_text)
    for email in found_emails:
        emails.add(email.lower())
    
    # 3. Chercher dans les attributs data-*
    elements_with_data = soup.select('[data-email], [data-contact]')
    for elem in elements_with_data:
        for attr in ['data-email', 'data-contact']:
            value = elem.get(attr, '')
            if '@' in value:
                emails.add(value.lower())
    
    # Filtrer les emails indésirables
    valid_emails = []
    for email in emails:
        is_excluded = any(excl in email.lower() for excl in EXCLUDED_EMAILS)
        if not is_excluded and len(email) > 5:
            valid_emails.append(email)
    
    return valid_emails


def find_category(title: str, description: str = "") -> List[str]:
    """Trouve les catégories les plus appropriées"""
    text = f"{title} {description}".lower()
    
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        if score > 0:
            scores[category] = score
    
    if not scores:
        return ["Loisirs & Animation > Défilés & Fêtes"]
    
    sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [cat for cat, _ in sorted_cats[:2]]


def geocode_location(location: str) -> Optional[Tuple[float, float]]:
    """Géocode une adresse"""
    location_lower = location.lower()
    
    for city_name, coords in VALAIS_CITIES.items():
        if city_name in location_lower:
            return (
                coords[0] + random.uniform(-0.003, 0.003),
                coords[1] + random.uniform(-0.003, 0.003)
            )
    
    return VALAIS_CITIES.get("valais")


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse une chaîne de date en datetime"""
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    months_fr = {
        "janvier": 1, "février": 2, "mars": 3, "avril": 4,
        "mai": 5, "juin": 6, "juillet": 7, "août": 8,
        "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
    }
    
    # Pattern: "Ve 06.02.2026"
    match = re.search(r'[A-Za-z]{2}\s+(\d{1,2})\.(\d{1,2})\.(\d{4})', date_str)
    if match:
        day, month, year = match.groups()
        try:
            return datetime(int(year), int(month), int(day))
        except:
            pass
    
    # Pattern: "15.03.2026"
    match = re.search(r'(\d{1,2})[./](\d{1,2})[./](\d{4})', date_str)
    if match:
        day, month, year = match.groups()
        try:
            return datetime(int(year), int(month), int(day))
        except:
            pass
    
    # Pattern: "15 mars 2026"
    match = re.search(r'(\d{1,2})\s+([a-zéûô]+)\s+(\d{4})', date_str, re.IGNORECASE)
    if match:
        day, month_str, year = match.groups()
        month = months_fr.get(month_str.lower())
        if month:
            try:
                return datetime(int(year), month, int(day))
            except:
                pass
    
    # Pattern: "2026-03-15"
    match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if match:
        year, month, day = match.groups()
        try:
            return datetime(int(year), int(month), int(day))
        except:
            pass
    
    return None


def rewrite_description(original: str, title: str, location: str) -> str:
    """Réécrit une description de manière originale"""
    if not original or len(original) < 20:
        original = title
    
    city = "Valais"
    for city_name in VALAIS_CITIES.keys():
        if city_name.lower() in location.lower():
            city = city_name.title().replace("-", "-")
            break
    
    # Nettoyer le texte
    clean = re.sub(r'\s+', ' ', original).strip()
    clean = re.sub(r'En savoir plus.*', '', clean, flags=re.IGNORECASE)
    
    if len(clean) > 200:
        clean = clean[:200] + "..."
    
    templates = [
        f"Événement à {city} : {clean}",
        f"Rendez-vous à {city} pour {title.lower()}. {clean}",
        f"{city} vous invite : {clean}",
    ]
    
    return random.choice(templates)


class ValaisScraperV4:
    """Scraper V4 avec extraction d'emails depuis les pages de détail"""
    
    def __init__(self):
        self.session = requests.Session()
        self.events = []
        self.seen_hashes = set()
        self.emails_found = 0
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Récupère et parse une page HTML"""
        try:
            response = self.session.get(url, headers=get_headers(), timeout=30, verify=True)
            
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
            else:
                return None
        except requests.exceptions.SSLError:
            try:
                response = self.session.get(url, headers=get_headers(), timeout=30, verify=False)
                if response.status_code == 200:
                    return BeautifulSoup(response.text, "html.parser")
            except:
                pass
            return None
        except Exception as e:
            print(f"    ❌ Erreur: {e}")
            return None
    
    def event_hash(self, title: str, date: datetime, location: str) -> str:
        """Génère un hash unique pour détecter les doublons"""
        key = f"{title.lower().strip()[:50]}_{date.strftime('%Y-%m-%d') if date else 'nodate'}_{location.lower().strip()[:30]}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def add_event(self, event: Dict) -> bool:
        """Ajoute un événement s'il n'est pas un doublon"""
        if not event.get("title") or not event.get("source_url"):
            return False
        
        event_id = self.event_hash(
            event.get("title", ""),
            event.get("start_date"),
            event.get("location", "")
        )
        
        if event_id in self.seen_hashes:
            return False
        
        self.seen_hashes.add(event_id)
        self.events.append(event)
        return True
    
    def fetch_detail_page_and_extract_email(self, url: str) -> Tuple[List[str], str, str]:
        """
        Va sur la page de détail pour extraire:
        - emails de contact
        - description complète
        - lieu complet
        """
        print(f"    📄 Détail: {url[:60]}...")
        
        soup = self.fetch_page(url)
        if not soup:
            return [], "", ""
        
        emails = extract_emails_from_page(soup, url)
        
        # Extraire la description complète
        description = ""
        desc_selectors = ['.description', '.content', '.event-description', 
                         '.event-content', 'article', '.body', 'main p']
        for sel in desc_selectors:
            elem = soup.select_one(sel)
            if elem:
                text = elem.get_text(strip=True)
                if len(text) > len(description):
                    description = text
        
        # Extraire le lieu complet
        location = ""
        loc_selectors = ['.location', '.venue', '.lieu', 'address', 
                        '.event-location', '[itemprop="location"]']
        for sel in loc_selectors:
            elem = soup.select_one(sel)
            if elem:
                text = elem.get_text(strip=True)
                if text and len(text) > 3:
                    location = text
                    break
        
        if emails:
            print(f"    📧 Email trouvé: {emails[0]}")
            self.emails_found += 1
        
        return emails, description, location
    
    def scrape_source(self, source: Dict) -> List[Dict]:
        """Scrape une source avec visite des pages de détail"""
        print(f"\n{'='*60}")
        print(f"🔍 Source: {source['name']}")
        print(f"{'='*60}")
        
        soup = self.fetch_page(source["url"])
        if not soup:
            print("  ❌ Impossible de charger la page")
            return []
        
        selectors = source.get("selectors", {})
        event_selector = selectors.get("event_list", "article, .event")
        items = soup.select(event_selector)
        
        print(f"  📋 {len(items)} éléments trouvés sur la page listing")
        
        events_added = 0
        
        for i, item in enumerate(items):
            if len(self.events) >= MAX_EVENTS:
                print(f"\n  🎯 Limite de {MAX_EVENTS} événements atteinte")
                break
            
            try:
                # Titre
                title_elem = item.select_one(selectors.get("title", "h2, h3"))
                title = title_elem.get_text(strip=True) if title_elem else None
                
                if not title or len(title) < 5:
                    continue
                
                # Ignorer les calendriers
                if title.startswith("LuMaMeJe"):
                    continue
                
                print(f"\n  [{i+1}] {title[:50]}...")
                
                # Lien vers page de détail
                link_elem = item.select_one(selectors.get("link", "a[href]"))
                if not link_elem or not link_elem.get("href"):
                    print("    ⚠️ Pas de lien de détail")
                    continue
                
                href = link_elem.get("href")
                if href.startswith("/"):
                    from urllib.parse import urljoin
                    source_url = urljoin(source["url"], href)
                elif href.startswith("http"):
                    source_url = href
                else:
                    continue
                
                # Extraire la date du listing
                date_elem = item.select_one(selectors.get("date", ".date, time"))
                date_str = ""
                if date_elem:
                    date_str = date_elem.get("datetime", "") or date_elem.get_text(strip=True)
                
                # Essayer aussi dans le texte complet
                if not date_str:
                    date_str = item.get_text(strip=True)
                
                start_date = parse_date(date_str)
                
                # Vérifier la date
                if start_date and start_date < START_DATE:
                    print(f"    ⏭️ Date passée: {start_date.strftime('%d.%m.%Y')}")
                    continue
                
                # === ALLER SUR LA PAGE DE DÉTAIL ===
                time.sleep(DETAIL_PAGE_DELAY)
                emails, detail_desc, detail_location = self.fetch_detail_page_and_extract_email(source_url)
                
                # Location
                location_elem = item.select_one(selectors.get("location", ".location"))
                location = location_elem.get_text(strip=True) if location_elem else ""
                
                # Prendre le lieu le plus complet
                if detail_location and len(detail_location) > len(location):
                    location = detail_location
                
                if not location or len(location) < 3:
                    location = "Valais, Suisse"
                
                # Géocoder
                coords = geocode_location(location)
                if not coords:
                    coords = VALAIS_CITIES["valais"]
                
                # Description
                full_text = item.get_text(strip=True)[:500] if item else title
                if detail_desc and len(detail_desc) > len(full_text):
                    full_text = detail_desc
                
                description = rewrite_description(full_text, title, location)
                
                # Catégories
                categories = find_category(title, description)
                
                # Email de l'organisateur
                organizer_email = emails[0] if emails else None
                
                event = {
                    "title": title[:255],
                    "description": description[:2000],
                    "location": location[:255],
                    "latitude": coords[0],
                    "longitude": coords[1],
                    "start_date": start_date,
                    "end_date": start_date,
                    "start_time": None,
                    "categories": categories,
                    "source_url": source_url,
                    "source_name": source["name"],
                    "organizer_email": organizer_email,
                    "organizer_name": source["name"]
                }
                
                if self.add_event(event):
                    events_added += 1
                    status = "📧" if organizer_email else "📝"
                    date_display = start_date.strftime('%d.%m.%Y') if start_date else "Date ?"
                    print(f"    {status} Ajouté! ({date_display})")
                
            except Exception as e:
                print(f"    ❌ Erreur: {e}")
                continue
        
        print(f"\n  ✅ {events_added} événements ajoutés depuis {source['name']}")
        return self.events
    
    def run(self):
        """Lance le scraping complet"""
        print("=" * 60)
        print("🗺️ SCRAPER ÉVÉNEMENTS VALAIS V4 - Avec extraction emails")
        print("=" * 60)
        print(f"📅 Période: Dès {START_DATE.strftime('%d.%m.%Y')}")
        print(f"🎯 Objectif: {MAX_EVENTS} événements max")
        print(f"⏱️ Délai page détail: {DETAIL_PAGE_DELAY}s")
        print("=" * 60)
        
        for source in SOURCES:
            if len(self.events) >= MAX_EVENTS:
                break
            
            try:
                self.scrape_source(source)
            except Exception as e:
                print(f"  ❌ Erreur source: {e}")
            
            time.sleep(RATE_LIMIT_SECONDS)
        
        print("\n" + "=" * 60)
        print(f"📊 RÉSULTAT FINAL")
        print("=" * 60)
        print(f"  📋 Total événements: {len(self.events)}")
        print(f"  📧 Avec email: {self.emails_found}")
        print(f"  📝 Sans email: {len(self.events) - self.emails_found}")
        print("=" * 60)
        
        return self.events
    
    def save_to_json(self, filename: str = "valais_events_v4.json"):
        """Sauvegarde en JSON"""
        events_serializable = []
        for event in self.events:
            ev = event.copy()
            if ev.get("start_date"):
                ev["start_date"] = ev["start_date"].strftime("%Y-%m-%d")
            if ev.get("end_date"):
                ev["end_date"] = ev["end_date"].strftime("%Y-%m-%d")
            events_serializable.append(ev)
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(events_serializable, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Sauvegardé: {filename}")


def main():
    print("\n🚀 Démarrage du scraper V4 (avec extraction emails)...")
    
    scraper = ValaisScraperV4()
    
    try:
        events = scraper.run()
        
        if events:
            scraper.save_to_json()
            
            print("\n📁 Fichier généré: valais_events_v4.json")
            print("\n📝 Pour importer via l'API:")
            print("   POST /api/events/scraped/batch")
            print("   Body: { \"events\": [...], \"send_emails\": true }")
        else:
            print("\n⚠️ Aucun événement trouvé")
            
    except KeyboardInterrupt:
        print("\n\n⛔ Scraping interrompu")
        if scraper.events:
            print(f"💾 Sauvegarde des {len(scraper.events)} événements collectés...")
            scraper.save_to_json()


if __name__ == "__main__":
    main()
