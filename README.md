# utano-youtube-checker

白玖ウタノの公開ライブ配信における「六甲おろし」歌唱回数を公開する非公式サイトです。

## データフロー

```text
GitHub Actions（毎日 JST 06:00）→ YouTube Data API v3 → data/videos.json
                                                ↓（変更時だけ）
                                           レビュー用 PR
                                                ↓（確認してマージ）
data/videos.json → ビルド時 JSON → GitHub Pages
```

閲覧時は GitHub Pages 上の `data/rokko.json` だけを取得し、外部APIを呼びません。

日次集計は毎日 6:00 JST に実行します。タイトル更新のため、サイトは毎週月曜 2:00 JST に再デプロイします。

## data の役割

- `videos.json`: 配信の集計値と確認状態を保存する唯一のデータファイルです。
- `confirmed: true` は人が確認済みの値で、日次集計は変更しません。
- 未登録の配信と、未確定かつ配信開始から3日以内の配信だけを日次集計します。

確認して値を直す場合は、レコードを `confirmed: true` にし、`reason` と `decided_on`（`YYYY-MM-DD`）を対で記入します。保存されるタイムスタンプは `h:mm:ss` です。セットリストのコメントは `mm:ss` 表記も読み取り、たとえば `12:43` は `0:12:43` に正規化します。

## 日次 PR の確認

PR 本文の変更表で回数・タイムスタンプリンク・根拠行を確認します。修正が必要なら `videos.json` の値を直し、確定フラグと理由・決定日を記入します。判定の詳細は [仕様書](docs/spec.md) を参照してください。

## セットアップとローカル実行

GitHub の Settings → Secrets and variables → Actions で `YOUTUBE_API_KEY` を登録します。Settings → Actions → General の「Allow GitHub Actions to create and approve pull requests」も有効にします。Google Cloud Console では当該キーを **YouTube Data API v3 のみ** に API 制限してください（アプリケーション制限も環境に合わせて設定）。値をリポジトリやログへ保存しません。

```bash
# 確認済みの過去 CSV を用意した後、一度だけ実行
uv run python -m collector import-confirmed --csv /path/to/confirmed.csv --reason "確認済み" --decided-on YYYY-MM-DD

# 日次更新・レビュー本文生成
uv run python -m collector update --report /tmp/review.md

# サイト用 JSON の生成
uv run python -m collector build-site --out web/public/data/rokko.json
```

Docker 利用時も app サービスで同じコマンドを実行できます。

```bash
docker compose exec app python -m collector update --report /tmp/review.md
```

Web 開発サーバーの前に公開 JSON を生成します。

```bash
uv run python -m collector build-site --out web/public/data/rokko.json
cd web && npm run dev
```

## 確認コマンド

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
cd web && npm run lint && npm run typecheck && npm test
```
