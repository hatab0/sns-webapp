"""
Cloudinaryアップロードヘルパー
Streamlitのfile_uploaderから受け取ったbytesをCloudinaryにアップロードする
"""
import os
import cloudinary
import cloudinary.uploader


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
