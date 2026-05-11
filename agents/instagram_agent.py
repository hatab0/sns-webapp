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

BIRTH_DATE = date(2025, 12, 22)
FIXED_TAGS     = ["#babyboo", "#baby", "#PR", "#育児", "#赤ちゃんのいる生活"]
FIXED_TAGS_STR = " ".join(FIXED_TAGS)
BUZZ_TAGS      = ["#babyboo", "#baby", "#育児", "#赤ちゃんのいる生活"]   # #PR なし
BUZZ_TAGS_STR  = " ".join(BUZZ_TAGS)

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


def _generate_buzz_caption_pattern_a(script: dict) -> str:
    """バズmodeパターンA：育児あるある悩み＋開き直り絵文字（ダンス・コミカル系）"""
    viral_concept = script.get("viral_concept") or script.get("drama_format") or ""
    mood = script.get("mood_context", "")
    mood_line = f"今日のパパの気分：{mood}（この気分を文章の軸にすること）" if mood else ""

    prompt = f"""
育休中のパパとして、生後{MONTH_AGE}ヶ月の育児あるあるの「悩み・愚痴」を1〜2行で書いてください。

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
・商品紹介なし
・ハッシュタグは合計5つのみ。次の4つは固定で必ず末尾に含める：{BUZZ_TAGS_STR}
・残り1つは動画の内容に最も合うハッシュタグをあなたが選ぶ（例：#夜泣き #寝かしつけ #育休パパ など）
・ハッシュタグは5つを超えないこと

キャプションテキストのみ出力。前置き不要。
"""
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()


def _generate_buzz_caption_pattern_b(script: dict) -> str:
    """バズmodeパターンB：パパのアメリカンジョーク形式（超かわいい系）"""
    viral_concept = script.get("viral_concept") or script.get("drama_format") or ""
    mood = script.get("mood_context", "")
    mood_line = f"今日のパパの気分：{mood}（この気分をジョークの前振りや落差に活かすこと）" if mood else ""

    prompt = f"""
育休中のパパとして、アメリカンジョーク風のInstagramキャプションを書いてください。
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
・最後に必ず「（別に〇〇はしていません）」の自虐ツッコミを1行追加（例：「（別に昇進はしていません）」「（プレゼンは大失敗でした）」）
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


def _generate_buzz_instagram_caption(script: dict, mood: str = "") -> str:
    """バズmode用Instagramキャプション：気分に応じてパターンA/Bを選択"""
    # 気分 → パターン対応
    mood_a = {"😭 疲れた・眠い", "😤 怒り・ムカつく", "😮‍💨 諦めた（開き直り）"}
    if mood in mood_a:
        pattern = "A"
    elif mood:
        pattern = "B"
    else:
        pattern = random.choice(["A", "B"])
    script["buzz_caption_pattern"] = pattern

    # 気分コンテキストをscriptに追加
    if mood:
        script["mood_context"] = mood

    try:
        if pattern == "A":
            text = _generate_buzz_caption_pattern_a(script)
        else:
            text = _generate_buzz_caption_pattern_b(script)
        if text:
            return text
    except Exception:
        pass

    return f"生後{MONTH_AGE}ヶ月のせなっち、かわいすぎた😭💕 これはフォロー案件じゃない？ {BUZZ_TAGS_STR}"


def run(product: dict) -> dict:
    """通常mode：商品あり Reel スクリプト＋Instagramキャプションを生成"""
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
    script["captions"] = {"instagram": caption_ig}
    return script


def run_buzz(mood: str = "") -> dict:
    """バズmode：商品なし Reel スクリプト＋Instagramキャプションを生成"""
    global MONTH_AGE
    MONTH_AGE = calc_month_age()
    script = _generate_buzz_script()
    script["type"] = "reel"
    caption_ig = _generate_buzz_instagram_caption(script, mood=mood)
    script["captions"] = {"instagram": caption_ig}
    return script
