import json
import re
import requests
import concurrent.futures as cf
from email_registry import was_already_sent

cities = {'paris','lyon','marseille','toulouse','nice','nantes','strasbourg','montpellier','bordeaux','lille','rennes','reims','toulon','grenoble','dijon','angers','nimes','villeurbanne','saint-etienne','le havre','perpignan','metz','caen','orleans','mulhouse','amiens','limoges','tourcoing','avignon','poitiers'}
pat = re.compile(r"(?i)\b[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}\b")
ban_tlds = {'png','jpg','jpeg','webp','gif','svg','css','js','ico','map','pdf','mp4'}
ban_domains_contains = ('facebook.com','instagram.com','tiktok.com','youtube.com','linkedin.com')

def clean_email(e: str) -> str:
    e = e.lower().strip(".,;:()[]<>'\"")
    for bad_prefix in ('u003e', 'mailto:'):
        if e.startswith(bad_prefix):
            e = e[len(bad_prefix):]
    for bad in ('www.',):
        if e.startswith(bad):
            e = e[len(bad):]
    return e

with open(r"c:\MapEventAI_NEW\backend\data\events_status.json", encoding="utf-8") as f:
    data = json.load(f)

fr_urls=[]
for it in data:
    c=(it.get('city') or '').lower(); a=(it.get('address') or '').lower(); u=(it.get('sourceUrl') or '').strip()
    if not u: continue
    if ('france' in a) or any(x in c for x in cities):
        fr_urls.append(u)
fr_urls=list(dict.fromkeys(fr_urls))[:2000]


def one(u):
    try:
        r=requests.get(u, timeout=8, headers={'User-Agent':'Mozilla/5.0'})
        if r.status_code!=200: return []
        out=[]
        for e in pat.findall(r.text):
            e=clean_email(e)
            if '@' not in e: continue
            dom=e.split('@',1)[1]
            tld=dom.rsplit('.',1)[-1] if '.' in dom else ''
            if tld in ban_tlds: continue
            if any(b in dom for b in ban_domains_contains): continue
            if was_already_sent(e): continue
            out.append((e,u,dom))
        return out
    except Exception:
        return []

rows=[]; seen=set()
with cf.ThreadPoolExecutor(max_workers=45) as ex:
    for arr in ex.map(one, fr_urls):
        for e,u,dom in arr:
            if e in seen: continue
            seen.add(e)
            rows.append({'email':e,'source_url':u,'host':dom})

rows.sort(key=lambda r:(0 if r['host'].endswith('.fr') else 1, r['host'], r['email']))
out=r"c:\MapEventAI_NEW\frontend\scraper\prospects_france_from_source_urls_wide.json"
with open(out,'w',encoding='utf-8') as f: json.dump(rows,f,ensure_ascii=False,indent=2)
print('urls_scanned', len(fr_urls))
print('new_emails_any_domain', len(rows))
print('out', out)
