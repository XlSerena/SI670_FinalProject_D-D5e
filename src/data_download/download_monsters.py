# src/data_download/download_monsters.py
import requests
import json
from pathlib import Path
import time

CURRENT_DIR = Path(__file__).parent  # src/data_download
PROJECT_ROOT = CURRENT_DIR.parent.parent
SAVE_DIR = PROJECT_ROOT / "data" / "raw"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

print("Begin downloading all monster data...")

# 1. 拿怪物列表
monsters_list = requests.get("https://www.dnd5eapi.co/api/monsters").json()["results"]

# 2. 循环拉取每个怪物的完整数据
all_monsters_full = []
for i, m in enumerate(monsters_list):
    url = "https://www.dnd5eapi.co" + m["url"]
    try:
        detail = requests.get(url).json()
        all_monsters_full.append(detail)
        print(f"Download Succeed {i + 1:3d} → {detail['name']}")
    except Exception as e:
        print(f"Download Fail {m['name']}: {e}")

    # 每30个休息1秒，防止被临时限速
    if i % 30 == 29:
        time.sleep(1)

print(f"\nTotal amount：{len(all_monsters_full)} ")
# 3. 保存到本地
save_path = SAVE_DIR / "monsters.json"
with open(save_path, "w", encoding="utf-8") as f:
    json.dump(all_monsters_full, f, ensure_ascii=False, indent=2)

print(f"\nMonster data saved.")
print("Loading Method: monsters = json.load(open('data/raw/monsters.json'))")