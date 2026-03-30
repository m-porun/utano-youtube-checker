# CLAUDE.md

## ペルソナ（最優先）
このプロジェクトでの応答はすべて ~/.claude/agents/sunsun.md のペルソナ・口調ルールに従うこと。

このファイルは、本リポジトリ内のコードを扱う際に、Claude Code（claude.ai/code）が従うべき指針を示しています。

## Project Overview

白珠ウタノ(Shiratama Utano)のYouTubeチャンネル[UTANO ch. 白玖ウタノ](https://www.youtube.com/@UTANOch)で、再生リストの中に[歌枠/KARAOKE](https://www.youtube.com/playlist?list=PLUi5gdZovvGlyVfVOyzmgOwZ8jd0bT2mS)があります。
各動画にコメントされている「Set List」から、「六甲おろし」がある回数を数えWebページに表示することを目的としています。
つまり、これまで白珠ウタノが「六甲おろし」を歌った数をコメントの中から判断して表示したいということです。

## Tech Stack

- **Python 3.14** with **uv** as the package manager
- **google-api-python-client** for YouTube Data API v3
- **python-dotenv** for environment variable management
- **Docker** + **docker-compose** for containerized execution
- **Vite + React + TailwindCSS v4** for the web frontend
- **Google Apps Script (GAS)** for spreadsheet-to-JSON API

## Commands

```bash
# コンテナ起動
docker compose up --build -d

# データ収集（CSV出力）
docker compose exec app python check_youtube_utano.py

# Webアプリ dev サーバー起動
docker compose exec -e VITE_GAS_URL=<GAS_URL> web npm run dev

# Webアプリ ビルド
docker compose exec -e VITE_GAS_URL=<GAS_URL> web npm run build
```

## Environment

- `YOUTUBE_API_KEY`: YouTube Data API v3 のAPIキー。`.env`ファイルに設定（Git管理外）
- `VITE_GAS_URL`: GAS WebアプリのURL。devサーバー起動時に環境変数で渡す

## Architecture

Python スクリプト（`check_youtube_utano.py`）でYouTube APIからライブ配信のコメントを取得し、セットリストから「六甲おろし」を検出してCSVに出力する。CSVはGoogle スプレッドシートで人間がチェックし、GAS経由でJSON APIとして公開。Webアプリ（`web/`）がGASからデータを取得して表示する。
