from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import BookInfo
from .utils import http_get, parse_year_from_date


GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"


def google_image_links_to_cover_urls(image_links: Dict[str, Any]) -> Dict[str, str]:
    if not image_links:
        return {}
    out: Dict[str, str] = {}
    if isinstance(image_links, dict):
        for key in ("smallThumbnail", "thumbnail"):
            if image_links.get(key):
                out.setdefault("s", image_links[key])
                break
        for key in ("medium", "thumbnail", "small"):
            if image_links.get(key):
                out.setdefault("m", image_links[key])
                break
        for key in ("extraLarge", "large", "medium", "thumbnail"):
            if image_links.get(key):
                out.setdefault("l", image_links[key])
                break
    return out


def gb_pick_isbn(industry_ids: Any) -> List[str]:
    if not isinstance(industry_ids, list):
        return []
    vals: List[str] = []
    for obj in industry_ids:
        if not isinstance(obj, dict):
            continue
        ident = obj.get("identifier")
        if isinstance(ident, str) and len(ident.replace("-", "")) in (10, 13):
            vals.append(ident.replace("-", ""))
    seen = set()
    uniq: List[str] = []
    for v in vals:
        if v not in seen:
            uniq.append(v)
            seen.add(v)
    return uniq


def search_googlebooks(
    title: Optional[str] = None,
    author: Optional[str] = None,
    isbn: Optional[str] = None,
    api_key: Optional[str] = None,
    timeout: int = 15,
) -> Dict[str, Any]:
    q_parts: List[str] = []
    if isbn:
        q_parts.append(f"isbn:{isbn}")
    if title:
        q_parts.append(f"intitle:{title}")
    if author:
        q_parts.append(f"inauthor:{author}")
    q = "+".join(q_parts) if q_parts else title or ""
    params: Dict[str, Any] = {"q": q, "maxResults": 5}
    if api_key:
        params["key"] = api_key
    r = http_get(GOOGLE_BOOKS_URL, params=params, timeout=timeout)
    return r.json()


def select_google_item(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    items = data.get("items") if isinstance(data, dict) else None
    if not items or not isinstance(items, list):
        return None
    return items[0]


def build_bookinfo_from_google(item: Dict[str, Any]) -> Optional[BookInfo]:
    if not item:
        return None
    vi = item.get("volumeInfo", {}) or {}
    if not vi:
        return None
    title = vi.get("title") or ""
    authors = vi.get("authors") or []
    publisher = vi.get("publisher")
    publishers = [publisher] if publisher else []
    published_date = vi.get("publishedDate")
    first_year = parse_year_from_date(published_date)
    isbns = gb_pick_isbn(vi.get("industryIdentifiers"))
    description = vi.get("description")
    categories = vi.get("categories") or []
    cover_urls = google_image_links_to_cover_urls(vi.get("imageLinks"))
    return BookInfo(
        title=title,
        authors=authors,
        first_publish_year=first_year,
        publishers=publishers,
        publish_date=published_date,
        isbns=isbns,
        openlibrary_work_key=None,
        openlibrary_edition_key=None,
        openlibrary_url=None,
        description=description,
        subjects=categories,
        cover_urls=cover_urls,
    )


def augment_with_google(
    info: BookInfo,
    title: Optional[str],
    authors_query: Optional[List[str]],
    isbns_query: Optional[List[str]],
    api_key: Optional[str] = None,
) -> BookInfo:
    isbn = None
    if isbns_query:
        isbn = next((i for i in isbns_query if i and len(i) in (10, 13)), None)
    try:
        gb = search_googlebooks(title=title, author=(authors_query or [None])[0] if authors_query else None, isbn=isbn, api_key=api_key)
        item = select_google_item(gb)
    except Exception:
        item = None
    if not item:
        return info

    vi = item.get("volumeInfo", {}) or {}
    if not vi:
        return info

    if not info.description:
        desc = vi.get("description")
        if isinstance(desc, str) and desc.strip():
            info.description = desc.strip()

    if not info.publish_date:
        pd = vi.get("publishedDate")
        if isinstance(pd, str) and pd.strip():
            info.publish_date = pd.strip()

    if not info.first_publish_year:
        yr = parse_year_from_date(info.publish_date or vi.get("publishedDate"))
        if yr:
            info.first_publish_year = yr

    if not info.publishers:
        pub = vi.get("publisher")
        if isinstance(pub, str) and pub.strip():
            info.publishers = [pub.strip()]

    gb_isbns = gb_pick_isbn(vi.get("industryIdentifiers"))
    if gb_isbns:
        seen = set(info.isbns)
        for i in gb_isbns:
            if i not in seen:
                info.isbns.append(i)
                seen.add(i)

    if not info.authors:
        ga = vi.get("authors") or []
        if ga:
            info.authors = list(dict.fromkeys([str(a) for a in ga]))

    cats = vi.get("categories") or []
    if cats:
        existing = set(info.subjects)
        for c in cats:
            if c not in existing:
                info.subjects.append(c)
                existing.add(c)

    g_covers = google_image_links_to_cover_urls(vi.get("imageLinks"))
    for size_key, url in g_covers.items():
        info.cover_urls.setdefault(size_key, url)

    return info

