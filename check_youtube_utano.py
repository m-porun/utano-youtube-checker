import csv
import os
import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# 白珠ウタノのチャンネルからライブ配信を取得
API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = "UCNskpCCH661BeRJkN8n8d-A"
UPLOADS_PLAYLIST_ID = "UUNskpCCH661BeRJkN8n8d-A"  # UCをUUに置き換え
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v="
SETLIST_KEYWORDS = re.compile(
    r"セトリ|セットリスト|set\s*list|setlist|タイムスタンプ|TS", re.IGNORECASE
)
TIMESTAMP_PATTERN = re.compile(r"\d{1,2}:\d{2}:\d{2}")
OUTPUT_CSV_PATH = "output/rokko_count.csv"


def fetch_all_uploads(youtube):
    """アップロード再生リスト（UU...）から全動画を取得する"""
    videos = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            playlistId=UPLOADS_PLAYLIST_ID,
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


def filter_live_videos(youtube, videos):
    """videos.list で liveStreamingDetails の有無を確認し、ライブ配信のみ返す（50件ずつバッチ処理）"""
    live_videos = []

    for i in range(0, len(videos), 50):
        batch = videos[i:i + 50]
        video_ids = [v["video_id"] for v in batch]

        request = youtube.videos().list(
            id=",".join(video_ids),
            part="liveStreamingDetails",
        )
        response = request.execute()

        live_ids = set()
        for item in response["items"]:
            if "liveStreamingDetails" in item:
                live_ids.add(item["id"])

        for v in batch:
            if v["video_id"] in live_ids:
                live_videos.append(v)

    return live_videos


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


SETLIST_END_KEYWORDS = re.compile(r"配信内容|タイムライン|雑談")


def count_rokko(setlist):
    """セットリストをタイムスタンプで曲単位に分割し、六甲おろしをカウントする。
    「配信内容」「タイムライン」「雑談」が出現したらセトリ終了とみなす。
    戻り値: [(rokko_no, timestamp), ...] のリスト。見つからなければ空リスト。
    """
    parts = re.split(r"(\d{1,2}:\d{2}:\d{2})", setlist)

    results = []
    rokko_count = 0
    # partsは [前テキスト, timestamp1, テキスト1, timestamp2, テキスト2, ...] の形式
    for j in range(1, len(parts) - 1, 2):
        timestamp = parts[j]
        song_text = parts[j + 1] if j + 1 < len(parts) else ""
        if SETLIST_END_KEYWORDS.search(song_text):
            break
        if "六甲おろし" in song_text:
            rokko_count += 1
            results.append((rokko_count, timestamp))

    return results


def write_csv_rows(writer, search_count, title, url, setlist, rokko_count, rokko_results):
    """CSV にレコードを書き込む。RokkoCount が 1 以上なら件数分、0 なら 1 レコード出力。"""
    if rokko_count == 0:
        writer.writerow([search_count, title, url, setlist, 0, None, None])
    else:
        for rokko_no, timestamp in rokko_results:
            writer.writerow([search_count, title, url, setlist, rokko_count, rokko_no, timestamp])


def main():
    if not API_KEY:
        print("エラー: YOUTUBE_API_KEY が設定されていません。")
        return

    youtube = build('youtube', 'v3', developerKey=API_KEY)

    print("--- 調査開始 ---")
    print(f"対象チャンネルID: {CHANNEL_ID}")

    all_videos = fetch_all_uploads(youtube)
    print(f"アップロード動画数: {len(all_videos)}")

    videos = filter_live_videos(youtube, all_videos)
    print(f"ライブ配信動画数: {len(videos)}")

    os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)
    csvfile = open(OUTPUT_CSV_PATH, "w", newline="", encoding="utf-8")
    writer = csv.writer(csvfile)
    writer.writerow(["検索件数", "動画タイトル", "動画URL", "セットリスト",
                      "六甲おろしが歌われた数", "六甲おろし番号", "タイムスタンプ"])

    total_rokko_count = 0
    search_count = 0

    for i, video in enumerate(videos, 1):
        title = video["title"]
        url = video["video_url"]
        search_count += 1
        print(f"\n  [{i}/{len(videos)}] {title}")
        print(f"    {url}")

        if title == "Private video":
            print(f"    → Private video のためスキップ（URL: {url}）")
            write_csv_rows(writer, search_count, None, url, None, 0, [])
            continue

        try:
            comments = fetch_comments(youtube, video["video_id"])
        except HttpError:
            print("    → コメント取得不可のためスキップ")
            write_csv_rows(writer, search_count, None, url, None, 0, [])
            continue

        setlist = extract_setlist(comments)

        if setlist == "セットリストなし":
            print("    → セットリストなし")
            write_csv_rows(writer, search_count, title, url, setlist, 0, [])
            continue

        print(f"    → セットリスト発見（{len(TIMESTAMP_PATTERN.findall(setlist))}曲）")

        rokko_results = count_rokko(setlist)
        rokko_count = len(rokko_results)
        if rokko_results:
            total_rokko_count += rokko_count
            for rokko_no, timestamp in rokko_results:
                print(f"    ★ 六甲おろし #{rokko_no} @ {timestamp}")

        write_csv_rows(writer, search_count, title, url, setlist, rokko_count, rokko_results)

    csvfile.close()

    print(f"\n六甲おろしカウンティングが終了しました。")
    print(f"CSVファイル: {os.path.abspath(OUTPUT_CSV_PATH)}")
    print(f"六甲おろし歌唱総数: {total_rokko_count}")


if __name__ == "__main__":
    main()
