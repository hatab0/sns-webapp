"""
品質チェックエージェント
生成された紹介文の品質を検証する
"""
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 禁止ワード
FORBIDDEN_WORDS = ["おすすめです", "良い商品", "〜と思います", "と思います"]

# 必須ハッシュタグ
REQUIRED_TAGS = ["#PR", "#生後"]

# 文字数範囲
MIN_LENGTH = 100
MAX_LENGTH = 200


def check_description(description: str) -> dict:
    """
    紹介文の品質チェックを行う
    """
    issues = []

    # 文字数チェック
    length = len(description)
    if length < MIN_LENGTH:
        issues.append(f"文字数が短すぎます（{length}字 < {MIN_LENGTH}字）")
    elif length > MAX_LENGTH:
        issues.append(f"文字数が長すぎます（{length}字 > {MAX_LENGTH}字）")

    # 禁止ワードチェック
    for word in FORBIDDEN_WORDS:
        if word in description:
            issues.append(f"禁止ワードが含まれています：「{word}」")

    # 必須タグチェック
    for tag in REQUIRED_TAGS:
        if tag not in description:
            issues.append(f"必須タグが不足しています：{tag}")

    return {
        "length": length,
        "passed": len(issues) == 0,
        "issues": issues
    }


def fix_description(product: dict, description: str, issues: list) -> str:
    """
    品質NGの場合に紹介文を修正する
    """
    prompt = f"""
以下の楽天ROOM紹介文に問題があります。修正してください。

【問題点】
{chr(10).join(f"・{issue}" for issue in issues)}

【元の紹介文】
{description}

【商品情報】
商品名：{product['name']}
価格：¥{product['price']:,}

【修正ルール】
・130〜150字以内
・#PR #生後4ヶ月 を必ず含む
・「おすすめです」「良い商品」「〜と思います」を使わない
・パパ目線の口語体

修正した紹介文のみを出力してください。
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text.strip()


def run(products: list) -> list:
    """
    全商品の紹介文を品質チェックし、NGなら修正する
    """
    print("✅ 品質チェックエージェント 起動")

    results = []
    for i, product in enumerate(products):
        description = product.get("room_description", "")
        print(f"\n  [{i+1}/{len(products)}] {product['name'][:40]}")

        # 品質チェック
        check = check_description(description)
        print(f"    文字数：{check['length']}字")

        if check["passed"]:
            print("    ✅ 品質OK")
            product["quality_passed"] = True
        else:
            print("    ⚠️  品質NG")
            for issue in check["issues"]:
                print(f"      - {issue}")

            # 自動修正
            print("    🔧 自動修正中...")
            fixed = fix_description(product, description, check["issues"])
            product["room_description"] = fixed
            product["quality_passed"] = True
            product["auto_fixed"] = True
            print(f"    ✅ 修正完了（{len(fixed)}字）")

        results.append(product)

    passed = sum(1 for p in results if p.get("quality_passed"))
    print(f"\n✅ 品質チェック完了：{passed}/{len(results)} 件通過")
    return results
