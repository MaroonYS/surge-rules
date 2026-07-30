#!/usr/bin/env python3
"""Verify that every policy referenced by a Rule exists in a Surge profile."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BUILT_IN_POLICIES = {
    "DIRECT",
    "REJECT",
    "REJECT-DROP",
    "REJECT-NO-DROP",
    "REJECT-TINYGIF",
}
POLICY_FIELD_BY_RULE = {
    "DOMAIN": 2,
    "DOMAIN-KEYWORD": 2,
    "DOMAIN-SET": 2,
    "DOMAIN-SUFFIX": 2,
    "DOMAIN-WILDCARD": 2,
    "FINAL": 1,
    "IP-ASN": 2,
    "IP-CIDR": 2,
    "IP-CIDR6": 2,
    "PROTOCOL": 2,
    "RULE-SET": 2,
}


def section_lines(text: str, section_name: str) -> list[tuple[int, str]]:
    active = False
    output: list[tuple[int, str]] = []
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.strip()
        if line.startswith("[") and line.endswith("]"):
            active = line == f"[{section_name}]"
            continue
        if active:
            output.append((line_number, raw_line))
    return output


def profile_policy_types(text: str) -> dict[str, str]:
    policies = {name: "built-in" for name in BUILT_IN_POLICIES}
    for section in ("Proxy", "Proxy Group"):
        for _, raw_line in section_lines(text, section):
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            name = name.strip().strip('"')
            if name:
                if section == "Proxy":
                    policy_type = "proxy"
                else:
                    policy_type = value.split(",", 1)[0].strip().casefold()
                policies[name] = policy_type
    return policies


def supplemental_group_types(text: str) -> dict[str, str]:
    policies: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if (
            not line
            or line.startswith("#")
            or (line.startswith("[") and line.endswith("]"))
            or "=" not in line
        ):
            continue
        name, value = line.split("=", 1)
        name = name.strip().strip('"')
        if name:
            policies[name] = value.split(",", 1)[0].strip().casefold()
    return policies


def referenced_policies(text: str) -> dict[str, list[int]]:
    references: dict[str, list[int]] = {}
    for line_number, raw_line in section_lines(text, "Rule"):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        fields = [field.strip().strip('"') for field in line.split(",")]
        policy_index = POLICY_FIELD_BY_RULE.get(fields[0].upper())
        if policy_index is None or len(fields) <= policy_index:
            continue
        policy = fields[policy_index]
        if policy:
            references.setdefault(policy, []).append(line_number)
    return references


def check(
    profile_text: str,
    rules_text: str,
    stable_policies: Sequence[str] = (),
    supplemental_texts: Sequence[str] = (),
) -> tuple[list[str], list[str], int]:
    defined = profile_policy_types(profile_text)
    for supplemental_text in supplemental_texts:
        defined.update(supplemental_group_types(supplemental_text))
    references = referenced_policies(rules_text)
    required = set(references) | set(stable_policies)
    missing = sorted(required - set(defined))
    unstable = sorted(
        policy
        for policy in stable_policies
        if policy in defined
        and defined[policy] not in {"proxy", "select"}
    )
    return missing, unstable, len(references)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument(
        "--rules",
        type=Path,
        default=REPOSITORY_ROOT / "surge-main.conf",
    )
    parser.add_argument(
        "--require-stable",
        nargs="*",
        default=(),
        metavar="POLICY",
        help="policies that must be a fixed proxy or a manual select group",
    )
    parser.add_argument(
        "--supplement",
        action="append",
        default=[],
        type=Path,
        help="additional policy-group snippet; may be repeated",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        profile_text = args.profile.read_text(encoding="utf-8")
        rules_text = args.rules.read_text(encoding="utf-8")
        supplemental_texts = [
            path.read_text(encoding="utf-8") for path in args.supplement
        ]
    except (OSError, UnicodeError) as exc:
        print(f"cannot read Surge configuration: {exc}", file=sys.stderr)
        return 2

    missing, unstable, reference_count = check(
        profile_text,
        rules_text,
        args.require_stable,
        supplemental_texts,
    )
    if missing:
        print("Missing Surge policies: " + ", ".join(missing), file=sys.stderr)
        return 1
    if unstable:
        print(
            "Non-stable Surge policies: " + ", ".join(unstable),
            file=sys.stderr,
        )
        return 1
    source_label = "profile and supplements" if args.supplement else "profile"
    print(f"All {reference_count} referenced policies exist in the supplied {source_label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
