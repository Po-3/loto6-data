
import requests
from bs4 import BeautifulSoup
import json

def judge_features(numbers, carry):
    features = []
    nums = sorted(numbers)
    
    # 連番あり
    for i in range(len(nums) - 1):
        if nums[i] + 1 == nums[i+1]:
            features.append("連番あり")
            break
    
    # 奇数・偶数のカウント
    odd_count = sum(1 for n in nums if n % 2 == 1)
    even_count = sum(1 for n in nums if n % 2 == 0)
    if odd_count >= 4:
        features.append("奇数多め")
    if even_count >= 4:
        features.append("偶数多め")
    
    # 下一桁かぶり
    last_digits = [n % 10 for n in nums]
    if len(last_digits) != len(set(last_digits)):
        features.append("下一桁かぶり")
    
    # 合計小さめ・合計大きめ
    total = sum(nums)
    if total < 114:
        features.append("合計小さめ")
    if total > 151:
        features.append("合計大きめ")
    
    # キャリーあり
    if carry and int(carry) > 0:
        features.append("キャリーあり")
    
    return "・".join(features)

def fetch_latest_loto6_data():
    url = "https://www.mizuhobank.co.jp/takarakuji/check/loto/loto6/index.html"
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")
    
    try:
        # 本数字＋ボーナス数字を取得
        nums = soup.select_one(".mizuhoTableType01.result tbody tr td.resultNum")  # 数字の親要素
        if nums is None:
            print("❌ データ取得失敗：数字ブロックが見つかりません")
            return
        
        all_numbers = [int(num.get_text()) for num in nums.select(".numberSet span")]
        
        if len(all_numbers) < 7:
            print("❌ データ取得失敗：数字が7個揃いません")
            return
        
        d1, d2, d3, d4, d5, d6, bonus = all_numbers[:7]
        
        # キャリーオーバー取得
        carry_area = soup.find(text="キャリーオーバー")
        if carry_area:
            carry = carry_area.find_next("td").get_text().replace(",", "").replace("円", "").strip()
        else:
            carry = "0"
        
        # 特徴判定
        features = judge_features([d1, d2, d3, d4, d5, d6], carry)
        
        # 結果まとめ
        item = {
            "第1数字": d1,
            "第2数字": d2,
            "第3数字": d3,
            "第4数字": d4,
            "第5数字": d5,
            "第6数字": d6,
            "BONUS数字": bonus,
            "キャリーオーバー": carry,
            "特徴": features
        }
        
        print("✅ 最新データ取得成功")
        print(json.dumps(item, indent=2, ensure_ascii=False))
        
        return item
    
    except Exception as e:
        print(f"❌ データ取得エラー: {e}")
        return

if __name__ == "__main__":
    fetch_latest_loto6_data()
