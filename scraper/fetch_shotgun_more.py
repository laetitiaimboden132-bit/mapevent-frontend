"""
Explore Shotgun.live and other platforms for electronic music events.
Check JSON-LD / embedded data for events in CH + FR.
"""
import requests, json, time, sys, re
sys.stdout.reconfigure(line_buffering=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
TODAY = "2026-02-12"

# ==========================================================================
# 1. Shotgun.live - JSON-LD from city pages
# ==========================================================================
print("=" * 70)
print("1. SHOTGUN.LIVE")
print("=" * 70)

shotgun_cities = [
    "geneva", "zurich", "lausanne", "lyon", "paris", 
    "marseille", "bordeaux", "nantes", "grenoble",
]

for city in shotgun_cities:
    url = f"https://shotgun.live/en/cities/{city}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            # Check for JSON-LD
            lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', r.text, re.DOTALL)
            # Check for __NEXT_DATA__ or similar
            next_data = re.findall(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text, re.DOTALL)
            # Check for inline JSON data
            json_patterns = re.findall(r'window\.__(?:DATA|STATE|INITIAL)__\s*=\s*({.*?});', r.text, re.DOTALL)
            
            events_found = 0
            if lds:
                print(f"  {city}: {len(lds)} JSON-LD blocks")
                for ld in lds[:2]:
                    try:
                        d = json.loads(ld)
                        print(f"    Type: {d.get('@type', '?')}, Name: {d.get('name', '')[:50]}")
                    except: pass
            if next_data:
                print(f"  {city}: Found __NEXT_DATA__ ({len(next_data[0])} chars)")
                try:
                    nd = json.loads(next_data[0])
                    # Look for event data in the structure
                    props = nd.get("props", {}).get("pageProps", {})
                    if props:
                        keys = list(props.keys())[:10]
                        print(f"    pageProps keys: {keys}")
                        events = props.get("events", props.get("items", props.get("initialEvents", [])))
                        if events:
                            print(f"    Events: {len(events)}")
                            if events:
                                print(f"    Sample: {json.dumps(events[0], indent=2, ensure_ascii=False)[:300]}")
                except: pass
            if json_patterns:
                print(f"  {city}: Found window.__DATA__ ({len(json_patterns[0])} chars)")
                
            if not lds and not next_data and not json_patterns:
                # Check if it's a SPA
                has_react = "react" in r.text.lower() or "__next" in r.text.lower()
                has_events = "event" in r.text.lower()
                link_count = len(re.findall(r'href="[^"]*event[^"]*"', r.text))
                print(f"  {city}: {r.status_code} | SPA={has_react} | events_mention={has_events} | event_links={link_count}")
        elif r.status_code == 429:
            print(f"  {city}: Rate limited (429)")
            break
        else:
            print(f"  {city}: {r.status_code}")
    except Exception as e:
        print(f"  {city}: {e}")
    time.sleep(3)


# ==========================================================================
# 2. Shotgun.live - Individual event pages
# ==========================================================================
print("\n" + "=" * 70)
print("2. SHOTGUN.LIVE - Event pages (Geneva)")
print("=" * 70)

try:
    r = requests.get("https://shotgun.live/en/cities/geneva", headers=HEADERS, timeout=15)
    if r.status_code == 200:
        # Find event links
        links = re.findall(r'href="(/en/events/[^"]+)"', r.text)
        links = list(dict.fromkeys(links))
        print(f"  Event links on Geneva page: {len(links)}")
        
        for link in links[:5]:
            url = f"https://shotgun.live{link}"
            try:
                r2 = requests.get(url, headers=HEADERS, timeout=10)
                if r2.status_code == 200:
                    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', r2.text, re.DOTALL)
                    if lds:
                        for ld in lds:
                            try:
                                d = json.loads(ld)
                                if d.get("@type") == "Event" or (isinstance(d, list) and any(x.get("@type") == "Event" for x in d)):
                                    print(f"    Event found: {json.dumps(d, indent=2, ensure_ascii=False)[:400]}")
                            except: pass
                    else:
                        nd = re.findall(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r2.text, re.DOTALL)
                        if nd:
                            data = json.loads(nd[0])
                            pp = data.get("props", {}).get("pageProps", {})
                            print(f"    {link[:50]}: pageProps keys = {list(pp.keys())[:8]}")
                            # Try to find event data
                            event = pp.get("event", pp.get("data", {}))
                            if event:
                                print(f"    Event data: {json.dumps(event, indent=2, ensure_ascii=False)[:400]}")
                elif r2.status_code == 429:
                    print(f"    Rate limited!")
                    break
            except Exception as e:
                print(f"    {link[:50]}: {e}")
            time.sleep(3)
except Exception as e:
    print(f"  Error: {e}")


# ==========================================================================
# 3. What's Good In (Swiss events)
# ==========================================================================
print("\n" + "=" * 70)
print("3. WHATSGOODIN.CH")
print("=" * 70)

try:
    r = requests.get("https://whatsgoodin.ch/en/events?category=techno", headers=HEADERS, timeout=15)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', r.text, re.DOTALL)
        next_data = re.findall(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text, re.DOTALL)
        links = re.findall(r'href="(/en/events/[^"]+)"', r.text)
        print(f"  JSON-LD: {len(lds)}, __NEXT_DATA__: {len(next_data)}, event links: {len(links)}")
        if next_data:
            nd = json.loads(next_data[0])
            pp = nd.get("props", {}).get("pageProps", {})
            print(f"  pageProps keys: {list(pp.keys())[:10]}")
except Exception as e:
    print(f"  Error: {e}")

# Also try wasgoht.ch (German version)
try:
    r = requests.get("https://wasgoht.ch/en/events?category=techno", headers=HEADERS, timeout=15)
    print(f"  wasgoht.ch: {r.status_code}")
    if r.status_code == 200:
        links = re.findall(r'href="[^"]*event[^"]*"', r.text, re.I)
        print(f"  Event links: {len(links)}")
except Exception as e:
    print(f"  wasgoht.ch: {e}")


# ==========================================================================
# 4. Inclusound (electro app France)
# ==========================================================================
print("\n" + "=" * 70)
print("4. INCLUSOUND")
print("=" * 70)

try:
    r = requests.get("https://inclusound.com/", headers=HEADERS, timeout=15)
    if r.status_code == 200:
        # Check for API calls in source
        api_patterns = re.findall(r'(?:api|endpoint|fetch|axios)[^"]*"(https?://[^"]+)"', r.text, re.I)
        next_data = re.findall(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', r.text, re.DOTALL)
        print(f"  API patterns: {api_patterns[:5]}")
        print(f"  __NEXT_DATA__: {len(next_data)}")
except Exception as e:
    print(f"  Error: {e}")


# ==========================================================================
# 5. Residentadvisor - check for accessible data
# ==========================================================================
print("\n" + "=" * 70)
print("5. RESIDENT ADVISOR")
print("=" * 70)

# RA uses GraphQL - let's try their known endpoint
try:
    r = requests.post("https://ra.co/graphql", json={
        "query": """
        {
            eventListings(
                filters: {
                    areas: {eq: 41}
                    listingDate: {gte: "2026-02-12"}
                }
                pageSize: 5
            ) {
                data {
                    event {
                        title
                        date
                        venue {
                            name
                            area { name }
                        }
                    }
                }
            }
        }
        """
    }, headers={**HEADERS, "Content-Type": "application/json", "Referer": "https://ra.co/"}, timeout=15)
    print(f"  RA GraphQL: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  Response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
    else:
        print(f"  Response: {r.text[:300]}")
except Exception as e:
    print(f"  Error: {e}")

# Try RA event listing page for JSON-LD
try:
    r = requests.get("https://ra.co/events/ch/all", headers=HEADERS, timeout=15)
    print(f"\n  RA events page CH: {r.status_code}")
    if r.status_code == 200:
        lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', r.text, re.DOTALL)
        print(f"  JSON-LD blocks: {len(lds)}")
        for ld in lds[:2]:
            try:
                d = json.loads(ld)
                t = d.get("@type", "?")
                print(f"    Type: {t}")
                if isinstance(d, list):
                    print(f"    List of {len(d)}")
                    for item in d[:3]:
                        print(f"      {item.get('@type', '?')}: {item.get('name', '')[:50]}")
            except: pass
except Exception as e:
    print(f"  Error: {e}")


# ==========================================================================
# 6. Opendata soirees electro Paris (events.paris.fr specific)
# ==========================================================================
print("\n" + "=" * 70)
print("6. PARIS OPENDATA - Events electro")
print("=" * 70)

try:
    # Paris has an open data portal with events
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records"
    params = {
        "where": "tags like '%electro%' OR tags like '%techno%' OR tags like '%house%' OR tags like '%dj%' OR title like '%techno%' OR title like '%electro%' OR title like '%rave%'",
        "limit": 50,
        "offset": 0,
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=15)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        total = data.get("total_count", 0)
        results = data.get("results", [])
        print(f"  Total: {total}, Recus: {len(results)}")
        
        for evt in results[:5]:
            title = evt.get("title", "")
            date_start = evt.get("date_start", "")
            date_end = evt.get("date_end", "")
            tags = evt.get("tags", "")
            address = evt.get("address_name", "") + " " + evt.get("address_street", "")
            print(f"    {title[:50]} | {date_start[:10]} | {address[:40]} | tags: {tags[:40]}")
    else:
        print(f"  Response: {r.text[:200]}")
except Exception as e:
    print(f"  Paris: {e}")

# Also try searching for "soiree" "nuit" "club"
try:
    params2 = {
        "where": "tags like '%club%' OR tags like '%nuit%' OR title like '%nuit%' OR title like '%clubbing%'",
        "limit": 20,
    }
    r2 = requests.get(url, params=params2, headers=HEADERS, timeout=15)
    if r2.status_code == 200:
        data2 = r2.json()
        total2 = data2.get("total_count", 0)
        print(f"\n  Club/Nuit: {total2} events")
        for evt in data2.get("results", [])[:5]:
            title = evt.get("title", "")
            print(f"    {title[:60]}")
except: pass


print("\nDONE!")
