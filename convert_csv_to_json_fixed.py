import csv
import json
import os

# 変換対象ファイルと出力ファイルのペア
files = [
    ("loto6.csv", "loto6_from_csv.json"),
    ("loto7.csv", "loto7_from_csv.json"),
    ("miniloto.csv", "miniloto_from_csv.json")
]

for csv_file, json_file in files:
    if not os.path.exists(csv_file):
        print(f"⚠️ {csv_file} が見つかりません。スキップします。")
        continue

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        data = list(reader)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ {csv_file} を {json_file} に変換しました。")
