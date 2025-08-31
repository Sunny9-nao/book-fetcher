from __future__ import annotations

from typing import Any, Dict, List, Optional

from .amazon import build_amazon_urls
from .googlebooks import (
    augment_with_google,
    build_bookinfo_from_google,
    search_googlebooks,
    select_google_item,
)
from .models import BookInfo
from .openlibrary import (
    OPENLIB_BASE,
    build_cover_urls,
    choose_candidate,
    fetch_edition_details,
    fetch_work_details,
    search_openlibrary,
)
from .utils import normalize_desc


def fetch_book_info(
    title: str,
    author: Optional[str] = None,
    year: Optional[int] = None,
    pick_index: int = 0,
    use_google: bool = False,
    google_api_key: Optional[str] = None,
    amazon_domain: str = "co.jp",
) -> Optional[BookInfo]:
    candidates = search_openlibrary(title=title, author=author, year=year, limit=max(5, pick_index + 1))
    cand = choose_candidate(candidates, pick_index)
    if not cand:
        if use_google:
            try:
                gb = search_googlebooks(title=title, author=author, api_key=google_api_key)
                item = select_google_item(gb)
                binfo = build_bookinfo_from_google(item)
                if binfo:
                    binfo.amazon_urls = build_amazon_urls(binfo.title, binfo.authors, binfo.isbns, amazon_domain)
                return binfo
            except Exception:
                return None
        return None

    description: Optional[str] = None
    subjects: List[str] = []
    publishers: List[str] = []
    publish_date: Optional[str] = None

    if cand.work_key:
        try:
            work = fetch_work_details(cand.work_key)
            description = normalize_desc(work.get("description")) or description
            subjects = work.get("subjects", []) or subjects
        except Exception:
            pass

    edition_key: Optional[str] = cand.edition_keys[0] if cand.edition_keys else None
    if edition_key:
        try:
            ed = fetch_edition_details(edition_key)
            description = normalize_desc(ed.get("description")) or normalize_desc(ed.get("notes")) or description
            pubs = ed.get("publishers") or []
            if isinstance(pubs, list):
                publishers = [p["name"] if isinstance(p, dict) and "name" in p else str(p) for p in pubs]
            publish_date = ed.get("publish_date") or publish_date
        except Exception:
            pass

    cover_urls = build_cover_urls(cand.cover_id, cand.isbns)
    openlibrary_url = None
    if cand.work_key:
        openlibrary_url = f"{OPENLIB_BASE}{cand.work_key}"
    elif edition_key:
        openlibrary_url = f"{OPENLIB_BASE}/books/{edition_key}"

    result = BookInfo(
        title=cand.title,
        authors=cand.author_names,
        first_publish_year=cand.first_publish_year,
        publishers=publishers,
        publish_date=publish_date,
        isbns=cand.isbns,
        openlibrary_work_key=cand.work_key,
        openlibrary_edition_key=edition_key,
        openlibrary_url=openlibrary_url,
        description=description,
        subjects=subjects,
        cover_urls=cover_urls,
    )

    if use_google:
        result = augment_with_google(
            result,
            title=cand.title or title,
            authors_query=cand.author_names,
            isbns_query=cand.isbns,
            api_key=google_api_key,
        )

    result.amazon_urls = build_amazon_urls(result.title, result.authors, result.isbns, amazon_domain)
    return result


def build_cover_filename(info: BookInfo, size: str) -> str:
    from .utils import slugify_filename

    base = slugify_filename(info.title)
    suffix = None
    if info.openlibrary_edition_key:
        suffix = info.openlibrary_edition_key
    elif info.openlibrary_work_key:
        suffix = (info.openlibrary_work_key or "").split("/")[-1]
    elif info.isbns:
        suffix = info.isbns[0]
    if suffix:
        base = f"{base}_{suffix}"
    return f"{base}_{size}.jpg"

