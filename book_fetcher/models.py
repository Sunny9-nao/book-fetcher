from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BookCandidate:
    index: int
    title: str
    author_names: List[str]
    first_publish_year: Optional[int]
    work_key: Optional[str]
    edition_keys: List[str]
    cover_id: Optional[int]
    isbns: List[str]


@dataclass
class BookInfo:
    title: str
    authors: List[str]
    first_publish_year: Optional[int]
    publishers: List[str]
    publish_date: Optional[str]
    isbns: List[str]
    openlibrary_work_key: Optional[str]
    openlibrary_edition_key: Optional[str]
    openlibrary_url: Optional[str]
    description: Optional[str]
    subjects: List[str]
    cover_urls: Dict[str, str]
    amazon_urls: Dict[str, str] = field(default_factory=dict)

