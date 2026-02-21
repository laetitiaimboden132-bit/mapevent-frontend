"""
Fetch electronic music events from:
1. Resident Advisor (RA) GraphQL API - Swiss + French cities
2. Paris OpenData (corrected query)
"""
import requests, json, time, sys, re
sys.stdout.reconfigure(line_buffering=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
TODAY = "2026-02-12"

all_events = []

# ==========================================================================
# 1. RA - Find area IDs for Switzerland and France
# ==========================================================================
print("=" * 70)
print("1. RESIDENT ADVISOR - Exploration")
print("=" * 70)

# Try to find area IDs
# Known area IDs: 41 = Madrid, let's try common ones
# First, let me try the areas query
try:
    r = requests.post("https://ra.co/graphql", json={
        "query": """
        {
            areas(first: 200) {
                id
                name
                country {
                    name
                    urlName
                }
                urlName
            }
        }
        """
    }, headers={**HEADERS, "Content-Type": "application/json", "Referer": "https://ra.co/"}, timeout=15)
    print(f"  Areas query: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        areas = data.get("data", {}).get("areas", [])
        if areas:
            print(f"  Total areas: {len(areas)}")
            # Filter CH + FR
            ch_fr = [a for a in areas if a.get("country", {}).get("urlName", "") in ("switzerland", "france")]
            for a in ch_fr[:30]:
                print(f"    ID={a['id']}: {a.get('name', '')} ({a.get('country', {}).get('name', '')})")
        else:
            print(f"  Response: {json.dumps(data, indent=2, ensure_ascii=False)[:400]}")
except Exception as e:
    print(f"  Error: {e}")


# Try alternative: search for events by country/area name  
print("\n--- Trying direct event search ---")

# Try known area IDs and see what cities they correspond to
test_areas = list(range(1, 100))
ch_areas = []
fr_areas = []

for batch_start in range(0, len(test_areas), 10):
    batch = test_areas[batch_start:batch_start+10]
    for area_id in batch:
        try:
            r = requests.post("https://ra.co/graphql", json={
                "query": f"""
                {{
                    eventListings(
                        filters: {{
                            areas: {{eq: {area_id}}}
                            listingDate: {{gte: "2026-02-12"}}
                        }}
                        pageSize: 1
                    ) {{
                        totalResults
                        data {{
                            event {{
                                title
                                venue {{
                                    name
                                    area {{ id name }}
                                }}
                            }}
                        }}
                    }}
                }}
                """
            }, headers={**HEADERS, "Content-Type": "application/json", "Referer": "https://ra.co/"}, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                listings = data.get("data", {}).get("eventListings", {})
                total = listings.get("totalResults", 0)
                events = listings.get("data", [])
                if events and total > 0:
                    evt = events[0].get("event", {})
                    venue = evt.get("venue", {})
                    area = venue.get("area", {})
                    area_name = area.get("name", "?")
                    if "zurich" in area_name.lower() or "geneva" in area_name.lower() or \
                       "bern" in area_name.lower() or "basel" in area_name.lower() or \
                       "lausanne" in area_name.lower() or "switzerland" in area_name.lower():
                        ch_areas.append({"id": area_id, "name": area_name, "total": total})
                        print(f"  CH Area {area_id}: {area_name} ({total} events)")
                    elif "paris" in area_name.lower() or "lyon" in area_name.lower() or \
                         "marseille" in area_name.lower() or "bordeaux" in area_name.lower() or \
                         "france" in area_name.lower() or "nantes" in area_name.lower() or \
                         "strasbourg" in area_name.lower() or "grenoble" in area_name.lower():
                        fr_areas.append({"id": area_id, "name": area_name, "total": total})
                        print(f"  FR Area {area_id}: {area_name} ({total} events)")
        except:
            pass
    time.sleep(0.5)

print(f"\n  CH areas found: {len(ch_areas)}")
print(f"  FR areas found: {len(fr_areas)}")


# ==========================================================================
# 2. RA - Fetch events from discovered areas
# ==========================================================================
print("\n" + "=" * 70)
print("2. RESIDENT ADVISOR - Fetch events")
print("=" * 70)

target_areas = ch_areas + fr_areas

for area in target_areas:
    area_id = area["id"]
    area_name = area["name"]
    print(f"\n  --- {area_name} (ID={area_id}) ---")
    
    try:
        r = requests.post("https://ra.co/graphql", json={
            "query": f"""
            {{
                eventListings(
                    filters: {{
                        areas: {{eq: {area_id}}}
                        listingDate: {{gte: "2026-02-12", lte: "2026-12-31"}}
                    }}
                    pageSize: 30
                ) {{
                    totalResults
                    data {{
                        event {{
                            id
                            title
                            date
                            startTime
                            endTime
                            contentUrl
                            venue {{
                                name
                                address
                                area {{ name }}
                                location {{
                                    latitude
                                    longitude
                                }}
                            }}
                            artists {{
                                name
                            }}
                        }}
                    }}
                }}
            }}
            """
        }, headers={**HEADERS, "Content-Type": "application/json", "Referer": "https://ra.co/"}, timeout=15)
        
        if r.status_code == 200:
            data = r.json()
            listings = data.get("data", {}).get("eventListings", {})
            total = listings.get("totalResults", 0)
            events = listings.get("data", [])
            print(f"    Total: {total}, Recus: {len(events)}")
            
            for item in events:
                evt = item.get("event", {})
                title = evt.get("title", "")
                event_date = evt.get("date", "")[:10]
                start_time = evt.get("startTime", "")
                venue = evt.get("venue", {})
                venue_name = venue.get("name", "")
                venue_addr = venue.get("address", "")
                loc = venue.get("location", {})
                lat = loc.get("latitude") if loc else None
                lon = loc.get("longitude") if loc else None
                artists = [a.get("name", "") for a in evt.get("artists", [])]
                content_url = evt.get("contentUrl", "")
                
                source_url = f"https://ra.co{content_url}" if content_url else ""
                
                all_events.append({
                    "_source": "ra",
                    "title": title,
                    "date": event_date,
                    "time": start_time[:5] if start_time else None,
                    "location": f"{venue_name}, {venue_addr}".strip(", ") if venue_addr else venue_name,
                    "latitude": float(lat) if lat else None,
                    "longitude": float(lon) if lon else None,
                    "source_url": source_url,
                    "area": area_name,
                    "artists": artists,
                })
                print(f"      {title[:45]} | {event_date} | {venue_name[:25]} | artists: {', '.join(artists[:3])}")
        else:
            print(f"    Error: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"    Error: {e}")
    time.sleep(1)


# ==========================================================================
# 3. PARIS OPENDATA - Corrected query
# ==========================================================================
print("\n" + "=" * 70)
print("3. PARIS OPENDATA")
print("=" * 70)

try:
    # First check available fields
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records"
    r = requests.get(url, params={"limit": 1}, headers=HEADERS, timeout=15)
    if r.status_code == 200:
        data = r.json()
        results = data.get("results", [])
        if results:
            fields = list(results[0].keys())
            print(f"  Champs disponibles: {fields}")
            # Print sample
            print(f"  Sample: {json.dumps(results[0], indent=2, ensure_ascii=False)[:600]}")
except Exception as e:
    print(f"  Error: {e}")

# Search for electro events with correct fields
try:
    # Try searching in title and description
    for search_term in ["electro", "techno", "house music", "dj set", "rave", "clubbing"]:
        params = {
            "where": f"title like '%{search_term}%' OR lead_text like '%{search_term}%'",
            "limit": 20,
        }
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            total = data.get("total_count", 0)
            if total > 0:
                print(f"\n  '{search_term}': {total} events")
                for evt in data.get("results", [])[:3]:
                    title = evt.get("title", "")
                    date_start = evt.get("date_start", "")
                    addr = evt.get("address_name", "")
                    print(f"    {title[:55]} | {date_start[:10]} | {addr[:35]}")
        time.sleep(0.5)
except Exception as e:
    print(f"  Error: {e}")


# ==========================================================================
# RESULTAT
# ==========================================================================
print("\n" + "=" * 70)
print("RESULTAT")
print("=" * 70)

sources = {}
for e in all_events:
    src = e.get("_source", "?")
    sources[src] = sources.get(src, 0) + 1

print(f"Total events: {len(all_events)}")
for src, cnt in sorted(sources.items(), key=lambda x: -x[1]):
    print(f"  {src}: {cnt}")

# Save
with open("scraper/ra_paris_electro.json", "w", encoding="utf-8") as f:
    json.dump(all_events, f, ensure_ascii=False, indent=2)

print(f"\nSauvegarde: scraper/ra_paris_electro.json")
