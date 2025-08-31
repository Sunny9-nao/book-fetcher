from __future__ import annotations

from typing import Dict, List, Optional
from urllib.parse import quote_plus


def isbn13_to_isbn10(isbn13: str) -> Optional[str]:
    if not isinstance(isbn13, str):
        return None
    digits = "".join(ch for ch in isbn13 if ch.isdigit())
    if len(digits) != 13 or not digits.startswith("978"):
        return None
    core = digits[3:12]  # 9 digits
    total = 0
    for i, ch in enumerate(core):
        total += (10 - i) * int(ch)
    check = (11 - (total % 11)) % 11
    check_char = "X" if check == 10 else str(check)
    return core + check_char


def build_amazon_urls(
    title: Optional[str],
    authors: Optional[List[str]],
    isbns: Optional[List[str]],
    domain: str = "co.jp",
) -> Dict[str, str]:
    host_map = {
        "co.jp": "https://www.amazon.co.jp",
        "com": "https://www.amazon.com",
        "co.uk": "https://www.amazon.co.uk",
        "de": "https://www.amazon.de",
        "fr": "https://www.amazon.fr",
        "it": "https://www.amazon.it",
        "es": "https://www.amazon.es",
        "ca": "https://www.amazon.ca",
        "com.au": "https://www.amazon.com.au",
    }
    base = host_map.get(domain, host_map["co.jp"])
    urls: Dict[str, str] = {}

    isbn10: Optional[str] = None
    if isbns:
        isbn10 = next((i for i in isbns if isinstance(i, str) and len(i.replace("-", "")) == 10), None)
        if not isbn10:
            isbn13 = next((i for i in isbns if isinstance(i, str) and len(i.replace("-", "")) == 13), None)
            if isbn13:
                isbn10 = isbn13_to_isbn10(isbn13)
    if isbn10:
        isbn10 = isbn10.replace("-", "")
        urls["product"] = f"{base}/dp/{isbn10}"

    q_parts: List[str] = []
    if title:
        q_parts.append(title)
    if authors:
        q_parts.append(authors[0])
    q = quote_plus(" ".join([p for p in q_parts if p])) if q_parts else ""
    urls["search"] = f"{base}/s?k={q}&i=stripbooks"
    return urls

