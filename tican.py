import json

input_path = "/Users/po-san/hatena/loto6-data/loto6.json"
with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

for row in data:
    feat = row.get("特徴")
    if isinstance(feat, str):
        row["特徴"] = [f.strip() for f in feat.split("・") if f.strip()]
    elif not feat:
        row["特徴"] = []

with open(input_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)