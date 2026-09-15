"""collector の CLI と日次更新オーケストレーション。"""

import argparse
import os
import sys
from pathlib import Path
from typing import Any

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
    """環境変数だけから API クライアントを作る。値は例外へ含めない。"""
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY が設定されていません")
    return build("youtube", "v3", developerKey=api_key)


def update(
    client: Any,
    baseline_path: Path,
    counts_path: Path,
    overrides_path: Path,
    report_path: Path,
) -> bool:
    """baseline 外のライブ配信だけを再集計し、変更時だけ counts を保存する。"""
    baseline = load_json(baseline_path, "baseline")
    counts = load_json(counts_path, "counts")
    overrides = load_json(overrides_path, "overrides")
    live = fetch_live_videos(client, fetch_upload_ids(client))
    old = counts["videos"]
    next_records: dict[str, dict[str, Any]] = {}
    titles: dict[str, str] = {}
    setlists: dict[str, str | None] = {}
    for video_id, metadata in live.items():
        if video_id in baseline["videos"]:
            continue
        titles[video_id] = metadata["title"]
        comments = fetch_comments(client, video_id)
        setlist = extract_setlist(comments or []) if comments is not None else None
        setlists[video_id] = setlist
        matches = count_rokko(setlist)
        previous = old.get(video_id)
        if previous and previous["count"] > 0 and setlist is None:
            next_records[video_id] = dict(previous)
            next_records[video_id]["setlist_found"] = False
        else:
            next_records[video_id] = {
                "count": len(matches),
                "timestamps": [stamp for _, stamp in matches],
                "setlist_found": setlist is not None,
            }
    removed = sorted(set(old) - set(live))
    changes = {
        video_id: (old.get(video_id), next_records.get(video_id))
        for video_id in set(old) | set(next_records)
        if old.get(video_id) != next_records.get(video_id)
    }
    changed = bool(changes)
    if changed:
        write_json(counts_path, {"videos": next_records})
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        build_report(changes, titles, setlists, removed, set(overrides["videos"])),
        encoding="utf-8",
    )
    return changed


def parser() -> argparse.ArgumentParser:
    """CLI 引数定義を作る。"""
    result = argparse.ArgumentParser(prog="python -m collector")
    commands = result.add_subparsers(dest="command", required=True)
    update_parser = commands.add_parser("update")
    update_parser.add_argument("--report", type=Path, required=True)
    imported = commands.add_parser("import-baseline")
    imported.add_argument("--csv", type=Path, required=True)
    imported.add_argument("--overrides", type=Path, default=Path("data/overrides.json"))
    imported.add_argument("--out", type=Path, default=Path("data/baseline.json"))
    imported.add_argument("--source-name")
    site = commands.add_parser("build-site")
    site.add_argument("--out", type=Path, required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    """CLI を実行し、キー未設定は終了コード2にする。"""
    args = parser().parse_args(argv)
    if args.command == "import-baseline":
        run_import(args.csv, args.overrides, args.out, args.source_name)
        return 0
    try:
        client = require_client()
    except RuntimeError as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 2
    try:
        if args.command == "update":
            changed = update(
                client,
                Path("data/baseline.json"),
                Path("data/counts.json"),
                Path("data/overrides.json"),
                args.report,
            )
            print(f"changed={str(changed).lower()}")
            return 0
        baseline = load_json(Path("data/baseline.json"), "baseline")
        counts = load_json(Path("data/counts.json"), "counts")
        overrides = load_json(Path("data/overrides.json"), "overrides")
        write_site(args.out, build_site_data(client, baseline, counts, overrides))
        return 0
    except HttpError as error:
        print(f"エラー: YouTube API がステータス {error.resp.status} を返しました", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
