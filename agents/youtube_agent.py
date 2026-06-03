"""
YouTubeエージェント（一体型）
Instagramスクリプトを受け取りYouTube Shorts専用コンテンツを生成。
2026年アルゴリズム対応：保存率・シェア率・視聴完了率を最大化。
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
FIXED_TAGS      = ["#babyboo", "#baby", "#PR", "#育児", "#赤ちゃんのいる生活"]
FIXED_TAGS_STR  = " ".join(FIXED_TAGS)
BUZZ_TAGS       = ["#babyboo", "#baby", "#育児", "#赤ちゃんのいる生活"]   # #PR なし
BUZZ_TAGS_STR   = " ".join(BUZZ_TAGS)


MONTH_AGE = calc_month_age()

BABY_MILESTONE_BY_MONTH = {
    0:  "生まれたばかり。泣き声と向き合う毎日の生後0ヶ月のせなっちの成長を記録中です。",
    1:  "クーイングが始まった生後1ヶ月のせなっちの成長を記録中です。",
    2:  "笑顔が少しずつ出てきた生後2ヶ月のせなっちの成長を記録中です。",
    3:  "首がすわり始め、笑顔が増えてきた生後3ヶ月のせなっちの成長を記録中です。",
    4:  "首すわり完了、笑顔全開の生後4ヶ月のせなっちの成長を記録中です。",
    5:  "喃語が始まり、ずり這いに挑戦中の生後5ヶ月のせなっちの成長を記録中です。",
    6:  "離乳食スタート！ずり這いも上達してきた生後6ヶ月のせなっちの成長を記録中です。",
    7:  "ハイハイ挑戦中、後追いも始まった生後7ヶ月のせなっちの成長を記録中です。",
    8:  "ハイハイが上手になった生後8ヶ月のせなっちの成長を記録中です。",
    9:  "つかまり立ちを始めた生後9ヶ月のせなっちの成長を記録中です。",
    10: "初語が出てきた！伝い歩きに挑戦中の生後10ヶ月のせなっちの成長を記録中です。",
    11: "伝い歩き上達中、もうすぐ1歳の生後11ヶ月のせなっちの成長を記録中です。",
    12: "1歳を迎えた！歩き始めた生後12ヶ月のせなっちの成長を記録中です。",
    13: "よちよち歩きが上達してきた生後13ヶ月のせなっちの成長を記録中です。",
    14: "言葉が少しずつ出てきた生後14ヶ月のせなっちの成長を記録中です。",
    15: "二語文に向かって成長中の生後15ヶ月のせなっちの成長を記録中です。",
}


def get_fixed_footer() -> str:
    milestone = BABY_MILESTONE_BY_MONTH.get(
        MONTH_AGE,
        f"生後{MONTH_AGE}ヶ月のせなっちの成長を記録中です。"
    )
    return (
        "\n━━━━━━━━━━━━━━━\n"
        "📱 Baby Boo SNS\n"
        "⭐️ Instagram → https://www.instagram.com/aibaby.jp/\n"
        "　　検索用 → @aibaby.jp\n"
        "\n〜Baby Booの説明〜\n"
        "我が子せなっちの成長をAIで作成してリアルタイムに記録する育児日記。\n"
        f"{milestone}\n"
        "夜泣き・寝かしつけ・初めての笑顔…赤ちゃんのリアルな成長をAIで体験してください。\n"
        "育休パパ・育児中のママ・赤ちゃんのいる家庭の方、コメント欄でぜひ交流しましょう！\n"
        "━━━━━━━━━━━━━━━"
    )


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
・50〜70文字（短くコンパクトに）
・「生後{MONTH_AGE}ヶ月」を必ず入れる
・「〇〇したら△△だった」「〇〇が想像以上だった」形式
・検索キーワード（夜泣き/寝かしつけ/育休パパ/ベビーグッズ）を1つ含める
・末尾に「 #Shorts」を必ず付ける

【説明文のルール】
・冒頭に動画の内容を説明する自然な文章を2〜3文（検索キーワードを自然に含める）
・その後にハッシュタグを続ける
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


def _run_buzz_pattern_a(instagram_script: dict) -> dict:
    """バズmodeパターンA：育児あるある悩み＋開き直り（ダンス・コミカル系）"""
    hook = instagram_script.get("hook", "")
    concept = instagram_script.get("viral_concept", "")
    mood = instagram_script.get("mood_context", "")
    mood_line = f"今日のパパの気分：{mood}（この感情をタイトル・説明文の軸にすること）" if mood else ""

    prompt = f"""
あなたはバイラル育児系YouTube Shortsのチャンネル運営者です。
育休パパの「育児あるある悩み・開き直り」で共感を集めるコンテンツを作ります。

【動画情報】
AIベビーキャラ「せなっち」（生後{MONTH_AGE}ヶ月）
フック：{hook}
コンセプト：{concept}
{mood_line}

【タイトルのルール】
・50〜70文字（短くコンパクトに）
・「生後{MONTH_AGE}ヶ月」を必ず入れる
・「〇〇してくれない」「〇〇されたのでダンスで解決した」など育児あるある・諦め形式
・例：「生後{MONTH_AGE}ヶ月、3時間寝かしつけ失敗したのでダンスした #Shorts」
・検索キーワード（育休パパ/夜泣き/寝かしつけ）を1つ含める
・末尾に「 #Shorts」を必ず付ける

【説明文のルール】
・冒頭に育児あるある悩みを自然な文章で2〜3文（「生後{MONTH_AGE}ヶ月 夜泣き」など検索キーワードを自然に含める）
・開き直り・諦めの絵文字（😇😅🤷‍♂️🫠）を使う
・その後にハッシュタグを続ける
・「#Shorts」を必ず入れる
・末尾：{BUZZ_TAGS_STR} #Shorts #生後{MONTH_AGE}ヶ月 #育休パパ #夜泣き #育児あるある

【ピン留めコメント】
・「チャンネル登録してね▼」から始める
・育児の悩みへの共感一言
・次回予告を1行追加（例：「来週また育児の修羅場を報告します😮‍💨」「同じ経験のパパママ、コメントで語りましょう」）

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


def _run_buzz_pattern_b(instagram_script: dict) -> dict:
    """バズmodeパターンB：パパのアメリカンジョーク形式（超かわいい系）"""
    hook = instagram_script.get("hook", "")
    concept = instagram_script.get("viral_concept", "")
    mood = instagram_script.get("mood_context", "")
    mood_line = f"今日のパパの気分：{mood}（この感情をジョークの前振りに活かすこと）" if mood else ""

    prompt = f"""
あなたはバイラル育児系YouTube Shortsのチャンネル運営者です。
育休パパの「アメリカンジョーク風の落差ネタ」でバズを狙います。

【動画情報】
AIベビーキャラ「せなっち」（生後{MONTH_AGE}ヶ月）
フック：{hook}
コンセプト：{concept}
{mood_line}

【タイトルのルール】
・50〜70文字（短くコンパクトに）
・「生後{MONTH_AGE}ヶ月」を必ず入れる
・「パパが〇〇した日に△△された」「昇進した日にうんちかけられた」系の落差タイトル
・例：「生後{MONTH_AGE}ヶ月のせなっち、パパの昇進を全力で祝わなかった #Shorts」
・検索キーワード（育休パパ/育児vlog）を1つ含める
・末尾に「 #Shorts」を必ず付ける

【説明文のルール】
・冒頭に「パパ今日〇〇した。でもせなっちは〇〇だった。」の落差ネタを2〜3文の自然な文章で（「育休パパ」「育児vlog」などのキーワードを自然に含める）
・最後に必ず「（別に〇〇はしていません）」の自虐ツッコミを1行追加（例：「（別に昇進はしていません）」）
・笑い・涙絵文字（😂🥲😭）を使う
・その後にハッシュタグを続ける
・「#Shorts」を必ず入れる
・末尾：{BUZZ_TAGS_STR} #Shorts #生後{MONTH_AGE}ヶ月 #育休パパ #育児vlog #パパ

【ピン留めコメント】
・「チャンネル登録してね▼」から始める
・「（別に〇〇はしていません）」系の自虐一言
・次回予告を1行追加（例：「次回も格差ネタ続きます😂」「また笑いに来てね」）

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


def _run_buzz_pattern_c(instagram_script: dict) -> dict:
    """バズmodeパターンC：せなっちのかわいさ全振り（「かわいい」コメント誘発）"""
    hook    = instagram_script.get("hook", "")
    concept = instagram_script.get("viral_concept", "")

    prompt = f"""
あなたはバイラル育児系YouTube Shortsのチャンネル運営者です。
「見た人が思わず再生→保存→コメントしてしまう」かわいい系コンテンツを作ります。

【動画情報】
AIベビーキャラ「せなっち」（生後{MONTH_AGE}ヶ月）
フック：{hook}
コンセプト：{concept}

【タイトルのルール】
・50〜70文字（短くコンパクトに）
・「生後{MONTH_AGE}ヶ月」を必ず入れる
・感情爆発ワードを使う（「かわいすぎた」「泣いた」「ずっと見てられる」「天使すぎた」）
・例：「生後{MONTH_AGE}ヶ月の赤ちゃんがかわいすぎて泣いた😭 #Shorts」
・末尾に「 #Shorts」を必ず付ける

【説明文のルール】
・冒頭にせなっちのかわいさを感情的に表現した文章を2〜3文
・「このかわいさをみんなに見せたくて動画にしました」のような素直な感情
・「かわいいと思ったらコメントに🥺を送って」という誘いかけを必ず入れる
・末尾：{BUZZ_TAGS_STR} #Shorts #生後{MONTH_AGE}ヶ月 #かわいい赤ちゃん #babyvideo

【ピン留めコメント】
・「せなっちのかわいさを毎日お届け中🍼」から始める
・チャンネル登録・通知ボタンONを促す1行

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


def _run_milestone(instagram_script: dict) -> dict:
    """マイルストーム用YouTube Shorts（週1成長記録）"""
    week_in_month = calc_week_in_month()
    weeks_alive   = calc_weeks_alive()

    prompt = f"""
あなたはYouTube Shorts育児チャンネルの運営者です。
「週1成長記録」動画のコンテンツを生成してください。

【せなっち情報】生後{MONTH_AGE}ヶ月（第{week_in_month}週・生まれてから{weeks_alive}週目）

【タイトルのルール】
・「生後{MONTH_AGE}ヶ月{week_in_month}週目の記録」を軸にする
・変化・成長ポイントを感情的に（「大きくなりすぎた」「泣いた」など）
・例：「生後{MONTH_AGE}ヶ月{week_in_month}週目、先週と全然違う顔してた😭 #Shorts」
・末尾に「 #Shorts」を必ず付ける

【説明文のルール】
・今週の月齢{MONTH_AGE}ヶ月らしい成長・変化を3点
・「同じ月齢のお子さんはどうですか？コメント欄で教えてください！」を入れる
・末尾：{BUZZ_TAGS_STR} #Shorts #生後{MONTH_AGE}ヶ月 #育児記録 #成長記録

【ピン留めコメント】
・「毎週せなっちの成長を記録中🍼」から始める

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
    """バズmode：パターンA/B/Cを選択（Instagramと同期）"""
    pattern = instagram_script.get("buzz_caption_pattern")
    if not pattern:
        pattern = random.choices(["A", "B", "C"], weights=[25, 25, 50])[0]
        instagram_script["buzz_caption_pattern"] = pattern

    if pattern == "A":
        return _run_buzz_pattern_a(instagram_script)
    elif pattern == "B":
        return _run_buzz_pattern_b(instagram_script)
    else:
        return _run_buzz_pattern_c(instagram_script)


def _load_tags_from_sheets():
    """Sheetsに承認済みタグがあればモジュール変数を上書きする。"""
    global FIXED_TAGS_STR, BUZZ_TAGS_STR
    try:
        from utils.sheets_helper import get_hashtags
        _yt = get_hashtags("youtube")
        if _yt:
            FIXED_TAGS_STR = " ".join(_yt)
            BUZZ_TAGS_STR  = " ".join([t for t in _yt if t != "#PR"])
    except Exception:
        pass


def run(instagram_script: dict, product: dict = None) -> dict:
    """
    Instagramスクリプトを受け取りYouTube Shorts専用コンテンツを生成。
    product=None のときはバズmode（#PRなし・バズ特化キャプション）。
    instagram_script の captions に youtube_title / youtube / pin_comment / threads を追記して返す。
    """
    global MONTH_AGE
    MONTH_AGE = calc_month_age()
    _load_tags_from_sheets()
    is_buzz = product is None

    if is_buzz and instagram_script.get("is_milestone"):
        result = _run_milestone(instagram_script)
        default_title = f"生後{MONTH_AGE}ヶ月の成長記録"
    elif is_buzz:
        result = _run_buzz(instagram_script)
        default_title = f"生後{MONTH_AGE}ヶ月せなっちが可愛すぎた"
    else:
        result = _run_normal(instagram_script, product)
        default_title = f"生後{MONTH_AGE}ヶ月せなっちの記録"

    instagram_script.setdefault("captions", {})
    instagram_script["captions"]["youtube_title"] = result.get("title", default_title)
    description = result.get("description", "")
    instagram_script["captions"]["youtube"] = description + "\n" + get_fixed_footer()
    instagram_script["captions"]["pin_comment"] = result.get("pin_comment", "")

    return instagram_script
