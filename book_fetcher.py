#!/usr/bin/env python3
from __future__ import annotations

"""エントリーポイント（実行用の薄いファイル）

コマンド例（推奨）: `python3 -m book_fetcher --preset standard`
このファイルを直接実行しても同じ動作になります。
"""

from book_fetcher.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
