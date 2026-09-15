from pathlib import Path
from unittest.mock import MagicMock

import pytest

from collector import __main__ as cli
from collector.baseline_import import import_baseline
from collector.report import build_report, sanitize_comment
from collector.setlist import count_rokko, evidence_lines, extract_setlist, uncounted_mentions
from collector.site import build_site_data
from collector.store import load_json, merged_videos, write_json
from collector.timestamps import normalize_timestamp, timestamp_seconds
from collector.youtube import fetch_live_videos, fetch_upload_ids


@pytest.mark.parametrize(
    ("path", "kind"),
    [
        (Path("data/baseline.json"), "baseline"),
        (Path("data/counts.json"), "counts"),
        (Path("data/overrides.json"), "overrides"),
    ],
)
def test_repository_data_is_valid(path: Path, kind: str) -> None:
    load_json(path, kind)


def test_setlist_rules_and_evidence() -> None:
    text = "セットリスト 六甲おろし見出し\n00:01:02 六甲おろし\n00:02:03 雑談 六甲おろし"
    assert extract_setlist(["TS\n00:01:02 A", text]) == text
    assert count_rokko(text) == [(1, "0:01:02"), (2, "0:02:03")]
    assert evidence_lines(text) == [
        "0:01:02 六甲おろし",
        "0:02:03 雑談 六甲おろし",
    ]
    assert uncounted_mentions(text) == [
        "セットリスト 六甲おろし見出し",
    ]


def test_count_rokko_counts_setlist_after_chat() -> None:
    setlist = "雑談: 六甲おろし耐久\nセットリスト\n0:01:02 六甲おろし"
    assert count_rokko(setlist) == [(1, "0:01:02")]


def test_count_rokko_counts_mentions_after_end_words() -> None:
    setlist = (
        "セットリスト\n0:01:02 雑談: 六甲おろし\n0:02:03 配信内容: 六甲おろし\n"
        "0:03:04 タイムライン: 六甲おろし\n0:04:05 六甲おろし"
    )
    assert count_rokko(setlist) == [
        (1, "0:01:02"),
        (2, "0:02:03"),
        (3, "0:03:04"),
        (4, "0:04:05"),
    ]


def test_count_rokko_counts_each_timestamp_in_endurance_stream() -> None:
    setlist = "セットリスト\n" + "\n".join(f"0:0{index}:00 六甲おろし" for index in range(5))
    assert len(count_rokko(setlist)) == 5


def test_count_rokko_counts_duplicate_mentions_in_one_section_once() -> None:
    setlist = "セットリスト\n0:01:02 六甲おろし 六甲おろし"
    assert count_rokko(setlist) == [(1, "0:01:02")]


def test_uncounted_mentions_returns_only_lines_before_first_timestamp() -> None:
    setlist = "六甲おろし見出し\n0:01:02 六甲おろし\n0:02:03 雑談 六甲おろし"
    assert uncounted_mentions(setlist) == ["六甲おろし見出し"]


def test_evidence_lines_include_sections_after_chat() -> None:
    setlist = "セットリスト\n0:01:02 雑談\n0:02:03 六甲おろし"
    assert evidence_lines(setlist) == ["0:02:03 六甲おろし"]


def test_count_rokko_matches_spec_example() -> None:
    setlist = (
        "セトリ\n00:12:43 阪神タイガースの歌 (六甲おろし)\n"
        "00:16:26 阪神タイガースの歌 (六甲おろし) 六甲おろし耐久ラスト\n"
        "01:05:10 雑談: 土曜は六甲おろし耐久"
    )
    assert count_rokko(setlist) == [(1, "0:12:43"), (2, "0:16:26"), (3, "1:05:10")]


@pytest.mark.parametrize(
    ("raw", "normalized"), [("00:12:43", "0:12:43"), ("0:12:43", "0:12:43"), ("1:02:03", "1:02:03")]
)
def test_timestamps(raw: str, normalized: str) -> None:
    assert normalize_timestamp(raw) == normalized
    assert timestamp_seconds(normalized) == int(normalized.split(":")[0]) * 3600 + int(
        normalized.split(":")[1]
    ) * 60 + int(normalized.split(":")[2])


def test_invalid_timestamp() -> None:
    with pytest.raises(ValueError):
        normalize_timestamp("1:99:00")


def test_invalid_timestamp_in_comment_is_ignored() -> None:
    setlist = "セットリスト\n12:99:99 六甲おろし\n0:01:02 六甲おろし"
    assert count_rokko(setlist) == [(1, "0:01:02")]


def test_youtube_paging_batches_and_reservation_exclusion() -> None:
    client = MagicMock()
    client.playlistItems().list().execute.side_effect = [
        {"items": [{"snippet": {"resourceId": {"videoId": "a"}}}], "nextPageToken": "next"},
        {"items": [{"snippet": {"resourceId": {"videoId": "b"}}}]},
    ]
    assert fetch_upload_ids(client) == ["a", "b"]
    client.videos().list().execute.return_value = {
        "items": [
            {
                "id": "a",
                "snippet": {"title": "live"},
                "liveStreamingDetails": {"actualStartTime": "x"},
            },
            {"id": "b", "liveStreamingDetails": {}},
        ]
    }
    assert fetch_live_videos(client, ["a", "b"]) == {"a": {"title": "live", "actualStartTime": "x"}}


def test_store_priority_and_stable_output(tmp_path: Path) -> None:
    video_id = "abcD_efG-12"
    base = {"source": None, "videos": {video_id: {"count": 1, "timestamps": ["0:00:01"]}}}
    counts = {
        "videos": {
            video_id: {"count": 2, "timestamps": ["0:00:01", "0:00:02"], "setlist_found": True}
        }
    }
    over = {
        "videos": {
            video_id: {"count": 0, "timestamps": [], "reason": "r", "decided_on": "2026-01-01"}
        }
    }
    assert merged_videos(base, counts, over)[video_id]["count"] == 0
    path = tmp_path / "x.json"
    write_json(path, counts)
    first = path.read_bytes()
    write_json(path, counts)
    assert first == path.read_bytes()
    with pytest.raises(ValueError):
        load_json(path, "baseline")


def test_baseline_import_omits_private_columns_and_normalizes(tmp_path: Path) -> None:
    override = tmp_path / "overrides.json"
    write_json(override, {"videos": {}})
    csv = tmp_path / "old.csv"
    csv.write_text(
        "動画URL,六甲おろしが歌われた数,タイムスタンプ,動画タイトル,セットリスト\nhttps://www.youtube.com/watch?v=abcD_efG-12,1,00:01:02,secret,secret\nhttps://www.youtube.com/watch?v=ZZZZZZZZZZZ,0,,,secret,secret\n",
        encoding="utf-8",
    )
    result = import_baseline(csv, override)
    assert result == {
        "source": "old.csv",
        "videos": {
            "ZZZZZZZZZZZ": {"count": 0, "timestamps": []},
            "abcD_efG-12": {"count": 1, "timestamps": ["0:01:02"]},
        },
    }


def test_report_sanitizes_comment_and_timestamp_links() -> None:
    report = build_report(
        {"abcD_efG-12": (None, {"count": 1, "timestamps": ["0:01:02"], "setlist_found": True})},
        {"abcD_efG-12": "title"},
        {"abcD_efG-12": "TS\n0:01:02 [x](http://evil) 六甲おろし @user <script> |"},
        [],
    )
    assert "&t=62" in report and "@\u200buser" in report and "\\<script\\>" in report
    assert "セットリスト" not in report
    assert sanitize_comment("[x](http://evil)").startswith("\\[")


def test_site_excludes_zero_and_totals() -> None:
    client = MagicMock()
    client.videos().list().execute.return_value = {
        "items": [
            {
                "id": "abcD_efG-12",
                "snippet": {"title": "title"},
                "liveStreamingDetails": {"actualStartTime": "x"},
            }
        ]
    }
    data = build_site_data(
        client,
        {"source": None, "videos": {"zero": {"count": 0, "timestamps": []}}},
        {
            "videos": {
                "abcD_efG-12": {
                    "count": 2,
                    "timestamps": ["0:00:01", "0:00:02"],
                    "setlist_found": True,
                }
            }
        },
        {"videos": {}},
        "2026-09-15",
    )
    assert data["totalCount"] == 2 and len(data["videos"]) == 1


def test_update_skips_baseline_and_keeps_file_when_unchanged(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    baseline_path = tmp_path / "baseline.json"
    counts_path = tmp_path / "counts.json"
    overrides_path = tmp_path / "overrides.json"
    write_json(
        baseline_path, {"source": None, "videos": {"abcD_efG-12": {"count": 0, "timestamps": []}}}
    )
    write_json(counts_path, {"videos": {}})
    write_json(overrides_path, {"videos": {}})
    monkeypatch.setattr(cli, "fetch_upload_ids", lambda client: ["abcD_efG-12"])
    monkeypatch.setattr(
        cli,
        "fetch_live_videos",
        lambda client, ids: {"abcD_efG-12": {"title": "old", "actualStartTime": "x"}},
    )
    comments = MagicMock()
    monkeypatch.setattr(cli, "fetch_comments", comments)

    before = counts_path.read_bytes()
    assert not cli.update(
        MagicMock(), baseline_path, counts_path, overrides_path, tmp_path / "report.md"
    )
    assert counts_path.read_bytes() == before
    comments.assert_not_called()


def test_cli_hides_missing_api_key(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    monkeypatch.setattr(cli, "load_dotenv", lambda: None)
    assert cli.main(["build-site", "--out", "unused.json"]) == 2
    assert "YOUTUBE_API_KEY" in capsys.readouterr().err
