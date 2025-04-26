import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

# ローカルJSONファイルのパス
json_path = "/Users/po-san/hatena/loto6-data/loto6.json"

# 抽選結果を取得するみずほ銀行のページ
url = "https://www.mizuhobank.co.jp/takarakuji/check/loto/loto6/index.html"

def fetch_latest_loto6():
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")

    try:
        rows = soup.select("table.js-lottery-number tbody tr")
        round_text = rows[0].select_one("th").text.strip()
        round_num = round_text.replace("第", "").replace("回", "").strip()
        date_text = rows[1].select_one("td").text.strip()
        date = datetime.strptime(date_text, "%Y年%m月%d日").strftime("%Y/%-m/%-d")

        numbers = [td.text.strip() for td in rows[2].select("td b") if td.text.strip().isdigit()]
        if len(numbers) < 7:
            print("⚠️ 数字の取得に失敗しました。")
            return None

        bonus = numbers[-1]
        main_numbers = numbers[:-1]

        return {
            "開催回": round_num,
            "日付": date,
            "第1数字": main_numbers[0],
            "第2数字": main_numbers[1],
            "第3数字": main_numbers[2],
            "第4数字": main_numbers[3],
            "第5数字": main_numbers[4],
            "第6数字": main_numbers[5],
            "BONUS数字": bonus
        }

    except Exception as e:
        print("❌ データ取得エラー:", e)
        return None

def update_json(entry):
    if not os.path.exists(json_path):
        print("⚠️ JSONファイルが存在しません")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if any(d["開催回"] == entry["開催回"] for d in data):
        print(f"✅ すでに登録済みの開催回（{entry['開催回']}）です")
        return

    data.append(entry)
    data.sort(key=lambda x: int(x["開催回"]))

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ 開催回 {entry['開催回']} を追加しました")

if __name__ == "__main__":
    entry = fetch_latest_loto6()
    if entry:
        update_json(entry)
