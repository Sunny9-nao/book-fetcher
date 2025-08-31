from __future__ import annotations

"""Open Library クライアント

Open Library（無料・APIキー不要）の検索や詳細取得を担当します。
"""

from typing import Any, Dict, List, Optional

from .models import BookCandidate
from .utils import http_get


OPENLIB_SEARCH_URL = "https://openlibrary.org/search.json"  # 検索APIのURL
OPENLIB_BASE = "https://openlibrary.org"  # ページや詳細APIのベースURL
OPENLIB_COVER_BASE = "https://covers.openlibrary.org"  # カバー画像のベースURL


def search_openlibrary(
    title: str,
    author: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = 5,
) -> List[BookCandidate]:
    """タイトル（と任意で著者・年）で本を検索し、候補一覧を返す。"""
    params = {"title": title, "limit": limit}
    if author:
        params["author"] = author
    if year:
        params["first_publish_year"] = year

    res = http_get(OPENLIB_SEARCH_URL, params=params)
    data = res.json()
    docs = data.get("docs", [])
    candidates: List[BookCandidate] = []
    for i, d in enumerate(docs[:limit]):
        candidates.append(
            BookCandidate(
                index=i,
                title=d.get("title") or d.get("title_suggest") or "",
                author_names=d.get("author_name", []) or [],
                first_publish_year=d.get("first_publish_year"),
                work_key=d.get("key"),
                edition_keys=d.get("edition_key", []) or [],
                cover_id=d.get("cover_i"),
                isbns=d.get("isbn", []) or [],
            )
        )
    return candidates


def fetch_work_details(work_key: str) -> Dict[str, Any]:
    """作品（work）の詳細JSONを取得する（例: /works/OL…W）。"""
    url = f"{OPENLIB_BASE}{work_key}.json"
    return http_get(url).json()


def fetch_edition_details(edition_key: str) -> Dict[str, Any]:
    """版（edition）の詳細JSONを取得する（例: OL…M）。"""
    url = f"{OPENLIB_BASE}/books/{edition_key}.json"
    return http_get(url).json()


def build_cover_urls(
    cover_id: Optional[int] = None,
    isbns: Optional[List[str]] = None,
) -> Dict[str, str]:
    """カバー画像のURL（S/M/L）を組み立てる。cover_id か ISBN を利用。"""
    urls: Dict[str, str] = {}
    if cover_id:
        for size in ("S", "M", "L"):
            urls[size.lower()] = f"{OPENLIB_COVER_BASE}/b/id/{cover_id}-{size}.jpg"
        return urls
    if isbns:
        isbn = next((i for i in isbns if i and len(i) in (10, 13)), None)
        if isbn:
            for size in ("S", "M", "L"):
                urls[size.lower()] = f"{OPENLIB_COVER_BASE}/b/isbn/{isbn}-{size}.jpg?default=false"
    return urls


def choose_candidate(candidates: List[BookCandidate], index: int = 0) -> Optional[BookCandidate]:
    """候補一覧から、指定のインデックス（なければ先頭）を選ぶ。"""
    if not candidates:
        return None
    if 0 <= index < len(candidates):
        return candidates[index]
    return candidates[0]
