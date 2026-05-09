"""
リール台本・Threads投稿コンセプト生成エージェント
Claude APIを使って3種類のコンテンツを自律生成する（1回実行で完結）

生成コンテンツ：
  1. Threads投稿①（商品アフィリエイト）
  2. Threads投稿②（バズ・あるある：Claudeが自律的にテーマを選定）
  3. Instagram Reel（バイラルコンセプト：AIベビーが月齢に合った声を出す）
"""
import anthropic
import os
import json
from datetime import date
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# せなっちの誕生日（ここだけ変更すれば月齢が全自動で切り替わる）
BIRTH_DATE = date(2025, 12, 22)


def calc_month_age() -> int:
    """誕生日から現在の月齢を自動計算する"""
    today = date.today()
    months = (today.year - BIRTH_DATE.year) * 12 + (today.month - BIRTH_DATE.month)
    if today.day < BIRTH_DATE.day:
        months -= 1
    return max(0, months)


MONTH_AGE = calc_month_age()

# 月齢別・育児あるある（バズ投稿のネタ選定に参照させる）
MONTHLY_STRUGGLES = {
    0: ["授乳が2時間おき", "泣き止まない理由がわからない", "沐浴が毎回緊張する"],
    1: ["げっぷがうまく出ない", "抱っこじゃないと寝ない", "夜中の授乳で限界"],
    2: ["あやしても泣き止まない黄昏泣き", "やっと笑った瞬間が全てを癒す", "哺乳瓶拒否が始まった"],
    3: ["首すわり練習が地味にきつい", "よだれが急に増えた", "寝返り練習で目が離せない"],
    4: ["よだれスタイが1日5枚でも足りない", "夜中まだ2〜3回起きる", "ベビーカー乗り嫌いが発覚"],
    5: ["離乳食準備どこから始めるか問題", "寝返りしてうつ伏せで泣く無限ループ", "後追いが始まった気がする"],
    6: ["離乳食を全拒否される", "お座りが不安定で目が離せない", "人見知りがひどくなってきた"],
    7: ["ハイハイで何でも触りに行く", "離乳食の食べムラがすごい", "夜泣き復活した"],
    8: ["つかまり立ちで毎日ひとり転倒", "後追いMAX期でトイレも行けない", "なんでも口に入れる"],
    9: ["伝い歩きが始まって家中危ない", "指差しが始まってどこでも「あっあっ」", "昼寝が1回になってきた"],
    10: ["「ママ」「パパ」がやっと出てきた感動", "食べ物の好き嫌いがはっきりしてきた", "靴を嫌がって泣く"],
    11: ["もうすぐ1歳なのに感慨深い", "歩きたいのに歩けなくてギャン泣き", "卒乳問題が頭をよぎる"],
    12: ["1歳の誕生日準備が想定外に大変", "一升餅で泣かせてしまった", "やっと歩いた瞬間"],
}

# 月齢別・赤ちゃんの発声マップ（バイラルリール用）
BABY_SPEECH_BY_MONTH = {
    0: {"sounds": ["おぎゃー", "ふにゃー"],                  "desc": "泣き声のみ"},
    1: {"sounds": ["あー", "うー"],                          "desc": "クーイング（母音）"},
    2: {"sounds": ["あーうー", "えへへ"],                    "desc": "クーイング＋笑い声"},
    3: {"sounds": ["あははっ", "きゃっ", "うふー"],          "desc": "笑い声・喜び声"},
    4: {"sounds": ["あーっ！", "えへへ", "んー？", "きゃっ"], "desc": "クーイング・笑い声・驚き"},
    5: {"sounds": ["ままま", "ばばば", "あっあっ"],          "desc": "喃語（繰り返し音）開始"},
    6: {"sounds": ["まーまー", "ぱーぱー", "んまー"],        "desc": "喃語が増える"},
    7: {"sounds": ["あーあー", "まんまー", "ぱっぱー"],      "desc": "意味のある喃語"},
    8: {"sounds": ["まんまー", "ねーね", "うー！"],          "desc": "食べ物・眠気の喃語"},
    9: {"sounds": ["まんまー！", "ぱっぱー", "やー！"],      "desc": "喃語＋指差し声"},
    10: {"sounds": ["ママ", "パパ", "まんま"],               "desc": "初語デビュー！"},
    11: {"sounds": ["ママ！", "パパ！", "まんまー！"],       "desc": "初語が明確に"},
    12: {"sounds": ["ママ", "パパ", "わんわん", "ねんね"],   "desc": "語彙が増える"},
    13: {"sounds": ["ねんね", "だっこ", "いやー"],           "desc": "要求語が出る"},
    14: {"sounds": ["あっち！", "これ？", "もっと！"],       "desc": "指差し＋要求語"},
    15: {"sounds": ["ママ きて", "もっと！", "いやいや"],    "desc": "二語文に向かう"},
}


def _parse_json_response(text: str) -> dict:
    """Claude応答からJSONを安全に取り出す"""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw": text, "error": "JSON parse failed"}


def generate_threads_product(product: dict) -> dict:
    """
    Threads投稿①：商品アフィリエイト用コンセプトを生成する。
    商品情報を受け取り、パパ目線のリアルな体験談ベースで生成。
    """
    prompt = f"""
あなたはせなっち（生後{MONTH_AGE}ヶ月）を育てる育休中のパパです。

以下の商品のThreads投稿コンセプトを作成してください。

【商品情報】
商品名：{product['name']}
価格：¥{product['price']:,}
キャッチコピー：{product.get('catch_copy', '')}

【コンセプトのルール】
・パパ目線の口語体（AIっぽくしない）
・感情ファースト（「神すぎた」「もっと早く買えばよかった」など）
・体験談ベース（「昨日さ〜」「試してみたんだけど」など）
・Instagramへの誘導を自然に含める（「Instagramで動画あげてるよ」など）
・アフィリエイトURLは含めない
・450字以内

【出力形式】JSONのみ。前置き不要。

{{
  "type": "threads_product",
  "title": "投稿タイトル（内部管理用・20字以内）",
  "caption_hint": "Threads投稿の方向性・雰囲気を2〜3文で要約（キャプション生成エージェントへのヒント）"
}}
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    result = _parse_json_response(message.content[0].text.strip())
    result["type"] = "threads_product"
    result["product_name"] = product["name"]
    return result


def generate_threads_buzz() -> dict:
    """
    Threads投稿②：バズ・あるある投稿コンセプトをClaudeが自律的に選定・生成する。
    商品情報は使わない。育児パパとしての共感・感動・あるある系。
    """
    struggles = MONTHLY_STRUGGLES.get(MONTH_AGE, MONTHLY_STRUGGLES[4])
    struggles_str = "・" + "\n・".join(struggles)

    prompt = f"""
あなたはせなっち（生後{MONTH_AGE}ヶ月）を育てる育休中のパパです。

Threads向けのバズ投稿コンセプトを自律的に生成してください。
商品紹介は一切しません。育児パパとしての共感・感動・あるある系の投稿です。

【今の月齢（生後{MONTH_AGE}ヶ月）の育児リアル】
{struggles_str}

【テーマカテゴリ（いずれか1つを選んで投稿コンセプトを作る）】
① 育児あるある（思わず笑える共感ネタ）
② 月齢ならではの出来事（生後{MONTH_AGE}ヶ月に特有の体験・成長）
③ パパの等身大のつぶやき（育児の本音・気づき・感動）
④ 感動の瞬間（こどもの成長を見て心が動いた瞬間）

【コンセプトのルール】
・カテゴリをClaudeが自律的に選ぶ（どれでもよい）
・スマホで打ったような自然な口語体
・Instagramへの誘導は任意（入れても入れなくてもよい）
・450字以内で完結する投稿を想定

【出力形式】JSONのみ。前置き不要。

{{
  "type": "threads_buzz",
  "title": "投稿タイトル（内部管理用・20字以内）",
  "theme": "選んだカテゴリと具体的なテーマ（例：② 生後4ヶ月のハンドリガードが止まらない件）",
  "caption_hint": "Threads投稿の方向性・雰囲気を2〜3文で要約（キャプション生成エージェントへのヒント）"
}}
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    result = _parse_json_response(message.content[0].text.strip())
    result["type"] = "threads_buzz"
    return result


def generate_reel_concept(product: dict) -> dict:
    """
    Instagram Reel：バイラルコンセプトを生成する。
    せなっちが商品を実際に着ている・使っている状態で月齢に合った声・仕草をする。
    @baby_cubo_official スタイル参考：自然な赤ちゃんの瞬間 × 商品が主役。
    ループしやすい・フォロワー外リーチ最大化を狙う。
    """
    speech_info = BABY_SPEECH_BY_MONTH.get(MONTH_AGE, BABY_SPEECH_BY_MONTH[4])
    sounds_str = "・".join(speech_info["sounds"])
    speech_desc = speech_info["desc"]

    prompt = f"""
あなたはInstagramバイラルリール動画のコンテンツ戦略家です。

AIベビーキャラ「せなっち」（生後{MONTH_AGE}ヶ月）のバイラルリールコンセプトを作成してください。

【コンセプトの核心】
・@baby_cubo_official スタイル参考：自然な赤ちゃんの瞬間を捉えながら、商品がちゃんと映る
・せなっちが商品を実際に着ている・使っている状態で月齢の声・仕草をする
・「かわいすぎ」「これ何使ってるの？」と思わずコメントしたくなる
・宣伝感はゼロでも、商品はしっかり主役として映っている
・自然にループする動画構成（最後→最初がつながる）

【せなっちの月齢情報】
・生後{MONTH_AGE}ヶ月
・この月齢の発声レベル：{speech_desc}
・月齢に合った声・音：{sounds_str}

【商品情報（せなっちが実際に着る・使う）】
商品名：{product['name']}
商品カテゴリ：{product.get('catch_copy', '')}
→ この商品をせなっちに着せる・持たせる・使わせることで自然にシーンに組み込む

【リールの構成ルール】
・0〜2秒：フック（「これ着てる赤ちゃん見て」「生後{MONTH_AGE}ヶ月がこんな声出した」と思わせる冒頭）
・2〜8秒：メインシーン（商品を着ている/使っているせなっちが声・音を出す、笑う、驚くなど）
・8〜12秒：ループポイント（自然に最初に戻る構成）
・商品はせなっちが着用中・使用中の状態でカメラにしっかり映る
・音声OFFでも伝わるテキストオーバーレイを想定

【出力形式】JSONのみ。前置き不要。

{{
  "type": "reel",
  "title": "動画タイトル（内部管理用・20字以内）",
  "hook": "冒頭0〜2秒のフックテキスト（スクロールを止める一言・日本語）",
  "bgm_style": "BGMの雰囲気（トレンド感があるもの。例：ほんわか邦楽・ポップなインスト・TikTokトレンド系）",
  "viral_concept": "バイラルシーンの詳細な説明（撮影者・動画生成への指示として3〜5文。商品の着用/使用方法・月齢サウンド・ループポイントを含める）"
}}
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    result = _parse_json_response(message.content[0].text.strip())
    result["type"] = "reel"
    result["product_name"] = product["name"]
    return result


def run(product: dict) -> list:
    """
    3種類のコンテンツコンセプトを一括生成して返す。
    戻り値: [threads_product, threads_buzz, reel] の3要素リスト
    """
    print(f"コンテンツコンセプト生成エージェント 起動（生後{MONTH_AGE}ヶ月）")

    # ── Threads① 商品投稿 ──
    print("  [1/3] Threads① 商品投稿コンセプト 生成中...")
    threads_product = generate_threads_product(product)
    print(f"    完了：{threads_product.get('title', 'タイトルなし')}")

    # ── Threads② バズ投稿（Claudeが自律選定） ──
    print("  [2/3] Threads② バズ投稿コンセプト 生成中（Claudeが自律テーマ選定）...")
    threads_buzz = generate_threads_buzz()
    print(f"    完了：{threads_buzz.get('title', 'タイトルなし')}（テーマ: {threads_buzz.get('theme', '')}）")

    # ── Instagram Reel バイラルコンセプト ──
    print("  [3/3] Instagram Reel バイラルコンセプト 生成中...")
    reel = generate_reel_concept(product)
    print(f"    完了：{reel.get('title', 'タイトルなし')}")

    print(f"\n3 件のコンテンツコンセプトを生成しました")
    return [threads_product, threads_buzz, reel]
