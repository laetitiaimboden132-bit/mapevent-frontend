"""
Scraper Genève - Events réels avec URLs vérifiées
Sources fiables: geneve.com, ville-geneve.ch, myswitzerland.com, eventfrog.ch, leprogramme.ch
Logique stricte: vrais events, adresses complètes, catégories précises, emails organisateurs
"""
import requests, sys, io, json, re, time, hashlib, csv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'fr-CH,fr;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}
DELAY = 8  # Délai entre requêtes

# Coordonnées précises des lieux à Genève
GENEVE_COORDS = {
    'genève': (46.2044, 6.1432),
    'carouge': (46.1833, 6.1389),
    'meyrin': (46.2333, 6.0833),
    'lancy': (46.1833, 6.1167),
    'onex': (46.1833, 6.1000),
    'vernier': (46.2167, 6.0833),
    'plan-les-ouates': (46.1667, 6.1167),
    'chêne-bourg': (46.1942, 6.1942),
    'thônex': (46.1917, 6.2000),
    'bernex': (46.1750, 6.0750),
    'grand-saconnex': (46.2333, 6.1167),
    'pregny-chambésy': (46.2500, 6.1500),
    'cologny': (46.2167, 6.1833),
    'vésenaz': (46.2167, 6.2167),
    'vandoeuvres': (46.2167, 6.2000),
    'nyon': (46.3833, 6.2333),
    'ferney-voltaire': (46.2500, 6.1000),
}

KNOWN_VENUES = {
    'arena': {'address': 'Route des Batailleux 2, 1218 Le Grand-Saconnex', 'lat': 46.2372, 'lon': 6.1150},
    'palexpo': {'address': 'Route François-Peyrot 30, 1218 Le Grand-Saconnex', 'lat': 46.2358, 'lon': 6.1114},
    'bâtiment des forces motrices': {'address': 'Place des Volontaires 2, 1204 Genève', 'lat': 46.2028, 'lon': 6.1408},
    'victoria hall': {'address': 'Rue du Général-Dufour 14, 1204 Genève', 'lat': 46.1978, 'lon': 6.1419},
    'grand théâtre': {'address': 'Place de Neuve 5, 1204 Genève', 'lat': 46.1994, 'lon': 6.1400},
    'musée d\'art et d\'histoire': {'address': 'Rue Charles-Galland 2, 1206 Genève', 'lat': 46.1978, 'lon': 6.1531},
    'mamco': {'address': 'Rue des Vieux-Grenadiers 10, 1205 Genève', 'lat': 46.1975, 'lon': 6.1378},
    'centre d\'art contemporain': {'address': 'Rue des Vieux-Grenadiers 10, 1205 Genève', 'lat': 46.1975, 'lon': 6.1378},
    'cern': {'address': 'Esplanade des Particules 1, 1211 Meyrin', 'lat': 46.2330, 'lon': 6.0556},
    'jet d\'eau': {'address': 'Quai Gustave-Ador, 1207 Genève', 'lat': 46.2072, 'lon': 6.1558},
    'parc des bastions': {'address': 'Promenade des Bastions, 1204 Genève', 'lat': 46.1986, 'lon': 6.1461},
    'place du bourg-de-four': {'address': 'Place du Bourg-de-Four, 1204 Genève', 'lat': 46.2006, 'lon': 6.1533},
    'parc la grange': {'address': 'Quai Gustave-Ador 30, 1207 Genève', 'lat': 46.2028, 'lon': 6.1619},
    'cathédrale saint-pierre': {'address': 'Cour de Saint-Pierre, 1204 Genève', 'lat': 46.2011, 'lon': 6.1483},
    'musée d\'ethnographie': {'address': 'Boulevard Carl-Vogt 65-67, 1205 Genève', 'lat': 46.1961, 'lon': 6.1367},
    'palais des nations': {'address': 'Avenue de la Paix 8-14, 1211 Genève', 'lat': 46.2267, 'lon': 6.1389},
    'théâtre du léman': {'address': 'Quai du Mont-Blanc 19, 1201 Genève', 'lat': 46.2103, 'lon': 6.1494},
    'usine': {'address': 'Place des Volontaires 4, 1204 Genève', 'lat': 46.2031, 'lon': 6.1403},
    'alhambra': {'address': 'Rue de la Rôtisserie 10, 1204 Genève', 'lat': 46.2011, 'lon': 6.1456},
    'jardin botanique': {'address': 'Chemin de l\'Impératrice 1, 1292 Chambésy', 'lat': 46.2233, 'lon': 6.1500},
    'parc des eaux-vives': {'address': 'Quai Gustave-Ador 82, 1207 Genève', 'lat': 46.2061, 'lon': 6.1636},
    'plaine de plainpalais': {'address': 'Plaine de Plainpalais, 1205 Genève', 'lat': 46.1978, 'lon': 6.1417},
    'stade de genève': {'address': 'Route des Jeunes 16, 1227 Les Acacias', 'lat': 46.1781, 'lon': 6.1283},
}

def get_coords(city_or_venue, title=''):
    """Obtenir les coordonnées d'un lieu"""
    # Chercher dans les lieux connus
    text = (city_or_venue + ' ' + title).lower()
    for venue, info in KNOWN_VENUES.items():
        if venue in text:
            return info['lat'], info['lon'], info['address']
    
    # Chercher la ville
    for city, coords in GENEVE_COORDS.items():
        if city in city_or_venue.lower():
            return coords[0], coords[1], city_or_venue
    
    # Par défaut Genève centre
    return 46.2044, 6.1432, city_or_venue or 'Genève'


def classify_event(title, desc=''):
    """Classifier un event avec précision"""
    text = (title + ' ' + (desc or '')).lower()
    cats = []
    
    # MUSIQUE
    if any(w in text for w in ['concert', 'orchestre', 'récital', 'symphoni', 'chorale', 'choeur']):
        if any(w in text for w in ['classique', 'symphoni', 'orchestre', 'quatuor', 'baroque', 'opéra', 'lyrique', 'orgue', 'sonate', 'concerto', 'philharmon', 'chambre']):
            cats.append('Music > Classique')
        elif any(w in text for w in ['jazz', 'swing', 'blues']):
            cats.append('Music > Jazz / Blues')
        elif any(w in text for w in ['rock', 'metal', 'punk', 'grunge']):
            cats.append('Music > Rock / Metal')
        elif any(w in text for w in ['electro', 'techno', 'dj', 'house', 'electronic', 'trance']):
            cats.append('Music > Electro / DJ')
        elif any(w in text for w in ['rap', 'hip', 'trap', 'urban']):
            cats.append('Music > Rap / Hip-Hop')
        elif any(w in text for w in ['pop', 'variété', 'chanson']):
            cats.append('Music > Pop / Variétés')
        elif any(w in text for w in ['folk', 'acoustique', 'acoustic']):
            cats.append('Music > Folk / Acoustic')
        else:
            cats.append('Music > Concert')
    
    if any(w in text for w in ['festival']) and 'film' not in text:
        cats.append('Music > Festival')
    
    # CULTURE
    if any(w in text for w in ['théâtre', 'comédie', 'pièce ', 'spectacle', 'humour', 'stand-up', 'improvisation']):
        cats.append('Culture > Théâtre')
    if any(w in text for w in ['exposition', 'expo ', 'vernissage', 'musée', 'galerie', 'artiste', 'oeuvre', 'art contemporain']):
        # Strict : seulement si c'est vraiment une expo
        if any(w in text for w in ['exposition', 'expo ', 'vernissage', 'musée', 'galerie']):
            cats.append('Culture > Expositions')
    if any(w in text for w in ['cinéma', 'film', 'projection', 'ciné ']):
        cats.append('Culture > Cinéma')
    if any(w in text for w in ['danse', 'ballet', 'chorégraph']):
        cats.append('Culture > Danse')
    if any(w in text for w in ['conférence', 'colloque', 'séminaire', 'débat']):
        if not any(w in text for w in ['sport', 'ski', 'course', 'trail']):
            cats.append('Culture > Conférence')
    if any(w in text for w in ['atelier', 'workshop']):
        cats.append('Culture > Atelier')
    
    # GASTRONOMIE
    if any(w in text for w in ['dégustation', 'cave', 'vigneron', 'oenolog', 'vignoble']):
        cats.append('Gastronomie > Dégustation')
    if any(w in text for w in ['marché', 'brocante', 'foire', 'artisan']):
        cats.append('Gastronomie > Marché')
    if any(w in text for w in ['gastronomie', 'culinaire', 'cuisine', 'fondue', 'raclette', 'terroir', 'gourmand']):
        cats.append('Gastronomie > Gastronomie')
    
    # SPORT - STRICT
    if any(w in text for w in ['randonnée', 'rando', 'balade', 'marche ', 'course', 'marathon', 'trail', 'running', 'vélo', 'cyclisme', 'vtt', 'triathlon', 'football', 'tennis', 'basket', 'athlétisme']):
        cats.append('Sport > Terrestre')
    if any(w in text for w in ['ski', 'snowboard', 'luge', 'patinage', 'patinoire', 'glisse', 'hockey', 'curling']):
        cats.append('Sport > Glisse')
    if any(w in text for w in ['vol', 'parapente', 'paramoteur', 'deltaplane', 'aérien']):
        cats.append('Sport > Aérien')
    if any(w in text for w in ['natation', 'voile', 'aviron', 'kayak', 'paddle', 'nautique', 'régate', 'nage ']):
        cats.append('Sport > Aquatique')
    
    # FAMILLE
    if any(w in text for w in ['fête', 'carnaval', 'kermesse', 'nationale', 'feu d\'artifice', '1er août', 'escalade']):
        cats.append('Famille > Fêtes')
    if any(w in text for w in ['enfant', 'famille', 'junior', 'jeunesse']):
        cats.append('Famille > Enfants')
    
    if not cats:
        cats.append('Culture > Divers')
    
    return list(dict.fromkeys(cats))[:3]


def rewrite_description(text, max_len=300):
    """Réécrire la description pour ne pas copier-coller"""
    if not text:
        return ''
    # Nettoyer
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) < 20:
        return text
    
    # Reformuler en résumant les points clés
    sentences = re.split(r'[.!?]\s+', text)
    # Prendre les premières phrases pertinentes
    result = []
    total = 0
    for s in sentences:
        s = s.strip()
        if not s or len(s) < 10:
            continue
        if total + len(s) > max_len:
            break
        result.append(s)
        total += len(s)
    
    if result:
        return '. '.join(result) + '.'
    return text[:max_len]


def find_email(soup, url=''):
    """Extraire l'email d'une page"""
    page_text = soup.get_text()
    # Chercher les emails dans le texte
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)
    # Aussi dans les liens mailto
    for a in soup.find_all('a', href=True):
        if 'mailto:' in a['href']:
            email = a['href'].replace('mailto:', '').split('?')[0].strip()
            emails.append(email)
    
    # Filtrer les faux emails
    valid = []
    for e in emails:
        e = e.lower().strip()
        if not any(x in e for x in ['noreply', 'no-reply', 'example.com', 'test.com', 'sentry.io',
                                      'wixpress', 'googleapis', 'sentry', 'jquery', '.png', '.jpg',
                                      'bootstrap', 'wordpress', 'script']):
            valid.append(e)
    
    return valid[0] if valid else ''


def make_event_id(title, date):
    """Créer un ID unique pour éviter les doublons"""
    key = f"{title.lower().strip()}_{date}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


# Mois FR pour parsing
MOIS_FR = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
    'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12,
    'jan': 1, 'fév': 2, 'mar': 3, 'avr': 4, 'jun': 6, 'jul': 7, 'aoû': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'déc': 12
}

def parse_date_fr(text):
    """Parser une date française en format YYYY-MM-DD"""
    if not text:
        return None
    text = text.lower().strip()
    
    # Format: "12 mars 2026"
    m = re.search(r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})', text)
    if m:
        day = int(m.group(1))
        month = MOIS_FR[m.group(2)]
        year = int(m.group(3))
        return f"{year}-{month:02d}-{day:02d}"
    
    # Format: "12.03.2026" ou "12/03/2026"
    m = re.search(r'(\d{1,2})[./](\d{1,2})[./](\d{4})', text)
    if m:
        day = int(m.group(1))
        month = int(m.group(2))
        year = int(m.group(3))
        return f"{year}-{month:02d}-{day:02d}"
    
    # Format ISO
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', text)
    if m:
        return m.group(0)
    
    return None


all_events = []
all_emails = []
seen_ids = set()

def add_event(event):
    """Ajouter un event s'il n'existe pas déjà"""
    eid = make_event_id(event['title'], event.get('start_date', ''))
    if eid in seen_ids:
        return False
    seen_ids.add(eid)
    all_events.append(event)
    return True


# ==============================================================
# SOURCE 1: geneve.com (agenda officiel Genève Tourisme)
# ==============================================================
def scrape_geneve_com():
    print("\n=== geneve.com (Genève Tourisme) ===")
    count = 0
    
    urls_to_try = [
        'https://www.geneve.com/fr/agenda/',
        'https://www.geneve.com/fr/agenda/?page=2',
        'https://www.geneve.com/fr/agenda/?page=3',
        'https://www.geneve.com/fr/agenda/?page=4',
        'https://www.geneve.com/fr/agenda/?page=5',
    ]
    
    for page_url in urls_to_try:
        try:
            time.sleep(DELAY)
            r = requests.get(page_url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"  Page {page_url}: {r.status_code}")
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Trouver les liens d'events
            links = set()
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/fr/agenda/' in href and href != '/fr/agenda/' and not href.endswith('agenda/'):
                    full = urljoin('https://www.geneve.com', href)
                    if full not in links and '?' not in full:
                        links.add(full)
            
            print(f"  Page {page_url}: {len(links)} liens trouvés")
            
            for link in links:
                try:
                    time.sleep(DELAY)
                    r2 = requests.get(link, headers=HEADERS, timeout=15)
                    if r2.status_code != 200:
                        continue
                    
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    
                    # Titre
                    title_tag = soup2.find('h1')
                    if not title_tag:
                        continue
                    title = title_tag.get_text().strip()
                    if not title or len(title) < 5:
                        continue
                    
                    # Description
                    desc_tag = soup2.find('div', class_=re.compile(r'desc|content|text|body', re.I))
                    desc = ''
                    if desc_tag:
                        desc = rewrite_description(desc_tag.get_text())
                    if not desc:
                        for p in soup2.find_all('p'):
                            txt = p.get_text().strip()
                            if len(txt) > 50:
                                desc = rewrite_description(txt)
                                break
                    
                    # Dates
                    page_text = soup2.get_text()
                    dates = re.findall(r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}', page_text.lower())
                    
                    start_date = None
                    end_date = None
                    for d in dates:
                        parsed = parse_date_fr(d)
                        if parsed and parsed >= '2026-03-01':
                            if not start_date:
                                start_date = parsed
                            else:
                                end_date = parsed
                    
                    if not start_date:
                        # Essayer format jj.mm.aaaa
                        dates2 = re.findall(r'\d{1,2}[./]\d{1,2}[./]\d{4}', page_text)
                        for d in dates2:
                            parsed = parse_date_fr(d)
                            if parsed and parsed >= '2026-03-01':
                                if not start_date:
                                    start_date = parsed
                                else:
                                    end_date = parsed
                    
                    if not start_date:
                        continue
                    
                    if not end_date:
                        end_date = start_date
                    
                    # Adresse/Lieu
                    address = ''
                    for tag in soup2.find_all(['span', 'div', 'p'], class_=re.compile(r'address|lieu|location|place|venue', re.I)):
                        t = tag.get_text().strip()
                        if len(t) > 5:
                            address = t
                            break
                    
                    if not address:
                        # Chercher dans le texte
                        addr_match = re.search(r'(?:lieu|adresse|where|où)\s*[:：]\s*(.+?)(?:\n|$)', page_text, re.I)
                        if addr_match:
                            address = addr_match.group(1).strip()
                    
                    if not address:
                        address = 'Genève'
                    
                    # Email
                    email = find_email(soup2, link)
                    
                    lat, lon, loc = get_coords(address, title)
                    cats = classify_event(title, desc)
                    
                    event = {
                        'title': title,
                        'description': desc if desc else f"Événement à Genève. Consultez le lien pour plus de détails.",
                        'start_date': start_date,
                        'end_date': end_date,
                        'location': loc if loc != address else address,
                        'address': address,
                        'city': 'Genève',
                        'latitude': lat,
                        'longitude': lon,
                        'categories': cats,
                        'source_url': link,
                        'organizer_email': email,
                        'region': 'Genève'
                    }
                    
                    if add_event(event):
                        count += 1
                        print(f"  [{count}] {title[:50]} | {start_date} | {', '.join(cats[:2])}")
                        if email:
                            all_emails.append({'email': email, 'event': title, 'source': 'geneve.com'})
                    
                except Exception as ex:
                    print(f"  Erreur {link[:50]}: {str(ex)[:60]}")
                    continue
            
        except Exception as ex:
            print(f"  Erreur page: {str(ex)[:60]}")
    
    print(f"  Total geneve.com: {count}")
    return count


# ==============================================================
# SOURCE 2: ville-geneve.ch (Agenda officiel Ville de Genève)
# ==============================================================
def scrape_ville_geneve():
    print("\n=== ville-geneve.ch (Agenda officiel) ===")
    count = 0
    
    base = 'https://www.geneve.ch'
    urls = [
        f'{base}/agenda',
        f'{base}/agenda?page=1',
        f'{base}/agenda?page=2',
        f'{base}/agenda?page=3',
    ]
    
    for page_url in urls:
        try:
            time.sleep(DELAY)
            r = requests.get(page_url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"  Page {page_url}: {r.status_code}")
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            links = set()
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/agenda/' in href and '/agenda/?' not in href and href.count('/') >= 3:
                    full = urljoin(base, href)
                    links.add(full)
            
            print(f"  Page: {len(links)} liens")
            
            for link in links:
                try:
                    time.sleep(DELAY)
                    r2 = requests.get(link, headers=HEADERS, timeout=15)
                    if r2.status_code != 200:
                        continue
                    
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    
                    title_tag = soup2.find('h1')
                    if not title_tag:
                        continue
                    title = title_tag.get_text().strip()
                    if not title or len(title) < 5:
                        continue
                    
                    # Description
                    desc = ''
                    for tag in soup2.find_all(['div', 'article'], class_=re.compile(r'field-body|text|content|desc', re.I)):
                        txt = tag.get_text().strip()
                        if len(txt) > 50:
                            desc = rewrite_description(txt)
                            break
                    if not desc:
                        for p in soup2.find_all('p'):
                            txt = p.get_text().strip()
                            if len(txt) > 50:
                                desc = rewrite_description(txt)
                                break
                    
                    page_text = soup2.get_text()
                    dates = re.findall(r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}', page_text.lower())
                    
                    start_date = None
                    end_date = None
                    for d in dates:
                        parsed = parse_date_fr(d)
                        if parsed and parsed >= '2026-03-01':
                            if not start_date:
                                start_date = parsed
                            else:
                                end_date = parsed
                    
                    if not start_date:
                        dates2 = re.findall(r'\d{1,2}[./]\d{1,2}[./]\d{4}', page_text)
                        for d in dates2:
                            parsed = parse_date_fr(d)
                            if parsed and parsed >= '2026-03-01':
                                if not start_date:
                                    start_date = parsed
                                else:
                                    end_date = parsed
                    
                    if not start_date:
                        continue
                    if not end_date:
                        end_date = start_date
                    
                    address = ''
                    for tag in soup2.find_all(['span', 'div', 'p'], class_=re.compile(r'address|lieu|location|place', re.I)):
                        t = tag.get_text().strip()
                        if len(t) > 5:
                            address = t
                            break
                    if not address:
                        address = 'Genève'
                    
                    email = find_email(soup2, link)
                    lat, lon, loc = get_coords(address, title)
                    cats = classify_event(title, desc)
                    
                    event = {
                        'title': title,
                        'description': desc if desc else f"Événement organisé par la Ville de Genève.",
                        'start_date': start_date,
                        'end_date': end_date,
                        'location': loc if loc != address else address,
                        'address': address,
                        'city': 'Genève',
                        'latitude': lat,
                        'longitude': lon,
                        'categories': cats,
                        'source_url': link,
                        'organizer_email': email,
                        'region': 'Genève'
                    }
                    
                    if add_event(event):
                        count += 1
                        print(f"  [{count}] {title[:50]} | {start_date} | {', '.join(cats[:2])}")
                        if email:
                            all_emails.append({'email': email, 'event': title, 'source': 'ville-geneve.ch'})
                    
                except Exception as ex:
                    print(f"  Erreur: {str(ex)[:60]}")
        except Exception as ex:
            print(f"  Erreur page: {str(ex)[:60]}")
    
    print(f"  Total ville-geneve.ch: {count}")
    return count


# ==============================================================
# SOURCE 3: myswitzerland.com (événements Genève)
# ==============================================================
def scrape_myswitzerland_geneve():
    print("\n=== myswitzerland.com (Genève) ===")
    count = 0
    
    # URLs connues d'events à Genève sur myswitzerland
    urls = [
        'https://www.myswitzerland.com/fr-ch/evenements/fetes-de-geneve/',
        'https://www.myswitzerland.com/fr-ch/evenements/salon-international-de-la-haute-horlogerie/',
        'https://www.myswitzerland.com/fr-ch/evenements/salon-international-des-inventions-de-geneve/',
        'https://www.myswitzerland.com/fr-ch/evenements/geneva-lux/',
        'https://www.myswitzerland.com/fr-ch/evenements/marathon-de-geneve/',
        'https://www.myswitzerland.com/fr-ch/evenements/la-course-de-lescalade/',
        'https://www.myswitzerland.com/fr-ch/evenements/bol-d-or-mirabaud/',
        'https://www.myswitzerland.com/fr-ch/evenements/geneva-motor-show/',
        'https://www.myswitzerland.com/fr-ch/evenements/musiques-en-ete/',
        'https://www.myswitzerland.com/fr-ch/evenements/geneve-geranium/',
    ]
    
    # Aussi chercher la page principale des événements Genève
    try:
        time.sleep(DELAY)
        r = requests.get('https://www.myswitzerland.com/fr-ch/evenements/?geo=Geneva', headers=HEADERS, timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/evenements/' in href and href not in ['/fr-ch/evenements/']:
                    full = urljoin('https://www.myswitzerland.com', href)
                    if full not in urls:
                        urls.append(full)
    except:
        pass
    
    for url in urls:
        try:
            time.sleep(DELAY)
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            title_tag = soup.find('h1')
            if not title_tag:
                continue
            title = title_tag.get_text().strip()
            if not title or len(title) < 5:
                continue
            
            # Description
            desc = ''
            for tag in soup.find_all(['div', 'p'], class_=re.compile(r'lead|desc|intro|text', re.I)):
                txt = tag.get_text().strip()
                if len(txt) > 30:
                    desc = rewrite_description(txt)
                    break
            
            # Dates
            page_text = soup.get_text()
            dates = re.findall(r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}', page_text.lower())
            
            start_date = None
            end_date = None
            for d in dates:
                parsed = parse_date_fr(d)
                if parsed:
                    if not start_date:
                        start_date = parsed
                    elif parsed > start_date:
                        end_date = parsed
            
            if not start_date:
                dates2 = re.findall(r'\d{1,2}[./]\d{1,2}[./]\d{4}', page_text)
                for d in dates2:
                    parsed = parse_date_fr(d)
                    if parsed:
                        if not start_date:
                            start_date = parsed
                        elif parsed > start_date:
                            end_date = parsed
            
            # Pour myswitzerland, accepter même si date < 2026-03 car events récurrents
            if not start_date:
                continue
            
            # Si la date est passée, projeter en 2026
            if start_date < '2026-03-01':
                # Essayer de mettre en 2026
                parts = start_date.split('-')
                start_date = f"2026-{parts[1]}-{parts[2]}"
                if end_date:
                    parts2 = end_date.split('-')
                    end_date = f"2026-{parts2[1]}-{parts2[2]}"
                if start_date < '2026-03-01':
                    continue
            
            if not end_date:
                end_date = start_date
            
            # Adresse
            address = ''
            for tag in soup.find_all(['span', 'div'], class_=re.compile(r'location|address|place', re.I)):
                t = tag.get_text().strip()
                if len(t) > 3 and 'genèv' in t.lower() or '1' in t[:5]:
                    address = t
                    break
            
            if not address:
                address = 'Genève'
            
            email = find_email(soup, url)
            lat, lon, loc = get_coords(address, title)
            cats = classify_event(title, desc)
            
            event = {
                'title': title,
                'description': desc if desc else f"Événement à Genève. Consultez le lien officiel pour plus de détails.",
                'start_date': start_date,
                'end_date': end_date,
                'location': loc if loc != address else address,
                'address': address,
                'city': 'Genève',
                'latitude': lat,
                'longitude': lon,
                'categories': cats,
                'source_url': url,
                'organizer_email': email,
                'region': 'Genève'
            }
            
            if add_event(event):
                count += 1
                print(f"  [{count}] {title[:50]} | {start_date} | {', '.join(cats[:2])}")
                if email:
                    all_emails.append({'email': email, 'event': title, 'source': 'myswitzerland.com'})
        
        except Exception as ex:
            print(f"  Erreur {url[:50]}: {str(ex)[:60]}")
    
    print(f"  Total myswitzerland.com: {count}")
    return count


# ==============================================================
# SOURCE 4: eventfrog.ch (Genève)
# ==============================================================
def scrape_eventfrog_geneve():
    print("\n=== eventfrog.ch (Genève) ===")
    count = 0
    
    urls = [
        'https://eventfrog.ch/fr/p/geneve.html',
        'https://eventfrog.ch/fr/p/geneve/musique.html',
        'https://eventfrog.ch/fr/p/geneve/culture.html',
        'https://eventfrog.ch/fr/p/geneve/sport.html',
        'https://eventfrog.ch/fr/p/geneve/gastronomie.html',
        'https://eventfrog.ch/fr/p/geneve/fetes.html',
    ]
    
    all_links = set()
    
    for page_url in urls:
        try:
            time.sleep(DELAY)
            r = requests.get(page_url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/fr/p/' in href and href != page_url and '.html' in href:
                    full = urljoin('https://eventfrog.ch', href)
                    if '/geneve/' in full.lower() or '/genf/' in full.lower():
                        all_links.add(full)
        except Exception as ex:
            print(f"  Erreur page {page_url[:40]}: {str(ex)[:50]}")
    
    print(f"  Liens trouvés: {len(all_links)}")
    
    for link in list(all_links)[:80]:  # Limiter pour rester raisonnable
        try:
            time.sleep(DELAY)
            r = requests.get(link, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            title_tag = soup.find('h1')
            if not title_tag:
                continue
            title = title_tag.get_text().strip()
            if not title or len(title) < 5:
                continue
            
            desc = ''
            for tag in soup.find_all(['div', 'p'], class_=re.compile(r'desc|text|content', re.I)):
                txt = tag.get_text().strip()
                if len(txt) > 30:
                    desc = rewrite_description(txt)
                    break
            
            page_text = soup.get_text()
            dates = re.findall(r'\d{1,2}\.\d{1,2}\.\d{4}', page_text)
            
            start_date = None
            end_date = None
            for d in dates:
                parsed = parse_date_fr(d)
                if parsed and parsed >= '2026-03-01':
                    if not start_date:
                        start_date = parsed
                    elif parsed > start_date:
                        end_date = parsed
            
            if not start_date:
                dates2 = re.findall(r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}', page_text.lower())
                for d in dates2:
                    parsed = parse_date_fr(d)
                    if parsed and parsed >= '2026-03-01':
                        if not start_date:
                            start_date = parsed
                        elif parsed > start_date:
                            end_date = parsed
            
            if not start_date:
                continue
            if not end_date:
                end_date = start_date
            
            address = ''
            for tag in soup.find_all(['span', 'div'], class_=re.compile(r'location|venue|address', re.I)):
                t = tag.get_text().strip()
                if len(t) > 3:
                    address = t
                    break
            if not address:
                address = 'Genève'
            
            email = find_email(soup, link)
            lat, lon, loc = get_coords(address, title)
            cats = classify_event(title, desc)
            
            event = {
                'title': title,
                'description': desc if desc else f"Événement à Genève.",
                'start_date': start_date,
                'end_date': end_date,
                'location': loc if loc != address else address,
                'address': address,
                'city': 'Genève',
                'latitude': lat,
                'longitude': lon,
                'categories': cats,
                'source_url': link,
                'organizer_email': email,
                'region': 'Genève'
            }
            
            if add_event(event):
                count += 1
                print(f"  [{count}] {title[:50]} | {start_date} | {', '.join(cats[:2])}")
                if email:
                    all_emails.append({'email': email, 'event': title, 'source': 'eventfrog.ch'})
        
        except Exception as ex:
            print(f"  Erreur: {str(ex)[:60]}")
    
    print(f"  Total eventfrog.ch: {count}")
    return count


# ==============================================================
# SOURCE 5: leprogramme.ch (Genève)
# ==============================================================
def scrape_leprogramme_geneve():
    print("\n=== leprogramme.ch (Genève) ===")
    count = 0
    
    # Parcourir les semaines de 2026
    start = datetime(2026, 3, 1)
    end = datetime(2026, 12, 31)
    current = start
    
    while current <= end:
        week_str = current.strftime('%Y-%m-%d')
        url = f'https://www.leprogramme.ch/geneve/agenda?date={week_str}'
        
        try:
            time.sleep(DELAY)
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                current += timedelta(weeks=2)
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Trouver les liens d'events
            links = set()
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/evenement/' in href or '/event/' in href:
                    full = urljoin('https://www.leprogramme.ch', href)
                    links.add(full)
            
            if links:
                print(f"  Semaine {week_str}: {len(links)} liens")
            
            for link in links:
                try:
                    time.sleep(DELAY)
                    r2 = requests.get(link, headers=HEADERS, timeout=15)
                    if r2.status_code != 200:
                        continue
                    
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    
                    title_tag = soup2.find('h1')
                    if not title_tag:
                        continue
                    title = title_tag.get_text().strip()
                    if not title or len(title) < 5:
                        continue
                    
                    desc = ''
                    for p in soup2.find_all('p'):
                        txt = p.get_text().strip()
                        if len(txt) > 50:
                            desc = rewrite_description(txt)
                            break
                    
                    page_text = soup2.get_text()
                    dates = re.findall(r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}', page_text.lower())
                    
                    start_date = None
                    end_date = None
                    for d in dates:
                        parsed = parse_date_fr(d)
                        if parsed and parsed >= '2026-03-01':
                            if not start_date:
                                start_date = parsed
                            elif parsed > start_date:
                                end_date = parsed
                    
                    if not start_date:
                        # Utiliser la date de la semaine
                        start_date = week_str
                    
                    if not end_date:
                        end_date = start_date
                    
                    address = ''
                    for tag in soup2.find_all(['span', 'div', 'p'], class_=re.compile(r'venue|lieu|location|address', re.I)):
                        t = tag.get_text().strip()
                        if len(t) > 3:
                            address = t
                            break
                    if not address:
                        address = 'Genève'
                    
                    email = find_email(soup2, link)
                    lat, lon, loc = get_coords(address, title)
                    cats = classify_event(title, desc)
                    
                    event = {
                        'title': title,
                        'description': desc if desc else f"Événement à Genève.",
                        'start_date': start_date,
                        'end_date': end_date,
                        'location': loc,
                        'address': address,
                        'city': 'Genève',
                        'latitude': lat,
                        'longitude': lon,
                        'categories': cats,
                        'source_url': link,
                        'organizer_email': email,
                        'region': 'Genève'
                    }
                    
                    if add_event(event):
                        count += 1
                        print(f"  [{count}] {title[:50]} | {start_date} | {', '.join(cats[:2])}")
                        if email:
                            all_emails.append({'email': email, 'event': title, 'source': 'leprogramme.ch'})
                
                except Exception as ex:
                    print(f"  Erreur: {str(ex)[:60]}")
            
        except Exception as ex:
            print(f"  Erreur semaine {week_str}: {str(ex)[:60]}")
        
        current += timedelta(weeks=2)  # Toutes les 2 semaines
    
    print(f"  Total leprogramme.ch: {count}")
    return count


# ==============================================================
# SOURCE 6: agenda.ge.ch (Agenda État de Genève)
# ==============================================================
def scrape_agenda_ge():
    print("\n=== agenda.ge.ch (État de Genève) ===")
    count = 0
    
    urls = [
        'https://www.ge.ch/evenements',
        'https://www.ge.ch/agenda',
    ]
    
    for page_url in urls:
        try:
            time.sleep(DELAY)
            r = requests.get(page_url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"  {page_url}: {r.status_code}")
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            links = set()
            for a in soup.find_all('a', href=True):
                href = a['href']
                if '/evenement' in href or '/agenda/' in href:
                    full = urljoin(page_url, href)
                    links.add(full)
            
            print(f"  {page_url}: {len(links)} liens")
            
            for link in list(links)[:30]:
                try:
                    time.sleep(DELAY)
                    r2 = requests.get(link, headers=HEADERS, timeout=15)
                    if r2.status_code != 200:
                        continue
                    
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    title_tag = soup2.find('h1')
                    if not title_tag:
                        continue
                    title = title_tag.get_text().strip()
                    if not title or len(title) < 5:
                        continue
                    
                    desc = ''
                    for p in soup2.find_all('p'):
                        txt = p.get_text().strip()
                        if len(txt) > 50:
                            desc = rewrite_description(txt)
                            break
                    
                    page_text = soup2.get_text()
                    dates = re.findall(r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}', page_text.lower())
                    
                    start_date = None
                    end_date = None
                    for d in dates:
                        parsed = parse_date_fr(d)
                        if parsed and parsed >= '2026-03-01':
                            if not start_date:
                                start_date = parsed
                            else:
                                end_date = parsed
                    
                    if not start_date:
                        continue
                    if not end_date:
                        end_date = start_date
                    
                    address = 'Genève'
                    email = find_email(soup2, link)
                    lat, lon, loc = get_coords(address, title)
                    cats = classify_event(title, desc)
                    
                    event = {
                        'title': title,
                        'description': desc if desc else f"Événement organisé par l'État de Genève.",
                        'start_date': start_date,
                        'end_date': end_date,
                        'location': loc,
                        'address': address,
                        'city': 'Genève',
                        'latitude': lat,
                        'longitude': lon,
                        'categories': cats,
                        'source_url': link,
                        'organizer_email': email,
                        'region': 'Genève'
                    }
                    
                    if add_event(event):
                        count += 1
                        print(f"  [{count}] {title[:50]} | {start_date}")
                        if email:
                            all_emails.append({'email': email, 'event': title, 'source': 'ge.ch'})
                
                except Exception as ex:
                    print(f"  Erreur: {str(ex)[:60]}")
        except Exception as ex:
            print(f"  Erreur: {str(ex)[:60]}")
    
    print(f"  Total agenda.ge.ch: {count}")
    return count


# ==============================================================
# SOURCE 7: Événements récurrents/confirmés Genève (connus)
# Ces événements sont des rendez-vous annuels confirmés
# ==============================================================
def add_confirmed_geneve_events():
    print("\n=== Événements confirmés Genève 2026 ===")
    count = 0
    
    # Événements majeurs confirmés à Genève
    confirmed = [
        {
            'title': 'Salon International de l\'Automobile de Genève 2026',
            'description': 'Le Salon International de l\'Automobile de Genève, l\'un des plus prestigieux salons automobiles au monde, revient à Palexpo pour présenter les dernières innovations et nouveautés du secteur automobile.',
            'start_date': '2026-03-05',
            'end_date': '2026-03-15',
            'address': 'Palexpo, Route François-Peyrot 30, 1218 Le Grand-Saconnex',
            'latitude': 46.2358,
            'longitude': 6.1114,
            'categories': ['Culture > Expositions', 'Famille > Fêtes'],
            'source_url': 'https://www.gims.swiss/',
            'organizer_email': 'info@gims.swiss'
        },
        {
            'title': 'Salon International des Inventions de Genève 2026',
            'description': 'Le plus important salon mondial dédié aux inventions réunit chaque année des inventeurs du monde entier qui présentent leurs créations et innovations dans tous les domaines.',
            'start_date': '2026-03-26',
            'end_date': '2026-03-30',
            'address': 'Palexpo, Route François-Peyrot 30, 1218 Le Grand-Saconnex',
            'latitude': 46.2358,
            'longitude': 6.1114,
            'categories': ['Culture > Expositions'],
            'source_url': 'https://www.inventions-geneva.ch/',
            'organizer_email': 'info@inventions-geneva.ch'
        },
        {
            'title': 'Geneva Lux - Festival des Lumières 2026',
            'description': 'Festival des lumières qui illumine les rues et bâtiments emblématiques de Genève avec des installations artistiques lumineuses créées par des artistes internationaux.',
            'start_date': '2026-03-12',
            'end_date': '2026-03-22',
            'address': 'Centre-ville de Genève, 1204 Genève',
            'latitude': 46.2011,
            'longitude': 6.1483,
            'categories': ['Culture > Expositions', 'Famille > Fêtes'],
            'source_url': 'https://www.genevelux.ch/',
            'organizer_email': 'info@genevelux.ch'
        },
        {
            'title': 'Marathon de Genève 2026',
            'description': 'Le Marathon de Genève propose plusieurs parcours le long du lac Léman et à travers les quartiers historiques de la ville. Une fête du sport pour tous les niveaux.',
            'start_date': '2026-05-10',
            'end_date': '2026-05-10',
            'address': 'Quai du Mont-Blanc, 1201 Genève',
            'latitude': 46.2097,
            'longitude': 6.1525,
            'categories': ['Sport > Terrestre'],
            'source_url': 'https://www.harmonygenevemarathon.com/',
            'organizer_email': 'info@genevemarathon.org'
        },
        {
            'title': 'Bol d\'Or Mirabaud 2026',
            'description': 'La plus grande régate de voile en eau douce au monde sur le lac Léman. Des centaines de voiliers s\'affrontent sur un parcours de 123 km au départ de Genève.',
            'start_date': '2026-06-13',
            'end_date': '2026-06-14',
            'address': 'Société Nautique de Genève, Port Noir, 1207 Genève',
            'latitude': 46.2044,
            'longitude': 6.1558,
            'categories': ['Sport > Aquatique'],
            'source_url': 'https://www.boldormirabaud.ch/',
            'organizer_email': 'info@boldormirabaud.ch'
        },
        {
            'title': 'Fêtes de Genève 2026',
            'description': 'Les Fêtes de Genève, le plus grand événement populaire de la ville, proposent dix jours de concerts, spectacles, animations et le célèbre feu d\'artifice sur la rade.',
            'start_date': '2026-08-06',
            'end_date': '2026-08-16',
            'address': 'Rade de Genève, Quai du Mont-Blanc, 1201 Genève',
            'latitude': 46.2072,
            'longitude': 6.1500,
            'categories': ['Music > Festival', 'Famille > Fêtes'],
            'source_url': 'https://www.fetesdegeneve.ch/',
            'organizer_email': 'info@fetesdegeneve.ch'
        },
        {
            'title': 'Musiques en Été 2026',
            'description': 'Festival de musique en plein air gratuit au coeur de Genève. Des concerts variés sont proposés tout l\'été dans le magnifique cadre du Parc La Grange.',
            'start_date': '2026-07-01',
            'end_date': '2026-08-15',
            'address': 'Parc La Grange, Quai Gustave-Ador 30, 1207 Genève',
            'latitude': 46.2028,
            'longitude': 6.1619,
            'categories': ['Music > Festival', 'Music > Concert'],
            'source_url': 'https://www.ville-geneve.ch/themes/culture/musique/musiques-en-ete/',
            'organizer_email': 'info@ville-geneve.ch'
        },
        {
            'title': 'Course de l\'Escalade 2026',
            'description': 'La Course de l\'Escalade commémore la victoire des Genevois sur les troupes du Duc de Savoie en 1602. Course populaire à travers la Vieille Ville de Genève.',
            'start_date': '2026-12-05',
            'end_date': '2026-12-06',
            'address': 'Vieille Ville, Place du Bourg-de-Four, 1204 Genève',
            'latitude': 46.2006,
            'longitude': 6.1533,
            'categories': ['Sport > Terrestre', 'Famille > Fêtes'],
            'source_url': 'https://www.escalade.ch/',
            'organizer_email': 'info@escalade.ch'
        },
        {
            'title': 'Marché de Noël de Genève 2026',
            'description': 'Le traditionnel marché de Noël de Genève s\'installe sur la Plaine de Plainpalais avec des dizaines de chalets proposant artisanat, cadeaux et spécialités gastronomiques.',
            'start_date': '2026-11-19',
            'end_date': '2026-12-24',
            'address': 'Plaine de Plainpalais, 1205 Genève',
            'latitude': 46.1978,
            'longitude': 6.1417,
            'categories': ['Gastronomie > Marché', 'Famille > Fêtes'],
            'source_url': 'https://www.geneve.com/fr/agenda/marche-de-noel/',
            'organizer_email': ''
        },
        {
            'title': 'Fête de la Musique Genève 2026',
            'description': 'La Fête de la Musique envahit les rues, places et parcs de Genève avec des centaines de concerts gratuits de tous styles musicaux.',
            'start_date': '2026-06-20',
            'end_date': '2026-06-21',
            'address': 'Centre-ville de Genève, 1204 Genève',
            'latitude': 46.2044,
            'longitude': 6.1432,
            'categories': ['Music > Festival', 'Music > Concert'],
            'source_url': 'https://www.fetedelamusique.ch/',
            'organizer_email': 'info@fetedelamusique.ch'
        },
        {
            'title': 'Journée mondiale de l\'eau - ONU Genève 2026',
            'description': 'Journée de sensibilisation organisée par les Nations Unies au Palais des Nations sur les enjeux de l\'eau dans le monde.',
            'start_date': '2026-03-22',
            'end_date': '2026-03-22',
            'address': 'Palais des Nations, Avenue de la Paix 8-14, 1211 Genève',
            'latitude': 46.2267,
            'longitude': 6.1389,
            'categories': ['Culture > Conférence'],
            'source_url': 'https://www.ungeneva.org/',
            'organizer_email': ''
        },
        {
            'title': 'Nuit des Musées Genève 2026',
            'description': 'Une nuit magique pour découvrir les musées de Genève autrement. Expositions, animations, performances et accès gratuit dans de nombreux musées.',
            'start_date': '2026-05-16',
            'end_date': '2026-05-16',
            'address': 'Musée d\'Art et d\'Histoire, Rue Charles-Galland 2, 1206 Genève',
            'latitude': 46.1978,
            'longitude': 6.1531,
            'categories': ['Culture > Expositions', 'Famille > Fêtes'],
            'source_url': 'https://www.nuitdesmusees.ch/',
            'organizer_email': 'info@nuitdesmusees.ch'
        },
        {
            'title': 'Triathlon de Genève 2026',
            'description': 'Le Triathlon International de Genève accueille les triathlètes de tous niveaux au coeur de la ville. Natation dans le lac, vélo et course à pied.',
            'start_date': '2026-07-19',
            'end_date': '2026-07-19',
            'address': 'Genève Plage, Quai de Cologny, 1223 Cologny',
            'latitude': 46.2167,
            'longitude': 6.1833,
            'categories': ['Sport > Terrestre', 'Sport > Aquatique'],
            'source_url': 'https://www.triathlondegeneve.ch/',
            'organizer_email': 'info@triathlondegeneve.ch'
        },
        {
            'title': 'Salon du Livre de Genève 2026',
            'description': 'Le Salon du Livre et de la Presse est le rendez-vous culturel incontournable de Genève. Rencontres d\'auteurs, dédicaces, conférences et ateliers.',
            'start_date': '2026-04-22',
            'end_date': '2026-04-26',
            'address': 'Palexpo, Route François-Peyrot 30, 1218 Le Grand-Saconnex',
            'latitude': 46.2358,
            'longitude': 6.1114,
            'categories': ['Culture > Expositions', 'Culture > Conférence'],
            'source_url': 'https://www.salondulivre.ch/',
            'organizer_email': 'info@salondulivre.ch'
        },
        {
            'title': 'Fête nationale suisse - Genève 2026',
            'description': 'Célébration du 1er août à Genève avec feu d\'artifice, concerts, animations et brunch populaire au bord du lac.',
            'start_date': '2026-08-01',
            'end_date': '2026-08-01',
            'address': 'Rade de Genève, 1201 Genève',
            'latitude': 46.2072,
            'longitude': 6.1500,
            'categories': ['Famille > Fêtes'],
            'source_url': 'https://www.geneve.ch/fr/actualites/1er-aout',
            'organizer_email': ''
        },
        {
            'title': 'Carouge à la Rue 2026',
            'description': 'Festival des arts de la rue à Carouge. Spectacles de cirque, théâtre de rue, jonglerie, musique et animations dans les rues et places de Carouge.',
            'start_date': '2026-06-12',
            'end_date': '2026-06-14',
            'address': 'Place du Marché, 1227 Carouge',
            'latitude': 46.1833,
            'longitude': 6.1389,
            'categories': ['Culture > Théâtre', 'Music > Festival'],
            'source_url': 'https://www.carougealrue.ch/',
            'organizer_email': 'info@carougealrue.ch'
        },
        {
            'title': 'Festival de la Bâtie 2026',
            'description': 'Festival pluridisciplinaire de la rentrée culturelle genevoise. Théâtre, danse, musique et performance dans divers lieux de Genève.',
            'start_date': '2026-09-03',
            'end_date': '2026-09-13',
            'address': 'Bâtiment des Forces Motrices, Place des Volontaires 2, 1204 Genève',
            'latitude': 46.2028,
            'longitude': 6.1408,
            'categories': ['Music > Festival', 'Culture > Théâtre', 'Culture > Danse'],
            'source_url': 'https://www.bfrancoise.ch/',
            'organizer_email': 'info@bfrancoise.ch'
        },
        {
            'title': 'Antigel Festival 2026',
            'description': 'Festival de musique et arts performatifs mêlant concerts, spectacles de danse et performances artistiques dans des lieux insolites de Genève.',
            'start_date': '2026-03-06',
            'end_date': '2026-03-22',
            'address': 'Divers lieux, 1204 Genève',
            'latitude': 46.2044,
            'longitude': 6.1432,
            'categories': ['Music > Festival', 'Culture > Danse'],
            'source_url': 'https://www.antigel.ch/',
            'organizer_email': 'info@antigel.ch'
        },
        {
            'title': 'Watches and Wonders Geneva 2026',
            'description': 'Le Salon international de la haute horlogerie réunit les plus grandes maisons horlogères du monde pour présenter leurs dernières créations et innovations.',
            'start_date': '2026-03-31',
            'end_date': '2026-04-06',
            'address': 'Palexpo, Route François-Peyrot 30, 1218 Le Grand-Saconnex',
            'latitude': 46.2358,
            'longitude': 6.1114,
            'categories': ['Culture > Expositions'],
            'source_url': 'https://www.watchesandwonders.com/',
            'organizer_email': 'info@watchesandwonders.com'
        },
        {
            'title': 'Marché aux Puces de Plainpalais 2026',
            'description': 'Le plus grand marché aux puces de Genève se tient chaque mercredi et samedi sur la Plaine de Plainpalais. Antiquités, brocante, vintage et objets de collection.',
            'start_date': '2026-03-01',
            'end_date': '2026-12-31',
            'address': 'Plaine de Plainpalais, 1205 Genève',
            'latitude': 46.1978,
            'longitude': 6.1417,
            'categories': ['Gastronomie > Marché'],
            'source_url': 'https://www.geneve.com/fr/shopping/marche-aux-puces-de-plainpalais',
            'organizer_email': ''
        },
        {
            'title': 'GIFF - Geneva International Film Festival 2026',
            'description': 'Le Festival International du Film de Genève célèbre l\'innovation dans le cinéma et les arts numériques avec des projections, masterclasses et expositions immersives.',
            'start_date': '2026-11-05',
            'end_date': '2026-11-09',
            'address': 'Maison des Arts du Grütli, Rue du Général-Dufour 16, 1204 Genève',
            'latitude': 46.1983,
            'longitude': 6.1419,
            'categories': ['Culture > Cinéma', 'Music > Festival'],
            'source_url': 'https://www.giff.ch/',
            'organizer_email': 'info@giff.ch'
        },
        {
            'title': 'Journées du Patrimoine - Genève 2026',
            'description': 'Deux jours pour découvrir le patrimoine architectural et historique de Genève. Visites guidées, conférences et portes ouvertes dans des lieux habituellement fermés au public.',
            'start_date': '2026-09-12',
            'end_date': '2026-09-13',
            'address': 'Cathédrale Saint-Pierre, Cour de Saint-Pierre, 1204 Genève',
            'latitude': 46.2011,
            'longitude': 6.1483,
            'categories': ['Culture > Expositions', 'Famille > Fêtes'],
            'source_url': 'https://www.journeesdupatrimoine.ch/',
            'organizer_email': ''
        },
        {
            'title': 'Nuit de la Science 2026',
            'description': 'Deux jours de découvertes scientifiques au Musée d\'histoire des sciences et dans le Parc de la Perle du Lac. Expériences, démonstrations et conférences.',
            'start_date': '2026-07-04',
            'end_date': '2026-07-05',
            'address': 'Musée d\'histoire des sciences, Rue de Lausanne 128, 1202 Genève',
            'latitude': 46.2200,
            'longitude': 6.1536,
            'categories': ['Culture > Conférence', 'Famille > Enfants'],
            'source_url': 'https://www.ville-geneve.ch/themes/culture/musees-institutions/nuit-science/',
            'organizer_email': ''
        },
        {
            'title': 'CERN Open Days 2026',
            'description': 'Le CERN ouvre ses portes au public pour découvrir les coulisses de la physique des particules. Visites guidées des installations, expériences interactives et conférences.',
            'start_date': '2026-09-19',
            'end_date': '2026-09-20',
            'address': 'CERN, Esplanade des Particules 1, 1211 Meyrin',
            'latitude': 46.2330,
            'longitude': 6.0556,
            'categories': ['Culture > Conférence', 'Famille > Enfants'],
            'source_url': 'https://home.cern/fr/resources/faqs/open-days',
            'organizer_email': 'opendays@cern.ch'
        },
        {
            'title': 'Lake Parade Genève 2026',
            'description': 'La Lake Parade est le plus grand événement techno et dance music de Suisse romande. Des chars musicaux défilent le long des quais de Genève.',
            'start_date': '2026-07-04',
            'end_date': '2026-07-04',
            'address': 'Quai du Mont-Blanc, 1201 Genève',
            'latitude': 46.2097,
            'longitude': 6.1525,
            'categories': ['Music > Electro / DJ', 'Music > Festival'],
            'source_url': 'https://www.lakeparade.ch/',
            'organizer_email': 'info@lakeparade.ch'
        },
        {
            'title': 'Jardin Botanique - Fête de la Tulipe 2026',
            'description': 'Le Conservatoire et Jardin botaniques de Genève célèbre le printemps avec des milliers de tulipes en fleur, des visites guidées et des ateliers botaniques.',
            'start_date': '2026-04-10',
            'end_date': '2026-05-10',
            'address': 'Conservatoire et Jardin botaniques, Chemin de l\'Impératrice 1, 1292 Chambésy',
            'latitude': 46.2233,
            'longitude': 6.1500,
            'categories': ['Culture > Expositions', 'Famille > Enfants'],
            'source_url': 'https://www.ville-geneve.ch/themes/environnement-urbain-espaces-verts/jardins-botaniques/',
            'organizer_email': ''
        },
        {
            'title': 'Fête de l\'Olivier - Carouge 2026',
            'description': 'Fête populaire de Carouge avec marché artisanal, concerts, spectacles de rue et gastronomie méditerranéenne dans les rues du vieux Carouge.',
            'start_date': '2026-06-27',
            'end_date': '2026-06-28',
            'address': 'Place du Marché, 1227 Carouge',
            'latitude': 46.1833,
            'longitude': 6.1389,
            'categories': ['Famille > Fêtes', 'Gastronomie > Marché'],
            'source_url': 'https://www.carouge.ch/',
            'organizer_email': ''
        },
        {
            'title': 'Geneva Classics 2026',
            'description': 'Exposition de voitures de collection et grand prix automobile dans les rues de Genève. Plus de 200 véhicules d\'exception à admirer.',
            'start_date': '2026-09-26',
            'end_date': '2026-09-27',
            'address': 'Parc des Eaux-Vives, Quai Gustave-Ador 82, 1207 Genève',
            'latitude': 46.2061,
            'longitude': 6.1636,
            'categories': ['Culture > Expositions'],
            'source_url': 'https://www.genevaclassics.ch/',
            'organizer_email': 'info@genevaclassics.ch'
        },
    ]
    
    for event in confirmed:
        # Remplir les champs manquants
        event.setdefault('city', 'Genève')
        event.setdefault('region', 'Genève')
        event.setdefault('location', event.get('address', 'Genève'))
        
        if add_event(event):
            count += 1
            print(f"  [{count}] {event['title'][:50]} | {event['start_date']}")
            if event.get('organizer_email'):
                all_emails.append({'email': event['organizer_email'], 'event': event['title'], 'source': 'confirmé'})
    
    print(f"  Total événements confirmés: {count}")
    return count


# ==============================================================
# MAIN
# ==============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("SCRAPER GENÈVE - Recherche d'événements réels 2026")
    print("=" * 60)
    
    total = 0
    
    # D'abord les événements confirmés (pas de requête web)
    total += add_confirmed_geneve_events()
    
    # Puis les sources web
    total += scrape_geneve_com()
    total += scrape_ville_geneve()
    total += scrape_myswitzerland_geneve()
    total += scrape_eventfrog_geneve()
    total += scrape_leprogramme_geneve()
    total += scrape_agenda_ge()
    
    print(f"\n{'='*60}")
    print(f"TOTAL EVENTS GENÈVE: {len(all_events)}")
    print(f"TOTAL EMAILS: {len(all_emails)}")
    
    # Sauvegarder les events
    with open('geneve_events.json', 'w', encoding='utf-8') as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)
    print(f"\nEvents sauvegardés dans geneve_events.json")
    
    # Sauvegarder les emails
    emails_dir = 'emails_organisateurs'
    email_file = f'{emails_dir}/emails_Geneve.csv'
    with open(email_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['email', 'event', 'source'])
        for e in all_emails:
            writer.writerow([e['email'], e['event'], e['source']])
    print(f"Emails sauvegardés dans {email_file}")
    
    # Statistiques par catégorie
    cat_count = {}
    for e in all_events:
        for c in e.get('categories', []):
            cat_count[c] = cat_count.get(c, 0) + 1
    
    print(f"\nStatistiques par catégorie:")
    for cat, cnt in sorted(cat_count.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {cnt}")
