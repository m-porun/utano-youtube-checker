"""videos.json の検証と安定出力。"""

import json
import re
from pathlib import Path
from typing import Any

from .timestamps import normalize_timestamp

VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load_json(path: Path) -> dict[str, Any]:
    """単一の集計ファイルを読み、レコードスキーマを検証する。"""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{path}: JSON を読めません") from error
    try:
        validate(data)
    except ValueError as error:
        raise ValueError(f"{path}: {error}") from error
    return data


def validate(data: Any) -> None:
    """videos.json のメモリ上データを検証する。"""
    if not isinstance(data, dict) or set(data) != {"source", "videos"}:
        raise ValueError("source と videos が必要です")
    if data["source"] is not None and not isinstance(data["source"], str):
        raise ValueError("source は文字列または null です")
    if not isinstance(data["videos"], dict):
        raise ValueError("videos はオブジェクトです")
    for video_id, record in data["videos"].items():
        if not isinstance(video_id, str) or not VIDEO_ID.fullmatch(video_id):
            raise ValueError("動画 ID が不正です")
        if not isinstance(record, dict) or type(record.get("count")) is not int:
            raise ValueError(f"{video_id}: count は整数です")
        if record["count"] < 0 or not isinstance(record.get("confirmed"), bool):
            raise ValueError(f"{video_id}: count または confirmed が不正です")
        timestamps = record.get("timestamps")
        if not isinstance(timestamps, list) or not all(
            isinstance(value, str) for value in timestamps
        ):
            raise ValueError(f"{video_id}: timestamps は文字列配列です")
        if len(timestamps) != record["count"]:
            raise ValueError(f"{video_id}: count と timestamps 件数が一致しません")
        record["timestamps"] = [normalize_timestamp(value) for value in timestamps]
        if not record["confirmed"] and not isinstance(record.get("setlist_found"), bool):
            raise ValueError(f"{video_id}: setlist_found が必要です")
        reason = record.get("reason")
        decided_on = record.get("decided_on")
        if (reason is None) != (decided_on is None):
            raise ValueError(f"{video_id}: reason と decided_on は対で指定します")
        if reason is not None and (
            not isinstance(reason, str)
            or not isinstance(decided_on, str)
            or not DATE.fullmatch(decided_on)
        ):
            raise ValueError(f"{video_id}: reason または decided_on が不正です")


def write_json(path: Path, data: dict[str, Any]) -> None:
    """キー順・インデント・末尾改行を固定して書き出す。"""
    content = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
