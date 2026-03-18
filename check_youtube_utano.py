import os
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# 白珠ウタノの再生リスト「歌枠/KARAOKE」を取得
API_KEY = os.getenv("YOUTUBE_API_KEY")
PLAYLIST_ID = "PLUi5gdZovvGlyVfVOyzmgOwZ8jd0bT2mS"
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v="
SETLIST_KEYWORDS = re.compile(
    r"セトリ|セットリスト|set\s*list|setlist|タイムスタンプ|TS", re.IGNORECASE
)
TIMESTAMP_PATTERN = re.compile(r"\d{1,2}:\d{2}:\d{2}")


def fetch_all_playlist_items(youtube, playlist_id):
    """再生リストの全動画を取得する"""
    videos = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            playlistId=playlist_id,
            part="snippet",
            maxResults=50,
            pageToken=next_page_token,
        )
        response = request.execute()

        for item in response["items"]:
            snippet = item["snippet"]
            video_id = snippet["resourceId"]["videoId"]
            videos.append({
                "title": snippet["title"],
                "video_id": video_id,
                "video_url": f"{YOUTUBE_VIDEO_URL}{video_id}",
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return videos


def fetch_comments(youtube, video_id):
    """動画の人気順上位20件のトップレベルコメントを取得する"""
    request = youtube.commentThreads().list(
        videoId=video_id,
        part="snippet",
        order="relevance",
        maxResults=20,
        textFormat="plainText",
    )
    response = request.execute()

    comments = []
    for item in response["items"]:
        comments.append(item["snippet"]["topLevelComment"]["snippet"]["textDisplay"])
    return comments


def extract_setlist(comments):
    """条件A（キーワード）と条件B（タイムスタンプ）を両方満たすコメントを特定する"""
    candidates = []
    for comment in comments:
        has_keyword = SETLIST_KEYWORDS.search(comment)
        timestamps = TIMESTAMP_PATTERN.findall(comment)
        if has_keyword and timestamps:
            candidates.append((comment, len(timestamps)))

    if not candidates:
        return "セットリストなし"
    if len(candidates) == 1:
        return candidates[0][0]
    # 複数件の場合はタイムスタンプの数が最も多いものを選択
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]


def main():
    if not API_KEY:
        print("エラー: YOUTUBE_API_KEY が設定されていません。")
        return

    youtube = build('youtube', 'v3', developerKey=API_KEY)

    print("--- 調査開始 ---")
    print(f"対象プレイリストID: {PLAYLIST_ID}")

    videos = fetch_all_playlist_items(youtube, PLAYLIST_ID)
    print(f"取得した動画数: {len(videos)}")

    for i, video in enumerate(videos, 1):
        title = video["title"]
        url = video["video_url"]
        print(f"\n  [{i}/{len(videos)}] {title}")
        print(f"    {url}")

        if title == "Private video":
            print(f"    → Private video のためスキップ（URL: {url}）")
            continue

        try:
            comments = fetch_comments(youtube, video["video_id"])
        except HttpError:
            print("    → コメント取得不可のためスキップ")
            continue

        setlist = extract_setlist(comments)

        if setlist == "セットリストなし":
            print("    → セットリストなし")
        else:
            print(f"    → セットリスト発見（{len(TIMESTAMP_PATTERN.findall(setlist))}曲）")


if __name__ == "__main__":
    main()
