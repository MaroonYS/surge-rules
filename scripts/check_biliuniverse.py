#!/usr/bin/env python3
"""Verify that the latest BiliUniverse Global module stays disjoint from Bili CDN routing."""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODULE_URL = (
    "https://github.com/BiliUniverse/Global/releases/latest/download/"
    "BiliBili.Global.sgmodule"
)
VERSION_RE = re.compile(r"^#!version\s*=\s*(.+)$", re.MULTILINE)
ARGUMENTS_RE = re.compile(r"^#!arguments\s*=\s*(.+)$", re.MULTILINE)


@dataclass(frozen=True)
class CompatibilityResult:
    version: str
    direct_suffixes: tuple[str, ...]
    mitm_hosts: tuple[str, ...]
    problems: tuple[str, ...]


def section(text: str, name: str) -> str:
    lines: list[str] = []
    inside = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line == f"[{name}]":
            inside = True
            continue
        if inside and line.startswith("[") and line.endswith("]"):
            break
        if inside:
            lines.append(raw_line)
    return "\n".join(lines)


def parse_direct_suffixes(path: Path) -> tuple[str, ...]:
    suffixes = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if not line.startswith("."):
            raise ValueError(f"expected suffix entry, got {line!r}")
        suffixes.append(line[1:].lower())
    return tuple(sorted(suffixes))


def parse_mitm_hosts(mitm_text: str) -> tuple[str, ...]:
    hosts: set[str] = set()
    for raw_line in mitm_text.splitlines():
        key, separator, value = raw_line.partition("=")
        if not separator or key.strip().lower() != "hostname":
            continue
        for item in value.split(","):
            host = item.strip().lower()
            if host and host != "%append%":
                hosts.add(host.removeprefix("%append% ").lstrip("*."))
    return tuple(sorted(hosts))


def suffix_matches(host: str, suffix: str) -> bool:
    return host == suffix or host.endswith(f".{suffix}")


def validate_module(
    module_text: str,
    direct_suffixes: Sequence[str],
) -> CompatibilityResult:
    problems: list[str] = []
    script_text = section(module_text, "Script")
    mitm_text = section(module_text, "MITM")
    mitm_hosts = parse_mitm_hosts(mitm_text)

    version_match = VERSION_RE.search(module_text)
    version = version_match.group(1).strip() if version_match else "unknown"
    arguments_match = ARGUMENTS_RE.search(module_text)
    arguments = arguments_match.group(1) if arguments_match else ""

    if not script_text:
        problems.append("official module has no [Script] section")
    if not mitm_hosts:
        problems.append("official module has no MITM host list")
    if 'ForceHost:"1"' not in arguments:
        problems.append("official module no longer defaults ForceHost to HTTP domains")
    if "ability=http-client-policy" not in script_text:
        problems.append("official module no longer exposes dynamic HTTP client policy")
    if "bilivideo" in script_text.lower():
        problems.append("official module now intercepts bilivideo traffic")

    for host in mitm_hosts:
        for suffix in direct_suffixes:
            if suffix_matches(host, suffix):
                problems.append(
                    f"DIRECT suffix {suffix} overlaps module MITM host {host}"
                )

    return CompatibilityResult(
        version=version,
        direct_suffixes=tuple(sorted(direct_suffixes)),
        mitm_hosts=mitm_hosts,
        problems=tuple(problems),
    )


def download(url: str, timeout: float) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "surge-rules-biliuniverse-check/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read()
    return payload.decode("utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_MODULE_URL)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument(
        "--domain-set",
        type=Path,
        default=REPOSITORY_ROOT / "bilibili-direct.conf",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        suffixes = parse_direct_suffixes(args.domain_set)
        module_text = download(args.url, args.timeout)
        result = validate_module(module_text, suffixes)
    except (OSError, UnicodeError, ValueError, urllib.error.URLError) as error:
        print(f"BiliUniverse compatibility check failed: {error}", file=sys.stderr)
        return 1

    if result.problems:
        for problem in result.problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1

    print(
        "BiliUniverse Global compatibility PASS: "
        f"version {result.version}; "
        f"{len(result.direct_suffixes)} DIRECT suffixes; "
        f"{len(result.mitm_hosts)} disjoint MITM hosts; "
        "ForceHost=1; dynamic policy enabled"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
