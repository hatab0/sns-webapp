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


def _is_skip(item_code: str, history: dict, recent_codes: set) -> bool:
    """
    - 直近7日間に生成した商品（recent_codes に含まれる）→ True
    - 楽天ROOMに1件でも投稿済み → True（楽天ROOMは同一商品の重複投稿不可）
    - 生成回数が3回以上 → True
    """
    if item_code and item_code in recent_codes:
        return True
    rec = history.get(item_code, {})
    if rec.get("楽天ROOM投稿数", 0) > 0:
        return True
    return rec.get("生成回数", 0) >= 3


def run(products: list = None, history: dict = None, recent_codes: set = None, last_code: str = "") -> list:
    """
    商品をスコアリングしてTOP3を返す。
    history: sheets_helper.get_product_history() の結果（Webアプリ用）
    recent_codes: 直近7日間に生成した item_code のセット（重複防止）
    """
    print("📊 市場分析エージェント 起動")

    # productsが渡されなければファイルから読み込む
    if products is None:
        try:
            with open("output/products.json", "r", encoding="utf-8") as f:
                products = json.load(f)
        except FileNotFoundError:
            print("  ❌ output/products.json が見つかりません")
            return []

    if not products:
        print("  ❌ 商品データが空です")
        return []

    # スコアリング
    for p in products:
        p["score"] = round(score_product(p), 2)

    sorted_products = sorted(products, key=lambda x: x["score"], reverse=True)

    # ─── フィルタリング ───
    if history is not None:
        # Webアプリ: Sheets履歴ベースでフィルタ
        _recent = recent_codes or set()
        filtered = [
            p for p in sorted_products
            if not _is_skip(p.get("item_code", ""), history, _recent)
        ]
        skipped = len(sorted_products) - len(filtered)
        if skipped:
            print(f"\n  ⏭️  重複スキップ: {skipped} 件（楽天ROOM投稿済み / 直近7日以内 / 生成3回済）")
    else:
        # CLI用: ローカル skip_list.json
        skip_keys = []
        if SKIP_LIST_FILE.exists():
            with open(SKIP_LIST_FILE, encoding="utf-8") as f:
                skip_keys = json.load(f)
        filtered = (
            [p for p in sorted_products if not any(k in skip_keys for k in _product_keys(p))]
            if skip_keys else sorted_products
        )

    if not filtered:
        print("  ⚠️  全商品がフィルタ対象のため、制限なしで選出します")
        filtered = sorted_products

    print(f"\n  上位10件（重複除外後 {len(filtered)} 件から）：")
    for i, p in enumerate(filtered[:10]):
        print(f"  {i+1:2d}. {p['name'][:35]:35s} | ¥{p['price']:,} | ⭐{p['review_average']}({p['review_count']:,}件) | スコア:{p['score']}")

    top3 = filtered[:3]
    print(f"\n✅ TOP3 選出完了")
    for i, p in enumerate(top3):
        print(f"  {i+1}位: {p['name'][:40]}")

    return top3
