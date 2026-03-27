import urllib.request, json, gzip, ssl, time
from collections import defaultdict

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
ADMIN_KEY = "mapevent-admin-2026-cleanup"
ctx = ssl.create_default_context()

print("=== SUPPRESSION DES DOUBLONS ===")
print("[1/3] Chargement des events...")
req = urllib.request.Request(f"{API}/api/events?limit=60000", headers={"Accept-Encoding": "gzip"})
resp = urllib.request.urlopen(req, context=ctx)
raw = resp.read()
try:
    content = gzip.decompress(raw).decode("utf-8")
except:
    content = raw.decode("utf-8")
data = json.loads(content)
events = [dict(zip(data["k"], item)) for item in data["d"]]
print(f"  Total events: {len(events)}")

print("[2/3] Recherche des doublons...")
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

print(f"  Doublons a supprimer: {len(ids_to_delete)}")
if not ids_to_delete:
    print("Aucun doublon!")
    exit(0)

print("[3/3] Suppression via endpoint admin...")
batch_size = 150
deleted_total = 0
failed_total = 0

for i in range(0, len(ids_to_delete), batch_size):
    batch = ids_to_delete[i:i+batch_size]
    body = json.dumps({"admin_key": ADMIN_KEY, "ids": batch}).encode("utf-8")
    req = urllib.request.Request(
        f"{API}/api/admin/delete-duplicates",
        data=body, method="POST",
        headers={"Content-Type": "application/json"}
    )
    try:
        resp = urllib.request.urlopen(req, context=ctx, timeout=30)
        result = json.loads(resp.read().decode("utf-8"))
        deleted = result.get("deleted", 0)
        deleted_total += deleted
        batch_num = i // batch_size + 1
        total_batches = (len(ids_to_delete) + batch_size - 1) // batch_size
        print(f"  Batch {batch_num}/{total_batches}: {deleted} supprimes (total: {deleted_total}/{len(ids_to_delete)})")
    except Exception as e:
        failed_total += len(batch)
        print(f"  ERREUR batch {i//batch_size+1}: {e}")
    time.sleep(0.3)

print(f"\nTermine! Supprimes: {deleted_total}, Echecs: {failed_total}")
