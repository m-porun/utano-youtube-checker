"""collector の CLI と日次更新。"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .baseline_import import run_import
from .report import build_report
from .setlist import count_rokko, extract_setlist
from .site import build_site_data, write_site
from .store import load_json, write_json
from .youtube import fetch_comments, fetch_live_videos, fetch_upload_ids


def require_client() -> Any:
    """環境変数から API クライアントを作る。"""
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY が設定されていません")
    return build("youtube", "v3", developerKey=api_key)


def _within_three_days(started_at: str, now: datetime) -> bool:
    started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    return now.astimezone(started.tzinfo) - started <= timedelta(days=3)


def update(client: Any, videos_path: Path, report_path: Path, now: datetime | None = None) -> bool:
    """未登録または3日以内の未確定配信だけを集計する。"""
    data = load_json(videos_path)
    old = data["videos"]
    live = fetch_live_videos(client, fetch_upload_ids(client))
    current = now or datetime.now(ZoneInfo("Asia/Tokyo"))
    next_records = dict(old)
    titles: dict[str, str] = {}
    setlists: dict[str, str | None] = {}
    removed: list[str] = []
    for video_id, record in old.items():
        if video_id not in live and not record["confirmed"]:
            next_records.pop(video_id)
            removed.append(video_id)
    for video_id, metadata in live.items():
        previous = old.get(video_id)
        if previous and previous["confirmed"]:
            continue
        if previous and not _within_three_days(metadata["actualStartTime"], current):
            continue
        titles[video_id] = metadata["title"]
        comments = fetch_comments(client, video_id)
        setlist = extract_setlist(comments or []) if comments is not None else None
        setlists[video_id] = setlist
        matches = count_rokko(setlist)
        if previous and previous["count"] > 0 and setlist is None:
            record = dict(previous)
            record["setlist_found"] = False
        else:
            record = {
                "count": len(matches),
                "timestamps": [stamp for _, stamp in matches],
                "confirmed": False,
                "setlist_found": setlist is not None,
            }
        next_records[video_id] = record
    missing_confirmed = [
        video_id for video_id in sorted(set(old) - set(live)) if old[video_id]["confirmed"]
    ]
    changes = {
        video_id: (old.get(video_id), next_records.get(video_id))
        for video_id in set(old) | set(next_records)
        if old.get(video_id) != next_records.get(video_id)
    }
    changed = bool(changes)
    if changed:
        write_json(videos_path, {"source": data["source"], "videos": next_records})
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        build_report(changes, titles, setlists, removed, missing_confirmed), encoding="utf-8"
    )
    return changed


def parser() -> argparse.ArgumentParser:
    """CLI 引数定義を作る。"""
    result = argparse.ArgumentParser(prog="python -m collector")
    commands = result.add_subparsers(dest="command", required=True)
    updated = commands.add_parser("update")
    updated.add_argument("--report", type=Path, required=True)
    imported = commands.add_parser("import-confirmed")
    imported.add_argument("--csv", type=Path, required=True)
    imported.add_argument("--out", type=Path, default=Path("data/videos.json"))
    imported.add_argument("--source-name")
    imported.add_argument("--correction", action="append", default=[])
    imported.add_argument("--reason", required=True)
    imported.add_argument("--decided-on", required=True)
    site = commands.add_parser("build-site")
    site.add_argument("--out", type=Path, required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    """CLI を実行する。"""
    args = parser().parse_args(argv)
    if args.command == "import-confirmed":
        run_import(
            args.csv,
            args.out,
            args.source_name,
            args.correction,
            args.reason,
            args.decided_on,
        )
        return 0
    try:
        client = require_client()
        if args.command == "update":
            changed = update(client, Path("data/videos.json"), args.report)
            print(f"changed={str(changed).lower()}")
            return 0
        data = load_json(Path("data/videos.json"))
        write_site(args.out, build_site_data(client, data))
        return 0
    except RuntimeError as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 2
    except HttpError as error:
        print(f"エラー: YouTube API がステータス {error.resp.status} を返しました", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
