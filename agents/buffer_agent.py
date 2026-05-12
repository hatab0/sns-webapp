"""
Buffer投稿エージェント（Webアプリ版）
Buffer APIを使ってInstagram・Threadsに予約投稿する。
投稿時刻は「現在時刻 + 3分後」を基準とする。
"""
import requests
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

JST = timezone(timedelta(hours=9))

load_dotenv()

BUFFER_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")
BUFFER_ORG_ID = os.getenv("BUFFER_ORGANIZATION_ID")
BUFFER_GRAPHQL = "https://api.buffer.com/graphql"


def get_headers() -> dict:
    return {
        "Authorization": f"Bearer {BUFFER_TOKEN}",
        "Content-Type": "application/json",
    }


def get_base_post_time() -> datetime:
    """現在のJST時刻 + 3分を基準投稿時刻として返す"""
    return datetime.now(tz=JST) + timedelta(minutes=3)


def get_profiles() -> list:
    """Bufferに連携されているチャンネル一覧を取得する"""
    query = """
    query GetChannels($input: ChannelsInput!) {
      channels(input: $input) {
        id
        name
        service
      }
    }
    """
    variables = {"input": {"organizationId": BUFFER_ORG_ID}}
    response = requests.post(
        BUFFER_GRAPHQL,
        json={"query": query, "variables": variables},
        headers=get_headers()
    )
    if response.status_code != 200:
        return []
    data = response.json()
    return data.get("data", {}).get("channels", [])


def schedule_post(
    channel_id: str,
    caption: str,
    scheduled_at: str,
    video_url: str = None,
    service: str = "threads",
    youtube_title: str = "",
) -> dict:
    """Bufferに投稿を予約する"""
    if not BUFFER_TOKEN:
        return {"success": False, "error": "BUFFER_ACCESS_TOKEN未設定"}

    mutation = """
    mutation CreatePost($input: CreatePostInput!) {
      createPost(input: $input) {
        ... on PostActionSuccess {
          post { id status dueAt }
        }
        ... on InvalidInputError { message }
        ... on UnauthorizedError { message }
        ... on LimitReachedError { message }
        ... on UnexpectedError { message }
      }
    }
    """
    post_input = {
        "channelId": channel_id,
        "text": caption,
        "dueAt": scheduled_at,
        "schedulingType": "automatic",
        "mode": "customScheduled",
    }
    if service == "instagram":
        post_input["metadata"] = {"instagram": {"type": "reel", "shouldShareToFeed": True}}
        if video_url:
            post_input["assets"] = {"videos": [{"url": video_url}]}
    elif service == "threads":
        if video_url:
            post_input["assets"] = {"videos": [{"url": video_url}]}
    elif service == "youtube":
        post_input["metadata"] = {"youtube": {
            "title": youtube_title or "Baby Boo 育児vlog",
            "privacy": "public",
            "categoryId": "22",
            "madeForKids": False,
        }}
        if video_url:
            post_input["assets"] = {"videos": [{"url": video_url}]}

    response = requests.post(
        BUFFER_GRAPHQL,
        json={"query": mutation, "variables": {"input": post_input}},
        headers=get_headers()
    )
    try:
        resp_json = response.json()
    except Exception:
        return {"success": False, "error": response.text}

    if resp_json.get("errors"):
        msgs = [e.get("message", "") for e in resp_json["errors"]]
        return {"success": False, "error": " | ".join(msgs)}

    if response.status_code in [200, 201]:
        payload = resp_json.get("data", {}).get("createPost", {})
        post = payload.get("post", {})
        if post.get("id"):
            return {"success": True, "buffer_id": post["id"], "scheduled_at": post.get("dueAt", scheduled_at)}
        return {"success": False, "error": payload.get("message", str(resp_json))}
    return {"success": False, "error": response.text}


def run(scripts: list, video_url: str = None, platforms: list = None) -> list:
    """
    3種類のコンテンツをBuffer予約投稿する。

    投稿時刻（現在時刻を基準）:
      threads_product → +3分
      threads_buzz    → +33分
      reel instagram  → +3分
      reel threads    → +48分

    platforms: ["instagram"] / ["threads"] / None（全て）
    video_url: CloudinaryのURL（Instagram Reel用）
    """
    if not BUFFER_TOKEN:
        return scripts

    profiles = get_profiles()
    if not profiles:
        return scripts

    platform_map = {"instagram": None, "threads": None, "youtube": None}
    for ch in profiles:
        service = ch.get("service", "").lower()
        if "instagram" in service:
            platform_map["instagram"] = ch["id"]
        elif "threads" in service:
            platform_map["threads"] = ch["id"]
        elif "youtube" in service:
            platform_map["youtube"] = ch["id"]

    base = get_base_post_time()

    def fmt(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%dT%H:%M:%S+09:00")

    time_threads      = fmt(base)                          # threads_text: +3分
    time_reel_ig      = fmt(base)                          # Instagram Reel: +3分
    time_reel_threads = fmt(base + timedelta(minutes=45))  # Threads 動画: +48分

    results = []
    for script in scripts:
        ctype = script.get("type", "")
        captions = script.get("captions", {})
        post_results = {}

        if ctype == "threads_text":
            if not (platforms and "threads" not in platforms) and platform_map["threads"]:
                r = schedule_post(platform_map["threads"], captions.get("threads", ""), time_threads, service="threads")
                post_results["threads"] = r

        elif ctype == "reel":
            if not (platforms and "instagram" not in platforms) and platform_map["instagram"] and video_url:
                r = schedule_post(platform_map["instagram"], captions.get("instagram", ""), time_reel_ig, video_url=video_url, service="instagram")
                post_results["instagram"] = r

            if not (platforms and "threads" not in platforms) and platform_map["threads"] and video_url:
                r = schedule_post(platform_map["threads"], captions.get("threads", ""), time_reel_threads, video_url=video_url, service="threads")
                post_results["threads_reel"] = r

            if not (platforms and "youtube" not in platforms) and platform_map["youtube"] and video_url:
                r = schedule_post(
                    platform_map["youtube"],
                    captions.get("youtube", ""),
                    time_reel_ig,
                    video_url=video_url,
                    service="youtube",
                    youtube_title=captions.get("youtube_title", ""),
                )
                post_results["youtube"] = r

        script["buffer_posts"] = post_results
        results.append(script)

    return results
