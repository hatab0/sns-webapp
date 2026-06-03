"""
Threadsエージェント（一体型）
今日の出来事テキストをもとにThreads投稿文を生成する。
2026年アルゴリズム対応：返信継続を最大化・エンゲージメントベイト禁止。
"""
import anthropic
import os
import re
from datetime import date
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

from utils.baby_config import BIRTH_DATE, calc_month_age
LIMIT = 450

BAIT_PATTERNS = [
    "コメントください", "フォローしてください", "いいねしてくれたら",
    "保存お願いします", "リポストよろしく", "コメントしてください",
    "フォローよろしく", "RTください",
]

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


MONTH_AGE = calc_month_age()


def _bait_check(text: str) -> str:
    for pat in BAIT_PATTERNS:
        if pat in text:
            return "fail"
    return "pass"


def _trim(text: str) -> str:
    text = re.sub(r'https?://\S+', '', text).strip()
    if len(text) > LIMIT:
        trimmed = text[:LIMIT]
        for sep in ["。", "！", "？"]:
            idx = trimmed.rfind(sep)
            if idx > LIMIT * 0.6:
                trimmed = trimmed[:idx + 1]
                break
        text = trimmed
    return text.strip()


def run(today_event: str = "") -> dict:
    """
    今日の出来事をもとにThreads投稿文を生成。
    today_event: ユーザーが入力した今日の出来事（空の場合は月齢あるあるで生成）
    戻り値は buffer_agent と互換の形式。
    """
    struggles = MONTHLY_STRUGGLES.get(MONTH_AGE, MONTHLY_STRUGGLES[4])

    if today_event.strip():
        event_section = f"【今日の出来事（実際にあったこと）】\n{today_event}"
        theme = today_event[:30]
    else:
        event_section = f"【生後{MONTH_AGE}ヶ月のリアル】\n" + "・".join(struggles)
        theme = f"生後{MONTH_AGE}ヶ月の育児"

    prompt = f"""
あなたはせなっち（生後{MONTH_AGE}ヶ月）を育てる育休中のパパです。
Threadsに投稿する文章を書いてください。

{event_section}

【2026年Threadsアルゴリズム対応ルール】
・返信が続く問いかけで締める（「同じ経験ある？」「これって普通？」など）
・YES/NOで答えられる or 一言で返せる問いかけにする
・エンゲージメントベイト禁止：「フォローしてください」「コメントください」「いいね」は絶対に入れない

【文体ルール】
・450字以内
・スマホでさっと打ったような口語体
・「ですます調」「おすすめです」「素晴らしい」は禁止
・感情が先、説明は後
・具体的なエピソードを入れる（今日・昨日・さっき）
・絵文字は0〜1個まで
・ハッシュタグ・URL・Instagram誘導は絶対に入れない

キャプションテキストのみを出力。前置き・説明不要。
"""
    text = ""
    for _ in range(3):
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        text = _trim(message.content[0].text.strip())
        if _bait_check(text) == "pass":
            break

    return {
        "type": "threads_text",
        "theme": theme,
        "bait_check": _bait_check(text),
        "captions": {"threads": text},
    }
