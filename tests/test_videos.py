import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

import pytest

from collector import __main__ as cli
from collector.baseline_import import import_confirmed
from collector.store import load_json, write_json

VIDEO = "abcD_efG-12"
NOW = datetime(2026, 9, 19, tzinfo=ZoneInfo("Asia/Tokyo"))
HEADER = "動画URL,六甲おろしが歌われた数,タイムスタンプ,動画タイトル,セットリスト\n"


def _record(confirmed: bool = False) -> dict[str, object]:
    return {"count": 0, "timestamps": [], "confirmed": confirmed, "setlist_found": True}


def _update_setup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, record: dict[str, object] | None = None
) -> tuple[Path, Path, MagicMock]:
    path = tmp_path / "videos.json"
    write_json(path, {"source": None, "videos": {VIDEO: record} if record else {}})
    monkeypatch.setattr(cli, "fetch_upload_ids", lambda client: [VIDEO])
    monkeypatch.setattr(
        cli,
        "fetch_live_videos",
        lambda client, ids: {VIDEO: {"title": "title", "actualStartTime": "2026-09-18T00:00:00Z"}},
    )
    comments = MagicMock(return_value=["TS\n0:01:02 六甲おろし"])
    monkeypatch.setattr(cli, "fetch_comments", comments)
    return path, tmp_path / "report.md", comments


def test_update_adds_unregistered_old_video(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path, report, _ = _update_setup(monkeypatch, tmp_path)
    monkeypatch.setattr(
        cli,
        "fetch_live_videos",
        lambda client, ids: {VIDEO: {"title": "title", "actualStartTime": "2020-01-01T00:00:00Z"}},
    )
    assert cli.update(MagicMock(), path, report, NOW)


def test_update_recounts_unconfirmed_within_three_days(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path, report, comments = _update_setup(monkeypatch, tmp_path, _record())
    cli.update(MagicMock(), path, report, NOW)
    comments.assert_called_once()


def test_update_skips_unconfirmed_after_three_days(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path, report, comments = _update_setup(monkeypatch, tmp_path, _record())
    monkeypatch.setattr(
        cli,
        "fetch_live_videos",
        lambda client, ids: {VIDEO: {"title": "title", "actualStartTime": "2020-01-01T00:00:00Z"}},
    )
    assert not cli.update(MagicMock(), path, report, NOW)
    comments.assert_not_called()


def test_update_never_touches_confirmed_records(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    record = {"count": 1, "timestamps": ["0:01:02"], "confirmed": True}
    path, report, comments = _update_setup(monkeypatch, tmp_path, record)
    assert not cli.update(MagicMock(), path, report, NOW)
    comments.assert_not_called()


def test_update_removes_unconfirmed_missing_video(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "videos.json"
    videos = {f"video{index:06}": _record() for index in range(10)}
    write_json(path, {"source": None, "videos": videos})
    live = {
        key: {"title": "title", "actualStartTime": "2020-01-01T00:00:00Z"}
        for key in list(videos)[1:]
    }
    monkeypatch.setattr(cli, "fetch_upload_ids", lambda client: list(live))
    monkeypatch.setattr(cli, "fetch_live_videos", lambda client, ids: live)
    assert cli.update(MagicMock(), path, tmp_path / "report.md", NOW)
    assert "video000000" not in load_json(path)["videos"]


def test_update_keeps_confirmed_missing_video_and_reports_it(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "videos.json"
    videos = {"video000000": _record(True)}
    videos.update({f"video{index:06}": _record() for index in range(1, 10)})
    write_json(path, {"source": None, "videos": videos})
    report = tmp_path / "report.md"
    live = {
        key: {"title": "title", "actualStartTime": "2020-01-01T00:00:00Z"}
        for key in list(videos)[1:]
    }
    monkeypatch.setattr(cli, "fetch_upload_ids", lambda client: list(live))
    monkeypatch.setattr(cli, "fetch_live_videos", lambda client, ids: live)
    assert not cli.update(MagicMock(), path, report)
    assert "非公開または削除" in report.read_text(encoding="utf-8")


def test_update_keeps_previous_count_when_setlist_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    record = {"count": 1, "timestamps": ["0:01:02"], "confirmed": False, "setlist_found": True}
    path, report, _ = _update_setup(monkeypatch, tmp_path, record)
    monkeypatch.setattr(cli, "fetch_comments", lambda client, video_id: None)
    cli.update(MagicMock(), path, report, NOW)
    assert load_json(path)["videos"][VIDEO]["count"] == 1


def test_update_does_not_crash_on_invalid_timestamp_in_comment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path, report, _ = _update_setup(monkeypatch, tmp_path)
    monkeypatch.setattr(cli, "fetch_comments", lambda client, video_id: ["TS\n12:99:99 六甲おろし"])
    assert cli.update(MagicMock(), path, report, NOW)


def test_update_aborts_when_live_videos_are_empty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "videos.json"
    write_json(path, {"source": None, "videos": {VIDEO: _record()}})
    before = path.read_bytes()
    monkeypatch.setattr(cli, "fetch_upload_ids", lambda client: [])
    monkeypatch.setattr(cli, "fetch_live_videos", lambda client, ids: {})
    with pytest.raises(RuntimeError):
        cli.update(MagicMock(), path, tmp_path / "report.md", NOW)
    assert path.read_bytes() == before


def test_update_aborts_when_live_videos_drop_below_threshold(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "videos.json"
    videos = {f"video{index:06}": _record() for index in range(10)}
    write_json(path, {"source": None, "videos": videos})
    live = {
        key: {"title": "x", "actualStartTime": "2020-01-01T00:00:00Z"} for key in list(videos)[:8]
    }
    before = path.read_bytes()
    monkeypatch.setattr(cli, "fetch_upload_ids", lambda client: list(live))
    monkeypatch.setattr(cli, "fetch_live_videos", lambda client, ids: live)
    with pytest.raises(RuntimeError):
        cli.update(MagicMock(), path, tmp_path / "report.md", NOW)
    assert path.read_bytes() == before


def test_update_requires_timezone_aware_now(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path, report, _ = _update_setup(monkeypatch, tmp_path, _record())
    with pytest.raises(ValueError):
        cli.update(MagicMock(), path, report, datetime(2026, 9, 19))


def test_store_rejects_boolean_count(tmp_path: Path) -> None:
    path = tmp_path / "videos.json"
    path.write_text(
        json.dumps(
            {
                "source": None,
                "videos": {VIDEO: {"count": True, "timestamps": [], "confirmed": True}},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        load_json(path)


def test_update_reports_unresolved_setlist_every_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    record = {"count": 0, "timestamps": [], "confirmed": False, "setlist_found": False}
    path, report, _ = _update_setup(monkeypatch, tmp_path, record)
    monkeypatch.setattr(
        cli,
        "fetch_live_videos",
        lambda client, ids: {VIDEO: {"title": "title", "actualStartTime": "2020-01-01T00:00:00Z"}},
    )
    comments = MagicMock()
    monkeypatch.setattr(cli, "fetch_comments", comments)
    assert not cli.update(MagicMock(), path, report, NOW)
    comments.assert_not_called()
    assert "セットリストが見つかっていません" in report.read_text(encoding="utf-8")


def test_update_distinguishes_unavailable_comments_from_missing_setlist(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    second = "ZZZZZZZZZZZ"
    path = tmp_path / "videos.json"
    report = tmp_path / "report.md"
    write_json(path, {"source": None, "videos": {}})
    live = {
        VIDEO: {"title": "A", "actualStartTime": "2026-09-18T00:00:00Z"},
        second: {"title": "B", "actualStartTime": "2026-09-18T00:00:00Z"},
    }
    monkeypatch.setattr(cli, "fetch_upload_ids", lambda client: list(live))
    monkeypatch.setattr(cli, "fetch_live_videos", lambda client, ids: live)
    monkeypatch.setattr(
        cli,
        "fetch_comments",
        lambda client, video_id: None if video_id == VIDEO else ["ただの感想"],
    )
    assert cli.update(MagicMock(), path, report, NOW)
    text = report.read_text(encoding="utf-8")
    assert f"`{VIDEO}`: コメントを取得できませんでした" in text
    assert f"`{second}`: セットリストが見つかりません" in text


@pytest.mark.parametrize(
    "record",
    [
        {"count": 0, "timestamps": []},
        {"count": 0, "timestamps": [], "confirmed": False},
        {"count": 0, "timestamps": [], "confirmed": True, "reason": "x"},
        {"count": 0, "timestamps": [], "confirmed": True, "reason": "x", "decided_on": "bad"},
        {"count": 1, "timestamps": [], "confirmed": True},
        {"count": -1, "timestamps": [], "confirmed": True},
    ],
)
def test_load_json_rejects_invalid_records(tmp_path: Path, record: dict[str, object]) -> None:
    path = tmp_path / "videos.json"
    path.write_text(json.dumps({"source": None, "videos": {VIDEO: record}}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_json(path)


def test_write_json_uses_indent_and_trailing_newline(tmp_path: Path) -> None:
    path = tmp_path / "videos.json"
    write_json(path, {"source": None, "videos": {}})
    assert path.read_text(encoding="utf-8") == '{\n  "source": null,\n  "videos": {}\n}\n'


def test_repository_data_is_valid() -> None:
    load_json(Path("data/videos.json"))


def test_import_confirmed_marks_all_records_confirmed(tmp_path: Path) -> None:
    csv = tmp_path / "in.csv"
    csv.write_text(HEADER + f"https://www.youtube.com/watch?v={VIDEO},0,,,\n", encoding="utf-8")
    assert import_confirmed(csv, {}, "", "2026-09-19", None)["videos"][VIDEO]["confirmed"]


def test_import_confirmed_rejects_count_timestamp_mismatch(tmp_path: Path) -> None:
    csv = tmp_path / "in.csv"
    csv.write_text(HEADER + f"https://www.youtube.com/watch?v={VIDEO},1,,,\n", encoding="utf-8")
    with pytest.raises(ValueError):
        import_confirmed(csv, {}, "", "2026-09-19", None)


def test_import_confirmed_applies_zero_correction_with_reason(tmp_path: Path) -> None:
    csv = tmp_path / "in.csv"
    csv.write_text(HEADER + f"https://www.youtube.com/watch?v={VIDEO},1,,,\n", encoding="utf-8")
    record = import_confirmed(csv, {VIDEO: 0}, "reason", "2026-09-19", None)["videos"][VIDEO]
    assert record["count"] == 0 and record["reason"] == "reason"


def test_import_confirmed_rejects_non_zero_correction(tmp_path: Path) -> None:
    csv = tmp_path / "in.csv"
    csv.write_text(HEADER + f"https://www.youtube.com/watch?v={VIDEO},1,,,\n", encoding="utf-8")
    with pytest.raises(ValueError):
        import_confirmed(csv, {VIDEO: 1}, "", "2026-09-19", None)
