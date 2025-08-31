"""Book Fetcher パッケージ

非エンジニアの方にも分かりやすい形で、書籍情報を取得・保存するための
モジュール群をまとめています。主な役割は以下の通りです。

- openlibrary: Open Library API へ問い合わせる処理
- googlebooks: Google Books から不足情報を補完する処理
- amazon: Amazon の商品/検索リンクを作る処理（安全なリンク生成のみ）
- service: 各APIの結果をまとめて「1冊の本の情報」に統合する中核
- covers: カバー画像をダウンロードする処理
- render: 画面表示用のテキストを組み立てる処理
- cli: コマンドライン引数の受け取り～結果出力までの流れ
"""

__all__ = [
    "__version__",
]

__version__ = "0.1.0"
