"""確認済み CSV を確定済み videos.json に変換する。"""

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .store import VIDEO_ID, validate, write_json
from .timestamps import normalize_timestamp


def _video_id(value: str) -> str:
    video_id = parse_qs(urlparse(value).query).get("v", [""])[0]
    if not VIDEO_ID.fullmatch(video_id):
        raise ValueError(f"不正な動画URL: {value}")
    return video_id


def import_confirmed(
    csv_path: Path,
    corrections: dict[str, int],
    reason: str,
    decided_on: str,
    source_name: str | None,
) -> dict[str, Any]:
    """CSV から、すべて確定済みのレコードを生成する。"""
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    with csv_path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        required = {"動画URL", "六甲おろしが歌われた数", "タイムスタンプ"}
        if not reader.fieldnames or not required <= set(reader.fieldnames):
            raise ValueError("CSV ヘッダーが不足しています")
        for row in reader:
            groups[_video_id(row["動画URL"])].append(row)
    videos: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for video_id, rows in groups.items():
        count = int(rows[0]["六甲おろしが歌われた数"])
        if any(row["六甲おろしが歌われた数"] != str(count) for row in rows):
            raise ValueError(f"{video_id}: 回数列が一致しません")
        timestamps = [
            normalize_timestamp(row["タイムスタンプ"]) for row in rows if row["タイムスタンプ"]
        ]
        if len(timestamps) != count and video_id not in corrections:
            errors.append(video_id)
            continue
        value = corrections.get(video_id, count)
        if video_id in corrections and value != 0:
            raise ValueError(f"{video_id}: 補正は0だけ指定できます。CSV 側を修正してください")
        record: dict[str, Any] = {
            "count": value,
            "timestamps": timestamps if value == count else [],
            "confirmed": True,
        }
        if video_id in corrections:
            record.update({"reason": reason, "decided_on": decided_on})
        videos[video_id] = record
    if errors:
        raise ValueError("回数とタイムスタンプ件数が不一致: " + ", ".join(errors))
    result = {"source": source_name or csv_path.name, "videos": videos}
    validate(result)
    return result


def run_import(
    csv_path: Path,
    out_path: Path,
    source_name: str | None,
    corrections: list[str],
    reason: str,
    decided_on: str,
    force: bool,
) -> None:
    """CLI の補正指定を解析してインポート結果を書き出す。"""
    if out_path.exists() and not force:
        raise ValueError(f"{out_path} は既に存在します。上書きには --force を使用してください")
    parsed: dict[str, int] = {}
    for item in corrections:
        video_id, separator, count_text = item.partition("=")
        if not separator or not VIDEO_ID.fullmatch(video_id) or not count_text.isdecimal():
            raise ValueError("--correction は <videoId>=<count> 形式で指定してください")
        parsed[video_id] = int(count_text)
    result = import_confirmed(csv_path, parsed, reason, decided_on, source_name)
    write_json(out_path, result)
