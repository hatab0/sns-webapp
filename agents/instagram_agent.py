"""
Instagramエージェント（一体型）
DMシェアを最大化するReelスクリプト＋Instagramキャプションを一括生成。
2026年アルゴリズム対応：DMシェア > 保存 > コメント > いいね
"""
import anthropic
import os
import json
from datetime import date
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

BIRTH_DATE = date(2025, 12, 22)
FIXED_TAGS = ["#babyboo", "#baby", "#PR", "#育児", "#赤ちゃんのいる生活"]
FIXED_TAGS_STR = " ".join(FIXED_TAGS)

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


def calc_month_age() -> int:
    today = date.today()
    months = (today.year - BIRTH_DATE.year) * 12 + (today.month - BIRTH_DATE.month)
    if today.day < BIRTH_DATE.day:
        months -= 1
    return max(0, months)


MONTH_AGE = calc_month_age()


def _parse_json(text: str) -> dict:
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(text)
    except Exception:
        return {"raw": text}


def run(product: dict) -> dict:
    """
    通常mode：商品あり Reel スクリプト＋Instagramキャプションを一体生成。
    戻り値は buffer_agent と互換の形式。
    """
    speech_info = BABY_SPEECH_BY_MONTH.get(MONTH_AGE, BABY_SPEECH_BY_MONTH[4])
    sounds_str = "・".join(speech_info["sounds"])
    speech_desc = speech_info["desc"]

    prompt = f"""
あなたはInstagramバイラルリール動画のコンテンツ戦略家です。
2026年の最新アルゴリズムに基づき、**DMシェア**を最大化するコンテンツを設計してください。

【DMシェアを生む3条件（必ず全て含める）】
① 共感：「うちだけじゃなかった」と思わせる
② 驚き：「え、そうなの？」と止まらせる
③ 有益：「知らなかった、保存しとこう」と思わせる

【せなっちの月齢情報】
・生後{MONTH_AGE}ヶ月のAIベビーキャラ
・この月齢の発声：{speech_desc}
・月齢に合った声：{sounds_str}

【商品情報（せなっちが実際に着る・使う）】
商品名：{product['name']}
カテゴリ：{product.get('catch_copy', '')}

【15秒動画の構造（必ずこの流れで設計）】
0〜2秒  : Hook（スクロールを止めるフレーム）
2〜6秒  : 問題提起（育児あるある共感パート）
6〜12秒 : 解決＋せなっちのリアクション（商品使用シーン・月齢サウンド）
12〜15秒: CTA（「プロフのROOMへ」）
最後→最初が自然につながるループ設計

【出力形式】JSONのみ。前置き不要。

{{
  "type": "reel",
  "title": "動画タイトル（内部管理用20字以内）",
  "hook": "冒頭0〜2秒のセリフ・映像指示（スクロールを止める一言）",
  "drama_format": "起承転結の構成メモ（2〜3文）",
  "dm_trigger": "DMシェアを誘う設計の根拠（どの感情を刺激するか）",
  "viral_concept": "バイラルコンセプトの詳細（3〜4文。月齢サウンド・商品シーン・ループ設計を含む）",
  "bgm_style": "BGMの雰囲気（例：ほんわか邦楽・ポップなインスト）",
  "caption_instagram": "Instagramキャプション（150〜200字・絵文字2〜3個・口語体・「プロフのROOMから」誘導・末尾に必ず{FIXED_TAGS_STR}）"
}}
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=900,
        messages=[{"role": "user", "content": prompt}]
    )
    result = _parse_json(message.content[0].text.strip())
    result["type"] = "reel"
    caption_ig = result.pop("caption_instagram", "")
    result["captions"] = {"instagram": caption_ig}
    return result


def run_buzz() -> dict:
    """
    バズmode：商品なし。フォロワー獲得に特化したReelスクリプト＋キャプションを生成。
    """
    speech_info = BABY_SPEECH_BY_MONTH.get(MONTH_AGE, BABY_SPEECH_BY_MONTH[4])
    sounds_str = "・".join(speech_info["sounds"])
    speech_desc = speech_info["desc"]

    prompt = f"""
あなたはInstagramバイラルリール動画のコンテンツ戦略家です。
商品紹介ではなく、**フォロワー獲得・バズ**に特化したコンテンツを設計してください。

【バズの核心】
・「かわいすぎてDMした」と思わせる感情トリガー
・「友達に見せたい」と思わせる共感・驚き
・商品の宣伝は一切なし

【せなっちの月齢情報】
・生後{MONTH_AGE}ヶ月のAIベビーキャラ
・この月齢の発声：{speech_desc}
・月齢に合った声：{sounds_str}

【15秒動画の構造】
0〜2秒  : Hook（止まらずにいられない冒頭）
2〜12秒 : せなっちのリアルな瞬間（笑顔・声・仕草）
12〜15秒: 余韻（フォローを自然に促す）

【出力形式】JSONのみ。前置き不要。

{{
  "type": "reel",
  "title": "動画タイトル（内部管理用20字以内）",
  "hook": "冒頭0〜2秒のセリフ・映像指示",
  "drama_format": "動画の流れ（2〜3文）",
  "dm_trigger": "DMシェアを誘う感情設計",
  "viral_concept": "バイラルコンセプトの詳細（3〜4文）",
  "bgm_style": "BGMの雰囲気",
  "caption_instagram": "Instagramキャプション（100〜150字・絵文字2個・バズ狙い・末尾に必ず{FIXED_TAGS_STR}）"
}}
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    result = _parse_json(message.content[0].text.strip())
    result["type"] = "reel"
    caption_ig = result.pop("caption_instagram", "")
    result["captions"] = {"instagram": caption_ig}
    return result
