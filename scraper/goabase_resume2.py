# -*- coding: utf-8 -*-
"""Goabase scraper - RESUME v2 with bulletproof error handling"""
import requests, json, sys, os, re, time, random
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8'
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except: pass

GOABASE = 'https://www.goabase.net/api/party/json'
MAPEVENT = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api'
HDR = {'User-Agent': 'MapEventAI-Bot/1.0', 'Accept': 'application/json'}
SAVE_FILE = 'goabase_events_to_add.json'

GP = [
    (r'\bacid.techno\b', 'Music > Electronic > Techno > Acid Techno'),
    (r'\bminimal.techno\b', 'Music > Electronic > Techno > Minimal Techno'),
    (r'\bhard.techno\b', 'Music > Electronic > Techno > Hard Techno'),
    (r'\bmelodic.techno\b', 'Music > Electronic > Techno > Melodic Techno'),
    (r'\bdeep.house\b', 'Music > Electronic > House > Deep House'),
    (r'\btech.house\b', 'Music > Electronic > House > Tech House'),
    (r'\bprogressive.house\b', 'Music > Electronic > House > Progressive House'),
    (r'\bafro.house\b', 'Music > Electronic > House > Afro House'),
    (r'\bpsytrance\b', 'Music > Electronic > Trance > Psytrance'),
    (r'\bpsy.trance\b', 'Music > Electronic > Trance > Psytrance'),
    (r'\bfull.on\b', 'Music > Electronic > Trance > Full On'),
    (r'\bfullon\b', 'Music > Electronic > Trance > Full On'),
    (r'\bgoa.trance\b', 'Music > Electronic > Trance > Goa'),
    (r'\bprogressive.psy\b', 'Music > Electronic > Trance > Progressive Psy'),
    (r'\bdark.psy\b', 'Music > Electronic > Trance > Dark Psy'),
    (r'\bdarkpsy\b', 'Music > Electronic > Trance > Dark Psy'),
    (r'\bforest.psy\b', 'Music > Electronic > Trance > Forest'),
    (r'\bforest\b', 'Music > Electronic > Trance > Forest'),
    (r'\bhitech\b', 'Music > Electronic > Trance > Hi-Tech'),
    (r'\bhi.tech\b', 'Music > Electronic > Trance > Hi-Tech'),
    (r'\bsuomisaundi\b', 'Music > Electronic > Trance > Psytrance'),
    (r'\bzenonesque\b', 'Music > Electronic > Trance > Progressive Psy'),
    (r'\bneurofunk\b', 'Music > Electronic > Drum & Bass > Neurofunk'),
    (r'\bjungle\b', 'Music > Electronic > Drum & Bass > Jungle'),
    (r'\bdubstep\b', 'Music > Electronic > Bass Music > Dubstep'),
    (r'\bhardstyle\b', 'Music > Electronic > Hard Music > Hardstyle'),
    (r'\bhardcore\b', 'Music > Electronic > Hard Music > Hardcore'),
    (r'\bgabber\b', 'Music > Electronic > Hard Music > Gabber'),
    (r'\bambient\b', 'Music > Electronic > Chill / Ambient > Ambient'),
    (r'\bdowntempo\b', 'Music > Electronic > Chill / Ambient > Downtempo'),
    (r'\btechno.trance\b', 'Music > Electronic > Techno'),
    (r'\btechno\b', 'Music > Electronic > Techno'),
    (r'\bhouse\b', 'Music > Electronic > House'),
    (r'\btrance\b', 'Music > Electronic > Trance'),
    (r'\bdrum.(?:and|&|n).bass\b', 'Music > Electronic > Drum & Bass'),
]

def safe(s):
    if not s: return ''
    return ''.join(c if ord(c) < 65536 else '?' for c in str(s))

def genres(txt):
    if not txt: return ['Music > Electronic']
    t = safe(txt).lower()
    f = []
    for p, c in GP:
        if re.search(p, t): f.append(c)
    r = [c for c in f if not any(o != c and o.startswith(c+' > ') for o in f)]
    return list(dict.fromkeys(r))[:3] or ['Music > Electronic']

def desc(p):
    tw = safe(p.get('nameTown',''))
    co = safe(p.get('nameCountry',''))
    ty = {'Club':'Soiree club','Indoor':'Soiree indoor','Open Air':'Open air','Festival':'Festival'}.get(str(p.get('nameType','')),'Evenement')
    parts = [f"{ty} musique electronique, {tw} ({co})."]
    o = safe(p.get('nameOrganizer',''))
    if o: parts.append(f"Par {o}.")
    lu = safe(p.get('textLineUp',''))
    if lu:
        ar, gs = [], set()
        for l in lu.split('\n'):
            l = l.strip()
            if not l: continue
            m = re.match(r'[\d:]+\s*-\s*[\d:]+\s+(.+?)\s*-\s*(.+)', l)
            if m: ar.append(m.group(1).strip()); gs.add(m.group(2).strip())
        if ar:
            parts.append(f"Line-up: {', '.join(ar[:5])}{'...' if len(ar)>5 else ''}.")
        if gs:
            parts.append(f"Styles: {', '.join(sorted(gs))}.")
    return ' '.join(parts)[:500]

# Load saved events
events = []
if os.path.exists(SAVE_FILE):
    try:
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            events = json.load(f)
    except: pass
print(f"Previously saved: {len(events)}", flush=True)

saved_urls = {safe(e.get('source_url','')).lower() for e in events}

# Load list
with open('goabase_list.json', 'r', encoding='utf-8') as f:
    parties = json.load(f)

# Check DB
db_urls = set()
for ch in [{'south':-90,'north':90,'west':-180,'east':0},{'south':-90,'north':90,'west':0,'east':180}]:
    try:
        r = requests.get(f'{MAPEVENT}/events/viewport', params={**ch,'zoom':10}, timeout=30)
        d = r.json()
        if d.get('type')=='events' and d.get('d'):
            k = d['k']
            si = k.index('source_url') if 'source_url' in k else -1
            if si>=0:
                for row in d['d']:
                    u = safe(row[si] or '').lower()
                    if 'goabase' in u: db_urls.add(u)
    except: pass
print(f"In DB: {len(db_urls)}", flush=True)

# Filter remaining
remaining = []
for p in parties:
    url1 = safe(p.get('urlPartyHtml','')).lower()
    url2 = f"https://www.goabase.net/party/{p['id']}".lower()
    if url1 in db_urls or url2 in db_urls:
        continue
    if url1 in saved_urls or url2 in saved_urls:
        continue
    remaining.append(p)

print(f"Remaining: {len(remaining)}", flush=True)

errors = 0
for i, p in enumerate(remaining):
    pid = p['id']
    try:
        nm = safe(p.get('nameParty',''))[:35]
        tw = safe(p.get('nameTown',''))
    except:
        nm = f"party-{pid}"
        tw = "?"
    
    try:
        r = requests.get(f'{GOABASE}/{pid}', headers=HDR, timeout=20)
        if r.status_code != 200:
            print(f"[{i+1}/{len(remaining)}] {nm} HTTP{r.status_code}", flush=True)
            time.sleep(8)
            continue
        
        raw = r.text
        dt = json.loads(raw).get('party', {})
        
        txt = f"{safe(dt.get('nameParty',''))}\n{safe(dt.get('textLineUp',''))}\n{safe(dt.get('textMore',''))}"
        cats = genres(txt)
        
        ds = str(dt.get('dateStart',''))
        de = str(dt.get('dateEnd',''))
        date = tm = ed = et = None
        try:
            if ds: d2 = datetime.fromisoformat(ds); date = d2.strftime('%Y-%m-%d'); tm = d2.strftime('%H:%M')
            if de: d3 = datetime.fromisoformat(de); ed = d3.strftime('%Y-%m-%d'); et = d3.strftime('%H:%M')
        except: pass
        
        loc = f"{safe(tw)}, {safe(dt.get('nameCountry',''))}" if tw else safe(dt.get('nameCountry',''))
        src = safe(dt.get('urlParty','')) or f"https://www.goabase.net/party/{pid}"
        
        lat_val = dt.get('geoLat')
        lon_val = dt.get('geoLon')
        
        if not date or not lat_val:
            print(f"[{i+1}/{len(remaining)}] {nm} SKIP", flush=True)
            time.sleep(8)
            continue
        
        ev = {
            'title': safe(dt.get('nameParty',''))[:200],
            'description': desc(dt),
            'date': date, 'time': tm, 'end_date': ed, 'end_time': et,
            'location': safe(loc)[:200],
            'latitude': float(lat_val),
            'longitude': float(lon_val),
            'categories': cats,
            'source_url': src,
            'validation_status': 'auto_validated',
        }
        events.append(ev)
        
        cs = ','.join(c.split('>')[-1].strip() for c in cats)
        print(f"[{i+1}/{len(remaining)}] {nm} ({tw}) -> {cs}", flush=True)
        
    except Exception as e:
        errors += 1
        print(f"[{i+1}/{len(remaining)}] {nm} ERR:{str(e)[:50]}", flush=True)
    
    # Save every 5
    if i % 5 == 4:
        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(events, f, ensure_ascii=False, indent=2)
        except: pass
    
    time.sleep(8 + random.uniform(0, 3))

# Final save
with open(SAVE_FILE, 'w', encoding='utf-8') as f:
    json.dump(events, f, ensure_ascii=False, indent=2)
print(f"\nTotal: {len(events)} events ({errors} errors)", flush=True)

# Insert new ones (only those not yet in DB)
new_events = [e for e in events if e.get('source_url','').lower() not in db_urls]
print(f"New to insert: {len(new_events)}", flush=True)

ok = 0
for i in range(0, len(new_events), 20):
    b = new_events[i:i+20]
    try:
        r = requests.post(f'{MAPEVENT}/events/scraped/batch', json={'events': b}, timeout=30)
        if r.status_code in [200, 201]:
            n = r.json().get('inserted', r.json().get('count', len(b)))
            ok += n
            print(f"  +{n} (total:{ok})", flush=True)
        else:
            print(f"  ERR {r.status_code}", flush=True)
    except Exception as e:
        print(f"  ERR: {e}", flush=True)
    time.sleep(1)

print(f"\nDONE: {ok} new inserted", flush=True)
