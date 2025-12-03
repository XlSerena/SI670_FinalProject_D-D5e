# src/data_download/download_spells.py
import requests
import json
from pathlib import Path
import time

CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
SAVE_DIR = PROJECT_ROOT / "data" / "raw"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

print("Begin downloading all spell data...")

spells_list = requests.get("https://www.dnd5eapi.co/api/spells").json()["results"]

all_spells_full = []
for i, s in enumerate(spells_list):
    url = "https://www.dnd5eapi.co" + s["url"]
    try:
        detail = requests.get(url).json()
        all_spells_full.append(detail)
        print(f"Download Succeed {i + 1:3d} → {detail['name']}")
    except Exception as e:
        print(f"Download Fail {s['name']}: {e}")

    if i % 30 == 29:
        time.sleep(1)

save_path = SAVE_DIR / "spells.json"
with open(save_path, "w", encoding="utf-8") as f:
    json.dump(all_spells_full, f, ensure_ascii=False, indent=2)

print(f"\nSpell data saved.")
print("Loading Method: spells = json.load(open('data/raw/spells.json'))")