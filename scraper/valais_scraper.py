"""
Scraper d'événements publics pour le Valais (Suisse)
Collecte les informations factuelles (dates, lieux, titres) depuis des sources publiques

Usage: python valais_scraper.py

Règles légales respectées:
- Collecte uniquement d'informations factuelles publiques (non protégées par le droit d'auteur)
- Respect du rate limiting (8 sec entre requêtes)
- Respect des robots.txt
- Descriptions réécrites (pas de copier-coller)
- Lien source conservé
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import urllib.robotparser
from urllib.parse import urljoin, urlparse
import hashlib
import os

# Configuration
RATE_LIMIT_SECONDS = 8  # Délai entre les requêtes
MAX_EVENTS = 300
START_DATE = datetime(2026, 3, 1)  # Mars 2026

# User-Agents rotatifs (navigateurs réels)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
]

# Arbre des catégories MapEvent (simplifié pour le mapping)
CATEGORY_KEYWORDS = {
    # Music
    "Music > Electronic > Techno": ["techno", "electronic", "dj", "club"],
    "Music > Electronic > House": ["house", "deep house", "tech house"],
    "Music > Rock / Metal > Rock": ["rock", "punk", "grunge", "indie rock"],
    "Music > Rock / Metal > Metal": ["metal", "heavy metal", "metalcore"],
    "Music > Jazz / Soul / Funk": ["jazz", "blues", "soul", "funk", "swing"],
    "Music > Pop / Variété": ["pop", "chanson", "variété", "concert"],
    "Music > Folk / Acoustic": ["folk", "acoustic", "country", "bluegrass"],
    "Music > Classique > Formes": ["classique", "orchestre", "symphonie", "opéra", "choeur", "chœur"],
    
    # Culture
    "Culture > Cinéma & Projections": ["cinéma", "film", "projection", "court-métrage"],
    "Culture > Expositions": ["exposition", "vernissage", "galerie", "musée", "art"],
    "Culture > Conférences & Rencontres": ["conférence", "débat", "rencontre", "lecture"],
    "Culture > Workshops": ["atelier", "workshop", "cours", "formation"],
    
    # Arts Vivants
    "Arts Vivants > Théâtre": ["théâtre", "spectacle", "comédie", "stand-up", "humour", "one-man"],
    "Arts Vivants > Danse": ["danse", "ballet", "chorégraphie"],
    "Arts Vivants > Cirque": ["cirque", "acrobatie", "clown"],
    
    # Food & Drinks
    "Food & Drinks > Dégustations": ["dégustation", "vin", "œnologie", "cave", "vigneron"],
    "Food & Drinks > Restauration": ["brunch", "repas", "gastronomie", "food", "marché alimentaire"],
    
    # Loisirs & Animation
    "Loisirs & Animation > Jeux & Soirées": ["quiz", "blind test", "karaoke", "jeu", "loto", "bingo"],
    "Loisirs & Animation > Défilés & Fêtes": ["fête", "carnaval", "défilé", "marché", "brocante", "noël", "foire"],
    
    # Sport
    "Sport > Terrestre": ["course", "trail", "randonnée", "vélo", "cyclisme", "football", "ski de fond", "raquettes"],
    "Sport > Glisse": ["ski", "snowboard", "patinage", "hockey", "luge"],
    "Sport > Aquatique": ["natation", "piscine", "aquagym"],
    
    # Festivals
    "Festivals & Grandes Fêtes": ["festival", "open air", "grande fête", "rave"],
    
    # Business
    "Business & Communauté": ["networking", "séminaire", "congrès", "salon professionnel"]
}

# Sources publiques d'événements en Valais
SOURCES = [
    {
        "name": "Valais/Wallis Tourisme",
        "base_url": "https://www.valais.ch",
        "events_url": "https://www.valais.ch/fr/activites/evenements",
        "type": "official_tourism"
    },
    {
        "name": "Sion Ville",
        "base_url": "https://www.sion.ch",
        "events_url": "https://www.sion.ch/vivre/culture-sports-loisirs/agenda",
        "type": "municipality"
    },
    {
        "name": "Monthey Ville",
        "base_url": "https://www.monthey.ch",
        "events_url": "https://www.monthey.ch/loisirs-et-culture/agenda-evenements",
        "type": "municipality"
    },
    {
        "name": "Martigny Ville",
        "base_url": "https://www.martigny.ch",
        "events_url": "https://www.martigny.ch/fr/agenda",
        "type": "municipality"
    },
    {
        "name": "Sierre Ville",
        "base_url": "https://www.sierre.ch",
        "events_url": "https://www.sierre.ch/fr/agenda",
        "type": "municipality"
    },
    {
        "name": "Verbier",
        "base_url": "https://www.verbier.ch",
        "events_url": "https://www.verbier.ch/fr/evenements",
        "type": "resort"
    },
    {
        "name": "Crans-Montana",
        "base_url": "https://www.crans-montana.ch",
        "events_url": "https://www.crans-montana.ch/fr/evenements",
        "type": "resort"
    },
    {
        "name": "Zermatt",
        "base_url": "https://www.zermatt.ch",
        "events_url": "https://www.zermatt.ch/fr/Evenements",
        "type": "resort"
    }
]

# Coordonnées approximatives des villes du Valais (pour géocodage de fallback)
VALAIS_CITIES_COORDS = {
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
    "naters": (46.3258, 7.9886),
    "saas-fee": (46.1083, 7.9278),
    "leukerbad": (46.3792, 7.6261),
    "champéry": (46.1750, 6.8694),
    "nendaz": (46.1833, 7.3000),
    "val d'anniviers": (46.2167, 7.5667),
    "grimentz": (46.1789, 7.5756),
    "evolène": (46.1128, 7.4931),
    "val d'hérens": (46.1128, 7.4931),
    "saxon": (46.1500, 7.1667),
    "fully": (46.1333, 7.1167),
    "conthey": (46.2167, 7.3000),
    "savièse": (46.2500, 7.3500),
    "ayent": (46.2833, 7.4167),
    "lens": (46.2833, 7.4333),
    "chermignon": (46.2833, 7.4667),
    "montana": (46.3067, 7.4800),
    "anzère": (46.2917, 7.4000),
    "saint-maurice": (46.2167, 7.0000),
    "st-maurice": (46.2167, 7.0000),
    "vouvry": (46.3333, 6.8833),
    "collombey": (46.2667, 6.9333),
    "troistorrents": (46.2167, 6.9167),
    "val-d'illiez": (46.2000, 6.8833),
    "champoussin": (46.1833, 6.8500),
    "morgins": (46.2333, 6.8500),
    "les crosets": (46.1833, 6.8333),
    "leysin": (46.3500, 7.0167),
    "ovronnaz": (46.1917, 7.1667),
    "valais": (46.2333, 7.3667),  # Centre du Valais par défaut
}


class RobotsChecker:
    """Vérifie les règles robots.txt des sites"""
    
    def __init__(self):
        self.parsers = {}
    
    def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        """Vérifie si on peut accéder à une URL selon robots.txt"""
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            if base_url not in self.parsers:
                rp = urllib.robotparser.RobotFileParser()
                rp.set_url(f"{base_url}/robots.txt")
                try:
                    rp.read()
                except:
                    # Si pas de robots.txt, on autorise
                    return True
                self.parsers[base_url] = rp
            
            return self.parsers[base_url].can_fetch(user_agent, url)
        except:
            return True  # En cas d'erreur, on autorise


class DescriptionRewriter:
    """Réécrit les descriptions pour créer un contenu original"""
    
    TEMPLATES = [
        "Rendez-vous à {location} pour {event_type}. {details}",
        "{event_type} prévu à {location}. {details}",
        "Ne manquez pas {event_type} qui se tiendra à {location}. {details}",
        "{location} accueille {event_type}. {details}",
        "Découvrez {event_type} à {location}. {details}",
    ]
    
    EVENT_TYPE_MAPPING = {
        "concert": "un concert",
        "spectacle": "un spectacle",
        "exposition": "une exposition",
        "festival": "un festival",
        "fête": "une fête",
        "marché": "un marché",
        "atelier": "un atelier",
        "conférence": "une conférence",
        "dégustation": "une dégustation",
        "randonnée": "une randonnée",
        "course": "une course",
        "théâtre": "une représentation théâtrale",
        "cinéma": "une projection",
        "vernissage": "un vernissage",
    }
    
    @classmethod
    def rewrite(cls, original: str, title: str, location: str) -> str:
        """Réécrit une description de manière originale"""
        if not original:
            original = title
        
        # Déterminer le type d'événement
        event_type = "cet événement"
        title_lower = title.lower()
        for keyword, phrase in cls.EVENT_TYPE_MAPPING.items():
            if keyword in title_lower:
                event_type = phrase
                break
        
        # Extraire les détails importants (horaires, prix, infos pratiques)
        details = ""
        
        # Chercher les horaires
        time_match = re.search(r'(\d{1,2}[h:]\d{0,2})', original)
        if time_match:
            details += f"Début à {time_match.group(1)}. "
        
        # Chercher les prix
        price_match = re.search(r'(\d+[\.,]?\d*)\s*(CHF|Fr\.|francs?)', original, re.IGNORECASE)
        if price_match:
            details += f"Entrée: {price_match.group(1)} CHF. "
        
        # Si pas de détails, ajouter une phrase générique
        if not details:
            details = "Événement ouvert à tous."
        
        # Choisir un template aléatoire
        template = random.choice(cls.TEMPLATES)
        
        return template.format(
            location=location,
            event_type=event_type,
            details=details.strip()
        )


class CategoryMapper:
    """Mappe les événements vers les catégories de l'arbre MapEvent"""
    
    @staticmethod
    def find_category(title: str, description: str = "") -> List[str]:
        """Trouve la catégorie la plus appropriée"""
        text = f"{title} {description}".lower()
        
        scores = {}
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text)
            if score > 0:
                scores[category] = score
        
        if not scores:
            return ["Loisirs & Animation > Défilés & Fêtes"]  # Catégorie par défaut
        
        # Retourner les meilleures catégories
        sorted_cats = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [cat for cat, _ in sorted_cats[:2]]  # Max 2 catégories


class GeocodingService:
    """Service de géocodage pour les adresses"""
    
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    
    @classmethod
    def geocode(cls, address: str, city: str = "") -> Optional[Tuple[float, float]]:
        """Géocode une adresse en utilisant Nominatim (gratuit)"""
        
        # D'abord essayer avec l'adresse complète
        full_address = f"{address}, {city}, Valais, Suisse" if city else f"{address}, Valais, Suisse"
        
        try:
            response = requests.get(
                cls.NOMINATIM_URL,
                params={
                    "q": full_address,
                    "format": "json",
                    "limit": 1,
                    "countrycodes": "ch"
                },
                headers={"User-Agent": "MapEventAI/1.0 (contact@mapevent.world)"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    return (float(data[0]["lat"]), float(data[0]["lon"]))
        except:
            pass
        
        # Fallback: utiliser les coordonnées de la ville
        city_lower = city.lower() if city else ""
        for city_name, coords in VALAIS_CITIES_COORDS.items():
            if city_name in city_lower or city_lower in city_name:
                return coords
        
        # Fallback ultime: centre du Valais
        return VALAIS_CITIES_COORDS.get("valais")
    
    @classmethod
    def extract_city_from_address(cls, address: str) -> str:
        """Extrait le nom de la ville depuis une adresse"""
        for city_name in VALAIS_CITIES_COORDS.keys():
            if city_name.lower() in address.lower():
                return city_name.title()
        return "Valais"


class ValaisScraper:
    """Scraper principal pour les événements du Valais"""
    
    def __init__(self):
        self.robots_checker = RobotsChecker()
        self.session = requests.Session()
        self.events = []
        self.seen_hashes = set()  # Pour éviter les doublons
    
    def get_headers(self) -> Dict:
        """Retourne des headers avec User-Agent rotatif"""
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "fr-CH,fr;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Récupère et parse une page"""
        # Vérifier robots.txt
        if not self.robots_checker.can_fetch(url):
            print(f"  ⚠️ Bloqué par robots.txt: {url}")
            return None
        
        try:
            response = self.session.get(
                url,
                headers=self.get_headers(),
                timeout=30
            )
            
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
            else:
                print(f"  ⚠️ HTTP {response.status_code}: {url}")
                return None
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            return None
    
    def parse_date(self, date_str: str) -> Optional[Tuple[datetime, datetime]]:
        """Parse une chaîne de date en dates de début et fin"""
        if not date_str:
            return None
        
        # Nettoyer la chaîne
        date_str = date_str.strip()
        
        # Formats courants
        patterns = [
            # "15 mars 2026"
            (r"(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})", 
             lambda m: datetime(int(m.group(3)), cls._month_to_num(m.group(2)), int(m.group(1)))),
            # "15.03.2026"
            (r"(\d{1,2})\.(\d{1,2})\.(\d{4})",
             lambda m: datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))),
            # "2026-03-15"
            (r"(\d{4})-(\d{1,2})-(\d{1,2})",
             lambda m: datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))),
        ]
        
        for pattern, parser in patterns:
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                try:
                    start_date = parser(match)
                    # Par défaut, même date de fin
                    end_date = start_date
                    
                    # Chercher une date de fin
                    remaining = date_str[match.end():]
                    for pattern2, parser2 in patterns:
                        match2 = re.search(pattern2, remaining, re.IGNORECASE)
                        if match2:
                            try:
                                end_date = parser2(match2)
                            except:
                                pass
                            break
                    
                    return (start_date, end_date)
                except:
                    pass
        
        return None
    
    @staticmethod
    def _month_to_num(month: str) -> int:
        """Convertit un nom de mois en numéro"""
        months = {
            "janvier": 1, "février": 2, "mars": 3, "avril": 4,
            "mai": 5, "juin": 6, "juillet": 7, "août": 8,
            "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12
        }
        return months.get(month.lower(), 1)
    
    def parse_time(self, time_str: str) -> Optional[str]:
        """Parse une chaîne d'heure"""
        if not time_str:
            return None
        
        # Formats: "19h30", "19:30", "19h", "19 h 30"
        patterns = [
            (r"(\d{1,2})\s*[h:]\s*(\d{2})?", lambda m: f"{int(m.group(1)):02d}:{m.group(2) or '00'}:00"),
        ]
        
        for pattern, formatter in patterns:
            match = re.search(pattern, time_str, re.IGNORECASE)
            if match:
                try:
                    return formatter(match)
                except:
                    pass
        
        return None
    
    def event_hash(self, title: str, date: datetime, location: str) -> str:
        """Génère un hash unique pour détecter les doublons"""
        key = f"{title.lower().strip()}_{date.strftime('%Y-%m-%d')}_{location.lower().strip()}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def add_event(self, event: Dict) -> bool:
        """Ajoute un événement s'il n'est pas un doublon"""
        # Vérifier que toutes les infos obligatoires sont présentes
        required = ["title", "start_date", "location", "source_url"]
        for field in required:
            if not event.get(field):
                print(f"  ⚠️ Champ manquant: {field}")
                return False
        
        # Vérifier que la date est >= mars 2026
        if event["start_date"] < START_DATE:
            print(f"  ⚠️ Date trop ancienne: {event['start_date']}")
            return False
        
        # Vérifier les doublons
        event_id = self.event_hash(event["title"], event["start_date"], event["location"])
        if event_id in self.seen_hashes:
            print(f"  ⚠️ Doublon détecté: {event['title']}")
            return False
        
        self.seen_hashes.add(event_id)
        self.events.append(event)
        return True
    
    def scrape_generic_page(self, source: Dict) -> List[Dict]:
        """Scrape une page générique d'événements"""
        print(f"\n🔍 Scraping: {source['name']}")
        
        soup = self.fetch_page(source["events_url"])
        if not soup:
            return []
        
        events = []
        
        # Chercher les liens vers les événements individuels
        # Patterns communs: articles, divs avec class event, liens dans des listes
        event_selectors = [
            "article.event",
            ".event-item",
            ".agenda-item",
            ".event-card",
            "[class*='event']",
            "[class*='agenda']",
            "li.event",
            ".list-item"
        ]
        
        found_items = []
        for selector in event_selectors:
            items = soup.select(selector)
            if items:
                found_items = items
                break
        
        if not found_items:
            # Fallback: chercher tous les liens qui semblent être des événements
            links = soup.find_all("a", href=True)
            for link in links:
                href = link.get("href", "")
                if any(kw in href.lower() for kw in ["event", "agenda", "manifestation", "evenement"]):
                    found_items.append(link)
        
        print(f"  📋 {len(found_items)} éléments trouvés")
        
        # Limiter et traiter
        for item in found_items[:50]:  # Max 50 par source
            time.sleep(RATE_LIMIT_SECONDS)
            
            try:
                # Extraire les infos de base
                title_elem = item.find(["h1", "h2", "h3", "h4", ".title", "[class*='title']"])
                title = title_elem.get_text(strip=True) if title_elem else item.get_text(strip=True)[:100]
                
                if not title or len(title) < 5:
                    continue
                
                # Lien vers la page détail
                link = item.get("href") if item.name == "a" else item.find("a", href=True)
                if link and hasattr(link, "get"):
                    link = link.get("href")
                
                if link:
                    detail_url = urljoin(source["base_url"], link)
                else:
                    detail_url = source["events_url"]
                
                # Essayer de scraper la page de détail
                detail_soup = None
                if link and link != source["events_url"]:
                    detail_soup = self.fetch_page(detail_url)
                    time.sleep(RATE_LIMIT_SECONDS)
                
                # Extraire les infos
                date_text = ""
                location_text = ""
                description_text = ""
                
                search_elem = detail_soup if detail_soup else item
                
                # Date
                date_elem = search_elem.find(["time", ".date", "[class*='date']", "[datetime]"])
                if date_elem:
                    date_text = date_elem.get("datetime", "") or date_elem.get_text(strip=True)
                
                # Lieu
                location_elem = search_elem.find([".location", ".lieu", "[class*='location']", "[class*='lieu']", "address"])
                if location_elem:
                    location_text = location_elem.get_text(strip=True)
                
                # Description
                desc_elem = search_elem.find([".description", ".content", "p", "[class*='description']"])
                if desc_elem:
                    description_text = desc_elem.get_text(strip=True)[:500]
                
                # Parser les dates
                dates = self.parse_date(date_text) if date_text else None
                if not dates:
                    # Essayer de trouver la date dans le titre ou la description
                    dates = self.parse_date(f"{title} {description_text}")
                
                if not dates:
                    print(f"  ⚠️ Pas de date trouvée pour: {title[:50]}")
                    continue
                
                start_date, end_date = dates
                
                # Location
                if not location_text:
                    # Extraire de la ville de la source
                    location_text = source["name"].replace("Ville", "").strip()
                
                # Géocoder
                city = GeocodingService.extract_city_from_address(location_text)
                coords = GeocodingService.geocode(location_text, city)
                
                if not coords:
                    print(f"  ⚠️ Pas de coordonnées pour: {location_text}")
                    continue
                
                # Catégories
                categories = CategoryMapper.find_category(title, description_text)
                
                # Réécrire la description
                new_description = DescriptionRewriter.rewrite(description_text, title, location_text)
                
                event = {
                    "title": title[:255],
                    "description": new_description,
                    "location": location_text[:255],
                    "latitude": coords[0],
                    "longitude": coords[1],
                    "start_date": start_date,
                    "end_date": end_date,
                    "start_time": self.parse_time(date_text),
                    "end_time": None,
                    "categories": categories,
                    "source_url": detail_url,
                    "source_name": source["name"]
                }
                
                if self.add_event(event):
                    print(f"  ✅ {title[:50]}... ({start_date.strftime('%d.%m.%Y')})")
                    
                if len(self.events) >= MAX_EVENTS:
                    print(f"\n🎉 Objectif atteint: {MAX_EVENTS} événements!")
                    return events
                    
            except Exception as e:
                print(f"  ❌ Erreur parsing: {e}")
                continue
        
        return events
    
    def run(self):
        """Lance le scraping complet"""
        print("=" * 60)
        print("🗺️ SCRAPER ÉVÉNEMENTS VALAIS - MapEventAI")
        print("=" * 60)
        print(f"📅 Période: Mars 2026 et après")
        print(f"🎯 Objectif: {MAX_EVENTS} événements")
        print(f"⏱️ Rate limit: {RATE_LIMIT_SECONDS} secondes")
        print("=" * 60)
        
        # Mélanger les sources pour varier
        sources = SOURCES.copy()
        random.shuffle(sources)
        
        for source in sources:
            if len(self.events) >= MAX_EVENTS:
                break
            
            try:
                self.scrape_generic_page(source)
            except Exception as e:
                print(f"  ❌ Erreur source {source['name']}: {e}")
            
            # Pause entre les sources
            time.sleep(RATE_LIMIT_SECONDS * 2)
        
        print("\n" + "=" * 60)
        print(f"📊 RÉSULTAT: {len(self.events)} événements collectés")
        print("=" * 60)
        
        return self.events
    
    def save_to_json(self, filename: str = "valais_events.json"):
        """Sauvegarde les événements en JSON"""
        # Convertir les dates en strings
        events_serializable = []
        for event in self.events:
            ev = event.copy()
            ev["start_date"] = ev["start_date"].strftime("%Y-%m-%d")
            ev["end_date"] = ev["end_date"].strftime("%Y-%m-%d") if ev.get("end_date") else None
            events_serializable.append(ev)
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(events_serializable, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Sauvegardé: {filename}")
    
    def save_to_sql(self, filename: str = "valais_events.sql"):
        """Génère un fichier SQL pour insérer les événements"""
        lines = [
            "-- Événements Valais pour MapEventAI",
            f"-- Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"-- {len(self.events)} événements",
            "",
            "-- D'abord, ajouter la colonne source_url si elle n'existe pas",
            "ALTER TABLE events ADD COLUMN IF NOT EXISTS source_url TEXT;",
            "",
        ]
        
        for event in self.events:
            title = event["title"].replace("'", "''")
            description = event["description"].replace("'", "''") if event.get("description") else ""
            location = event["location"].replace("'", "''")
            categories = json.dumps(event["categories"])
            source_url = event["source_url"].replace("'", "''")
            
            sql = f"""INSERT INTO events (title, description, location, latitude, longitude, date, time, end_date, categories, source_url, status, creator_id)
VALUES (
    '{title}',
    '{description}',
    '{location}',
    {event["latitude"]},
    {event["longitude"]},
    '{event["start_date"].strftime("%Y-%m-%d")}',
    {f"'{event['start_time']}'" if event.get("start_time") else "NULL"},
    {f"'{event['end_date'].strftime('%Y-%m-%d')}'" if event.get("end_date") else "NULL"},
    '{categories}'::jsonb,
    '{source_url}',
    'active',
    'system_scraper'
) ON CONFLICT DO NOTHING;
"""
            lines.append(sql)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        print(f"💾 SQL sauvegardé: {filename}")


def main():
    """Point d'entrée principal"""
    # Forcer l'encodage UTF-8 sur Windows
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    scraper = ValaisScraper()
    
    try:
        events = scraper.run()
        
        if events:
            # Sauvegarder en JSON et SQL
            scraper.save_to_json()
            scraper.save_to_sql()
            
            print("\n✅ Scraping terminé avec succès!")
            print("📁 Fichiers générés:")
            print("   - valais_events.json (pour inspection)")
            print("   - valais_events.sql (pour import en base)")
            print("\n📝 Pour importer en base:")
            print("   psql -h <host> -U <user> -d <database> -f valais_events.sql")
        else:
            print("\n⚠️ Aucun événement trouvé")
            
    except KeyboardInterrupt:
        print("\n\n⛔ Scraping interrompu par l'utilisateur")
        if scraper.events:
            print(f"💾 Sauvegarde des {len(scraper.events)} événements collectés...")
            scraper.save_to_json()
            scraper.save_to_sql()


if __name__ == "__main__":
    main()
