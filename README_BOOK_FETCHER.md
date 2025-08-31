# Book Fetcher

Open Library（公開API・APIキー不要）をベースに、必要に応じて Google Books でも補完し、書籍情報・カバー画像URL・概要・Amazonリンク（安全な検索/ISBNリンク）を取得するツールです。

## 動作要件

- Python 3.8 以上
- インターネット接続（Open Library へアクセスします）
- 追加ライブラリ: `requests`

## ディレクトリ構成（抜粋）

```
book-fetcher/
  ├─ book_fetcher/        # 実装（モジュール）
  │   ├─ __main__.py      # python3 -m book_fetcher のエントリ
  │   ├─ cli.py           # CLI本体
  │   ├─ service.py       # 取得/統合の中核
  │   ├─ openlibrary.py   # Open Library クライアント
  │   ├─ googlebooks.py   # Google Books 補完
  │   ├─ amazon.py        # Amazonリンク生成
  │   ├─ render.py        # テキスト出力
  │   └─ models.py / utils.py
  ├─ book_fetcher.py      # 薄いシム（python3 book_fetcher.pyでも実行可）
  ├─ requirements.txt
  ├─ README_BOOK_FETCHER.md
  └─ .venv/
```

## セットアップ

```bash
cd book-fetcher
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

すでに `.venv` が作成済みの場合は、有効化のみで構いません。

## 使い方（最短）

仮想環境を有効化後、`titles.txt`（1行1タイトル）を用意し、次で実行します。

```bash
# 標準プリセット（推奨）：JSON出力をresults.jsonへ保存＋Lサイズのカバーをcovers/へ保存
python3 -m book_fetcher --preset standard

# 省略形：引数なし・titles.txtがある場合、同等の処理を自動実行
python3 -m book_fetcher
```

実行後の主な成果物
- `results.json`: 書籍情報の配列（Open Library＋必要に応じてGoogleで補完、amazon_urls含む）
- `covers/`: Lサイズのカバー画像一式

`titles.txt` の例
```
The Pragmatic Programmer
Norwegian Wood
# コメント行
The Hobbit
```

単体の本を調べたい場合
```bash
python3 -m book_fetcher "Norwegian Wood"
# JSONで1件だけ表示
python3 -m book_fetcher --format json "Norwegian Wood"
```

バッチ出力を明示的に制御したい場合
```bash
# 出力先やカバー保存先を変更
python3 -m book_fetcher --format json --input-file titles.txt \
  --output-file out.json --covers-dir covers --cover-size l
```

注意:
- `--input-file`使用時は`--show-candidates`や`--download-cover`は利用できません（エラーになります）。
- `--author`や`--year`はバッチ全体に適用されます。
- `--use-google`はバッチでも有効です。Google側のクォータ/レート制限に注意してください。
- `--covers-dir`はバッチ専用です。単体のカバー保存は`--download-cover`を使ってください。

## 取得できる情報

- タイトル、著者、初出年
- 出版社、出版日（取得できる場合）
- ISBN（取得できる場合）
- Open Library のURL
- Subjects（主題）と概要（取得できる場合）
- カバー画像URL（S / M / L）

## 注意事項・よくある質問

- 取得データは Open Library の Search / Work / Edition API 由来です。書籍によっては概要や出版社などが登録されていないことがあります。
- カバー画像は `cover_id` または ISBN をもとに組み立てたURLから参照します。存在しない場合はダウンロードできません。
- 日本語タイトルでも検索可能です。結果の候補が複数ある場合は `--show-candidates` で確認し、`--pick-index` で選択してください。
- ネットワークやプロキシの影響で接続に失敗する場合があります。再実行しても改善しない場合はご相談ください。

## 開発メモ

- 実行エントリ: `python3 -m book_fetcher`（モジュール実行推奨）
- 依存関係: `requirements.txt`（`requests` のみ）
- Google BooksのAPIキーは任意（`--google-api-key` または `GOOGLE_BOOKS_API_KEY`）。未指定でも動作する場合あり。
