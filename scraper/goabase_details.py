"""Phase 2: fetch details for each Goabase event and insert into MapEvent"""
import requests, json, sys, os, re, time, random
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

GOABASE = 'https://www.goabase.net/api/party/json'
MAPEVENT = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api'
HEADERS = {'User-Agent': 'MapEventAI-Bot/1.0 (+https://mapevent.world)', 'Accept': 'application/json'}

GENRE_PATTERNS = [
    (r'\bacid\s*techno\b', 'Music > Electronic > Techno > Acid Techno'),
    (r'\bminimal\s*techno\b', 'Music > Electronic > Techno > Minimal Techno'),
    (r'\bhard\s*techno\b', 'Music > Electronic > Techno > Hard Techno'),
    (r'\bindustrial\s*techno\b', 'Music > Electronic > Techno > Industrial Techno'),
    (r'\bmelodic\s*techno\b', 'Music > Electronic > Techno > Melodic Techno'),
    (r'\bdub\s*techno\b', 'Music > Electronic > Techno > Dub Techno'),
    (r'\bhypnotic\s*techno\b', 'Music > Electronic > Techno > Hypnotic Techno'),
    (r'\bdeep\s*house\b', 'Music > Electronic > House > Deep House'),
    (r'\btech\s*house\b', 'Music > Electronic > House > Tech House'),
    (r'\bprogressive\s*house\b', 'Music > Electronic > House > Progressive House'),
    (r'\bafro\s*house\b', 'Music > Electronic > House > Afro House'),
    (r'\belectro\s*house\b', 'Music > Electronic > House > Electro House'),
    (r'\bpsytrance\b', 'Music > Electronic > Trance > Psytrance'),
    (r'\bpsy[\s-]?trance\b', 'Music > Electronic > Trance > Psytrance'),
    (r'\bfull[\s-]?on\b', 'Music > Electronic > Trance > Full On'),
    (r'\bfullon\b', 'Music > Electronic > Trance > Full On'),
    (r'\bgoa[\s-]?trance\b', 'Music > Electronic > Trance > Goa'),
    (r'\bprogressive\s*psy\b', 'Music > Electronic > Trance > Progressive Psy'),
    (r'\bprog[\s-]?psy\b', 'Music > Electronic > Trance > Progressive Psy'),
    (r'\bdark[\s-]?psy\b', 'Music > Electronic > Trance > Dark Psy'),
    (r'\bdarkpsy\b', 'Music > Electronic > Trance > Dark Psy'),
    (r'\bdark\s*to\s*forest\b', 'Music > Electronic > Trance > Dark Psy'),
    (r'\bforest\s*psy\b', 'Music > Electronic > Trance > Forest'),
    (r'\bforest\b', 'Music > Electronic > Trance > Forest'),
    (r'\bhi[\s-]?tech\b', 'Music > Electronic > Trance > Hi-Tech'),
    (r'\bhitech\b', 'Music > Electronic > Trance > Hi-Tech'),
    (r'\buplifting[\s-]?trance\b', 'Music > Electronic > Trance > Uplifting Trance'),
    (r'\bacid[\s-]?trance\b', 'Music > Electronic > Trance > Acid Trance'),
    (r'\bsuomisaundi\b', 'Music > Electronic > Trance > Psytrance'),
    (r'\bzenonesque\b', 'Music > Electronic > Trance > Progressive Psy'),
    (r'\bnitzhonot\b', 'Music > Electronic > Trance > Full On'),
    (r'\bneurofunk\b', 'Music > Electronic > Drum & Bass > Neurofunk'),
    (r'\bjungle\b', 'Music > Electronic > Drum & Bass > Jungle'),
    (r'\bliquid\s*dnb\b', 'Music > Electronic > Drum & Bass > Liquid DnB'),
    (r'\bdubstep\b', 'Music > Electronic > Bass Music > Dubstep'),
    (r'\briddim\b', 'Music > Electronic > Bass Music > Riddim'),
    (r'\bhardstyle\b', 'Music > Electronic > Hard Music > Hardstyle'),
    (r'\bhardcore\b', 'Music > Electronic > Hard Music > Hardcore'),
    (r'\bgabber\b', 'Music > Electronic > Hard Music > Gabber'),
    (r'\bfrenchcore\b', 'Music > Electronic > Hard Music > Hardcore'),
    (r'\bambient\b', 'Music > Electronic > Chill / Ambient > Ambient'),
    (r'\bdowntempo\b', 'Music > Electronic > Chill / Ambient > Downtempo'),
    (r'\bchill[\s-]?out\b', 'Music > Electronic > Chill / Ambient > Chillout'),
    (r'\btechno[\s-]?trance\b', 'Music > Electronic > Techno'),
    (r'\btechno\b', 'Music > Electronic > Techno'),
    (r'\bhouse\b(?!\s*(?:of|museum|maison|warming))', 'Music > Electronic > House'),
    (r'\btrance\b(?!\s*(?:formation|ition|port|parent|cend))', 'Music > Electronic > Trance'),
    (r'\bdrum\s*(?:and|&|n)\s*bass\b', 'Music > Electronic > Drum & Bass'),
    (r'\bd[\s]?n[\s]?b\b', 'Music > Electronic > Drum & Bass'),
]

def detect_genres(text):
    if not text: return ['Music > Electronic']
    found = []
    for pat, cat in GENRE_PATTERNS:
        if re.search(pat, text.lower()): found.append(cat)
    final = [c for c in found if not any(o != c and o.startswith(c + ' > ') for o in found)]
    r = list(dict.fromkeys(final))[:3]
    return r if r else ['Music > Electronic']

def rewrite_desc(p):
    town = p.get('nameTown','')
    country = p.get('nameCountry','')
    etype = p.get('nameType','Club')
    lineup = p.get('textLineUp','')
    org = p.get('nameOrganizer','')
    more = p.get('textMore','')
    types = {'Club':'Soiree en club','Indoor':'Soiree indoor','Open Air':'Evenement en plein air','Festival':'Festival','In- & Outdoor':'Evenement indoor/outdoor'}
    parts = [f"{types.get(etype,'Evenement')} de musique electronique a {town} ({country})."]
    if org: parts.append(f"Organise par {org}.")
    if lineup:
        artists, genres = [], set()
        for line in lineup.split('\n'):
            line = line.strip()
            if not line: continue
            m = re.match(r'[\d:]+\s*-\s*[\d:]+\s+(.+?)\s*-\s*(.+)', line)
            if m: artists.append(m.group(1).strip()); genres.add(m.group(2).strip())
            else:
                m2 = re.match(r'[\d:]+\s*-?\s*[\d:]*\s*(.+)', line)
                if m2 and len(m2.group(1).strip()) > 2: artists.append(m2.group(1).strip())
        if artists:
            if len(artists) <= 4: parts.append(f"Au programme : {', '.join(artists)}.")
            else: parts.append(f"Au programme : {', '.join(artists[:4])} et {len(artists)-4} autres.")
        if genres: parts.append(f"Styles : {', '.join(sorted(genres))}.")
    fee = p.get('textEntryFee','')
    if fee and fee.strip(): parts.append(f"Entree : {fee.strip()}.")
    return ' '.join(parts)

# Load list
with open('goabase_list.json', 'r', encoding='utf-8') as f:
    all_parties = json.load(f)
print(f"Loaded {len(all_parties)} parties from list", flush=True)

# Check existing
print("Checking existing...", flush=True)
existing = set()
for chunk in [{'south':-90,'north':90,'west':-180,'east':0},{'south':-90,'north':90,'west':0,'east':180}]:
    try:
        r = requests.get(f'{MAPEVENT}/events/viewport', params={**chunk,'zoom':10}, timeout=30)
        data = r.json()
        if data.get('type')=='events' and data.get('d'):
            keys = data['k']
            si = keys.index('source_url') if 'source_url' in keys else -1
            if si >= 0:
                for row in data['d']:
                    url = (row[si] or '').lower()
                    if 'goabase' in url: existing.add(url)
    except: pass
print(f"  {len(existing)} existing Goabase events", flush=True)

new_parties = [p for p in all_parties if p.get('urlPartyHtml','').lower() not in existing]
print(f"  {len(new_parties)} new events to add", flush=True)

# Fetch details
events = []
for i, party in enumerate(new_parties):
    pid = party['id']
    name = party.get('nameParty','')[:40]
    town = party.get('nameTown','')
    
    try:
        r = requests.get(f'{GOABASE}/{pid}', headers=HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"  [{i+1}/{len(new_parties)}] {name} - ERR {r.status_code}", flush=True)
            time.sleep(8)
            continue
        detail = r.json().get('party',{})
    except Exception as e:
        print(f"  [{i+1}/{len(new_parties)}] {name} - ERR {e}", flush=True)
        time.sleep(8)
        continue
    
    full_text = f"{name}\n{detail.get('textLineUp','')}\n{detail.get('textMore','')}"
    cats = detect_genres(full_text)
    desc = rewrite_desc(detail)
    
    ds, de = detail.get('dateStart',''), detail.get('dateEnd','')
    date = time_str = end_date = end_time = None
    if ds:
        try: dt = datetime.fromisoformat(ds); date = dt.strftime('%Y-%m-%d'); time_str = dt.strftime('%H:%M')
        except: pass
    if de:
        try: dt = datetime.fromisoformat(de); end_date = dt.strftime('%Y-%m-%d'); end_time = dt.strftime('%H:%M')
        except: pass
    
    loc = f"{town}, {detail.get('nameCountry','')}" if town else detail.get('nameCountry','')
    src = detail.get('urlParty','') or f"https://www.goabase.net/party/{pid}"
    
    if not date or not detail.get('geoLat'): 
        print(f"  [{i+1}/{len(new_parties)}] {name} - SKIP missing data", flush=True)
        time.sleep(8)
        continue
    
    events.append({
        'title': detail.get('nameParty',''), 'description': desc,
        'date': date, 'time': time_str, 'end_date': end_date, 'end_time': end_time,
        'location': loc, 'latitude': float(detail.get('geoLat',0)), 'longitude': float(detail.get('geoLon',0)),
        'categories': cats, 'source_url': src, 'validation_status': 'auto_validated',
    })
    print(f"  [{i+1}/{len(new_parties)}] {name} ({town}) -> {cats}", flush=True)
    time.sleep(8 + random.uniform(0, 3))

print(f"\n{len(events)} events ready", flush=True)

# Save
with open('goabase_events_to_add.json', 'w', encoding='utf-8') as f:
    json.dump(events, f, ensure_ascii=False, indent=2)

# Insert
print(f"\nInserting {len(events)} events...", flush=True)
success = 0
for i in range(0, len(events), 20):
    batch = events[i:i+20]
    try:
        r = requests.post(f'{MAPEVENT}/events/scraped/batch', json={'events': batch}, timeout=30)
        if r.status_code in [200,201]:
            n = r.json().get('inserted', r.json().get('count', len(batch)))
            success += n
            print(f"  Batch {i//20+1}: +{n} (total: {success})", flush=True)
        else:
            print(f"  Batch {i//20+1}: ERR {r.status_code} - {r.text[:150]}", flush=True)
    except Exception as e:
        print(f"  Batch {i//20+1}: ERR {e}", flush=True)
    time.sleep(1)

print(f"\nDONE: {success} events added", flush=True)

# Stats
genres = {}
for e in events:
    for c in e['categories']: genres[c] = genres.get(c,0)+1
print("\nGenre distribution:")
for g, c in sorted(genres.items(), key=lambda x: -x[1]):
    print(f"  {c:3d}x {g}", flush=True)
