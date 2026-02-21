"""
Supprime les événements de test
"""

import requests
import sys
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

# IDs des événements de test à supprimer
TEST_IDS = [347, 348]

print("🗑️ Suppression des événements de test...")

for event_id in TEST_IDS:
    response = requests.delete(
        f"{API_URL}/api/events/{event_id}",
        timeout=30
    )
    print(f"   Event {event_id}: {response.status_code}")

print("✅ Terminé!")
