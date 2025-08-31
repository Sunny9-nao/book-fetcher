from __future__ import annotations

"""共通ユーティリティ

非エンジニア向けの要約:
- http_get: URLにアクセスして結果を返す基本関数
- normalize_desc: 概要テキストを整える（空文字や辞書形式に対応）
- parse_year_from_date: 日付文字列から「年」だけ取り出す
- slugify_filename: ファイル名に使える安全な文字へ変換する
"""

from typing import Any, Dict, Optional

import requests


def http_get(url: str, params: Optional[dict] = None, timeout: int = 15) -> requests.Response:
    """HTTPでGETアクセスを行う基本関数。

    引数:
    - url: アクセス先URL
    - params: クエリパラメータ（?key=value の部分）
    - timeout: 待ち時間（秒）
    戻り値: requests.Response（成功時のレスポンス）
    """
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r


def normalize_desc(desc: Any) -> Optional[str]:
    """APIから得た「説明文」表現を統一してテキストにする。

    desc が文字列ならそのまま、辞書なら value を取り、空なら None を返す。
    """
    if not desc:
        return None
    if isinstance(desc, str):
        return desc.strip() or None
    if isinstance(desc, dict):
        val = desc.get("value")
        if isinstance(val, str):
            return val.strip() or None
    return None


def parse_year_from_date(date_str: Optional[str]) -> Optional[int]:
    """日付文字列（例: 1999-04-01）から「年」だけを取り出す。見つからない場合は None。"""
    if not date_str or not isinstance(date_str, str):
        return None
    for i in range(len(date_str)):
        if date_str[i : i + 4].isdigit():
            try:
                year = int(date_str[i : i + 4])
                if 1000 <= year <= 2100:
                    return year
            except Exception:
                pass
    return None


def slugify_filename(s: str, maxlen: int = 64) -> str:
    """ファイル名に安全に使えるように、危険文字を取り除き置換する。"""
    import re

    s = (s or "book").strip()
    s = re.sub(r"[\\/:*?\"<>|]+", "", s)
    s = re.sub(r"\s+", "_", s)
    return (s or "book")[:maxlen]
