import pytest

from collector.setlist import (
    count_rokko,
    evidence_lines,
    extract_setlist,
    uncounted_mentions,
)
from collector.timestamps import normalize_timestamp, timestamp_seconds


def test_extract_setlist_picks_comment_with_most_timestamps() -> None:
    short = "TS\n0:01:02 曲A"
    long = "セットリスト\n0:01:02 曲A\n0:02:03 曲B"
    assert extract_setlist([short, long]) == long


def test_extract_setlist_returns_none_without_keyword_or_timestamp() -> None:
    assert extract_setlist(["0:01:02 曲A", "セットリストです"]) is None


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


def test_normalize_timestamp_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        normalize_timestamp("0:99:00")


def test_timestamp_seconds_converts_hours_minutes_seconds() -> None:
    assert timestamp_seconds("1:02:03") == 3723


def test_invalid_timestamp_in_comment_is_ignored() -> None:
    assert count_rokko("TS\n12:99:99 六甲おろし\n0:01:02 六甲おろし") == [(1, "0:01:02")]
