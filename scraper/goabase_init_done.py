# -*- coding: utf-8 -*-
"""Initialize done_ids from already saved events + goabase_list"""
import json, os, re

SAVE = os.path.join(os.path.dirname(__file__), '..', 'goabase_events_to_add.json')
DONE = os.path.join(os.path.dirname(__file__), '..', 'goabase_done_ids.json')
LIST = os.path.join(os.path.dirname(__file__), '..', 'goabase_list.json')

events = json.load(open(SAVE, 'r', encoding='utf-8'))
parties = json.load(open(LIST, 'r', encoding='utf-8'))

# Map source URLs to party IDs
url_to_id = {}
for p in parties:
    url = (p.get('urlPartyHtml','') or '').lower()
    url_to_id[url] = str(p['id'])
    url_to_id[f"https://www.goabase.net/party/{p['id']}".lower()] = str(p['id'])

done = set()
for e in events:
    su = (e.get('source_url','') or '').lower()
    if su in url_to_id:
        done.add(url_to_id[su])
    else:
        m = re.search(r'/party/(\d+)', su)
        if m: done.add(m.group(1))

json.dump(sorted(done), open(DONE, 'w'))
print(f"Initialized {len(done)} done IDs from {len(events)} saved events")
