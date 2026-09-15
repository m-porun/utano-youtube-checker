"""永続 JSON の検証・安定出力・優先順位マージ。"""

import json
import re
from pathlib import Path
from typing import Any

from .timestamps import normalize_timestamp

VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")


def _fail(path: Path, message: str) -> ValueError:
    return ValueError(f"{path}: {message}")


def load_json(path: Path, kind: str) -> dict[str, Any]:
    """指定種別の JSON を読み、最小スキーマを検証する。"""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{path}: JSON を読めません") from error
    if not isinstance(data, dict) or not isinstance(data.get("videos"), dict):
        raise _fail(path, "videos オブジェクトが必要です")
    if kind == "baseline" and set(data) != {"source", "videos"}:
        raise _fail(path, "source と videos だけが必要です")
    if kind == "baseline" and data["source"] is not None and not isinstance(data["source"], str):
        raise _fail(path, "source は文字列または null です")
    for video_id, record in data["videos"].items():
        if not isinstance(video_id, str) or not VIDEO_ID.fullmatch(video_id):
            raise _fail(path, "動画 ID が不正です")
        if not isinstance(record, dict):
            raise _fail(path, "動画レコードが不正です")
        if not isinstance(record.get("count"), int) or record["count"] < 0:
            raise _fail(path, f"{video_id}: count は0以上の整数です")
        timestamps = record.get("timestamps")
        if not isinstance(timestamps, list) or not all(
            isinstance(value, str) for value in timestamps
        ):
            raise _fail(path, f"{video_id}: timestamps は文字列配列です")
        if len(timestamps) != record["count"]:
            raise _fail(path, f"{video_id}: count と timestamps 件数が一致しません")
        try:
            record["timestamps"] = [normalize_timestamp(value) for value in timestamps]
        except ValueError as error:
            raise _fail(path, f"{video_id}: {error}") from error
        if kind == "counts" and not isinstance(record.get("setlist_found"), bool):
            raise _fail(path, f"{video_id}: setlist_found は真偽値です")
        if kind == "overrides" and (
            not isinstance(record.get("reason"), str)
            or not isinstance(record.get("decided_on"), str)
            or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", record["decided_on"])
        ):
            raise _fail(path, f"{video_id}: reason と YYYY-MM-DD の decided_on が必要です")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    """キー順・末尾改行を固定して JSON を書き出す。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(content, encoding="utf-8")


def merged_videos(
    baseline: dict[str, Any], counts: dict[str, Any], overrides: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """overrides > baseline > counts の順で配信記録を解決する。"""
    result = dict(counts["videos"])
    result.update(baseline["videos"])
    result.update(overrides["videos"])
    return result
