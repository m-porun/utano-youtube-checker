import csv
import io
from unittest.mock import MagicMock, call, patch

import check_youtube_utano as checker


def test_extract_setlist_returns_single_matching_comment() -> None:
    comment = "セットリスト\n00:01:02 曲A"

    assert checker.extract_setlist([comment, "セトリだけ", "00:02:03 だけ"]) == comment


def test_extract_setlist_selects_comment_with_most_timestamps() -> None:
    short_comment = "セトリ\n00:01:00 曲A"
    long_comment = "タイムスタンプ\n00:01:00 曲A\n00:02:00 曲B"

    assert checker.extract_setlist([short_comment, long_comment]) == long_comment


def test_extract_setlist_rejects_keyword_without_timestamp() -> None:
    comments = ["セットリストです", "TS はありません"]

    assert checker.extract_setlist(comments) == "セットリストなし"


def test_extract_setlist_returns_no_setlist_for_no_comments() -> None:
    assert checker.extract_setlist([]) == "セットリストなし"


def test_count_rokko_counts_one_song() -> None:
    setlist = "セトリ\n00:01:02 六甲おろし"

    assert checker.count_rokko(setlist) == [(1, "00:01:02")]


def test_count_rokko_numbers_multiple_songs_and_uses_timestamps() -> None:
    setlist = "00:01:02 曲A\n00:03:04 六甲おろし\n00:05:06 六甲おろし"

    assert checker.count_rokko(setlist) == [(1, "00:03:04"), (2, "00:05:06")]


def test_count_rokko_stops_at_setlist_end_keywords() -> None:
    setlist = "00:01:02 六甲おろし\n00:03:04 配信内容: 六甲おろし\n00:05:06 六甲おろし"

    assert checker.count_rokko(setlist) == [(1, "00:01:02")]


def test_count_rokko_ignores_mentions_before_first_timestamp() -> None:
    setlist = "六甲おろしを歌った回\n00:01:02 曲A"

    assert checker.count_rokko(setlist) == []


def test_count_rokko_counts_duplicate_mentions_in_one_song_once() -> None:
    setlist = "00:01:02 六甲おろし、六甲おろし\n00:03:04 曲A"

    assert checker.count_rokko(setlist) == [(1, "00:01:02")]


def test_count_rokko_returns_empty_list_when_not_found() -> None:
    assert checker.count_rokko("00:01:02 曲A\n00:03:04 曲B") == []


def test_write_csv_rows_writes_one_row_for_zero_rokko_count() -> None:
    output = io.StringIO()
    writer = csv.writer(output)

    checker.write_csv_rows(writer, 1, "title", "url", "setlist", 0, [])

    assert list(csv.reader(io.StringIO(output.getvalue()))) == [
        ["1", "title", "url", "setlist", "0", "", ""]
    ]


def test_write_csv_rows_writes_one_row_per_rokko_count() -> None:
    output = io.StringIO()
    writer = csv.writer(output)

    checker.write_csv_rows(
        writer,
        1,
        "title",
        "url",
        "setlist",
        2,
        [(1, "00:01:02"), (2, "00:03:04")],
    )

    assert list(csv.reader(io.StringIO(output.getvalue()))) == [
        ["1", "title", "url", "setlist", "2", "1", "00:01:02"],
        ["1", "title", "url", "setlist", "2", "2", "00:03:04"],
    ]


def test_fetch_all_uploads_follows_next_page_tokens() -> None:
    first_request = MagicMock()
    first_request.execute.return_value = {
        "items": [{"snippet": {"title": "first", "resourceId": {"videoId": "video-id-01"}}}],
        "nextPageToken": "next-page",
    }
    second_request = MagicMock()
    second_request.execute.return_value = {
        "items": [{"snippet": {"title": "second", "resourceId": {"videoId": "video-id-02"}}}]
    }
    youtube = MagicMock()
    youtube.playlistItems().list.side_effect = [first_request, second_request]

    assert checker.fetch_all_uploads(youtube) == [
        {
            "title": "first",
            "video_id": "video-id-01",
            "video_url": "https://www.youtube.com/watch?v=video-id-01",
        },
        {
            "title": "second",
            "video_id": "video-id-02",
            "video_url": "https://www.youtube.com/watch?v=video-id-02",
        },
    ]
    assert youtube.playlistItems().list.call_args_list == [
        call(
            playlistId=checker.UPLOADS_PLAYLIST_ID,
            part="snippet",
            maxResults=50,
            pageToken=None,
        ),
        call(
            playlistId=checker.UPLOADS_PLAYLIST_ID,
            part="snippet",
            maxResults=50,
            pageToken="next-page",
        ),
    ]


def test_filter_live_videos_returns_only_videos_with_live_streaming_details() -> None:
    request = MagicMock()
    request.execute.return_value = {
        "items": [
            {"id": "live-video", "liveStreamingDetails": {}},
            {"id": "regular-video"},
        ]
    }
    youtube = MagicMock()
    youtube.videos().list.return_value = request
    videos = [
        {"video_id": "live-video", "title": "live", "video_url": "live-url"},
        {"video_id": "regular-video", "title": "regular", "video_url": "regular-url"},
    ]

    assert checker.filter_live_videos(youtube, videos) == [videos[0]]


def test_main_exits_without_api_key_or_creating_a_client(monkeypatch, capsys) -> None:
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    monkeypatch.setattr(checker, "load_dotenv", lambda: None)

    with patch.object(checker, "build") as build_mock:
        checker.main()

    output = capsys.readouterr().out
    assert "YOUTUBE_API_KEY が設定されていません" in output
    build_mock.assert_not_called()


def test_main_does_not_print_configured_api_key(monkeypatch, capsys, tmp_path) -> None:
    api_key = "example-secret-value"
    monkeypatch.setenv("YOUTUBE_API_KEY", api_key)
    monkeypatch.setattr(checker, "load_dotenv", lambda: None)
    monkeypatch.setattr(checker, "OUTPUT_CSV_PATH", str(tmp_path / "rokko_count.csv"))

    with (
        patch.object(checker, "build") as build_mock,
        patch.object(checker, "fetch_all_uploads", return_value=[]),
        patch.object(checker, "filter_live_videos", return_value=[]),
    ):
        checker.main()

    build_mock.assert_called_once_with("youtube", "v3", developerKey=api_key)
    assert api_key not in capsys.readouterr().out
