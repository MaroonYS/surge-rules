#!/usr/bin/env python3
"""Check HTTP availability of remote rule resources in surge-main.conf."""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
URL_RE = re.compile(r"https://[^,\s]+")


def collect_urls(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return sorted(set(URL_RE.findall(text)))


def probe(url: str, timeout: float) -> tuple[str, int | None, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "surge-rules-upstream-check/1.0",
            "Range": "bytes=0-0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read(1)
            return url, response.status, "ok"
    except urllib.error.HTTPError as exc:
        return url, exc.code, str(exc.reason)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return url, None, str(exc)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--main",
        type=Path,
        default=REPOSITORY_ROOT / "surge-main.conf",
        help="Surge file containing remote rule URLs",
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--workers", type=int, default=8)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.timeout <= 0 or args.workers < 1:
        print("timeout and workers must be positive", file=sys.stderr)
        return 2
    try:
        urls = collect_urls(args.main)
    except (OSError, UnicodeError) as exc:
        print(f"cannot read {args.main}: {exc}", file=sys.stderr)
        return 2

    failures = 0
    results: list[tuple[str, int | None, str]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        pending = {executor.submit(probe, url, args.timeout): url for url in urls}
        for future in as_completed(pending):
            results.append(future.result())

    for url, status, message in sorted(results):
        passed = status is not None and 200 <= status < 400
        failures += not passed
        label = str(status) if status is not None else "ERR"
        print(f"{'PASS' if passed else 'FAIL'} {label:>3} {url}")
        if not passed:
            print(f"         {message}")
    print(f"Checked {len(urls)} URLs: {len(urls) - failures} passed, {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
