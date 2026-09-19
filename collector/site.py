"""公開用 JSON をビルド時だけ生成する。"""

from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .store import write_json
from .youtube import fetch_video_titles


def build_site_data(client: Any, data: dict[str, Any], today: str | None = None) -> dict[str, Any]:
    """videos.json の回数と API タイトルから公開データを作る。"""
    records = {key: value for key, value in data["videos"].items() if value["count"] > 0}
    titles = fetch_video_titles(client, list(records))
    videos = [
        {
            "videoId": key,
            "title": titles.get(key),
            "rokkoCount": value["count"],
            "timestamps": value["timestamps"],
        }
        for key, value in records.items()
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
