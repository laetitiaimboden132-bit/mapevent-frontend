"""Re-import Toronto with truly unique source_urls (id+date)."""
import requests, json, time, re, hashlib
from datetime import datetime, date

API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}
TODAY = date.today().strftime("%Y-%m-%d")

TORONTO_NEIGHBORHOODS = {
    "Toronto": (43.6532, -79.3832), "North York": (43.7615, -79.4111),
    "Scarborough": (43.7731, -79.2574), "Etobicoke": (43.6205, -79.5132),
    "East York": (43.6911, -79.3280), "York": (43.6897, -79.4908),
    "Downtown": (43.6510, -79.3470),
}


def categorize(title, desc=""):
    cats = []
    c = f"{title} {desc}".lower()
    if any(w in c for w in ["concert", "music"]): cats.append("Musique > Concert")
    if any(w in c for w in ["theater", "theatre"]): cats.append("Spectacle > Théâtre")
    if any(w in c for w in ["dance"]): cats.append("Danse")
    if any(w in c for w in ["arts", "exhibit"]): cats.append("Culture > Exposition")
    if any(w in c for w in ["film", "cinema", "movie"]): cats.append("Culture > Cinéma")
    if any(w in c for w in ["sport", "skating", "hockey", "swimming"]): cats.append("Sport")
    if "festival" in c: cats.append("Festival")
    if any(w in c for w in ["market", "farmers"]): cats.append("Marché & Brocante")
    if any(w in c for w in ["family", "children", "kids"]): cats.append("Famille & Enfants")
    if any(w in c for w in ["community"]): cats.append("Événement")
    if "tourism" in c: cats.append("Tourisme")
    if not cats: cats.append("Événement")
    return list(dict.fromkeys(cats))[:3]


def send_all(events, name):
    total = 0
    for i in range(0, len(events), 10):
        batch = events[i:i+10]
        try:
            r = requests.post(f"{API_BASE}/events/scraped/batch", json={"events": batch}, headers=HEADERS, timeout=60)
            if r.status_code in (200, 201):
                resp = r.json()
                created = resp.get("results", {}).get("created", 0)
                skipped = resp.get("results", {}).get("skipped", 0)
                total += created
                if i == 0:
                    print(f"  First batch: created={created}, skipped={skipped}")
        except: pass
        if i + 10 < len(events): time.sleep(0.5)
    return total


print("🇨🇦 TORONTO - Re-import with unique URLs")
r = requests.get(
    "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/9201059e-43ed-4369-885e-0b867652feac/resource/8900fdb2-7f6c-4f50-8581-b463311ff05d/download/file.json",
    headers=HEADERS, timeout=30)
data = r.json().get("value", [])
print(f"Raw items: {len(data)}")

events = []
seen_urls = set()

for item in data:
    title = item.get("calendar_name") or ""
    if not title: continue
    
    cal_date = item.get("calendar_date", "")[:10]
    if not cal_date or cal_date < TODAY: continue
    
    cal_id = item.get("calendar_id", "")
    
    # Generate truly unique URL using calendar_id + date
    source_url = f"https://www.toronto.ca/explore-enjoy/festivals-events/?id={cal_id}&date={cal_date}"
    
    # Skip if we've already seen this URL
    if source_url in seen_urls: continue
    seen_urls.add(source_url)
    
    # Location
    location_str = "Toronto, ON, Canada"
    lat, lon = 43.6532, -79.3832
    
    event_dates = item.get("event_dates", [])
    if event_dates:
        for ed in event_dates:
            locs = ed.get("locations", [])
            if locs:
                location_str = locs[0]
                for hood, coords in TORONTO_NEIGHBORHOODS.items():
                    if hood.lower() in location_str.lower():
                        lat, lon = coords
                        break
                h = int(hashlib.md5(location_str.encode()).hexdigest()[:8], 16)
                lat += ((h % 200) - 100) / 8000.0
                lon += ((h // 200 % 200) - 100) / 8000.0
                break
    
    categories_raw = item.get("event_category", [])
    cat_str = " ".join(categories_raw) if isinstance(categories_raw, list) else ""
    
    desc = f"Event in Toronto. {cat_str}."
    cost = item.get("cost_notes") or ""
    if "free" in str(cost).lower(): desc += " Free admission."
    
    events.append({
        "title": title[:200],
        "description": desc[:350],
        "date": cal_date,
        "end_date": None,
        "time": None,
        "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "categories": categorize(title, cat_str),
        "source_url": source_url,
        "source": "Toronto Open Data",
        "validation_status": "auto_validated"
    })

print(f"Unique events: {len(events)}")
n = send_all(events, "Toronto")
print(f"\n✅ Toronto: {n} events created")
