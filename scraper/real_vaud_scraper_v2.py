"""
Scraper V2 - Plus de sites d'événements réels pour le Canton de Vaud
Sites ciblés:
1. eventfrog.ch - Plateforme suisse majeure d'événements
2. lausanne.ch - Agenda de Lausanne
3. loisirs.ch - Loisirs en Suisse romande
4. agenda.ch - Agrégateur suisse d'événements 
5. bfrenchcomic.com et autres festivals connus
6. myswitzerland.com - Tourisme Suisse

Délai: 8 secondes entre requêtes
"""
import requests
from bs4 import BeautifulSoup
import sys, io, json, time, re, random
from urllib.parse import urljoin, urlparse

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr-CH,fr;q=0.9,en;q=0.5',
}
DELAY = 8

VAUD_COORDS = {
    'lausanne': (46.5197, 6.6323),
    'montreux': (46.4312, 6.9107),
    'vevey': (46.4628, 6.8432),
    'nyon': (46.3833, 6.2398),
    'morges': (46.5108, 6.4989),
    'yverdon': (46.7784, 6.6411),
    'aigle': (46.3183, 6.9719),
    'château-d\'oex': (46.4748, 7.1360),
    'payerne': (46.8207, 6.9381),
    'moudon': (46.6686, 6.7947),
    'rolle': (46.4594, 6.3367),
    'cully': (46.4887, 6.7294),
    'pully': (46.5097, 6.6611),
    'renens': (46.5345, 6.5874),
    'ecublens': (46.5275, 6.5597),
    'bex': (46.2487, 6.9997),
    'villeneuve': (46.3963, 6.9267),
    'la tour-de-peilz': (46.4512, 6.8582),
    'blonay': (46.4634, 6.8911),
    'saint-cergue': (46.4467, 6.1578),
    'rougemont': (46.4889, 7.2083),
    'leysin': (46.3417, 7.0133),
    'villars': (46.2989, 7.0528),
    'orbe': (46.7269, 6.5317),
    'cossonay': (46.6136, 6.5058),
    'echallens': (46.6425, 6.6336),
    'avenches': (46.8819, 7.0411),
    'grandson': (46.8097, 6.6461),
    'prilly': (46.5287, 6.6011),
    'lavaux': (46.4890, 6.7300),
    'lutry': (46.5050, 6.6850),
    'crissier': (46.5450, 6.5800),
    'bussigny': (46.5520, 6.5560),
    'gland': (46.4220, 6.2720),
    'aubonne': (46.4930, 6.3880),
    'la sarraz': (46.6580, 6.5100),
    'vallorbe': (46.7130, 6.3730),
    'sainte-croix': (46.8220, 6.5050),
    'le sentier': (46.6100, 6.2330),
    'chexbres': (46.4830, 6.7810),
}

def get_coords(lieu):
    lieu_l = (lieu or '').lower()
    for city, (lat, lon) in VAUD_COORDS.items():
        if city in lieu_l:
            return (lat + random.uniform(-0.003, 0.003), lon + random.uniform(-0.003, 0.003))
    return (46.55 + random.uniform(-0.08, 0.08), 6.60 + random.uniform(-0.15, 0.15))

def classify_event(title, desc=''):
    text = (title + ' ' + desc).lower()
    cats = []
    
    if any(w in text for w in ['concert', 'musique', 'orchestre', 'récital', 'chorale']):
        if any(w in text for w in ['classique', 'symphoni', 'orchestre', 'quatuor', 'baroque', 'opéra']):
            cats.append('Music > Classique')
        elif any(w in text for w in ['jazz', 'swing', 'blues']):
            cats.append('Music > Jazz / Blues')
        elif any(w in text for w in ['rock', 'metal', 'punk']):
            cats.append('Music > Rock / Metal')
        elif any(w in text for w in ['electro', 'techno', 'dj', 'house']):
            cats.append('Music > Electro / DJ')
        else:
            cats.append('Music > Concert')
    
    if 'festival' in text:
        cats.append('Music > Festival')
    
    if any(w in text for w in ['théâtre', 'comédie', 'pièce', 'spectacle']):
        cats.append('Culture > Théâtre')
    if any(w in text for w in ['exposition', 'expo ', 'vernissage', 'musée']) and \
       any(w in text for w in ['exposition', 'expo ', 'vernissage', 'galerie', 'oeuvre', 'art ', 'peinture', 'sculpture', 'musée']):
        cats.append('Culture > Expositions')
    if any(w in text for w in ['cinéma', 'film', 'projection']):
        cats.append('Culture > Cinéma')
    if any(w in text for w in ['conférence', 'colloque', 'séminaire']):
        cats.append('Culture > Conférence')
    if any(w in text for w in ['atelier', 'workshop', 'cours ']):
        cats.append('Culture > Atelier')
    if any(w in text for w in ['danse', 'ballet', 'chorégraph']):
        cats.append('Culture > Danse')
    
    if any(w in text for w in ['dégustation', 'cave', 'vigneron', 'oenolog', 'vendang']):
        cats.append('Gastronomie > Dégustation')
    if any(w in text for w in ['marché', 'brocante', 'foire']):
        cats.append('Gastronomie > Marché')
    if any(w in text for w in ['gastronomie', 'culinaire', 'cuisine', 'foodtruck', 'brunch', 'fondue', 'raclette']):
        cats.append('Gastronomie > Gastronomie')
    
    if any(w in text for w in ['randonnée', 'rando', 'balade', 'marche ', 'trek']):
        cats.append('Sport > Terrestre')
    if any(w in text for w in ['course', 'marathon', 'trail', 'running']):
        cats.append('Sport > Terrestre')
    if any(w in text for w in ['ski', 'snowboard', 'luge', 'neige']):
        cats.append('Sport > Glisse')
    if any(w in text for w in ['natation', 'voile', 'aviron', 'kayak', 'piscine']):
        cats.append('Sport > Aquatique')
    
    if any(w in text for w in ['fête', 'carnaval', 'kermesse']):
        cats.append('Famille > Fêtes')
    if any(w in text for w in ['enfant', 'famille', 'junior', 'jeunesse']):
        cats.append('Famille > Enfants')
    
    # Max 3 catégories
    if not cats:
        cats.append('Culture > Divers')
    return cats[:3]

def find_emails(soup):
    emails = set()
    for a in soup.find_all('a', href=True):
        if 'mailto:' in a['href']:
            email = a['href'].replace('mailto:', '').split('?')[0].strip()
            if '@' in email and '.' in email:
                emails.add(email.lower())
    text = soup.get_text()
    found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    for em in found:
        em = em.lower().strip('.')
        if not any(x in em for x in ['example.com', 'test.com', 'sentry.io', 'w3.org', '.png', '.jpg', '.gif', '.css', '.js']):
            emails.add(em)
    return list(emails)

def clean_description(text, title):
    """Nettoyer et remanier la description"""
    if not text:
        return f"Découvrez '{title}', un événement à ne pas manquer dans le Canton de Vaud."
    
    # Enlever les menus de navigation
    text = re.sub(r'AccueilVaud\w+', '', text)
    text = re.sub(r'Catégories\s*:.*?(?=[A-Z])', '', text)
    text = re.sub(r'©.*?(?=\d|[A-Z])', '', text)
    text = re.sub(r'En cours.*?(?=\d|[A-Z])', '', text)
    text = re.sub(r'En savoir plus', '', text)
    text = re.sub(r'VivreDécouvrir.*?En savoir plus', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) < 20:
        return f"Découvrez '{title}', un événement à ne pas manquer dans le Canton de Vaud."
    
    if len(text) > 400:
        text = text[:397] + '...'
    
    return text


def scrape_eventfrog():
    """Scraper eventfrog.ch pour le Canton de Vaud"""
    events = []
    emails_found = []
    seen = set()
    
    # eventfrog.ch a une structure API-like
    base_urls = [
        'https://eventfrog.ch/fr/p/lausanne.html',
        'https://eventfrog.ch/fr/p/montreux.html',
        'https://eventfrog.ch/fr/p/vevey.html',
        'https://eventfrog.ch/fr/p/nyon.html',
        'https://eventfrog.ch/fr/p/morges.html',
        'https://eventfrog.ch/fr/p/yverdon-les-bains.html',
        'https://eventfrog.ch/fr/p/aigle.html',
        'https://eventfrog.ch/fr/p/rolle.html',
        'https://eventfrog.ch/fr/p/pully.html',
        'https://eventfrog.ch/fr/p/renens.html',
    ]
    
    for base_url in base_urls:
        city = base_url.split('/p/')[1].replace('.html','')
        print(f"\n  eventfrog.ch/{city}")
        time.sleep(DELAY)
        
        try:
            r = requests.get(base_url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"    Status {r.status_code}")
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Chercher les liens d'événements
            event_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(base_url, href)
                if 'eventfrog.ch/fr/p/' in full_url and full_url != base_url:
                    if '/e/' in full_url or re.search(r'/\d+', full_url):
                        if full_url not in seen:
                            seen.add(full_url)
                            event_links.append(full_url)
            
            # Aussi chercher les cartes d'événements
            for div in soup.find_all(['div', 'article'], class_=re.compile(r'event|card|item', re.I)):
                a = div.find('a', href=True)
                if a:
                    full_url = urljoin(base_url, a['href'])
                    if full_url not in seen and 'eventfrog.ch' in full_url:
                        seen.add(full_url)
                        event_links.append(full_url)
            
            print(f"    {len(event_links)} liens trouvés")
            
            for evt_url in event_links[:15]:
                time.sleep(DELAY)
                try:
                    r2 = requests.get(evt_url, headers=HEADERS, timeout=15)
                    if r2.status_code != 200:
                        continue
                    
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    
                    title = ''
                    for el in soup2.find_all(['h1', 'h2']):
                        t = el.get_text(strip=True)
                        if len(t) > 5 and len(t) < 200:
                            title = t
                            break
                    if not title:
                        continue
                    
                    desc = ''
                    for el in soup2.find_all(['div', 'p'], class_=re.compile(r'desc|content|detail|text|body', re.I)):
                        t = el.get_text(strip=True)
                        if len(t) > 30:
                            desc = t[:500]
                            break
                    
                    lieu = ''
                    for el in soup2.find_all(['span', 'div', 'address'], class_=re.compile(r'loc|venue|address|place', re.I)):
                        t = el.get_text(strip=True)
                        if t and len(t) < 200:
                            lieu = t
                            break
                    
                    all_text = soup2.get_text()
                    start_date = None
                    m = re.search(r'(\d{1,2})[./](\d{1,2})[./](2026)', all_text)
                    if m:
                        start_date = f"2026-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
                    if not start_date:
                        mois_fr = {'janvier':'01','février':'02','mars':'03','avril':'04','mai':'05','juin':'06',
                                   'juillet':'07','août':'08','septembre':'09','octobre':'10','novembre':'11','décembre':'12'}
                        m = re.search(r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s*(\d{4})?', all_text, re.I)
                        if m:
                            day = int(m.group(1))
                            month = mois_fr.get(m.group(2).lower(), '01')
                            year = m.group(3) or '2026'
                            start_date = f"{year}-{month}-{day:02d}"
                    
                    if not start_date or start_date < '2026-03-01':
                        continue
                    
                    page_emails = find_emails(soup2)
                    cats = classify_event(title, desc)
                    desc_clean = clean_description(desc, title)
                    lat, lon = get_coords(lieu or city)
                    
                    event = {
                        'title': title,
                        'description': desc_clean,
                        'date': start_date,
                        'end_date': start_date,
                        'location': lieu if lieu else city.replace('-', ' ').title() + ', Canton de Vaud',
                        'latitude': lat,
                        'longitude': lon,
                        'categories': cats,
                        'source_url': evt_url,
                        'organizer_email': page_emails[0] if page_emails else '',
                        'validation_status': 'validated' if page_emails else 'auto_validated',
                    }
                    events.append(event)
                    if page_emails:
                        for em in page_emails:
                            emails_found.append({'event': title, 'email': em, 'url': evt_url})
                    
                    print(f"    + {title[:45]} | {start_date} | emails:{len(page_emails)}")
                    
                except Exception as ex:
                    continue
        
        except Exception as ex:
            print(f"    ERREUR: {str(ex)[:50]}")
    
    return events, emails_found


def scrape_lausanne_agenda():
    """Scraper l'agenda de Lausanne"""
    events = []
    emails_found = []
    seen = set()
    
    urls = [
        'https://www.lausanne.ch/vie-pratique/culture/agenda-culturel.html',
        'https://www.lausanne.ch/vie-pratique/sports/agenda-sportif.html',
    ]
    
    for base_url in urls:
        print(f"\n  lausanne.ch: {base_url.split('/')[-1]}")
        time.sleep(DELAY)
        
        try:
            r = requests.get(base_url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"    Status {r.status_code}")
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            event_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(base_url, href)
                if 'lausanne.ch' in full_url and full_url not in seen:
                    if any(x in full_url for x in ['/agenda', '/evenement', '/event']):
                        seen.add(full_url)
                        event_links.append(full_url)
            
            print(f"    {len(event_links)} liens")
            
            for evt_url in event_links[:20]:
                time.sleep(DELAY)
                try:
                    r2 = requests.get(evt_url, headers=HEADERS, timeout=15)
                    if r2.status_code != 200:
                        continue
                    
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    title = ''
                    for el in soup2.find_all('h1'):
                        title = el.get_text(strip=True)
                        if title:
                            break
                    if not title:
                        continue
                    
                    desc = ''
                    for p in soup2.find_all('p'):
                        t = p.get_text(strip=True)
                        if len(t) > 40:
                            desc = t[:500]
                            break
                    
                    lieu = 'Lausanne'
                    for el in soup2.find_all(['span', 'div'], class_=re.compile(r'lieu|loc|address|venue', re.I)):
                        t = el.get_text(strip=True)
                        if t:
                            lieu = t
                            break
                    
                    all_text = soup2.get_text()
                    start_date = None
                    m = re.search(r'(\d{1,2})[./](\d{1,2})[./](2026)', all_text)
                    if m:
                        start_date = f"2026-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
                    
                    if not start_date or start_date < '2026-03-01':
                        continue
                    
                    page_emails = find_emails(soup2)
                    cats = classify_event(title, desc)
                    desc_clean = clean_description(desc, title)
                    lat, lon = get_coords(lieu)
                    
                    event = {
                        'title': title,
                        'description': desc_clean,
                        'date': start_date,
                        'end_date': start_date,
                        'location': lieu,
                        'latitude': lat,
                        'longitude': lon,
                        'categories': cats,
                        'source_url': evt_url,
                        'organizer_email': page_emails[0] if page_emails else '',
                        'validation_status': 'validated' if page_emails else 'auto_validated',
                    }
                    events.append(event)
                    if page_emails:
                        for em in page_emails:
                            emails_found.append({'event': title, 'email': em, 'url': evt_url})
                    
                    print(f"    + {title[:45]} | {start_date} | emails:{len(page_emails)}")
                    
                except Exception as ex:
                    continue
        
        except Exception as ex:
            print(f"    ERREUR: {str(ex)[:50]}")
    
    return events, emails_found


def scrape_loisirs_ch():
    """Scraper loisirs.ch pour le Canton de Vaud"""
    events = []
    emails_found = []
    seen = set()
    
    base_urls = [
        'https://www.loisirs.ch/agenda/vaud',
        'https://www.loisirs.ch/agenda/lausanne',
        'https://www.loisirs.ch/agenda/montreux',
        'https://www.loisirs.ch/agenda/nyon',
    ]
    
    for base_url in base_urls:
        city = base_url.split('/')[-1]
        print(f"\n  loisirs.ch/{city}")
        time.sleep(DELAY)
        
        try:
            r = requests.get(base_url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"    Status {r.status_code}")
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            event_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(base_url, href)
                if 'loisirs.ch' in full_url and full_url not in seen:
                    if re.search(r'/\d+', href) or '/event' in href or '/manifestation' in href:
                        seen.add(full_url)
                        event_links.append(full_url)
            
            print(f"    {len(event_links)} liens")
            
            for evt_url in event_links[:20]:
                time.sleep(DELAY)
                try:
                    r2 = requests.get(evt_url, headers=HEADERS, timeout=15)
                    if r2.status_code != 200:
                        continue
                    
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    title = ''
                    for el in soup2.find_all('h1'):
                        title = el.get_text(strip=True)
                        if title:
                            break
                    if not title:
                        continue
                    
                    desc = ''
                    for p in soup2.find_all('p'):
                        t = p.get_text(strip=True)
                        if len(t) > 40:
                            desc = t[:500]
                            break
                    
                    lieu = city
                    all_text = soup2.get_text()
                    start_date = None
                    m = re.search(r'(\d{1,2})[./](\d{1,2})[./](2026)', all_text)
                    if m:
                        start_date = f"2026-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
                    
                    if not start_date or start_date < '2026-03-01':
                        continue
                    
                    page_emails = find_emails(soup2)
                    cats = classify_event(title, desc)
                    desc_clean = clean_description(desc, title)
                    lat, lon = get_coords(lieu)
                    
                    event = {
                        'title': title,
                        'description': desc_clean,
                        'date': start_date,
                        'end_date': start_date,
                        'location': lieu,
                        'latitude': lat,
                        'longitude': lon,
                        'categories': cats,
                        'source_url': evt_url,
                        'organizer_email': page_emails[0] if page_emails else '',
                        'validation_status': 'validated' if page_emails else 'auto_validated',
                    }
                    events.append(event)
                    if page_emails:
                        for em in page_emails:
                            emails_found.append({'event': title, 'email': em, 'url': evt_url})
                    
                    print(f"    + {title[:45]} | {start_date} | emails:{len(page_emails)}")
                    
                except Exception as ex:
                    continue
        
        except Exception as ex:
            print(f"    ERREUR: {str(ex)[:50]}")
    
    return events, emails_found


def scrape_myswitzerland():
    """Scraper myswitzerland.com pour les événements dans le Canton de Vaud"""
    events = []
    emails_found = []
    seen = set()
    
    urls = [
        'https://www.myswitzerland.com/fr-ch/decouvrir/evenements/top-events/',
        'https://www.myswitzerland.com/fr-ch/destinations/canton-de-vaud/',
    ]
    
    for base_url in urls:
        print(f"\n  myswitzerland.com: {base_url.split('/')[-2]}")
        time.sleep(DELAY)
        
        try:
            r = requests.get(base_url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"    Status {r.status_code}")
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            event_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(base_url, href)
                if 'myswitzerland.com' in full_url and full_url not in seen:
                    if any(x in full_url for x in ['/evenement', '/event', 'vaud']):
                        seen.add(full_url)
                        event_links.append(full_url)
            
            print(f"    {len(event_links)} liens")
            
            for evt_url in event_links[:15]:
                time.sleep(DELAY)
                try:
                    r2 = requests.get(evt_url, headers=HEADERS, timeout=15)
                    if r2.status_code != 200:
                        continue
                    
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    title = ''
                    for el in soup2.find_all('h1'):
                        title = el.get_text(strip=True)
                        if title:
                            break
                    if not title:
                        continue
                    
                    desc = ''
                    for p in soup2.find_all('p'):
                        t = p.get_text(strip=True)
                        if len(t) > 40:
                            desc = t[:500]
                            break
                    
                    all_text = soup2.get_text()
                    start_date = None
                    m = re.search(r'(\d{1,2})[./](\d{1,2})[./](2026)', all_text)
                    if m:
                        start_date = f"2026-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
                    
                    if not start_date or start_date < '2026-03-01':
                        continue
                    
                    lieu = 'Canton de Vaud'
                    page_emails = find_emails(soup2)
                    cats = classify_event(title, desc)
                    desc_clean = clean_description(desc, title)
                    lat, lon = get_coords(lieu)
                    
                    event = {
                        'title': title,
                        'description': desc_clean,
                        'date': start_date,
                        'end_date': start_date,
                        'location': lieu,
                        'latitude': lat,
                        'longitude': lon,
                        'categories': cats,
                        'source_url': evt_url,
                        'organizer_email': page_emails[0] if page_emails else '',
                        'validation_status': 'validated' if page_emails else 'auto_validated',
                    }
                    events.append(event)
                    if page_emails:
                        for em in page_emails:
                            emails_found.append({'event': title, 'email': em, 'url': evt_url})
                    
                    print(f"    + {title[:45]} | {start_date} | emails:{len(page_emails)}")
                    
                except Exception as ex:
                    continue
        
        except Exception as ex:
            print(f"    ERREUR: {str(ex)[:50]}")
    
    return events, emails_found


def scrape_nyon_morges():
    """Scraper les agendas de Nyon et Morges"""
    events = []
    emails_found = []
    seen = set()
    
    urls = [
        ('https://www.nyon.ch/fr/nyon-s-anime/agenda', 'Nyon'),
        ('https://www.nyon.ch/fr/nyon-s-anime/manifestations', 'Nyon'),
        ('https://www.morges.ch/officiel/nyon-decouverte/agenda', 'Morges'),
        ('https://www.morges-tourisme.ch/fr/agenda', 'Morges'),
        ('https://www.yverdonlesbainsregion.ch/fr/agenda', 'Yverdon'),
    ]
    
    for base_url, city in urls:
        print(f"\n  {urlparse(base_url).netloc}: {city}")
        time.sleep(DELAY)
        
        try:
            r = requests.get(base_url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"    Status {r.status_code}")
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            event_links = []
            domain = urlparse(base_url).netloc
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(base_url, href)
                if domain in full_url and full_url not in seen and full_url != base_url:
                    if any(x in full_url.lower() for x in ['/agenda/', '/event', '/manifestation', '/detail']):
                        seen.add(full_url)
                        event_links.append(full_url)
            
            print(f"    {len(event_links)} liens")
            
            for evt_url in event_links[:15]:
                time.sleep(DELAY)
                try:
                    r2 = requests.get(evt_url, headers=HEADERS, timeout=15)
                    if r2.status_code != 200:
                        continue
                    
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    title = ''
                    for el in soup2.find_all(['h1', 'h2']):
                        t = el.get_text(strip=True)
                        if len(t) > 3 and len(t) < 200:
                            title = t
                            break
                    if not title:
                        continue
                    
                    desc = ''
                    for p in soup2.find_all('p'):
                        t = p.get_text(strip=True)
                        if len(t) > 30:
                            desc = t[:500]
                            break
                    
                    all_text = soup2.get_text()
                    start_date = None
                    m = re.search(r'(\d{1,2})[./](\d{1,2})[./](2026)', all_text)
                    if m:
                        start_date = f"2026-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
                    
                    if not start_date or start_date < '2026-03-01':
                        continue
                    
                    lieu = city
                    for el in soup2.find_all(['span', 'div'], class_=re.compile(r'lieu|loc|address', re.I)):
                        t = el.get_text(strip=True)
                        if t:
                            lieu = t
                            break
                    
                    page_emails = find_emails(soup2)
                    cats = classify_event(title, desc)
                    desc_clean = clean_description(desc, title)
                    lat, lon = get_coords(lieu or city)
                    
                    event = {
                        'title': title,
                        'description': desc_clean,
                        'date': start_date,
                        'end_date': start_date,
                        'location': lieu,
                        'latitude': lat,
                        'longitude': lon,
                        'categories': cats,
                        'source_url': evt_url,
                        'organizer_email': page_emails[0] if page_emails else '',
                        'validation_status': 'validated' if page_emails else 'auto_validated',
                    }
                    events.append(event)
                    if page_emails:
                        for em in page_emails:
                            emails_found.append({'event': title, 'email': em, 'url': evt_url})
                    
                    print(f"    + {title[:45]} | {start_date} | emails:{len(page_emails)}")
                    
                except Exception as ex:
                    continue
        
        except Exception as ex:
            print(f"    ERREUR: {str(ex)[:50]}")
    
    return events, emails_found


# ========================================
# MAIN
# ========================================
if __name__ == '__main__':
    all_events = []
    all_emails = []
    
    # Charger les events du V1
    try:
        with open('real_vaud_events.json', 'r', encoding='utf-8') as f:
            v1_events = json.load(f)
        all_events.extend(v1_events)
        print(f"Chargé {len(v1_events)} events du V1")
    except:
        pass
    
    # 1. eventfrog.ch
    print("\n" + "=" * 60)
    print("SCRAPING eventfrog.ch")
    print("=" * 60)
    e1, em1 = scrape_eventfrog()
    all_events.extend(e1)
    all_emails.extend(em1)
    print(f"\neventfrog.ch: {len(e1)} events, {len(em1)} emails")
    
    # 2. lausanne.ch
    print("\n" + "=" * 60)
    print("SCRAPING lausanne.ch")
    print("=" * 60)
    e2, em2 = scrape_lausanne_agenda()
    all_events.extend(e2)
    all_emails.extend(em2)
    print(f"\nlausanne.ch: {len(e2)} events, {len(em2)} emails")
    
    # 3. loisirs.ch
    print("\n" + "=" * 60)
    print("SCRAPING loisirs.ch")
    print("=" * 60)
    e3, em3 = scrape_loisirs_ch()
    all_events.extend(e3)
    all_emails.extend(em3)
    print(f"\nloisirs.ch: {len(e3)} events, {len(em3)} emails")
    
    # 4. myswitzerland.com
    print("\n" + "=" * 60)
    print("SCRAPING myswitzerland.com")
    print("=" * 60)
    e4, em4 = scrape_myswitzerland()
    all_events.extend(e4)
    all_emails.extend(em4)
    print(f"\nmyswitzerland.com: {len(e4)} events, {len(em4)} emails")
    
    # 5. Nyon, Morges, Yverdon
    print("\n" + "=" * 60)
    print("SCRAPING nyon.ch, morges.ch, yverdon.ch")
    print("=" * 60)
    e5, em5 = scrape_nyon_morges()
    all_events.extend(e5)
    all_emails.extend(em5)
    print(f"\nVilles: {len(e5)} events, {len(em5)} emails")
    
    # Dédupliquer
    seen_titles = set()
    unique_events = []
    for e in all_events:
        key = e['title'].lower().strip()
        if key not in seen_titles:
            seen_titles.add(key)
            unique_events.append(e)
    
    print(f"\n{'=' * 60}")
    print(f"TOTAL V2: {len(unique_events)} events uniques, {len(all_emails)} emails")
    print(f"{'=' * 60}")
    
    with open('real_vaud_events_v2.json', 'w', encoding='utf-8') as f:
        json.dump(unique_events, f, ensure_ascii=False, indent=2)
    
    with open('emails_organisateurs/emails_Vaud_v2.csv', 'w', encoding='utf-8') as f:
        f.write('event_title,email,source_url\n')
        for em in all_emails:
            title = em['event'].replace('"', "'")
            f.write(f'"{title}",{em["email"]},{em["url"]}\n')
    
    print(f"Sauvegardé dans real_vaud_events_v2.json")
    print(f"Emails dans emails_organisateurs/emails_Vaud_v2.csv")
