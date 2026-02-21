"""
Scraper d'événements Valais V3 - Sources réelles vérifiées
Collecte les informations factuelles publiques (dates, lieux, titres)

Usage: python valais_scraper_v3.py

Sources vérifiées février 2026:
- valais.ch/fr/evenements (Tourisme officiel)
- agenda.culturevalais.ch (Culture Valais)
- siontourisme.ch/fr/agenda (Sion Tourisme)
- sierre.ch/fr/calendrier-manifestations (Sierre)
- culturesion.ch/agenda (Culture Sion)
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
MAX_EVENTS = 300
START_DATE = datetime(2026, 3, 1)

# User-Agents rotatifs
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

# Sources d'événements réelles et vérifiées
SOURCES = [
    {
        "name": "Valais Tourisme",
        "url": "https://www.valais.ch/fr/evenements",
        "type": "json_api",
        "api_url": "https://www.valais.ch/api/tomas/events",
        "params": {"lang": "fr", "limit": 100}
    },
    {
        "name": "Culture Valais",
        "url": "https://agenda.culturevalais.ch/fr/agenda/evenements",
        "type": "html",
        "selectors": {
            "event_list": ".event-item, .agenda-item, article",
            "title": "h2, h3, .title, .event-title",
            "date": ".date, time, [datetime]",
            "location": ".location, .lieu, address",
            "link": "a[href]"
        }
    },
    {
        "name": "Sion Tourisme",
        "url": "https://siontourisme.ch/fr/agenda",
        "type": "html",
        "selectors": {
            "event_list": ".event, .agenda-item, article",
            "title": "h2, h3, .title",
            "date": ".date, time",
            "location": ".location, .lieu",
            "link": "a[href]"
        }
    },
    {
        "name": "Culture Sion",
        "url": "https://www.culturesion.ch/agenda",
        "type": "html",
        "selectors": {
            "event_list": ".event, .agenda-item, article, .post",
            "title": "h2, h3, .title, .entry-title",
            "date": ".date, time, .event-date",
            "location": ".location, .venue",
            "link": "a[href]"
        }
    },
    {
        "name": "Sierre Calendrier",
        "url": "https://www.sierre.ch/fr/calendrier-manifestations-1738.html",
        "type": "html",
        "selectors": {
            "event_list": "tr, .event, .manifestation",
            "title": "td:first-child, .title, a",
            "date": "td:nth-child(2), .date",
            "location": "td:nth-child(3), .lieu",
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
    "Loisirs & Animation > Défilés & Fêtes": ["fête", "carnaval", "défilé", "marché", "brocante", "noël", "foire", "combat de reines"],
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
    "champéry": (46.1750, 6.8694),
    "grimentz": (46.1789, 7.5756),
    "evolène": (46.1128, 7.4931),
    "saint-maurice": (46.2167, 7.0000),
    "fully": (46.1333, 7.1167),
    "conthey": (46.2167, 7.3000),
    "savièse": (46.2500, 7.3500),
    "ayent": (46.2833, 7.4167),
    "lens": (46.2833, 7.4333),
    "anzère": (46.2917, 7.4000),
    "ovronnaz": (46.1917, 7.1667),
    "saxon": (46.1500, 7.1667),
    "riddes": (46.1667, 7.2333),
    "val d'anniviers": (46.2167, 7.5667),
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
    """Géocode une adresse en utilisant les coordonnées connues"""
    location_lower = location.lower()
    
    for city_name, coords in VALAIS_CITIES.items():
        if city_name in location_lower:
            # Ajouter une légère variation pour éviter les empilements
            return (
                coords[0] + random.uniform(-0.003, 0.003),
                coords[1] + random.uniform(-0.003, 0.003)
            )
    
    # Fallback: centre du Valais
    return VALAIS_CITIES.get("valais")


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse une chaîne de date en datetime - recherche dans tout le texte"""
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    # Mois en français
    months_fr = {
        "janvier": 1, "février": 2, "mars": 3, "avril": 4,
        "mai": 5, "juin": 6, "juillet": 7, "août": 8,
        "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
        "jan": 1, "fév": 2, "mar": 3, "avr": 4, "jui": 6, "juil": 7,
        "aoû": 8, "sep": 9, "oct": 10, "nov": 11, "déc": 12
    }
    
    # Pattern: "Ve 06.02.2026" ou "Sa 15.03.2026" (format culture valais)
    match = re.search(r'[A-Za-z]{2}\s+(\d{1,2})\.(\d{1,2})\.(\d{4})', date_str)
    if match:
        day, month, year = match.groups()
        try:
            return datetime(int(year), int(month), int(day))
        except:
            pass
    
    # Pattern: "15.03.2026" ou "15/03/2026"
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
    
    # Extraire la ville
    city = "Valais"
    for city_name in VALAIS_CITIES.keys():
        if city_name.lower() in location.lower():
            city = city_name.title().replace("-", "-")
            break
    
    templates = [
        f"Événement à {city} : {title}. {original[:200]}..." if len(original) > 200 else f"Événement à {city} : {original}",
        f"Rendez-vous à {city} pour cet événement. {original[:200]}..." if len(original) > 200 else f"Rendez-vous à {city}. {original}",
        f"{city} accueille cet événement. {original[:200]}..." if len(original) > 200 else f"{city} accueille cet événement. {original}",
    ]
    
    return random.choice(templates)


class ValaisScraperV3:
    """Scraper V3 avec sources réelles vérifiées"""
    
    def __init__(self):
        self.session = requests.Session()
        self.events = []
        self.seen_hashes = set()
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Récupère et parse une page HTML"""
        try:
            print(f"  📡 Fetching: {url}")
            response = self.session.get(url, headers=get_headers(), timeout=30, verify=True)
            
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
            else:
                print(f"  ⚠️ HTTP {response.status_code}")
                return None
        except requests.exceptions.SSLError:
            print(f"  ⚠️ Erreur SSL - tentative sans vérification...")
            try:
                response = self.session.get(url, headers=get_headers(), timeout=30, verify=False)
                if response.status_code == 200:
                    return BeautifulSoup(response.text, "html.parser")
            except:
                pass
            return None
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
            return None
    
    def fetch_json_api(self, url: str, params: dict = None) -> Optional[dict]:
        """Récupère des données JSON depuis une API"""
        try:
            print(f"  📡 API: {url}")
            response = self.session.get(url, headers=get_headers(), params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"  ⚠️ API HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"  ❌ Erreur API: {e}")
            return None
    
    def event_hash(self, title: str, date: datetime, location: str) -> str:
        """Génère un hash unique pour détecter les doublons"""
        key = f"{title.lower().strip()[:50]}_{date.strftime('%Y-%m-%d') if date else 'nodate'}_{location.lower().strip()[:30]}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def add_event(self, event: Dict) -> bool:
        """Ajoute un événement s'il n'est pas un doublon et a les champs obligatoires"""
        # Vérifier les champs obligatoires
        if not event.get("title") or not event.get("source_url"):
            return False
        
        # Vérifier la date (doit être >= mars 2026)
        if event.get("start_date"):
            if event["start_date"] < START_DATE:
                return False
        
        # Vérifier les doublons
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
    
    def scrape_html_source(self, source: Dict) -> List[Dict]:
        """Scrape une source HTML"""
        print(f"\n🔍 Scraping: {source['name']}")
        
        soup = self.fetch_page(source["url"])
        if not soup:
            return []
        
        events = []
        selectors = source.get("selectors", {})
        
        # Trouver les éléments d'événements
        event_selector = selectors.get("event_list", "article, .event")
        items = soup.select(event_selector)
        
        print(f"  📋 {len(items)} éléments trouvés")
        
        for item in items[:50]:  # Max 50 par source
            try:
                # Titre
                title_elem = item.select_one(selectors.get("title", "h2, h3"))
                title = title_elem.get_text(strip=True) if title_elem else None
                
                if not title or len(title) < 5:
                    continue
                
                # Lien
                link_elem = item.select_one(selectors.get("link", "a[href]"))
                if link_elem and link_elem.get("href"):
                    href = link_elem.get("href")
                    if href.startswith("/"):
                        # URL relative
                        from urllib.parse import urljoin
                        source_url = urljoin(source["url"], href)
                    elif href.startswith("http"):
                        source_url = href
                    else:
                        source_url = source["url"]
                else:
                    source_url = source["url"]
                
                # Date
                date_elem = item.select_one(selectors.get("date", ".date, time"))
                date_str = ""
                if date_elem:
                    date_str = date_elem.get("datetime", "") or date_elem.get_text(strip=True)
                
                start_date = parse_date(date_str)
                
                # Location
                location_elem = item.select_one(selectors.get("location", ".location"))
                location = location_elem.get_text(strip=True) if location_elem else "Valais, Suisse"
                
                if not location or len(location) < 3:
                    location = "Valais, Suisse"
                
                # Géocoder
                coords = geocode_location(location)
                if not coords:
                    coords = VALAIS_CITIES["valais"]
                
                # Description (prendre le texte de l'élément ou du lien)
                full_text = item.get_text(strip=True)[:500] if item else title
                
                # Si pas de date trouvée, essayer de l'extraire du texte complet
                if not start_date:
                    start_date = parse_date(full_text)
                
                description = rewrite_description(full_text, title, location)
                
                # Catégories
                categories = find_category(title, description)
                
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
                    "organizer_email": None,  # À extraire de la page de détail
                    "organizer_name": source["name"]
                }
                
                if self.add_event(event):
                    date_str = start_date.strftime('%d.%m.%Y') if start_date else "Date inconnue"
                    print(f"  ✅ {title[:40]}... ({date_str})")
                
                time.sleep(1)  # Court délai entre les items
                
            except Exception as e:
                print(f"  ⚠️ Erreur parsing: {e}")
                continue
        
        return events
    
    def run(self):
        """Lance le scraping complet"""
        print("=" * 60)
        print("🗺️ SCRAPER ÉVÉNEMENTS VALAIS V3 - MapEventAI")
        print("=" * 60)
        print(f"📅 Période: Mars 2026 et après")
        print(f"🎯 Objectif: {MAX_EVENTS} événements")
        print(f"⏱️ Rate limit: {RATE_LIMIT_SECONDS} secondes entre sources")
        print("=" * 60)
        
        for source in SOURCES:
            if len(self.events) >= MAX_EVENTS:
                break
            
            try:
                if source.get("type") == "json_api":
                    # Scraper API JSON
                    data = self.fetch_json_api(
                        source.get("api_url", source["url"]),
                        source.get("params")
                    )
                    if data:
                        print(f"  📊 API response: {type(data)}")
                        # Traiter selon la structure de l'API
                else:
                    # Scraper HTML
                    self.scrape_html_source(source)
                
            except Exception as e:
                print(f"  ❌ Erreur source {source['name']}: {e}")
            
            # Pause entre les sources
            print(f"  ⏳ Pause {RATE_LIMIT_SECONDS} secondes...")
            time.sleep(RATE_LIMIT_SECONDS)
        
        print("\n" + "=" * 60)
        print(f"📊 RÉSULTAT: {len(self.events)} événements collectés")
        print("=" * 60)
        
        return self.events
    
    def save_to_json(self, filename: str = "valais_events_v3.json"):
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
    
    def save_to_sql(self, filename: str = "valais_events_v3.sql"):
        """Génère un fichier SQL pour import via l'API batch"""
        lines = [
            "-- Événements Valais V3 pour MapEventAI",
            f"-- Généré le {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"-- {len(self.events)} événements",
            "",
            "-- Pour importer, utilisez l'API /api/events/scraped/batch",
            "-- ou exécutez directement ce SQL",
            "",
            "-- Ajouter les colonnes si elles n'existent pas",
            "ALTER TABLE events ADD COLUMN IF NOT EXISTS source_url TEXT;",
            "ALTER TABLE events ADD COLUMN IF NOT EXISTS organizer_name VARCHAR(255);",
            "ALTER TABLE events ADD COLUMN IF NOT EXISTS organizer_email VARCHAR(255);",
            "ALTER TABLE events ADD COLUMN IF NOT EXISTS validation_status VARCHAR(50) DEFAULT 'pending';",
            "ALTER TABLE events ADD COLUMN IF NOT EXISTS validation_token VARCHAR(255);",
            "ALTER TABLE events ADD COLUMN IF NOT EXISTS scraped_at TIMESTAMP;",
            "",
            "-- Créer l'utilisateur système scraper",
            "INSERT INTO users (id, email, username) VALUES ('system_scraper', 'scraper@mapevent.world', 'MapEvent Scraper') ON CONFLICT DO NOTHING;",
            "",
        ]
        
        for event in self.events:
            title = event["title"].replace("'", "''")
            description = (event.get("description") or "").replace("'", "''")
            location = event["location"].replace("'", "''")
            categories = json.dumps(event.get("categories", []))
            source_url = event["source_url"].replace("'", "''")
            organizer_name = (event.get("organizer_name") or "").replace("'", "''")
            
            date_str = event["start_date"].strftime("%Y-%m-%d") if event.get("start_date") else "NULL"
            end_date_str = event["end_date"].strftime("%Y-%m-%d") if event.get("end_date") else "NULL"
            
            sql = f"""INSERT INTO events (title, description, location, latitude, longitude, date, end_date, categories, source_url, organizer_name, validation_status, status, creator_id, scraped_at)
VALUES (
    '{title}',
    '{description}',
    '{location}',
    {event["latitude"]},
    {event["longitude"]},
    {f"'{date_str}'" if date_str != "NULL" else "NULL"},
    {f"'{end_date_str}'" if end_date_str != "NULL" else "NULL"},
    '{categories}'::jsonb,
    '{source_url}',
    '{organizer_name}',
    'validated',
    'active',
    'system_scraper',
    CURRENT_TIMESTAMP
) ON CONFLICT DO NOTHING;
"""
            lines.append(sql)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        
        print(f"💾 SQL sauvegardé: {filename}")


def main():
    print("\n🚀 Démarrage du scraper V3...")
    
    scraper = ValaisScraperV3()
    
    try:
        events = scraper.run()
        
        if events:
            scraper.save_to_json()
            scraper.save_to_sql()
            
            print("\n✅ Scraping terminé!")
            print("\n📁 Fichiers générés:")
            print("   - valais_events_v3.json")
            print("   - valais_events_v3.sql")
            print("\n📝 Pour importer via l'API:")
            print("   POST /api/events/scraped/batch")
            print("   Body: { \"events\": [...], \"send_emails\": true }")
        else:
            print("\n⚠️ Aucun événement trouvé")
            print("   Les sites peuvent avoir changé de structure.")
            print("   Vérifiez manuellement les URLs.")
            
    except KeyboardInterrupt:
        print("\n\n⛔ Scraping interrompu")
        if scraper.events:
            print(f"💾 Sauvegarde des {len(scraper.events)} événements collectés...")
            scraper.save_to_json()
            scraper.save_to_sql()


if __name__ == "__main__":
    main()
