"""セットリスト解析の純粋ロジック。"""

import re

from .timestamps import normalize_timestamp

SETLIST_KEYWORDS = re.compile(r"セトリ|セットリスト|set\s*list|setlist|タイムスタンプ|TS", re.I)
TIMESTAMP_PATTERN = re.compile(r"\d{1,2}:\d{2}:\d{2}")


def _valid_timestamps(text: str) -> list[tuple[re.Match[str], str]]:
    """範囲内のタイムスタンプだけを区切り候補として返す。"""
    valid: list[tuple[re.Match[str], str]] = []
    for match in TIMESTAMP_PATTERN.finditer(text):
        try:
            valid.append((match, normalize_timestamp(match.group())))
        except ValueError:
            continue
    return valid


def extract_setlist(comments: list[str]) -> str | None:
    """キーワードと有効なタイムスタンプを持つ最有力コメントを返す。"""
    candidates = [
        (comment, len(_valid_timestamps(comment)))
        for comment in comments
        if SETLIST_KEYWORDS.search(comment) and _valid_timestamps(comment)
    ]
    return max(candidates, key=lambda item: item[1])[0] if candidates else None


def _sections(setlist: str) -> list[tuple[str, str]]:
    timestamps = _valid_timestamps(setlist)
    sections: list[tuple[str, str]] = []
    for index, (match, stamp) in enumerate(timestamps):
        end = timestamps[index + 1][0].start() if index + 1 < len(timestamps) else len(setlist)
        sections.append((stamp, setlist[match.end() : end]))
    return sections


def count_rokko(setlist: str | None) -> list[tuple[int, str]]:
    """「六甲おろし」を含む区間を1回ずつ数える。

    例: ``0:01:02 六甲おろし 六甲おろし`` は同じ区間なので1回とする。
    """
    results: list[tuple[int, str]] = []
    for stamp, text in _sections(setlist or ""):
        if "六甲おろし" in text:
            results.append((len(results) + 1, stamp))
    return results


def evidence_lines(setlist: str | None) -> list[str]:
    """実際に数えた曲区間の六甲おろしを含む行を返す。"""
    lines: list[str] = []
    for stamp, text in _sections(setlist or ""):
        if "六甲おろし" in text:
            section_lines = f"{stamp}{text}".splitlines()
            lines.extend(line for line in section_lines if "六甲おろし" in line)
    return lines


def uncounted_mentions(setlist: str | None) -> list[str]:
    """最初のタイムスタンプより前にある未集計の言及だけを返す。"""
    source = setlist or ""
    timestamps = _valid_timestamps(source)
    first_start = timestamps[0][0].start() if timestamps else len(source)
    lines = [line for line in source[:first_start].splitlines() if "六甲おろし" in line]
    return lines
