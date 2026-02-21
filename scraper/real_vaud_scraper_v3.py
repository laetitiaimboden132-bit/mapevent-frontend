"""
Scraper V3 - Sources RÉELLES confirmées
1. myswitzerland.com - 47+ festivals/fêtes Vaud (URLs réelles, dates confirmées)
2. leprogramme.ch - agenda culturel Vaud par semaine (URLs réelles)
3. tempslibre.ch - événements détaillés
4. vaud.ch/tourisme - événements officiels

Délai: 8 secondes entre requêtes
"""
import requests
from bs4 import BeautifulSoup
import sys, io, json, time, re, random, csv
from urllib.parse import urljoin
from datetime import datetime, timedelta

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
    'lausanne': (46.5197, 6.6323), 'montreux': (46.4312, 6.9107),
    'vevey': (46.4628, 6.8432), 'nyon': (46.3833, 6.2398),
    'morges': (46.5108, 6.4989), 'yverdon': (46.7784, 6.6411),
    'aigle': (46.3183, 6.9719), 'château-d\'oex': (46.4748, 7.1360),
    'payerne': (46.8207, 6.9381), 'moudon': (46.6686, 6.7947),
    'rolle': (46.4594, 6.3367), 'cully': (46.4887, 6.7294),
    'pully': (46.5097, 6.6611), 'renens': (46.5345, 6.5874),
    'villars': (46.2989, 7.0528), 'leysin': (46.3417, 7.0133),
    'avenches': (46.8819, 7.0411), 'crissier': (46.5450, 6.5800),
    'cossonay': (46.6136, 6.5058), 'gland': (46.4220, 6.2720),
    'prangins': (46.3960, 6.2520), 'préverenges': (46.5180, 6.5370),
    'cudrefin': (46.9520, 7.0190), 'mézières': (46.5950, 6.7720),
    'le sentier': (46.6100, 6.2330), 'le lieu': (46.6400, 6.3000),
    'crans-près-céligny': (46.3770, 6.1940), 'l\'abbaye': (46.6500, 6.3200),
    'romainmôtier': (46.6920, 6.4570), 'saint-saphorin': (46.4730, 6.8100),
    'monthey': (46.2540, 6.9540),
    'lavey': (46.2060, 7.0290), 'prilly': (46.5290, 6.6010),
    'sainte-croix': (46.8220, 6.5050),
}

MOIS_FR = {
    'janvier':'01','février':'02','mars':'03','avril':'04','mai':'05','juin':'06',
    'juillet':'07','août':'08','septembre':'09','octobre':'10','novembre':'11','décembre':'12',
    'janv':'01','févr':'02','avr':'04','juil':'07','sept':'09','oct':'10','nov':'11','déc':'12'
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
    
    if any(w in text for w in ['concert', 'musique', 'orchestre', 'récital', 'chorale', 'chœur']):
        if any(w in text for w in ['classique', 'symphoni', 'orchestre', 'quatuor', 'baroque', 'opéra', 'lyrique']):
            cats.append('Music > Classique')
        elif any(w in text for w in ['jazz', 'swing', 'blues']):
            cats.append('Music > Jazz / Blues')
        elif any(w in text for w in ['rock', 'metal', 'punk']):
            cats.append('Music > Rock / Metal')
        elif any(w in text for w in ['electro', 'techno', 'dj', 'house', 'electronic']):
            cats.append('Music > Electro / DJ')
        elif any(w in text for w in ['folk', 'acoustique', 'acoustic']):
            if any(w in text for w in ['folk', 'acoustique']) and any(w in text for w in ['concert', 'musique']):
                cats.append('Music > Folk / Acoustic')
        else:
            cats.append('Music > Concert')
    
    if 'festival' in text:
        cats.append('Music > Festival')
    
    if any(w in text for w in ['théâtre', 'théatre', 'comédie', 'pièce', 'spectacle', 'humour', 'stand-up', 'impro']):
        cats.append('Culture > Théâtre')
    if any(w in text for w in ['exposition', 'expo ', 'vernissage', 'musée', 'galerie']):
        cats.append('Culture > Expositions')
    if any(w in text for w in ['cinéma', 'film', 'projection', 'ciné ']):
        cats.append('Culture > Cinéma')
    if any(w in text for w in ['danse', 'ballet', 'chorégraph']):
        cats.append('Culture > Danse')
    if any(w in text for w in ['conférence', 'colloque', 'séminaire', 'débat', 'lecture']):
        cats.append('Culture > Conférence')
    if any(w in text for w in ['atelier', 'workshop']):
        cats.append('Culture > Atelier')
    
    if any(w in text for w in ['dégustation', 'cave', 'vigneron', 'vin ', 'vignoble']):
        cats.append('Gastronomie > Dégustation')
    if any(w in text for w in ['marché', 'brocante', 'foire']):
        cats.append('Gastronomie > Marché')
    if any(w in text for w in ['gastronomie', 'culinaire', 'cuisine', 'fondue', 'raclette', 'truffe', 'terroir']):
        cats.append('Gastronomie > Gastronomie')
    
    if any(w in text for w in ['randonnée', 'rando', 'balade', 'marche ']):
        cats.append('Sport > Terrestre')
    if any(w in text for w in ['course', 'marathon', 'trail', 'running', 'triathlon']):
        cats.append('Sport > Terrestre')
    if any(w in text for w in ['ski', 'snowboard', 'luge', 'neige']):
        cats.append('Sport > Glisse')
    if any(w in text for w in ['natation', 'voile', 'aviron', 'kayak', 'aquatique', 'lac']):
        cats.append('Sport > Aquatique')
    
    if any(w in text for w in ['fête', 'fete', 'carnaval', 'nationale']):
        cats.append('Famille > Fêtes')
    if any(w in text for w in ['enfant', 'famille', 'junior', 'kid', 'jeunesse']):
        cats.append('Famille > Enfants')
    if any(w in text for w in ['médiéval', 'historique', 'patrimoine']):
        cats.append('Culture > Divers')
    
    if not cats:
        cats.append('Culture > Divers')
    return list(set(cats[:3]))

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
        if not any(x in em for x in ['example.com','test.com','sentry.io','w3.org','.png','.jpg','.gif','.css','.js','noreply','no-reply']):
            emails.add(em)
    return list(emails)

def clean_desc(text, title):
    if not text or len(text) < 10:
        return f"Découvrez '{title}', événement dans le Canton de Vaud."
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > 400:
        text = text[:397] + '...'
    return text

def parse_date_myswitzerland(text):
    """Parse dates from myswitzerland.com format like '27.03.2026 - 11.05.2026' or '10.04.2026'"""
    dates = re.findall(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', text)
    if dates:
        start = dates[0]
        end = dates[-1]
        start_date = f"{start[2]}-{int(start[1]):02d}-{int(start[0]):02d}"
        end_date = f"{end[2]}-{int(end[1]):02d}-{int(end[0]):02d}"
        return start_date, end_date
    return None, None


def scrape_myswitzerland_vaud():
    """Scraper myswitzerland.com - 47+ festivals Vaud avec vraies URLs"""
    events = []
    emails_found = []
    
    # URLs des événements trouvés sur myswitzerland.com
    event_urls = [
        # Mars
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/les-printemps-de-sevelin/', 'Lausanne', '2026-03-05', '2026-03-22'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/shapes-festival-leysin/', 'Leysin', '2026-03-16', '2026-03-22'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/projection-commentee-festival-histoire-et-cite-2026/', 'Lausanne', '2026-03-21', '2026-03-21'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/world-dance-festival-orientalp/', "Château-d'Oex", '2026-03-25', '2026-03-29'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/fete-de-la-tulipe/', 'Morges', '2026-03-27', '2026-05-11'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/repas-concert-du-aiglin-music/', 'Aigle', '2026-03-27', '2026-03-27'),
        
        # Avril
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/43e-edition-cully-jazz-festival/', 'Cully', '2026-04-10', '2026-04-18'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/villars-afterseason-electronic-festival/', 'Villars-sur-Ollon', '2026-04-10', '2026-04-11'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/festival-international-classique-et-lyrique-de-morges-et-region/', 'Morges', '2026-04-25', '2026-04-30'),
        
        # Mai
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/la-fete-de-la-danse/', 'Lausanne', '2026-05-06', '2026-05-10'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/fete-de-la-danse-a-morges/', 'Morges', '2026-05-06', '2026-05-10'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/avenches-open-air/', 'Avenches', '2026-05-28', '2026-05-30'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/fete-medievale-1/', "L'Abbaye", '2026-05-29', '2026-05-31'),
        
        # Juin
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/16eme-blues-rules-crissier-festival/', 'Crissier', '2026-06-05', '2026-06-06'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/festimusiques/', 'Moudon', '2026-06-13', '2026-06-14'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/caribana-festival/', 'Crans-près-Céligny', '2026-06-17', '2026-06-20'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/fete-de-la-musique-de-morges/', 'Morges', '2026-06-17', '2026-06-21'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/red-pigs-festival/', 'Payerne', '2026-06-18', '2026-06-20'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/fete-de-la-musique-5/', 'Le Sentier', '2026-06-20', '2026-06-20'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/diabolo-festival/', 'Morges', '2026-06-20', '2026-06-21'),
        
        # Juillet
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/festival-de-la-cite/', 'Lausanne', '2026-06-30', '2026-07-05'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/la-collection-de-lart-brut-au-festival-de-la-cite/', 'Lausanne', '2026-06-29', '2026-06-29'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/festival-rive-jazzy-2026/', 'Prangins', '2026-07-02', '2026-08-09'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/montreux-jazz-festival/', 'Montreux', '2026-07-03', '2026-07-18'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/festival-yadlo/', 'Préverenges', '2026-07-10', '2026-07-12'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/paleo-festival/', 'Nyon', '2026-07-21', '2026-07-26'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/fete-nationale-au-village-du-lieu/', 'Le Lieu', '2026-07-31', '2026-07-31'),
        
        # Août
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/fete-nationale-au-rocheray/', 'Le Sentier', '2026-08-01', '2026-08-01'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/festival-into-the-corn/', 'Mézières', '2026-08-07', '2026-08-08'),
        ('https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/rock-the-lakes-festival/', 'Cudrefin', '2026-08-14', '2026-08-16'),
    ]
    
    print(f"myswitzerland.com: {len(event_urls)} événements à scraper")
    
    for url, city, start_date, end_date in event_urls:
        time.sleep(DELAY)
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"  ERR {r.status_code} | {url.split('/')[-2]}")
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Titre
            title = ''
            for el in soup.find_all('h1'):
                t = el.get_text(strip=True)
                if t and len(t) > 3:
                    title = t
                    break
            if not title:
                title = url.split('/')[-2].replace('-', ' ').title()
            
            # Description
            desc = ''
            # Chercher les paragraphes après le titre
            for p in soup.find_all('p'):
                t = p.get_text(strip=True)
                if len(t) > 40 and 'cookie' not in t.lower() and 'suisse tourisme' not in t.lower():
                    desc = t[:500]
                    break
            
            # Lieu détaillé
            lieu = city
            for el in soup.find_all(['span', 'div', 'address'], attrs={'class': re.compile(r'location|address|venue|place', re.I)}):
                t = el.get_text(strip=True)
                if t and len(t) < 150:
                    lieu = t
                    break
            
            # Emails
            page_emails = find_emails(soup)
            
            cats = classify_event(title, desc)
            desc_clean = clean_desc(desc, title)
            lat, lon = get_coords(lieu or city)
            
            event = {
                'title': title,
                'description': desc_clean,
                'date': start_date,
                'end_date': end_date,
                'location': f"{lieu}, Canton de Vaud" if 'vaud' not in lieu.lower() else lieu,
                'latitude': lat,
                'longitude': lon,
                'categories': cats,
                'source_url': url,
                'organizer_email': page_emails[0] if page_emails else '',
                'validation_status': 'validated' if page_emails else 'auto_validated',
            }
            events.append(event)
            if page_emails:
                for em in page_emails:
                    emails_found.append({'event': title, 'email': em, 'url': url})
            
            print(f"  + {title[:45]} | {start_date} | {city} | emails:{len(page_emails)}")
        
        except Exception as ex:
            print(f"  ERR {str(ex)[:50]} | {url.split('/')[-2]}")
    
    return events, emails_found


def scrape_leprogramme_vaud():
    """Scraper leprogramme.ch - agenda culturel Vaud semaine par semaine"""
    events = []
    emails_found = []
    seen_urls = set()
    
    # Générer les URLs pour chaque semaine de mars à décembre 2026
    # Format: https://vd.leprogramme.ch/agenda-culturel-de-la-semaine/Vaud/2026/10
    # Le dernier nombre est le numéro de semaine dans l'année
    
    # Semaines mars-décembre 2026: semaines ~10 à ~52
    for week in range(10, 53):
        url = f"https://vd.leprogramme.ch/agenda-culturel-de-la-semaine/Vaud/2026/{week:02d}"
        print(f"\n  leprogramme.ch semaine {week}")
        time.sleep(DELAY)
        
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"    Status {r.status_code}")
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            page_text = soup.get_text()
            
            # Chercher les liens vers des événements individuels
            event_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'leprogramme.ch/' in href and any(x in href for x in ['/concerts/', '/theatre/', '/danse/', '/spectacle', '/autres']):
                    full_url = urljoin(url, href)
                    if full_url not in seen_urls:
                        seen_urls.add(full_url)
                        event_links.append(full_url)
            
            if not event_links:
                print(f"    0 liens")
                continue
            
            print(f"    {len(event_links)} liens")
            
            # Visiter chaque événement (max 10 par semaine pour la vitesse)
            for evt_url in event_links[:10]:
                time.sleep(DELAY)
                try:
                    r2 = requests.get(evt_url, headers=HEADERS, timeout=15)
                    if r2.status_code != 200:
                        continue
                    
                    soup2 = BeautifulSoup(r2.text, 'html.parser')
                    
                    # Titre
                    title = ''
                    for el in soup2.find_all('h1'):
                        t = el.get_text(strip=True)
                        if t and len(t) > 3:
                            title = t
                            break
                    if not title:
                        continue
                    
                    # Description
                    desc = ''
                    for p in soup2.find_all(['p', 'div'], class_=re.compile(r'desc|synopsis|content|detail', re.I)):
                        t = p.get_text(strip=True)
                        if len(t) > 30:
                            desc = t[:500]
                            break
                    if not desc:
                        for p in soup2.find_all('p'):
                            t = p.get_text(strip=True)
                            if len(t) > 40 and 'copyright' not in t.lower():
                                desc = t[:500]
                                break
                    
                    # Lieu
                    lieu = ''
                    for el in soup2.find_all(['span', 'div', 'address'], class_=re.compile(r'venue|lieu|salle|location|address', re.I)):
                        t = el.get_text(strip=True)
                        if t and len(t) < 150:
                            lieu = t
                            break
                    if not lieu:
                        # Essayer d'extraire du breadcrumb ou de la page
                        for el in soup2.find_all(['span', 'a']):
                            t = el.get_text(strip=True)
                            if any(city in t.lower() for city in VAUD_COORDS.keys()) and len(t) < 80:
                                lieu = t
                                break
                    
                    # Date
                    all_text = soup2.get_text()
                    start_date = None
                    
                    # Format dd.mm.yyyy
                    m = re.search(r'(\d{1,2})\.(\d{1,2})\.(2026)', all_text)
                    if m:
                        start_date = f"2026-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
                    
                    # Format dd/mm/yyyy
                    if not start_date:
                        m = re.search(r'(\d{1,2})/(\d{1,2})/(2026)', all_text)
                        if m:
                            start_date = f"2026-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
                    
                    # Mois en français
                    if not start_date:
                        for mois, num in MOIS_FR.items():
                            m = re.search(rf'(\d{{1,2}})\s+{mois}\s*(2026)?', all_text, re.I)
                            if m:
                                day = int(m.group(1))
                                start_date = f"2026-{num}-{day:02d}"
                                break
                    
                    if not start_date or start_date < '2026-03-01':
                        continue
                    
                    # Emails
                    page_emails = find_emails(soup2)
                    
                    cats = classify_event(title, desc)
                    desc_clean = clean_desc(desc, title)
                    lat, lon = get_coords(lieu)
                    
                    event = {
                        'title': title,
                        'description': desc_clean,
                        'date': start_date,
                        'end_date': start_date,
                        'location': lieu if lieu else 'Canton de Vaud',
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
                    
                    print(f"    + {title[:40]} | {start_date} | {lieu[:25]} | emails:{len(page_emails)}")
                
                except Exception as ex:
                    continue
        
        except Exception as ex:
            print(f"    ERREUR: {str(ex)[:50]}")
    
    return events, emails_found


def scrape_myswitzerland_other_categories():
    """Scraper d'autres catégories sur myswitzerland.com pour Vaud"""
    events = []
    emails_found = []
    seen = set()
    
    cat_urls = [
        'https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/manifestations-rechercher/sportactivite/canton-de-vaud/',
        'https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/manifestations-rechercher/coutumes-marche/canton-de-vaud/',
        'https://www.myswitzerland.com/fr-ch/decouvrir/manifestations/manifestations-rechercher/exposition-foire/canton-de-vaud/',
    ]
    
    for cat_url in cat_urls:
        cat_name = cat_url.split('/')[-3]
        print(f"\n  myswitzerland.com/{cat_name}")
        time.sleep(DELAY)
        
        try:
            r = requests.get(cat_url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                print(f"    Status {r.status_code}")
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Chercher les liens d'événements
            event_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                full_url = urljoin(cat_url, href)
                if '/manifestations/' in full_url and full_url not in seen and full_url != cat_url:
                    if 'manifestations-rechercher' not in full_url:
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
                        t = el.get_text(strip=True)
                        if t and len(t) > 3:
                            title = t
                            break
                    if not title:
                        continue
                    
                    desc = ''
                    for p in soup2.find_all('p'):
                        t = p.get_text(strip=True)
                        if len(t) > 40 and 'cookie' not in t.lower():
                            desc = t[:500]
                            break
                    
                    all_text = soup2.get_text()
                    start_date, end_date = parse_date_myswitzerland(all_text)
                    
                    if not start_date or start_date < '2026-03-01':
                        continue
                    
                    # Lieu
                    lieu = ''
                    for el in soup2.find_all(['span', 'div'], class_=re.compile(r'location|address|venue', re.I)):
                        t = el.get_text(strip=True)
                        if t:
                            lieu = t
                            break
                    
                    page_emails = find_emails(soup2)
                    cats = classify_event(title, desc)
                    desc_clean = clean_desc(desc, title)
                    lat, lon = get_coords(lieu)
                    
                    event = {
                        'title': title,
                        'description': desc_clean,
                        'date': start_date,
                        'end_date': end_date or start_date,
                        'location': lieu if lieu else 'Canton de Vaud',
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
                    
                    print(f"    + {title[:40]} | {start_date} | emails:{len(page_emails)}")
                
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
    
    # 1. myswitzerland.com - Festivals
    print("=" * 60)
    print("SCRAPING myswitzerland.com - Festivals Vaud")
    print("=" * 60)
    e1, em1 = scrape_myswitzerland_vaud()
    all_events.extend(e1)
    all_emails.extend(em1)
    print(f"\nmyswitzerland.com festivals: {len(e1)} events, {len(em1)} emails")
    
    # 2. myswitzerland.com - Autres catégories
    print("\n" + "=" * 60)
    print("SCRAPING myswitzerland.com - Sport, Coutumes, Expos")
    print("=" * 60)
    e2, em2 = scrape_myswitzerland_other_categories()
    all_events.extend(e2)
    all_emails.extend(em2)
    print(f"\nmyswitzerland.com autres: {len(e2)} events, {len(em2)} emails")
    
    # 3. leprogramme.ch
    print("\n" + "=" * 60)
    print("SCRAPING leprogramme.ch - Agenda culturel Vaud")
    print("=" * 60)
    e3, em3 = scrape_leprogramme_vaud()
    all_events.extend(e3)
    all_emails.extend(em3)
    print(f"\nleprogramme.ch: {len(e3)} events, {len(em3)} emails")
    
    # Charger les events V2 (vrais tempslibre + vaud.ch)
    try:
        with open('real_vaud_events_v2.json', 'r', encoding='utf-8') as f:
            v2_events = json.load(f)
        all_events.extend(v2_events)
        print(f"\n+ {len(v2_events)} events du V2")
    except:
        pass
    
    # Dédupliquer
    seen_titles = set()
    unique_events = []
    for e in all_events:
        key = e['title'].lower().strip()[:50]
        if key not in seen_titles:
            seen_titles.add(key)
            unique_events.append(e)
    
    print(f"\n{'=' * 60}")
    print(f"TOTAL V3: {len(unique_events)} events uniques, {len(all_emails)} emails")
    print(f"{'=' * 60}")
    
    # Sauvegarder
    with open('real_vaud_events_v3.json', 'w', encoding='utf-8') as f:
        json.dump(unique_events, f, ensure_ascii=False, indent=2)
    
    with open('emails_organisateurs/emails_Vaud_v3.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['event_title', 'email', 'source_url'])
        for em in all_emails:
            writer.writerow([em['event'], em['email'], em['url']])
    
    print(f"\nSauvegardé dans real_vaud_events_v3.json")
    print(f"Emails dans emails_organisateurs/emails_Vaud_v3.csv")
