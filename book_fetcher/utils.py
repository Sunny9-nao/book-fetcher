from __future__ import annotations

from typing import Any, Dict, Optional

import requests


def http_get(url: str, params: Optional[dict] = None, timeout: int = 15) -> requests.Response:
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r


def normalize_desc(desc: Any) -> Optional[str]:
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
    import re

    s = (s or "book").strip()
    s = re.sub(r"[\\/:*?\"<>|]+", "", s)
    s = re.sub(r"\s+", "_", s)
    return (s or "book")[:maxlen]

