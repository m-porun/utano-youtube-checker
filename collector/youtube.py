"""YouTube Data API の I/O 境界。"""

import json
from typing import Any

from googleapiclient.errors import HttpError

UPLOADS_PLAYLIST_ID = "UUNskpCCH661BeRJkN8n8d-A"


def fetch_upload_ids(client: Any) -> list[str]:
    """アップロード再生リストを全ページ走査して動画 ID を返す。"""
    ids: list[str] = []
    token: str | None = None
    seen_tokens: set[str] = set()
    while True:
        response = (
            client.playlistItems()
            .list(
                playlistId=UPLOADS_PLAYLIST_ID,
                part="snippet",
                maxResults=50,
                pageToken=token,
            )
            .execute()
        )
        ids.extend(item["snippet"]["resourceId"]["videoId"] for item in response.get("items", []))
        token = response.get("nextPageToken")
        if not token:
            return ids
        if token in seen_tokens:
            raise RuntimeError("アップロード再生リストのページトークンが繰り返されました")
        seen_tokens.add(token)


def fetch_live_videos(client: Any, video_ids: list[str]) -> dict[str, dict[str, str]]:
    """開始済みライブのみを ID、title、開始時刻の辞書で返す。"""
    found: dict[str, dict[str, str]] = {}
    for start in range(0, len(video_ids), 50):
        response = (
            client.videos()
            .list(
                id=",".join(video_ids[start : start + 50]),
                part="snippet,liveStreamingDetails",
            )
            .execute()
        )
        for item in response.get("items", []):
            actual = item.get("liveStreamingDetails", {}).get("actualStartTime")
            if actual:
                found[item["id"]] = {
                    "title": item.get("snippet", {}).get("title", ""),
                    "actualStartTime": actual,
                }
    return found


def fetch_video_titles(client: Any, video_ids: list[str]) -> dict[str, str]:
    """動画 ID を50件ずつ問い合わせ、返せたタイトルだけを返す。"""
    titles: dict[str, str] = {}
    for start in range(0, len(video_ids), 50):
        response = (
            client.videos()
            .list(
                id=",".join(video_ids[start : start + 50]),
                part="snippet",
            )
            .execute()
        )
        for item in response.get("items", []):
            titles[item["id"]] = item.get("snippet", {}).get("title", "")
    return titles


def fetch_comments(client: Any, video_id: str) -> list[str] | None:
    """人気順トップレベルコメント20件。403/404 は取得不可として None。"""
    try:
        response = (
            client.commentThreads()
            .list(
                videoId=video_id,
                part="snippet",
                order="relevance",
                maxResults=20,
                textFormat="plainText",
            )
            .execute()
        )
    except HttpError as error:
        if error.resp.status == 404:
            return None
        if error.resp.status == 403 and _comment_error_reason(error) in {
            "commentsDisabled",
            "videoNotFound",
        }:
            return None
        raise
    return [
        item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        for item in response.get("items", [])
    ]


def _comment_error_reason(error: HttpError) -> str | None:
    """YouTube API のエラー本文から reason を安全に取り出す。"""
    try:
        content = json.loads(error.content.decode("utf-8"))
        errors = content.get("error", {}).get("errors", [])
        reason = errors[0].get("reason") if errors else None
        return reason if isinstance(reason, str) else None
    except AttributeError, UnicodeDecodeError, json.JSONDecodeError, IndexError:
        return None
