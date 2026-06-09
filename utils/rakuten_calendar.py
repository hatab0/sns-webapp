"""
楽天イベントカレンダー
マラソン/スーパーセールの日程を管理し、3日前アラートを提供する。
確認済み日程 + 傾向ベースの予想日程（予想はFalseフラグで区別）。
"""
from datetime import date, timedelta
from typing import Optional

# (開始日, 終了日, イベント種別, 公式確認済み)
# 傾向: マラソンは毎月4日/9日/14日/19日/24日前後スタート、約5〜7日間
# スーパーセール: 3月・6月・9月・12月の年4回、約7〜8日間
RAKUTEN_EVENTS: list[tuple] = [
    # ── 2026年（確認済み）
    ("2026-01-09", "2026-01-16", "marathon",   True),
    ("2026-04-04", "2026-04-10", "marathon",   True),
    ("2026-04-14", "2026-04-17", "marathon",   True),
    ("2026-04-24", "2026-04-27", "marathon",   True),
    ("2026-05-09", "2026-05-16", "marathon",   True),
    ("2026-06-04", "2026-06-11", "super_sale", True),
    ("2026-06-22", "2026-06-27", "marathon",   True),
    # ── 2026年（予想）
    ("2026-07-09", "2026-07-16", "marathon",   False),
    ("2026-07-24", "2026-07-31", "marathon",   False),
    ("2026-08-04", "2026-08-11", "marathon",   False),
    ("2026-08-19", "2026-08-26", "marathon",   False),
    ("2026-09-04", "2026-09-11", "super_sale", False),
    ("2026-09-19", "2026-09-26", "marathon",   False),
    ("2026-10-09", "2026-10-16", "marathon",   False),
    ("2026-10-24", "2026-10-31", "marathon",   False),
    ("2026-11-04", "2026-11-11", "marathon",   False),
    ("2026-11-19", "2026-11-26", "marathon",   False),
    ("2026-12-04", "2026-12-11", "super_sale", False),
]

_LABEL = {
    "marathon":   "楽天お買い物マラソン",
    "super_sale": "楽天スーパーセール",
}
_EMOJI = {
    "marathon":   "🏃",
    "super_sale": "⭐",
}


def _build(start: date, end: date, etype: str, confirmed: bool) -> dict:
    return {
        "label":     _LABEL[etype],
        "emoji":     _EMOJI[etype],
        "type":      etype,
        "start":     start,
        "end":       end,
        "confirmed": confirmed,
    }


def get_marathon_alert(days_before: int = 3, today: date = None) -> Optional[dict]:
    """
    3日前〜終了日までの期間に入っているイベントがあれば返す。
    is_active=True  → 現在開催中
    is_active=False → days_before日以内に開始
    なければ None。
    """
    today = today or date.today()
    for start_str, end_str, etype, confirmed in RAKUTEN_EVENTS:
        start = date.fromisoformat(start_str)
        end   = date.fromisoformat(end_str)
        if (start - timedelta(days=days_before)) <= today <= end:
            info = _build(start, end, etype, confirmed)
            info["days_until_start"] = (start - today).days
            info["is_active"]        = today >= start
            return info
    return None


def get_next_marathon(today: date = None) -> Optional[dict]:
    """次回のイベント情報を返す（アラート期間外でも常に取得できる）"""
    today = today or date.today()
    future = [
        (date.fromisoformat(s), date.fromisoformat(e), t, c)
        for s, e, t, c in RAKUTEN_EVENTS
        if date.fromisoformat(s) > today
    ]
    if not future:
        return None
    future.sort()
    start, end, etype, confirmed = future[0]
    info = _build(start, end, etype, confirmed)
    info["days_until_start"] = (start - today).days
    info["is_active"]        = False
    return info
