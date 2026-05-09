"""
紹介文生成エージェント
Claude APIを使ってせなっち目線の楽天ROOM紹介文を生成する
"""
import anthropic
import os
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

# 必須ハッシュタグ（毎投稿で必ず含める）
REQUIRED_TAGS = ["#オリジナル写真", f"#生後{MONTH_AGE}ヶ月"]


def ensure_required_tags(description: str) -> str:
    """必須ハッシュタグが含まれていなければ末尾に追加する。#PRは除去する。"""
    import re
    # #PR タグを確実に除去（単体・末尾スペースあり・改行前後どちらでも）
    description = re.sub(r'\s*#PR\b', '', description)
    missing = [tag for tag in REQUIRED_TAGS if tag not in description]
    if missing:
        description = description.rstrip() + "\n" + " ".join(missing)
    return description.strip()


def generate_description(product: dict, event: str = None) -> str:
    """商品の楽天ROOM紹介文を生成する"""
    event_text = f"【{event}開催中】を冒頭に入れる。" if event else ""

    prompt = f"""
あなたは生後{MONTH_AGE}ヶ月の赤ちゃん「せなっち」を育てる育休中のパパです。

以下の商品について楽天ROOMの紹介文を作成してください。

【商品情報】
商品名：{product['name']}
価格：¥{product['price']:,}
キャッチコピー：{product.get('catch_copy', '')}
説明：{product.get('description', '')}

【必ず守るルール】
1. 冒頭は結論から始める
   例：「これ神すぎた…」「もっと早く買えばよかった」「生後{MONTH_AGE}ヶ月のせなっちに大正解」

2. 具体的な使用シーンを1つ入れる
   例：「夜泣きのとき包んだら即寝してくれた」

3. 正直なデメリットを1つだけ入れる
   例：「値段は高めだけど」「洗濯は手洗い推奨だけど」

4. スペックを1行で入れる
   例：「オーガニックコットン・洗濯機OK・通年使える」

5. フォロワーへの問いかけで締める
   例：「使ってるママパパいますか？」

6. 文字数：本文130〜150字以内（ハッシュタグは別）

7. 絵文字：2〜3個のみ

8. 語尾：口語体（〜だった、〜だよ、〜かも）

9. ハッシュタグ（必須）：
   #オリジナル写真 #生後{MONTH_AGE}ヶ月
   ＋商品に合うタグを2〜3個追加（例：#おくるみ #夜泣き対策 など）
   ※ #PR は絶対に使わない（楽天ROOMには不要）

{event_text}

【絶対に使わない言葉】
・「おすすめです」
・「良い商品です」
・「〜と思います」

紹介文のみを出力してください。前置き不要。
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=350,
        messages=[{"role": "user", "content": prompt}]
    )

    description = message.content[0].text.strip()
    return ensure_required_tags(description)


def run(products: list) -> list:
    """TOP商品の紹介文を生成して返す"""
    print(f"✍️  紹介文生成エージェント 起動（生後{MONTH_AGE}ヶ月）")

    results = []
    for i, product in enumerate(products):
        print(f"  [{i+1}/{len(products)}] {product['name'][:40]}")
        print("    生成中...")

        description = generate_description(product)
        product["room_description"] = description
        results.append(product)

        print(f"    ✅ 完了（{len(description)}字）")

    print(f"\n✅ {len(results)} 件の紹介文を生成しました")
    return results
