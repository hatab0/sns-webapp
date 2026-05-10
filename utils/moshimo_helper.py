"""
もしもアフィリエイト リンク生成ヘルパー
楽天・Amazon の商品URLをW報酬リンクに変換する。

必要な環境変数:
  MOSHIMO_A_ID               : あなたのアフィリエイターID（管理画面で確認）
  MOSHIMO_RAKUTEN_P_ID       : 楽天プログラムID
  MOSHIMO_RAKUTEN_PC_ID      : 楽天プログラムカテゴリID
  MOSHIMO_RAKUTEN_PL_ID      : 楽天プレースメントID
  MOSHIMO_AMAZON_P_ID        : AmazonプログラムID
  MOSHIMO_AMAZON_PC_ID       : Amazonプログラムカテゴリ ID
  MOSHIMO_AMAZON_PL_ID       : AmazonプレースメントID

各 ID の確認方法:
  もしもアフィリエイト管理画面 → 広告を探す → 楽天/Amazonで提携申請
  → 広告リンクHTMLを表示 → URLパラメータをコピー
"""
import os
from urllib.parse import quote

BASE = "https://af.moshimo.com/af/c/click"


def _build(a_id: str, p_id: str, pc_id: str, pl_id: str, product_url: str) -> str:
    encoded = quote(product_url, safe="")
    return f"{BASE}?a_id={a_id}&p_id={p_id}&pc_id={pc_id}&pl_id={pl_id}&url={encoded}"


def wrap_rakuten(product_url: str) -> str:
    """楽天商品URLをもしもW報酬リンクに変換。未設定なら元URLをそのまま返す。"""
    a_id  = os.getenv("MOSHIMO_A_ID", "")
    p_id  = os.getenv("MOSHIMO_RAKUTEN_P_ID", "")
    pc_id = os.getenv("MOSHIMO_RAKUTEN_PC_ID", "")
    pl_id = os.getenv("MOSHIMO_RAKUTEN_PL_ID", "")
    if not all([a_id, p_id, pc_id, pl_id, product_url]):
        return product_url
    return _build(a_id, p_id, pc_id, pl_id, product_url)


def wrap_amazon(product_url: str) -> str:
    """AmazonのURLをもしもW報酬リンクに変換。未設定なら元URLをそのまま返す。"""
    a_id  = os.getenv("MOSHIMO_A_ID", "")
    p_id  = os.getenv("MOSHIMO_AMAZON_P_ID", "")
    pc_id = os.getenv("MOSHIMO_AMAZON_PC_ID", "")
    pl_id = os.getenv("MOSHIMO_AMAZON_PL_ID", "")
    if not all([a_id, p_id, pc_id, pl_id, product_url]):
        return product_url
    return _build(a_id, p_id, pc_id, pl_id, product_url)


def is_configured_rakuten() -> bool:
    return all([
        os.getenv("MOSHIMO_A_ID"),
        os.getenv("MOSHIMO_RAKUTEN_P_ID"),
        os.getenv("MOSHIMO_RAKUTEN_PC_ID"),
        os.getenv("MOSHIMO_RAKUTEN_PL_ID"),
    ])


def is_configured_amazon() -> bool:
    return all([
        os.getenv("MOSHIMO_A_ID"),
        os.getenv("MOSHIMO_AMAZON_P_ID"),
        os.getenv("MOSHIMO_AMAZON_PC_ID"),
        os.getenv("MOSHIMO_AMAZON_PL_ID"),
    ])
