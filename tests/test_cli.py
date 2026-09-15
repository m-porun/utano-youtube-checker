from unittest.mock import MagicMock

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
