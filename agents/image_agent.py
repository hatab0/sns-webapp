"""
画像プロンプト生成エージェント
ChatGPT GPT Image 2用の画像プロンプトと InsMind動画プロンプトをClaude APIで生成する
"""
import anthropic
import os
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# せなっちの誕生日（ここだけ変更すれば全プロンプトが自動切り替わる）
BIRTH_DATE = date(2025, 12, 22)


def calc_month_age() -> int:
    """誕生日から現在の月齢を自動計算する"""
    today = date.today()
    months = (today.year - BIRTH_DATE.year) * 12 + (today.month - BIRTH_DATE.month)
    if today.day < BIRTH_DATE.day:
        months -= 1
    return max(0, months)


MONTH_AGE = calc_month_age()

# 月齢別・赤ちゃんの発声マップ
BABY_SPEECH_BY_MONTH = {
    0: {"sounds": ["おぎゃー", "ふにゃー"],           "desc": "泣き声のみ"},
    1: {"sounds": ["あー", "うー"],                   "desc": "クーイング（母音）"},
    2: {"sounds": ["あーうー", "えへへ"],              "desc": "クーイング＋笑い声"},
    3: {"sounds": ["あははっ", "きゃっ", "うふー"],    "desc": "笑い声・喜び声"},
    4: {"sounds": ["あーっ！", "えへへ", "んー？", "きゃっ"], "desc": "クーイング・笑い声・驚き"},
    5: {"sounds": ["ままま", "ばばば", "あっあっ"],    "desc": "喃語（繰り返し音）開始"},
    6: {"sounds": ["まーまー", "ぱーぱー", "んまー"],  "desc": "喃語が増える"},
    7: {"sounds": ["あーあー", "まんまー", "ぱっぱー"], "desc": "意味のある喃語"},
    8: {"sounds": ["まんまー", "ねーね", "うー！"],     "desc": "食べ物・眠気の喃語"},
    9: {"sounds": ["まんまー！", "ぱっぱー", "やー！"], "desc": "喃語＋指差し声"},
    10: {"sounds": ["ママ", "パパ", "まんま"],          "desc": "初語デビュー！"},
    11: {"sounds": ["ママ！", "パパ！", "まんまー！"],  "desc": "初語が明確に"},
    12: {"sounds": ["ママ", "パパ", "わんわん", "ねんね"], "desc": "語彙が増える"},
    13: {"sounds": ["ねんね", "だっこ", "いやー"],      "desc": "要求語が出る"},
    14: {"sounds": ["あっち！", "これ？", "もっと！"],  "desc": "指差し＋要求語"},
    15: {"sounds": ["ママ きて", "もっと！", "いやいや"], "desc": "二語文に向かう"},
}


def _base_image_prompt_text(product: dict) -> str:
    """画像プロンプトの共通部分（2枚参照画像を前提とした構成）"""
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


def generate_image_prompt(product: dict) -> str:
    """
    【楽天ROOM用】文字あり画像プロンプト（英語）
    手書き風テキスト3フレーズを画面に追加。
    ChatGPTに2枚の参照画像（せなっち写真 + 商品写真）を添付して使用。
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
    【InsMind動画用・バイラルリール素材】文字なし画像プロンプト（英語）
    テキストオーバーレイなし。InsMindに読み込む素材画像として使用。
    バイラルコンセプト用：せなっちが月齢に合った声・反応をしている自然な瞬間を捉えた構図。
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


def generate_insmind_prompt(product: dict) -> str:
    """
    InsMind（Image to Video）用バイラルリールプロンプトを生成する（英語）

    バイラルコンセプト：
    - AIベビー「せなっち」が月齢に合った声・音を出しているように見えるショート動画
    - 商品はさりげなく背景や手元に映る（宣伝感ゼロ）
    - 自然にループする動画構成

    InsMindの特性：
    - シンプルで直接的なモーション記述
    - Negative Promptなし
    - 50〜100語程度
    - カメラ動き・雰囲気を簡潔に含める
    """
    speech_info = BABY_SPEECH_BY_MONTH.get(MONTH_AGE, BABY_SPEECH_BY_MONTH[4])
    sounds = speech_info["sounds"]
    motion_sound = sounds[0]
    speech_desc = speech_info["desc"]
    all_sounds = "、".join(sounds)

    prompt = f"""
せなっち（生後{MONTH_AGE}ヶ月）が商品「{product['name'][:40]}」を着ている・使っている静止画を
InsMind（Image to Video）でInstagramリール バイラル動画にするプロンプトを英語で作成してください。

【バイラルコンセプト：@baby_cubo_official スタイル参考】
・自然な赤ちゃんの瞬間を捉えながら、商品がちゃんと映る
・せなっちが商品を着ている・使っている状態で「{motion_sound}」と声を出す瞬間
・生後{MONTH_AGE}ヶ月の発声レベル：{speech_desc}
・月齢に合った声・音：{all_sounds}
・「かわいすぎ」「これ何使ってるの？」と思わずコメントしたくなる構成
・動画が自然にループする構成

【InsMindプロンプトのルール】
・外見の詳細描写は不要（入力画像から取得するため）
・「動き・カメラ・雰囲気・フック」を50〜80語程度で簡潔に記述
・Negative Promptは不要
・箇条書き不要・1段落で出力

【動きのヒント（バイラル要素を必ず含める）】
・冒頭：商品を着ている・使っているせなっちがカメラを見て、ふいに「{motion_sound}」と声を出す瞬間
・商品がカメラにしっかり映った状態で、満面の笑顔になる
・カメラはゆっくりズームイン（slow gentle zoom in）からゆっくり引く（自然ループ用）
・全体的に温かくナチュラルな雰囲気（warm, cozy, natural）
・最後のフレームが最初のフレームとつながるように終わる（ループ設計）

英語のプロンプト（1段落）のみ出力してください。前置き・見出し不要。
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    result = message.content[0].text.strip()
    # コードブロック除去
    if result.startswith("```"):
        result = "\n".join(result.split("\n")[1:])
    if result.endswith("```"):
        result = "\n".join(result.split("\n")[:-1])
    return result.strip()


def run(products: list) -> list:
    """商品の画像・動画プロンプトを生成して返す"""
    print("画像・動画プロンプト生成エージェント 起動")

    results = []
    for i, product in enumerate(products):
        print(f"  [{i+1}/{len(products)}] {product['name'][:40]}")
        product["gpt_image_prompt"] = generate_image_prompt(product)
        product["gpt_image_prompt_notxt"] = generate_image_prompt_notxt(product)
        product["video_prompt"] = generate_insmind_prompt(product)
        results.append(product)
        print(f"    ✅ プロンプト生成完了")

    print(f"\n✅ {len(results)} 件のプロンプトを生成しました")
    return results


# ─────────────────────────────────────────────────────────────────
#  商品なし・コンテンツタイプ別シーンプロンプト（buzz/growth/aruraru）
# ─────────────────────────────────────────────────────────────────

SCENE_BY_MODE = {
    "buzz": {
        "scene": f"生後{MONTH_AGE}ヶ月のせなっちが突然パパを見て声を出して笑った、感動的な日常の一コマ。暖かいナチュラル光の中。",
        "motion": "突然カメラ方向を向いて満面のgummy smileが広がる・手をばたばたさせて全身で喜ぶ・自然でゆっくりした幸せな動き",
        "text_hint": "「初めて笑った😭」「パパだけに見せてくれる笑顔がある」「天使すぎた」",
    },
    "growth": {
        "scene": f"生後{MONTH_AGE}ヶ月のせなっちが腹ばい練習で懸命に頭を持ち上げようとしているチャレンジのシーン。真剣な表情と小さな達成感。",
        "motion": "腹ばいでぐっと頭を持ち上げようとする・顔が少し赤くなりながら頑張る・目がきょろきょろと周りを見渡す・成功した瞬間に笑顔",
        "text_hint": f"「生後{MONTH_AGE}ヶ月、できるようになったこと」「日々成長中」「今しか見れない」",
    },
    "aruraru": {
        "scene": f"生後{MONTH_AGE}ヶ月のせなっちのよだれが止まらず、スタイをつけてもすぐびちょびちょになる育児あるあるな日常シーン。",
        "motion": "よだれがぽたぽた垂れているのに本人は満足そうな表情・手をじーっと見つめるハンドリガード・急に思い出したように泣き出す愛らしい動き",
        "text_hint": "「わかる人いる？笑」「スタイ1日5枚でも足りない」「これが現実」",
    },
}


def _base_scene_text(mode: str) -> str:
    """商品なし・モード別の共通プロンプトベース"""
    scene = SCENE_BY_MODE.get(mode, SCENE_BY_MODE["buzz"])
    return f"""
ChatGPT GPT Image 2で使用する、高品質な画像生成プロンプトを英語で作成してください。

シーン設定：{scene['scene']}

【GPT Image 2向け：撮影スタイルの指定】
・スタイル：Photorealistic studio photography, professional baby lifestyle photo
・カメラ：Shot with 85mm portrait lens, shallow depth of field, soft bokeh background
・照明：Soft diffused studio lighting, warm 3200K color temperature, gentle fill light from left
・構図：Close-up to medium shot, subject centered, 1:1 square format

【被写体（せなっちのキャラクター設定 — 毎回必ず全部記述する）】
・生後{MONTH_AGE}ヶ月の日本人男の子
・黒髪・ふわっとした柔らかい前髪
・大きくて丸い黒目・くりくりした瞳・白目がはっきり
・ぷっくりとしたほっぺ・ふっくらした赤ちゃん体型
・白いリボンカチューシャ（細いサテンリボン）
・白いレースのロンパース（フリル付き）
・表情：シーンに合った自然な表情

【背景・雰囲気】
・背景：クリーム色・アイボリー・ベージュのナチュラルスタジオ
・小物：白いふわふわのブランケット・薄いモスリンガーゼ
・全体的にナチュラル・オーガニック・清潔感のある世界観
"""


def generate_image_prompt_for_mode(mode: str) -> str:
    """【モード別・文字あり版】SNS投稿用 → YYYYMMDD.png"""
    scene = SCENE_BY_MODE.get(mode, SCENE_BY_MODE["buzz"])
    prompt = _base_scene_text(mode) + f"""
【テキスト（SNS投稿用・文字あり版）】
・画面の端に白い細い手書き風ペンで日本語1フレーズ
  （{scene['text_hint']} などシーンに合った感情的な一言）
・No watermarks, no logos, no brand names

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


def generate_image_prompt_notxt_for_mode(mode: str) -> str:
    """【モード別・文字なし版】InsMind動画用 → YYYYMMDD_video.png"""
    prompt = _base_scene_text(mode) + """
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


def generate_insmind_prompt_for_mode(mode: str) -> str:
    """【モード別】InsMind（Image to Video）動画プロンプト"""
    speech_info = BABY_SPEECH_BY_MONTH.get(MONTH_AGE, BABY_SPEECH_BY_MONTH[4])
    motion_sound = speech_info["sounds"][0]
    scene = SCENE_BY_MODE.get(mode, SCENE_BY_MODE["buzz"])

    prompt = f"""
せなっち（生後{MONTH_AGE}ヶ月）の静止画を
InsMind（Image to Video）でInstagramリール動画にするプロンプトを英語で作成してください。

シーン設定：{scene['scene']}

【InsMindプロンプトのルール】
・外見の詳細描写は不要（入力画像から取得するため）
・「動き・カメラ・雰囲気」のみを50〜80語程度で簡潔に記述
・Negative Promptは不要
・箇条書き不要・1段落で出力

【動きのヒント】
・{scene['motion']}
・「{motion_sound}」と声を出しながら自然な表情変化
・カメラはゆっくりズームイン（slow gentle zoom in）
・全体的に温かくナチュラルな雰囲気（warm, cozy, natural）

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


def run_for_mode(mode: str) -> list:
    """商品なし・モード別のプロンプトを生成して output_posts.json 形式で返す"""
    mode_label = {"buzz": "バズ狙い", "growth": "成長記録", "aruraru": "あるある"}.get(mode, mode)
    print(f"  [{mode_label}] 画像・動画プロンプト生成中...")

    result = {
        "rank": 1,
        "name": f"せなっち - {mode_label}",
        "price": 0,
        "url": "",
        "affiliate_url": "",
        "room_description": "",
        "gpt_image_prompt": generate_image_prompt_for_mode(mode),
        "gpt_image_prompt_notxt": generate_image_prompt_notxt_for_mode(mode),
        "video_prompt": generate_insmind_prompt_for_mode(mode),
        "posted": False,
        "posted_at": None,
        "generated_at": datetime.now().isoformat(),
    }
    print(f"  ✅ プロンプト生成完了")
    return [result]
