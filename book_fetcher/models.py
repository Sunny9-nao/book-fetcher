from __future__ import annotations

"""データモデル定義

このファイルでは、やり取りする「本の情報」の入れ物（型）を定義します。
非エンジニアの方向けの要点:
- BookCandidate: 検索直後の「候補の本」。確定前の軽い情報。
- BookInfo: 1冊の本としてまとめた最終情報（画面表示・保存に使う）。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BookCandidate:
    """検索結果の候補1件分。

    - index: 候補の並び順（0から）
    - title: タイトル
    - author_names: 著者名の一覧
    - first_publish_year: 初出年（分かれば）
    - work_key: Open Library 側の「作品」キー（/works/〜）
    - edition_keys: 版（エディション）のキー一覧
    - cover_id: カバー画像のID（分かれば）
    - isbns: ISBN の候補一覧
    """

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
    """最終的に出力・保存するための、本1冊のまとまった情報。

    - title: タイトル
    - authors: 著者名一覧
    - first_publish_year: 初出年
    - publishers: 出版社一覧
    - publish_date: 出版日（文字列）
    - isbns: ISBN の一覧
    - openlibrary_work_key: Open Library の作品キー
    - openlibrary_edition_key: Open Library の版キー
    - openlibrary_url: Open Library 上のページURL
    - description: 概要（説明文）
    - subjects: 主題（カテゴリ）
    - cover_urls: カバー画像のURL（s/m/l）
    - amazon_urls: Amazon の商品/検索リンク
    """

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
