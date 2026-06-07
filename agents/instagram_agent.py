"""
Instagramエージェント（一体型）
DMシェアを最大化するReelスクリプト＋Instagramキャプションを生成。
スクリプトとキャプションを別APIコールに分離して安定性を確保。
"""
import anthropic
import os
import json
import random
from datetime import date
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

from utils.baby_config import BIRTH_DATE, calc_month_age, calc_weeks_alive, calc_week_in_month
FIXED_TAGS     = ["#babyboo", "#baby", "#PR", "#育児", "#赤ちゃんのいる生活"]
FIXED_TAGS_STR = " ".join(FIXED_TAGS)
BUZZ_TAGS      = ["#babyboo", "#baby", "#育児", "#赤ちゃんのいる生活"]   # #PR なし
BUZZ_TAGS_STR  = " ".join(BUZZ_TAGS)
TIKTOK_FIXED_TAGS = ["#赤ちゃん", "#育児vlog", "#babyboo", "#赤ちゃんのいる暮らし", "#育休パパ"]
TIKTOK_FIXED_TAGS_STR = " ".join(TIKTOK_FIXED_TAGS)

# バズmode Instagram専用（海外向け・baby_cuboスタイル）
BUZZ_IG_HASHTAGS = "#baby #babyboo #babylove #cutebaby #kawaii"
BUZZ_IG_ONELINER_POOL = [
    "Kawaii is a Japanese dad's first language. 🍼✨",
    "In Japan, we call it kawaii. 🇯🇵💕",
    "No translation needed. Just kawaii. 🇯🇵✨",
    "Pure kawaii, straight from Japan. 🇯🇵🍼",
    "Warning: extreme kawaii from Japan. 🇯🇵✨",
    "Japanese babies hit different. 🇯🇵💕",
    "Kawaii unlocked. 🔓🍼",
    "Made in Japan. Maximum kawaii. 🇯🇵✨",
    "Japan's secret: everything is more kawaii here. 🍼💕",
    "Kawaii has no translation. It just is. 🇯🇵🍼",
]

BABY_SPEECH_BY_MONTH = {
    0:  {"sounds": ["おぎゃー", "ふにゃー"], "desc": "泣き声のみ"},
    1:  {"sounds": ["あー", "うー"], "desc": "クーイング"},
    2:  {"sounds": ["あーうー", "えへへ"], "desc": "クーイング＋笑い声"},
    3:  {"sounds": ["あははっ", "きゃっ", "うふー"], "desc": "笑い声・喜び声"},
    4:  {"sounds": ["あーっ！", "えへへ", "んー？", "きゃっ"], "desc": "クーイング・笑い声・驚き"},
    5:  {"sounds": ["ままま", "ばばば", "あっあっ"], "desc": "喃語開始"},
    6:  {"sounds": ["まーまー", "ぱーぱー", "んまー"], "desc": "喃語が増える"},
    7:  {"sounds": ["あーあー", "まんまー", "ぱっぱー"], "desc": "意味のある喃語"},
    8:  {"sounds": ["まんまー", "ねーね", "うー！"], "desc": "食べ物・眠気の喃語"},
    9:  {"sounds": ["まんまー！", "ぱっぱー", "やー！"], "desc": "喃語＋指差し声"},
    10: {"sounds": ["ママ", "パパ", "まんま"], "desc": "初語デビュー！"},
    11: {"sounds": ["ママ！", "パパ！", "まんまー！"], "desc": "初語が明確に"},
    12: {"sounds": ["ママ", "パパ", "わんわん", "ねんね"], "desc": "語彙が増える"},
    13: {"sounds": ["ねんね", "だっこ", "いやー"], "desc": "要求語が出る"},
    14: {"sounds": ["あっち！", "これ？", "もっと！"], "desc": "指差し＋要求語"},
    15: {"sounds": ["ママ きて", "もっと！", "いやいや"], "desc": "二語文に向かう"},
}


MONTH_AGE = calc_month_age()


def _parse_json(text: str) -> dict:
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(text)
    except Exception:
        return {}


def _generate_script(product_name: str, catch_copy: str, sounds_str: str, speech_desc: str) -> dict:
    """スクリプト（hook / drama_format / dm_trigger / viral_concept / bgm_style）を生成"""
    prompt = f"""
あなたはInstagramバイラルリール動画のコンテンツ戦略家です。
2026年アルゴリズム最重要指標「DMシェア」を最大化するコンテンツを設計してください。

【DMシェアを生む3条件（全て含める）】
① 共感：「うちだけじゃなかった」
② 驚き：「え、そうなの？」
③ 有益：「保存しとこう」

【せなっち情報】生後{MONTH_AGE}ヶ月 / 発声：{speech_desc} / 声：{sounds_str}
【商品】{product_name} / {catch_copy}

【8秒構成】0〜2秒:Hook / 2〜6秒:問題提起+解決+リアクション / 6〜8秒:CTA+ループ設計

JSONのみ出力。前置き不要。
{{
  "title": "20字以内の内部管理タイトル",
  "hook": "冒頭0〜2秒のセリフ・映像指示",
  "drama_format": "起承転結（2〜3文）",
  "dm_trigger": "DMシェアを誘う感情設計",
  "viral_concept": "バイラルコンセプト詳細（3〜4文）",
  "bgm_style": "BGMの雰囲気"
}}
"""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse_json(msg.content[0].text.strip())


def _generate_instagram_caption(script: dict, product_name: str) -> str:
    """Instagram通常mode: バイリンガルキャプション（英語メイン + 日本語商品説明）"""
    prompt = f"""
You are a bilingual Instagram creator — a Japanese dad on parental leave with a {MONTH_AGE}-month-old baby.
Write a bilingual Instagram Reel caption for a product review post.

Video concept: {script.get('viral_concept', '')}
Hook: {script.get('hook', '')}
Product: {product_name}

STRUCTURE (follow this exact order):

[ENGLISH SECTION — 2-3 lines]
- Lead with the baby reaction or product benefit (emotional, punchy)
- End with a CTA: "Comment 🥺 if you want to know more!" or "Save this for your baby list! 🙌"

[blank line]

[JAPANESE SECTION — starting with 🇯🇵]
- Opening: 「🇯🇵 生後{MONTH_AGE}ヶ月のせなっちに[商品名]を使ってみました！」
- 1-2 sentences of honest product explanation in Japanese (what it does, baby's reaction)
- Last line: 「プロフのROOMからチェックできます！」

[blank line]

{FIXED_TAGS_STR}

RULES:
- English section: punchy, emotional, 2-3 lines max
- Japanese section: conversational tone (口語体, ですます禁止)
- Do NOT translate the English — Japanese section is an original product explanation

Output caption text only. No preamble.
"""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


def _generate_buzz_script() -> dict:
    """バズmode：商品なしのReelスクリプトを生成"""
    speech_info = BABY_SPEECH_BY_MONTH.get(MONTH_AGE, BABY_SPEECH_BY_MONTH[4])
    sounds_str = "・".join(speech_info["sounds"])
    speech_desc = speech_info["desc"]

    prompt = f"""
あなたはInstagramバイラルリール動画のコンテンツ戦略家です。
商品紹介ではなく「フォロワー獲得・バズ」に特化したコンテンツを設計してください。

【バズの核心】「かわいすぎてDMした」「友達に見せたい」感情
【せなっち情報】生後{MONTH_AGE}ヶ月 / {speech_desc} / {sounds_str}
【8秒構成】0〜2秒:Hook / 2〜6秒:せなっちのリアルな瞬間 / 6〜8秒:余韻+ループ設計

JSONのみ出力。前置き不要。
{{
  "title": "20字以内の内部管理タイトル",
  "hook": "冒頭0〜2秒の映像指示",
  "drama_format": "動画の流れ（2〜3文）",
  "dm_trigger": "DMシェアを誘う感情設計",
  "viral_concept": "バイラルコンセプト詳細（3〜4文）",
  "bgm_style": "BGMの雰囲気"
}}
"""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse_json(msg.content[0].text.strip())


def _visual_context_line(script: dict) -> str:
    """動画の視覚的内容を日本語で説明する行を返す（キャプション生成用）"""
    vc = script.get("visual_context", "")
    if not vc:
        return ""
    return f"""
【動画の内容（最優先・必ずこれに合ったキャプションを書く）】
{vc}
→ 上記の動画シーンを見た人が「かわいい」「この顔！」と感じる表現にすること。
→ 気分・トーンはこの動画内容に合わせて自然に決める。
"""


def _generate_buzz_caption_pattern_a(script: dict) -> str:
    """バズmodeパターンA：育児あるある悩み＋開き直り絵文字（ダンス・コミカル系）"""
    viral_concept = script.get("viral_concept") or script.get("drama_format") or ""
    mood = script.get("mood_context", "")
    mood_line = f"今日のパパの気分：{mood}（この気分を文章の軸にすること）" if mood else ""
    visual_line = _visual_context_line(script)

    prompt = f"""
育休中のパパとして、生後{MONTH_AGE}ヶ月の育児あるあるの「悩み・愚痴」を1〜2行で書いてください。
{visual_line}
【月齢に合わせた悩みの例】
・生後0〜2ヶ月：寝てくれない、昼夜逆転
・生後3〜4ヶ月：やっと寝かしつけたのにすぐ起きる
・生後5ヶ月：離乳食を全部吐き出す、ずり這いで目が離せない
・生後{MONTH_AGE}ヶ月ならではのリアルな悩みを自然に
{mood_line}

動画のコンセプト（参考）：{viral_concept}

【ルール】
・本文は1〜2行・60〜90字（Reelsは短く読ませる）
・開き直り・諦め絵文字を1〜2個（😇🤷‍♂️😅🫠😮‍💨から選ぶ）
・口語体（ですます禁止）
・1行目に悩み、2行目に開き直りオチ（「もう踊るしかない」など）
・3行目に次回予告または共感の問いかけを必ず1行追加
  例A：「来週また報告します😮‍💨」「同じ経験ある人コメントで教えて！」「育児ってこんなもんだよね😇」
・商品紹介なし
・ハッシュタグは合計5つのみ。次の4つは固定で必ず末尾に含める：{BUZZ_TAGS_STR}
・残り1つは動画の内容に最も合うハッシュタグをあなたが選ぶ（例：#夜泣き #寝かしつけ #育休パパ など）
・ハッシュタグは5つを超えないこと

キャプションテキストのみ出力。前置き不要。
"""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=350,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


def _generate_buzz_caption_pattern_b(script: dict) -> str:
    """バズmodeパターンB：パパのアメリカンジョーク形式（超かわいい系）"""
    viral_concept = script.get("viral_concept") or script.get("drama_format") or ""
    mood = script.get("mood_context", "")
    mood_line = f"今日のパパの気分：{mood}（この気分をジョークの前振りや落差に活かすこと）" if mood else ""
    visual_line = _visual_context_line(script)

    prompt = f"""
育休中のパパとして、アメリカンジョーク風のInstagramキャプションを書いてください。
{visual_line}
{mood_line}

【形式】「パパ今日〇〇した。でもせなっちは〇〇だった。」という落差が笑えるオチ形式
例：
・「パパ今日昇進した。せなっちに報告したら完全無視された。」
・「今日から新プロジェクトのリーダーになった。でも夜泣き係は昇進なし。」
・「パパ今日プレゼン大成功した。帰宅したらせなっちにうんちをかけられた。」

動画のコンセプト（参考）：{viral_concept}

【ルール】
・本文は1〜2行・60〜90字（Reelsは短く読ませる）
・絵文字1〜2個（😂🥲😭笑い・涙系）
・口語体（ですます禁止）
・1行目にパパのニュース、2行目にせなっちのオチ（落差が笑いポイント）
・「（別に〇〇はしていません）」の自虐ツッコミを1行追加
・その後にフォロー誘導または次回予告を1行追加
  例B：「次回も格差ネタ続きます😂」「フォローして見守ってください🥹」「また騙されに来てね😂」
・商品紹介なし
・ハッシュタグは合計5つのみ。次の4つは固定で必ず末尾に含める：{BUZZ_TAGS_STR}
・残り1つは動画の内容に最も合うハッシュタグをあなたが選ぶ（例：#育休パパ #パパ #育児vlog など）
・ハッシュタグは5つを超えないこと

キャプションテキストのみ出力。前置き不要。
"""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


def _generate_buzz_caption_pattern_c(script: dict) -> str:
    """バズmodeパターンC：せなっちのかわいさ全振り（「かわいい」コメント誘発）"""
    viral_concept = script.get("viral_concept") or script.get("drama_format") or ""
    visual_line = _visual_context_line(script)

    prompt = f"""
あなたは生後{MONTH_AGE}ヶ月の赤ちゃん「せなっち」を育てる育休中のパパです。

「見た人が思わず😭🥺💕とだけコメントしてしまう」Instagramキャプションを書いてください。
{visual_line}
動画のコンセプト（参考）：{viral_concept}

【このキャプションの目的】
・視聴者に「かわいい」「泣いた」「癒された」という感情を引き出す
・コメントしやすくするために絵文字だけで返せる内容にする
・パパの育児苦労ではなく、せなっちそのものの可愛さにフォーカス

【ルール】
・本文は1〜2行・40〜70字（短く感情的に）
・冒頭に感情爆発ワードを入れる
  例：「この顔で全部許せる」「存在が罪」「かわいすぎて無理」「見るたびに時間止まれって思う」
・絵文字は😭🥺💕🍼👶から1〜2個のみ
・口語体（ですます禁止）
・本文の後に必ず1行：「かわいいと思ったら絵文字だけでいいからコメントして😭」
・ハッシュタグは合計5つのみ。次の4つは固定で必ず末尾に含める：{BUZZ_TAGS_STR}
・残り1つはかわいさ・月齢に合うタグを選ぶ（例：#生後5ヶ月 #newborn #かわいい赤ちゃん）

キャプションテキストのみ出力。前置き不要。
"""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


def _generate_milestone_instagram_caption(script: dict) -> str:
    """マイルストーン用Instagramキャプション（週1成長記録）"""
    weeks_alive = calc_weeks_alive()
    week_in_month = calc_week_in_month()
    speech_info = BABY_SPEECH_BY_MONTH.get(MONTH_AGE, BABY_SPEECH_BY_MONTH[4])

    prompt = f"""
あなたは生後{MONTH_AGE}ヶ月の赤ちゃん「せなっち」を育てる育休中のパパです。

「今週の成長記録」Instagramキャプションを書いてください。

【せなっち情報】
・生後{MONTH_AGE}ヶ月（生まれてから{weeks_alive}週目）
・今月第{week_in_month}週
・この月齢の発声：{speech_info['desc']}（{' / '.join(speech_info['sounds'])}）

【ルール】
・冒頭に「生後{MONTH_AGE}ヶ月{week_in_month}週目🍼」を入れる
・今週できるようになったことや変化を2〜3点（月齢{MONTH_AGE}ヶ月らしい具体的な内容）
・感動・驚きの感情を1行
・最後に「同じ月齢のパパママ、コメントで教えて！」
・絵文字は2〜3個
・ハッシュタグは合計5つのみ。次の4つは固定：{BUZZ_TAGS_STR}
・残り1つは月齢タグ（例：#生後{MONTH_AGE}ヶ月）

キャプションテキストのみ出力。前置き不要。
"""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=350,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


def _generate_milestone_tiktok_caption() -> str:
    """マイルストーン用TikTokキャプション（週1成長記録）"""
    week_in_month = calc_week_in_month()
    return (
        f"生後{MONTH_AGE}ヶ月{week_in_month}週目の成長記録👶\n"
        f"同じ月齢の子いたらコメントして！\n"
        f"#赤ちゃん #育児vlog #babyboo #赤ちゃんのいる暮らし #生後{MONTH_AGE}ヶ月"
    )


def _generate_buzz_instagram_caption(script: dict, mood: str = "", is_milestone: bool = False) -> str:
    """バズmode用Instagramキャプション（baby_cuboスタイル・海外向け）
    英語一言（kawaii + 日本パパ視点）+ 固定5ハッシュタグのシンプル構成。
    """
    if is_milestone:
        script["buzz_caption_pattern"] = "milestone"
        return _generate_milestone_instagram_caption(script)

    oneliner = random.choice(BUZZ_IG_ONELINER_POOL)
    script["buzz_caption_pattern"] = "kawaii_en"
    return f"{oneliner}\n{BUZZ_IG_HASHTAGS}"


def _generate_tiktok_caption(script: dict, product_name: str = "", is_buzz: bool = False) -> str:
    """TikTok専用キャプション生成
    ・冒頭30文字にキーワードを集中（アルゴリズム対策）
    ・短め本文（1〜2行）＋固定ハッシュタグ5個
    """
    concept = script.get("viral_concept", "") or script.get("drama_format", "")
    hook = script.get("hook", "")
    product_line = f"商品：{product_name}" if product_name else "商品紹介なし（バズ系コンテンツ）"

    prompt = f"""
あなたは生後{MONTH_AGE}ヶ月の赤ちゃん「せなっち」を育てる育休中のパパです。
TikTok用のキャプションを書いてください。

動画のコンセプト：{concept}
フック：{hook}
{product_line}

【TikTokキャプションのルール】
・1行目（冒頭30文字以内）に必ずキーワードを入れる
  例：「生後{MONTH_AGE}ヶ月の赤ちゃんが〇〇した瞬間」「AIで生み出した赤ちゃんが〇〇」
・本文は1〜2行・40〜60字（短く読ませる）
・絵文字1〜2個
・口語体（ですます禁止）
・本文の最後に必ず次のどちらかを入れる（かわいい動画の場合は①を優先）
  ①「かわいいと思ったらコメントして🥺」
  ②「同じ経験ある人？💬」「フォローして見守ってね🍼」
・末尾に必ず次の5つのハッシュタグを全て入れる（追加・変更禁止）：{TIKTOK_FIXED_TAGS_STR}

キャプションテキストのみ出力。前置き不要。
"""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


def run(product: dict) -> dict:
    """通常mode：商品あり Reel スクリプト＋Instagram・TikTokキャプションを生成"""
    global MONTH_AGE
    MONTH_AGE = calc_month_age()
    speech_info = BABY_SPEECH_BY_MONTH.get(MONTH_AGE, BABY_SPEECH_BY_MONTH[4])
    sounds_str = "・".join(speech_info["sounds"])
    speech_desc = speech_info["desc"]

    script = _generate_script(
        product_name=product["name"],
        catch_copy=product.get("catch_copy", ""),
        sounds_str=sounds_str,
        speech_desc=speech_desc,
    )
    script["type"] = "reel"
    caption_ig = _generate_instagram_caption(script, product["name"])
    caption_tt = _generate_tiktok_caption(script, product_name=product["name"])
    script["captions"] = {"instagram": caption_ig, "tiktok": caption_tt}
    return script


def _generate_seasonal_instagram_caption(event: dict) -> str:
    """イベント専用 Instagram キャプションを生成する"""
    hashtags = event.get("hashtags", f"#babyboo #赤ちゃんのいる生活 #育児")
    prompt = f"""
育休中のパパとして、{event['emoji']}「{event['label']}」の特別なInstagramキャプションを書いてください。

【せなっち情報】生後{MONTH_AGE}ヶ月

【テーマ・雰囲気】
{event['caption_theme'].format(age=MONTH_AGE)}

【使いたいキーワード（すべて使わなくてもOK）】
{event['caption_keywords'].format(age=MONTH_AGE)}

【ルール】
・本文は60〜100字（短く感情的に）
・口語体（ですます禁止）
・感情を先に出す（「かわいすぎた」「泣きそう」など）
・絵文字は1〜2個のみ
・最後に共感の問いかけまたは感謝の一言を入れる
・ハッシュタグは必ず最後に: {hashtags}

キャプションテキストのみ出力。前置き不要。
"""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


def _generate_seasonal_tiktok_caption(event: dict) -> str:
    """イベント専用 TikTok キャプションを生成する"""
    hashtags = event.get("hashtags", f"#babyboo #赤ちゃんのいる生活 #育児").replace("#babyboo", "#赤ちゃん").replace("#赤ちゃんのいる生活", "#育児vlog")
    prompt = f"""
育休中のパパとして、{event['emoji']}「{event['label']}」のTikTok向けキャプションを書いてください。

【せなっち情報】生後{MONTH_AGE}ヶ月

【テーマ】{event['caption_theme'].format(age=MONTH_AGE)}

【ルール】
・冒頭に月齢と感情を入れる（例：「生後{MONTH_AGE}ヶ月の{event['label']}が可愛すぎた」）
・本文40〜60字（TikTokは超短く）
・最後に「コメントして」または「フォローして」を自然に入れる
・ハッシュタグ5つのみ: {hashtags}

キャプションテキストのみ出力。前置き不要。
"""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


def run_buzz(mood: str = "", event: dict = None, is_milestone: bool = False, buzz_post: dict = None) -> dict:
    """バズmode：商品なし Reel スクリプト＋Instagram・TikTokキャプションを生成
    event が渡された場合はイベント専用キャプション。
    is_milestone が True の場合は週1成長記録キャプション。
    buzz_post が渡された場合は動画の視覚的内容をキャプションに反映する。
    """
    global MONTH_AGE, BUZZ_TAGS_STR, TIKTOK_FIXED_TAGS_STR
    MONTH_AGE = calc_month_age()
    try:
        from utils.sheets_helper import get_hashtags
        _ig = get_hashtags("instagram_buzz")
        if _ig:
            BUZZ_TAGS_STR = " ".join(_ig)
        _tt = get_hashtags("tiktok")
        if _tt:
            TIKTOK_FIXED_TAGS_STR = " ".join(_tt)
    except Exception:
        pass
    script = _generate_buzz_script()
    if not script.get("hook"):
        script["hook"] = f"生後{MONTH_AGE}ヶ月のせなっちが可愛すぎた瞬間"
    if not script.get("viral_concept"):
        script["viral_concept"] = f"生後{MONTH_AGE}ヶ月のAIベビー「せなっち」のリアルな育児日常"
    script["type"] = "reel"
    script["is_milestone"] = is_milestone

    # 動画の視覚的内容をscriptに格納（キャプション生成で使用）
    if buzz_post:
        vp = buzz_post.get("video_prompt", "")
        if "Positive Prompt:" in vp:
            visual_context = vp.split("Positive Prompt:")[-1].split("Negative Prompt:")[0].strip()
        else:
            visual_context = vp[:400]
        script["visual_context"] = visual_context

    if event:
        caption_ig = _generate_seasonal_instagram_caption(event)
        try:
            caption_tt = _generate_seasonal_tiktok_caption(event)
        except Exception:
            caption_tt = f"生後{MONTH_AGE}ヶ月の{event['label']}😭 {event.get('hashtags', TIKTOK_FIXED_TAGS_STR)}"
    elif is_milestone:
        caption_ig = _generate_milestone_instagram_caption(script)
        caption_tt = _generate_milestone_tiktok_caption()
    else:
        caption_ig = _generate_buzz_instagram_caption(script, mood=mood)
        try:
            caption_tt = _generate_tiktok_caption(script, is_buzz=True)
        except Exception:
            caption_tt = f"生後{MONTH_AGE}ヶ月のせなっち、かわいすぎた😭 {TIKTOK_FIXED_TAGS_STR}"

    script["captions"] = {"instagram": caption_ig, "tiktok": caption_tt}
    return script
