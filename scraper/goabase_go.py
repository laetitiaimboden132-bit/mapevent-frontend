# -*- coding: utf-8 -*-
"""Goabase scraper - robust version with incremental save"""
import requests, json, sys, os, re, time, random, traceback
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8'
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except: pass

GOABASE = 'https://www.goabase.net/api/party/json'
MAPEVENT = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api'
HDR = {'User-Agent': 'MapEventAI-Bot/1.0', 'Accept': 'application/json'}

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

def genres(txt):
    if not txt: return ['Music > Electronic']
    t = txt.lower()
    f = []
    for p, c in GP:
        if re.search(p, t): f.append(c)
    r = [c for c in f if not any(o != c and o.startswith(c+' > ') for o in f)]
    return list(dict.fromkeys(r))[:3] or ['Music > Electronic']

def desc(p):
    tw = p.get('nameTown','')
    co = p.get('nameCountry','')
    ty = {'Club':'Soiree club','Indoor':'Soiree indoor','Open Air':'Open air','Festival':'Festival'}.get(p.get('nameType',''),'Evenement')
    parts = [f"{ty} musique electronique, {tw} ({co})."]
    o = p.get('nameOrganizer','')
    if o: parts.append(f"Par {o}.")
    lu = p.get('textLineUp','')
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
    return ' '.join(parts)

# Load list
with open('goabase_list.json','r',encoding='utf-8') as f:
    parties = json.load(f)
print(f"List: {len(parties)}", flush=True)

# Check existing
ex = set()
for ch in [{'south':-90,'north':90,'west':-180,'east':0},{'south':-90,'north':90,'west':0,'east':180}]:
    try:
        r = requests.get(f'{MAPEVENT}/events/viewport', params={**ch,'zoom':10}, timeout=30)
        d = r.json()
        if d.get('type')=='events' and d.get('d'):
            k = d['k']
            si = k.index('source_url') if 'source_url' in k else -1
            if si>=0:
                for row in d['d']:
                    u = (row[si] or '').lower()
                    if 'goabase' in u: ex.add(u)
    except: pass
print(f"Existing: {len(ex)}", flush=True)

new = [p for p in parties if p.get('urlPartyHtml','').lower() not in ex]
print(f"New: {len(new)}", flush=True)

# Fetch details with incremental save
events = []
SAVE_FILE = 'goabase_events_to_add.json'

for i, p in enumerate(new):
    pid = p['id']
    nm = ''.join(c if ord(c) < 128 else '?' for c in p.get('nameParty','')[:35])
    tw = ''.join(c if ord(c) < 128 else '?' for c in p.get('nameTown',''))
    
    try:
        r = requests.get(f'{GOABASE}/{pid}', headers=HDR, timeout=15)
        if r.status_code != 200:
            print(f"[{i+1}/{len(new)}] {nm} ERR{r.status_code}", flush=True)
            time.sleep(8)
            continue
        dt = r.json().get('party',{})
    except Exception as e:
        print(f"[{i+1}/{len(new)}] {nm} ERR:{e}", flush=True)
        time.sleep(8)
        continue
    
    txt = f"{dt.get('nameParty','')}\n{dt.get('textLineUp','')}\n{dt.get('textMore','')}"
    cats = genres(txt)
    ds = dt.get('dateStart','')
    de = dt.get('dateEnd','')
    date=tm=ed=et=None
    try:
        if ds: d2=datetime.fromisoformat(ds); date=d2.strftime('%Y-%m-%d'); tm=d2.strftime('%H:%M')
        if de: d3=datetime.fromisoformat(de); ed=d3.strftime('%Y-%m-%d'); et=d3.strftime('%H:%M')
    except: pass
    
    loc = f"{tw}, {dt.get('nameCountry','')}" if tw else dt.get('nameCountry','')
    src = dt.get('urlParty','') or f"https://www.goabase.net/party/{pid}"
    
    if not date or not dt.get('geoLat'):
        print(f"[{i+1}/{len(new)}] {nm} SKIP", flush=True)
        time.sleep(8)
        continue
    
    events.append({
        'title': dt.get('nameParty',''),
        'description': desc(dt),
        'date':date,'time':tm,'end_date':ed,'end_time':et,
        'location':loc,
        'latitude':float(dt.get('geoLat',0)),
        'longitude':float(dt.get('geoLon',0)),
        'categories':cats,
        'source_url':src,
        'validation_status':'auto_validated',
    })
    
    cs = ','.join(c.split('>')[-1].strip() for c in cats)
    print(f"[{i+1}/{len(new)}] {nm} ({tw}) -> {cs}", flush=True)
    
    # Save every 10
    if len(events) % 10 == 0:
        with open(SAVE_FILE,'w',encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
    
    time.sleep(8 + random.uniform(0, 3))

# Final save
with open(SAVE_FILE,'w',encoding='utf-8') as f:
    json.dump(events, f, ensure_ascii=False, indent=2)
print(f"\nSaved {len(events)} events", flush=True)

# Insert
print(f"Inserting...", flush=True)
ok = 0
for i in range(0, len(events), 20):
    b = events[i:i+20]
    try:
        r = requests.post(f'{MAPEVENT}/events/scraped/batch', json={'events':b}, timeout=30)
        if r.status_code in [200,201]:
            n = r.json().get('inserted', r.json().get('count', len(b)))
            ok += n
            print(f"  +{n} (total:{ok})", flush=True)
        else:
            print(f"  ERR {r.status_code}: {r.text[:100]}", flush=True)
    except Exception as e:
        print(f"  ERR: {e}", flush=True)
    time.sleep(1)

print(f"\nDONE: {ok} inserted", flush=True)
g = {}
for e in events:
    for c in e['categories']: g[c]=g.get(c,0)+1
for k,v in sorted(g.items(),key=lambda x:-x[1]):
    print(f"  {v:3d}x {k}", flush=True)
