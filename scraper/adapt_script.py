# -*- coding: utf-8 -*-
"""
Adapts send_20_new_promo.py into send_30_personal_promo.py with fixed password,
TARGET=30, new JSON file, and script name. Uses encoding=utf-8 for all I/O.
"""
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

INPUT_PATH = r"c:\MapEventAI_NEW\frontend\scraper\send_20_new_promo.py"
OUTPUT_PATH = r"c:\MapEventAI_NEW\frontend\scraper\send_30_personal_promo.py"

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "APP_PASSWORD = sys.argv[1].replace(' ', '') if len(sys.argv) > 1 else None",
    "APP_PASSWORD = 'poymmsajpfhpkfci'"
)

block = "if not APP_PASSWORD:\n    print(\"Usage: python send_20_new_promo.py MOT_DE_PASSE_APP\")\n    sys.exit(1)\n\n"
content = content.replace(block, "")

content = content.replace("TARGET = 20", "TARGET = 30")
content = content.replace("selected_20_new.json", "selected_35_promo_v2.json")
content = content.replace("send_20_new_promo.py", "send_30_personal_promo.py")

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Done. Read", INPUT_PATH)
print("Wrote", OUTPUT_PATH)
print("Replacements applied: APP_PASSWORD, removed usage block, TARGET=30, selected_35_promo_v2.json, send_30_personal_promo.py")