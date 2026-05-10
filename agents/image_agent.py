"""
画像プロンプト生成エージェント
ChatGPT GPT Image 2用の画像プロンプトと InsMind動画プロンプトをClaude APIで生成する
"""
import anthropic
import os
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

# 月齢グループ別InsMind動画プロンプト設計
INSMIND_BY_AGE_GROUP = {
    "0-2": {
        "sounds": ["おぎゃー", "あー", "うー"],
        "motion_en": (
            "stares gently at camera with wide innocent eyes, tiny fingers occasionally twitch, "
            "peaceful newborn breathing rhythm, slow subtle head tilt, serene newborn moment"
        ),
        "mood_en": "serene, calm, precious newborn",
    },
    "3": {
        "sounds": ["あははっ", "きゃっ", "うふー"],
        "motion_en": (
            "suddenly breaks into a big gummy smile directly at camera, arms flap excitedly, "
            "legs kick with joy, whole body expresses happiness"
        ),
        "mood_en": "joyful, heartwarming, first real laughs",
    },
    "4-5": {
        "sounds": ["あーっ！", "えへへ", "きゃっ"],
        "motion_en": (
            "looks directly at camera then suddenly flashes a huge delighted smile, "
            "slow gentle zoom in, natural seamless loop"
        ),
        "mood_en": "warm, natural, irresistibly cute",
    },
    "6-7": {
        "sounds": ["まーまー", "ぱーぱー", "んまー"],
        "motion_en": (
            "babbles 'mama' or 'papa' sounds with mouth movements, hands open and close "
            "in grabbing motion, leans forward curiously toward camera"
        ),
        "mood_en": "curious, developing personality, engaging babbling",
    },
    "8-9": {
        "sounds": ["まんまー！", "ぱっぱー", "やー！"],
        "motion_en": (
            "points finger at camera with big expressive eyes, leans forward excitedly, "
            "waves hands enthusiastically, clear intentional gestures"
        ),
        "mood_en": "expressive, interactive, dynamic personality",
    },
    "10-12": {
        "sounds": ["ママ！", "パパ！", "まんま！"],
        "motion_en": (
            "clearly mouths 'mama' or 'papa', reaches both arms toward camera with a big smile, "
            "milestone moment of first real words"
        ),
        "mood_en": "milestone, emotional, first words moment",
    },
    "13+": {
        "sounds": ["だっこ！", "もっと！", "いやいや！"],
        "motion_en": (
            "shakes head 'no' expressively or reaches out with demanding gesture, "
            "strong emerging personality, deliberate funny toddler movements"
        ),
        "mood_en": "opinionated, funny, relatable toddler",
    },
}

# バズmode：月齢別ダンス動作
BUZZ_MOTION_BY_AGE_GROUP = {
    "0-6": (
        "body sways gently from side to side, head bobs adorably, "
        "tiny arms wave in rhythm, pure joy and movement"
    ),
    "7-12": (
        "whole body bounces up and down to the beat, claps hands together, "
        "big excited smile, full body rhythm"
    ),
    "13+": (
        "spins in place laughing, wiggles hips to the music, "
        "falls down and pops back up still dancing, irresistibly funny"
    ),
}


def _get_age_group(month_age: int) -> str:
    if month_age <= 2:
        return "0-2"
    elif month_age == 3:
        return "3"
    elif month_age <= 5:
        return "4-5"
    elif month_age <= 7:
        return "6-7"
    elif month_age <= 9:
        return "8-9"
    elif month_age <= 12:
        return "10-12"
    else:
        return "13+"


def _get_buzz_age_group(month_age: int) -> str:
    if month_age <= 6:
        return "0-6"
    elif month_age <= 12:
        return "7-12"
    else:
        return "13+"


def _base_image_prompt_text(product: dict) -> str:
    """商品あり：画像プロンプトの共通部分（2枚参照画像前提）"""
    return f"""
ChatGPT GPT Image 2で使用する、高品質な画像生成プロンプトを英語で作成してください。

【前提：ユーザーから2枚の参照画像が送信されます】
  参照画像1: 赤ちゃん「せなっち」の写真 → 外見の完全一致に使用
  参照画像2: 商品「{product['name'][:50]}」の商品写真 → 商品外観の完全一致に使用

【タスク】
参照画像1のせなっちが、参照画像2の商品を実際に着用・使用しているリアルな写真を生成する。
赤ちゃんの顔・髪・体つきは参照画像1と完全一致させること。
商品のデザイン・色・形は参照画像2と完全一致させること。

【GPT Image 2向け：撮影スタイル】
・スタイル：Photorealistic studio photography, professional baby product lifestyle photo
・カメラ：Shot with 85mm portrait lens, shallow depth of field, soft bokeh background
・照明：Soft diffused studio lighting, warm 3200K color temperature, gentle fill light from left
・構図：Close-up to medium shot, subject centered, 1:1 square format

【せなっちのキャラクター補足（参照画像1に加えて守る）】
・生後{MONTH_AGE}ヶ月の日本人男の子
・白いリボンカチューシャ（細いサテンリボン）
・表情：穏やかな笑顔 or 商品に興味を示している顔

【背景・雰囲気】
・背景：クリーム色・アイボリー・ベージュのナチュラルスタジオ
・小物：白いふわふわのブランケット・薄いモスリンガーゼ
・全体的にナチュラル・オーガニック・清潔感のある世界観
"""


def _base_scene_text_buzz() -> str:
    """バズmode：せなっちがコスチュームを着て豊かな表情でバズるシーン（2枚参照画像前提）"""
    age_group = _get_age_group(MONTH_AGE)
    age_info = INSMIND_BY_AGE_GROUP.get(age_group, INSMIND_BY_AGE_GROUP["4-5"])
    sounds = "・".join(age_info["sounds"])

    return f"""
ChatGPT GPT Image 2で使用する、高品質な画像生成プロンプトを英語で作成してください。

【前提：ユーザーから2枚の参照画像が送信されます】
  参照画像1: 赤ちゃん「せなっち」の写真 → 顔・外見の完全一致に使用
  参照画像2: コスチューム・衣装の画像（アニメ服・野菜コス・果物コス・キャラクターコスなど） → 着せる服装として使用

【タスク】
参照画像1のせなっちが、参照画像2のコスチュームを着て、バイラルな表情・ポーズをしているリアルな写真を生成する。
赤ちゃんの顔・髪・体つきは参照画像1と完全一致させること。
コスチュームのデザイン・色・形は参照画像2と完全一致させること。

【バズる表情・ポーズ（最重要 — 必ずいずれかを選ぶ）】
・「誇張した驚き顔」: 口をあんぐり開けて目を最大限に見開いた驚き
・「最高潮の笑顔」: ほっぺがぷくっと膨らみ目が細くなるくらいの全力の笑顔
・「コミカルな困り顔」: 眉をハの字にして口をとがらせた愛らしい表情
いずれも「思わずスクリーンショットしたくなる」誇張された豊かな表情にすること

【ポーズ・動き】
・両手を広げてガッツポーズ・踊っている・ジャンプしている雰囲気
・体全体から「かわいすぎてDMしたくなる」エネルギーを出す

【GPT Image 2向け：撮影スタイル】
・スタイル：Photorealistic studio photography, vibrant and colorful, playful and energetic
・カメラ：Shot with 85mm portrait lens, dynamic slightly tilted angle
・照明：Bright and vivid studio lighting, colorful and cheerful
・構図：Medium shot to close-up, 1:1 square format

【せなっちのキャラクター補足（参照画像1に加えて守る）】
・生後{MONTH_AGE}ヶ月の日本人男の子
・白いリボンカチューシャ（細いサテンリボン）
・月齢({MONTH_AGE}ヶ月)に合った声のイメージ：{sounds}

【背景・雰囲気】
・背景：明るいカラフルな単色背景（黄色・水色・白など）
・全体的に明るく・カラフル・楽しくてシェアしたくなる世界観
・No text, no logos
"""


def generate_image_prompt(product: dict) -> str:
    """
    【楽天ROOM用】文字あり画像プロンプト（英語）
    手書き風テキスト3フレーズを画面に追加。
    保存ファイル名: YYYYMMDD.png
    """
    product_short = product['name'][:20]
    prompt = _base_image_prompt_text(product) + f"""
【手書き風テキスト 3フレーズ（必須）】
商品「{product_short}」に合わせて、白い細い手書き風ペンで以下の3つを画面の端・隅に配置する：
  1. 商品への感動コメント（「{product_short}最高すぎた！」のようなスタイル / 8〜12文字の日本語）
  2. ブランド名または商品の種類名（4〜8文字 / やや小さめのサイズ）
  3. 必要性を訴えるフレーズ（「これないと困る」「神育児グッズ」「買って大正解」など / 7〜10文字）

各テキストは角度・サイズを少しずつ変えてナチュラルな手書き感を出す。
No watermarks, no logos, no brand logos.

【出力仕様（プロンプト末尾に必ず明記）】
Output format: PNG / Size: 1024×1024 (square, 1:1) / File size: under 2097152 bytes (2MB)

英語のプロンプトのみ出力してください。前置き不要。
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def generate_image_prompt_notxt(product: dict) -> str:
    """
    【動画用・通常mode】文字なし画像プロンプト（英語）
    InsMindに読み込む素材画像として使用。
    保存ファイル名: YYYYMMDD_video.png
    """
    prompt = _base_image_prompt_text(product) + """
【テキスト（InsMind動画用・文字なし版）】
・テキスト・文字・手書き文字は一切入れない
・No text, no handwriting, no captions, no watermarks, no logos, no overlays of any kind
・純粋な写真のみ

【出力仕様（プロンプト末尾に必ず明記）】
Output format: PNG / Size: 1024×1024 (square, 1:1) / File size: under 2097152 bytes (2MB)

英語のプロンプトのみ出力してください。前置き不要。
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def generate_image_prompt_notxt_buzz() -> str:
    """
    【動画用・バズmode】文字なし画像プロンプト（英語）
    せなっちが踊っている・ふざけているシーン。
    保存ファイル名: YYYYMMDD_buzz.png
    """
    prompt = _base_scene_text_buzz() + """
【テキスト（InsMind動画用・文字なし版）】
・テキスト・文字・手書き文字は一切入れない
・No text, no handwriting, no captions, no watermarks, no logos, no overlays of any kind
・純粋な写真のみ

【出力仕様（プロンプト末尾に必ず明記）】
Output format: PNG / Size: 1024×1024 (square, 1:1) / File size: under 2097152 bytes (2MB)

英語のプロンプトのみ出力してください。前置き不要。
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def generate_insmind_prompt(product: dict) -> str:
    """
    【通常mode】InsMind（Image to Video）用動画プロンプト（英語1段落）
    月齢に合った声・動きで15秒バイラル動画を生成。
    """
    age_group = _get_age_group(MONTH_AGE)
    age_info = INSMIND_BY_AGE_GROUP.get(age_group, INSMIND_BY_AGE_GROUP["4-5"])
    primary_sound = age_info["sounds"][0]
    motion_en = age_info["motion_en"]
    mood_en = age_info["mood_en"]

    prompt = f"""
せなっち（生後{MONTH_AGE}ヶ月）が商品「{product['name'][:40]}」を着ている・使っている静止画を
InsMind（Image to Video）でInstagramリール バイラル動画にするプロンプトを英語で作成してください。

【バイラルコンセプト】
・せなっちが商品を着ている・使っている状態で月齢に合った自然な動きをする
・主な動き：{motion_en}
・月齢({MONTH_AGE}ヶ月)の声のイメージ："{primary_sound}"
・「かわいすぎ」「これ何使ってるの？」と思わずコメントしたくなる構成
・動画が自然にループする構成（最後のフレームが最初につながる）

【InsMindプロンプトのルール】
・外見の詳細描写は不要（入力画像から取得するため）
・「動き・カメラ・雰囲気」のみを50〜80語程度で簡潔に記述
・Negative Promptは不要
・箇条書き不要・1段落で出力

【カメラワーク・雰囲気】
・カメラ：slow gentle zoom in then slowly pull back（自然ループ用）
・全体的な雰囲気：{mood_en}, warm, cozy, natural

英語のプロンプト（1段落）のみ出力してください。前置き・見出し不要。
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    result = message.content[0].text.strip()
    if result.startswith("```"):
        result = "\n".join(result.split("\n")[1:])
    if result.endswith("```"):
        result = "\n".join(result.split("\n")[:-1])
    return result.strip()


def generate_insmind_prompt_buzz() -> str:
    """
    【バズmode】InsMind（Image to Video）用ダンス動画プロンプト（英語1段落）
    せなっちが踊っている・ふざけているコミカルな動画。
    """
    buzz_age_group = _get_buzz_age_group(MONTH_AGE)
    motion_en = BUZZ_MOTION_BY_AGE_GROUP.get(buzz_age_group, BUZZ_MOTION_BY_AGE_GROUP["0-6"])
    age_group = _get_age_group(MONTH_AGE)
    age_info = INSMIND_BY_AGE_GROUP.get(age_group, INSMIND_BY_AGE_GROUP["4-5"])
    primary_sound = age_info["sounds"][0]

    prompt = f"""
せなっち（生後{MONTH_AGE}ヶ月）の静止画を
InsMind（Image to Video）でバイラル ダンス動画にするプロンプトを英語で作成してください。

【バズコンセプト：思わずシェアしたくなるコミカルな動き】
・主な動き：{motion_en}
・月齢({MONTH_AGE}ヶ月)の声のイメージ："{primary_sound}"
・「かわいすぎて笑える」「友達に送りたい」という感情を引き出す
・リズミカルで楽しい動き・明るいテンポ

【InsMindプロンプトのルール】
・外見の詳細描写は不要（入力画像から取得するため）
・「動き・カメラ・雰囲気」のみを50〜80語程度で簡潔に記述
・Negative Promptは不要
・箇条書き不要・1段落で出力

【カメラワーク・雰囲気】
・カメラ：dynamic, slightly bouncy camera movement matching the energy
・全体的な雰囲気：fun, playful, comedic, bright and cheerful

英語のプロンプト（1段落）のみ出力してください。前置き・見出し不要。
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    result = message.content[0].text.strip()
    if result.startswith("```"):
        result = "\n".join(result.split("\n")[1:])
    if result.endswith("```"):
        result = "\n".join(result.split("\n")[:-1])
    return result.strip()


def run(products: list) -> list:
    """通常mode：商品ありの画像・動画プロンプトを生成して返す"""
    print("画像・動画プロンプト生成エージェント 起動")
    results = []
    for i, product in enumerate(products):
        print(f"  [{i+1}/{len(products)}] {product['name'][:40]}")
        product["gpt_image_prompt"]       = generate_image_prompt(product)
        product["gpt_image_prompt_notxt"] = generate_image_prompt_notxt(product)
        product["video_prompt"]           = generate_insmind_prompt(product)
        results.append(product)
        print("    ✅ プロンプト生成完了")
    print(f"\n✅ {len(results)} 件のプロンプトを生成しました")
    return results


def run_buzz() -> dict:
    """バズmode：商品なしのダンス画像・動画プロンプトを生成して返す"""
    print("画像・動画プロンプト生成エージェント 起動（バズmode）")
    result = {
        "name": f"バズmode - せなっち生後{MONTH_AGE}ヶ月",
        "price": 0,
        "url": "",
        "affiliate_url": "",
        "item_code": "",
        "gpt_image_prompt": "",
        "gpt_image_prompt_notxt": generate_image_prompt_notxt_buzz(),
        "video_prompt": generate_insmind_prompt_buzz(),
        "room_description": "",
        "score": 0,
        "is_buzz_mode": True,
    }
    print("  ✅ バズmodeプロンプト生成完了")
    return result
