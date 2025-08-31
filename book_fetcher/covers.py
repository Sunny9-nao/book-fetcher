from __future__ import annotations

"""カバー画像の保存

指定されたURLから画像データをダウンロードし、指定パスに保存します。
"""

import os
from typing import Optional

import requests


def download_cover(url: str, output_path: str, timeout: int = 30) -> None:
    """カバー画像を保存する関数。

    引数:
    - url: 画像のURL
    - output_path: 保存先ファイルパス（例: covers/xxx_l.jpg）
    - timeout: 通信の待ち時間（秒）
    """
    with requests.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
