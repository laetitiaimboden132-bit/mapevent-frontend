# -*- coding: utf-8 -*-
"""Goabase scraper - fetches ONE event at a time, saves after each.
Run in a loop: while ($true) { python scraper/goabase_one_by_one.py; Start-Sleep 9 }
"""
import requests, json, sys, os, re, time, random
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except: pass

GOABASE = 'https://www.goabase.net/api/party/json'
MAPEVENT = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api'
HDR = {'User-Agent': 'MapEventAI-Bot/1.0', 'Accept': 'application/json'}
SAVE = os.path.join(os.path.dirname(__file__), '..', 'goabase_events_to_add.json')
SAVE = os.path.normpath(SAVE)
DONE = os.path.join(os.path.dirname(__file__), '..', 'goabase_done_ids.json')
DONE = os.path.normpath(DONE)

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
    (r'\bneurofunk\b', 'Music > Electronic > Drum & Bass > Neurofunk'),
    (r'\bjungle\b', 'Music > Electronic > Drum & Bass > Jungle'),
    (r'\bdubstep\b', 'Music > Electronic > Bass Music > Dubstep'),
    (r'\bhardstyle\b', 'Music > Electronic > Hard Music > Hardstyle'),
    (r'\bhardcore\b', 'Music > Electronic > Hard Music > Hardcore'),
    (r'\bgabber\b', 'Music > Electronic > Hard Music > Gabber'),
    (r'\bambient\b', 'Music > Electronic > Chill / Ambient > Ambient'),
    (r'\bdowntempo\b', 'Music > Electronic > Chill / Ambient > Downtempo'),
    (r'\btechno\b', 'Music > Electronic > Techno'),
    (r'\bhouse\b', 'Music > Electronic > House'),
    (r'\btrance\b', 'Music > Electronic > Trance'),
    (r'\bdrum.(?:and|&|n).bass\b', 'Music > Electronic > Drum & Bass'),
]

def genres(txt):
    if not txt: return ['Music > Electronic']
    t = txt.lower()
    f = []
    for p, c in GP:
        if re.search(p, t): f.append(c)
    r = [c for c in f if not any(o != c and o.startswith(c+' > ') for o in f)]
    return list(dict.fromkeys(r))[:3] or ['Music > Electronic']

def mkdesc(p):
    tw = p.get('nameTown',''); co = p.get('nameCountry','')
    ty = {'Club':'Soiree club','Indoor':'Soiree indoor','Open Air':'Open air','Festival':'Festival'}.get(p.get('nameType',''),'Evenement')
    parts = [f"{ty} musique electronique, {tw} ({co})."]
    o = p.get('nameOrganizer','')
    if o: parts.append(f"Par {o}.")
    lu = p.get('textLineUp','')
    if lu:
        ar = []
        for l in lu.split('\n'):
            l = l.strip()
            if not l: continue
            m = re.match(r'[\d:]+\s*-\s*[\d:]+\s+(.+?)(?:\s*-\s*(.+))?$', l)
            if m and m.group(1): ar.append(m.group(1).strip())
        if ar: parts.append(f"Line-up: {', '.join(ar[:5])}{'...' if len(ar)>5 else ''}.")
    return ' '.join(parts)

# Load done IDs
done_ids = set()
if os.path.exists(DONE):
    done_ids = set(json.load(open(DONE, 'r')))

# Load list
parties = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'goabase_list.json'), 'r', encoding='utf-8'))

# Find next event to process
next_p = None
for p in parties:
    if str(p['id']) not in done_ids:
        next_p = p
        break

if not next_p:
    print(f"ALL DONE ({len(done_ids)}/{len(parties)})")
    
    # Now insert all saved events
    events = json.load(open(SAVE, 'r', encoding='utf-8')) if os.path.exists(SAVE) else []
    if events:
        print(f"Inserting {len(events)} events...")
        ok = 0
        for i in range(0, len(events), 20):
            b = events[i:i+20]
            try:
                r = requests.post(f'{MAPEVENT}/events/scraped/batch', json={'events':b}, timeout=30)
                if r.status_code in [200,201]:
                    n = r.json().get('inserted', r.json().get('count', len(b)))
                    ok += n
                    print(f"  +{n} (total:{ok})")
                else:
                    print(f"  ERR {r.status_code}")
            except Exception as e:
                print(f"  ERR: {e}")
            time.sleep(1)
        print(f"Inserted: {ok}")
    sys.exit(0)

pid = next_p['id']
nm = next_p.get('nameParty','')[:40]
tw = next_p.get('nameTown','')
print(f"[{len(done_ids)+1}/{len(parties)}] Fetching {pid}: {nm} ({tw})...", end=' ', flush=True)

try:
    r = requests.get(f'{GOABASE}/{pid}', headers=HDR, timeout=20)
    if r.status_code != 200:
        print(f"HTTP {r.status_code}")
        done_ids.add(str(pid))
        json.dump(sorted(done_ids), open(DONE, 'w'))
        sys.exit(0)
    
    dt = r.json().get('party', {})
    txt = f"{dt.get('nameParty','')}\n{dt.get('textLineUp','')}\n{dt.get('textMore','')}"
    cats = genres(txt)
    
    ds = dt.get('dateStart','')
    de = dt.get('dateEnd','')
    date = tm = ed = et = None
    if ds:
        d2 = datetime.fromisoformat(ds); date = d2.strftime('%Y-%m-%d'); tm = d2.strftime('%H:%M')
    if de:
        d3 = datetime.fromisoformat(de); ed = d3.strftime('%Y-%m-%d'); et = d3.strftime('%H:%M')
    
    loc = f"{tw}, {dt.get('nameCountry','')}" if tw else dt.get('nameCountry','')
    src = dt.get('urlParty','') or f"https://www.goabase.net/party/{pid}"
    
    if not date or not dt.get('geoLat'):
        print(f"SKIP (no date/geo)")
        done_ids.add(str(pid))
        json.dump(sorted(done_ids), open(DONE, 'w'))
        sys.exit(0)
    
    ev = {
        'title': dt.get('nameParty',''),
        'description': mkdesc(dt),
        'date': date, 'time': tm, 'end_date': ed, 'end_time': et,
        'location': loc,
        'latitude': float(dt.get('geoLat', 0)),
        'longitude': float(dt.get('geoLon', 0)),
        'categories': cats,
        'source_url': src,
        'validation_status': 'auto_validated',
    }
    
    # Load existing, append, save
    events = json.load(open(SAVE, 'r', encoding='utf-8')) if os.path.exists(SAVE) else []
    events.append(ev)
    json.dump(events, open(SAVE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    
    cs = ','.join(c.split('>')[-1].strip() for c in cats)
    print(f"OK -> {cs} (total: {len(events)})")

except Exception as e:
    print(f"ERR: {str(e)[:60]}")

done_ids.add(str(pid))
json.dump(sorted(done_ids), open(DONE, 'w'))
