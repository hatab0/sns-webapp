"""
市場分析エージェント
取得した商品をスコアリングしてTOP3を選出する
"""
import json
import os
from pathlib import Path

SKIP_LIST_FILE = Path(__file__).parent.parent.parent / "data" / "skip_list.json"


def _product_keys(product: dict) -> list:
    """商品の全キーリストを返す（URLパターンの違いによる不一致を防ぐため複数生成）"""
    from urllib.parse import urlparse, parse_qs, unquote

    url = product.get("url", "")
    keys = []

    if "hb.afl.rakuten.co.jp" in url:
        # ベースのアフィリURLを候補に追加
        base_afl = url.split("?")[0]
        keys.append(base_afl)
        # pcパラメータがあれば楽天URLも候補に追加
        params = parse_qs(urlparse(url).query)
        pc_url = params.get("pc", [""])[0]
        if pc_url:
            resolved = unquote(pc_url).split("?")[0]
            if "item.rakuten.co.jp" in resolved:
                keys.append(resolved)
    elif "item.rakuten.co.jp" in url:
        keys.append(url.split("?")[0])
    else:
        keys.append(url)

    # item_codeも候補に追加
    item_code = product.get("item_code", "")
    if item_code:
        keys.append(f"code:{item_code}")

    return [k for k in keys if k]


def score_product(product: dict) -> float:
    """
    商品をスコアリングする
    スコア = レビュー数 * 0.6 + レビュー評価 * 10 * 0.4
    """
    review_count = product.get("review_count", 0)
    review_average = product.get("review_average", 0.0)
    return (review_count * 0.6) + (review_average * 10 * 0.4)


def run(products: list = None) -> list:
    """
    商品をスコアリングしてTOP3を返す
    """
    print("📊 市場分析エージェント 起動")

    # productsが渡されなければファイルから読み込む
    if products is None:
        try:
            with open("output/products.json", "r", encoding="utf-8") as f:
                products = json.load(f)
        except FileNotFoundError:
            print("  ❌ output/products.json が見つかりません")
            print("  先に rakuten_agent を実行してください")
            return []

    if not products:
        print("  ❌ 商品データが空です")
        return []

    # スコアリング
    for p in products:
        p["score"] = round(score_product(p), 2)

    # スコア順にソート
    sorted_products = sorted(products, key=lambda x: x["score"], reverse=True)

    # ─── 重複チェック：スキップリストを読み込んでフィルタリング ───
    skip_keys = []
    if SKIP_LIST_FILE.exists():
        with open(SKIP_LIST_FILE, encoding="utf-8") as f:
            skip_keys = json.load(f)

    if skip_keys:
        before = len(sorted_products)
        filtered = [p for p in sorted_products if not any(k in skip_keys for k in _product_keys(p))]
        skipped = before - len(filtered)
        if skipped:
            print(f"\n  ⏭️  重複スキップ: {skipped} 件")
        # フィルタ後に商品が0件になった場合は全件から選ぶ（安全策）
        if not filtered:
            print("  ⚠️  全商品がクールダウン中のため、スキップなしで選出します")
            filtered = sorted_products
    else:
        filtered = sorted_products

    # 上位10件を表示
    print(f"\n  上位10件（重複除外後 {len(filtered)} 件から）：")
    for i, p in enumerate(filtered[:10]):
        print(f"  {i+1:2d}. {p['name'][:35]:35s} | ¥{p['price']:,} | ⭐{p['review_average']}({p['review_count']:,}件) | スコア:{p['score']}")

    # TOP3を選出
    top3 = filtered[:3]

    print(f"\n✅ TOP3 選出完了")
    for i, p in enumerate(top3):
        print(f"  {i+1}位: {p['name'][:40]}")

    return top3
