"""
Sync filtered widget-data to S3:
- Upload all remaining JSON files
- Delete removed city files from S3
- Invalidate CloudFront cache
"""
import boto3, os, json

BUCKET = "mapevent-frontend-laetibibi"
CF_DIST = "E2FC7JI2N08SGK"
DATA_DIR = r"c:\MapEventAI_NEW\frontend\public\widget-data"
S3_PREFIX = "widget-data/"

REMOVED_CITIES = ["antwerpen", "gent", "lugano", "st-gallen"]

s3 = boto3.client("s3")
cf = boto3.client("cloudfront")

print("=== Upload des fichiers filtrés ===")
uploaded = 0
for f in sorted(os.listdir(DATA_DIR)):
    if not f.endswith(".json"):
        continue
    path = os.path.join(DATA_DIR, f)
    key = S3_PREFIX + f
    s3.upload_file(path, BUCKET, key, ExtraArgs={"ContentType": "application/json"})
    print(f"  [OK] {key}")
    uploaded += 1

print(f"\n{uploaded} fichiers uploadés.")

print("\n=== Suppression des villes retirées ===")
for city in REMOVED_CITIES:
    key = S3_PREFIX + city + ".json"
    try:
        s3.delete_object(Bucket=BUCKET, Key=key)
        print(f"  [DEL] {key}")
    except Exception as e:
        print(f"  [ERR] {key}: {e}")

print("\n=== Invalidation CloudFront ===")
resp = cf.create_invalidation(
    DistributionId=CF_DIST,
    InvalidationBatch={
        "Paths": {"Quantity": 1, "Items": ["/widget-data/*"]},
        "CallerReference": "widget-opendata-cleanup-" + str(int(__import__('time').time())),
    },
)
inv_id = resp["Invalidation"]["Id"]
print(f"  Invalidation: {inv_id}")
print("\nTerminé !")
