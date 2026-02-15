import os
import json
from googleapiclient.discovery import build
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
PLAYLIST_ID = "PLUi5gdZovvGlyVfVOyzmgOwZ8jd0bT2mS"

def main():
    if not API_KEY:
        print("エラー: YOUTUBE_API_KEY が設定されていません。")
        return

    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    print("--- 調査開始 ---")
    # ここに動画リスト取得とコメント解析のロジックを書く（次ステップで詳細化）
    print("APIキーの接続確認に成功しました。")
    print(f"対象プレイリストID: {PLAYLIST_ID}")

if __name__ == "__main__":
    main()
