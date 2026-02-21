# -*- coding: utf-8 -*-
"""
MEGA AUDIT V2 - Vérifie TOUS les events, TOUTES les catégories.
Pour chaque event: lit titre + description, vérifie que CHAQUE catégorie est justifiée.
Sauvegarde progression toutes les 25 events.
Corrige automatiquement les catégories injustifiées.
"""
import json, sys, os, re, requests, time
from datetime import datetime, date

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except: pass

MAPEVENT = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api'
PROGRESS_FILE = 'mega_audit_progress.json'
ISSUES_FILE = 'mega_audit_issues.json'

# ============================================================
# CATEGORY DETECTION - chaque catégorie a ses mots-clés
# Si AUCUN mot-clé trouvé dans titre+desc => catégorie injustifiée
# ============================================================

CAT_RULES = {
    # ===== MUSIC =====
    'electronic': {
        'match': [r'\btechno\b', r'\bhouse\b', r'\btrance\b', r'\bpsytrance\b',
                  r'\bdrum\s*(?:and|&|n)\s*bass\b', r'\bdnb\b', r'\bdubstep\b',
                  r'\bedm\b', r'\belectro(?:nic|nique)?\b', r'\brave\b',
                  r'\bdj[\s\.\-]', r'\bdj$', r'\bclub\s+night',
                  r'\bhardstyle\b', r'\bgabber\b', r'\bhardcore\b',
                  r'\bambient\b', r'\bdowntempo\b', r'\bminimal\b',
                  r'\bdeep\s+house\b', r'\btech\s+house\b', r'\bprogressive\b',
                  r'\bdarkpsy\b', r'\bforest\s+psy\b', r'\bsynthwave\b',
                  r'\bindustrial\b', r'\bmusique\s+[eé]lectronique\b',
                  r'\bsound\s*system\b', r'\bdancefloor\b', r'\bbeat\b',
                  r'\bofenbach\b', r'\bmix\b.*\bdj\b', r'\bdj\b.*\bmix\b'],
        'cats': ['Music > Electronic'],
    },
    'music_general': {
        'match': [r'\bconcert\b', r'\bmusique\b', r'\bmusic\b', r'\bchanson\b',
                  r'\borchestre\b', r'\bsymphoni', r'\bop[eé]ra\b',
                  r'\br[eé]cital\b', r'\bchorale?\b', r'\bch[oœ]ur\b',
                  r'\bjazz\b', r'\bblues\b', r'\brock\b', r'\bm[eé]tal\b',
                  r'\bpunk\b', r'\bhip.?hop\b', r'\brap\b', r'\breggae\b',
                  r'\bsoul\b', r'\bfunk\b', r'\bfolk\b', r'\bpop\b',
                  r'\bclassique\b', r'\bbaroque\b', r'\bchant\b',
                  r'\bguitar[ei]?\b', r'\bpiano\b', r'\bviolon\b',
                  r'\borgue\b', r'\bflûte\b', r'\bharpe\b', r'\btrompette\b',
                  r'\bsaxophone\b', r'\bbatterie\b.*\bmusic',
                  r'\bgroupe\b.*\bmusic', r'\bmusic.*\bgroupe\b',
                  r'\bcompositeur\b', r'\binterpr[eè]te\b',
                  r'\bsonate?\b', r'\bconcerto\b', r'\bcantate\b',
                  r'\blieder\b', r'\bm[eé]lodie\b.*\bmusic',
                  r'\bfestival\s+(?:de\s+)?musique\b',
                  r'\bmusicien', r'\bartiste\b.*\bmusic'],
        'cats': ['Music'],
    },
    'sport': {
        'match': [r'\bcourse\s+[àa]\s+pied\b', r'\bmarathon\b', r'\btrail\b',
                  r'\brandonnée\b', r'\bv[eé]lo\b', r'\bcyclisme\b',
                  r'\bfootball\b', r'\btennis\b', r'\bnatation\b',
                  r'\bski\b', r'\bsnowboard\b', r'\bhockey\b',
                  r'\bbasket\b', r'\bescalade\b', r'\balpinisme\b',
                  r'\byoga\b', r'\bfitness\b', r'\bgolf\b', r'\bvoile\b',
                  r'\bsport\b', r'\bathl[eé]', r'\bcomp[eé]tition\b',
                  r'\btournoi\b', r'\bgymnastique\b', r'\bboxe\b',
                  r'\bjudo\b', r'\bkarat[eé]\b', r'\brugby\b',
                  r'\bpatinaoire\b', r'\bpatinage\b', r'\bluge\b',
                  r'\bcanoé\b', r'\bkayak\b', r'\bplongée\b',
                  r'\bswim\b', r'\brun\b', r'\bbike\b', r'\brace\b',
                  r'\butmb\b', r'\biron\s*man\b', r'\btriathlon\b',
                  r'\bcross\b', r'\brelay\b', r'\bsprint\b'],
        'cats': ['Sport'],
    },
    'theatre': {
        'match': [r'\bth[eé][aâ]tre\b', r'\bspectacle\b', r'\bcom[eé]die\b',
                  r'\bpi[eè]ce\b.*\bth[eé]', r'\bimprovisation\b',
                  r'\bcirque\b', r'\bmarionnett', r'\bclown\b',
                  r'\bmagie\b', r'\bmagicien\b', r'\bsc[eè]ne\b',
                  r'\bdramaturgie\b', r'\bmetteur\s+en\s+sc[eè]ne\b',
                  r'\bcom[eé]dien\b', r'\bacteur\b', r'\bactrice\b',
                  r'\btragiqu', r'\bmonologue\b',
                  r'\bone.man.show\b', r'\bone.woman.show\b'],
        'cats': ['Arts Vivants > Théâtre'],
    },
    'danse': {
        'match': [r'\bdanse\b', r'\bballet\b', r'\bchor[eé]graphi',
                  r'\bdanseur', r'\bdanseuse\b', r'\bflamenco\b',
                  r'\btango\b', r'\bsalsa\b', r'\bvalse\b',
                  r'\bbollywood\b', r'\bcontempor.*dans',
                  r'\bclassiqu.*dans', r'\bdans.*classiqu'],
        'cats': ['Arts Vivants > Danse'],
    },
    'humour': {
        'match': [r'\bhumour\b', r'\bhumorist', r'\bstand.?up\b',
                  r'\bcomedy\b', r'\bsketch\b', r'\brire\b',
                  r'\bblague\b', r'\bone.man\b', r'\bone.woman\b'],
        'cats': ['Culture > Humour'],
    },
    'expo': {
        'match': [r'\bexposition\b', r'\bexpo\b', r'\bgalerie\b',
                  r'\bvernissage\b', r'\bpeinture\b', r'\bsculpture\b',
                  r'\bpalette\b', r'\bartiste\b.*\b(?:peint|sculpt|œuvre|expos)',
                  r'\bœuvres?\b', r'\bphotographi', r'\binstallation\b.*\bart',
                  r'\bmus[eé]e\b.*\b(?:expos|visite|collection)',
                  r'\bcollection\b', r'\bbeaux.arts\b', r'\bart\s+contemporain\b',
                  r'\bgravure\b', r'\baquarelle\b', r'\bdessin\b.*\bart',
                  r'\brétrospective\b', r'\bcéramique\b'],
        'cats': ['Culture > Expositions'],
    },
    'food': {
        'match': [r'\bd[eé]gustation\b', r'\bgastronomie\b', r'\bcuisine\b',
                  r'\bvin\b', r'\bbi[eè]re\b', r'\bfromage\b', r'\bfondue\b',
                  r'\bbrunch\b', r'\brestaurant\b', r'\btraiteur\b',
                  r'\bcocktail\b', r'\bap[eé]r(?:o|itif)\b',
                  r'\bvigneron\b', r'\bsommelier\b', r'\bcave\b.*\bvin',
                  r'\bvin\b.*\bcave\b', r'\bcaviste\b',
                  r'\bmarch[eé]\b.*\b(?:product|terroir|paysan|fermier|artisan)',
                  r'\bfood\b', r'\bdrink\b', r'\bcaf[eé]\b.*\bspecial',
                  r'\brecette\b', r'\bchocolat\b', r'\bpâtisserie\b'],
        'cats': ['Food & Drinks'],
    },
    'famille': {
        'match': [r'\benfant', r'\bfamille\b', r'\bfamily\b', r'\bkids?\b',
                  r'\bjeunes?\b', r'\bb[eé]b[eé]', r'\bparent',
                  r'\bjeu\s+de\b', r'\bjeux\b.*\benfant',
                  r'\benfant.*\bjeux\b', r'\bpour\s+les\s+(?:petit|enfant)',
                  r'\bà\s+partir\s+de\s+\d+\s+ans\b',
                  r'\bd[eè]s\s+\d+\s+ans\b',
                  r'\bjuvenile\b', r'\bjunior\b', r'\bado(?:lescent)?\b'],
        'cats': ['Famille & Enfants'],
    },
    'atelier': {
        'match': [r'\batelier\b', r'\bworkshop\b', r'\bcours\b',
                  r'\bstage\b', r'\bformation\b', r'\bapprendr',
                  r'\binitiation\b', r'\bd[eé]couverte\b.*\bpratique',
                  r'\bpratique\b.*\bd[eé]couverte\b',
                  r'\bmaster\s*class\b', r'\benseignement\b'],
        'cats': ['Culture > Ateliers'],
    },
    'conference': {
        'match': [r'\bconf[eé]rence\b', r'\bd[eé]bat\b', r'\bs[eé]minaire\b',
                  r'\bcolloque\b', r'\brencontre\b.*\bauteur',
                  r'\btable.ronde\b', r'\bsymposium\b',
                  r'\bintervention\b.*\bpubli'],
        'cats': ['Culture > Conférences & Rencontres'],
    },
    'nature': {
        'match': [r'\bnature\b', r'\bjardin\b', r'\bbotanique\b',
                  r'\bplein\s+air\b', r'\bbalade\b', r'\bpromenade\b',
                  r'\bfor[eê]t\b', r'\bobservation\b.*\b(?:oiseau|faune|flore)',
                  r'\bécologi', r'\benvironnem', r'\bbiodiversit'],
        'cats': ['Nature & Plein Air'],
    },
    'cinema': {
        'match': [r'\bcin[eé]ma\b', r'\bfilm\b', r'\bprojection\b',
                  r'\bdocumentaire\b', r'\bcourt.m[eé]trage\b',
                  r'\blong.m[eé]trage\b', r'\br[eé]alisateur\b',
                  r'\bscreening\b'],
        'cats': ['Culture > Cinéma & Projections'],
    },
    'visite': {
        'match': [r'\bvisite\b', r'\bpatrimoine\b', r'\bguid[eé]e?\b',
                  r'\bhistorique\b', r'\bmonument\b', r'\bch[aâ]teau\b',
                  r'\b[eé]glise\b', r'\bcath[eé]drale\b',
                  r'\barch[eé]ologi', r'\bheritage\b'],
        'cats': ['Culture > Visites & Patrimoine'],
    },
    'litterature': {
        'match': [r'\blecture\b', r'\blitt[eé]rature\b', r'\blivre\b',
                  r'\bconte\b', r'\bpo[eé]si', r'\bauteur\b',
                  r'\broman\b', r'\bd[eé]dicace\b', r'\b[eé]criv',
                  r'\bbiblioth[eè]que\b', r'\bsalon\s+du\s+livre\b'],
        'cats': ['Culture > Littérature & Conte'],
    },
    'fete': {
        'match': [r'\bcarnaval\b', r'\bf[eê]te\b(?!\s+du\s+livre)',
                  r'\bparade\b', r'\bd[eé]fil[eé]\b',
                  r'\bbrocante\b', r'\bvide.grenier\b',
                  r'\bkermesse\b', r'\bfoire\b(?!.*\bsalon)'],
        'cats': ['Loisirs & Animation > Défilés & Fêtes'],
    },
    'marche': {
        'match': [r'\bmarch[eé]\b.*\b(?:noël|noel|paysan|terroir|fermier|artisan|puces|aux\s+fleurs|nocturne|de\s+noel)',
                  r'\bbrocante\b', r'\bvide.grenier\b'],
        'cats': ['Loisirs & Animation > Défilés & Fêtes'],
    },
    'festival': {
        'match': [r'\bfestival\b', r'\bsalon\b(?!.*\bcoiffure)',
                  r'\bfoire\b.*\b(?:intern|nation|commerc)'],
        'cats': ['Festivals & Grandes Fêtes'],
    },
    'bienetre': {
        'match': [r'\bbien.?[eê]tre\b', r'\bwellness\b', r'\bspa\b',
                  r'\bm[eé]ditation\b', r'\bsophrologie\b',
                  r'\brelaxation\b', r'\bth[eé]rmes?\b',
                  r'\bmassage\b', r'\bacupuncture\b'],
        'cats': ['Bien-être'],
    },
    'business': {
        'match': [r'\bnetworking\b', r'\bbusiness\b', r'\bentrepren',
                  r'\bstartup\b', r'\bstart.up\b', r'\binnovation\b',
                  r'\btechnolog', r'\bhackathon\b', r'\bpitch\b',
                  r'\bcoworking\b'],
        'cats': ['Business & Communauté'],
    },
}

def has_kw(text, patterns):
    for p in patterns:
        if re.search(p, text): return True
    return False

def detect_categories(title, desc):
    """Detect correct categories from title + description content."""
    text = f"{title} {desc}".lower()
    detected = []
    for rule_name, rule in CAT_RULES.items():
        if has_kw(text, rule['match']):
            detected.extend(rule['cats'])
    return list(dict.fromkeys(detected))[:3] or ['Culture']

def normalize_cat(cat):
    """Normalize a category string for comparison."""
    return cat.lower().strip().replace('é', 'e').replace('è', 'e').replace('ê', 'e').replace('â', 'a').replace('î', 'i').replace('ô', 'o').replace('û', 'u')

def cat_is_justified(cat, text):
    """Check if a SPECIFIC category is justified by the text content."""
    cn = normalize_cat(cat)
    
    # Map each possible category to its detection rule
    cat_to_rule = {
        'electronic': 'electronic', 'electro': 'electronic', 'techno': 'electronic',
        'house': 'electronic', 'trance': 'electronic', 'drum & bass': 'electronic',
        'bass music': 'electronic', 'hard music': 'electronic',
        'chill': 'electronic', 'ambient': 'electronic',
        
        'music': 'music_general',
        'pop': 'music_general', 'rock': 'music_general', 'metal': 'music_general',
        'jazz': 'music_general', 'blues': 'music_general', 'classique': 'music_general',
        'folk': 'music_general', 'urban': 'music_general', 'reggae': 'music_general',
        'hip-hop': 'music_general', 'rap': 'music_general', 'soul': 'music_general',
        'funk': 'music_general', 'chanson': 'music_general', 'variete': 'music_general',
        'opera': 'music_general', 'world': 'music_general',
        
        'sport': 'sport', 'terrestre': 'sport', 'aquatique': 'sport', 'glisse': 'sport',
        
        'theatre': 'theatre', 'spectacle': 'theatre', 'cirque': 'theatre',
        'arts vivants': 'theatre',
        
        'danse': 'danse', 'ballet': 'danse',
        
        'humour': 'humour', 'comedy': 'humour', 'stand-up': 'humour',
        
        'exposition': 'expo', 'expositions': 'expo', 'galerie': 'expo',
        
        'food': 'food', 'drinks': 'food', 'degustation': 'food', 'gastronomie': 'food',
        
        'famille': 'famille', 'enfants': 'famille', 'family': 'famille', 'kids': 'famille',
        
        'atelier': 'atelier', 'ateliers': 'atelier', 'workshop': 'atelier', 'workshops': 'atelier',
        
        'conference': 'conference', 'conferences': 'conference', 'rencontres': 'conference',
        
        'nature': 'nature', 'plein air': 'nature',
        
        'cinema': 'cinema', 'projections': 'cinema', 'film': 'cinema',
        
        'visite': 'visite', 'patrimoine': 'visite',
        
        'litterature': 'litterature', 'conte': 'litterature',
        
        'defil': 'fete', 'fetes': 'fete', 'carnaval': 'fete',
        'brocante': 'marche',
        
        'festival': 'festival', 'grandes fetes': 'festival',
        
        'bien-etre': 'bienetre', 'wellness': 'bienetre',
        
        'business': 'business', 'communaute': 'business', 'networking': 'business',
    }
    
    # Find which rule applies to this category
    rule_name = None
    for key, rule in cat_to_rule.items():
        if key in cn:
            rule_name = rule
            break
    
    if not rule_name:
        # Generic/unknown category - check common generic ones
        if cn in ['culture', 'evenement', 'divertissement', 'loisirs', 'animation']:
            return True  # These are too generic to reject
        return True  # Unknown category, don't touch
    
    # Check if the rule's keywords match the text
    rule = CAT_RULES.get(rule_name)
    if not rule:
        return True
    
    return has_kw(text, rule['match'])


def check_event(ev_basic, ev_full):
    """Full check of one event. Returns (issues_list, fix_dict_or_None)."""
    eid = ev_basic['id']
    title = (ev_full.get('title') or ev_basic.get('title', '')).strip()
    desc = (ev_full.get('description') or '').strip()
    location = (ev_full.get('location') or ev_basic.get('location', '')).strip()
    lat = ev_full.get('latitude') or ev_basic.get('latitude')
    lng = ev_full.get('longitude') or ev_basic.get('longitude')
    date_str = ev_full.get('date') or ev_basic.get('date', '')
    source_url = (ev_full.get('source_url') or ev_basic.get('source_url', '')).lower()
    cats = ev_full.get('categories') or ev_basic.get('categories', [])
    
    if isinstance(cats, str):
        cat_list = [c.strip() for c in cats.split(',') if c.strip()]
    elif isinstance(cats, list):
        cat_list = list(cats)
    else:
        cat_list = []
    
    text = f"{title} {desc}".lower()
    issues = []
    fix = None
    
    # Skip Goabase events for category check (they're all electronic, correct)
    is_goabase = 'goabase' in source_url
    
    # ===== 1. CATEGORY CHECK =====
    if not is_goabase and cat_list:
        unjustified = []
        justified = []
        for cat in cat_list:
            if cat_is_justified(cat, text):
                justified.append(cat)
            else:
                unjustified.append(cat)
        
        if unjustified:
            # Determine correct categories from content
            detected = detect_categories(title, desc)
            # Merge justified + detected, deduplicate
            new_cats = list(dict.fromkeys(justified + detected))[:3]
            if not new_cats:
                new_cats = detected[:3] or ['Culture']
            
            issues.append(f"WRONG_CATS:{','.join(unjustified)}")
            fix = {'id': eid, 'categories': new_cats}
    
    # ===== 2. DATE CHECK =====
    if date_str:
        try:
            d = datetime.strptime(str(date_str)[:10], '%Y-%m-%d').date()
            if d < date(2025, 1, 1):
                issues.append(f'DATE_OLD:{date_str}')
            if d > date(2028, 12, 31):
                issues.append(f'DATE_FAR:{date_str}')
        except:
            issues.append(f'DATE_INVALID:{date_str}')
    
    # ===== 3. LOCATION/COORDS CHECK =====
    if lat is not None and lng is not None:
        lat_f = float(lat)
        lng_f = float(lng)
        
        if abs(lat_f) < 0.1 and abs(lng_f) < 0.1:
            issues.append('COORDS_NULL_ISLAND')
        
        if abs(lat_f) > 90 or abs(lng_f) > 180:
            issues.append('COORDS_INVALID')
        
        loc_lower = location.lower()
        # Swiss check
        swiss_kw = ['suisse', 'schweiz', 'switzerland', 'zürich', 'zurich',
                     'genève', 'geneve', 'bern', 'lausanne', 'bâle', 'basel',
                     'valais', 'vaud', 'fribourg', 'neuchâtel', 'sion', 'sierre',
                     'zermatt', 'montreux', 'nendaz', 'crans-montana', 'verbier',
                     'lucerne', 'luzern', 'interlaken', 'davos', 'st. gallen',
                     'thun', 'biel', 'aarau', 'olten', 'winterthur', 'schaffhausen']
        if any(kw in loc_lower for kw in swiss_kw):
            if not (45.7 <= lat_f <= 48.0 and 5.8 <= lng_f <= 10.6):
                issues.append(f'COORDS_WRONG_CH')
        
        # France check
        france_kw = ['france', 'paris', 'lyon', 'marseille', 'toulouse',
                      'bordeaux', 'nantes', 'strasbourg', 'lille', 'nancy',
                      'montpellier', 'rennes', 'grenoble', 'nice', 'rouen']
        if any(kw in loc_lower for kw in france_kw):
            if not (41 <= lat_f <= 51.5 and -5.5 <= lng_f <= 10):
                issues.append(f'COORDS_WRONG_FR')
    else:
        issues.append('NO_COORDS')
    
    if not location or len(location) < 3:
        issues.append('NO_LOCATION')
    
    return issues, fix


# ============================================================
# MAIN
# ============================================================

# Load progress
checked_ids = set()
if os.path.exists(PROGRESS_FILE):
    try:
        with open(PROGRESS_FILE, 'r') as f:
            progress = json.load(f)
        checked_ids = set(progress.get('checked_ids', []))
        print(f"Resuming: {len(checked_ids)} already checked", flush=True)
    except: pass

all_issues = []
if os.path.exists(ISSUES_FILE):
    try:
        with open(ISSUES_FILE, 'r', encoding='utf-8') as f:
            all_issues = json.load(f)
    except: pass

# Fetch all events
print("Fetching all events...", flush=True)
events = []
seen_ids = set()
viewports = [
    {'south': -90, 'north': 0, 'west': -180, 'east': 180},
    {'south': 0, 'north': 45, 'west': -180, 'east': 0},
    {'south': 0, 'north': 45, 'west': 0, 'east': 180},
    {'south': 45, 'north': 48, 'west': -10, 'east': 5},
    {'south': 45, 'north': 48, 'west': 5, 'east': 15},
    {'south': 48, 'north': 52, 'west': -10, 'east': 5},
    {'south': 48, 'north': 52, 'west': 5, 'east': 15},
    {'south': 52, 'north': 90, 'west': -180, 'east': 0},
    {'south': 52, 'north': 90, 'west': 0, 'east': 180},
]
for ch in viewports:
    try:
        r = requests.get(f'{MAPEVENT}/events/viewport', params={**ch, 'zoom': 10}, timeout=30)
        d = r.json()
        if d.get('type') == 'events' and d.get('d'):
            k = d['k']
            for row in d['d']:
                ev = dict(zip(k, row))
                eid = ev.get('id')
                if eid and eid not in seen_ids:
                    seen_ids.add(eid)
                    events.append(ev)
    except: pass

to_check = [ev for ev in events if ev['id'] not in checked_ids]
print(f"Total: {len(events)} | Already: {len(checked_ids)} | To check: {len(to_check)}", flush=True)

# Process
cat_fixes_count = 0
total_issues_count = 0
batch_fixes = []
errors = 0

for i, ev in enumerate(to_check):
    eid = ev['id']
    
    try:
        r = requests.get(f'{MAPEVENT}/events/{eid}', timeout=10)
        if r.status_code != 200:
            checked_ids.add(eid)
            errors += 1
            continue
        full = r.json()
        if isinstance(full, dict) and 'event' in full:
            full = full['event']
        
        issues, fix = check_event(ev, full)
        
        if issues:
            total_issues_count += 1
            cats = full.get('categories') or ev.get('categories', [])
            issue_record = {
                'id': eid,
                'title': (ev.get('title') or '')[:80],
                'issues': issues,
                'categories': cats if isinstance(cats, list) else str(cats),
                'location': str(ev.get('location', ''))[:80],
            }
            if fix:
                issue_record['fix'] = fix['categories']
                batch_fixes.append(fix)
                cat_fixes_count += 1
            all_issues.append(issue_record)
        
        checked_ids.add(eid)
        
    except Exception as e:
        checked_ids.add(eid)
        errors += 1
    
    # Progress every 25
    if (i + 1) % 25 == 0:
        print(f"[{i+1}/{len(to_check)}] issues:{total_issues_count} fixes:{cat_fixes_count} err:{errors}", flush=True)
        
        # Save progress
        with open(PROGRESS_FILE, 'w') as f:
            json.dump({'checked_ids': list(checked_ids)}, f)
        with open(ISSUES_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_issues, f, ensure_ascii=False, indent=2)
        
        # Apply fixes
        if len(batch_fixes) >= 25:
            try:
                r = requests.post(f'{MAPEVENT}/admin/fix-categories', json={'updates': batch_fixes}, timeout=30)
                if r.status_code == 200:
                    n = r.json().get('updated', 0)
                    print(f"  -> Fixed {n} categories", flush=True)
            except: pass
            batch_fixes = []
    
    time.sleep(0.05)

# Final save
with open(PROGRESS_FILE, 'w') as f:
    json.dump({'checked_ids': list(checked_ids)}, f)
with open(ISSUES_FILE, 'w', encoding='utf-8') as f:
    json.dump(all_issues, f, ensure_ascii=False, indent=2)

# Apply remaining fixes
if batch_fixes:
    try:
        for bi in range(0, len(batch_fixes), 50):
            bb = batch_fixes[bi:bi+50]
            r = requests.post(f'{MAPEVENT}/admin/fix-categories', json={'updates': bb}, timeout=30)
            if r.status_code == 200:
                print(f"Final batch: {r.json().get('updated', 0)} fixed", flush=True)
    except: pass

# Summary
print(f"\n{'='*60}", flush=True)
print(f"AUDIT COMPLETE", flush=True)
print(f"{'='*60}", flush=True)
print(f"Checked: {len(checked_ids)}", flush=True)
print(f"Issues: {total_issues_count}", flush=True)
print(f"Category fixes: {cat_fixes_count}", flush=True)
print(f"Errors: {errors}", flush=True)

issue_types = {}
for iss in all_issues:
    for it in iss.get('issues', []):
        key = it.split(':')[0]
        issue_types[key] = issue_types.get(key, 0) + 1

print(f"\nBreakdown:", flush=True)
for k, v in sorted(issue_types.items(), key=lambda x: -x[1]):
    print(f"  {v:5d}x {k}", flush=True)

# Show examples of fixes
cat_fix_examples = [i for i in all_issues if 'fix' in i][:15]
if cat_fix_examples:
    print(f"\nExamples of fixes:", flush=True)
    for ex in cat_fix_examples:
        print(f"  [{ex['id']}] {ex['title'][:50]}", flush=True)
        print(f"    Was: {ex['categories']}", flush=True)
        print(f"    Now: {ex['fix']}", flush=True)
        print(f"    Why: {ex['issues']}", flush=True)

print(f"\nDONE", flush=True)
