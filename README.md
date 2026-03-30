# utano-youtube-checker

白珠ウタノ - 六甲おろしカウンター

VTuber「[白玖ウタノ](https://www.youtube.com/@UTANOch)」がライブ配信で「六甲おろし」を歌った回数をカウントし、Webページで公開するプロジェクト。

## 仕組み

```
1. Python スクリプトで YouTube API からライブ配信のコメントを取得
2. セットリストコメントから「六甲おろし」を検出し、CSV に出力
3. CSV を Google スプレッドシートにコピーし、人間の目で正確性をチェック
4. GAS（Google Apps Script）がスプレッドシートを JSON API として公開
5. Webアプリ（React）が GAS から データを取得して表示
```

## 技術スタック

| レイヤー | 技術 |
|---|---|
| データ収集 | Python 3.14 / uv / google-api-python-client |
| データ管理 | Google スプレッドシート |
| API | Google Apps Script（GAS） |
| フロントエンド | Vite + React + TailwindCSS v4 |
| コンテナ | Docker + docker-compose |
| デプロイ | GitHub Pages + GitHub Actions |

## プロジェクト構成

```
utano-youtube-checker/
├── check_youtube_utano.py   # データ収集スクリプト（YouTube API → CSV）
├── output/
│   └── rokko_count.csv      # 出力CSV（git管理外）
├── gas/
│   └── ReadRokkoCount.gs    # GAS コード（スプレッドシート → JSON API）
├── web/                     # Webアプリ（Vite + React）
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── RokkoCount.tsx       # 歌唱総数の表示
│   │   │   ├── IntroSequence.tsx    # イントロ演出
│   │   │   ├── VideoCard.tsx        # 動画カード（YouTube埋め込み）
│   │   │   └── TimestampList.tsx    # タイムスタンプリンク
│   │   ├── hooks/
│   │   │   └── useRokkoData.ts      # GAS API データ取得
│   │   └── types.ts
│   └── ...
├── .github/workflows/
│   └── deploy.yml           # GitHub Pages 自動デプロイ
├── docs/
│   └── spec.md              # 機能仕様書
├── Dockerfile
└── docker-compose.yaml
```

## 開発環境セットアップ

### 前提条件

- Docker / Docker Compose
- `.env` ファイルに `YOUTUBE_API_KEY` を設定済み

### 1. コンテナの起動

```bash
# 全コンテナをビルド＆起動
docker compose up --build -d
```

2つのコンテナが起動する:

| コンテナ | 用途 | イメージ |
|---|---|---|
| `utano_youtube_checker` | Python スクリプト実行用 | python:3.14-slim + uv |
| `utano_web` | Webアプリ開発用 | node:22-slim |

### 2. データ収集（Python）

```bash
docker compose exec app python check_youtube_utano.py
```

`output/rokko_count.csv` が生成される。

### 3. Webアプリの開発サーバー起動

```bash
# 依存関係のインストール（初回のみ）
docker compose exec web npm install

# dev サーバー起動（GAS URLを環境変数で渡す）
docker compose exec -e VITE_GAS_URL=<GAS_URL> web npm run dev
```

Webアプリの接続URL: http://localhost:5173/utano-youtube-checker/

### 4. Webアプリのビルド

```bash
docker compose exec -e VITE_GAS_URL=<GAS_URL> web npm run build
```

`web/dist/` にビルド成果物が出力される。

## データ更新フロー

1. `docker compose exec app python check_youtube_utano.py` でCSV出力
2. CSVの内容を Google スプレッドシートにコピー
3. 人間の目で六甲おろしのカウントが正しいか確認・修正
4. GAS のスクリプトエディタで `clearCache` 関数を実行（キャッシュクリア）
5. Webページに最新データが反映される

## 環境変数

| 変数 | 用途 | 設定場所 |
|---|---|---|
| `YOUTUBE_API_KEY` | YouTube Data API v3 のAPIキー | `.env` |
| `VITE_GAS_URL` | GAS WebアプリのURL | dev サーバー起動時 / GitHub Secrets |
