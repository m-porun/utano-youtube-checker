from unittest.mock import MagicMock

import pytest

from collector.site import build_site_data


def _data(count: int = 1) -> dict[str, object]:
    return {
        "source": None,
        "videos": {
            "abcD_efG-12": {
                "count": count,
                "timestamps": ["0:01:02"] if count else [],
                "confirmed": True,
            }
        },
    }


def test_build_site_uses_videos_json() -> None:
    client = MagicMock()
    client.videos.return_value.list.return_value.execute.return_value = {"items": []}
    assert build_site_data(client, _data())["totalCount"] == 1


def test_build_site_excludes_zero_count() -> None:
    client = MagicMock()
    assert build_site_data(client, _data(0))["videos"] == []


def test_build_site_raises_on_api_error() -> None:
    client = MagicMock()
    client.videos.return_value.list.return_value.execute.side_effect = RuntimeError("API error")
    with pytest.raises(RuntimeError):
        build_site_data(client, _data())


def test_build_site_sets_null_title_for_missing_video() -> None:
    client = MagicMock()
    client.videos.return_value.list.return_value.execute.return_value = {"items": []}
    assert build_site_data(client, _data())["videos"][0]["title"] is None
