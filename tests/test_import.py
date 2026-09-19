from pathlib import Path

import pytest

from collector.baseline_import import import_confirmed

HEADER = "動画URL,六甲おろしが歌われた数,タイムスタンプ,動画タイトル,セットリスト\n"
URL = "https://www.youtube.com/watch?v=abcD_efG-12"


def _csv(path: Path, text: str, encoding: str = "utf-8") -> Path:
    path.write_text(text, encoding=encoding)
    return path


def test_import_confirmed_rejects_invalid_video_url(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        import_confirmed(
            _csv(tmp_path / "x.csv", HEADER + "https://bad,0,,,\n"), {}, "", "2026-09-19", None
        )


def test_import_confirmed_reads_bom_csv(tmp_path: Path) -> None:
    data = import_confirmed(
        _csv(tmp_path / "x.csv", HEADER + f"{URL},0,,,\n", "utf-8-sig"), {}, "", "2026-09-19", None
    )
    assert data["videos"]["abcD_efG-12"]["confirmed"]


def test_import_confirmed_rejects_inconsistent_count_column(tmp_path: Path) -> None:
    csv = _csv(tmp_path / "x.csv", HEADER + f"{URL},0,,,\n{URL},1,0:01:02,,\n")
    with pytest.raises(ValueError):
        import_confirmed(csv, {}, "", "2026-09-19", None)


def test_import_confirmed_omits_title_and_setlist_columns(tmp_path: Path) -> None:
    data = import_confirmed(
        _csv(tmp_path / "x.csv", HEADER + f"{URL},0,,title,setlist\n"), {}, "", "2026-09-19", None
    )
    assert "title" not in data["videos"]["abcD_efG-12"]


def test_import_confirmed_rejects_missing_columns(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        import_confirmed(_csv(tmp_path / "x.csv", "動画URL\n"), {}, "", "2026-09-19", None)
