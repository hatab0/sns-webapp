"""
Cloudinaryアップロードヘルパー
Streamlitのfile_uploaderから受け取ったbytesをCloudinaryにアップロードする
"""
import os
from datetime import datetime, timedelta, timezone
import cloudinary
import cloudinary.uploader
import cloudinary.api


def _configure():
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True,
    )


def upload_bytes(data: bytes, resource_type: str = "image") -> str:
    """
    bytesデータをCloudinaryにアップロードして公開URLを返す。
    resource_type: "image" or "video"
    """
    _configure()
    try:
        result = cloudinary.uploader.upload(
            data,
            resource_type=resource_type,
            folder="senacchi",
        )
        return result.get("secure_url", "")
    except Exception as e:
        print(f"Cloudinaryアップロードエラー: {e}")
        return ""


def list_assets(days_old: int = 30, resource_type: str = "video") -> list:
    """指定日数以上前にアップロードされたアセット一覧を返す"""
    _configure()
    try:
        result = cloudinary.api.resources(
            resource_type=resource_type,
            prefix="senacchi/",
            max_results=100,
            type="upload",
        )
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_old)
        old_assets = []
        for r in result.get("resources", []):
            created_at = r.get("created_at", "")
            if created_at:
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                if dt < cutoff:
                    old_assets.append({
                        "public_id":    r["public_id"],
                        "resource_type": resource_type,
                        "created_at":   created_at,
                        "bytes":        r.get("bytes", 0),
                    })
        return old_assets
    except Exception as e:
        print(f"list_assets error: {e}")
        return []


def delete_asset(public_id: str, resource_type: str = "video") -> bool:
    """指定アセットをCloudinaryから削除する"""
    _configure()
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return result.get("result") == "ok"
    except Exception as e:
        print(f"delete_asset error: {e}")
        return False
