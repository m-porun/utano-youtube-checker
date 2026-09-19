from unittest.mock import MagicMock

import pytest
from googleapiclient.errors import HttpError

from collector.youtube import (
    fetch_comments,
    fetch_live_videos,
    fetch_upload_ids,
    fetch_video_titles,
)


def _http_error(status: int) -> HttpError:
    response = MagicMock()
    response.status = status
    return HttpError(response, b"error")


def _reason_error(reason: str | None) -> HttpError:
    error = _http_error(403)
    error.content = (
        b'{"error":{"errors":[{"reason":"' + reason.encode() + b'"}]}}' if reason else b"not-json"
    )
    return error


def test_fetch_comments_returns_none_for_comments_disabled() -> None:
    client = MagicMock()
    client.commentThreads().list().execute.side_effect = _reason_error("commentsDisabled")
    assert fetch_comments(client, "abcD_efG-12") is None


def test_fetch_comments_raises_for_quota_exceeded() -> None:
    client = MagicMock()
    client.commentThreads().list().execute.side_effect = _reason_error("quotaExceeded")
    with pytest.raises(HttpError):
        fetch_comments(client, "abcD_efG-12")


def test_fetch_comments_raises_for_403_without_reason() -> None:
    client = MagicMock()
    client.commentThreads().list().execute.side_effect = _reason_error(None)
    with pytest.raises(HttpError):
        fetch_comments(client, "abcD_efG-12")


def test_fetch_comments_returns_none_for_video_not_found() -> None:
    client = MagicMock()
    client.commentThreads().list().execute.side_effect = _http_error(404)
    assert fetch_comments(client, "abcD_efG-12") is None


def test_fetch_comments_raises_for_500() -> None:
    client = MagicMock()
    client.commentThreads().list().execute.side_effect = _http_error(500)
    with pytest.raises(HttpError):
        fetch_comments(client, "abcD_efG-12")


def test_fetch_live_videos_splits_ids_into_batches_of_50() -> None:
    client = MagicMock()
    client.videos.return_value.list.return_value.execute.return_value = {"items": []}
    ids = [f"id{index}" for index in range(51)]
    fetch_live_videos(client, ids)
    calls = client.videos().list.call_args_list
    assert len(calls) == 2
    assert len(calls[0].kwargs["id"].split(",")) == 50


def test_fetch_video_titles_returns_only_returned_items() -> None:
    client = MagicMock()
    client.videos().list().execute.return_value = {
        "items": [{"id": "abcD_efG-12", "snippet": {"title": "title"}}]
    }
    assert fetch_video_titles(client, ["abcD_efG-12", "ZZZZZZZZZZZ"]) == {"abcD_efG-12": "title"}


def test_fetch_upload_ids_raises_on_repeated_page_token() -> None:
    client = MagicMock()
    client.playlistItems().list().execute.return_value = {"items": [], "nextPageToken": "same"}
    with pytest.raises(RuntimeError):
        fetch_upload_ids(client)
