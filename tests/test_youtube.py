from unittest.mock import MagicMock

import pytest
from googleapiclient.errors import HttpError

from collector.youtube import fetch_comments, fetch_live_videos, fetch_video_titles


def _http_error(status: int) -> HttpError:
    response = MagicMock()
    response.status = status
    return HttpError(response, b"error")


def test_fetch_comments_returns_none_for_403_and_404() -> None:
    for status in (403, 404):
        client = MagicMock()
        client.commentThreads().list().execute.side_effect = _http_error(status)
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
