from collector.report import build_report, sanitize_comment


def _record(count: int, timestamp: str) -> dict[str, object]:
    return {"count": count, "timestamps": [timestamp], "setlist_found": True}


def test_report_excludes_non_matching_setlist_lines() -> None:
    report = build_report(
        {"abcD_efG-12": (None, _record(1, "0:01:02"))},
        {"abcD_efG-12": "title"},
        {"abcD_efG-12": "TS\n0:01:02 六甲おろし\n0:02:03 他の曲"},
        [],
    )
    assert "他の曲" not in report


def test_report_truncates_before_escaping() -> None:
    assert not sanitize_comment("a" * 79 + "[x]").endswith("\\")


def test_report_disables_autolinks() -> None:
    text = sanitize_comment("https://evil.example www.evil.example")
    assert "https://evil.example" not in text
    assert "www.evil.example" not in text


def test_report_marks_override() -> None:
    report = build_report(
        {"abcD_efG-12": (None, _record(1, "0:01:02"))},
        {},
        {"abcD_efG-12": "TS\n0:01:02 六甲おろし"},
        [],
        {"abcD_efG-12"},
    )
    assert "override あり" in report


def test_report_uses_each_videos_own_before_value() -> None:
    report = build_report(
        {
            "abcD_efG-12": (_record(1, "0:01:02"), _record(2, "0:01:02")),
            "ZZZZZZZZZZZ": (_record(3, "0:02:03"), _record(4, "0:02:03")),
        },
        {},
        {},
        [],
    )
    assert "1 → 2" in report
    assert "3 → 4" in report


def test_report_limits_body_length() -> None:
    changes = {f"video{index:06}": (None, _record(1, "0:01:02")) for index in range(1_000)}
    report = build_report(changes, {}, {}, [])
    assert len(report) <= 60_000
    assert "ほか" in report


def test_report_limits_body_length_with_many_checks() -> None:
    changes = {
        f"video{index:06}": (None, {"count": 0, "timestamps": [], "setlist_found": False})
        for index in range(1_000)
    }
    report = build_report(changes, {}, {}, [])
    assert len(report) <= 60_000
    assert "## 要確認" in report
    assert "ほか" in report
