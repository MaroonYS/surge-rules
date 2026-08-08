#!/usr/bin/env python3
"""Download and validate every remote rule resource in surge-main.conf."""

from __future__ import annotations

import argparse
import http.client
import ipaddress
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
from urllib.parse import urlsplit

import validate as repository_validator


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKK_SENTINEL = "7h1s_rul35et_i5_mad3_by_5ukk4w-ruleset.skk.moe"
SKK_SENTINEL_ALIASES = (
    "7h1s_rul35et_i5_mad3_by_5ukk4w",
    "this_rule_set_is_made_by_sukkaw",
)
POLICY_TOKENS = {
    "direct",
    "proxy",
    "reject",
    "reject-drop",
    "reject-no-drop",
    "reject-tinygif",
}
DOMAIN_RULE_TYPES = {
    "DOMAIN",
    "DOMAIN-KEYWORD",
    "DOMAIN-SUFFIX",
    "DOMAIN-WILDCARD",
}
IP_RULE_TYPES = {"GEOIP", "IP-ASN", "IP-CIDR", "IP-CIDR6"}
ALLOWED_CONTENT_TYPES = {
    "",
    "application/octet-stream",
    "binary/octet-stream",
    "text/plain",
}


@dataclass(frozen=True, order=True)
class Resource:
    url: str
    rule_type: str
    line: int


@dataclass(frozen=True)
class Result:
    resource: Resource
    status: int | None
    source: str
    effective_rules: int
    message: str
    final_url: str = ""

    @property
    def passed(self) -> bool:
        return self.status is not None and 200 <= self.status < 300 and not self.message


def collect_resources_text(text: str) -> list[Resource]:
    resources: dict[tuple[str, str], Resource] = {}
    for line_number, raw_line in enumerate(
        text.splitlines(),
        1,
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        fields = [field.strip() for field in line.split(",")]
        if (
            len(fields) >= 2
            and fields[0] in {"DOMAIN-SET", "RULE-SET"}
            and fields[1].startswith("https://")
        ):
            resource = Resource(fields[1], fields[0], line_number)
            key = (resource.url, resource.rule_type)
            resources.setdefault(key, resource)
    return sorted(resources.values())


def collect_resources(path: Path) -> list[Resource]:
    return collect_resources_text(path.read_text(encoding="utf-8"))


def local_raw_base(root: Path) -> str | None:
    try:
        manifest = json.loads(
            (root / "rules-manifest.json").read_text(encoding="utf-8")
        )
        return (
            "https://raw.githubusercontent.com/"
            f"{manifest['repository']}/{manifest['branch']}/"
        )
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError):
        return None


def local_raw_base_for_ref(root: Path, ref: str) -> str | None:
    """Return this repository's Raw base URL for an explicit Git ref."""
    try:
        manifest = json.loads(
            (root / "rules-manifest.json").read_text(encoding="utf-8")
        )
        repository = manifest["repository"]
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError):
        return None

    if (
        not isinstance(repository, str)
        or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)
    ):
        return None
    if (
        not ref
        or ref.startswith("/")
        or ref.endswith("/")
        or "//" in ref
        or any(part in {"", ".", ".."} for part in ref.split("/"))
        or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", ref)
    ):
        raise ValueError(f"invalid Git ref: {ref!r}")

    encoded_ref = urllib.parse.quote(ref, safe="/-._")
    return f"https://raw.githubusercontent.com/{repository}/{encoded_ref}/"


def local_relative_path(url: str, raw_base: str | None) -> str | None:
    """Return a safe repository-root filename for a configured Raw URL."""
    if raw_base is None or not url.startswith(raw_base):
        return None
    relative = url[len(raw_base) :]
    if (
        not relative
        or "/" in relative
        or relative in {".", ".."}
        or not re.fullmatch(r"[A-Za-z0-9_.-]+", relative)
    ):
        raise ValueError(f"unsafe local repository path: {relative!r}")
    return relative


def effective_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def is_skk_sentinel(line: str) -> bool:
    normalized = line.casefold()
    return any(alias in normalized for alias in SKK_SENTINEL_ALIASES)


def validate_upstream_domain(raw: str) -> str | None:
    if raw != raw.casefold():
        return "domain must be lowercase"
    domain = raw[1:] if raw.startswith(".") else raw
    if not domain or raw.startswith("..") or domain.endswith("."):
        return "invalid leading or trailing dot"
    if len(domain) > 253:
        return "domain exceeds 253 characters"
    try:
        ipaddress.ip_address(domain)
    except ValueError:
        pass
    else:
        return "IP address is not a DOMAIN-SET record"
    labels = domain.split(".")
    if any(not label for label in labels):
        return "domain must contain non-empty labels"
    for label in labels:
        if (
            len(label) > 63
            or label[0] not in "abcdefghijklmnopqrstuvwxyz0123456789_"
            or label[-1] not in "abcdefghijklmnopqrstuvwxyz0123456789_"
            or any(
                character not in "abcdefghijklmnopqrstuvwxyz0123456789-_"
                for character in label
            )
        ):
            return f"invalid domain label {label!r}"
    return None


def validate_domain_set(lines: Sequence[str]) -> str | None:
    for line_number, line in enumerate(lines, 1):
        if (
            "," in line
            or "://" in line
            or any(character.isspace() for character in line)
        ):
            return f"invalid DOMAIN-SET record {line_number}: {line!r}"
        problem = validate_upstream_domain(line)
        if problem:
            return f"invalid DOMAIN-SET record {line_number}: {problem}: {line!r}"
    return None


def validate_rule_set(lines: Sequence[str]) -> str | None:
    for line_number, line in enumerate(lines, 1):
        fields = [field.strip() for field in line.split(",")]
        if len(fields) < 2 or not fields[0]:
            return f"invalid RULE-SET record {line_number}: {line!r}"
        rule_type = fields[0].upper()
        if len(fields) >= 3 and fields[-1].casefold() in POLICY_TOKENS:
            return (
                f"RULE-SET record {line_number} contains an embedded policy "
                f"{fields[-1]!r}"
            )
        if rule_type in DOMAIN_RULE_TYPES and len(fields) != 2:
            return (
                f"RULE-SET record {line_number} has unsupported DOMAIN options: "
                f"{line!r}"
            )
        if rule_type in IP_RULE_TYPES and (
            len(fields) not in {2, 3}
            or (len(fields) == 3 and fields[2].casefold() != "no-resolve")
        ):
            return (
                f"RULE-SET record {line_number} has unsupported IP options: "
                f"{line!r}"
            )
    return None


def validate_payload(
    resource: Resource,
    text: str,
    strict_local_rule_set: bool = False,
) -> tuple[int, str]:
    if text.startswith("\ufeff"):
        return 0, "resource contains a UTF-8 BOM"
    beginning = text.lstrip()[:256].casefold()
    if beginning.startswith(("<!doctype html", "<html")):
        return 0, "resource returned an HTML document"

    header = "\n".join(text.splitlines()[:40])
    if re.search(r"^#.*\bdeprecated\b", header, flags=re.IGNORECASE | re.MULTILINE):
        return 0, "resource is marked Deprecated"

    lines = effective_lines(text)
    if not lines:
        return 0, "resource contains no effective rules"
    business_lines = [line for line in lines if not is_skk_sentinel(line)]
    if not business_lines:
        return 0, "resource contains only the SKK sentinel rule"

    if resource.rule_type == "DOMAIN-SET":
        problem = validate_domain_set(business_lines)
    else:
        problem = validate_rule_set(business_lines)
        if problem is None and strict_local_rule_set:
            for line_number, line in enumerate(business_lines, 1):
                _, local_problem = repository_validator.validate_policy_free_rule(
                    line
                )
                if local_problem:
                    problem = (
                        f"invalid local RULE-SET record {line_number}: "
                        f"{local_problem}: {line!r}"
                    )
                    break
    return len(business_lines), problem or ""


def read_http(
    url: str,
    timeout: float,
    max_bytes: int,
    retries: int,
) -> tuple[int, str, str, str]:
    last_error: Exception | None = None
    for _ in range(retries + 1):
        request = urllib.request.Request(
            url,
            headers={
                "Accept-Encoding": "identity",
                "User-Agent": "surge-rules-upstream-check/2.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                final_url = response.geturl()
                if urlsplit(final_url).scheme != "https":
                    raise ValueError(f"redirected to a non-HTTPS URL: {final_url}")
                declared_size = response.headers.get("Content-Length")
                if declared_size is not None:
                    try:
                        expected_size = int(declared_size)
                    except ValueError as exc:
                        raise ValueError(
                            f"invalid Content-Length: {declared_size!r}"
                        ) from exc
                    if expected_size > max_bytes:
                        raise ValueError(f"resource exceeds {max_bytes} bytes")
                payload = response.read(max_bytes + 1)
                if len(payload) > max_bytes:
                    raise ValueError(f"resource exceeds {max_bytes} bytes")
                if declared_size is not None and len(payload) != expected_size:
                    raise ValueError(
                        "Content-Length mismatch: "
                        f"expected {expected_size}, received {len(payload)}"
                    )
                content_type = response.headers.get_content_type().lower()
                if content_type not in ALLOWED_CONTENT_TYPES:
                    raise ValueError(f"unexpected content type: {content_type}")
                return (
                    response.status,
                    final_url,
                    content_type,
                    payload.decode("utf-8"),
                )
        except (
            http.client.HTTPException,
            urllib.error.URLError,
            TimeoutError,
            OSError,
        ) as exc:
            last_error = exc
    assert last_error is not None
    raise last_error


def probe(
    resource: Resource,
    timeout: float,
    max_bytes: int,
    root: Path,
    raw_base: str | None,
    fetch_local: bool,
    retries: int,
    local_ref_base: str | None = None,
) -> Result:
    result_resource = resource
    try:
        relative = local_relative_path(resource.url, raw_base)
        if relative is not None and not fetch_local and local_ref_base is None:
            text = (root / relative).read_text(encoding="utf-8")
            status = 200
            final_url = resource.url
            source = "LOCAL"
        else:
            request_url = (
                f"{local_ref_base}{relative}"
                if relative is not None and local_ref_base is not None
                else resource.url
            )
            result_resource = Resource(
                request_url,
                resource.rule_type,
                resource.line,
            )
            status, final_url, _, text = read_http(
                request_url,
                timeout,
                max_bytes,
                retries,
            )
            source = "HTTP"
        count, problem = validate_payload(
            result_resource,
            text,
            strict_local_rule_set=relative is not None,
        )
        return Result(result_resource, status, source, count, problem, final_url)
    except urllib.error.HTTPError as exc:
        return Result(result_resource, exc.code, "HTTP", 0, str(exc.reason))
    except (
        UnicodeError,
        urllib.error.URLError,
        TimeoutError,
        OSError,
        ValueError,
    ) as exc:
        return Result(result_resource, None, "ERR", 0, str(exc))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--main",
        type=Path,
        default=REPOSITORY_ROOT / "surge-main.conf",
        help="Surge file containing remote rule URLs",
    )
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--max-bytes", type=int, default=16 * 1024 * 1024)
    local_source = parser.add_mutually_exclusive_group()
    local_source.add_argument(
        "--fetch-local",
        action="store_true",
        help="fetch this repository's Raw URLs instead of validating local files",
    )
    local_source.add_argument(
        "--local-ref",
        metavar="REF",
        help=(
            "fetch this repository's Raw files from an explicit Git ref "
            "(for example the current commit SHA)"
        ),
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="check only this repository's Raw resources",
    )
    parser.add_argument(
        "--config-ref",
        metavar="REF",
        help=(
            "load surge-main.conf from this repository at REF and fetch its "
            "local Raw resources (used to validate a deployed production ref)"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if (
        args.timeout <= 0
        or args.workers < 1
        or args.retries < 0
        or args.max_bytes < 1
    ):
        print(
            "timeout, workers and max-bytes must be positive; retries cannot be negative",
            file=sys.stderr,
        )
        return 2
    main_path = args.main.resolve()
    root = main_path.parent
    try:
        local_ref_base = (
            local_raw_base_for_ref(root, args.local_ref)
            if args.local_ref is not None
            else None
        )
        config_ref_base = (
            local_raw_base_for_ref(root, args.config_ref)
            if args.config_ref is not None
            else None
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.config_ref is not None and (
        args.local_ref is not None or args.fetch_local
    ):
        print(
            "--config-ref cannot be combined with --local-ref or --fetch-local",
            file=sys.stderr,
        )
        return 2

    try:
        if config_ref_base is not None:
            config_url = f"{config_ref_base}{main_path.name}"
            _, final_url, _, config_text = read_http(
                config_url,
                args.timeout,
                args.max_bytes,
                args.retries,
            )
            resources = collect_resources_text(config_text)
            print(f"Loaded deployed configuration: {final_url}")
        else:
            resources = collect_resources(main_path)
    except urllib.error.HTTPError as exc:
        print(
            f"cannot fetch deployed configuration: HTTP {exc.code} {exc.reason}",
            file=sys.stderr,
        )
        return 2
    except (
        UnicodeError,
        urllib.error.URLError,
        TimeoutError,
        OSError,
        ValueError,
    ) as exc:
        print(f"cannot read configuration: {exc}", file=sys.stderr)
        return 2

    raw_base = config_ref_base or local_raw_base(root)
    if raw_base is None:
        print("cannot determine local Raw URL base from rules-manifest.json", file=sys.stderr)
        return 2

    try:
        local_resources = [
            resource
            for resource in resources
            if local_relative_path(resource.url, raw_base) is not None
        ]
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if not local_resources:
        print("surge-main.conf contains no local Raw resources", file=sys.stderr)
        return 2
    if args.local_only:
        resources = local_resources

    results: list[Result] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        pending = {
            executor.submit(
                probe,
                resource,
                args.timeout,
                args.max_bytes,
                root,
                raw_base,
                args.fetch_local or config_ref_base is not None,
                args.retries,
                local_ref_base,
            ): resource
            for resource in resources
        }
        for future in as_completed(pending):
            results.append(future.result())

    failures = 0
    for result in sorted(results, key=lambda item: item.resource):
        failures += not result.passed
        status = str(result.status) if result.status is not None else "ERR"
        print(
            f"{'PASS' if result.passed else 'FAIL'} {status:>3} "
            f"{result.resource.rule_type:<10} {result.effective_rules:>6} "
            f"{result.source:<5} {result.resource.url}"
        )
        if result.final_url and result.final_url != result.resource.url:
            print(f"         redirected to {result.final_url}")
        if result.message:
            print(f"         {result.message}")

    print(
        f"Checked {len(resources)} resources: "
        f"{len(resources) - failures} passed, {failures} failed"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
