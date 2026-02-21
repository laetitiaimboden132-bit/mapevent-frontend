# -*- coding: utf-8 -*-
"""Insert saved Goabase events into DB + populate email registry"""
import json, sys, os, requests

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except: pass

MAPEVENT = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api'

# === 1. INSERT GOABASE EVENTS ===
print("=== INSERT GOABASE EVENTS ===", flush=True)
with open('goabase_events_to_add.json', 'r', encoding='utf-8') as f:
    events = json.load(f)
print(f"Loaded {len(events)} events", flush=True)

ok = 0
for i in range(0, len(events), 20):
    b = events[i:i+20]
    try:
        r = requests.post(f'{MAPEVENT}/events/scraped/batch', json={'events': b}, timeout=30)
        if r.status_code in [200, 201]:
            n = r.json().get('inserted', r.json().get('count', len(b)))
            ok += n
            print(f"  batch {i//20+1}: +{n} (total:{ok})", flush=True)
        else:
            print(f"  batch {i//20+1}: ERR {r.status_code}: {r.text[:100]}", flush=True)
    except Exception as e:
        print(f"  batch {i//20+1}: ERR: {e}", flush=True)

print(f"\nInserted: {ok} events", flush=True)

# Genre stats
g = {}
for e in events:
    for c in e.get('categories', []):
        g[c] = g.get(c, 0) + 1
print("\nGenre distribution:")
for k, v in sorted(g.items(), key=lambda x: -x[1]):
    print(f"  {v:3d}x {k}", flush=True)

# === 2. POPULATE EMAIL REGISTRY ===
print("\n=== POPULATE EMAIL REGISTRY ===", flush=True)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from email_registry import was_already_sent, mark_as_sent, get_sent_count

before = get_sent_count()
print(f"Registry before: {before} emails", flush=True)

# Add all emails from send_35_promo.py hardcoded list
promo_35 = [
    "info@montreux-riviera.com", "info@fribourgtourisme.ch", "info@neuchateltourisme.ch",
    "info@juratourisme.ch", "info@biel-bienne.ch", "info@interlaken.ch",
    "info@ticino.ch", "info@luzern.com", "info@zuerich.com", "info@basel.com",
    "info@lyon-france.com", "info@bordeaux-tourisme.com", "info@nantes-tourisme.com",
    "info@toulouse-tourisme.com", "info@marseille-tourisme.com", "info@nice-tourisme.com",
    "info@strasbourg.eu", "contact@lilleattractions.com", "info@montpellier-tourisme.fr",
    "info@rennes-tourisme.com", "info@visitberlin.de", "info@visithelsinki.fi",
    "info@esmadrid.com", "info@mtl.org", "info@nycgo.com",
    "contact@openagenda.com", "info@eventbrite.fr", "hello@shotgun.live",
    "contact@mapstr.com", "hello@billetweb.fr", "info@sortiraparis.com",
    "redaction@leprogres.fr", "contact@timeout.fr", "info@infoconcert.com",
    "contact@digitick.com",
]
for e in promo_35:
    if not was_already_sent(e):
        mark_as_sent(e, script="send_35_promo.py", context="promo 35 offices tourisme")

# Add opendata emails
opendata = [
    "opendata@switzerland.com", "opendata@bfs.admin.ch", "info@valais.ch",
    "info@vaud-promotion.ch", "info@lausanne-tourisme.ch",
    "billetterie-culture@geneve.ch", "info@opendata.ch", "contact@openagenda.com",
]
for e in opendata:
    if not was_already_sent(e):
        mark_as_sent(e, script="send_opendata_emails.py", context="demande API opendata")

# Add emails from selected_5_organizers.json
try:
    with open('scraper/selected_5_organizers.json', 'r', encoding='utf-8') as f:
        sel5 = json.load(f)
    for c in sel5:
        em = c.get('email', '')
        if em and not was_already_sent(em):
            mark_as_sent(em, script="send_5_test_emails.py", context=c.get('title', ''))
    print(f"  Added {len(sel5)} from selected_5_organizers.json", flush=True)
except Exception as e:
    print(f"  selected_5: {e}", flush=True)

# Add emails from selected_25_more.json
try:
    with open('scraper/selected_25_more.json', 'r', encoding='utf-8') as f:
        sel25 = json.load(f)
    for c in sel25:
        em = c.get('email', '')
        if em and not was_already_sent(em):
            mark_as_sent(em, script="send_25_more.py", context=c.get('title', ''))
    print(f"  Added {len(sel25)} from selected_25_more.json", flush=True)
except Exception as e:
    print(f"  selected_25: {e}", flush=True)

# Add emails from TOUS_LES_EMAILS.json that have validation_email_sent_at in DB
try:
    # Query DB for all emails that were actually sent
    for ch in [{'south': -90, 'north': 90, 'west': -180, 'east': 0},
               {'south': -90, 'north': 90, 'west': 0, 'east': 180}]:
        r = requests.get(f'{MAPEVENT}/events/viewport', params={**ch, 'zoom': 10}, timeout=30)
        d = r.json()
        if d.get('type') == 'events' and d.get('d'):
            k = d['k']
            ei = k.index('organizer_email') if 'organizer_email' in k else -1
            if ei >= 0:
                for row in d['d']:
                    em = row[ei]
                    if em and '@' in str(em) and not was_already_sent(em):
                        mark_as_sent(em, script="from_db", context="organizer_email in DB")
except Exception as e:
    print(f"  DB scan: {e}", flush=True)

after = get_sent_count()
print(f"Registry after: {after} emails (+{after - before} new)", flush=True)
print("\nDONE", flush=True)
