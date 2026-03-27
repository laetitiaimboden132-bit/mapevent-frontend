# -*- coding: utf-8 -*-
"""Resend to original 26 recipients with fixed sender (contact@mapevent.world)."""
import sys, os, time, boto3
from botocore.exceptions import ClientError

sys.path.insert(0, os.path.dirname(__file__))
from send_widget_campaign import send_email, REGION, RECIPIENTS

dry_run = "--send" not in sys.argv

if dry_run:
    print("=" * 60)
    print("  DRY-RUN - ajoutez --send pour envoyer")
    print("=" * 60)

client = boto3.client("ses", region_name=REGION)
sent = 0
errors = 0

for r in RECIPIENTS:
    tag = "[MEDIA]" if r.get("media") else "[VILLE]"
    label = f"{tag} {r['city']} -> {r['to']}"

    if dry_run:
        print(f"  {label}")
    else:
        try:
            msg_id = send_email(client, r)
            print(f"  [OK] {label}  (ID: {msg_id})")
            sent += 1
            time.sleep(1.5)
        except ClientError as e:
            print(f"  [ERR] {label}: {e.response['Error']['Message']}")
            errors += 1

print()
if dry_run:
    print(f"{len(RECIPIENTS)} emails prêts. --send pour envoyer.")
else:
    print(f"Terminé: {sent} envoyés, {errors} erreurs.")
