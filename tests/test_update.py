from pathlib import Path
from unittest.mock import MagicMock

import pytest

from collector import __main__ as cli
from collector.store import load_json, write_json


def _paths(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    names = ("baseline.json", "counts.json", "overrides.json", "report.md")
    baseline, counts, overrides, report = (tmp_path / name for name in names)
    write_json(baseline, {"source": None, "videos": {}})
    write_json(overrides, {"videos": {}})
    return baseline, counts, overrides, report


def _live() -> dict[str, dict[str, str]]:
    return {"abcD_efG-12": {"title": "title", "actualStartTime": "time"}}


def test_update_writes_counts_and_reports_changes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    baseline, counts, overrides, report = _paths(tmp_path)
    write_json(counts, {"videos": {}})
    monkeypatch.setattr(cli, "fetch_upload_ids", lambda client: ["abcD_efG-12"])
    monkeypatch.setattr(cli, "fetch_live_videos", lambda client, ids: _live())
    monkeypatch.setattr(cli, "fetch_comments", lambda client, video_id: ["TS\n0:01:02 六甲おろし"])
    assert cli.update(MagicMock(), baseline, counts, overrides, report)
    assert load_json(counts, "counts")["videos"]["abcD_efG-12"]["count"] == 1
    assert "title" in report.read_text(encoding="utf-8")


def test_update_removes_deleted_videos_and_reports_them(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    baseline, counts, overrides, report = _paths(tmp_path)
    write_json(
        counts,
        {"videos": {"abcD_efG-12": {"count": 0, "timestamps": [], "setlist_found": True}}},
    )
    monkeypatch.setattr(cli, "fetch_upload_ids", lambda client: [])
    monkeypatch.setattr(cli, "fetch_live_videos", lambda client, ids: {})
    assert cli.update(MagicMock(), baseline, counts, overrides, report)
    assert load_json(counts, "counts")["videos"] == {}
    assert "削除・非公開" in report.read_text(encoding="utf-8")


def test_update_keeps_previous_record_when_setlist_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    baseline, counts, overrides, report = _paths(tmp_path)
    record = {"count": 1, "timestamps": ["0:01:02"], "setlist_found": True}
    write_json(counts, {"videos": {"abcD_efG-12": record}})
    monkeypatch.setattr(cli, "fetch_upload_ids", lambda client: ["abcD_efG-12"])
    monkeypatch.setattr(cli, "fetch_live_videos", lambda client, ids: _live())
    monkeypatch.setattr(cli, "fetch_comments", lambda client, video_id: None)
    assert cli.update(MagicMock(), baseline, counts, overrides, report)
    saved = load_json(counts, "counts")["videos"]["abcD_efG-12"]
    assert saved["count"] == 1 and saved["timestamps"] == ["0:01:02"]
    assert saved["setlist_found"] is False
    assert "前回値を維持" in report.read_text(encoding="utf-8")


def test_update_does_not_crash_on_invalid_timestamp_in_comment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    baseline, counts, overrides, report = _paths(tmp_path)
    write_json(counts, {"videos": {}})
    monkeypatch.setattr(cli, "fetch_upload_ids", lambda client: ["abcD_efG-12"])
    monkeypatch.setattr(cli, "fetch_live_videos", lambda client, ids: _live())
    monkeypatch.setattr(cli, "fetch_comments", lambda client, video_id: ["TS\n12:99:99 六甲おろし"])
    assert cli.update(MagicMock(), baseline, counts, overrides, report)
