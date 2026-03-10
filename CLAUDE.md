# CLAUDE.md

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

## Commands

```bash
# Install dependencies (local)
uv sync

# Run the main script (local)
uv run python check_youtube_utano.py

# Docker build and run
docker compose up --build

# Run in existing container
docker compose exec app python check_youtube_utano.py
```

## Environment

`YOUTUBE_API_KEY`が設定された`.env`ファイルが必要です。`.env`ファイルはGitとClaudeの管理対象外です。

## Architecture

APIキーを使ってYouTube Data APIに接続する単一スクリプトのアプリケーション（`check_youtube_utano.py`）です。対象プレイリストは`PLUi5gdZovvGlyVfVOyzmgOwZ8jd0bT2mS`としてハードコードされています。このプロジェクトはまだ開発の初期段階にあり、スクリプトは現在、APIキーの接続性検証のみを行っています。
