import boto3

s3 = boto3.client("s3", region_name="eu-west-1")
cf = boto3.client("cloudfront", region_name="eu-west-1")

BUCKET = "mapevent-frontend-laetibibi"
TO_DELETE = [
    "sion", "martigny", "monthey", "montreux", "vevey", "bulle",
    "zurich", "winterthur", "schaffhausen", "luzern", "zug",
    "berne", "thun", "aarau", "solothurn", "davos", "interlaken",
]

paths = []
for city in TO_DELETE:
    key = f"widget-data/{city}.json"
    try:
        s3.delete_object(Bucket=BUCKET, Key=key)
        print(f"  [OK] Supprimé s3://{BUCKET}/{key}")
        paths.append(f"/{key}")
    except Exception as e:
        print(f"  [ERR] {key}: {e}")

if paths:
    import time
    cf.create_invalidation(
        DistributionId="EMB53HDL7VFIJ",
        InvalidationBatch={
            "Paths": {"Quantity": len(paths), "Items": paths},
            "CallerReference": f"cleanup-{time.time()}",
        },
    )
    print(f"\nCache invalidé pour {len(paths)} fichiers.")

print(f"\nTerminé: {len(TO_DELETE)} villes nettoyées.")
