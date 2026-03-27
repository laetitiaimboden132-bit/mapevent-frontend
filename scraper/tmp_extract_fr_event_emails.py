import json
import re
import requests
import concurrent.futures as cf

cities = {
    'paris','lyon','marseille','toulouse','nice','nantes','strasbourg','montpellier','bordeaux','lille','rennes','reims','toulon','grenoble','dijon','angers','nimes','villeurbanne','saint-etienne','le havre','perpignan','metz','caen','orleans','mulhouse'
}
pat = re.compile(r"(?i)\b[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}\b")
ban_tlds = {'png','jpg','jpeg','webp','gif','svg','css','js','ico','map'}

with open(r"c:\MapEventAI_NEW\backend\data\events_status.json", encoding="utf-8") as f:
    data = json.load(f)

fr_urls = []
for it in data:
    c = (it.get("city") or "").lower()
    a = (it.get("address") or "").lower()
    u = (it.get("sourceUrl") or "").strip()
    if not u:
        continue
    if ("france" in a) or any(x in c for x in cities):
        fr_urls.append(u)

fr_urls = list(dict.fromkeys(fr_urls))[:800]


def one(u: str):
    try:
        r = requests.get(u, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return []
        out = []
        for e in pat.findall(r.text):
            e = e.lower().strip(".,;:()[]<>'\"")
            tld = e.rsplit('.', 1)[-1] if '.' in e else ''
            if tld in ban_tlds:
                continue
            out.append(e)
        return out
    except Exception:
        return []

emails = set()
with cf.ThreadPoolExecutor(max_workers=40) as ex:
    for arr in ex.map(one, fr_urls):
        for e in arr:
            emails.add(e)

print("urls_tested", len(fr_urls), "emails", len(emails))
for e in sorted(emails)[:120]:
    print(e)
