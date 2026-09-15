"""レビュー用 PR 本文の生成。コメント本文は常に無害化する。"""

from typing import Any

from .setlist import evidence_lines, uncounted_mentions
from .timestamps import timestamp_seconds

_SPECIAL = "\\`*_[]()<>|#!&"
_LIMIT = 60_000


def sanitize_comment(value: str) -> str:
    """コメントを一行・最大80文字の Markdown 非実行テキストにする。"""
    text = " ".join(value.splitlines())[:80]
    text = text.replace("@", "@\u200b")
    text = text.replace("://", ":\u200b//").replace("www.", "www\u200b.")
    for char in _SPECIAL:
        text = text.replace(char, "\\" + char)
    return text


def _links(video_id: str, timestamps: list[str]) -> str:
    return ", ".join(
        f"[{stamp}](https://www.youtube.com/watch?v={video_id}&t={timestamp_seconds(stamp)})"
        for stamp in timestamps
    )


def _append_items(
    lines: list[str], heading: str | None, items: list[str], limit: int = _LIMIT
) -> None:
    """節を追加し、残りの行は省略注記を含めて本文上限内に収める。"""
    if not items:
        return
    prefix = ["", heading, ""] if heading else []
    marker = f"ほか {len(items)} 件（data/counts.json の差分を確認）"
    if len("\n".join(lines + prefix + [marker])) + 1 > limit:
        return
    lines.extend(prefix)
    added = 0
    for item in items:
        remaining = len(items) - added - 1
        reserve = [f"ほか {remaining} 件（data/counts.json の差分を確認）"] if remaining else []
        if len("\n".join(lines + [item] + reserve)) + 1 > limit:
            break
        lines.append(item)
        added += 1
    if added < len(items):
        lines.append(f"ほか {len(items) - added} 件（data/counts.json の差分を確認）")


def build_report(
    changes: dict[str, tuple[dict[str, Any] | None, dict[str, Any] | None]],
    titles: dict[str, str],
    setlists: dict[str, str | None],
    removed: list[str],
    overrides: set[str] | None = None,
) -> str:
    """変更・要確認事項だけを含む、上限内の PR 本文を返す。"""
    override_ids = overrides or set()
    lines = ["## 日次集計レポート", "", "| 配信 | 回数 | 根拠 |", "| --- | --- | --- |"]
    rows: list[str] = []
    checks: list[str] = []
    for video_id, (before, after) in sorted(changes.items()):
        if after is None:
            continue
        title = sanitize_comment(titles.get(video_id, "タイトルを取得できませんでした"))
        evidence = (
            "<br>".join(sanitize_comment(line) for line in evidence_lines(setlists.get(video_id)))
            or "-"
        )
        note = " override あり（公開値は override）" if video_id in override_ids else ""
        rows.append(
            f"| [{title}](https://www.youtube.com/watch?v={video_id}) | "
            f"{(before or {}).get('count', 0)} → {after['count']}{note} | "
            f"{evidence}<br>{_links(video_id, after['timestamps'])} |"
        )
        if before and before["count"] > 0 and not after["setlist_found"]:
            checks.append(f"- `{video_id}`: セットリストを再取得できませんでした（前回値を維持）")
        elif not after["setlist_found"]:
            checks.append(f"- `{video_id}`: セットリストが見つかりません")
        else:
            checks.extend(
                f"- `{video_id}`: {sanitize_comment(line)}"
                for line in uncounted_mentions(setlists.get(video_id))
            )
    check_reserve = 0
    if checks:
        check_reserve = len("\n## 要確認\n\n") + len(
            f"ほか {len(checks)} 件（data/counts.json の差分を確認）\n"
        )
    _append_items(lines, None, rows, _LIMIT - check_reserve)
    _append_items(lines, "## 要確認", checks)
    removed_items = [f"- `{video_id}` を counts から除外しました" for video_id in sorted(removed)]
    _append_items(lines, "## 削除・非公開", removed_items)
    return "\n".join(lines) + "\n"
