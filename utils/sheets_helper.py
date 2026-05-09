"""
Google Sheets履歴読み込みヘルパー
"""
import os
import json
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

SPREADSHEET_ID = "1DfBLBGMQ7kSCXAS_omgBBQ8b59DfFL9j0qkniyLRbro"
SHEET_GID = 748487579


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


def get_history() -> pd.DataFrame | None:
    """投稿履歴をGoogle Sheetsから取得してDataFrameで返す"""
    try:
        client = _get_client()
        if client is None:
            return None

        sheet_id = os.getenv("GOOGLE_SHEETS_ID", SPREADSHEET_ID)
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.get_worksheet_by_id(SHEET_GID)
        records = worksheet.get_all_records()

        if not records:
            return pd.DataFrame()

        return pd.DataFrame(records)

    except Exception as e:
        print(f"Sheets読み込みエラー: {e}")
        return None
