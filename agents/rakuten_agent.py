"""
楽天APIエージェント
楽天市場からベビー商品の売れ筋データを取得する
"""
import requests
import os
import json
import time
import random
from dotenv import load_dotenv

load_dotenv()

# 育児全般キーワード（毎回ランダム10件を使用）
ALL_BABY_KEYWORDS = [
    # 新生児・乳児
    "おくるみ 新生児",
    "スリーパー ベビー ガーゼ",
    "ベビーソープ 新生児",
    "ガラガラ 歯固め 赤ちゃん",
    "哺乳瓶 消毒 セット",
    "おしゃぶり 新生児",
    "抱っこ紐 よだれカバー",
    "ベビー爪切り 電動",
    "新生児 セレモニードレス",
    # マタニティ
    "マタニティ パジャマ 授乳",
    "抱き枕 授乳枕 妊婦",
    "マタニティ 骨盤ベルト",
    "授乳ブラ ノンワイヤー",
    "マタニティ 腹帯 さらし",
    # 離乳食
    "離乳食 食器 セット 赤ちゃん",
    "離乳食 冷凍 容器 小分け",
    "ベビーフード 離乳食 5ヶ月",
    "離乳食 調理器 セット すり鉢",
    "ベビー 麦茶 赤ちゃん",
    # お風呂・スキンケア
    "ベビーバス 新生児 沐浴",
    "ベビー 保湿クリーム 全身",
    "赤ちゃん シャンプー 泡",
    "沐浴 ガーゼ タオル 新生児",
    # 寝具・部屋
    "ベビー布団 セット 洗える",
    "ベビーベッド 折りたたみ 軽量",
    "ベビーモニター 無線 カメラ",
    "プレイマット ベビー 折りたたみ",
    # おもちゃ・知育
    "ベビー 知育玩具 6ヶ月",
    "積み木 木製 赤ちゃん",
    "赤ちゃん ぬいぐるみ 安全",
    "メリー ベビー 音楽",
    "絵本 赤ちゃん 布",
    # お出かけ
    "抱っこ紐 新生児 メッシュ",
    "チャイルドシート 新生児 回転式",
    "マザーズバッグ 大容量 軽量",
    "ベビーカー 軽量 折りたたみ",
    "日よけ ベビーカー サンシェード",
    # 安全グッズ
    "ベビーゲート 突っ張り",
    "コーナーガード 赤ちゃん",
    "チャイルドロック 引き出し",
    # 子ども服
    "ベビー ロンパース 新生児",
    "赤ちゃん 帽子 日よけ UVカット",
    "ベビー 肌着 セット 新生児",
]

# 毎回ランダムに10件選ぶ（バリエーションを確保）
BABY_KEYWORDS = random.sample(ALL_BABY_KEYWORDS, min(10, len(ALL_BABY_KEYWORDS)))

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
