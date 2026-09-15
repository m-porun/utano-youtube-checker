from pathlib import Path

import pytest

from collector.baseline_import import import_baseline
from collector.store import write_json

HEADER = "動画URL,六甲おろしが歌われた数,タイムスタンプ\n"
URL = "https://www.youtube.com/watch?v=abcD_efG-12"


def _overrides(path: Path, videos: dict[str, object] | None = None) -> Path:
    write_json(path, {"videos": videos or {}})
    return path


def test_baseline_import_rejects_count_timestamp_mismatch(tmp_path: Path) -> None:
    csv = tmp_path / "input.csv"
    csv.write_text(HEADER + f"{URL},2,0:01:02\n", encoding="utf-8")
    with pytest.raises(ValueError):
        import_baseline(csv, _overrides(tmp_path / "overrides.json"))


def test_baseline_import_uses_override_for_mismatch(tmp_path: Path) -> None:
    csv = tmp_path / "input.csv"
    csv.write_text(HEADER + f"{URL},2,0:01:02\n", encoding="utf-8")
    override = {
        "abcD_efG-12": {
            "count": 0,
            "timestamps": [],
            "reason": "x",
            "decided_on": "2026-01-01",
        }
    }
    result = import_baseline(csv, _overrides(tmp_path / "overrides.json", override))
    assert result["videos"]["abcD_efG-12"]["count"] == 0


def test_baseline_import_rejects_invalid_video_url(tmp_path: Path) -> None:
    csv = tmp_path / "input.csv"
    csv.write_text(HEADER + "https://example.invalid,0,\n", encoding="utf-8")
    with pytest.raises(ValueError):
        import_baseline(csv, _overrides(tmp_path / "overrides.json"))


def test_baseline_import_reads_bom_csv(tmp_path: Path) -> None:
    csv = tmp_path / "input.csv"
    csv.write_text(HEADER + f"{URL},1,00:01:02\n", encoding="utf-8-sig")
    result = import_baseline(csv, _overrides(tmp_path / "overrides.json"))
    assert result["videos"]["abcD_efG-12"]["timestamps"] == ["0:01:02"]


def test_baseline_import_rejects_inconsistent_count_column(tmp_path: Path) -> None:
    csv = tmp_path / "input.csv"
    csv.write_text(HEADER + f"{URL},2,0:01:02\n{URL},1,0:02:03\n", encoding="utf-8")
    with pytest.raises(ValueError):
        import_baseline(csv, _overrides(tmp_path / "overrides.json"))
