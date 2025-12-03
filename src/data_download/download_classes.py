# src/data_download/download_classes.py
# Download all 12 classes + spellcasting + multiclassing (if available, otherwise None)
import requests
import json
from pathlib import Path
import time

CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
SAVE_DIR = PROJECT_ROOT / "data" / "raw"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

print("Begin downloading all profession data...")

classes_list = requests.get("https://www.dnd5eapi.co/api/classes").json()["results"]

all_classes_full = []
for i, c in enumerate(classes_list):
    index = c["index"]
    name = c["name"]

    # 1. 主职业数据（一定有）
    main = requests.get(f"https://www.dnd5eapi.co/api/classes/{index}").json()

    # 2. spellcasting（只有施法职业有）
    spellcasting = None
    sc_url = f"https://www.dnd5eapi.co/api/classes/{index}/spellcasting"
    sc_resp = requests.get(sc_url)
    if sc_resp.status_code == 200:
        spellcasting = sc_resp.json()

    # 3. multiclassing（有则取，无则 None）
    multiclassing = None
    multi_url = f"https://www.dnd5eapi.co/api/classes/{index}/multiclassing"
    multi_resp = requests.get(multi_url)
    if multi_resp.status_code == 200:
        try:
            multiclassing = multi_resp.json()
        except:
            multiclassing = None

    full_data = {
        "main": main,
        "spellcasting": spellcasting,
        "multiclassing": multiclassing
    }

    all_classes_full.append(full_data)
    print(
        f"Download Succeed. {i + 1:2d}/12 → {name.ljust(15)} | spellcasting: {'✓' if spellcasting else '✗'} | multiclassing: {'✓' if multiclassing else '✗'}")

    time.sleep(0.1)

save_path = SAVE_DIR / "classes.json"
with open(save_path, "w", encoding="utf-8") as f:
    json.dump(all_classes_full, f, ensure_ascii=False, indent=2)

print(f"\nClass data saved.")
print("Loading Method：")
print("classes = json.load(open('data/raw/classes.json'))")
print("wizard = [c for c in classes if c['main']['name']=='Wizard'][0]")