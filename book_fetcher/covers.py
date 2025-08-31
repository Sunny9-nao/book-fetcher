from __future__ import annotations

import os
from typing import Optional

import requests


def download_cover(url: str, output_path: str, timeout: int = 30) -> None:
    with requests.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

