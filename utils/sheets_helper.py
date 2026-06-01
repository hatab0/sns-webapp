"""
Google Sheets 商品履歴ヘルパー
- 1商品 = 1行（item_code でユニーク管理）
- 生成回数・各プラットフォーム投稿数を追跡
"""
import os
import json
import pandas as pd
import gspread
from datetime import datetime, timedelta, timezone
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = "1DfBLBGMQ7kSCXAS_omgBBQ8b59DfFL9j0qkniyLRbro"
SHEET_GID = 748487579
JST = timezone(timedelta(hours=9))

HEADERS = [
    "最終生成日", "item_code", "商品名", "価格", "キーワード",
    "生成回数", "楽天ROOM投稿数", "Instagram投稿数", "TikTok投稿数", "YouTube投稿数", "アフィリエイトURL", "メモ",
]


def _get_client():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
    if not creds_json:
        return None
    creds_dict = json.loads(creds_json)
    scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)


def _get_worksheet():
    client = _get_client()
    if client is None:
        return None
    sheet_id = os.getenv("GOOGLE_SHEETS_ID", SPREADSHEET_ID)
    spreadsheet = client.open_by_key(sheet_id)
    return spreadsheet.get_worksheet_by_id(SHEET_GID)


def _get_col_map(ws) -> dict:
    """ヘッダー行 → {列名: 列番号(1-based)}。item_code がなければ初期化。"""
    row1 = ws.row_values(1)
    if row1 and "item_code" in row1:
        return {h: i + 1 for i, h in enumerate(row1) if h}
    ws.update("A1", [HEADERS])
    return {h: i + 1 for i, h in enumerate(HEADERS)}


def _all_rows(ws) -> tuple[list, list[dict]]:
    """(headers, [{col: val, ...}, ...]) を返す（row 2 以降）"""
    vals = ws.get_all_values()
    if len(vals) < 2:
        return vals[0] if vals else [], []
    headers = vals[0]
    rows = []
    for row_idx, row in enumerate(vals[1:], start=2):
        padded = row + [""] * (len(headers) - len(row))
        rec = {headers[i]: padded[i] for i in range(len(headers))}
        rec["__row__"] = row_idx
        rows.append(rec)
    return headers, rows


def get_product_history() -> dict:
    """
    {item_code: {
        "row": int,
        "生成回数": int,
        "楽天ROOM投稿数": int,
        "Instagram投稿数": int,
        "TikTok投稿数": int,
        "YouTube投稿数": int,
        "最終生成日": str,
    }}
    """
    try:
        ws = _get_worksheet()
        if ws is None:
            return {}
        _get_col_map(ws)
        _, rows = _all_rows(ws)
        history = {}
        for rec in rows:
            code = str(rec.get("item_code", "")).strip()
            if not code:
                continue
            history[code] = {
                "row":           rec["__row__"],
                "生成回数":       int(rec.get("生成回数", 0) or 0),
                "楽天ROOM投稿数": int(rec.get("楽天ROOM投稿数", 0) or 0),
                "Instagram投稿数": int(rec.get("Instagram投稿数", 0) or 0),
                "TikTok投稿数":  int(rec.get("TikTok投稿数", 0) or 0),
                "YouTube投稿数": int(rec.get("YouTube投稿数", 0) or 0),
                "最終生成日":     str(rec.get("最終生成日", "")),
            }
        return history
    except Exception as e:
        print(f"get_product_history error: {e}")
        return {}


def get_last_generated_code(history: dict) -> str:
    """最後に生成した item_code を返す（後方互換用）"""
    if not history:
        return ""
    try:
        latest = max(history.items(), key=lambda x: x[1].get("最終生成日", "") or "")
        return latest[0]
    except Exception:
        return ""


def get_recent_codes(history: dict, days: int = 7) -> set:
    """直近N日間に生成した item_code のセット（同一商品の連続紹介防止）"""
    cutoff = (datetime.now(tz=JST) - timedelta(days=days)).strftime("%Y-%m-%d")
    return {
        code
        for code, rec in history.items()
        if rec.get("最終生成日", "") >= cutoff
    }


def upsert_product(product: dict) -> bool:
    """コンテンツ生成後に商品行を追加 / 生成回数をインクリメント"""
    try:
        ws = _get_worksheet()
        if ws is None:
            return False
        col_map = _get_col_map(ws)
        today = datetime.now(tz=JST).strftime("%Y-%m-%d")
        item_code = str(product.get("item_code", "")).strip()
        if not item_code:
            return False

        history = get_product_history()

        if item_code in history:
            row = history[item_code]["row"]
            ws.update_cell(row, col_map["最終生成日"], today)
            ws.update_cell(row, col_map["生成回数"], history[item_code]["生成回数"] + 1)
        else:
            new_row = [""] * len(HEADERS)
            for header, val in [
                ("最終生成日",      today),
                ("item_code",      item_code),
                ("商品名",         product.get("name", "")[:50]),
                ("価格",           product.get("price", 0)),
                ("キーワード",      product.get("keyword", "")),
                ("生成回数",        1),
                ("楽天ROOM投稿数",  0),
                ("Instagram投稿数", 0),
                ("TikTok投稿数",   0),
                ("YouTube投稿数",  0),
                ("アフィリエイトURL", product.get("affiliate_url", "")),
            ]:
                idx = col_map.get(header)
                if idx:
                    new_row[idx - 1] = val
            ws.append_row(new_row, value_input_option="USER_ENTERED")
        return True
    except Exception as e:
        print(f"upsert_product error: {e}")
        return False


def increment_count(item_code: str, platform: str) -> bool:
    """
    platform: "楽天ROOM投稿数" | "Instagram投稿数" | "TikTok投稿数" | "YouTube投稿数"
    対象行の投稿数を +1 する
    """
    try:
        ws = _get_worksheet()
        if ws is None:
            return False
        col_map = _get_col_map(ws)
        col = col_map.get(platform)
        if not col:
            return False
        history = get_product_history()
        if item_code not in history:
            return False
        row = history[item_code]["row"]
        new_val = history[item_code].get(platform, 0) + 1
        ws.update_cell(row, col, new_val)
        return True
    except Exception as e:
        print(f"increment_count error: {e}")
        return False


HASHTAG_SHEET_NAME  = "hashtags"
HASHTAG_PLATFORMS   = ["instagram_fixed", "instagram_buzz", "tiktok", "youtube"]
PROFILE_SHEET_NAME  = "senacchi_profile"
PROFILE_HEADERS = ["month_age", "cloudinary_url", "registered_at"]


def _get_hashtag_worksheet():
    """hashtags シートを取得。なければ自動作成。"""
    client = _get_client()
    if client is None:
        return None
    sheet_id = os.getenv("GOOGLE_SHEETS_ID", SPREADSHEET_ID)
    spreadsheet = client.open_by_key(sheet_id)
    try:
        return spreadsheet.worksheet(HASHTAG_SHEET_NAME)
    except Exception:
        ws = spreadsheet.add_worksheet(title=HASHTAG_SHEET_NAME, rows=20, cols=4)
        ws.update("A1", [["platform", "tags", "updated_at"]])
        return ws


def get_hashtags(platform: str) -> list | None:
    """指定プラットフォームのハッシュタグリストを返す。未設定の場合は None。"""
    try:
        ws = _get_hashtag_worksheet()
        if ws is None:
            return None
        for rec in ws.get_all_records():
            if rec.get("platform") == platform:
                raw = rec.get("tags", "").strip()
                if raw:
                    return [t.strip() for t in raw.split() if t.strip()]
        return None
    except Exception as e:
        print(f"get_hashtags error: {e}")
        return None


def set_hashtags(platform: str, tags: list) -> bool:
    """指定プラットフォームのハッシュタグを保存 / 更新する。"""
    try:
        ws = _get_hashtag_worksheet()
        if ws is None:
            return False
        today = datetime.now(tz=JST).strftime("%Y-%m-%d")
        tags_str = " ".join(tags)
        records = ws.get_all_records()
        for i, rec in enumerate(records, start=2):
            if rec.get("platform") == platform:
                ws.update(f"A{i}:C{i}", [[platform, tags_str, today]])
                return True
        ws.append_row([platform, tags_str, today])
        return True
    except Exception as e:
        print(f"set_hashtags error: {e}")
        return False


def _get_profile_worksheet():
    """senacchi_profile シートを取得。なければ自動作成。"""
    client = _get_client()
    if client is None:
        return None
    sheet_id = os.getenv("GOOGLE_SHEETS_ID", SPREADSHEET_ID)
    spreadsheet = client.open_by_key(sheet_id)
    try:
        return spreadsheet.worksheet(PROFILE_SHEET_NAME)
    except Exception:
        ws = spreadsheet.add_worksheet(title=PROFILE_SHEET_NAME, rows=50, cols=5)
        ws.update("A1", [PROFILE_HEADERS])
        return ws


def get_reference_photo(month_age: int) -> dict | None:
    """指定月齢の基準写真情報を返す。未登録の場合は None。"""
    try:
        ws = _get_profile_worksheet()
        if ws is None:
            return None
        records = ws.get_all_records()
        for rec in records:
            if str(rec.get("month_age", "")) == str(month_age):
                url = rec.get("cloudinary_url", "")
                if url:
                    return {"url": url, "registered_at": rec.get("registered_at", "")}
        return None
    except Exception as e:
        print(f"get_reference_photo error: {e}")
        return None


def set_reference_photo(month_age: int, url: str) -> bool:
    """指定月齢の基準写真URLを保存 / 上書き更新する。"""
    try:
        ws = _get_profile_worksheet()
        if ws is None:
            return False
        today = datetime.now(tz=JST).strftime("%Y-%m-%d")
        records = ws.get_all_records()
        for i, rec in enumerate(records, start=2):
            if str(rec.get("month_age", "")) == str(month_age):
                ws.update(f"A{i}:C{i}", [[month_age, url, today]])
                return True
        ws.append_row([month_age, url, today])
        return True
    except Exception as e:
        print(f"set_reference_photo error: {e}")
        return False


def get_history() -> pd.DataFrame | None:
    """履歴タブ用: 全行を DataFrame で返す"""
    try:
        ws = _get_worksheet()
        if ws is None:
            return None
        _get_col_map(ws)
        headers, rows = _all_rows(ws)
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)[headers]  # __row__ を除外
        df = df[df["item_code"].str.strip() != ""]
        return df
    except Exception as e:
        print(f"Sheets読み込みエラー: {e}")
        return None
