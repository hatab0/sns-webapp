"""
リール台本・Threads投稿コンセプト生成エージェント

生成コンテンツ：
  1. Threads投稿（育児ランダムトピック・1本）
  2. Instagram Reel（バイラルコンセプト）
"""
import anthropic
import os
import json
import random
from datetime import date
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

BIRTH_DATE = date(2025, 12, 22)


def calc_month_age() -> int:
    today = date.today()
    months = (today.year - BIRTH_DATE.year) * 12 + (today.month - BIRTH_DATE.month)
    if today.day < BIRTH_DATE.day:
        months -= 1
    return max(0, months)


MONTH_AGE = calc_month_age()

MONTHLY_STRUGGLES = {
    0:  ["授乳が2時間おき", "泣き止まない理由がわからない", "沐浴が毎回緊張する"],
    1:  ["げっぷがうまく出ない", "抱っこじゃないと寝ない", "夜中の授乳で限界"],
    2:  ["あやしても泣き止まない黄昏泣き", "やっと笑った瞬間が全てを癒す", "哺乳瓶拒否が始まった"],
    3:  ["首すわり練習が地味にきつい", "よだれが急に増えた", "寝返り練習で目が離せない"],
    4:  ["よだれスタイが1日5枚でも足りない", "夜中まだ2〜3回起きる", "ベビーカー乗り嫌いが発覚"],
    5:  ["離乳食準備どこから始めるか問題", "寝返りしてうつ伏せで泣く無限ループ", "後追いが始まった気がする"],
    6:  ["離乳食を全拒否される", "お座りが不安定で目が離せない", "人見知りがひどくなってきた"],
    7:  ["ハイハイで何でも触りに行く", "離乳食の食べムラがすごい", "夜泣き復活した"],
    8:  ["つかまり立ちで毎日ひとり転倒", "後追いMAX期でトイレも行けない", "なんでも口に入れる"],
    9:  ["伝い歩きが始まって家中危ない", "指差しが始まってどこでも「あっあっ」", "昼寝が1回になってきた"],
    10: ["「ママ」「パパ」がやっと出てきた感動", "食べ物の好き嫌いがはっきりしてきた", "靴を嫌がって泣く"],
    11: ["もうすぐ1歳なのに感慨深い", "歩きたいのに歩けなくてギャン泣き", "卒乳問題が頭をよぎる"],
    12: ["1歳の誕生日準備が想定外に大変", "一升餅で泣かせてしまった", "やっと歩いた瞬間"],
}

THREADS_THEMES = [
    "育児あるある（笑える・思わず共感する日常の出来事）",
    "パパの本音（育休・育児の大変さ・正直な気持ち）",
    f"生後{{month}}ヶ月の成長の気づき（月齢ならではの出来事・変化）",
    "夜泣き・睡眠・授乳など深夜の一コマ",
    "赤ちゃんに癒された・心が動いた瞬間",
    "育休中のリアル（孤独感・充実感・予想外だったこと）",
    "育児グッズについて正直な感想（良かった・これじゃなかった）",
    "パートナーとの育児分担・気づいたこと",
]

BABY_SPEECH_BY_MONTH = {
    0:  {"sounds": ["おぎゃー", "ふにゃー"],                   "desc": "泣き声のみ"},
    1:  {"sounds": ["あー", "うー"],                           "desc": "クーイング（母音）"},
    2:  {"sounds": ["あーうー", "えへへ"],                     "desc": "クーイング＋笑い声"},
    3:  {"sounds": ["あははっ", "きゃっ", "うふー"],           "desc": "笑い声・喜び声"},
    4:  {"sounds": ["あーっ！", "えへへ", "んー？", "きゃっ"],  "desc": "クーイング・笑い声・驚き"},
    5:  {"sounds": ["ままま", "ばばば", "あっあっ"],           "desc": "喃語（繰り返し音）開始"},
    6:  {"sounds": ["まーまー", "ぱーぱー", "んまー"],         "desc": "喃語が増える"},
    7:  {"sounds": ["あーあー", "まんまー", "ぱっぱー"],       "desc": "意味のある喃語"},
    8:  {"sounds": ["まんまー", "ねーね", "うー！"],           "desc": "食べ物・眠気の喃語"},
    9:  {"sounds": ["まんまー！", "ぱっぱー", "やー！"],       "desc": "喃語＋指差し声"},
    10: {"sounds": ["ママ", "パパ", "まんま"],                 "desc": "初語デビュー！"},
    11: {"sounds": ["ママ！", "パパ！", "まんまー！"],         "desc": "初語が明確に"},
    12: {"sounds": ["ママ", "パパ", "わんわん", "ねんね"],     "desc": "語彙が増える"},
}


def _parse_json_response(text: str) -> dict:
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text, "error": "JSON parse failed"}


def generate_threads_text() -> dict:
    """
    Threads投稿：育児トピックをランダムに選んでリアルな投稿コンセプトを1本生成する。
    商品紹介・インスタ誘導・ハッシュタグなし。
    Threadsのアルゴリズムで表示されやすい育児共感コンテンツ。
    """
    theme = random.choice(THREADS_THEMES).replace("{month}", str(MONTH_AGE))
    struggles = MONTHLY_STRUGGLES.get(MONTH_AGE, MONTHLY_STRUGGLES[4])

    prompt = f"""
あなたはせなっち（生後{MONTH_AGE}ヶ月）を育てる育休中のパパです。
Threads向けの育児投稿コンセプトを1本作成してください。

【今回のテーマ】
{theme}

【今の月齢（生後{MONTH_AGE}ヶ月）の育児リアル】
・{"・".join(struggles)}

【絶対守ること】
・商品紹介・アフィリエイトは一切なし
・Instagramへの誘導なし
・ハッシュタグなし
・AIが書いた文章に見えてはいけない
・スマホでさっと打ったような自然な口語体
・Threadsのアルゴリズムで同じ境遇の人に届くような内容

【出力形式】JSONのみ。前置き不要。

{{
  "type": "threads_text",
  "title": "投稿タイトル（内部管理用・20字以内）",
  "theme": "選んだテーマ",
  "caption_hint": "投稿の方向性・具体的なエピソードのヒント（2〜3文）"
}}
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    result = _parse_json_response(message.content[0].text.strip())
    result["type"] = "threads_text"
    result["theme"] = theme
    return result


def generate_reel_concept(product: dict) -> dict:
    """Instagram Reel：バイラルコンセプトを生成する。"""
    speech_info = BABY_SPEECH_BY_MONTH.get(MONTH_AGE, BABY_SPEECH_BY_MONTH[4])
    sounds_str = "・".join(speech_info["sounds"])
    speech_desc = speech_info["desc"]

    prompt = f"""
あなたはInstagramバイラルリール動画のコンテンツ戦略家です。

AIベビーキャラ「せなっち」（生後{MONTH_AGE}ヶ月）のバイラルリールコンセプトを作成してください。

【コンセプトの核心】
・自然な赤ちゃんの瞬間を捉えながら、商品がちゃんと映る
・せなっちが商品を実際に着ている・使っている状態で月齢の声・仕草をする
・「かわいすぎ」「これ何使ってるの？」と思わずコメントしたくなる
・宣伝感はゼロでも、商品はしっかり主役として映っている
・自然にループする動画構成（最後→最初がつながる）

【せなっちの月齢情報】
・生後{MONTH_AGE}ヶ月
・この月齢の発声レベル：{speech_desc}
・月齢に合った声・音：{sounds_str}

【商品情報（せなっちが実際に着る・使う）】
商品名：{product['name']}
商品カテゴリ：{product.get('catch_copy', '')}

【リールの構成ルール】
・0〜2秒：フック（スクロールを止める冒頭）
・2〜8秒：メインシーン（商品を着ている/使っているせなっちが声・音を出す）
・8〜12秒：ループポイント（自然に最初に戻る構成）
・音声OFFでも伝わるテキストオーバーレイを想定

【出力形式】JSONのみ。前置き不要。

{{
  "type": "reel",
  "title": "動画タイトル（内部管理用・20字以内）",
  "hook": "冒頭0〜2秒のフックテキスト（スクロールを止める一言・日本語）",
  "bgm_style": "BGMの雰囲気（例：ほんわか邦楽・ポップなインスト・TikTokトレンド系）",
  "viral_concept": "バイラルシーンの詳細な説明（3〜5文。商品の着用/使用方法・月齢サウンド・ループポイントを含める）"
}}
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    result = _parse_json_response(message.content[0].text.strip())
    result["type"] = "reel"
    result["product_name"] = product["name"]
    return result


def run(product: dict) -> list:
    """
    2種類のコンテンツコンセプトを生成して返す。
    戻り値: [threads_text, reel]
    """
    print(f"コンテンツコンセプト生成エージェント 起動（生後{MONTH_AGE}ヶ月）")

    print("  [1/2] Threads 育児投稿コンセプト 生成中...")
    threads_text = generate_threads_text()
    print(f"    完了：{threads_text.get('title', '')}（テーマ: {threads_text.get('theme', '')}）")

    print("  [2/2] Instagram Reel バイラルコンセプト 生成中...")
    reel = generate_reel_concept(product)
    print(f"    完了：{reel.get('title', '')}")

    print(f"\n2 件のコンテンツコンセプトを生成しました")
    return [threads_text, reel]
