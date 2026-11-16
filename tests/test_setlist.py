import pytest

from collector.setlist import (
    count_rokko,
    evidence_lines,
    extract_setlist,
    uncounted_mentions,
)
from collector.timestamps import normalize_timestamp, timestamp_seconds


def test_extract_setlist_picks_comment_with_most_timestamps() -> None:
    short = "\n".join(f"{minute}:00 曲{minute}" for minute in range(5))
    long = "\n".join(f"{minute}:00 曲{minute}" for minute in range(6))
    assert extract_setlist([short, long]) == long


def test_extract_setlist_returns_none_with_fewer_than_five_timestamps() -> None:
    comment = "セットリスト\n" + "\n".join(f"{minute}:00 曲{minute}" for minute in range(4))
    assert extract_setlist([comment, "セットリストです"]) is None


def test_extract_setlist_does_not_require_setlist_keyword() -> None:
    comment = "\n".join(f"{minute}:00 曲{minute}" for minute in range(5))
    assert extract_setlist([comment]) == comment


def test_count_rokko_counts_setlist_after_chat() -> None:
    assert count_rokko("雑談: 六甲おろし\nTS\n0:01:02 六甲おろし") == [(1, "0:01:02")]


def test_count_rokko_counts_mentions_after_end_words() -> None:
    text = "TS\n0:01:02 雑談 六甲おろし\n0:02:03 配信内容 六甲おろし\n0:03:04 六甲おろし"
    assert len(count_rokko(text)) == 3


def test_count_rokko_counts_each_timestamp_in_endurance_stream() -> None:
    text = "TS\n" + "\n".join(f"0:0{number}:00 六甲おろし" for number in range(5))
    assert len(count_rokko(text)) == 5


def test_count_rokko_counts_duplicate_mentions_in_one_section_once() -> None:
    assert count_rokko("TS\n0:01:02 六甲おろし 六甲おろし") == [(1, "0:01:02")]


def test_count_rokko_matches_spec_example() -> None:
    text = (
        "セトリ\n00:12:43 阪神タイガースの歌 (六甲おろし)\n"
        "00:16:26 阪神タイガースの歌 (六甲おろし) 六甲おろし耐久ラスト\n"
        "01:05:10 雑談: 土曜は六甲おろし耐久"
    )
    assert len(count_rokko(text)) == 3


def test_uncounted_mentions_returns_only_lines_before_first_timestamp() -> None:
    text = "六甲おろし見出し\n0:01:02 六甲おろし\n0:02:03 雑談 六甲おろし"
    assert uncounted_mentions(text) == ["六甲おろし見出し"]


def test_evidence_lines_include_sections_after_chat() -> None:
    assert evidence_lines("TS\n0:01:02 雑談\n0:02:03 六甲おろし") == ["0:02:03 六甲おろし"]


def test_normalize_timestamp_accepts_zero_padded_and_plain() -> None:
    assert normalize_timestamp("00:12:43") == "0:12:43"
    assert normalize_timestamp("0:12:43") == "0:12:43"


def test_normalize_timestamp_accepts_minute_second() -> None:
    assert normalize_timestamp("12:43") == "0:12:43"


def test_count_rokko_counts_minute_second_sections() -> None:
    assert count_rokko("TS\n12:43 六甲おろし\n13:00 六甲おろし") == [(1, "0:12:43"), (2, "0:13:00")]


def test_extract_setlist_ignores_ts_inside_words() -> None:
    assert extract_setlist(["it's starts\n0:01:02 曲"]) is None


def test_extract_setlist_is_deterministic_for_tied_candidates() -> None:
    first = "\n".join(f"{minute}:00 A" for minute in range(5))
    second = "\n".join(f"{minute}:00 B" for minute in range(5))
    assert extract_setlist([first, second]) == extract_setlist([second, first])


def test_normalize_timestamp_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        normalize_timestamp("0:99:00")


def test_timestamp_seconds_converts_hours_minutes_seconds() -> None:
    assert timestamp_seconds("1:02:03") == 3723


def test_invalid_timestamp_in_comment_is_ignored() -> None:
    assert count_rokko("TS\n12:99:99 六甲おろし\n0:01:02 六甲おろし") == [(1, "0:01:02")]
