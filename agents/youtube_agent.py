"""
YouTubeエージェント（一体型）
Instagramスクリプトを受け取りYouTube Shorts専用コンテンツを生成。
2026年アルゴリズム対応：保存率・シェア率・視聴完了率を最大化。
"""
import anthropic
import os
import json
from datetime import date
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

BIRTH_DATE = date(2025, 12, 22)
FIXED_TAGS      = ["#babyboo", "#baby", "#PR", "#育児", "#赤ちゃんのいる生活"]
FIXED_TAGS_STR  = " ".join(FIXED_TAGS)
BUZZ_TAGS       = ["#babyboo", "#baby", "#育児", "#赤ちゃんのいる生活"]   # #PR なし
BUZZ_TAGS_STR   = " ".join(BUZZ_TAGS)


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



def _run_normal(instagram_script: dict, product: dict) -> dict:
    """通常mode：商品紹介YouTube Shortsキャプションを生成"""
    hook = instagram_script.get("hook", "")
    concept = instagram_script.get("viral_concept", "")

    prompt = f"""
あなたはYouTube Shortsの育児チャンネル運営者です。
2026年の最新アルゴリズムに基づき、**検索流入×視聴完了率×保存率**を最大化するコンテンツを生成してください。

【動画情報】
AIベビーキャラ「せなっち」（生後{MONTH_AGE}ヶ月）
フック：{hook}
コンセプト：{concept}
商品：{product["name"]}

【タイトルのルール】
・100文字以内・感情系
・「生後{MONTH_AGE}ヶ月」を必ず入れる
・「〇〇したら△△だった」「〇〇が想像以上だった」形式
・検索キーワード（夜泣き/寝かしつけ/育休パパ/ベビーグッズ）を1つ含める

【説明文のルール】
・3〜5行の自然な文章
・「#Shorts」を必ず入れる
・末尾に全て入れる：{FIXED_TAGS_STR} #Shorts #生後{MONTH_AGE}ヶ月 #育児vlog #ベビーグッズ

【ピン留めコメントのルール】
・「詳細はこちら▼」から始める1〜2行
・商品名を自然に入れる

【出力形式】JSONのみ。前置き不要。

{{
  "title": "YouTubeタイトル（100文字以内）",
  "description": "説明文テキスト（タグ含む）",
  "pin_comment": "ピン留めコメントテキスト"
}}
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse_json(message.content[0].text.strip())


def _run_buzz(instagram_script: dict) -> dict:
    """バズmode：かわいさ・面白さ特化のYouTube Shortsキャプションを生成（#PRなし）"""
    hook = instagram_script.get("hook", "")
    concept = instagram_script.get("viral_concept", "")

    prompt = f"""
あなたはバイラル育児系YouTube Shortsのチャンネル運営者です。
商品紹介ではなく「せなっちのかわいさ・面白さ」でフォロワーを増やすことが目的です。

【動画情報】
AIベビーキャラ「せなっち」（生後{MONTH_AGE}ヶ月）
フック：{hook}
コンセプト：{concept}

【タイトルのルール】
・100文字以内
・「生後{MONTH_AGE}ヶ月」を必ず入れる
・「かわいすぎた」「笑いが止まらない」「奇跡の瞬間」など感情爆発系タイトル
・「〇〇したら△△だった」形式推奨
・検索キーワード（育休パパ/育児vlog/赤ちゃん/かわいい赤ちゃん）を1つ含める
・商品名・ブランド名は一切入れない

【説明文のルール】
・3〜5行の自然な文章（商品紹介なし）
・「#Shorts」を必ず入れる
・末尾に全て入れる：{BUZZ_TAGS_STR} #Shorts #生後{MONTH_AGE}ヶ月 #育児vlog #かわいい赤ちゃん #バズ

【ピン留めコメントのルール】
・「チャンネル登録してね▼」から始める1行
・せなっちへの一言コメントで自然に締める

【出力形式】JSONのみ。前置き不要。

{{
  "title": "YouTubeタイトル（100文字以内）",
  "description": "説明文テキスト（タグ含む）",
  "pin_comment": "ピン留めコメントテキスト"
}}
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return _parse_json(message.content[0].text.strip())


def run(instagram_script: dict, product: dict = None) -> dict:
    """
    Instagramスクリプトを受け取りYouTube Shorts専用コンテンツを生成。
    product=None のときはバズmode（#PRなし・バズ特化キャプション）。
    instagram_script の captions に youtube_title / youtube / pin_comment / threads を追記して返す。
    """
    is_buzz = product is None

    if is_buzz:
        result = _run_buzz(instagram_script)
        default_title = f"生後{MONTH_AGE}ヶ月せなっちが可愛すぎた"
    else:
        result = _run_normal(instagram_script, product)
        default_title = f"生後{MONTH_AGE}ヶ月せなっちの記録"

    instagram_script.setdefault("captions", {})
    instagram_script["captions"]["youtube_title"] = result.get("title", default_title)
    instagram_script["captions"]["youtube"] = result.get("description", "")
    instagram_script["captions"]["pin_comment"] = result.get("pin_comment", "")

    return instagram_script
