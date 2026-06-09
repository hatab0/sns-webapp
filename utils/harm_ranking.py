"""
HARM × Baby Boo ランキング取得
楽天APIを使ってHARMカテゴリ別の売れ筋商品を取得する。
マラソン前の通常mode商品選定に使用。
"""
import time
from agents.rakuten_agent import fetch_products

HARM_CATEGORIES = {
    "H": {
        "label": "H — 健康・スキンケア",
        "emoji": "💊",
        "description": "赤ちゃんの健康・肌ケア・栄養",
        "keywords": [
            "ベビー 保湿クリーム 全身",
            "ベビーローション 低刺激",
            "赤ちゃん 鼻水吸引器",
            "ベビー 体温計 非接触",
            "ベビーフード オーガニック 離乳食",
            "赤ちゃん 日焼け止め",
        ],
        "min_price": 800,
        "max_price": 8000,
    },
    "A": {
        "label": "A — 撮影・パパ活",
        "emoji": "📱",
        "description": "育休パパのコンテンツ制作・撮影グッズ",
        "keywords": [
            "スマホスタンド 卓上 自撮り",
            "リングライト スマホ 撮影",
            "ミニ三脚 スマホ コンパクト",
            "赤ちゃん 撮影 小道具",
            "ベビーフォト 小物 セット",
        ],
        "min_price": 500,
        "max_price": 8000,
    },
    "R": {
        "label": "R — 育児・おもちゃ",
        "emoji": "🧸",
        "description": "親子の絆・おもちゃ・寝かしつけ",
        "keywords": [
            "知育玩具 0歳 赤ちゃん",
            "ガラガラ 歯固め 赤ちゃん",
            "絵本 赤ちゃん 布",
            "抱っこ紐 新生児 メッシュ",
            "スリーパー ガーゼ ベビー",
            "おしゃぶり 新生児",
        ],
        "min_price": 1000,
        "max_price": 15000,
    },
    "M": {
        "label": "M — 節約・消耗品",
        "emoji": "💰",
        "description": "育休中パパの節約・コスパ重視グッズ",
        "keywords": [
            "おむつ まとめ買い コスパ",
            "おしりふき まとめ買い",
            "粉ミルク コスパ",
            "ベビー ウェットティッシュ まとめ",
            "哺乳瓶 消毒 コスパ",
        ],
        "min_price": 500,
        "max_price": 6000,
    },
}


def fetch_harm_ranking(harm_key: str, top_n: int = 3) -> list:
    """
    指定HARMカテゴリの売れ筋上位商品を返す。
    複数キーワードで検索し、レビュー数でソートして上位top_nを返す。
    """
    cat = HARM_CATEGORIES.get(harm_key)
    if not cat:
        return []

    all_products = []
    seen_names = set()

    for i, keyword in enumerate(cat["keywords"]):
        if i > 0:
            time.sleep(1.0)
        products = fetch_products(keyword, hits=3)
        for p in products:
            if p["name"] not in seen_names:
                seen_names.add(p["name"])
                all_products.append(p)

    all_products.sort(key=lambda x: x.get("review_count", 0), reverse=True)
    return all_products[:top_n]


def fetch_all_harm_rankings(top_n: int = 3) -> dict:
    """全HARMカテゴリのランキングを返す。{harm_key: [products]}"""
    result = {}
    for key in HARM_CATEGORIES:
        result[key] = fetch_harm_ranking(key, top_n=top_n)
        time.sleep(0.5)
    return result
