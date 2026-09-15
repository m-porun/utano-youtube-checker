import json
from pathlib import Path

import pytest

from collector.store import load_json, write_json


@pytest.mark.parametrize(
    ("kind", "data"),
    [
        ("baseline", {"source": None, "videos": {"abcD_efG-12": {"count": -1, "timestamps": []}}}),
        (
            "baseline",
            {"source": None, "videos": {"abcD_efG-12": {"count": 1, "timestamps": [1]}}},
        ),
        ("baseline", {"source": None, "videos": {"abcD_efG-12": {"count": 1, "timestamps": []}}}),
        ("baseline", {"source": None, "videos": {"invalid": {"count": 0, "timestamps": []}}}),
        ("counts", {"videos": {"abcD_efG-12": {"count": 0, "timestamps": []}}}),
        (
            "overrides",
            {
                "videos": {
                    "abcD_efG-12": {
                        "count": 0,
                        "timestamps": [],
                        "reason": "x",
                        "decided_on": "bad",
                    }
                }
            },
        ),
    ],
)
def test_load_json_rejects_invalid_schema(
    tmp_path: Path, kind: str, data: dict[str, object]
) -> None:
    path = tmp_path / "data.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        load_json(path, kind)


def test_write_json_uses_indent_and_trailing_newline(tmp_path: Path) -> None:
    path = tmp_path / "data.json"
    write_json(path, {"videos": {}})
    assert path.read_text(encoding="utf-8") == '{\n  "videos": {}\n}\n'
