# CLAUDE.md

## ペルソナ（最優先）
このプロジェクトでの応答はすべて ~/.claude/agents/sunsun.md のペルソナ・口調ルールに従うこと。

このファイルは、本リポジトリ内のコードを扱う際に、Claude Code（claude.ai/code）が従うべき指針を示しています。

## Project Overview

白玖ウタノ(Shiratama Utano)のYouTubeチャンネル[UTANO ch. 白玖ウタノ](https://www.youtube.com/@UTANOch)の、[公開ライブ配信](https://www.youtube.com/@UTANOch/streams)すべてを対象にします。
チャンネルのアップロード再生リスト（UU...）から取得した動画のうち、`liveStreamingDetails` を持つライブ配信を抽出し、各配信の人気順上位20件のトップレベルコメントにある「Set List」から「六甲おろし」の回数を数えてWebページに表示します。
つまり、これまで白玖ウタノが「六甲おろし」を歌った数をコメントの中から判断して表示したいということです。

## Tech Stack

- **Python 3.14** with **uv** as the package manager
- **google-api-python-client** for YouTube Data API v3
- **python-dotenv** for environment variable management
- **Docker** + **docker-compose** for containerized execution
- **Vite + React + TailwindCSS v4** for the web frontend

## Commands

```bash
# コンテナ起動
docker compose up --build -d

# 日次集計（レビュー本文を生成）
docker compose exec app python -m collector update --report /tmp/review.md

# Webアプリ dev サーバー起動
docker compose exec web npm run dev

# Webアプリ ビルド
docker compose exec app python -m collector build-site --out web/public/data/rokko.json
docker compose exec web npm run build

# Python lint・format・テスト
uv run ruff check .
uv run ruff format --check .
uv run pytest

# Web lint・型検査・テスト
cd web && npm run lint
cd web && npm run typecheck
cd web && npm test
```

## 役割分担と確認ゲート

- Claude は設計・レビュー、Codex は実装を担当する。
- 実装前後に変更サマリーを提示し、ユーザーの承認を得る。PR 作成前にも確認する。
- 外部公開、情報漏えいの可能性がある変更は、必ず事前にユーザーへ確認する。
- コミットメッセージはペルソナ口調にせず、端的な日本語で記述する。
- 詳細な開発ルールは [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) を参照する。
- AI エージェントは GitHub の PR・Issue をマージまたはクローズせず、その提案もしない。判断と操作はユーザーが行う。
- コメントとドキュメントは初めて読む人向けに、現在の仕様と必要な選択理由だけを書く。変更の経緯はコミットメッセージとPR本文に記録する。
- 実行時刻・曜日・頻度・保存期間・上限値など具体的な値は、推奨値と理由を添えてユーザーに確認し、AI エージェントが独断で決めない。
- タイムゾーンが関わる値は、日本時間と設定値を併記する。GitHub Actions の cron は UTC で指定する。

## Environment

- `YOUTUBE_API_KEY`: YouTube Data API v3 のAPIキー。`.env`ファイルに設定（Git管理外）

## Architecture

GitHub Actions は未登録の配信と、未確定かつ配信開始から3日以内の配信を集計する。確認済みレコードは変更せず、`videos.json` から公開 JSON を生成してWebアプリが表示する。
