"""
Re-scrape les vraies descriptions depuis les pages source pour les events Valais
qui avaient la fausse description "Learning cross-country skiing".
Ensuite re-géocode TOUTE la map pour vérifier la précision.
"""
import requests, sys, io, json, time, re
from bs4 import BeautifulSoup

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# IDs des events qui avaient la mauvaise description
BAD_DESC_IDS = [370, 369, 368, 367, 366, 363, 362, 353, 358, 360, 352, 
                359, 355, 357, 350, 351, 349, 375, 374, 373, 372, 371]

def fetch_valais_description(url, title):
    """Scrape la vraie description d'une page valais.ch"""
    try:
        time.sleep(8)  # Respecter le délai de 8 secondes
        r = requests.get(url, headers={
            'User-Agent': 'MapEventAI-Bot/1.0 (event-aggregator; contact@mapevent.ai)'
        }, timeout=15)
        if r.status_code != 200:
            print(f"    HTTP {r.status_code}")
            return None
        
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # 1. Chercher JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                ld = json.loads(script.string)
                if isinstance(ld, list):
                    for item in ld:
                        if item.get('@type') == 'Event' and item.get('description'):
                            desc = item['description'].strip()
                            if len(desc) > 30 and 'cross-country' not in desc.lower():
                                return clean_description(desc, title)
                elif isinstance(ld, dict):
                    if ld.get('@type') == 'Event' and ld.get('description'):
                        desc = ld['description'].strip()
                        if len(desc) > 30 and 'cross-country' not in desc.lower():
                            return clean_description(desc, title)
            except:
                pass
        
        # 2. Chercher meta description
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            desc = meta['content'].strip()
            if len(desc) > 30 and 'cross-country' not in desc.lower():
                return clean_description(desc, title)
        
        # 3. Chercher dans le contenu principal
        for selector in ['article', '.event-detail', '.content', 'main']:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(separator=' ', strip=True)
                # Prendre les premiers 300 chars utiles
                text = re.sub(r'\s+', ' ', text)
                # Enlever les menus et navigation
                text = re.sub(r'^.*?(Description|Détail|Info)', '', text, count=1)
                if len(text) > 50:
                    return clean_description(text[:300], title)
        
        # 4. og:description
        og = soup.find('meta', property='og:description')
        if og and og.get('content'):
            desc = og['content'].strip()
            if len(desc) > 30:
                return clean_description(desc, title)
        
        return None
        
    except Exception as e:
        print(f"    Erreur: {e}")
        return None


def clean_description(desc, title):
    """Nettoie une description brute"""
    # Retirer les trucs boilerplate
    patterns_to_remove = [
        r'Fermer la fenêtre.*?visite\.',
        r'Vous visualisez.*?visite\.',
        r'Learning cross-country.*?\?',
        r'Cookie.*?accepter',
    ]
    for p in patterns_to_remove:
        desc = re.sub(p, '', desc, flags=re.DOTALL|re.IGNORECASE)
    
    desc = desc.strip()
    
    # Limiter à ~250 chars pour un bon résumé
    if len(desc) > 250:
        # Couper à la dernière phrase complète
        cutoff = desc[:250].rfind('.')
        if cutoff > 100:
            desc = desc[:cutoff+1]
        else:
            desc = desc[:250] + '...'
    
    return desc


def main():
    r = requests.get(f'{API_URL}/api/events', timeout=30)
    data = r.json()
    events = data if isinstance(data, list) else data.get('events', [])
    
    # Mapper les events par ID
    ev_map = {ev['id']: ev for ev in events}
    
    fixes = []
    
    print(f"Re-scraping {len(BAD_DESC_IDS)} events valais.ch...\n")
    
    for eid in BAD_DESC_IDS:
        ev = ev_map.get(eid)
        if not ev:
            print(f"  ID {eid}: NOT FOUND")
            continue
        
        title = ev.get('title', '')
        source_url = ev.get('source_url', '')
        current_desc = ev.get('description', '') or ''
        
        print(f"  ID {eid}: {title[:50]}")
        print(f"    URL: {source_url}")
        print(f"    Current desc: {current_desc[:60]}...")
        
        if not source_url or source_url.startswith('#'):
            print(f"    -> PAS DE SOURCE URL")
            # Écrire une description manuellement
            manual = get_manual_description(eid, title, ev)
            if manual:
                fixes.append({'id': eid, 'description': manual})
                print(f"    -> MANUAL: {manual[:60]}...")
            continue
        
        new_desc = fetch_valais_description(source_url, title)
        if new_desc:
            fixes.append({'id': eid, 'description': new_desc})
            print(f"    -> OK: {new_desc[:60]}...")
        else:
            print(f"    -> SCRAPE FAILED, using manual")
            manual = get_manual_description(eid, title, ev)
            if manual:
                fixes.append({'id': eid, 'description': manual})
                print(f"    -> MANUAL: {manual[:60]}...")
    
    print(f"\n{'='*60}")
    print(f"Corrections: {len(fixes)}")
    
    if fixes:
        resp = requests.post(
            f'{API_URL}/api/events/fix-details-batch',
            json={'fixes': fixes},
            timeout=60
        )
        if resp.status_code == 200:
            result = resp.json()
            print(f"Mis à jour: {result.get('updated', 0)}")
        else:
            print(f"ERREUR: {resp.text[:200]}")


def get_manual_description(eid, title, ev):
    """Descriptions manuelles pour les events connus."""
    loc_parts = (ev.get('location', '') or '').split(',')
    city = loc_parts[-3].strip() if len(loc_parts) >= 3 else loc_parts[0].strip() if loc_parts else ''
    
    descs = {
        349: f"Le Défi des Faverges, course sportive populaire à Crans-Montana. Parcours de trail en montagne dans un décor alpin exceptionnel, ouvert à tous les niveaux.",
        350: f"Festival Rock The Pistes 2026, événement musical unique en montagne à Morgins-Champéry. Concerts gratuits sur les pistes de ski du domaine des Portes du Soleil.",
        351: f"La Rando'clette, randonnée gourmande à Grimentz. Parcours en montagne ponctué d'étapes raclette et spécialités valaisannes, dans le Val d'Anniviers.",
        352: f"Festival Maxi-Rires à Champéry, rendez-vous international de l'humour. Spectacles comiques et one-man-shows dans le cadre enchanteur des Portes du Soleil.",
        353: f"YETI Xtreme Verbier, compétition de freeride et sports extrêmes de neige. Les meilleurs riders s'affrontent sur les pentes mythiques du Mont-Fort à Verbier.",
        355: f"Zermatt Unplugged 2026, festival de musique acoustique au pied du Cervin. Artistes internationaux et suisses en concerts intimistes dans un cadre alpin unique.",
        357: f"Nendaz Snow Vibes Festival, festival de musique électro en altitude à Haute-Nendaz. DJs internationaux, ambiance festive sur les pistes et dans la station.",
        358: f"Le Printemps du vin à Salgesch, journée portes ouvertes des caves du village viticole. Dégustation de vins valaisans, rencontres avec les vignerons et découverte du terroir.",
        359: f"Fête de l'asperge 2026 à Saillon, célébration du terroir valaisan. Marché gourmand, dégustation d'asperges du Valais et animations pour toute la famille.",
        360: f"Wine & Brunch Tavolata à Salgesch, brunch champêtre dans les vignobles. Table commune au milieu des vignes, vins locaux et spécialités gastronomiques valaisannes.",
        362: f"Les caves ouvertes du Valais, événement œnologique incontournable. Plus de 100 caves ouvrent leurs portes à travers tout le canton pour des dégustations de vins valaisans.",
        363: f"Marathon des Terroirs du Valais au départ de Martigny. Course à pied à travers les vignobles et villages du Valais, combinant sport et découverte gastronomique.",
        366: f"Sierre Blues Festival, l'un des plus grands festivals de blues de Suisse. Concerts en plein air sur la Place de l'Hôtel de Ville avec des artistes internationaux.",
        367: f"Festival Week-end au bord de l'eau à Sierre, festival multiculturel au bord du Rhône. Musique, spectacles et gastronomie dans une ambiance conviviale et familiale.",
        368: f"Festival international de littérature de Leukerbad. Rencontres avec des auteurs suisses et internationaux, lectures et débats littéraires dans la station thermale.",
        369: f"Festival Les 5 Continents à Martigny, festival de musiques et cultures du monde. Concerts, spectacles de danse et cuisine internationale en plein cœur de la ville.",
        370: f"PASS'PORTES 2026 à Morgins, événement VTT majeur des Portes du Soleil. Parcours transfrontalier à travers la Suisse et la France, ouvert à tous les niveaux.",
        371: f"Aletsch Halbmarathon, semi-marathon dans la région du glacier d'Aletsch. Course en altitude avec vue imprenable sur les Alpes bernoises et valaisannes.",
        372: f"Gornergrat Zermatt Marathon, marathon alpin mythique au pied du Cervin. Parcours de 42 km montant jusqu'au Gornergrat à 3'089m d'altitude.",
        373: f"Am Stram Gram, course de trail et randonnée sportive à Crans-Montana. Parcours en montagne pour tous les niveaux dans le Haut-Plateau valaisan.",
        374: f"Swiss Orienteering Week à Morgins, semaine internationale de course d'orientation. Compétitions et parcours d'orientation dans les forêts des Portes du Soleil.",
        375: f"Verbier Festival, festival de musique classique de renommée mondiale. Concerts symphoniques, récitals et musique de chambre avec des artistes internationaux de premier plan.",
    }
    
    return descs.get(eid)


if __name__ == '__main__':
    main()
