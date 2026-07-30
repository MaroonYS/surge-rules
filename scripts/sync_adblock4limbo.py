#!/usr/bin/env python3
"""Build a precise DOMAIN-SET supplement from Adblock4limbo."""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import validate


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = (
    "https://raw.githubusercontent.com/limbopro/Adblock4limbo/"
    "main/Adblock4limbo_surge.list"
)
BASELINE_URL = "https://ruleset.skk.moe/List/domainset/reject.conf"
OUTPUT_PATH = REPOSITORY_ROOT / "adblock4limbo-supplement.conf"
MAX_DOWNLOAD_BYTES = 16 * 1024 * 1024
SKK_SENTINEL = "7h1s_rul35et_i5_mad3_by_5ukk4w-ruleset.skk.moe"


@dataclass(frozen=True, order=True)
class DomainRule:
    domain: str
    suffix: bool

    @property
    def serialized(self) -> str:
        return f".{self.domain}" if self.suffix else self.domain


@dataclass(frozen=True)
class BuildStats:
    upstream_rules: int
    keyword_rules: int
    invalid_rules: int
    duplicate_rules: int
    baseline_covered: int
    internally_redundant: int


def fetch_text(url: str, timeout: float) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "surge-rules-adblock-sync/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read(MAX_DOWNLOAD_BYTES + 1)
    if len(payload) > MAX_DOWNLOAD_BYTES:
        raise ValueError(f"resource exceeds {MAX_DOWNLOAD_BYTES} bytes: {url}")
    return payload.decode("utf-8")


def read_text(path: Path | None, url: str, timeout: float) -> str:
    if path is not None:
        return path.read_text(encoding="utf-8")
    return fetch_text(url, timeout)


def parse_adblock(text: str) -> tuple[set[DomainRule], dict[str, int]]:
    entries: set[DomainRule] = set()
    stats = {
        "upstream_rules": 0,
        "keyword_rules": 0,
        "invalid_rules": 0,
        "duplicate_rules": 0,
    }

    for line_number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        stats["upstream_rules"] += 1
        fields = [field.strip() for field in line.split(",")]
        if len(fields) != 3 or fields[2].casefold() != "reject":
            raise ValueError(
                f"unexpected Adblock4limbo rule at line {line_number}: {raw_line}"
            )

        rule_type = fields[0].upper()
        if rule_type == "DOMAIN-KEYWORD":
            stats["keyword_rules"] += 1
            continue
        if rule_type not in {"DOMAIN", "DOMAIN-SUFFIX"}:
            raise ValueError(
                f"unsupported Adblock4limbo rule at line {line_number}: {rule_type}"
            )

        domain = fields[1].lower()
        serialized = f".{domain}" if rule_type == "DOMAIN-SUFFIX" else domain
        if validate.validate_domain(serialized) is not None:
            stats["invalid_rules"] += 1
            continue

        entry = DomainRule(domain=domain, suffix=rule_type == "DOMAIN-SUFFIX")
        if entry in entries:
            stats["duplicate_rules"] += 1
            continue
        entries.add(entry)

    if not entries:
        raise ValueError("Adblock4limbo produced no usable domain rules")
    return entries, stats


def parse_domain_set(text: str) -> tuple[set[str], set[str]]:
    exact: set[str] = set()
    suffix: set[str] = set()
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line == SKK_SENTINEL:
            continue
        domain = line[1:] if line.startswith(".") else line
        if (
            not domain
            or domain != domain.lower()
            or domain.startswith(".")
            or domain.endswith(".")
            or ".." in domain
            or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-_."
                   for character in domain)
        ):
            raise ValueError(
                f"invalid baseline DOMAIN-SET line {line_number}: {raw_line}"
            )
        if line.startswith("."):
            suffix.add(domain)
        else:
            exact.add(domain)
    if not exact and not suffix:
        raise ValueError("baseline DOMAIN-SET has no usable entries")
    return exact, suffix


def ancestors(domain: str) -> list[str]:
    labels = domain.split(".")
    return [".".join(labels[index:]) for index in range(len(labels) - 1)]


def covered_by_baseline(
    entry: DomainRule,
    baseline_exact: set[str],
    baseline_suffix: set[str],
) -> bool:
    if not entry.suffix and entry.domain in baseline_exact:
        return True
    return any(ancestor in baseline_suffix for ancestor in ancestors(entry.domain))


def minimize(entries: set[DomainRule]) -> tuple[list[DomainRule], int]:
    suffixes = {entry.domain for entry in entries if entry.suffix}
    kept: list[DomainRule] = []
    removed = 0
    for entry in sorted(entries):
        domain_ancestors = ancestors(entry.domain)
        if not entry.suffix and entry.domain in suffixes:
            removed += 1
            continue
        if any(
            ancestor != entry.domain and ancestor in suffixes
            for ancestor in domain_ancestors
        ):
            removed += 1
            continue
        kept.append(entry)
    return kept, removed


def build(
    source_text: str,
    baseline_text: str,
) -> tuple[str, BuildStats]:
    source_entries, source_stats = parse_adblock(source_text)
    baseline_exact, baseline_suffix = parse_domain_set(baseline_text)

    remaining: set[DomainRule] = set()
    baseline_covered = 0
    for entry in source_entries:
        if covered_by_baseline(entry, baseline_exact, baseline_suffix):
            baseline_covered += 1
        else:
            remaining.add(entry)

    minimized, internally_redundant = minimize(remaining)
    stats = BuildStats(
        upstream_rules=source_stats["upstream_rules"],
        keyword_rules=source_stats["keyword_rules"],
        invalid_rules=source_stats["invalid_rules"],
        duplicate_rules=source_stats["duplicate_rules"],
        baseline_covered=baseline_covered,
        internally_redundant=internally_redundant,
    )
    header = [
        "# AUTO-GENERATED by scripts/sync_adblock4limbo.py",
        f"# Source: {SOURCE_URL}",
        f"# Source SHA-256: {hashlib.sha256(source_text.encode('utf-8')).hexdigest()}",
        f"# Baseline: {BASELINE_URL}",
        (
            "# Baseline SHA-256: "
            f"{hashlib.sha256(baseline_text.encode('utf-8')).hexdigest()}"
        ),
        "# Upstream license: MIT, Copyright (c) 2022 毒奶博主",
        "# License notice: THIRD_PARTY_NOTICES.md",
        (
            "# Only DOMAIN and DOMAIN-SUFFIX records are retained; broad "
            "DOMAIN-KEYWORD records are intentionally excluded."
        ),
        (
            "# Duplicate, invalid, internally redundant and baseline-covered "
            "records are removed."
        ),
        "",
    ]
    payload = header + [entry.serialized for entry in minimized]
    return "\n".join(payload) + "\n", stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--source-file", type=Path)
    parser.add_argument("--baseline-file", type=Path)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--timeout", type=float, default=20.0)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.timeout <= 0:
        print("timeout must be positive", file=sys.stderr)
        return 2
    try:
        source_text = read_text(args.source_file, SOURCE_URL, args.timeout)
        baseline_text = read_text(args.baseline_file, BASELINE_URL, args.timeout)
        rendered, stats = build(source_text, baseline_text)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"cannot build Adblock4limbo supplement: {exc}", file=sys.stderr)
        return 1

    if args.write:
        args.output.write_text(rendered, encoding="utf-8")
        action = "Wrote"
    else:
        try:
            current = args.output.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"cannot read {args.output}: {exc}", file=sys.stderr)
            return 1
        if current != rendered:
            print(
                f"{args.output} is stale; run scripts/sync_adblock4limbo.py --write",
                file=sys.stderr,
            )
            return 1
        action = "Verified"

    count = sum(
        bool(line) and not line.startswith("#") for line in rendered.splitlines()
    )
    print(
        f"{action} {args.output} ({count} entries; "
        f"{stats.keyword_rules} keywords excluded, "
        f"{stats.duplicate_rules} duplicates removed, "
        f"{stats.invalid_rules} invalid removed, "
        f"{stats.baseline_covered} baseline-covered removed, "
        f"{stats.internally_redundant} internally redundant removed)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
