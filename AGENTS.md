# Codex 作業ガイド

Codex は実装を担当し、Claude は設計・レビューを担当します。詳細なルールは [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) を参照してください。

## 要点

- `feature/*`、`fix/*`、`docs/*`、`chore/*` で作業し、`main` へ直接 push しない。変更は PR 経由にする。
- コミットは `[種別] 端的な日本語要約` の形式とし、本文に変更理由を書く。1コミット1目的にする。
- Python は ruff・新規追加・変更する関数への型ヒント・I/O と純粋ロジックの分離を守る。既存コードは変更時に段階的に型ヒントを付与する。TypeScript は strict・ESLint・外部 JSON の型ガードを守る。
- 秘密情報をログに出さず、`dangerouslySetInnerHTML` と `pull_request_target` を使わない。
- ロジック変更にはテストを追加し、バグ修正では再現テストを先に書く。
- Secrets、デプロイ、公開範囲、リポジトリ設定の変更はユーザー確認が必要。
- コミット・push・デプロイはしない。

## ローカル確認コマンド

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest

cd web && npm run lint
cd web && npm run typecheck
cd web && npm test
cd web && VITE_GAS_URL=https://example.invalid npm run build
```
