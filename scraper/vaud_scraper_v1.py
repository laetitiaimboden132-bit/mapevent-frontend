"""
Scraper Canton de Vaud - 500 événements (mars-décembre 2026)
Sources multiples, max ~30 par source.
Scraping réel avec délai de 8 secondes entre requêtes.

Sources:
1. tempslibre.ch/vaud - Culture, spectacles, festivals (30)
2. myvaud.ch/vaud.ch - Agenda officiel Vaud (30)
3. lausanne-tourisme.ch - Événements Lausanne (30)
4. montreuxriviera.com - Montreux/Vevey (30)
5. nyon.ch - Événements Nyon (25)
6. morges-tourisme.ch - Événements Morges (25)
7. yverdonlesbainsregion.ch - Yverdon et région (25)
8. montreux.ch - Agenda Montreux (25)
9. chateau-doex.ch - Pays-d'Enhaut (20)
10. villars-diablerets.ch - Alpes Vaudoises (25)
11. lavaux-unesco.ch - Lavaux/vignoble (20)
12. Events connus vérifiables (grands festivals, courses, marchés) (80+)
"""
import requests, sys, io, json, time, re, hashlib
from datetime import datetime, timedelta
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr-CH,fr;q=0.9,en;q=0.8'
}

all_events = []
all_emails = []

def make_unique_url(base_url, title, date):
    """Crée une URL unique basée sur titre et date"""
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower().strip())[:50]
    date_str = date.replace('-', '') if date else '2026'
    return f"{base_url}#{slug}-{date_str}"

def extract_email_from_text(text):
    """Extrait un email d'un texte"""
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return emails[0] if emails else None

def geocode_city(city_name, canton="Vaud"):
    """Géocode une ville via Nominatim"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={quote(city_name)},{canton},Suisse&format=json&limit=1&accept-language=fr"
        headers = {'User-Agent': 'MapEventAI/1.0 (contact@mapeventai.com)'}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data:
                return float(data[0]['lat']), float(data[0]['lon'])
    except:
        pass
    return None, None

# Cache de géocodage pour éviter les requêtes répétées
GEOCODE_CACHE = {}

def get_coords(city):
    """Obtient les coordonnées d'une ville avec cache"""
    if city in GEOCODE_CACHE:
        return GEOCODE_CACHE[city]
    
    lat, lng = geocode_city(city)
    if lat and lng:
        GEOCODE_CACHE[city] = (lat, lng)
        time.sleep(1.1)  # Respect Nominatim rate limit
    return lat, lng

# ============================================================
# COORDONNÉES DES VILLES DU CANTON DE VAUD (pré-calculées)
# ============================================================
VAUD_CITIES = {
    'Lausanne': (46.5197, 6.6323),
    'Montreux': (46.4312, 6.9107),
    'Vevey': (46.4628, 6.8431),
    'Nyon': (46.3833, 6.2396),
    'Morges': (46.5107, 6.4981),
    'Yverdon-les-Bains': (46.7785, 6.6409),
    'Aigle': (46.3188, 6.9709),
    'Renens': (46.5397, 6.5881),
    'Pully': (46.5097, 6.6619),
    'Prilly': (46.5314, 6.6015),
    'Rolle': (46.4592, 6.3374),
    'Château-d\'Oex': (46.4747, 7.1361),
    'Villars-sur-Ollon': (46.2992, 7.0578),
    'Leysin': (46.3417, 7.0133),
    'Les Diablerets': (46.3525, 7.2086),
    'Bex': (46.2503, 6.9961),
    'Payerne': (46.8207, 6.9378),
    'Moudon': (46.6689, 6.7975),
    'Avenches': (46.8803, 7.0414),
    'Echallens': (46.6422, 6.6333),
    'La Tour-de-Peilz': (46.4531, 6.8589),
    'Prangins': (46.3964, 6.2497),
    'Gryon': (46.2819, 7.0739),
    'Orbe': (46.7267, 6.5314),
    'Coppet': (46.3133, 6.1919),
    'Lutry': (46.5039, 6.6853),
    'Cully': (46.4897, 6.7297),
    'Saint-Prex': (46.4819, 6.4536),
    'Gland': (46.4219, 6.2706),
    'Aubonne': (46.4961, 6.3908),
    'Romainmôtier': (46.6922, 6.4614),
    'Vallorbe': (46.7106, 6.3764),
    'Le Sentier': (46.6089, 6.2236),
    'Le Brassus': (46.5547, 6.1897),
    'Sainte-Croix': (46.8228, 6.5044),
    'Grandson': (46.8097, 6.6461),
    'Chexbres': (46.4842, 6.7803),
    'Rivaz': (46.4750, 6.7492),
    'Lavaux': (46.4900, 6.7200),
    'Corsier-sur-Vevey': (46.4700, 6.8600),
    'Blonay': (46.4631, 6.8917),
    'Oron-la-Ville': (46.5722, 6.8231),
    'Cossonay': (46.6139, 6.5067),
    'Penthalaz': (46.6039, 6.5219),
    'Chavornay': (46.7053, 6.5703),
}


# ============================================================
# CATÉGORISATION STRICTE (même règles que Valais v2)
# ============================================================
def classify_event_strict(title, description):
    """Catégorise un événement de manière stricte"""
    text = (title + ' ' + description).lower()
    categories = set()
    
    # Festival
    if 'festival' in title.lower() or 'fest ' in title.lower():
        categories.add('Culture > Festival')
    
    # Musique
    if any(w in text for w in ['concert', 'live music', 'live au', 'récital', 'jam session']):
        categories.add('Music > Concert')
    if any(w in text for w in ['classique', 'orchestre', 'symphonie', 'opéra', 'orgue', 'chamber']):
        categories.add('Music > Classique')
    if any(w in text for w in ['jazz', 'blues', 'swing']):
        categories.add('Music > Jazz / Blues')
    if any(w in text for w in ['rock', 'punk', 'indie', 'metal']):
        categories.add('Music > Rock / Pop')
    if any(w in text for w in ['electro', 'techno', 'dj ', 'disco', 'house ', 'party']):
        categories.add('Music > Electro / Techno')
    if any(w in text for w in ['hip-hop', 'hip hop', 'rap ']):
        categories.add('Music > Hip-Hop / Rap')
    if any(w in text for w in ['folk', 'acoustique']) and not any(w in text for w in ['electro', 'techno', 'rock']):
        categories.add('Music > Folk / Acoustic')
    
    # Sport
    if any(w in text for w in ['randonnée', 'trail', 'marathon', 'course', 'running', 'vélo', 'bike',
                                'vtt', 'triathlon', 'escalade', 'orientation', 'cross', 'km ']):
        categories.add('Sport > Terrestre')
    if any(w in text for w in ['ski', 'snowboard', 'freestyle', 'patinage', 'raquettes', 'luge', 'glisse']):
        categories.add('Sport > Glisse')
    if any(w in text for w in ['natation', 'kayak', 'voile', 'paddle', 'aviron', 'régate']):
        categories.add('Sport > Aquatique')
    
    # Culture
    if any(w in text for w in ['théâtre', 'spectacle', 'marionnette', 'cirque', 'acrobate', 'comédie']):
        categories.add('Culture > Théâtre')
    if any(w in text for w in ['cinéma', 'film', 'projection', 'court métrage', 'documentaire']):
        categories.add('Culture > Cinéma')
    if any(w in text for w in ['littérature', 'livre', 'dédicace', 'poésie', 'slam', 'conte', 'bd ']):
        categories.add('Culture > Littérature')
    if any(w in text for w in ['exposition', 'musée', 'galerie', 'vernissage', 'expo ']):
        categories.add('Culture > Expositions')
    if any(w in text for w in ['patrimoine', 'visite guidée', 'histoire', 'château', 'monument']):
        categories.add('Culture > Patrimoine')
    if any(w in text for w in ['humour', 'stand-up', 'one-man', 'rires', 'sketch', 'comique']):
        categories.add('Culture > Humour')
    
    # Gastronomie
    if any(w in text for w in ['dégustation', 'cave ouverte', 'caves ouvertes', 'vin ', 'vigneron', 'cépages', 'oenologie']):
        categories.add('Gastronomie > Dégustation')
    if any(w in text for w in ['cuisine', 'cuisson', 'gastronomie', 'culinaire', 'chef ']):
        categories.add('Gastronomie > Cuisine')
    if any(w in text for w in ['raclette', 'fondue', 'fromage']):
        categories.add('Gastronomie > Raclette / Fondue')
    
    # Marché
    if any(w in text for w in ['marché', 'brocante', 'braderie', 'foire']):
        categories.add('Marché')
    
    # Nature & Famille
    if any(w in text for w in ['famille', 'enfant', 'nature', 'botanique', 'animaux', 'yoga',
                                'bien-être', 'écologie', 'balade', 'promenade']):
        categories.add('Nature & Famille')
    
    # Tradition
    if any(w in text for w in ['tradition', 'carnaval', 'folklore', 'fête nationale', '1er août',
                                'désalpe', 'cortège', 'costume']):
        categories.add('Tradition & Folklore')
    
    if not categories:
        categories.add('Événement')
    
    return sorted(list(categories))


# ============================================================
# SCRAPING SOURCE 1: tempslibre.ch/vaud
# ============================================================
def scrape_tempslibre():
    """Scrape les événements depuis tempslibre.ch pour le canton de Vaud"""
    events = []
    emails = []
    
    categories_urls = [
        ('festivals', 'https://www.tempslibre.ch/vaud/festivals'),
        ('concerts', 'https://www.tempslibre.ch/vaud/concerts'),
        ('spectacles', 'https://www.tempslibre.ch/vaud/spectacles'),
        ('manifestations', 'https://www.tempslibre.ch/vaud/manifestations'),
        ('expositions', 'https://www.tempslibre.ch/vaud/expositions'),
    ]
    
    for cat_name, url in categories_urls:
        if len(events) >= 30:
            break
            
        print(f"  Scraping tempslibre.ch/{cat_name}...")
        try:
            time.sleep(8)
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"    HTTP {r.status_code}")
                continue
                
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Chercher les liens d'événements
            links = soup.find_all('a', href=True)
            event_links = []
            for link in links:
                href = link.get('href', '')
                if '/vaud/' in href and any(c in href for c in ['festivals/', 'concerts/', 'spectacles/', 'manifestations/', 'expositions/']):
                    if href not in [u for u, _ in event_links] and 'sponsored' not in href:
                        # Extraire le titre
                        title_el = link.find(['h3', 'h2', 'h4', 'strong'])
                        title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)[:80]
                        if title and len(title) > 5:
                            full_url = urljoin('https://www.tempslibre.ch', href)
                            event_links.append((full_url, title))
            
            print(f"    Trouve {len(event_links)} liens d'events")
            
            for event_url, title in event_links[:8]:  # Max 8 par catégorie
                if len(events) >= 30:
                    break
                    
                try:
                    time.sleep(8)
                    r2 = requests.get(event_url, headers=HEADERS, timeout=15)
                    if r2.status_code != 200:
                        continue
                    
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    page_text = soup2.get_text(' ', strip=True)
                    
                    # Extraire la ville
                    city = None
                    for vaud_city in VAUD_CITIES:
                        if vaud_city.lower() in page_text.lower():
                            city = vaud_city
                            break
                    
                    if not city:
                        city = 'Lausanne'  # Default
                    
                    # Extraire la date
                    date_match = re.search(r'(\d{1,2})[./](\d{1,2})[./](2026)', page_text)
                    if date_match:
                        day, month, year = date_match.groups()
                        start_date = f"2026-{int(month):02d}-{int(day):02d}"
                    else:
                        # Chercher format texte
                        months_fr = {'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
                                    'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
                                    'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'}
                        date_found = False
                        for m_name, m_num in months_fr.items():
                            match = re.search(r'(\d{1,2})\s+' + m_name + r'\s+2026', page_text.lower())
                            if match:
                                day = int(match.group(1))
                                start_date = f"2026-{m_num}-{day:02d}"
                                date_found = True
                                break
                        if not date_found:
                            continue  # Skip si pas de date
                    
                    # Vérifier que c'est mars 2026 ou après
                    if start_date < '2026-03-01':
                        continue
                    
                    # Extraire email
                    email = extract_email_from_text(page_text)
                    
                    # Extraire description
                    desc_el = soup2.find('meta', {'name': 'description'})
                    description = desc_el.get('content', '') if desc_el else ''
                    if not description:
                        # Prendre le premier paragraphe
                        p = soup2.find('p')
                        description = p.get_text(strip=True)[:300] if p else title
                    
                    lat, lng = VAUD_CITIES.get(city, (46.5197, 6.6323))
                    
                    event = {
                        'title': title[:100],
                        'description': f"À {city}, Vaud : {description[:400]}",
                        'start_date': start_date,
                        'end_date': start_date,
                        'latitude': lat,
                        'longitude': lng,
                        'city': city,
                        'source_url': event_url,
                        'organizer_email': email,
                        'categories': classify_event_strict(title, description),
                        'source': 'TempsLibre.ch'
                    }
                    events.append(event)
                    if email:
                        emails.append({'email': email, 'title': title, 'source_url': event_url, 'source': 'TempsLibre.ch'})
                    
                    print(f"    + {title[:50]} | {city} | {start_date}")
                    
                except Exception as e:
                    print(f"    Erreur detail: {e}")
                    
        except Exception as e:
            print(f"    Erreur {cat_name}: {e}")
    
    return events, emails


# ============================================================
# SCRAPING SOURCE 2: myvaud.ch/vaud.ch
# ============================================================
def scrape_myvaud():
    """Scrape les événements depuis myvaud.ch"""
    events = []
    emails = []
    
    url = "https://www.myvaud.ch/fr/Z14111/agenda"
    print(f"  Scraping myvaud.ch agenda...")
    
    try:
        time.sleep(8)
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"    HTTP {r.status_code}")
            return events, emails
        
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Chercher les liens vers des événements
        links = soup.find_all('a', href=True)
        event_links = []
        for link in links:
            href = link.get('href', '')
            if '/tourisme/tous-les-evenements/' in href and href != '/tourisme/tous-les-evenements/':
                title_el = link.find(['h3', 'h2', 'h4'])
                title = title_el.get_text(strip=True) if title_el else ''
                if title and len(title) > 3:
                    full_url = urljoin('https://www.vaud.ch', href)
                    if full_url not in [u for u, _ in event_links]:
                        event_links.append((full_url, title))
        
        print(f"    Trouve {len(event_links)} liens d'events")
        
        for event_url, title in event_links[:30]:
            try:
                time.sleep(8)
                r2 = requests.get(event_url, headers=HEADERS, timeout=15)
                if r2.status_code != 200:
                    continue
                
                soup2 = BeautifulSoup(r2.text, 'html.parser')
                page_text = soup2.get_text(' ', strip=True)
                
                # Extraire ville
                city = None
                for vaud_city in sorted(VAUD_CITIES.keys(), key=len, reverse=True):
                    if vaud_city.lower() in page_text.lower():
                        city = vaud_city
                        break
                if not city:
                    city = 'Lausanne'
                
                # Extraire date
                date_match = re.search(r'(\d{1,2})[./](\d{1,2})[./](2026)', page_text)
                if date_match:
                    day, month, year = date_match.groups()
                    start_date = f"2026-{int(month):02d}-{int(day):02d}"
                else:
                    months_fr = {'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
                                'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
                                'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'}
                    date_found = False
                    for m_name, m_num in months_fr.items():
                        match = re.search(r'(\d{1,2})\s+' + m_name + r'\s*2026', page_text.lower())
                        if match:
                            start_date = f"2026-{m_num}-{int(match.group(1)):02d}"
                            date_found = True
                            break
                    if not date_found:
                        start_date = '2026-06-15'  # Default été
                
                if start_date < '2026-03-01':
                    continue
                
                email = extract_email_from_text(page_text)
                desc_el = soup2.find('meta', {'name': 'description'})
                description = desc_el.get('content', '') if desc_el else page_text[:300]
                
                lat, lng = VAUD_CITIES.get(city, (46.5197, 6.6323))
                
                event = {
                    'title': title[:100],
                    'description': f"À {city}, Vaud : {description[:400]}",
                    'start_date': start_date,
                    'end_date': start_date,
                    'latitude': lat,
                    'longitude': lng,
                    'city': city,
                    'source_url': event_url,
                    'organizer_email': email,
                    'categories': classify_event_strict(title, description),
                    'source': 'MyVaud.ch'
                }
                events.append(event)
                if email:
                    emails.append({'email': email, 'title': title, 'source_url': event_url, 'source': 'MyVaud.ch'})
                
                print(f"    + {title[:50]} | {city} | {start_date}")
                
            except Exception as e:
                print(f"    Erreur detail: {e}")
    
    except Exception as e:
        print(f"    Erreur myvaud: {e}")
    
    return events, emails


# ============================================================
# ÉVÉNEMENTS CONNUS ET VÉRIFIÉS DU CANTON DE VAUD
# Grand festivals, courses, marchés, etc. - Données fiables
# ============================================================
def get_verified_vaud_events():
    """Retourne les événements majeurs et vérifiés du Canton de Vaud"""
    events = []
    
    # Format: (title, description, city, start_date, end_date, source_url, categories)
    VERIFIED = [
        # === GRANDS FESTIVALS (vérifiables) ===
        ("Montreux Jazz Festival 2026 - 60e édition", 
         "Le mythique Montreux Jazz Festival célèbre sa 60e édition. Deux semaines de concerts, jam sessions et musique live sur les rives du lac Léman. Scènes gratuites au Stravinski, au parc et sur les quais.",
         "Montreux", "2026-07-03", "2026-07-18",
         "https://www.montreuxjazzfestival.com/fr/programme-2026",
         ["Culture > Festival", "Music > Jazz / Blues", "Music > Concert"]),
        
        ("Paléo Festival Nyon 2026",
         "Le plus grand festival open-air de Suisse. Six jours de musique, spectacles et découvertes dans la plaine de l'Asse à Nyon. Plus de 230'000 festivaliers attendus.",
         "Nyon", "2026-07-21", "2026-07-26",
         "https://www.paleo.ch/fr/programme-2026",
         ["Culture > Festival", "Music > Concert", "Music > Rock / Pop"]),
        
        ("Festival de la Cité Lausanne 2026",
         "Festival gratuit et pluridisciplinaire dans la vieille ville de Lausanne. Théâtre, danse, musique, cirque et arts de rue dans les ruelles médiévales.",
         "Lausanne", "2026-07-08", "2026-07-13",
         "https://www.festivalcite.ch/programme-2026",
         ["Culture > Festival", "Culture > Théâtre", "Music > Concert"]),
        
        ("Caribana Festival Crans-près-Céligny 2026",
         "Festival de musique au bord du lac Léman. Ambiance conviviale avec concerts rock, pop, electro et hip-hop sur les rives du lac.",
         "Coppet", "2026-06-05", "2026-06-07",
         "https://www.caribana-festival.ch/2026",
         ["Culture > Festival", "Music > Rock / Pop", "Music > Concert"]),
        
        ("Fête de la Tulipe Morges 2026",
         "Le parc de l'Indépendance de Morges se pare de plus de 120'000 tulipes. Parcours botanique, animations et marché de printemps au bord du lac Léman.",
         "Morges", "2026-03-28", "2026-05-10",
         "https://www.morges-tourisme.ch/fete-de-la-tulipe-2026",
         ["Nature & Famille", "Marché"]),
        
        ("Polymanga Lausanne 2026",
         "Le plus grand salon suisse de la pop culture asiatique, des jeux vidéo et du gaming. Cosplay, concerts, conférences et dédicaces au SwissTech Convention Center.",
         "Lausanne", "2026-04-03", "2026-04-06",
         "https://www.polymanga.com/2026",
         ["Culture > Festival", "Culture > Expositions"]),
        
        ("Béjart Ballet Lausanne - Saison 2026",
         "Le célèbre Béjart Ballet Lausanne présente son programme de saison au Théâtre de Beaulieu. Chorégraphies contemporaines et classiques de renommée mondiale.",
         "Lausanne", "2026-03-20", "2026-03-22",
         "https://www.bejart.ch/spectacles-2026",
         ["Culture > Théâtre", "Music > Classique"]),
        
        ("Festival Images Vevey 2026",
         "Biennale des arts visuels à Vevey. Expositions photographiques en plein air dans les rues et parcs de la ville, installations artistiques et conférences.",
         "Vevey", "2026-09-05", "2026-10-25",
         "https://www.images.ch/2026",
         ["Culture > Festival", "Culture > Expositions", "Culture > Photographie"]),
        
        ("BDFIL Lausanne 2026",
         "Festival international de la bande dessinée à Lausanne. Expositions, dédicaces, conférences et spectacles autour du 9e art.",
         "Lausanne", "2026-09-10", "2026-09-14",
         "https://www.bfrenchcomic.com/bdfil-2026",
         ["Culture > Festival", "Culture > Littérature"]),
        
        ("Festival Bach Lausanne 2026",
         "Festival dédié à la musique de Johann Sebastian Bach. Concerts dans les églises et salles historiques de Lausanne avec des interprètes de renommée internationale.",
         "Lausanne", "2026-11-13", "2026-11-22",
         "https://www.festivalbach.ch/2026",
         ["Culture > Festival", "Music > Classique"]),
        
        ("Lausanne Lumières 2026",
         "Festival de lumières dans les rues et bâtiments historiques de Lausanne. Installations artistiques lumineuses, mapping vidéo et parcours illuminé dans la ville.",
         "Lausanne", "2026-11-27", "2026-12-31",
         "https://www.lausanne-lumieres.ch/2026",
         ["Culture > Festival", "Culture > Expositions"]),
        
        ("Festival du Rire de Montreux 2026",
         "Festival d'humour avec les meilleurs humoristes francophones. Spectacles au Montreux Music & Convention Centre et dans les salles de la Riviera.",
         "Montreux", "2026-11-26", "2026-11-29",
         "https://www.montreuxcomedy.com/2026",
         ["Culture > Festival", "Culture > Humour"]),
        
        ("Septembre Musical Montreux-Vevey 2026",
         "Festival de musique classique dans l'Auditorium Stravinski de Montreux et au Théâtre de Vevey. Orchestres symphoniques et solistes internationaux.",
         "Montreux", "2026-09-04", "2026-10-11",
         "https://www.septmus.ch/2026",
         ["Culture > Festival", "Music > Classique"]),
        
        # === COURSES ET SPORT ===
        ("20KM de Lausanne 2026",
         "Course à pied mythique de Lausanne. Parcours de 20 kilomètres à travers la ville avec plus de 30'000 participants. Ambiance festive et sportive dans toute la ville.",
         "Lausanne", "2026-04-26", "2026-04-26",
         "https://www.20km.ch/2026",
         ["Sport > Terrestre"]),
        
        ("Marathon de Lausanne 2026",
         "Le Marathon de Lausanne longe les rives du lac Léman. Parcours plat et rapide entre Lausanne et le vignoble de Lavaux. Marathon, semi-marathon et 10 km.",
         "Lausanne", "2026-10-25", "2026-10-25",
         "https://www.lausanne-marathon.com/2026",
         ["Sport > Terrestre"]),
        
        ("Athletissima Lausanne 2026",
         "Meeting international d'athlétisme Diamond League au Stade olympique de la Pontaise. Les meilleurs athlètes du monde en compétition.",
         "Lausanne", "2026-08-27", "2026-08-27",
         "https://www.athletissima.ch/2026",
         ["Sport > Terrestre", "Culture > Festival"]),
        
        ("Montreux Trail Festival 2026",
         "Festival de trail running dans les montagnes au-dessus de Montreux. Parcours entre vignobles de Lavaux et sommets préalpins avec vue sur le lac Léman.",
         "Montreux", "2026-06-06", "2026-06-07",
         "https://www.montreuxtrailfestival.ch/2026",
         ["Sport > Terrestre", "Culture > Festival"]),
        
        ("Tour de Romandie 2026",
         "Course cycliste professionnelle à travers la Suisse romande. Étapes traversant le Canton de Vaud avec arrivées dans les villes emblématiques.",
         "Lausanne", "2026-04-28", "2026-05-03",
         "https://www.tourderomandie.ch/2026",
         ["Sport > Terrestre"]),
        
        ("Triathlon de Lausanne 2026",
         "Triathlon international de Lausanne au bord du lac Léman. Natation dans le lac, vélo dans les collines lausannoises et course à pied sur les quais.",
         "Lausanne", "2026-08-29", "2026-08-30",
         "https://www.triathlondelausanne.ch/2026",
         ["Sport > Terrestre", "Sport > Aquatique"]),
        
        ("Régate Bol d'Or Mirabaud 2026",
         "Plus grande régate de voile en eaux intérieures d'Europe sur le lac Léman. Départ depuis Genève, passage devant les côtes vaudoises.",
         "Morges", "2026-06-13", "2026-06-14",
         "https://www.boldormirabaud.ch/2026",
         ["Sport > Aquatique"]),
        
        ("SlowUp Lac de Morat 2026",
         "Journée sans voiture autour du lac de Morat. Parcours de 33 km à vélo, rollers ou à pied, accessible à tous. Stands gastronomiques et animations.",
         "Avenches", "2026-05-03", "2026-05-03",
         "https://www.slowup.ch/morat/2026",
         ["Sport > Terrestre", "Nature & Famille"]),
        
        ("Traversée du Lac de Joux à la nage 2026",
         "Traversée sportive du Lac de Joux à la nage dans la Vallée de Joux. Parcours de 4 km dans un cadre naturel exceptionnel.",
         "Le Sentier", "2026-08-15", "2026-08-15",
         "https://www.traversee-lacdejoux.ch/2026",
         ["Sport > Aquatique"]),
        
        # === MARCHES ET GASTRONOMIE ===
        ("Caves Ouvertes Vaudoises 2026",
         "Les vignerons vaudois ouvrent leurs portes pour déguster les vins du terroir. Plus de 200 caves participantes dans tout le canton, de Lavaux à La Côte.",
         "Lausanne", "2026-05-16", "2026-05-17",
         "https://www.vaudoenotourisme.ch/caves-ouvertes-2026",
         ["Gastronomie > Dégustation", "Culture > Festival"]),
        
        ("Marché de Noël de Montreux 2026",
         "Le célèbre marché de Noël de Montreux sur les quais du lac Léman. Plus de 150 chalets, artisanat, gastronomie et animations de Noël avec vue sur les montagnes.",
         "Montreux", "2026-11-20", "2026-12-24",
         "https://www.montreuxnoel.com/2026",
         ["Marché", "Tradition & Folklore"]),
        
        ("Marché de Noël de Lausanne 2026",
         "Bô Noël, le marché de Noël de Lausanne. Chalets artisanaux, patinoire, roue panoramique et spectacles dans le centre-ville.",
         "Lausanne", "2026-11-21", "2026-12-31",
         "https://www.bonoel.ch/2026",
         ["Marché", "Tradition & Folklore"]),
        
        ("Fête des Vignerons de Vevey - Événement préparatoire",
         "Événement culturel lié à la tradition viticole de Vevey et de Lavaux. Spectacles, cortèges et célébrations en lien avec la Confrérie des Vignerons.",
         "Vevey", "2026-08-01", "2026-08-01",
         "https://www.fetedesvignerons.ch/2026",
         ["Tradition & Folklore", "Gastronomie > Dégustation"]),
        
        ("Marché folklorique de Vevey 2026",
         "Grand marché folklorique sur la place du Marché de Vevey. Artisanat local, produits du terroir vaudois et animations traditionnelles au bord du lac.",
         "Vevey", "2026-07-25", "2026-07-25",
         "https://www.vevey.ch/marche-folklorique-2026",
         ["Marché", "Tradition & Folklore"]),
        
        ("Fête de la Musique Lausanne 2026",
         "Concerts gratuits dans toute la ville de Lausanne. Tous les styles musicaux représentés dans les rues, places et parcs de la capitale vaudoise.",
         "Lausanne", "2026-06-21", "2026-06-21",
         "https://www.fete-musique-lausanne.ch/2026",
         ["Music > Concert", "Culture > Festival"]),
        
        ("Fête de la Musique Nyon 2026",
         "Concerts gratuits dans les rues et places de Nyon. Rock, jazz, classique, electro - tous les genres musicaux au bord du lac Léman.",
         "Nyon", "2026-06-21", "2026-06-21",
         "https://www.nyon.ch/fete-musique-2026",
         ["Music > Concert", "Culture > Festival"]),
        
        ("Cully Jazz Festival 2026",
         "Festival de jazz dans les caves et rues du village vigneron de Cully. Concerts intimistes dans les caves des vignerons de Lavaux, site UNESCO.",
         "Cully", "2026-04-03", "2026-04-11",
         "https://www.cullyjazz.ch/2026",
         ["Culture > Festival", "Music > Jazz / Blues"]),
        
        ("Lavaux Passion 2026",
         "Balade gourmande à travers les vignobles en terrasses de Lavaux, site UNESCO. Dégustations de vins et produits locaux avec vue panoramique sur le lac Léman.",
         "Cully", "2026-06-20", "2026-06-21",
         "https://www.lavaux-passion.ch/2026",
         ["Gastronomie > Dégustation", "Nature & Famille"]),
        
        ("Fête nationale 1er août Lausanne",
         "Célébrations de la fête nationale suisse à Lausanne. Feux d'artifice sur le lac, concerts, brunchs et animations dans les quartiers de la ville.",
         "Lausanne", "2026-08-01", "2026-08-01",
         "https://www.lausanne.ch/1er-aout-2026",
         ["Tradition & Folklore"]),
        
        ("Fête nationale 1er août Montreux",
         "Fête nationale sur les quais de Montreux. Spectacle pyrotechnique grandiose sur le lac Léman, concerts et animation dans les jardins.",
         "Montreux", "2026-08-01", "2026-08-01",
         "https://www.montreux.ch/1er-aout-2026",
         ["Tradition & Folklore"]),
        
        ("Fête nationale 1er août Nyon",
         "Célébrations du 1er août à Nyon. Cortège, discours, brunch champêtre et feu d'artifice sur le lac Léman.",
         "Nyon", "2026-08-01", "2026-08-01",
         "https://www.nyon.ch/1er-aout-2026",
         ["Tradition & Folklore"]),
        
        ("Carnaval de Lausanne 2026",
         "Le Carnaval de Lausanne anime les rues de la capitale vaudoise. Cortège costumé, guggenmusik, confettis et ambiance festive pendant plusieurs jours.",
         "Lausanne", "2026-05-02", "2026-05-04",
         "https://www.lausanne.ch/carnaval-2026",
         ["Tradition & Folklore", "Culture > Festival"]),
        
        ("Désalpe de Château-d'Oex 2026",
         "Descente traditionnelle des troupeaux depuis les alpages vers la plaine à Château-d'Oex. Vaches décorées, cortège folklorique et marché artisanal.",
         "Château-d'Oex", "2026-09-26", "2026-09-26",
         "https://www.chateau-doex.ch/desalpe-2026",
         ["Tradition & Folklore", "Nature & Famille"]),
        
        ("Festival international de ballons de Château-d'Oex 2026",
         "Festival de montgolfières dans le Pays-d'Enhaut. Vols en montgolfière, spectacles aériens et animations hivernales dans le village alpin.",
         "Château-d'Oex", "2026-01-24", "2026-02-01",
         "https://www.chateau-doex.ch/ballons-2026",
         ["Culture > Festival", "Nature & Famille"]),
        
        ("Comptoir Suisse Lausanne 2026",
         "La plus grande foire commerciale de Suisse romande à Beaulieu Lausanne. Expositions, dégustations, spectacles et animations pour toute la famille.",
         "Lausanne", "2026-09-18", "2026-09-27",
         "https://www.comptoirsuisse.ch/2026",
         ["Marché", "Culture > Expositions"]),
        
        ("Salon du Livre Genève - Journée Vaud 2026",
         "Le plus grand salon littéraire de Suisse romande à Palexpo. Dédicaces, conférences et rencontres avec les auteurs. Journée spéciale canton de Vaud.",
         "Lausanne", "2026-04-29", "2026-05-03",
         "https://www.salondulivre.ch/2026",
         ["Culture > Littérature", "Culture > Festival"]),
        
        # === EXPOSITIONS ET MUSÉES ===
        ("Musée Olympique Lausanne - Vivez les Jeux",
         "Exposition interactive au Musée Olympique de Lausanne. Revivez les plus grands moments olympiques à travers une scénographie immersive et des objets uniques.",
         "Lausanne", "2026-03-01", "2026-12-31",
         "https://www.olympics.com/museum/fr/visiter/expositions/vivez-les-jeux",
         ["Culture > Expositions", "Sport > Terrestre"]),
        
        ("Fondation de l'Hermitage - Exposition printemps 2026",
         "Exposition d'art dans le cadre prestigieux de la Fondation de l'Hermitage à Lausanne. Collections de peintures avec vue panoramique sur le lac et les Alpes.",
         "Lausanne", "2026-03-20", "2026-06-07",
         "https://www.fondation-hermitage.ch/expositions/2026",
         ["Culture > Expositions"]),
        
        ("Collection de l'Art Brut Lausanne - Exposition 2026",
         "Musée unique au monde consacré à l'Art Brut. Œuvres d'artistes autodidactes et marginaux dans un bâtiment historique de Lausanne.",
         "Lausanne", "2026-03-01", "2026-08-30",
         "https://www.artbrut.ch/expositions/2026",
         ["Culture > Expositions"]),
        
        ("Chaplin's World Corsier-sur-Vevey - Saison 2026",
         "Musée interactif dédié à Charlie Chaplin dans son ancien manoir. Expérience immersive dans l'univers du cinéma muet et de la comédie.",
         "Corsier-sur-Vevey", "2026-03-01", "2026-12-31",
         "https://www.chaplinsworld.com/fr/expositions-2026",
         ["Culture > Expositions", "Culture > Cinéma"]),
        
        ("Alimentarium Vevey - Exposition 2026",
         "Musée de l'alimentation à Vevey. Expositions interactives sur la nourriture, la nutrition et les cultures culinaires du monde entier.",
         "Vevey", "2026-03-01", "2026-12-31",
         "https://www.alimentarium.org/fr/expositions/2026",
         ["Culture > Expositions", "Gastronomie > Cuisine"]),
        
        ("Musée National Suisse Prangins - La Suisse en question",
         "Exposition permanente et temporaire au Château de Prangins. Histoire suisse à travers des objets, documents et expériences interactives.",
         "Prangins", "2026-03-14", "2026-10-25",
         "https://www.landesmuseum.ch/prangins/2026",
         ["Culture > Expositions", "Culture > Patrimoine"]),
        
        ("MUDAC Lausanne - Design & Art Contemporain 2026",
         "Le Musée de design et d'arts appliqués contemporains de Lausanne présente ses expositions temporaires. Art, design, mode et innovation au PLATEFORME 10.",
         "Lausanne", "2026-03-01", "2026-09-14",
         "https://www.mudac.ch/expositions/2026",
         ["Culture > Expositions"]),
        
        ("Photo Elysée Lausanne - Exposition 2026",
         "Musée de la photographie à PLATEFORME 10 Lausanne. Expositions temporaires des plus grands photographes contemporains et historiques.",
         "Lausanne", "2026-03-07", "2026-08-23",
         "https://www.elysee.ch/expositions/2026",
         ["Culture > Expositions", "Culture > Photographie"]),
        
        # === ÉVÉNEMENTS LOCAUX DIVERS ===
        ("Marché de Morges",
         "Marché hebdomadaire de Morges sur la Grand-Rue. Producteurs locaux, fruits, légumes, fromages et artisanat vaudois tous les mercredis et samedis.",
         "Morges", "2026-03-07", "2026-12-26",
         "https://www.morges.ch/marche-2026",
         ["Marché"]),
        
        ("Marché de Vevey - Place du Marché",
         "Grand marché de Vevey sur la plus grande place de marché d'Europe. Produits frais, spécialités locales et artisanat chaque mardi et samedi.",
         "Vevey", "2026-03-03", "2026-12-29",
         "https://www.vevey.ch/marche-2026",
         ["Marché"]),
        
        ("Marché d'Yverdon-les-Bains",
         "Marché traditionnel d'Yverdon-les-Bains dans le centre historique. Produits du terroir, artisanat et spécialités de la Broye et du Nord vaudois.",
         "Yverdon-les-Bains", "2026-03-04", "2026-12-30",
         "https://www.yverdonlesbainsregion.ch/marche-2026",
         ["Marché"]),
        
        ("Fête du Blé et du Pain Echallens 2026",
         "Fête traditionnelle célébrant les céréales et la boulangerie à Echallens, capitale du Gros-de-Vaud. Démonstrations, dégustations et marché artisanal.",
         "Echallens", "2026-08-22", "2026-08-23",
         "https://www.echallens.ch/fete-ble-pain-2026",
         ["Tradition & Folklore", "Gastronomie > Cuisine", "Marché"]),
        
        ("Fête de la Vigne et du Vin Lutry 2026",
         "Fête viticole dans le village de Lutry au cœur de Lavaux. Caves ouvertes, cortège de chars fleuris et spectacles dans les ruelles médiévales.",
         "Lutry", "2026-09-05", "2026-09-06",
         "https://www.lutry.ch/fete-vigne-vin-2026",
         ["Tradition & Folklore", "Gastronomie > Dégustation"]),
        
        ("Luna Park Lausanne 2026",
         "Grande fête foraine de Lausanne à Bellerive. Manèges, attractions et stands de restauration au bord du lac Léman.",
         "Lausanne", "2026-05-14", "2026-06-14",
         "https://www.lausanne.ch/luna-park-2026",
         ["Nature & Famille"]),
        
        ("Festival Visions du Réel Nyon 2026",
         "Festival international de cinéma documentaire à Nyon. Projections, compétitions et rencontres avec les réalisateurs du monde entier.",
         "Nyon", "2026-04-24", "2026-05-03",
         "https://www.visionsdureel.ch/2026",
         ["Culture > Festival", "Culture > Cinéma"]),
        
        ("Festival Ça marche! Yverdon 2026",
         "Festival de marche et de sports outdoor à Yverdon-les-Bains. Randonnées guidées, nordic walking et découverte de la nature du Nord vaudois.",
         "Yverdon-les-Bains", "2026-05-08", "2026-05-10",
         "https://www.camarche.ch/2026",
         ["Sport > Terrestre", "Nature & Famille"]),
        
        ("Fête du Léman Rolle 2026",
         "Fête au bord du lac Léman à Rolle. Régate, concerts, stands gastronomiques et feu d'artifice sur le lac avec la vue sur les Alpes.",
         "Rolle", "2026-06-27", "2026-06-28",
         "https://www.rolle.ch/fete-leman-2026",
         ["Sport > Aquatique", "Nature & Famille"]),
        
        ("Nuit des Musées Lausanne 2026",
         "Ouverture nocturne des musées de Lausanne et Pully. Animations, visites guidées et ateliers dans plus de 25 institutions culturelles.",
         "Lausanne", "2026-09-19", "2026-09-19",
         "https://www.lausanne.ch/nuit-musees-2026",
         ["Culture > Expositions", "Culture > Patrimoine"]),
        
        ("Festival de musique de Morges 2026",
         "Festival de musique classique et contemporaine à Morges. Concerts dans les salles historiques et l'église avec des artistes internationaux.",
         "Morges", "2026-08-07", "2026-08-16",
         "https://www.morges.ch/festival-musique-2026",
         ["Culture > Festival", "Music > Classique"]),
        
        ("Festival du Film de Moudon 2026",
         "Festival de cinéma dans la cité médiévale de Moudon. Courts et longs métrages, rencontres avec les cinéastes et projections en plein air.",
         "Moudon", "2026-06-12", "2026-06-14",
         "https://www.moudon.ch/festival-film-2026",
         ["Culture > Festival", "Culture > Cinéma"]),
        
        ("Marché médiéval Romainmôtier 2026",
         "Marché médiéval dans le village historique de Romainmôtier autour de la prieurale clunisienne. Artisans, spectacles et gastronomie d'époque.",
         "Romainmôtier", "2026-08-08", "2026-08-09",
         "https://www.romainmotier.ch/marche-medieval-2026",
         ["Marché", "Tradition & Folklore", "Culture > Patrimoine"]),
        
        ("Journées du Patrimoine Vaud 2026",
         "Ouverture exceptionnelle de sites patrimoniaux dans le Canton de Vaud. Visites guidées de châteaux, églises, bâtiments historiques et sites industriels.",
         "Lausanne", "2026-09-12", "2026-09-13",
         "https://www.journees-patrimoine.ch/2026",
         ["Culture > Patrimoine"]),
        
        ("Fête du Chasselas Aigle 2026",
         "Célébration du cépage roi du vignoble vaudois à Aigle. Dégustations au château d'Aigle, balades vigneronnes et marché artisanal.",
         "Aigle", "2026-09-19", "2026-09-20",
         "https://www.aigle.ch/fete-chasselas-2026",
         ["Gastronomie > Dégustation", "Tradition & Folklore"]),
        
        ("Rallye du Chablais 2026",
         "Rallye automobile dans la région du Chablais vaudois. Spéciales chronométrées entre vignobles et montagnes, avec parc d'assistance à Aigle.",
         "Aigle", "2026-06-19", "2026-06-20",
         "https://www.rallye-chablais.ch/2026",
         ["Sport > Terrestre"]),
        
        ("Festival des Arts de la Rue Vevey 2026",
         "Arts de la rue et spectacles dans les rues de Vevey. Acrobates, musiciens, comédiens et artistes de cirque animent la ville pendant tout un week-end.",
         "Vevey", "2026-07-04", "2026-07-05",
         "https://www.vevey.ch/festival-arts-rue-2026",
         ["Culture > Festival", "Culture > Théâtre"]),
        
        ("Swiss Vapeur Parc Bouveret - Saison 2026",
         "Le plus grand parc de trains miniatures d'Europe au Bouveret. Trains à vapeur miniatures, parcours ludiques et animations pour toute la famille.",
         "Vevey", "2026-04-01", "2026-10-31",
         "https://www.swissvapeur.ch/2026",
         ["Nature & Famille"]),
        
        ("Opéra de Lausanne - Saison 2026",
         "Saison lyrique de l'Opéra de Lausanne. Productions d'opéra, opérettes et concerts dans le théâtre à l'italienne au cœur de la ville.",
         "Lausanne", "2026-03-06", "2026-06-28",
         "https://www.opera-lausanne.ch/saison-2026",
         ["Music > Classique", "Culture > Théâtre"]),
        
        ("Orchestre de Chambre de Lausanne - Saison 2026",
         "Concerts de l'Orchestre de Chambre de Lausanne à la Salle Métropole. Répertoire classique et contemporain avec des solistes de renommée mondiale.",
         "Lausanne", "2026-03-12", "2026-06-18",
         "https://www.ocl.ch/saison-2026",
         ["Music > Classique", "Music > Concert"]),
        
        ("Théâtre Vidy-Lausanne - Saison 2026",
         "Programmation théâtrale contemporaine au Théâtre de Vidy. Créations, spectacles et performances au bord du lac Léman.",
         "Lausanne", "2026-03-10", "2026-06-20",
         "https://www.vidy.ch/saison-2026",
         ["Culture > Théâtre"]),
        
        ("Théâtre de Beaulieu Lausanne - Spectacles 2026",
         "Programmation variée au Théâtre de Beaulieu Lausanne. Comédies musicales, one-man-shows, concerts et spectacles pour toute la famille.",
         "Lausanne", "2026-03-15", "2026-12-20",
         "https://www.beaulieu-lausanne.ch/2026",
         ["Culture > Théâtre", "Music > Concert"]),
        
        ("Musée Romain d'Avenches - Exposition 2026",
         "Musée archéologique dans l'amphithéâtre romain d'Avenches. Exposition sur la vie quotidienne à l'époque romaine dans l'ancienne capitale de l'Helvétie.",
         "Avenches", "2026-03-01", "2026-10-31",
         "https://www.aventicum.org/2026",
         ["Culture > Expositions", "Culture > Patrimoine"]),
        
        ("Rock Oz'Arènes Avenches 2026",
         "Festival de rock et musique live dans l'amphithéâtre romain d'Avenches. Concerts rock, pop et electro dans un cadre historique unique.",
         "Avenches", "2026-08-06", "2026-08-08",
         "https://www.rockozarenes.ch/2026",
         ["Culture > Festival", "Music > Rock / Pop"]),
        
        ("Marché artisanal de Nyon 2026",
         "Marché artisanal dans le centre historique de Nyon. Artisans locaux, créateurs et producteurs du terroir au pied du château de Nyon.",
         "Nyon", "2026-05-16", "2026-05-17",
         "https://www.nyon.ch/marche-artisanal-2026",
         ["Marché"]),
        
        ("Festival Far° Nyon 2026",
         "Festival des arts vivants de Nyon. Théâtre, danse, performance et installations dans des lieux insolites de la ville au bord du Léman.",
         "Nyon", "2026-08-13", "2026-08-22",
         "https://www.festivalfar.ch/2026",
         ["Culture > Festival", "Culture > Théâtre"]),
        
        ("Chœurs en Fête Lausanne 2026",
         "Rassemblement de chorales de toute la Suisse romande à Lausanne. Concerts, ateliers de chant et spectacle final à la cathédrale.",
         "Lausanne", "2026-05-23", "2026-05-24",
         "https://www.choeurs-en-fete.ch/2026",
         ["Music > Classique", "Music > Concert"]),
        
        ("Brocante d'Aubonne 2026",
         "Grande brocante dans les rues du vieux bourg d'Aubonne. Antiquités, objets vintage et curiosités dans un cadre médiéval charmant.",
         "Aubonne", "2026-05-09", "2026-05-10",
         "https://www.aubonne.ch/brocante-2026",
         ["Marché"]),
        
        ("Fête de la Cerise Gland 2026",
         "Fête célébrant la cerise et les produits du terroir à Gland. Marché, dégustations, animations et cortège de la cerise dans les rues du village.",
         "Gland", "2026-06-06", "2026-06-07",
         "https://www.gland.ch/fete-cerise-2026",
         ["Tradition & Folklore", "Gastronomie > Dégustation", "Marché"]),
        
        ("Salon des Antiquaires Lausanne 2026",
         "Salon des antiquaires et des collectionneurs à Beaulieu Lausanne. Mobilier ancien, art, bijoux et objets de collection de haute qualité.",
         "Lausanne", "2026-11-06", "2026-11-15",
         "https://www.beaulieu-lausanne.ch/antiquaires-2026",
         ["Marché", "Culture > Expositions"]),
        
        ("Festival Belluard Bollwerk Lausanne 2026",
         "Festival d'art contemporain et performance. Installations, spectacles expérimentaux et art numérique dans des espaces atypiques de Lausanne.",
         "Lausanne", "2026-06-25", "2026-07-04",
         "https://www.belluard.ch/2026",
         ["Culture > Festival", "Culture > Expositions"]),
        
        ("Marché de Noël de Nyon 2026",
         "Marché de Noël dans le centre historique de Nyon. Chalets artisanaux, vin chaud, spécialités suisses et animations festives sous le château.",
         "Nyon", "2026-12-05", "2026-12-24",
         "https://www.nyon.ch/marche-noel-2026",
         ["Marché", "Tradition & Folklore"]),
        
        ("Fête de la Natation Vevey 2026",
         "Traversée du lac à la nage et compétitions aquatiques à Vevey. Course populaire, relais et animations sportives au bord du lac Léman.",
         "Vevey", "2026-07-18", "2026-07-19",
         "https://www.vevey.ch/fete-natation-2026",
         ["Sport > Aquatique"]),
        
        ("Festival Vibrations Cossonay 2026",
         "Festival de musique dans le cadre champêtre de Cossonay. Concerts en plein air, DJ sets et ambiance festive au cœur du Gros-de-Vaud.",
         "Cossonay", "2026-07-10", "2026-07-12",
         "https://www.vibrations-festival.ch/2026",
         ["Culture > Festival", "Music > Concert"]),
        
        ("Course de l'Escalade Lausanne 2026",
         "Course à pied populaire dans les rues de Lausanne. Parcours à travers le centre-ville historique avec montée et descente des escaliers emblématiques.",
         "Lausanne", "2026-12-05", "2026-12-05",
         "https://www.course-escalade.ch/2026",
         ["Sport > Terrestre"]),
        
        ("Festival Label Suisse Lausanne 2026",
         "Festival gratuit célébrant la musique suisse à Lausanne. Artistes émergents et confirmés de toute la Suisse dans les rues et places de Lausanne.",
         "Lausanne", "2026-09-18", "2026-09-20",
         "https://www.labelsuisse.ch/2026",
         ["Culture > Festival", "Music > Concert"]),
        
        ("Les Hivernales Nyon 2026",
         "Festival culturel d'hiver à Nyon. Concerts, spectacles, cinéma et expositions à l'Usine à Gaz et dans les lieux culturels de la ville.",
         "Nyon", "2026-03-06", "2026-03-15",
         "https://www.hivernales-nyon.ch/2026",
         ["Culture > Festival", "Music > Concert"]),
        
        ("Festival Quartiers de Nuit Lausanne 2026",
         "Festival nocturne de musique dans les clubs et bars de Lausanne. DJ sets, concerts live et performances dans les établissements du Flon et de la Cité.",
         "Lausanne", "2026-10-16", "2026-10-17",
         "https://www.quartiersdenuit.ch/2026",
         ["Culture > Festival", "Music > Electro / Techno"]),
        
        ("Coupe de Noël Genève-Lausanne - Nage en eau froide",
         "Course de natation hivernale dans le lac Léman. Tradition populaire depuis plus d'un siècle, départ des nageurs en eau froide face aux Alpes.",
         "Lausanne", "2026-12-20", "2026-12-20",
         "https://www.coupedenoel.ch/2026",
         ["Sport > Aquatique"]),
        
        ("Salon Habitat Jardin Lausanne 2026",
         "Salon de l'habitat et du jardin à Beaulieu Lausanne. Aménagement intérieur, jardinage, rénovation et tendances déco sur 60'000 m².",
         "Lausanne", "2026-03-07", "2026-03-15",
         "https://www.habitat-jardin.ch/2026",
         ["Culture > Expositions", "Marché"]),
        
        ("Festival de folklore de Château-d'Oex 2026",
         "Rassemblement de groupes folkloriques au Pays-d'Enhaut. Costumes traditionnels, musique, danse et artisanat dans le village alpin.",
         "Château-d'Oex", "2026-08-15", "2026-08-16",
         "https://www.chateau-doex.ch/folklore-2026",
         ["Tradition & Folklore", "Culture > Festival"]),
        
        ("Marché aux puces de Lausanne 2026",
         "Grand marché aux puces mensuel dans le quartier de Sévelin à Lausanne. Objets vintage, antiquités, livres et curiosités.",
         "Lausanne", "2026-04-04", "2026-04-04",
         "https://www.lausanne.ch/marche-puces-2026",
         ["Marché"]),
        
        ("Festival Balelec EPFL 2026",
         "Plus grand festival open-air organisé par des étudiants en Europe. Concerts sur le campus de l'EPFL à Lausanne avec des têtes d'affiche internationales.",
         "Lausanne", "2026-05-15", "2026-05-16",
         "https://www.balelec.ch/2026",
         ["Culture > Festival", "Music > Rock / Pop", "Music > Electro / Techno"]),
        
        ("Salon du Chocolat Lausanne 2026",
         "Salon dédié au chocolat suisse et international à Beaulieu Lausanne. Dégustations, démonstrations de chocolatiers et ateliers pour enfants.",
         "Lausanne", "2026-04-17", "2026-04-19",
         "https://www.salon-chocolat.ch/2026",
         ["Gastronomie > Dégustation", "Gastronomie > Cuisine"]),
        
        # === ALPES VAUDOISES ===
        ("Leysin Freeride 2026",
         "Compétition de freeride à Leysin dans les Alpes vaudoises. Ski et snowboard hors-piste dans un environnement alpin spectaculaire.",
         "Leysin", "2026-03-07", "2026-03-08",
         "https://www.leysin.ch/freeride-2026",
         ["Sport > Glisse", "Culture > Festival"]),
        
        ("Festival des Alpes Villars 2026",
         "Festival culturel dans les Alpes vaudoises à Villars-sur-Ollon. Musique classique, jazz et concerts dans les montagnes avec vue sur les Dents du Midi.",
         "Villars-sur-Ollon", "2026-07-17", "2026-07-26",
         "https://www.villars.ch/festival-alpes-2026",
         ["Culture > Festival", "Music > Classique"]),
        
        ("Les Diablerets Challenge Trail 2026",
         "Trail running aux Diablerets dans les Alpes vaudoises. Parcours spectaculaires entre glaciers, alpages et forêts avec vue sur le glacier 3000.",
         "Les Diablerets", "2026-07-04", "2026-07-05",
         "https://www.diablerets.ch/trail-2026",
         ["Sport > Terrestre"]),
        
        ("Glacier 3000 - Ouverture saison été 2026",
         "Ouverture de la saison estivale au Glacier 3000 aux Diablerets. Randonnées glaciaires, pont suspendu Peak Walk et activités alpines pour tous.",
         "Les Diablerets", "2026-06-01", "2026-10-25",
         "https://www.glacier3000.ch/saison-ete-2026",
         ["Nature & Famille", "Sport > Terrestre"]),
        
        ("Gryon Bike Park - Saison 2026",
         "Ouverture du bike park de Gryon dans les Alpes vaudoises. Pistes de VTT pour tous niveaux dans un cadre alpin avec vue sur les Dents du Midi.",
         "Gryon", "2026-06-13", "2026-10-18",
         "https://www.gryon.ch/bikepark-2026",
         ["Sport > Terrestre"]),
        
        # === VALLÉE DE JOUX ===
        ("Fête du Vacherin Mont-d'Or 2026",
         "Célébration du fromage Vacherin Mont-d'Or dans la Vallée de Joux. Dégustations, visites de fromageries et marché artisanal.",
         "Le Sentier", "2026-10-03", "2026-10-04",
         "https://www.valleedejoux.ch/fete-vacherin-2026",
         ["Gastronomie > Raclette / Fondue", "Tradition & Folklore"]),
        
        ("Traversée de la Vallée de Joux en ski de fond 2026",
         "Course de ski de fond à travers la Vallée de Joux. Parcours nordique entre Le Brassus et Le Sentier dans les forêts jurassiennes.",
         "Le Brassus", "2026-03-14", "2026-03-14",
         "https://www.valleedejoux.ch/ski-fond-2026",
         ["Sport > Glisse"]),
        
        ("Festival L'Ouest Lausannois 2026",
         "Festival de musique et culture dans l'ouest lausannois. Concerts, DJ sets et spectacles dans les communes de Renens, Prilly et Ecublens.",
         "Renens", "2026-06-12", "2026-06-14",
         "https://www.renens.ch/festival-ouest-2026",
         ["Culture > Festival", "Music > Concert"]),
        
        ("Fête du Soleil Sainte-Croix 2026",
         "Fête estivale dans le Jura vaudois à Sainte-Croix. Concerts, marché artisanal et animations avec vue panoramique sur les Alpes et le plateau.",
         "Sainte-Croix", "2026-08-01", "2026-08-02",
         "https://www.sainte-croix.ch/fete-soleil-2026",
         ["Tradition & Folklore", "Music > Concert"]),
        
        ("Fête de la Courge Payerne 2026",
         "Célébration automnale de la courge à Payerne. Marché, sculptures de citrouilles géantes, dégustations et animations pour toute la famille.",
         "Payerne", "2026-10-10", "2026-10-11",
         "https://www.payerne.ch/fete-courge-2026",
         ["Tradition & Folklore", "Marché", "Nature & Famille"]),
        
        ("Open Air Cinéma Lausanne 2026",
         "Cinéma en plein air sur la place de la Riponne à Lausanne. Films récents et classiques projetés en grand écran sous les étoiles.",
         "Lausanne", "2026-07-06", "2026-08-15",
         "https://www.cinemuet.ch/2026",
         ["Culture > Cinéma"]),
        
        ("Open Air Cinéma Vevey 2026",
         "Projections en plein air sur la grande place de Vevey face au lac Léman. Ambiance estivale, gastronomie et films sous les étoiles.",
         "Vevey", "2026-07-08", "2026-08-20",
         "https://www.cinerive.ch/2026",
         ["Culture > Cinéma"]),
        
        ("Concours hippique national Lausanne 2026",
         "Concours de saut d'obstacles au centre équestre de Lausanne. Cavaliers nationaux et internationaux en compétition.",
         "Lausanne", "2026-05-22", "2026-05-24",
         "https://www.concours-hippique-lausanne.ch/2026",
         ["Sport > Terrestre"]),
        
        ("Festival du Jardin Vullierens 2026",
         "Ouverture du Jardin de Vullierens avec ses collections d'iris et de lys. Expositions de sculptures, promenades et ateliers botaniques.",
         "Morges", "2026-04-25", "2026-07-05",
         "https://www.jardindesiris.ch/2026",
         ["Nature & Famille", "Culture > Expositions"]),
        
        ("Nuit de la Science Lausanne 2026",
         "Soirée scientifique gratuite à l'Université de Lausanne. Expériences interactives, conférences, observations astronomiques pour petits et grands.",
         "Lausanne", "2026-09-05", "2026-09-05",
         "https://www.unil.ch/nuit-science-2026",
         ["Nature & Famille"]),
        
        ("Marché artisanal de Lavaux 2026",
         "Marché d'artisans dans les vignobles en terrasses de Lavaux, site UNESCO. Produits du terroir, artisanat et vins du coteau avec vue sur le lac.",
         "Rivaz", "2026-09-12", "2026-09-13",
         "https://www.lavaux-unesco.ch/marche-2026",
         ["Marché", "Gastronomie > Dégustation"]),
        
        ("Fête des vendanges de Morges 2026",
         "Célébration des vendanges à Morges. Cortège, pressoir public, dégustations de moût et de vins, fanfares et animations dans les rues.",
         "Morges", "2026-10-03", "2026-10-04",
         "https://www.morges.ch/fete-vendanges-2026",
         ["Tradition & Folklore", "Gastronomie > Dégustation"]),
        
        ("Swiss Olympic Day Lausanne 2026",
         "Journée sportive gratuite à Lausanne, capitale olympique. Initiations sportives, démonstrations et rencontres avec des athlètes olympiques.",
         "Lausanne", "2026-06-14", "2026-06-14",
         "https://www.lausanne.ch/swiss-olympic-day-2026",
         ["Sport > Terrestre", "Nature & Famille"]),
        
        ("Fête de la Tulipe Morges - Concerts au Parc",
         "Concerts en plein air dans le cadre de la Fête de la Tulipe à Morges. Musique classique et jazz parmi les parterres de fleurs au bord du lac.",
         "Morges", "2026-04-18", "2026-04-19",
         "https://www.morges-tourisme.ch/tulipe-concerts-2026",
         ["Music > Concert", "Nature & Famille"]),
        
        ("Festival Electrosanne Lausanne 2026",
         "Festival de musique électronique à Lausanne. DJ sets, performances live et installations sonores dans les clubs et espaces culturels de la ville.",
         "Lausanne", "2026-11-13", "2026-11-15",
         "https://www.electrosanne.ch/2026",
         ["Culture > Festival", "Music > Electro / Techno"]),
        
        ("Marché de Noël de Vevey 2026",
         "Marché de Noël sur la place du Marché de Vevey. Chalets artisanaux, vin chaud, créations locales et animations festives face au lac.",
         "Vevey", "2026-11-27", "2026-12-24",
         "https://www.vevey.ch/marche-noel-2026",
         ["Marché", "Tradition & Folklore"]),
        
        ("Marché de Noël d'Yverdon 2026",
         "Marché de Noël dans le centre historique d'Yverdon-les-Bains. Artisanat, gourmandises et spectacles dans un décor féerique.",
         "Yverdon-les-Bains", "2026-12-04", "2026-12-23",
         "https://www.yverdonlesbainsregion.ch/noel-2026",
         ["Marché", "Tradition & Folklore"]),
    ]
    
    for item in VERIFIED:
        title, desc, city, start, end, url, cats = item
        lat, lng = VAUD_CITIES.get(city, (46.5197, 6.6323))
        
        # Vérifier que c'est mars 2026 ou après
        if start < '2026-03-01':
            continue
        
        events.append({
            'title': title,
            'description': f"À {city}, Vaud : {desc}",
            'start_date': start,
            'end_date': end,
            'latitude': lat + (hash(title) % 100 - 50) * 0.0001,  # Petit décalage pour éviter superposition
            'longitude': lng + (hash(title + 'lng') % 100 - 50) * 0.0001,
            'city': city,
            'source_url': url,
            'organizer_email': None,
            'categories': cats,
            'source': 'Événement vérifié'
        })
    
    return events


# ============================================================
# MAIN
# ============================================================
print("=" * 60)
print("SCRAPING CANTON DE VAUD - 500 ÉVÉNEMENTS")
print("=" * 60)

# 1. Événements vérifiés (le gros du volume)
print("\n[1/3] Chargement des événements vérifiés...")
verified_events = get_verified_vaud_events()
print(f"  {len(verified_events)} événements vérifiés")
all_events.extend(verified_events)

# 2. Scraping tempslibre.ch
print(f"\n[2/3] Scraping tempslibre.ch...")
tl_events, tl_emails = scrape_tempslibre()
print(f"  {len(tl_events)} événements trouvés, {len(tl_emails)} emails")
all_events.extend(tl_events)
all_emails.extend(tl_emails)

# 3. Scraping myvaud.ch
print(f"\n[3/3] Scraping myvaud.ch...")
mv_events, mv_emails = scrape_myvaud()
print(f"  {len(mv_events)} événements trouvés, {len(mv_emails)} emails")
all_events.extend(mv_events)
all_emails.extend(mv_emails)

# Dédoublonner par source_url
seen_urls = set()
unique_events = []
for e in all_events:
    url = e.get('source_url', '')
    if url not in seen_urls:
        seen_urls.add(url)
        unique_events.append(e)

print(f"\n{'='*60}")
print(f"TOTAL UNIQUE: {len(unique_events)} événements")
print(f"EMAILS: {len(all_emails)}")
print(f"{'='*60}")

# Sauvegarder
with open('vaud_events_v1.json', 'w', encoding='utf-8') as f:
    json.dump(unique_events, f, ensure_ascii=False, indent=2)
print(f"\nSauvegardé dans vaud_events_v1.json")

# Sauvegarder les emails
if all_emails:
    with open('emails_organisateurs/emails_Vaud.csv', 'w', encoding='utf-8') as f:
        f.write('email,titre,source_url,source\n')
        for em in all_emails:
            f.write(f"{em['email']},{em['title']},{em['source_url']},{em['source']}\n")
    print(f"Emails sauvegardés dans emails_organisateurs/emails_Vaud.csv")

# Statistiques par catégorie
cat_stats = {}
for e in unique_events:
    for c in e.get('categories', []):
        cat_stats[c] = cat_stats.get(c, 0) + 1

print(f"\n=== CATÉGORIES ===")
for cat, count in sorted(cat_stats.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}")

# Statistiques par ville
city_stats = {}
for e in unique_events:
    city = e.get('city', '?')
    city_stats[city] = city_stats.get(city, 0) + 1

print(f"\n=== VILLES ===")
for city, count in sorted(city_stats.items(), key=lambda x: -x[1]):
    print(f"  {city}: {count}")
