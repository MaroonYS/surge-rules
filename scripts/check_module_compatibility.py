#!/usr/bin/env python3
"""Validate the retained-module MITM contract and an optional effective profile."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPOSITORY_ROOT / "module-compatibility.json"
DOCUMENTATION_MARKER_START = "<!-- module-compatibility:positive-hosts:start -->"
DOCUMENTATION_MARKER_END = "<!-- module-compatibility:positive-hosts:end -->"
REQUIRED_MODULE_IDS = {
    "dualsubs-apple-tv",
    "iringo-location-service",
    "iringo-maps",
    "iringo-news",
    "iringo-tv",
    "iringo-weatherkit",
    "wloc",
}
EXPECTED_CONDITIONAL_DISABLE = {
    "id": "wloc-ios27-client-pinning",
    "requirement": (
        "DEVICE_MODEL BEGINSWITH 'iPhone' AND "
        "SYSTEM_VERSION CONTAINS 'Version 27.'"
    ),
    "hosts": ["gs-loc.apple.com", "gs-loc-cn.apple.com"],
}


def load_manifest(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read manifest {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("module compatibility manifest must be a JSON object")
    return data


def string_list(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty array")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{label} must contain non-empty strings")
    values = [item.strip().lower() for item in value]
    if len(values) != len(set(values)):
        raise ValueError(f"{label} contains duplicates")
    return values


def manifest_contract(data: dict[str, object]) -> tuple[list[str], list[str]]:
    if data.get("schema_version") != 2:
        raise ValueError("unsupported module compatibility schema_version")
    order = data.get("required_mitm_order")
    if not isinstance(order, dict):
        raise ValueError("required_mitm_order must be an object")
    positives = string_list(order.get("positive_hosts"), "positive_hosts")
    negatives = string_list(order.get("negative_hosts"), "negative_hosts")
    if len(positives) != 24:
        raise ValueError(f"positive_hosts must contain exactly 24 entries, got {len(positives)}")
    if any(host.startswith("-") for host in positives):
        raise ValueError("positive_hosts cannot contain exclusions")
    if any(not host.startswith("-") for host in negatives):
        raise ValueError("negative_hosts must contain Surge exclusions")
    if len(negatives) != 151:
        raise ValueError(
            f"negative_hosts must contain exactly 151 entries, got {len(negatives)}"
        )

    modules = data.get("modules")
    if not isinstance(modules, list) or not modules:
        raise ValueError("modules must be a non-empty array")
    module_ids: set[str] = set()
    covered_hosts: set[str] = set()
    for index, module in enumerate(modules):
        if not isinstance(module, dict):
            raise ValueError(f"modules[{index}] must be an object")
        module_id = module.get("id")
        if not isinstance(module_id, str) or not module_id:
            raise ValueError(f"modules[{index}].id must be a non-empty string")
        if module_id in module_ids:
            raise ValueError(f"duplicate module id: {module_id}")
        module_ids.add(module_id)
        hosts = string_list(
            module.get("required_mitm_hosts"),
            f"modules[{index}].required_mitm_hosts",
        )
        unknown = set(hosts) - set(positives)
        if unknown:
            raise ValueError(
                f"module {module_id} references hosts outside positive_hosts: "
                + ", ".join(sorted(unknown))
            )
        covered_hosts.update(hosts)
    if module_ids != REQUIRED_MODULE_IDS:
        missing = sorted(REQUIRED_MODULE_IDS - module_ids)
        extra = sorted(module_ids - REQUIRED_MODULE_IDS)
        raise ValueError(f"module ids drifted; missing={missing}, extra={extra}")
    if covered_hosts != set(positives):
        missing = sorted(set(positives) - covered_hosts)
        raise ValueError("positive hosts without a module owner: " + ", ".join(missing))

    conditional_disables = data.get("conditional_mitm_disables")
    if not isinstance(conditional_disables, list) or len(conditional_disables) != 1:
        raise ValueError("conditional_mitm_disables must contain exactly one entry")
    conditional = conditional_disables[0]
    if conditional != EXPECTED_CONDITIONAL_DISABLE:
        raise ValueError("WLOC iOS 27 conditional MITM disable contract drifted")
    if not set(conditional["hosts"]).issubset(positives):
        raise ValueError("conditional MITM disabled hosts must be positive hosts")
    return positives, negatives


def documented_hosts(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read documentation {path}: {exc}") from exc
    start = text.find(DOCUMENTATION_MARKER_START)
    end = text.find(DOCUMENTATION_MARKER_END)
    if start < 0 or end < 0 or end <= start:
        raise ValueError("module documentation markers are missing or out of order")
    body = text[start + len(DOCUMENTATION_MARKER_START) : end]
    fences = body.split("```")
    if len(fences) != 3:
        raise ValueError("module documentation marker must contain one fenced host list")
    lines = [line.strip().lower() for line in fences[1].splitlines() if line.strip()]
    if lines and lines[0] in {"text", "txt"}:
        lines = lines[1:]
    return lines


def mitm_host_tokens(profile_text: str) -> list[str]:
    section = ""
    tokens: list[str] = []
    for raw_line in profile_text.splitlines():
        line = raw_line.strip()
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip().casefold()
            continue
        if section != "mitm" or not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if separator and key.strip().casefold() == "hostname":
            tokens.extend(
                item.strip().lower()
                for item in value.split(",")
                if item.strip() and item.strip().casefold() != "%append%"
            )
    return tokens


def mitm_option(profile_text: str, option: str) -> str | None:
    section = ""
    expected = option.casefold()
    for raw_line in profile_text.splitlines():
        line = raw_line.strip()
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip().casefold()
            continue
        if section != "mitm" or not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if separator and key.strip().casefold() == expected:
            return value.strip()
    return None


def conditional_disable_line(conditional: dict[str, object]) -> str:
    requirement = conditional["requirement"]
    hosts = conditional["hosts"]
    return (
        f'#!REQUIREMENT "{requirement}" hostname-disabled = '
        + ", ".join(hosts)
    )


def validate_base_profile(
    profile_text: str,
    positives: Sequence[str],
    negatives: Sequence[str],
    conditional: dict[str, object],
) -> list[str]:
    problems = validate_profile_order(profile_text, positives, negatives)
    tokens = mitm_host_tokens(profile_text)
    if tokens != list(positives) + list(negatives):
        problems.append("base MITM hostname list differs from the complete manifest")
    if tokens[: len(positives)] != list(positives):
        problems.append("base MITM positive host prefix differs from the manifest")
    unexpected_positives = [
        token for token in tokens[len(positives) :] if not token.startswith("-")
    ]
    if unexpected_positives:
        problems.append(
            "unexpected positive MITM hosts after the protected prefix: "
            + ", ".join(unexpected_positives)
        )
    if len(tokens) != len(set(tokens)):
        problems.append("base MITM hostname list contains duplicate tokens")
    if "-<ip-address>" not in tokens:
        problems.append("base MITM hostname list must exclude raw IP hosts")
    if mitm_option(profile_text, "h2") != "true":
        problems.append("base MITM must enable h2")
    skip_verify = mitm_option(profile_text, "skip-server-cert-verify")
    if skip_verify not in {None, "false"}:
        problems.append("base MITM must verify upstream server certificates")
    expected_line = conditional_disable_line(conditional)
    if expected_line not in {line.strip() for line in profile_text.splitlines()}:
        problems.append("base profile is missing the exact iPhone iOS 27 WLOC disable")
    return problems


def validate_profile_order(
    profile_text: str,
    positives: Sequence[str],
    negatives: Sequence[str],
) -> list[str]:
    tokens = mitm_host_tokens(profile_text)
    problems: list[str] = []
    positions: dict[str, int] = {}
    for index, token in enumerate(tokens):
        positions.setdefault(token, index)
    present_negatives = [host for host in negatives if host in positions]
    for negative in negatives:
        if negative not in positions:
            problems.append(f"missing protected MITM exclusion: {negative}")
    for host in positives:
        if host not in positions:
            problems.append(f"missing positive MITM host: {host}")
            continue
        for negative in present_negatives:
            if positions[host] > positions[negative]:
                problems.append(f"{host} appears after protected exclusion {negative}")
    return problems


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--profile",
        type=Path,
        help="optional Surge modified/effective profile to verify",
    )
    parser.add_argument(
        "--base-profile",
        action="append",
        type=Path,
        default=[],
        help="optional unmodified base profile to verify (repeatable)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = load_manifest(args.manifest)
        positives, negatives = manifest_contract(data)
        documentation = data.get("documentation")
        if not isinstance(documentation, str) or not documentation:
            raise ValueError("documentation must be a repository-relative path")
        documentation_path = (args.manifest.parent / documentation).resolve()
        if args.manifest.parent.resolve() not in documentation_path.parents:
            raise ValueError("documentation path escapes the repository")
        documented = documented_hosts(documentation_path)
        if documented != positives:
            raise ValueError("documented MITM host list differs from the manifest")
        if args.profile is not None:
            profile_text = args.profile.read_text(encoding="utf-8")
            problems = validate_profile_order(profile_text, positives, negatives)
            if problems:
                for problem in problems:
                    print(f"ERROR: {problem}", file=sys.stderr)
                return 1
        conditional = data["conditional_mitm_disables"][0]
        for profile_path in args.base_profile:
            profile_text = profile_path.read_text(encoding="utf-8")
            problems = validate_base_profile(
                profile_text,
                positives,
                negatives,
                conditional,
            )
            if problems:
                for problem in problems:
                    print(f"ERROR ({profile_path}): {problem}", file=sys.stderr)
                return 1
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"module compatibility check failed: {exc}", file=sys.stderr)
        return 1

    checked_profiles = int(args.profile is not None) + len(args.base_profile)
    suffix = f"; {checked_profiles} profile(s) checked" if checked_profiles else ""
    print(
        "Module compatibility PASS: "
        f"{len(positives)} ordered MITM hosts; "
        f"{len(negatives)} protected exclusions; "
        f"{len(REQUIRED_MODULE_IDS)} retained module roles{suffix}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
