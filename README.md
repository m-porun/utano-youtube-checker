# utano-youtube-checker

白玖ウタノの公開ライブ配信における「六甲おろし」歌唱回数を公開する非公式サイトです。

## データフロー

```text
GitHub Actions（毎日 JST 06:00）→ YouTube Data API v3 → data/counts.json
                                                ↓（変更時だけ）
                                           レビュー用 PR
                                                ↓（確認してマージ）
data/baseline.json / counts.json / overrides.json → ビルド時 JSON → GitHub Pages
```

閲覧時は GitHub Pages 上の `data/rokko.json` だけを取得し、外部APIを呼びません。

## data の役割

- `baseline.json`: スプレッドシートで確認済みの過去配信。0回配信も含み、再集計しません。
- `counts.json`: baseline にない配信を日次自動集計した結果。PR で確認する対象です。
- `overrides.json`: 人による補正。`overrides > baseline > counts` で最優先です。

override は `videos` に動画 ID をキーとして、`count`、`timestamps`、`reason`、`decided_on`（`YYYY-MM-DD`）を記入します。タイムスタンプは `h:mm:ss` です。

## 日次 PR の確認

PR 本文の変更表で回数・タイムスタンプリンク・根拠行を確認し、「要確認」のセットリスト未発見や未集計言及を判断します。修正が必要なら `overrides.json` を追加・更新してからマージします。PR ブランチ上で加えた override のコミットは、翌日の更新でも保持されます。

## セットアップとローカル実行

GitHub の Settings → Secrets and variables → Actions で `YOUTUBE_API_KEY` を登録します。Settings → Actions → General の「Allow GitHub Actions to create and approve pull requests」も有効にします。Google Cloud Console では当該キーを **YouTube Data API v3 のみ** に API 制限してください（アプリケーション制限も環境に合わせて設定）。値をリポジトリやログへ保存しません。

```bash
# 確認済みの過去 CSV を用意した後、一度だけ実行
uv run python -m collector import-baseline --csv /path/to/confirmed.csv --source-name confirmed.csv

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
