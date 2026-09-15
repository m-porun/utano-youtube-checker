"""確認済みスプレッドシート CSV の一度限りのインポート。"""

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .store import load_json, write_json
from .timestamps import normalize_timestamp

VIDEO_ID_LENGTH = 11


def video_id_from_url(value: str) -> str:
    """YouTube URL の v パラメータから正規の動画 ID を抽出する。"""
    video_id = parse_qs(urlparse(value).query).get("v", [""])[0]
    if len(video_id) != VIDEO_ID_LENGTH or not all(
        char.isalnum() or char in "_-" for char in video_id
    ):
        raise ValueError(f"不正な動画URL: {value}")
    return video_id


def import_baseline(
    csv_path: Path, overrides_path: Path, source_name: str | None = None
) -> dict[str, Any]:
    """CSV を baseline 構造に変換し、矛盾は override がない限り拒否する。"""
    overrides = load_json(overrides_path, "overrides")["videos"]
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    with csv_path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        required = {"動画URL", "六甲おろしが歌われた数", "タイムスタンプ"}
        if not reader.fieldnames or not required <= set(reader.fieldnames):
            raise ValueError("CSV ヘッダーが不足しています")
        for row in reader:
            groups[video_id_from_url(row["動画URL"])].append(row)
    videos: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for video_id, rows in groups.items():
        try:
            count = int(rows[0]["六甲おろしが歌われた数"])
        except ValueError as error:
            raise ValueError(f"{video_id}: 回数が整数ではありません") from error
        if any(row["六甲おろしが歌われた数"] != str(count) for row in rows):
            raise ValueError(f"{video_id}: 回数列が一致しません")
        timestamps = [
            normalize_timestamp(row["タイムスタンプ"])
            for row in rows
            if row["タイムスタンプ"].strip()
        ]
        if len(timestamps) != count:
            if video_id in overrides:
                videos[video_id] = {
                    "count": overrides[video_id]["count"],
                    "timestamps": overrides[video_id]["timestamps"],
                }
            else:
                errors.append(video_id)
        else:
            videos[video_id] = {"count": count, "timestamps": timestamps}
    if errors:
        raise ValueError("回数とタイムスタンプ件数が不一致: " + ", ".join(sorted(errors)))
    return {"source": source_name or csv_path.name, "videos": videos}


def run_import(
    csv_path: Path, overrides_path: Path, out_path: Path, source_name: str | None
) -> None:
    """インポート I/O を実行する。"""
    write_json(out_path, import_baseline(csv_path, overrides_path, source_name))
