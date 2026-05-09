"""
楽天APIエージェント
楽天市場からベビー商品の売れ筋データを取得する
"""
import requests
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

# 生後4ヶ月向けキーワード一覧
BABY_KEYWORDS = [
    "おくるみ 新生児",
    "スリーパー ベビー ガーゼ",
    "抱っこ紐 よだれカバー",
    "ベビーソープ 新生児",
    "プレイマット ベビー",
    "ガラガラ 歯固め 赤ちゃん",
]

# 楽天APIエンドポイント（2026年版）
RAKUTEN_API_URL = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20220601"

# 必須ヘッダー（ないと403エラーになる）
HEADERS = {
    "Referer": "https://github.com",
    "Origin": "https://github.com"
}


def fetch_products(keyword: str, hits: int = 5) -> list:
    """
    キーワードで商品を検索して取得する
    """
    params = {
        "applicationId": os.getenv("RAKUTEN_APP_ID"),
        "accessKey": os.getenv("RAKUTEN_ACCESS_KEY"),
        "keyword": keyword,
        "hits": hits,
        "sort": "-reviewCount",   # レビュー数の多い順
        "minPrice": 1000,
        "maxPrice": 10000,
        "imageFlag": 1,
        "format": "json"
    }

    # アフィリエイトIDがあれば追加
    affiliate_id = os.getenv("RAKUTEN_AFFILIATE_ID")
    if affiliate_id:
        params["affiliateId"] = affiliate_id

    try:
        response = requests.get(RAKUTEN_API_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"  ❌ API エラー ({keyword}): {e}")
        return []

    items = []
    for item in response.json().get("Items", []):
        i = item["Item"]

        # 商品画像URL（最初の1枚）
        image_url = ""
        if i.get("mediumImageUrls"):
            image_url = i["mediumImageUrls"][0]["imageUrl"]

        # アフィリエイトURL（なければ通常URL）
        affiliate_url = i.get("affiliateUrl", i["itemUrl"])

        items.append({
            "name": i["itemName"],
            "price": i["itemPrice"],
            "url": i["itemUrl"],
            "affiliate_url": affiliate_url,
            "image_url": image_url,
            "shop_name": i.get("shopName", ""),
            "item_code": i.get("itemCode", ""),
            "review_count": i.get("reviewCount", 0),
            "review_average": i.get("reviewAverage", 0.0),
            "catch_copy": i.get("catchcopy", ""),
            "description": i.get("itemCaption", "")[:200],
            "keyword": keyword,
        })

    return items


def run() -> list:
    """
    全キーワードで商品を取得してまとめて返す
    """
    print("🔍 楽天APIエージェント 起動")

    all_products = []

    for i, keyword in enumerate(BABY_KEYWORDS):
        print(f"  検索中：{keyword}")
        # 429対策：2回目以降は1.5秒待機
        if i > 0:
            time.sleep(1.5)
        products = fetch_products(keyword, hits=3)
        all_products.extend(products)
        print(f"  → {len(products)}件取得")

    # 重複除去（商品名で判定）
    seen = set()
    unique = []
    for p in all_products:
        if p["name"] not in seen:
            seen.add(p["name"])
            unique.append(p)

    print(f"\n✅ 合計 {len(unique)} 件の商品を取得（重複除去後）")

    # output/products.json に保存
    os.makedirs("output", exist_ok=True)
    with open("output/products.json", "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    print("💾 output/products.json に保存しました")
    return unique
