"""
せなっちの基本設定（一元管理）
ここだけ変更すれば全エージェントに反映される。
"""
from datetime import date


# せなっちの誕生日
BIRTH_DATE = date(2025, 12, 22)


def calc_month_age() -> int:
    """誕生日から現在の月齢を計算して返す"""
    today = date.today()
    months = (today.year - BIRTH_DATE.year) * 12 + (today.month - BIRTH_DATE.month)
    if today.day < BIRTH_DATE.day:
        months -= 1
    return max(0, months)


def calc_weeks_alive() -> int:
    """誕生日からの総週数を返す"""
    return (date.today() - BIRTH_DATE).days // 7


def calc_week_in_month() -> int:
    """現在の月内の週番号（1〜5）を返す"""
    return ((date.today() - BIRTH_DATE).days % 30) // 7 + 1
