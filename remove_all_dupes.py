import urllib.request, json, gzip, ssl, time
from collections import defaultdict

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
ADMIN_KEY = "mapevent-admin-2026-cleanup"
ctx = ssl.create_default_context()

total_deleted = 0
pass_num = 0

while True:
    pass_num += 1
    req = urllib.request.Request(f"{API}/api/events?limit=60000", headers={"Accept-Encoding": "gzip"})
    resp = urllib.request.urlopen(req, context=ctx)
    raw = resp.read()
    try: content = gzip.decompress(raw).decode("utf-8")
    except: content = raw.decode("utf-8")
    data = json.loads(content)
    events = [dict(zip(data["k"], item)) for item in data["d"]]

    groups = defaultdict(list)
    for e in events:
        title = (e.get("title") or "").strip().lower()
        lat = round(float(e.get("latitude") or 0), 4)
        lng = round(float(e.get("longitude") or 0), 4)
        date = e.get("date") or ""
        key = f"{title}|{lat}|{lng}|{date}"
        groups[key].append(e)

    ids_to_delete = []
    for key, group in groups.items():
        if len(group) > 1:
            group.sort(key=lambda e: e["id"])
            for e in group[1:]:
                ids_to_delete.append(e["id"])

    if not ids_to_delete:
        print(f"Passe {pass_num}: 0 doublons - TERMINE!")
        print(f"Events restants: {len(events)}")
        break

    print(f"Passe {pass_num}: {len(ids_to_delete)} doublons, {len(events)} events...")
    
    for i in range(0, len(ids_to_delete), 150):
        batch = ids_to_delete[i:i+150]
        body = json.dumps({"admin_key": ADMIN_KEY, "ids": batch}).encode("utf-8")
        req = urllib.request.Request(f"{API}/api/admin/delete-duplicates", data=body, method="POST", headers={"Content-Type": "application/json"})
        try:
            resp = urllib.request.urlopen(req, context=ctx, timeout=30)
            result = json.loads(resp.read().decode("utf-8"))
            total_deleted += result.get("deleted", 0)
        except Exception as e:
            print(f"  Erreur: {e}")
        time.sleep(0.2)
    
    print(f"  -> Total supprime: {total_deleted}")
    time.sleep(1)

print(f"\n=== RESULTAT FINAL ===")
print(f"Total doublons supprimes: {total_deleted}")
