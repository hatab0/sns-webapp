"""
画像プロンプト生成エージェント
ChatGPT GPT Image 2用の画像プロンプトと Kling AI動画プロンプトをClaude APIで生成する
"""
import anthropic
import os
import random
from datetime import date
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

BIRTH_DATE = date(2025, 12, 22)

# 毎回ランダムで変わるかわいいアクセサリープール
CUTE_ACCESSORIES = [
    "白いリボンカチューシャ（細いサテンリボン）",
    "ピンクのフリルカチューシャ",
    "くまの耳カチューシャ（ベージュ・もこもこ素材）",
    "うさぎの耳カチューシャ（白・ふわふわ素材）",
    "白いポンポン付きニット帽（ベビーサイズ）",
    "淡いピンクのベレー帽",
    "白いフリル付きスタイ（前掛け）",
    "イチゴ柄のかわいいスタイ",
    "小花のヘアクリップ（白・ピンク）",
    "水色のドット柄スタイとお揃いカチューシャセット",
    "黄色のひよこコスチューム帽子",
    "クリームいろのアニマルニット帽（耳付き）",
]


def calc_month_age() -> int:
    today = date.today()
    months = (today.year - BIRTH_DATE.year) * 12 + (today.month - BIRTH_DATE.month)
    if today.day < BIRTH_DATE.day:
        months -= 1
    return max(0, months)


MONTH_AGE = calc_month_age()

# 月齢グループ別Kling AI動画プロンプト設計
MOTION_BY_AGE_GROUP = {
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

# バズmode：月齢別ダンス動作（Kling AI用）
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

# バズmode：月齢別シーン設定（baby_cubo_official スタイル）
BUZZ_SCENE_BY_AGE = {
    "0-2": {
        "pose": "peacefully sleeping, swaddled snugly in soft muslin, tiny lips slightly parted in a mini yawn",
        "expression": "serene angelic sleeping face, completely relaxed, impossibly tiny and precious",
        "camera": "extreme close-up on face filling 85% of frame, slight overhead angle, very shallow depth of field",
        "lighting": "ultra-soft diffused window light, gentle warm glow, no shadows, skin luminous",
        "background": "blurred soft white or cream fabric, completely clean and minimal",
        "costume_hint": "soft pastel swaddle wrap or tiny newborn knit hat with matching onesie",
    },
    "3": {
        "pose": "lying on back with legs kicking, arms reaching up, caught mid-laugh",
        "expression": "first big gummy smile ever captured — round chubby cheeks, eyes crinkled, pure delight",
        "camera": "close-up face and chest shot, slight low angle looking up at baby, 85mm portrait style",
        "lighting": "soft studio light, warm and flattering, bright catchlights in eyes",
        "background": "soft pastel single-color bokeh (pale pink, mint, or cream)",
        "costume_hint": "animal onesie with hood (bear, bunny, panda) or bright colorful romper",
    },
    "4-5": {
        "pose": "during tummy time lifting head confidently, OR lying back with both arms raised in excitement",
        "expression": "enormous open-mouth laugh, chubby cheeks puffed, bright eyes wide with joy — genuinely candid moment",
        "camera": "EITHER: extreme close-up (face fills frame, eyes are sharpest point) OR medium chest-up shot with slight tilt",
        "lighting": "soft warm studio or window light, prominent catchlights making eyes sparkle",
        "background": "creamy white or soft pastel bokeh, OR simple colorful single-tone background",
        "costume_hint": "character hoodie (dinosaur, frog, animal), fruit/veggie costume, or cute themed romper with matching hat",
    },
    "6-7": {
        "pose": "sitting with slight support, leaning forward curiously, one hand reaching toward camera",
        "expression": "wide-eyed wonder and curiosity, eyebrows raised, mouth slightly open in amazement",
        "camera": "medium shot (head to waist), straight-on or slight low angle to make baby look grand",
        "lighting": "bright soft light, warm tones, clear catchlights",
        "background": "lifestyle setting (soft sofa corner, textured blanket) or clean pastel backdrop",
        "costume_hint": "seasonal outfit, character hooded onesie with animal ears, or stylish mini streetwear set",
    },
    "8-9": {
        "pose": "sitting independently, pointing finger at camera, OR caught mid-babble with expressive hand gesture",
        "expression": "animated personality shining — mid-word babbling face, or conspiratorial smirk",
        "camera": "medium close-up, dynamic slight angle, face as main subject",
        "lighting": "vibrant warm light, sharp eye focus",
        "background": "colorful lifestyle or simple bold-color backdrop",
        "costume_hint": "mini streetwear (tiny cap + matching set), character costume, or vibrant seasonal outfit",
    },
    "10-12": {
        "pose": "pulling to stand holding something, or sitting clapping hands with huge proud expression",
        "expression": "milestone pride — huge beaming smile at achievement, or concentrating hard adorable focus face",
        "camera": "varies: full body to show milestone, OR tight close-up on proud expression",
        "lighting": "bright, celebratory feel",
        "background": "lifestyle setting or clean backdrop",
        "costume_hint": "mini fashion outfit, holiday-themed costume, or character costume",
    },
    "13+": {
        "pose": "toddling with arms out for balance, or caught mid-mischief doing something funny",
        "expression": "mischievous grin, or caught-being-naughty look, or full-body uncontrollable laugh",
        "camera": "full body OR medium to show personality and movement",
        "lighting": "bright, fun, energetic",
        "background": "indoor play setting or colorful backdrop",
        "costume_hint": "toddler fashion, character costume for play, seasonal themed outfit",
    },
}

# バズmode：コスチュームプール（baby_cubo_official スタイル）
BUZZ_COSTUME_POOL = [
    # アニマルフーディー・オールインワン
    "bright green dinosaur hoodie onesie with tiny spikes along the hood",
    "brown teddy bear onesie with round plush ears on hood",
    "black and white panda onesie with panda ear hood",
    "soft yellow duckling costume with orange beak hood",
    "white fluffy bunny onesie with long floppy ears",
    "orange tiger stripe onesie with tiger ear hood",
    "gray elephant hoodie onesie with big floppy ear hood",
    "mint green frog costume with round frog eye hood",
    # 果物・食べ物コスチューム
    "bright red strawberry costume with green leaf hat",
    "yellow pineapple knit hat with matching yellow romper",
    "orange pumpkin round costume (Halloween style)",
    "watermelon themed romper with green ruffles",
    # キャラクター・カジュアル
    "tiny black leather jacket over white onesie (mini biker style)",
    "navy blue baseball cap worn backwards with matching jersey onesie",
    "oversized pastel pink bucket hat with floral print romper",
    "blue star-pattern hooded fleece onesie",
    "cream sherpa bear-ear hooded zip-up suit",
    "red and white striped long-sleeve with tiny jeans (classic baby look)",
    # 季節・イベント
    "Santa Claus mini red suit with white trim and tiny hat",
    "rainbow striped knit sweater with matching booties",
    "Japanese matsuri happi coat in indigo blue with white pattern",
]


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


def _base_image_prompt_text(product: dict, accessory: str = "") -> str:
    """商品あり：画像プロンプトの共通部分（2枚参照画像前提）"""
    acc = accessory or random.choice(CUTE_ACCESSORIES)
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
・アクセサリー：{acc}
・表情：穏やかな笑顔 or 商品に興味を示している顔

【背景・雰囲気】
・背景：クリーム色・アイボリー・ベージュのナチュラルスタジオ
・小物：白いふわふわのブランケット・薄いモスリンガーゼ
・全体的にナチュラル・オーガニック・清潔感のある世界観
"""


def _base_scene_text_buzz() -> str:
    """バズmode：baby_cubo_officialスタイルの月齢特化シーン（参照画像1枚のみ）"""
    age_group = _get_age_group(MONTH_AGE)
    scene = BUZZ_SCENE_BY_AGE.get(age_group, BUZZ_SCENE_BY_AGE["4-5"])
    costume = random.choice(BUZZ_COSTUME_POOL)

    return f"""
ChatGPT GPT Image 2で使用する、高品質な画像生成プロンプトを英語で作成してください。
ターゲットスタイル：Instagram育児バイラルアカウント「baby_cubo_official」のような、
プロ品質のリアル赤ちゃん写真。自然でありながらも思わず保存・シェアしたくなるクオリティ。

【前提：ユーザーから参照画像を1枚送信します】
  参照画像1枚のみ: 赤ちゃん「せなっち」の写真
  → 顔・目・鼻・輪郭・肌色・髪の毛を完全一致させること
  → コスチューム・背景はすべて以下のテキスト指示から生成すること（参照画像2は不要）

【キャラクター設定（必ず守る）】
・日本人の男の子（baby boy）、生後{MONTH_AGE}ヶ月
・ぽっちゃりしたほっぺ、黒髪、丸くてかわいい目
・性別：male baby boy（女の子っぽくならないこと）

【コスチューム（テキストから完全生成）】
{costume}
→ 上記コスチュームを正確に再現すること。月齢に合ったサイズ感で

【生後{MONTH_AGE}ヶ月のポーズ・表情】
ポーズ：{scene['pose']}
表情：{scene['expression']}
→ 「本当に撮れた一瞬」のような自然なリアルさ。過度な誇張は不要

【カメラ・構図】
{scene['camera']}
1:1 square format / 85mm portrait lens / very shallow depth of field (f/1.8)

【照明】
{scene['lighting']}
目に必ず明るいキャッチライト（白い光の点）を入れること

【背景（テキストから完全生成）】
{scene['background']}
背景はシンプルにボケさせて赤ちゃんを際立たせる

【撮影品質（必須）】
・Style: Hyper-realistic professional infant photography, editorial quality
・Skin: Smooth, soft, naturally glowing baby skin — not plastic, not AI-looking
・Eyes: Tack sharp, bright, alive with natural catchlights
・Color: Warm, slightly golden color grade
・No text, no watermarks, no logos, no overlays, no feminine accessories
"""


def generate_image_prompt(product: dict, accessory: str = "") -> str:
    """
    【楽天ROOM用】文字あり画像プロンプト（英語）
    手書き風テキスト3フレーズを画面に追加。
    保存ファイル名: YYYYMMDD.png
    """
    product_short = product['name'][:20]
    prompt = _base_image_prompt_text(product, accessory) + f"""
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


def generate_image_prompt_notxt(product: dict, accessory: str = "") -> str:
    """
    【動画用・通常mode】文字なし画像プロンプト（英語）
    Kling AIに読み込む素材画像として使用。
    保存ファイル名: YYYYMMDD_video.png
    """
    prompt = _base_image_prompt_text(product, accessory) + """
【テキスト（Kling AI動画用・文字なし版）】
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
【テキスト（Kling AI動画用・文字なし版）】
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


def generate_kling_prompt(product: dict) -> str:
    """
    【通常mode】Kling AI（Image to Video）用動画プロンプト（英語）
    月齢に合った動きで15秒バイラル動画を生成。Positive / Negative Prompt形式で出力。
    """
    age_group = _get_age_group(MONTH_AGE)
    age_info = MOTION_BY_AGE_GROUP.get(age_group, MOTION_BY_AGE_GROUP["4-5"])
    primary_sound = age_info["sounds"][0]
    motion_en = age_info["motion_en"]
    mood_en = age_info["mood_en"]

    prompt = f"""
せなっち（生後{MONTH_AGE}ヶ月）が商品「{product['name'][:40]}」を着ている・使っている静止画を
Kling AI（Image to Video）でInstagramリール バイラル動画にするプロンプトを英語で作成してください。

【バイラルコンセプト】
・せなっちが商品を着ている・使っている状態で月齢に合った自然な動きをする
・主な動き：{motion_en}
・月齢({MONTH_AGE}ヶ月)の声のイメージ："{primary_sound}"
・「かわいすぎ」「これ何使ってるの？」と思わずコメントしたくなる構成
・動画が自然にループする構成（最後のフレームが最初につながる）

【Kling AIプロンプトのルール】
・外見の詳細描写は不要（入力画像から取得するため）
・Positive Promptは動き・カメラ・雰囲気を中心に60〜100語で記述
・Negative Promptは「NG要素」を15〜25語で列挙
・箇条書き不要・それぞれ1段落で出力

【カメラワーク・雰囲気】
・カメラ：slow gentle zoom in, then slowly pull back（自然ループ用）
・全体的な雰囲気：{mood_en}, warm, cozy, natural, cinematic

【出力形式】以下の形式のみ。前置き不要。
Positive Prompt:
（英語プロンプト）

Negative Prompt:
（英語NG要素）
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    result = message.content[0].text.strip()
    if result.startswith("```"):
        result = "\n".join(result.split("\n")[1:])
    if result.endswith("```"):
        result = "\n".join(result.split("\n")[:-1])
    return result.strip()


def generate_kling_prompt_buzz() -> str:
    """
    【バズmode】Kling AI（Image to Video）用ダンス動画プロンプト（英語）
    せなっちが踊っている・ふざけているコミカルな動画。Positive / Negative Prompt形式。
    """
    buzz_age_group = _get_buzz_age_group(MONTH_AGE)
    motion_en = BUZZ_MOTION_BY_AGE_GROUP.get(buzz_age_group, BUZZ_MOTION_BY_AGE_GROUP["0-6"])
    age_group = _get_age_group(MONTH_AGE)
    age_info = MOTION_BY_AGE_GROUP.get(age_group, MOTION_BY_AGE_GROUP["4-5"])
    primary_sound = age_info["sounds"][0]

    prompt = f"""
せなっち（生後{MONTH_AGE}ヶ月）のコスチューム姿の静止画を
Kling AI（Image to Video）でバイラル ダンス動画にするプロンプトを英語で作成してください。

【バズコンセプト：思わずシェアしたくなるコミカルな動き】
・主な動き：{motion_en}
・月齢({MONTH_AGE}ヶ月)の声のイメージ："{primary_sound}"
・「かわいすぎて笑える」「友達に送りたい」という感情を引き出す
・リズミカルで楽しい動き・明るいテンポ

【Kling AIプロンプトのルール】
・外見の詳細描写は不要（入力画像から取得するため）
・Positive Promptは動き・カメラ・雰囲気を中心に60〜100語で記述
・Negative Promptは「NG要素」を15〜25語で列挙
・箇条書き不要・それぞれ1段落で出力

【カメラワーク・雰囲気】
・カメラ：dynamic, slightly bouncy camera movement synced to the rhythm
・全体的な雰囲気：fun, playful, comedic, bright, energetic, viral

【出力形式】以下の形式のみ。前置き不要。
Positive Prompt:
（英語プロンプト）

Negative Prompt:
（英語NG要素）
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
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
        acc = random.choice(CUTE_ACCESSORIES)
        print(f"    アクセサリー: {acc}")
        product["gpt_image_prompt"]       = generate_image_prompt(product, accessory=acc)
        product["gpt_image_prompt_notxt"] = generate_image_prompt_notxt(product, accessory=acc)
        product["video_prompt"]           = generate_kling_prompt(product)
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
        "video_prompt": generate_kling_prompt_buzz(),
        "room_description": "",
        "score": 0,
        "is_buzz_mode": True,
    }
    print("  ✅ バズmodeプロンプト生成完了")
    return result
