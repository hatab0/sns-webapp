"""
Instagramエージェント（一体型）
DMシェアを最大化するReelスクリプト＋Instagramキャプションを生成。
スクリプトとキャプションを別APIコールに分離して安定性を確保。
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

【15秒構成】0〜2秒:Hook / 2〜6秒:問題提起 / 6〜12秒:解決+リアクション / 12〜15秒:CTA / ループ設計

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
    """Instagramキャプションをスクリプトと独立して生成（安定性確保）"""
    prompt = f"""
あなたは生後{MONTH_AGE}ヶ月の赤ちゃん「せなっち」を育てる育休中のパパです。
Instagram Reelのキャプションを書いてください。

動画のコンセプト：{script.get('viral_concept', '')}
フック：{script.get('hook', '')}
商品：{product_name}

【ルール】
・150〜200字程度
・絵文字2〜3個
・口語体（「ですます調」禁止）
・「プロフのROOMから」の購入誘導を入れる
・末尾に必ず以下を全て入れる（追加・変更禁止）：{FIXED_TAGS_STR}

キャプションテキストのみ出力。前置き不要。
"""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
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
【15秒構成】0〜2秒:Hook / 2〜12秒:せなっちのリアルな瞬間 / 12〜15秒:余韻

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


def _generate_buzz_instagram_caption(script: dict) -> str:
    """バズmode用Instagramキャプション"""
    prompt = f"""
育休中のパパとして、バズ狙いのInstagram Reelキャプションを書いてください。
動画コンセプト：{script.get('viral_concept', '')}

【ルール】
・100〜150字・絵文字2個・口語体
・商品紹介なし・フォロワー獲得狙い
・末尾に必ず入れる：{FIXED_TAGS_STR}

キャプションテキストのみ出力。前置き不要。
"""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


def run(product: dict) -> dict:
    """通常mode：商品あり Reel スクリプト＋Instagramキャプションを生成"""
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
    script["captions"] = {"instagram": caption_ig}
    return script


def run_buzz() -> dict:
    """バズmode：商品なし Reel スクリプト＋Instagramキャプションを生成"""
    script = _generate_buzz_script()
    script["type"] = "reel"
    caption_ig = _generate_buzz_instagram_caption(script)
    script["captions"] = {"instagram": caption_ig}
    return script
