#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
import os
import subprocess
from datetime import datetime

def scrape_loto_data(url, loto_type):
    response = requests.get(url)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')

    title_text = soup.find('h1').get_text()
    try:
        kai = title_text.split('回')[0].replace('第', '').strip()
        date_text = title_text.split('(')[-1].split(')')[0].strip()
    except Exception as e:
        print(f"開催回と抽選日パースエラー: {e}")
        return None

    result_spans = soup.select('div.result span')
    numbers = []
    bonus_numbers = []
    for span in result_spans:
        if 'bonus' in span.get('class', []):
            bonus_numbers.append(span.text.zfill(2))
        else:
            numbers.append(span.text.zfill(2))

    prize_table = soup.find('table')
    rows = prize_table.find_all('tr')[1:]
    prize_data = {}
    for idx, row in enumerate(rows):
        cols = row.find_all('td')
        if len(cols) >= 3:
            grade = f"{idx+1}等"
            prize_data[f"{grade}口数"] = cols[1].get_text(strip=True).replace(',', '')
            prize_data[f"{grade}賞金"] = cols[2].get_text(strip=True).replace(',', '').replace('円', '')

    carry_text = soup.get_text()
    carry_amount = "0"
    if 'キャリーオーバー' in carry_text:
        try:
            carry_line = [line for line in carry_text.splitlines() if 'キャリーオーバー' in line][0]
            carry_amount = carry_line.split('キャリーオーバー')[1]
            carry_amount = ''.join(filter(str.isdigit, carry_amount))
        except Exception as e:
            print(f"キャリー抽出エラー: {e}")

    features = []
    sorted_numbers = sorted([int(n) for n in numbers])
    if any(sorted_numbers[i] + 1 == sorted_numbers[i+1] for i in range(len(sorted_numbers)-1)):
        features.append("連番あり")

    odds = sum(1 for n in sorted_numbers if n % 2 == 1)
    evens = len(sorted_numbers) - odds
    if loto_type == 'miniloto':
        if odds >= 4:
            features.append("奇数多め")
        elif evens >= 4:
            features.append("偶数多め")
        else:
            features.append("バランス型")
    else:
        if odds >= len(sorted_numbers) - 1:
            features.append("奇数多め")
        elif evens >= len(sorted_numbers) - 1:
            features.append("偶数多め")

    last_digits = [n % 10 for n in sorted_numbers]
    if len(last_digits) != len(set(last_digits)):
        features.append("下一桁かぶり")

    total = sum(sorted_numbers)
    if loto_type == 'loto6':
        if total < 114:
            features.append("合計小さめ")
        elif total > 151:
            features.append("合計大きめ")
    elif loto_type == 'loto7':
        if total < 140:
            features.append("合計小さめ")
        elif total > 190:
            features.append("合計大きめ")
    elif loto_type == 'miniloto':
        if total < 70:
            features.append("合計小さめ")
        elif total > 100:
            features.append("合計大きめ")

    if loto_type == 'loto7':
        tens = [n // 10 for n in sorted_numbers]
        if tens.count(1) >= 3:
            features.append("10番台集中")
        if tens.count(3) >= 3:
            features.append("30番台多め")
        high = sum(1 for n in sorted_numbers if n >= 20)
        low = len(sorted_numbers) - high
        if abs(high - low) <= 1:
            features.append("高低ミックス")

    if loto_type != 'miniloto' and carry_amount.isdigit() and int(carry_amount) > 0:
        features.append("キャリーあり")

    data = {
        "開催回": kai,
        "日付": date_text,
    }
    for idx, num in enumerate(numbers):
        data[f"第{idx+1}数字"] = num

    if loto_type == 'loto7':
        data["BONUS数字1"] = bonus_numbers[0] if len(bonus_numbers) > 0 else ""
        data["BONUS数字2"] = bonus_numbers[1] if len(bonus_numbers) > 1 else ""
    else:
        data["BONUS数字"] = bonus_numbers[0] if bonus_numbers else ""

    data.update(prize_data)
    if loto_type != 'miniloto':
        data["キャリーオーバー"] = carry_amount
    data["特徴"] = features

    return data

def save_to_json(file_path, new_entry):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    data.append(new_entry)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def git_push():
    try:
        subprocess.run(["git", "add", "loto6.json"], check=True)
        subprocess.run(["git", "add", "../loto7-data/loto7.json"], check=True)
        subprocess.run(["git", "add", "../miniloto-data/miniloto_data_for_web_with_features.json"], check=True)
        subprocess.run(["git", "commit", "-m", "♻️ ロト最新データ自動取得＆保存"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ GitHubにPush完了")
    except subprocess.CalledProcessError as e:
        print(f"❌ Gitエラー: {e}")

if __name__ == "__main__":
    targets = [
        ("https://loto6.thekyo.jp", "loto6", "/Users/po-san/hatena/loto6-data/loto6.json"),
        ("https://loto7.thekyo.jp", "loto7", "/Users/po-san/hatena/loto7-data/loto7.json"),
        ("https://miniloto.thekyo.jp", "miniloto", "/Users/po-san/hatena/miniloto-data/miniloto_data_for_web_with_features.json")
    ]

    for url, loto_type, save_path in targets:
        print(f"\n▶️ {loto_type.upper()} データ取得開始")
        loto_data = scrape_loto_data(url, loto_type)
        if loto_data:
            save_to_json(save_path, loto_data)
            print(f"✅ 保存完了: {save_path}")
        else:
            print(f"❌ {loto_type.upper()} データ取得失敗")

    # Git自動Push
    git_push()
