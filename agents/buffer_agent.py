"""
Buffer投稿エージェント（Webアプリ版）
Buffer APIを使ってInstagram・TikTok・YouTubeに予約投稿する。
投稿時刻はプラットフォームごとのピーク時間帯に自動スケジュール。
枠が重複した場合は次のピーク枠に自動スライド。
（Threads廃止済み）
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

# ── プラットフォームごとのピーク時間帯（JST, 24h表記）
PEAK_SLOTS = {
    "instagram": [(12, 0), (19, 0), (21, 0)],
    "tiktok":    [(12, 0), (15, 0), (18, 0), (19, 0), (21, 0)],
    "youtube":   [(12, 0), (20, 0), (22, 0)],
}

# ── 同一セッション内で今回予約したスロットを記録（APIで取れない直後の重複防止）
_used_slots: dict = {"instagram": [], "tiktok": [], "youtube": []}


def _get_scheduled_slots(channel_id: str) -> list:
    """Buffer APIから既存の予約済み投稿の時刻一覧を取得する"""
    query = """
    query GetPosts($input: PostsInput!) {
      posts(input: $input) {
        edges {
          node {
            dueAt
          }
        }
      }
    }
    """
    try:
        response = requests.post(
            BUFFER_GRAPHQL,
            json={"query": query, "variables": {"input": {"channelId": channel_id, "status": "scheduled"}}},
            headers=get_headers(),
            timeout=10,
        )
        edges = response.json().get("data", {}).get("posts", {}).get("edges", [])
        slots = []
        for edge in edges:
            due = edge.get("node", {}).get("dueAt")
            if due:
                dt = datetime.fromisoformat(due.replace("Z", "+00:00")).astimezone(JST)
                slots.append(dt)
        return slots
    except Exception:
        return []


def _get_next_peak_slot(platform: str, channel_id: str = None) -> datetime:
    """
    指定プラットフォームの次のピーク枠を返す。
    - Buffer APIの既存予約 + 今セッションで予約済みの枠を両方チェック
    - 使用済み枠と30分以内に重なる場合は次の枠へスライド
    """
    now = datetime.now(tz=JST)
    min_time = now + timedelta(minutes=5)
    slots = PEAK_SLOTS.get(platform, PEAK_SLOTS["instagram"])
    buffer_used = _get_scheduled_slots(channel_id) if channel_id else []
    used = _used_slots.get(platform, []) + buffer_used

    for day_offset in range(5):
        base = (now + timedelta(days=day_offset)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        for h, m in sorted(slots):
            slot_dt = base.replace(hour=h, minute=m)
            if slot_dt <= min_time:
                continue
            if any(abs((slot_dt - u).total_seconds()) < 1800 for u in used):
                continue
            _used_slots[platform].append(slot_dt)
            return slot_dt

    # フォールバック（念のため）
    fallback = min_time + timedelta(hours=3)
    _used_slots[platform].append(fallback)
    return fallback


def _fmt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S+09:00")


def get_headers() -> dict:
    return {
        "Authorization": f"Bearer {BUFFER_TOKEN}",
        "Content-Type": "application/json",
    }


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
    service: str = "instagram",
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
            post_input["assets"] = {"video": {"url": video_url}}
    elif service == "tiktok":
        if video_url:
            post_input["assets"] = {"video": {"url": video_url}}
    elif service == "youtube":
        post_input["metadata"] = {"youtube": {
            "title": youtube_title or "Baby Boo 育児vlog",
            "privacy": "public",
            "categoryId": "22",
            "madeForKids": False,
        }}
        if video_url:
            post_input["assets"] = {"video": {"url": video_url}}

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
    コンテンツをBufferのピーク時間帯に予約投稿する。

    投稿時刻: プラットフォームごとのピーク枠（PEAK_SLOTS）から
              次の空き枠を自動選択。枠が重なった場合は次の枠へスライド。

    platforms: ["instagram"] / ["tiktok"] / ["youtube"] / None（全て）
    video_url: CloudinaryのURL（動画投稿用）
    """
    if not BUFFER_TOKEN:
        return scripts

    profiles = get_profiles()
    if not profiles:
        return scripts

    platform_map = {"instagram": None, "tiktok": None, "youtube": None}
    for ch in profiles:
        service = ch.get("service", "").lower()
        if "instagram" in service:
            platform_map["instagram"] = ch["id"]
        elif "tiktok" in service:
            platform_map["tiktok"] = ch["id"]
        elif "youtube" in service:
            platform_map["youtube"] = ch["id"]

    results = []
    for script in scripts:
        ctype = script.get("type", "")
        captions = script.get("captions", {})
        post_results = {}

        if ctype == "reel":
            if not (platforms and "instagram" not in platforms) and platform_map["instagram"] and video_url:
                slot = _fmt(_get_next_peak_slot("instagram", platform_map["instagram"]))
                r = schedule_post(platform_map["instagram"], captions.get("instagram", ""), slot, video_url=video_url, service="instagram")
                post_results["instagram"] = r

            if not (platforms and "tiktok" not in platforms) and platform_map["tiktok"] and video_url:
                slot = _fmt(_get_next_peak_slot("tiktok", platform_map["tiktok"]))
                r = schedule_post(platform_map["tiktok"], captions.get("tiktok", ""), slot, video_url=video_url, service="tiktok")
                post_results["tiktok"] = r

            if not (platforms and "youtube" not in platforms) and platform_map["youtube"] and video_url:
                slot = _fmt(_get_next_peak_slot("youtube", platform_map["youtube"]))
                r = schedule_post(
                    platform_map["youtube"],
                    captions.get("youtube", ""),
                    slot,
                    video_url=video_url,
                    service="youtube",
                    youtube_title=captions.get("youtube_title", ""),
                )
                post_results["youtube"] = r

        script["buffer_posts"] = post_results
        results.append(script)

    return results
