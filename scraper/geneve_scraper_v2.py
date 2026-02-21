"""
Scraper Genève V2 - Source geneve.ch/agenda (OpenAgenda)
+ billetterie-culture.geneve.ch + evenements.geneve.ch
"""
import requests, sys, io, json, re, time, hashlib, csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'fr-CH,fr;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}
DELAY = 8

KNOWN_VENUES = {
    'victoria hall': {'address': 'Rue du Général-Dufour 14, 1204 Genève', 'lat': 46.1978, 'lon': 6.1419},
    'grand théâtre': {'address': 'Place de Neuve 5, 1204 Genève', 'lat': 46.1994, 'lon': 6.1400},
    'bfm': {'address': 'Place des Volontaires 2, 1204 Genève', 'lat': 46.2028, 'lon': 6.1408},
    'bâtiment des forces motrices': {'address': 'Place des Volontaires 2, 1204 Genève', 'lat': 46.2028, 'lon': 6.1408},
    'musée d\'art et d\'histoire': {'address': 'Rue Charles-Galland 2, 1206 Genève', 'lat': 46.1978, 'lon': 6.1531},
    'meg': {'address': 'Boulevard Carl-Vogt 65-67, 1205 Genève', 'lat': 46.1961, 'lon': 6.1367},
    'musée d\'ethnographie': {'address': 'Boulevard Carl-Vogt 65-67, 1205 Genève', 'lat': 46.1961, 'lon': 6.1367},
    'chat noir': {'address': 'Rue Vautier 13, 1227 Carouge', 'lat': 46.1828, 'lon': 6.1394},
    'alhambra': {'address': 'Rue de la Rôtisserie 10, 1204 Genève', 'lat': 46.2011, 'lon': 6.1456},
    'usine': {'address': 'Place des Volontaires 4, 1204 Genève', 'lat': 46.2031, 'lon': 6.1403},
    'théâtre du léman': {'address': 'Quai du Mont-Blanc 19, 1201 Genève', 'lat': 46.2103, 'lon': 6.1494},
    'théâtre am stram gram': {'address': 'Route de Frontenex 56, 1207 Genève', 'lat': 46.2028, 'lon': 6.1642},
    'théâtre de carouge': {'address': 'Rue Ancienne 39, 1227 Carouge', 'lat': 46.1822, 'lon': 6.1389},
    'comédie de genève': {'address': 'Boulevard des Philosophes 6, 1205 Genève', 'lat': 46.1989, 'lon': 6.1425},
    'bibliothèque de la cité': {'address': 'Place des Trois-Perdrix 5, 1204 Genève', 'lat': 46.2011, 'lon': 6.1461},
    'conservatoire de musique': {'address': 'Place de Neuve 5, 1204 Genève', 'lat': 46.1994, 'lon': 6.1400},
    'maison des arts du grütli': {'address': 'Rue du Général-Dufour 16, 1204 Genève', 'lat': 46.1983, 'lon': 6.1419},
    'salle communale de plainpalais': {'address': 'Rue de Carouge 52, 1205 Genève', 'lat': 46.1961, 'lon': 6.1417},
    'palexpo': {'address': 'Route François-Peyrot 30, 1218 Le Grand-Saconnex', 'lat': 46.2358, 'lon': 6.1114},
    'arena': {'address': 'Route des Batailleux 2, 1218 Le Grand-Saconnex', 'lat': 46.2372, 'lon': 6.1150},
    'parc des bastions': {'address': 'Promenade des Bastions, 1204 Genève', 'lat': 46.1986, 'lon': 6.1461},
    'parc la grange': {'address': 'Quai Gustave-Ador 30, 1207 Genève', 'lat': 46.2028, 'lon': 6.1619},
    'plaine de plainpalais': {'address': 'Plaine de Plainpalais, 1205 Genève', 'lat': 46.1978, 'lon': 6.1417},
    'muséum d\'histoire naturelle': {'address': 'Route de Malagnou 1, 1208 Genève', 'lat': 46.1978, 'lon': 6.1575},
    'théâtre pitoëff': {'address': 'Rue de Carouge 52, 1205 Genève', 'lat': 46.1961, 'lon': 6.1417},
    'cave 12': {'address': 'Place des Volontaires 4, 1204 Genève', 'lat': 46.2031, 'lon': 6.1403},
}

MOIS_FR = {
    'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
    'juillet': 7, 'août': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
}

all_events = []
all_emails = []
seen_ids = set()

# Charger les events V1 déjà importés
try:
    with open('geneve_events.json', 'r', encoding='utf-8') as f:
        v1_events = json.load(f)
    for e in v1_events:
        key = hashlib.md5(f"{e['title'].lower().strip()}_{e.get('start_date', '')}".encode()).hexdigest()[:12]
        seen_ids.add(key)
    print(f"V1: {len(v1_events)} events déjà connus")
except:
    pass


def make_id(title, date):
    return hashlib.md5(f"{title.lower().strip()}_{date}".encode()).hexdigest()[:12]

def add_event(event):
    eid = make_id(event['title'], event.get('start_date', ''))
    if eid in seen_ids:
        return False
    seen_ids.add(eid)
    all_events.append(event)
    return True

def parse_date(text):
    if not text:
        return None
    text = text.lower().strip()
    m = re.search(r'(\d{1,2})\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+(\d{4})', text)
    if m:
        return f"{int(m.group(3))}-{MOIS_FR[m.group(2)]:02d}-{int(m.group(1)):02d}"
    m = re.search(r'(\d{1,2})[./](\d{1,2})[./](\d{4})', text)
    if m:
        return f"{int(m.group(3))}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', text)
    if m:
        return m.group(0)
    return None

def classify(title, desc=''):
    text = (title + ' ' + (desc or '')).lower()
    cats = []
    
    if any(w in text for w in ['concert', 'orchestre', 'récital', 'symphoni', 'chorale', 'choeur', 'musique', 'musical']):
        if any(w in text for w in ['classique', 'symphoni', 'orchestre', 'quatuor', 'baroque', 'opéra', 'lyrique', 'orgue', 'philharmon', 'sonate', 'chambre']):
            cats.append('Music > Classique')
        elif any(w in text for w in ['jazz', 'swing', 'blues']):
            cats.append('Music > Jazz / Blues')
        elif any(w in text for w in ['rock', 'metal', 'punk']):
            cats.append('Music > Rock / Metal')
        elif any(w in text for w in ['electro', 'techno', 'dj', 'house', 'electronic', 'trance', 'clubbing']):
            cats.append('Music > Electro / DJ')
        elif any(w in text for w in ['rap', 'hip', 'trap', 'urban']):
            cats.append('Music > Rap / Hip-Hop')
        elif any(w in text for w in ['folk', 'acoustique', 'acoustic']):
            cats.append('Music > Folk / Acoustic')
        elif any(w in text for w in ['pop', 'variété', 'chanson']):
            cats.append('Music > Pop / Variétés')
        else:
            cats.append('Music > Concert')
    
    if any(w in text for w in ['clubbing', 'dj', 'techno', 'house', 'trance']) and 'Music > Electro / DJ' not in cats:
        cats.append('Music > Electro / DJ')
    
    if 'festival' in text and 'film' not in text:
        cats.append('Music > Festival')
    
    if any(w in text for w in ['théâtre', 'comédie', 'pièce ', 'spectacle', 'humour', 'stand-up', 'improvisation', 'marionnette']):
        cats.append('Culture > Théâtre')
    if any(w in text for w in ['exposition', 'expo ', 'vernissage', 'musée', 'galerie']):
        cats.append('Culture > Expositions')
    if any(w in text for w in ['cinéma', 'film', 'projection', 'ciné ']):
        cats.append('Culture > Cinéma')
    if any(w in text for w in ['danse', 'ballet', 'chorégraph']):
        cats.append('Culture > Danse')
    if any(w in text for w in ['conférence', 'colloque', 'séminaire', 'débat', 'rencontre']):
        if not any(w in text for w in ['sport', 'ski', 'course']):
            cats.append('Culture > Conférence')
    if any(w in text for w in ['atelier', 'workshop']):
        cats.append('Culture > Atelier')
    if any(w in text for w in ['visite commentée', 'visite guidée', 'visite']):
        cats.append('Culture > Divers')
    if any(w in text for w in ['lecture', 'conte', 'poésie']):
        cats.append('Culture > Divers')
    
    if any(w in text for w in ['dégustation', 'cave', 'vigneron', 'oenolog']):
        cats.append('Gastronomie > Dégustation')
    if any(w in text for w in ['marché', 'brocante', 'foire']):
        cats.append('Gastronomie > Marché')
    if any(w in text for w in ['gastronomie', 'culinaire', 'cuisine', 'chocolat', 'brunch']):
        cats.append('Gastronomie > Gastronomie')
    
    if any(w in text for w in ['randonnée', 'course', 'marathon', 'trail', 'vélo', 'cyclisme', 'football', 'tennis', 'sport', 'athlétisme']):
        cats.append('Sport > Terrestre')
    if any(w in text for w in ['ski', 'snowboard', 'patinage', 'hockey']):
        cats.append('Sport > Glisse')
    if any(w in text for w in ['natation', 'voile', 'kayak', 'paddle', 'nautique']):
        cats.append('Sport > Aquatique')
    
    if any(w in text for w in ['fête', 'carnaval', 'kermesse', 'nationale']):
        cats.append('Famille > Fêtes')
    if any(w in text for w in ['enfant', 'famille', 'junior', 'bébé', 'éveil']):
        cats.append('Famille > Enfants')
    
    if not cats:
        cats.append('Culture > Divers')
    
    return list(dict.fromkeys(cats))[:3]


def get_venue_info(venue_text, title=''):
    text = (venue_text + ' ' + title).lower()
    for venue, info in KNOWN_VENUES.items():
        if venue in text:
            return info['lat'], info['lon'], info['address']
    return 46.2044, 6.1432, venue_text or 'Genève'


def rewrite_desc(text, max_len=280):
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'[.!?]\s+', text)
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
    return '. '.join(result) + '.' if result else text[:max_len]


def find_email(soup):
    page_text = soup.get_text()
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', page_text)
    for a in soup.find_all('a', href=True):
        if 'mailto:' in a['href']:
            email = a['href'].replace('mailto:', '').split('?')[0].strip()
            emails.append(email)
    
    valid = []
    for e in emails:
        e = e.lower().strip()
        if not any(x in e for x in ['noreply', 'no-reply', 'example', 'sentry', 'wixpress', 'googleapis', '.png', '.jpg', 'bootstrap', 'wordpress', 'script']):
            valid.append(e)
    return valid[0] if valid else ''


# ==============================================================
# SOURCE: geneve.ch/agenda - Toutes les pages
# ==============================================================
def scrape_geneve_ch_agenda():
    print("\n=== geneve.ch/agenda ===")
    count = 0
    
    # Parcourir les pages avec filtre Concert, Festival, Exposition, etc
    filters = [
        'Concert', 'Festival', 'Exposition', 'Spectacle%20-%20Th%C3%A9%C3%A2tre',
        'Danse', 'Clubbing', 'Conf%C3%A9rence%20-%20Rencontre', 'Sport',
        'Atelier', 'Animation', 'Balade%20%E2%80%93%20Excursion',
        'Manifestation%20%E2%80%93%20Salon', 'Opera', 'Projection'
    ]
    
    all_links = set()
    
    for filt in filters:
        for page in range(5):
            url = f'https://www.geneve.ch/agenda?f[0]=what:{filt}&page={page}'
            try:
                time.sleep(DELAY)
                r = requests.get(url, headers=HEADERS, timeout=15)
                if r.status_code != 200:
                    continue
                
                soup = BeautifulSoup(r.text, 'html.parser')
                
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if '/agenda/' in href and href != '/agenda' and '?' not in href and href.count('/') >= 2:
                        full = urljoin('https://www.geneve.ch', href)
                        if '/agenda/' in full and full not in all_links:
                            all_links.add(full)
                
            except Exception as ex:
                print(f"  Erreur {filt} page {page}: {str(ex)[:50]}")
    
    print(f"  Total liens uniques trouvés: {len(all_links)}")
    
    for link in all_links:
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
            
            # Description
            desc = ''
            for tag in soup.find_all(['div', 'p'], class_=re.compile(r'field|desc|text|lead|intro', re.I)):
                txt = tag.get_text().strip()
                if 20 < len(txt) < 2000:
                    desc = rewrite_desc(txt)
                    break
            if not desc:
                for p in soup.find_all('p'):
                    txt = p.get_text().strip()
                    if len(txt) > 30:
                        desc = rewrite_desc(txt)
                        break
            
            # Dates
            page_text = soup.get_text()
            
            # Chercher les dates futures (mars 2026+)
            dates_found = re.findall(r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}', page_text.lower())
            
            start_date = None
            end_date = None
            for d in dates_found:
                parsed = parse_date(d)
                if parsed and parsed >= '2026-03-01':
                    if not start_date:
                        start_date = parsed
                    elif parsed > start_date:
                        end_date = parsed
            
            if not start_date:
                # Essayer aussi dates plus proches (février 2026)
                for d in dates_found:
                    parsed = parse_date(d)
                    if parsed and parsed >= '2026-02-01':
                        if not start_date:
                            start_date = parsed
                        elif parsed > start_date:
                            end_date = parsed
            
            if not start_date:
                continue
            if not end_date:
                end_date = start_date
            
            # Lieu
            venue = ''
            for tag in soup.find_all(['span', 'div', 'p'], class_=re.compile(r'venue|lieu|location|address|place|where', re.I)):
                t = tag.get_text().strip()
                if 3 < len(t) < 200:
                    venue = t
                    break
            if not venue:
                # Chercher dans le texte
                venue_match = re.search(r'(?:Lieu|Adresse|Où)\s*[:：]\s*(.+?)(?:\n|<)', page_text, re.I)
                if venue_match:
                    venue = venue_match.group(1).strip()
            if not venue:
                venue = 'Genève'
            
            email = find_email(soup)
            lat, lon, address = get_venue_info(venue, title)
            cats = classify(title, desc)
            
            event = {
                'title': title,
                'description': desc if desc else f"Événement à Genève.",
                'start_date': start_date,
                'end_date': end_date,
                'location': address,
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
                    all_emails.append({'email': email, 'event': title, 'source': 'geneve.ch'})
        
        except Exception as ex:
            print(f"  Erreur {link[:40]}: {str(ex)[:60]}")
    
    print(f"  Total geneve.ch: {count}")
    return count


if __name__ == '__main__':
    print("=" * 60)
    print("SCRAPER GENÈVE V2 - geneve.ch/agenda")
    print("=" * 60)
    
    total = scrape_geneve_ch_agenda()
    
    print(f"\n{'='*60}")
    print(f"NOUVEAUX EVENTS: {len(all_events)}")
    print(f"EMAILS TROUVÉS: {len(all_emails)}")
    
    if all_events:
        with open('geneve_events_v2.json', 'w', encoding='utf-8') as f:
            json.dump(all_events, f, ensure_ascii=False, indent=2)
        print(f"\nEvents sauvegardés dans geneve_events_v2.json")
    
    if all_emails:
        with open('emails_organisateurs/emails_Geneve_v2.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['email', 'event', 'source'])
            for e in all_emails:
                writer.writerow([e['email'], e['event'], e['source']])
        print(f"Emails sauvegardés dans emails_organisateurs/emails_Geneve_v2.csv")
    
    # Stats par catégorie
    cat_count = {}
    for e in all_events:
        for c in e.get('categories', []):
            cat_count[c] = cat_count.get(c, 0) + 1
    if cat_count:
        print(f"\nCatégories:")
        for cat, cnt in sorted(cat_count.items(), key=lambda x: -x[1]):
            print(f"  {cat}: {cnt}")
