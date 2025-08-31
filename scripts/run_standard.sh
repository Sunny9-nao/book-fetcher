#!/usr/bin/env bash
set -euo pipefail

python3 -m book_fetcher --preset standard "$@"

