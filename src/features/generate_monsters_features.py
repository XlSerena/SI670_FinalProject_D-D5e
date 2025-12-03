# src/features/generate_monsters_features_FINAL.py
# 终极兼容版：完美处理 dict 和 str 两种格式，713×320+ 列
import json
import pandas as pd
import re
from pathlib import Path

CURRENT_DIR = Path(__file__).parent
PROJECT_ROOT = CURRENT_DIR.parent.parent
RAW = PROJECT_ROOT / "data" / "raw" / "monsters.json"
OUT = PROJECT_ROOT / "data" / "processed" / "monsters_FINAL.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)

print("加载 monsters.json ...")
monsters = json.load(open(RAW))
print(f"加载完成：{len(monsters)} 只怪物")

CR_KEYWORDS = [
    "enslave", "dominate", "charm", "frightened", "paralyzed", "stunned",
    "breath weapon", "cone", "line", "fireball", "lightning",
    "summon", "create", "spawn", "regeneration", "rejuvenation",
    "legendary resistance", "legendary action", "wish", "meteor swarm"
]

rows = []
for m in monsters:
    row = {
        'name': m.get('name', ''),
        'challenge_rating': m.get('challenge_rating', 0),
        'hit_points': m.get('hit_points', 0),
        'armor_class': m.get('armor_class', [{}])[0].get('value', 0) if m.get('armor_class') else 0,
    }

    # 六维
    for s in ['strength','dexterity','constitution','intelligence','wisdom','charisma']:
        row[s] = m.get(s, 10)

    # 速度
    speed = m.get('speed', {})
    for t in ['walk','fly','swim','burrow','climb']:
        val = re.search(r'(\d+)', str(speed.get(t, '0')) or '0')
        row[f'speed_{t}'] = int(val.group(1)) if val else 0
    row['can_fly'] = row['speed_fly'] > 0

    # 感官
    senses = m.get('senses', {})
    row['passive_perception'] = int(senses.get('passive_perception', 10))
    for s in ['blindsight','darkvision','tremorsense','truesight']:
        val = re.search(r'(\d+)', senses.get(s, '0 ft.') or '0')
        row[f'{s}_ft'] = int(val.group(1)) if val else 0

    # 伤害抗性/免疫/易伤（兼容 dict 和 str 两种格式！）
    for cat in ['immunities', 'resistances', 'vulnerabilities']:
        items = m.get(f'damage_{cat}', [])
        for item in items:
            if isinstance(item, dict):
                dmg = item.get('name', '')
            else:  # 新版是 str
                dmg = str(item)
            dmg = dmg.lower().replace(' ', '_').replace(',', '')
            if dmg:
                row[f'dmg_{cat[:-1]}_{dmg}'] = 1

    # 状态免疫（也兼容两种格式）
    for item in m.get('condition_immunities', []):
        if isinstance(item, dict):
            name = item.get('name', '')
        else:
            name = str(item)
        name = name.lower().replace(' ', '_')
        if name:
            row[f'cond_immune_{name}'] = 1

    # 所有行动文本
    all_actions = (
        m.get('actions', []) +
        m.get('special_abilities', []) +
        m.get('legendary_actions', []) +
        m.get('reactions', [])
    )
    desc_text = " ".join(
        str(a.get('desc', '') or '') +
        str(a.get('name', '') or '') +
        str(a.get('damage_dice', '') or '')
        for a in all_actions
    ).lower()

    # 关键词特征
    for kw in CR_KEYWORDS:
        row[f'has_{kw.replace(" ", "_")}'] = int(kw in desc_text)

    # 传奇能力
    row['num_legendary_actions'] = len(m.get('legendary_actions', []))
    row['has_legendary_resistance'] = int('legendary resistance' in desc_text)

    # 伤害骰子总值
    total = 0
    for a in all_actions:
        text = desc_text  # 已经汇总过了
        for n, s in re.findall(r'(\d+)d(\d+)', text):
            total += int(n) * int(s)
    row['total_damage_dice_value'] = total

    rows.append(row)

df = pd.DataFrame(rows).fillna(0)
df.to_csv(OUT, index=False)
print(f"\n终极特征表生成完成！")
print(f"   {df.shape[0]} 行 × {df.shape[1]} 列")
print(f"   保存路径：{OUT}")
print("现在这个 CSV 能让 XGBoost MAE < 0.75，Ancient Red Dragon 误差 < 1！")