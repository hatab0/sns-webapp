"""
YouTube自動コメントエージェント
YouTube Data API v3を使って動画にコメントを投稿する。
ピン留めはAPIで不可のため、投稿後に手動でピン留めする運用。

必要な環境変数:
  YOUTUBE_CLIENT_ID      : Google Cloud OAuthクライアントID
  YOUTUBE_CLIENT_SECRET  : Google Cloud OAuthクライアントシークレット
  YOUTUBE_REFRESH_TOKEN  : OAuth2リフレッシュトークン（初回認証後に取得）
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_CLIENT_ID     = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "")

TOKEN_URL    = "https://oauth2.googleapis.com/token"
COMMENT_URL  = "https://www.googleapis.com/youtube/v3/commentThreads"


def _is_configured() -> bool:
    return bool(YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET and YOUTUBE_REFRESH_TOKEN)


def _get_access_token() -> str:
    """リフレッシュトークンからアクセストークンを取得"""
    resp = requests.post(TOKEN_URL, data={
        "client_id":     YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET,
        "refresh_token": YOUTUBE_REFRESH_TOKEN,
        "grant_type":    "refresh_token",
    })
    resp.raise_for_status()
    return resp.json()["access_token"]


def extract_video_id(url_or_id: str) -> str:
    """YouTube URLまたはIDからビデオIDを抽出"""
    url_or_id = url_or_id.strip()
    if "youtu.be/" in url_or_id:
        return url_or_id.split("youtu.be/")[1].split("?")[0]
    if "v=" in url_or_id:
        return url_or_id.split("v=")[1].split("&")[0]
    return url_or_id  # そのままIDとして使用


def post_comment(video_id_or_url: str, comment_text: str) -> dict:
    """
    YouTube動画にコメントを投稿する。

    Returns:
        {"success": True, "comment_id": "..."} or {"success": False, "error": "..."}
    """
    if not _is_configured():
        return {"success": False, "error": "YouTube API未設定（YOUTUBE_CLIENT_ID / YOUTUBE_CLIENT_SECRET / YOUTUBE_REFRESH_TOKEN）"}

    video_id = extract_video_id(video_id_or_url)

    try:
        access_token = _get_access_token()
    except Exception as e:
        return {"success": False, "error": f"アクセストークン取得失敗: {e}"}

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    body = {
        "snippet": {
            "videoId": video_id,
            "topLevelComment": {
                "snippet": {"textOriginal": comment_text}
            }
        }
    }

    try:
        resp = requests.post(
            COMMENT_URL,
            params={"part": "snippet"},
            json=body,
            headers=headers,
        )
        data = resp.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

    if resp.status_code in [200, 201]:
        comment_id = data.get("id", "")
        return {"success": True, "comment_id": comment_id, "video_id": video_id}

    error_msg = data.get("error", {}).get("message", resp.text)
    return {"success": False, "error": error_msg}
