"""公開用 JSON をビルド時だけ生成する。"""

from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .store import merged_videos, write_json
from .youtube import fetch_video_titles


def build_site_data(
    client: Any,
    baseline: dict[str, Any],
    counts: dict[str, Any],
    overrides: dict[str, Any],
    today: str | None = None,
) -> dict[str, Any]:
    """保存済み集計と短命なタイトルを公開スキーマへ変換する。"""
    records = merged_videos(baseline, counts, overrides)
    positive = {video_id: record for video_id, record in records.items() if record["count"] > 0}
    titles = fetch_video_titles(client, list(positive))
    videos = [
        {
            "videoId": video_id,
            "title": titles.get(video_id),
            "rokkoCount": record["count"],
            "timestamps": record["timestamps"],
        }
        for video_id, record in positive.items()
    ]
    videos.sort(
        key=lambda value: (
            -value["rokkoCount"],
            value["title"] is None,
            value["title"] or "",
            value["videoId"],
        )
    )
    return {
        "totalCount": sum(value["rokkoCount"] for value in videos),
        "updatedAt": today or datetime.now(ZoneInfo("Asia/Tokyo")).date().isoformat(),
        "videos": videos,
    }


def write_site(path: Path, data: dict[str, Any]) -> None:
    """公開 JSON を安定した形式で書き出す。"""
    write_json(path, data)
