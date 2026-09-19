import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = "動画URL,六甲おろしが歌われた数,タイムスタンプ\n"
ROW = "https://www.youtube.com/watch?v=abcD_efG-12,0,\n"


def test_module_entrypoint_writes_output(tmp_path: Path) -> None:
    csv_path = tmp_path / "confirmed.csv"
    output_path = tmp_path / "videos.json"
    csv_path.write_text(HEADER + ROW, encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "collector",
            "import-confirmed",
            "--csv",
            str(csv_path),
            "--out",
            str(output_path),
            "--reason",
            "テスト",
            "--decided-on",
            "2026-09-15",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert output_path.is_file()


def test_module_entrypoint_reports_missing_api_key(tmp_path: Path) -> None:
    environment = dict(os.environ)
    environment["YOUTUBE_API_KEY"] = ""
    environment["PYTHONPATH"] = str(ROOT)
    result = subprocess.run(
        [sys.executable, "-m", "collector", "build-site", "--out", str(tmp_path / "site.json")],
        cwd=tmp_path,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "YOUTUBE_API_KEY が設定されていません" in result.stderr
