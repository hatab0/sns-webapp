"""
Google Sheets履歴読み込みヘルパー
"""
import os
import json
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials


def get_history() -> pd.DataFrame | None:
    """投稿履歴をGoogle Sheetsから取得してDataFrameで返す"""
    try:
        creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
        sheet_id = os.getenv("GOOGLE_SHEETS_ID", "")

        if not creds_json or not sheet_id:
            return None

        creds_dict = json.loads(creds_json)
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)

        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.get_worksheet(0)
        records = worksheet.get_all_records()

        if not records:
            return pd.DataFrame()

        return pd.DataFrame(records)

    except Exception as e:
        print(f"Sheets読み込みエラー: {e}")
        return None
