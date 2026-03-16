import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
PLAYLIST_ID = "PLUi5gdZovvGlyVfVOyzmgOwZ8jd0bT2mS"
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v="


def fetch_all_playlist_items(youtube, playlist_id):
    """再生リストの全動画を取得する（ページネーション対応）"""
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
        print(f"  {i}. {video['title']}")
        print(f"     {video['video_url']}")


if __name__ == "__main__":
    main()
