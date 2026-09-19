from unittest.mock import MagicMock

import pytest
from googleapiclient.errors import HttpError

from collector import __main__ as cli


def test_cli_does_not_print_api_key_when_set(monkeypatch, capsys) -> None:
    secret = "secret-value"
    monkeypatch.setenv("YOUTUBE_API_KEY", secret)
    monkeypatch.setattr(cli, "load_dotenv", lambda: None)
    monkeypatch.setattr(cli, "build", lambda *args, **kwargs: MagicMock())
    monkeypatch.setattr(cli, "build_site_data", lambda *args: {"videos": []})
    monkeypatch.setattr(cli, "write_site", lambda *args: None)
    assert cli.main(["build-site", "--out", "unused.json"]) == 0
    captured = capsys.readouterr()
    assert secret not in captured.out + captured.err


def test_cli_reports_http_error_without_uri(monkeypatch, capsys) -> None:
    secret = "secret-value"
    response = MagicMock(status=500, uri=f"https://example.invalid/?key={secret}")
    error = HttpError(response, b"error")
    monkeypatch.setenv("YOUTUBE_API_KEY", secret)
    monkeypatch.setattr(cli, "load_dotenv", lambda: None)
    monkeypatch.setattr(cli, "build", lambda *args, **kwargs: MagicMock())
    monkeypatch.setattr(cli, "build_site_data", lambda *args: (_ for _ in ()).throw(error))
    assert cli.main(["build-site", "--out", "unused.json"]) == 1
    stderr = capsys.readouterr().err
    assert "key=" not in stderr and response.uri not in stderr


@pytest.mark.parametrize("correction", ["invalid", "abcD_efG-12=x", "bad=0"])
def test_cli_rejects_malformed_correction(monkeypatch, tmp_path, capsys, correction) -> None:
    csv = tmp_path / "in.csv"
    csv.write_text("動画URL,六甲おろしが歌われた数,タイムスタンプ\n", encoding="utf-8")
    assert (
        cli.main(
            [
                "import-confirmed",
                "--csv",
                str(csv),
                "--out",
                str(tmp_path / "out.json"),
                "--reason",
                "x",
                "--decided-on",
                "2026-09-19",
                "--correction",
                correction,
            ]
        )
        == 2
    )
    assert capsys.readouterr().err.startswith("エラー:")


def test_cli_returns_two_for_invalid_json(monkeypatch, tmp_path, capsys) -> None:
    path = tmp_path / "videos.json"
    path.write_text("{", encoding="utf-8")
    monkeypatch.setattr(cli, "VIDEOS_PATH", path)
    monkeypatch.setenv("YOUTUBE_API_KEY", "test")
    monkeypatch.setattr(cli, "load_dotenv", lambda: None)
    monkeypatch.setattr(cli, "build", lambda *args, **kwargs: MagicMock())
    assert cli.main(["build-site", "--out", str(tmp_path / "out.json")]) == 2
    assert "Traceback" not in capsys.readouterr().err
