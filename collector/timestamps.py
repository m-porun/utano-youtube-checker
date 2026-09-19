"""タイムスタンプの純粋ロジック。"""

import re

_TIMESTAMP = re.compile(r"^(?:(\d{1,2}):)?(\d{1,2}):(\d{2})$")


def normalize_timestamp(value: str) -> str:
    """h:mm:ss 形式へ正規化し、範囲外の値は拒否する。"""
    match = _TIMESTAMP.fullmatch(value.strip())
    if not match:
        raise ValueError(f"不正なタイムスタンプ形式: {value!r}")
    hour_text, minute_text, second_text = match.groups()
    hour = int(hour_text or 0)
    minute, second = int(minute_text), int(second_text)
    if minute > 59 or second > 59:
        raise ValueError(f"不正なタイムスタンプ値: {value!r}")
    return f"{hour}:{minute:02}:{second:02}"


def timestamp_seconds(value: str) -> int:
    """正規化可能なタイムスタンプを秒数に変換する。"""
    hour, minute, second = (int(part) for part in normalize_timestamp(value).split(":"))
    return hour * 3600 + minute * 60 + second
