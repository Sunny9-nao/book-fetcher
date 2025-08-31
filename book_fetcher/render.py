from __future__ import annotations

from typing import List

from .models import BookInfo


def render_text(info: BookInfo) -> str:
    lines: List[str] = []
    lines.append(f"Title: {info.title}")
    if info.authors:
        lines.append(f"Authors: {', '.join(info.authors)}")
    if info.first_publish_year:
        lines.append(f"First Publish Year: {info.first_publish_year}")
    if info.publish_date:
        lines.append(f"Publish Date: {info.publish_date}")
    if info.publishers:
        lines.append(f"Publishers: {', '.join(info.publishers)}")
    if info.isbns:
        lines.append(f"ISBNs: {', '.join(info.isbns[:5])}{'...' if len(info.isbns) > 5 else ''}")
    if info.openlibrary_url:
        lines.append(f"Open Library: {info.openlibrary_url}")
    if info.subjects:
        lines.append(f"Subjects: {', '.join(info.subjects[:8])}{'...' if len(info.subjects) > 8 else ''}")
    if info.cover_urls:
        lines.append("Cover URLs:")
        for k in ["l", "m", "s"]:
            if k in info.cover_urls:
                lines.append(f"  {k.upper()}: {info.cover_urls[k]}")
    if info.amazon_urls:
        if info.amazon_urls.get("product"):
            lines.append(f"Amazon Product: {info.amazon_urls['product']}")
        if info.amazon_urls.get("search"):
            lines.append(f"Amazon Search:  {info.amazon_urls['search']}")
    if info.description:
        lines.append("")
        lines.append("Description:")
        lines.append(info.description)
    return "\n".join(lines)

