# 日次集計仕様

## 構成

毎日 JST 06:00 に GitHub Actions がアップロード再生リストを全件取得し、`actualStartTime` を持つライブだけを判定する。確認済みの `baseline.json` は境界として扱い、そこにないライブだけの人気順トップレベルコメント20件を再集計する。変更があるときだけ `data/daily-update` ブランチの PR を作る。

```text
YouTube API → collector update → counts.json → PR レビュー → main
                                                    ↓
                         collector build-site ← baseline / overrides / counts
                                                    ↓
                                               rokko.json → Web
```

`overrides > baseline > counts` の順で回数を決める。タイトルなど YouTube API 由来のデータは、ビルド時の `rokko.json` にだけ含め、リポジトリには保存しない。

## 判定

セットリスト候補はキーワードと `h:mm:ss` を両方持つコメントで、複数ならタイムスタンプ数最多を選ぶ。最初のタイムスタンプより前は数えず、「配信内容」「タイムライン」「雑談」以降は打ち切る。同一区間の重複は一回とする。

## 運用

日次 PR の回数・証拠・要確認項目を人が確認する。補正は `overrides.json` に理由と決定日を残す。
