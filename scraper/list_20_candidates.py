# -*- coding: utf-8 -*-
"""Liste 20 organisateurs individuels jamais contactes"""
import sys, os, requests

try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except: pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from email_registry import was_already_sent, get_sent_count

MAPEVENT = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api'

print(f"Registre: {get_sent_count()} emails deja envoyes\n")

all_events = []
for ch in [
    {'south': 44, 'north': 52, 'west': -6, 'east': 11},
    {'south': 44, 'north': 55, 'west': 5, 'east': 20},
    {'south': 35, 'north': 50, 'west': -10, 'east': 5},
    {'south': 40, 'north': 52, 'west': -130, 'east': -60},
]:
    try:
        r = requests.get(f'{MAPEVENT}/events/viewport', params={**ch, 'zoom': 10}, timeout=30)
        d = r.json()
        if d.get('type') == 'events' and d.get('d'):
            k = d['k']
            for row in d['d']:
                all_events.append(dict(zip(k, row)))
    except: pass

print(f"{len(all_events)} events\n")

seen = set()
candidates = []
for ev in all_events:
    email = (ev.get('organizer_email') or '').strip().lower()
    if not email or '@' not in email: continue
    if email in seen: continue
    if was_already_sent(email): continue
    if 'mapevent' in email: continue
    title = ev.get('title', '')
    source = ev.get('source_url', '')
    if not title or not source: continue
    seen.add(email)
    candidates.append({
        'email': email,
        'title': title,
        'location': ev.get('location', ''),
        'date': str(ev.get('date', ''))[:10],
    })

print(f"{len(candidates)} organisateurs jamais contactes:\n")
for i, c in enumerate(candidates[:30], 1):
    print(f"  {i:2d}. {c['email']:45s} | {c['title'][:40]} | {c['location'][:25]} | {c['date']}")
