"""
キャプション生成エージェント
Instagram Reel・Threads用のキャプションを自動生成する

対応コンテンツタイプ：
  threads_text → Threads投稿用キャプション（育児トピック・ハッシュタグなし）
  reel         → Instagramキャプション（ハッシュタグあり）+ Threadsキャプション（ハッシュタグなし）
"""
import anthropic
import os
import re
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

# ハッシュタグはInstagramのみ
FIXED_TAGS = ["#babyboo", "#baby", "#PR", "#育児", "#赤ちゃんのいる生活"]
FIXED_TAGS_STR = " ".join(FIXED_TAGS)


def generate_caption(script: dict, platform: str, product: dict = None) -> str:
    content_type = script.get("type", "reel")
    struggles_str = ", ".join(MONTHLY_STRUGGLES.get(MONTH_AGE, MONTHLY_STRUGGLES[4]))

    if content_type == "threads_text":
        content_label = "Threads 育児投稿（育児パパのリアルな独り言）"
        context_info = f"""
テーマ：{script.get('theme', '')}
方向性：{script.get('caption_hint', '')}
今の月齢あるある：{struggles_str}
"""
        closing = "「わかる人いる？」「同じ月齢の人どうだった？」「これあるあるじゃない？」のどれか、または自然に終わる"
        bad_good = """
【NG例（AIっぽい・絶対使わない）】
× 「育児の大変さを実感する毎日ですが、せなっちの成長に喜びを感じています」
× 「生後○ヶ月の育児あるあるをご紹介します」
× 「パパとして頑張っている様子をお届けします」

【OK例（リアルな育児パパの独り言）】
○ 「夜中2時に起こされて、寝かしつけて、また4時に起こされて、今日で3日目だよ…」
○ 「よだれスタイ今日だけで4枚目。洗濯どうにかなんないかな」
○ 「育休とった同期に「大変だった？」って聞いたら「意外と余裕」って言ってて意味わかんなかった。今ならわかる。無理。」"""
        hashtag_rule = "【ハッシュタグ】絶対に使用しない。#も一切つけない。"

    elif content_type in ("reel", "reel_threads"):
        if platform == "instagram":
            content_label = "Instagram Reel キャプション"
            product_info = f"動画でせなっちが着ている・使っている商品：{product['name']}" if product else ""
            context_info = f"""
タイトル：{script.get('title', '')}
フック：{script.get('hook', '')}
バイラルコンセプト：{script.get('viral_concept', '')}
{product_info}
"""
            closing = "「保存した人コメントしてくれると嬉しい」「フォローすると続きが見られるよ」"
            bad_good = """
【NG例】× 「せなっちの可愛い動画です」× 「この商品を使用しています」
【OK例】○ 「この反応見てパパ泣いた😭」○ 「着せたらこうなった」"""
            hashtag_rule = f"【ハッシュタグ】末尾に以下の5個を必ず全て使用（追加・変更・省略禁止）：{FIXED_TAGS_STR}"
        else:
            # Threadsに動画を投稿するときのキャプション（ハッシュタグなし）
            content_label = "Threads 動画投稿キャプション（短め・自然体）"
            product_info = f"（動画でせなっちが着ている・使っている商品：{product['name']}）" if product else ""
            context_info = f"""
動画コンセプト：{script.get('viral_concept', script.get('hook', ''))}
{product_info}
"""
            closing = "「これ何使ってるんですか？って聞いていいよ笑」または「フォローするとせなっちの成長が追えるよ」"
            bad_good = """
【NG例】× 「可愛い動画をお届けします」× 「商品を着用しています」
【OK例】○ 「着せたら動き出しちゃって笑」○ 「生後○ヶ月でこんな声出んの？」"""
            hashtag_rule = "【ハッシュタグ】絶対に使用しない。#も一切つけない。"

    else:
        # フォールバック（Instagram reel）
        content_label = "Instagram Reel キャプション"
        context_info = f"タイトル：{script.get('title', '')}\nフック：{script.get('hook', '')}"
        closing = "「フォローすると続きが見られるよ」"
        bad_good = ""
        hashtag_rule = f"【ハッシュタグ】末尾に以下の5個を必ず全て使用：{FIXED_TAGS_STR}"

    platform_rules = {
        "instagram": """
・150〜200字程度
・改行を使って読みやすくする
・絵文字を2〜3個
・「プロフィールのリンクから見れます」または「楽天ROOMはプロフからどうぞ」を入れる
""",
        "threads": """
・【厳守】450字以内
・アフィリエイトURLは絶対に貼らない
・Instagramへの誘導は入れない
・スマホで打ったような自然な口語体（AIが書いた文章に見えてはいけない）
・感情が先に来る（「やばい」「神すぎ」「まじで」など）
・体験談ベースで書く（「昨日さ〜」「先週試してみたんだけど」など）
・文末は「〜です。〜ます。」ではなく「〜だった」「〜だよ」「〜じゃない？」
""",
    }

    prompt = f"""
あなたは生後{MONTH_AGE}ヶ月の赤ちゃん「せなっち」を育てる育休中のパパです。
スマホで打ったような自然な投稿文を書いてください。

【コンテンツタイプ】
{content_label}

【コンテキスト】
{context_info}

{bad_good}

【文体ルール（絶対に守る）】
・1文を短く。改行多めにしてスマホで読みやすく
・文末は「〜だった」「〜だよ」「〜じゃない？」「〜だよな」など口語体
・感情を先に出す。説明は後
・具体的なエピソードを1つ入れる（「昨日〜」「今日〜」「先週〜」）
・絵文字は1〜2個まで。乱用しない
・「ですます調」「おすすめです」「素晴らしい」「ご紹介」は絶対禁止

【プラットフォームルール】
{platform_rules.get(platform, platform_rules["threads"])}

{hashtag_rule}

締め方のヒント：{closing}

キャプションテキストのみを出力。前置き・説明不要。
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def _trim_threads(caption: str, affiliate_url: str = "") -> str:
    LIMIT = 450
    if affiliate_url and affiliate_url in caption:
        caption = caption.replace(affiliate_url, "").strip()
    caption = re.sub(r'https?://\S*(rakuten|amazon|afl)\S*', '', caption).strip()
    if len(caption) > LIMIT:
        trimmed = caption[:LIMIT]
        for sep in ["。", "！", "？"]:
            idx = trimmed.rfind(sep)
            if idx > LIMIT * 0.6:
                trimmed = trimmed[:idx + 1]
                break
        caption = trimmed
    return caption.strip()


def run(scripts: list, product: dict = None) -> list:
    """
    [threads_text, reel] のコンテンツにキャプションを生成する。

    - threads_text → captions["threads"]（ハッシュタグなし）
    - reel         → captions["instagram"]（ハッシュタグあり）+ captions["threads"]（ハッシュタグなし）
    """
    print("キャプション生成エージェント 起動")
    results = []

    for i, script in enumerate(scripts):
        content_type = script.get("type", "reel")
        title = script.get("title", f"コンテンツ{i+1}")
        print(f"\n  [{i+1}/{len(scripts)}] {title}（{content_type}）")

        captions = {}

        if content_type == "threads_text":
            caption = generate_caption(script, platform="threads", product=None)
            caption = _trim_threads(caption)
            captions["threads"] = caption
            print(f"    threads用キャプション生成完了（{len(caption)}文字）")

        else:  # reel
            caption_ig = generate_caption(script, platform="instagram", product=product)
            captions["instagram"] = caption_ig
            print(f"    instagram用キャプション生成完了")

            reel_threads_script = {**script, "type": "reel_threads"}
            caption_th = generate_caption(reel_threads_script, platform="threads", product=product)
            caption_th = _trim_threads(caption_th)
            captions["threads"] = caption_th
            print(f"    threads動画用キャプション生成完了（{len(caption_th)}文字）")

        script["captions"] = captions
        results.append(script)

    print(f"\n{len(results)} 件のキャプションを生成しました")
    return results
