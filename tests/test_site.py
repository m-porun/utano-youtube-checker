from unittest.mock import MagicMock

import pytest

from collector.site import build_site_data


def _inputs() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    baseline = {"source": None, "videos": {}}
    counts = {
        "videos": {
            "abcD_efG-12": {
                "count": 1,
                "timestamps": ["0:01:02"],
                "setlist_found": True,
            }
        }
    }
    return baseline, counts, {"videos": {}}


def test_build_site_raises_on_api_error() -> None:
    client = MagicMock()
    client.videos.return_value.list.return_value.execute.side_effect = RuntimeError("api")
    with pytest.raises(RuntimeError):
        build_site_data(client, *_inputs())


def test_build_site_sets_null_title_for_missing_video() -> None:
    client = MagicMock()
    client.videos.return_value.list.return_value.execute.return_value = {"items": []}
    data = build_site_data(client, *_inputs())
    assert data["videos"][0]["title"] is None
