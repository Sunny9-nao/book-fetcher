from __future__ import annotations

"""コマンドライン（CLI）

非エンジニア向けの要点:
- 引数（オプション）を受け取り、バッチ/単体処理を切り替えます。
- 標準プリセット（--preset standard）で一発実行が可能です。
"""

import argparse
import json
import os
import sys
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from .covers import download_cover
from .models import BookInfo
from .openlibrary import search_openlibrary
from .openlibrary import choose_candidate
from .render import render_text
from .service import build_cover_filename, fetch_book_info


def build_parser() -> argparse.ArgumentParser:
    """CLIの引数（オプション）定義を行う。"""
    parser = argparse.ArgumentParser(
        prog="book_fetcher",
        description="Fetch book info, cover image URLs, and summary by title using Open Library (and optionally Google Books).",
    )
    parser.add_argument("title", nargs="?", help="Book title to search (exact or partial)")
    parser.add_argument("--author", help="Filter by author name", default=None)
    parser.add_argument("--year", type=int, help="Filter by first publish year", default=None)
    parser.add_argument("--show-candidates", type=int, metavar="N", default=0, help="Show top N candidates and exit")
    parser.add_argument("--pick-index", type=int, default=0, help="Pick candidate index (default 0)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--download-cover", metavar="PATH", help="Download the cover image to PATH (uses --cover-size)")
    parser.add_argument("--cover-size", choices=["s", "m", "l"], default="l", help="Cover image size when downloading")
    parser.add_argument("--input-file", metavar="PATH", help="Read titles from file (one per line; # and blank lines ignored)")
    parser.add_argument("--use-google", action="store_true", help="Augment results with Google Books when available")
    parser.add_argument("--google-api-key", default=os.environ.get("GOOGLE_BOOKS_API_KEY"), help="Google Books API key (optional; can use env GOOGLE_BOOKS_API_KEY)")
    parser.add_argument("--amazon-domain", choices=["co.jp","com","co.uk","de","fr","it","es","ca","com.au"], default="co.jp", help="Amazon domain for links")
    parser.add_argument("--output-file", metavar="PATH", help="Write results to PATH instead of stdout")
    parser.add_argument("--covers-dir", metavar="DIR", help="Download cover images for each entry to DIR (batch mode)")
    parser.add_argument("--preset", choices=["standard"], help="Use preset options; 'standard' equals: --use-google --format json --input-file titles.txt --output-file results.json --covers-dir covers --cover-size l")
    return parser


def apply_standard_preset(args: argparse.Namespace) -> None:
    """標準プリセットを適用する。

    - titles.txt があれば入力に採用
    - JSON出力とカバー保存（L）を既定に
    """
    if not args.input_file:
        default_in = "titles.txt"
        if os.path.exists(default_in):
            args.input_file = default_in
    args.use_google = True
    if args.format == "text":
        args.format = "json"
    if not args.output_file:
        args.output_file = "results.json"
    if not args.covers_dir:
        args.covers_dir = "covers"
    args.cover_size = args.cover_size or "l"


def _load_titles(path: str) -> List[str]:
    """入力ファイル（1行1タイトル）を読み込み、空行と#行を除く。"""
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]


def main(argv: Optional[List[str]] = None) -> int:
    """CLIのメイン処理。

    - 入力のバリデーション
    - バッチ処理（--input-file）または単体処理
    - 結果のファイル保存／画面出力
    - カバー画像の保存
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.preset == "standard":
        apply_standard_preset(args)

    no_cli_args = argv is None and len(sys.argv) <= 1
    if no_cli_args and os.path.exists("titles.txt"):
        apply_standard_preset(args)

    if not args.title and not args.input_file:
        parser.error("Provide a title or --input-file (or use --preset standard)")

    if args.input_file and args.show_candidates:
        print("--show-candidates is not supported with --input-file.", file=sys.stderr)
        return 2
    if args.input_file and args.download_cover:
        print("--download-cover is not supported with --input-file.", file=sys.stderr)
        return 2
    if args.covers_dir and not args.input_file:
        print("--covers-dir is only supported with --input-file (batch mode).", file=sys.stderr)
        return 2

    if args.input_file:
        try:
            titles = _load_titles(args.input_file)
        except OSError as oe:
            print(f"Failed to read input file: {oe}", file=sys.stderr)
            return 2
        if not titles:
            print("No titles found in input file.")
            return 1

        results: List[Dict[str, Any]] = []
        text_blocks: List[str] = []
        any_success = False
        covers_saved = 0

        covers_dir = None
        if args.covers_dir:
            covers_dir = os.path.abspath(args.covers_dir)
            try:
                os.makedirs(covers_dir, exist_ok=True)
            except OSError as oe:
                print(f"Failed to create covers directory: {oe}", file=sys.stderr)
                return 2

        for t in titles:
            try:
                info = fetch_book_info(
                    t,
                    author=args.author,
                    year=args.year,
                    pick_index=args.pick_index,
                    use_google=args.use_google,
                    google_api_key=args.google_api_key,
                    amazon_domain=args.amazon_domain,
                )
            except Exception as e:
                print(f"Error for '{t}': {e}", file=sys.stderr)
                continue
            if not info:
                print(f"No book found: {t}")
                continue
            any_success = True

            if args.format == "json":
                results.append(asdict(info))
            else:
                if not args.output_file:
                    print(render_text(info))
                    print("-" * 40)
                text_blocks.append(render_text(info) + "\n" + ("-" * 40) + "\n")

            if covers_dir:
                url = info.cover_urls.get(args.cover_size)
                if url:
                    try:
                        name = build_cover_filename(info, args.cover_size)
                        download_cover(url, os.path.join(covers_dir, name))
                        covers_saved += 1
                    except Exception:
                        pass

        if args.output_file:
            out_path = os.path.abspath(args.output_file)
            try:
                os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
                with open(out_path, "w", encoding="utf-8") as f:
                    if args.format == "json":
                        json.dump(results, f, ensure_ascii=False, indent=2)
                    else:
                        f.write("".join(text_blocks))
                print(f"Saved results to: {out_path}")
            except OSError as oe:
                print(f"Failed to write output file: {oe}", file=sys.stderr)
                return 2
        else:
            if args.format == "json":
                print(json.dumps(results, ensure_ascii=False, indent=2))

        if covers_dir:
            print(f"Saved cover images: {covers_saved} file(s) to {covers_dir}")
        return 0 if any_success else 1

    # Single-title mode
    try:
        candidates = search_openlibrary(args.title, author=args.author, year=args.year, limit=max(5, args.show_candidates or (args.pick_index + 1)))
    except Exception as e:
        print(f"Search error: {e}", file=sys.stderr)
        return 2

    if args.show_candidates:
        if not candidates:
            print("No candidates found.")
            return 1
        print(f"Top {min(args.show_candidates, len(candidates))} candidates:")
        for c in candidates[: args.show_candidates]:
            parts = [f"[{c.index}] {c.title}"]
            if c.author_names:
                parts.append(f"by {', '.join(c.author_names)}")
            if c.first_publish_year:
                parts.append(f"({c.first_publish_year})")
            print(" ".join(parts))
        return 0

    try:
        info = fetch_book_info(
            args.title,
            author=args.author,
            year=args.year,
            pick_index=args.pick_index,
            use_google=args.use_google,
            google_api_key=args.google_api_key,
            amazon_domain=args.amazon_domain,
        )
    except Exception as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return 2

    if not info:
        print("No book found.")
        return 1

    if args.output_file:
        out_path = os.path.abspath(args.output_file)
        try:
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                if args.format == "json":
                    json.dump(asdict(info), f, ensure_ascii=False, indent=2)
                else:
                    f.write(render_text(info) + "\n")
            print(f"Saved result to: {out_path}")
        except OSError as oe:
            print(f"Failed to write output file: {oe}", file=sys.stderr)
            return 2
    else:
        if args.format == "json":
            print(json.dumps(asdict(info), ensure_ascii=False, indent=2))
        else:
            print(render_text(info))

    if args.download_cover:
        url = info.cover_urls.get(args.cover_size)
        if not url:
            print("No cover image available to download.", file=sys.stderr)
        else:
            try:
                download_cover(url, args.download_cover)
                print(f"Saved cover image: {os.path.abspath(args.download_cover)}")
            except Exception as e:
                print(f"Failed to download cover: {e}", file=sys.stderr)

    return 0
