"""
HARM × Baby Boo ランキング取得
楽天APIを使ってHARMカテゴリ別・Klingシーン別の売れ筋商品を取得する。
通常mode の商品選定に使用。
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
    },
}

# Klingシーンキー → 楽天検索キーワード
SCENE_KEYWORDS = {
    "sleep":    ["スリーパー ベビー ガーゼ", "おくるみ 新生児 人気", "ベビー布団 洗える"],
    "feeding":  ["哺乳瓶 消毒 セット", "離乳食 食器 セット 赤ちゃん", "スタイ ビブ 防水 赤ちゃん"],
    "clothing": ["ベビー ロンパース 新生児", "ベビー 肌着 セット 新生児", "カバーオール 赤ちゃん 人気"],
    "toy":      ["知育玩具 0歳 赤ちゃん", "ガラガラ 歯固め 赤ちゃん", "絵本 赤ちゃん 布"],
    "bath":     ["ベビーバス 新生児 沐浴", "ベビーソープ 泡 赤ちゃん", "バスタオル 赤ちゃん ガーゼ"],
    "carrier":  ["抱っこ紐 新生児 メッシュ", "ヒップシート 抱っこ紐 人気"],
    "bouncer":  ["バウンサー ベビー 人気", "ハイローチェア 電動 赤ちゃん"],
    "teether":  ["歯固め 赤ちゃん 安全", "おしゃぶり 新生児 人気"],
    "stroller": ["ベビーカー 軽量 折りたたみ", "チャイルドシート 新生児 回転式"],
    "skincare": ["ベビー 保湿クリーム 全身", "ベビーローション 低刺激", "赤ちゃん 日焼け止め"],
    "blanket":  ["おくるみ ガーゼ 赤ちゃん", "スリーパー ガーゼ ベビー", "ブランケット ベビー 洗える"],
}


def _fetch_ranking(keywords: list, top_n: int = 3) -> list:
    """複数キーワードで検索してレビュー数順に上位top_nを返す共通ロジック"""
    all_products = []
    seen_names = set()
    for i, keyword in enumerate(keywords):
        if i > 0:
            time.sleep(1.0)
        for p in fetch_products(keyword, hits=3):
            if p["name"] not in seen_names:
                seen_names.add(p["name"])
                all_products.append(p)
    all_products.sort(key=lambda x: x.get("review_count", 0), reverse=True)
    return all_products[:top_n]


def fetch_harm_ranking(harm_key: str, top_n: int = 3) -> list:
    """指定HARMカテゴリの売れ筋上位商品を返す"""
    cat = HARM_CATEGORIES.get(harm_key)
    return _fetch_ranking(cat["keywords"], top_n) if cat else []


def fetch_scene_ranking(scene_key: str, top_n: int = 3) -> list:
    """指定Klingシーンの売れ筋上位商品を返す"""
    keywords = SCENE_KEYWORDS.get(scene_key)
    return _fetch_ranking(keywords, top_n) if keywords else []
