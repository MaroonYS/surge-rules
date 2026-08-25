#!/usr/bin/env python3
"""Validate this repository's local Surge rule files and main rule skeleton."""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Sequence
from urllib.parse import urlsplit


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
FORBIDDEN_SUFFIXES = {
    "apple.com",
    "auth0.com",
    "cloudflare.com",
    "co.jp",
    "co.kr",
    "co.uk",
    "com.cn",
    "com.hk",
    "com.sg",
    "google.com",
    "icloud.com",
    "microsoft.com",
}
ALLOWED_KEYWORD_RULES: set[str] = set()
SENSITIVE_POLICIES = {
    "Finance",
    "Identity",
    "Risk",
    "Verification",
    "Res-Frontier",
}
ALLOWED_SENSITIVE_SHARED_SUFFIX_ENTRIES = {
    ("us-residential.conf", "Res-Frontier", "apexclearing.com"),
    ("us-residential.conf", "Res-Frontier", "earlywarning.com"),
    ("us-residential.conf", "Res-Frontier", "id.me"),
    ("us-residential.conf", "Res-Frontier", "login.gov"),
    ("identity-context.conf", "Identity", "socure.com"),
    ("identity-context.conf", "Identity", "socure.co"),
    ("identity-context.conf", "Identity", "withpersona.com"),
    ("identity-context.conf", "Identity", "jumio.com"),
    ("identity-context.conf", "Identity", "jumio.ai"),
    ("identity-context.conf", "Identity", "netverify.com"),
    ("identity-context.conf", "Identity", "onfido.com"),
    ("identity-context.conf", "Identity", "trulioo.com"),
    ("identity-context.conf", "Identity", "idology.com"),
    ("identity-context.conf", "Identity", "au10tix.com"),
    ("identity-context.conf", "Identity", "alloy.com"),
    ("identity-context.conf", "Identity", "sentilink.com"),
    ("identity-context.conf", "Identity", "middesk.com"),
    ("identity-context.conf", "Identity", "prove.com"),
    ("identity-context.conf", "Identity", "proveidentity.com"),
    ("identity-context.conf", "Identity", "miteksystems.com"),
    ("identity-context.conf", "Identity", "mitekcloud.com"),
    ("identity-context.conf", "Identity", "veriff.com"),
    ("identity-context.conf", "Identity", "sumsub.com"),
    ("identity-context.conf", "Identity", "vouched.id"),
    ("identity-context.conf", "Identity", "ekata.com"),
    ("risk-context.conf", "Risk", "online-metrix.net"),
    ("risk-context.conf", "Risk", "threatmetrix.com"),
    ("risk-context.conf", "Risk", "iovation.com"),
    ("risk-context.conf", "Risk", "iovation.io"),
    ("risk-context.conf", "Risk", "biocatch.com"),
    ("risk-context.conf", "Risk", "fingerprint.com"),
    ("risk-context.conf", "Risk", "fingerprintjs.com"),
    ("risk-context.conf", "Risk", "incognia.com"),
}
SHARED_INFRASTRUCTURE_SUFFIXES = {
    "akoya.com",
    "alloy.com",
    "apexclearing.com",
    "argyle.com",
    "arkoselabs.com",
    "au10tix.com",
    "biocatch.com",
    "castle.io",
    "clarityservices.com",
    "consumerdebit.com",
    "corelogic.com",
    "datadome.co",
    "dataxltd.com",
    "earlywarning.com",
    "ekata.com",
    "factortrust.com",
    "fingerprint.com",
    "fingerprintjs.com",
    "finicity.com",
    "forter.com",
    "funcaptcha.com",
    "hcaptcha.com",
    "humansecurity.com",
    "id.me",
    "idology.com",
    "incognia.com",
    "iovation.com",
    "iovation.io",
    "jumio.ai",
    "jumio.com",
    "lexisnexisrisk.com",
    "login.gov",
    "microbilt.com",
    "middesk.com",
    "mitekcloud.com",
    "miteksystems.com",
    "mx.com",
    "netverify.com",
    "onfido.com",
    "online-metrix.net",
    "perimeterx.net",
    "persona.com",
    "plaid.com",
    "plaidcdn.com",
    "prove.com",
    "proveidentity.com",
    "riskified.com",
    "sagestreamllc.com",
    "sardine.ai",
    "seon.io",
    "sentilink.com",
    "sift.com",
    "siftcdn.net",
    "socure.co",
    "socure.com",
    "squareup.com",
    "stripe.com",
    "stripe.network",
    "sumsub.com",
    "teletrack.com",
    "threatmetrix.com",
    "trulioo.com",
    "veriff.com",
    "vouched.id",
    "withpersona.com",
    "yodlee.com",
}
LOCAL_RULE_TYPES = {
    "AND",
    "DEST-PORT",
    "DOMAIN",
    "DOMAIN-SUFFIX",
    "DOMAIN-WILDCARD",
    "IP-CIDR",
    "IP-CIDR6",
    "PROTOCOL",
}
LOGICAL_LEAF_TYPES = {
    "DEST-PORT",
    "DOMAIN",
    "DOMAIN-SUFFIX",
    "IP-CIDR",
    "IP-CIDR6",
    "PROTOCOL",
}
LOCAL_PROTOCOLS = {"TCP", "UDP"}


@dataclass(frozen=True)
class Diagnostic:
    severity: str
    code: str
    path: str
    line: int
    message: str


@dataclass(frozen=True)
class DomainEntry:
    path: str
    line: int
    raw: str
    domain: str
    suffix: bool
    policy: str
    archive: bool = False

    @property
    def semantic_key(self) -> tuple[bool, str]:
        return (self.suffix, self.domain)


@dataclass(frozen=True)
class RuleSetEntry:
    path: str
    line: int
    raw: str
    rule_type: str
    policy: str


@dataclass(frozen=True)
class Binding:
    file: str
    policy: str
    description: str
    type: str = "DOMAIN-SET"
    semantic_role: str = ""

    @property
    def semantic_policy(self) -> str:
        """Return the logical validation layer independently of runtime routing."""
        return self.semantic_role or self.policy


@dataclass
class ValidationResult:
    diagnostics: list[Diagnostic]
    active_entries: list[DomainEntry]
    archive_entries: list[DomainEntry]
    bindings: list[Binding]
    main_rule_count: int
    local_references: int
    active_rule_entries: list[RuleSetEntry] = field(default_factory=list)

    @property
    def errors(self) -> list[Diagnostic]:
        return [item for item in self.diagnostics if item.severity == "error"]

    @property
    def warnings(self) -> list[Diagnostic]:
        return [item for item in self.diagnostics if item.severity == "warning"]

    def report(self, strict: bool) -> dict[str, object]:
        exact = sum(not entry.suffix for entry in self.active_entries)
        suffix = sum(entry.suffix for entry in self.active_entries)
        ok = not self.errors and (not strict or not self.warnings)
        policy_counts = [
            {
                "file": binding.file,
                "policy": binding.policy,
                "semantic_role": binding.semantic_policy,
                "entries": sum(
                    entry.path == binding.file for entry in self.active_entries
                )
                + sum(
                    entry.path == binding.file for entry in self.active_rule_entries
                ),
            }
            for binding in self.bindings
        ]
        return {
            "ok": ok,
            "strict": strict,
            "files": {
                "active": len(self.bindings),
                "domain_set": sum(
                    binding.type == "DOMAIN-SET" for binding in self.bindings
                ),
                "rule_set": sum(
                    binding.type == "RULE-SET" for binding in self.bindings
                ),
                "archive": len({entry.path for entry in self.archive_entries}),
            },
            "entries": {
                "active": len(self.active_entries) + len(self.active_rule_entries),
                "domain_set": len(self.active_entries),
                "rule_set": len(self.active_rule_entries),
                "exact": exact,
                "suffix": suffix,
                "archive": len(self.archive_entries),
            },
            "main_rules": self.main_rule_count,
            "references": {
                "expected": len(self.bindings),
                "found": self.local_references,
            },
            "diagnostics": {
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "items": [asdict(item) for item in sorted_diagnostics(self.diagnostics)],
            },
            "policies": policy_counts,
        }


class ConfigurationError(RuntimeError):
    """The validator itself could not load the repository configuration."""


def sorted_diagnostics(items: Iterable[Diagnostic]) -> list[Diagnostic]:
    order = {"error": 0, "warning": 1}
    return sorted(
        items,
        key=lambda item: (
            order.get(item.severity, 9),
            item.path,
            item.line,
            item.code,
            item.message,
        ),
    )


def _diag(
    diagnostics: list[Diagnostic],
    severity: str,
    code: str,
    path: str,
    line: int,
    message: str,
) -> None:
    diagnostics.append(Diagnostic(severity, code, path, line, message))


def load_manifest(root: Path) -> tuple[str, str, str, str, list[Binding]]:
    path = root / "rules-manifest.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"cannot read {path}: {exc}") from exc

    try:
        repository = str(data["repository"])
        branch = str(data["branch"])
        main = str(data["main"])
        contract = str(data["contract"])
        raw_bindings = data["active"]
    except (KeyError, TypeError) as exc:
        raise ConfigurationError(f"invalid manifest structure: {exc}") from exc

    if (
        repository.count("/") != 1
        or not branch
        or Path(main).is_absolute()
        or ".." in Path(main).parts
        or Path(contract).is_absolute()
        or ".." in Path(contract).parts
    ):
        raise ConfigurationError("manifest repository, branch, or main path is invalid")

    bindings: list[Binding] = []
    seen_files: set[str] = set()
    for item in raw_bindings:
        try:
            binding = Binding(
                file=str(item["file"]),
                policy=str(item["policy"]),
                description=str(item.get("description", "")),
                type=str(item.get("type", "DOMAIN-SET")),
                semantic_role=str(item.get("semantic_role", item["policy"])),
            )
        except (AttributeError, KeyError, TypeError) as exc:
            raise ConfigurationError(f"invalid active binding: {exc}") from exc
        file_path = Path(binding.file)
        if (
            file_path.is_absolute()
            or len(file_path.parts) != 1
            or file_path.suffix != ".conf"
            or binding.file in seen_files
            or not binding.policy
            or not binding.semantic_role
            or binding.type not in {"DOMAIN-SET", "RULE-SET"}
        ):
            raise ConfigurationError(f"invalid active binding: {binding}")
        bindings.append(binding)
        seen_files.add(binding.file)

    if not bindings:
        raise ConfigurationError("manifest contains no active bindings")
    return repository, branch, main, contract, bindings


def _safe_repository_path(root: Path, relative: str) -> Path:
    candidate = root / relative
    resolved_root = root.resolve()
    try:
        resolved = candidate.resolve()
        resolved.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise ConfigurationError(f"path escapes repository root: {relative}") from exc
    if candidate.is_symlink():
        raise ConfigurationError(f"symbolic links are not accepted: {relative}")
    return candidate


def normalize_policy_name(value: str) -> str:
    """Normalize the optional Surge quotes used by policy names with spaces."""
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def validate_domain(raw: str) -> str | None:
    """Return an error message for an invalid DOMAIN-SET entry, else None."""
    if raw != raw.strip():
        return "leading or trailing whitespace is not allowed"
    if not raw:
        return "empty domain"
    if raw != raw.lower():
        return "domains must use lowercase ASCII"
    if any(character.isspace() for character in raw):
        return "whitespace is not allowed inside a domain"
    if raw.startswith(".."):
        return "at most one leading dot is allowed"

    domain = raw[1:] if raw.startswith(".") else raw
    if not domain:
        return "missing domain after leading dot"
    if len(domain) > 253:
        return "domain exceeds 253 characters"
    if domain.endswith("."):
        return "trailing dot is not allowed"
    if "://" in domain or any(token in domain for token in ("*", "/", ":", ",", "#")):
        return "URLs, paths, ports, wildcards, commas and inline comments are not allowed"

    try:
        ipaddress.ip_address(domain)
    except ValueError:
        pass
    else:
        return "IP addresses are not valid DOMAIN-SET entries"

    labels = domain.split(".")
    if len(labels) < 2 or any(not label for label in labels):
        return "a domain must contain at least two non-empty labels"
    for label in labels:
        if len(label) > 63:
            return f"label exceeds 63 characters: {label!r}"
        if not LABEL_RE.fullmatch(label):
            return f"invalid DNS label: {label!r}"
        if label.startswith("xn--"):
            try:
                decoded = label.encode("ascii").decode("idna")
                encoded = decoded.encode("idna").decode("ascii")
            except UnicodeError:
                return f"invalid punycode label: {label!r}"
            if encoded != label:
                return f"non-canonical punycode label: {label!r}"
    if raw.startswith(".") and domain in FORBIDDEN_SUFFIXES:
        return f"suffix is too broad for precise routing: {raw}"
    return None


def validate_domain_wildcard(raw: str) -> str | None:
    """Return an error for an unsafe DOMAIN-WILDCARD matcher, else None."""
    if not any(character in raw for character in "*?"):
        return "DOMAIN-WILDCARD matcher must contain * or ?"

    literalized = raw.replace("*", "a").replace("?", "a")
    problem = validate_domain(literalized)
    if problem:
        return problem

    labels = raw.split(".")
    fixed_suffix_labels: list[str] = []
    for label in reversed(labels):
        if "*" in label or "?" in label:
            break
        fixed_suffix_labels.append(label)
    if len(fixed_suffix_labels) < 2:
        return (
            "DOMAIN-WILDCARD matcher is too broad; "
            "at least two fixed suffix labels are required"
        )

    fixed_suffix = ".".join(reversed(fixed_suffix_labels))
    wildcard_prefix = labels[: -len(fixed_suffix_labels)]
    if fixed_suffix in FORBIDDEN_SUFFIXES and all(
        set(label) <= {"*", "?"} for label in wildcard_prefix
    ):
        return f"wildcard suffix is too broad for precise routing: {raw}"
    return None


def parse_domain_set(
    root: Path,
    relative: str,
    policy: str,
    archive: bool,
    diagnostics: list[Diagnostic],
) -> list[DomainEntry]:
    try:
        path = _safe_repository_path(root, relative)
    except ConfigurationError as exc:
        _diag(diagnostics, "error", "UNSAFE_PATH", relative, 0, str(exc))
        return []

    try:
        payload = path.read_bytes()
    except OSError as exc:
        _diag(diagnostics, "error", "FILE_READ", relative, 0, str(exc))
        return []

    if payload.startswith(b"\xef\xbb\xbf"):
        _diag(
            diagnostics,
            "error",
            "UTF8_BOM",
            relative,
            1,
            "UTF-8 BOM is not allowed",
        )
        payload = payload[3:]
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        _diag(diagnostics, "error", "UTF8", relative, exc.start, str(exc))
        return []

    if payload and not payload.endswith((b"\n", b"\r")):
        _diag(
            diagnostics,
            "warning",
            "FINAL_NEWLINE",
            relative,
            len(text.splitlines()),
            "file should end with a newline",
        )

    entries: list[DomainEntry] = []
    first_seen: dict[tuple[bool, str], DomainEntry] = {}
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        if not raw_line or raw_line.startswith("#"):
            continue
        problem = validate_domain(raw_line)
        if problem:
            _diag(
                diagnostics,
                "error",
                "DOMAIN_SYNTAX",
                relative,
                line_number,
                problem,
            )
            continue
        suffix = raw_line.startswith(".")
        domain = raw_line[1:] if suffix else raw_line
        entry = DomainEntry(
            path=relative,
            line=line_number,
            raw=raw_line,
            domain=domain,
            suffix=suffix,
            policy=policy,
            archive=archive,
        )
        original = first_seen.get(entry.semantic_key)
        if original is not None:
            _diag(
                diagnostics,
                "error",
                "DUPLICATE",
                relative,
                line_number,
                f"duplicates line {original.line}: {raw_line}",
            )
            continue
        first_seen[entry.semantic_key] = entry
        entries.append(entry)

    detect_internal_redundancy(entries, diagnostics)
    return entries


def split_rule_fields(raw: str) -> tuple[list[str], str | None]:
    """Split a rule on top-level commas while preserving logical sub-rules."""
    fields: list[str] = []
    start = 0
    depth = 0
    for index, character in enumerate(raw):
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth < 0:
                return [], "unbalanced parentheses"
        elif character == "," and depth == 0:
            fields.append(raw[start:index])
            start = index + 1
    if depth != 0:
        return [], "unbalanced parentheses"
    fields.append(raw[start:])
    return fields, None


def _logical_children(expression: str) -> tuple[list[str], str | None]:
    if not (expression.startswith("(") and expression.endswith(")")):
        return [], "logical matcher must wrap its sub-rules in parentheses"
    children, problem = split_rule_fields(expression[1:-1])
    if problem:
        return [], problem
    unwrapped: list[str] = []
    for child in children:
        if not (child.startswith("(") and child.endswith(")")):
            return [], "each logical sub-rule must be parenthesized"
        unwrapped.append(child[1:-1])
    return unwrapped, None


def _invalid_rule_fields(rule_type: str) -> tuple[None, str]:
    return (
        None,
        f"{rule_type} contains an embedded policy or unsupported option",
    )


def _validate_destination_port(matcher: str) -> str | None:
    match = re.fullmatch(r"([0-9]{1,5})(?:-([0-9]{1,5}))?", matcher)
    if match is None:
        return "DEST-PORT must be one port or one inclusive port range"
    start = int(match.group(1))
    end = int(match.group(2) or match.group(1))
    if not (1 <= start <= end <= 65535):
        return "DEST-PORT values must satisfy 1 <= start <= end <= 65535"
    return None


def validate_policy_free_rule(raw: str) -> tuple[str | None, str | None]:
    """Validate one deliberately narrow, policy-free local RULE-SET record.

    The repository currently needs logical AND rules composed from TCP/UDP,
    destination-port and IP-network leaves. Simple domain and IP records stay
    supported for deterministic expansion tests. Other Surge rule types must
    be added explicitly instead of being accepted by a permissive parser.
    """
    if raw != raw.strip():
        return None, "leading or trailing whitespace is not allowed"
    fields, problem = split_rule_fields(raw)
    if problem:
        return None, problem
    if any(field != field.strip() for field in fields):
        return None, "whitespace around top-level commas is not allowed"
    if len(fields) < 2 or not fields[0] or not fields[1]:
        return None, "a rule type and matcher are required"

    rule_type = fields[0]
    if rule_type not in LOCAL_RULE_TYPES:
        return None, f"unsupported local RULE-SET rule type: {rule_type!r}"

    if rule_type in {"IP-CIDR", "IP-CIDR6"}:
        if len(fields) == 3 and fields[2] == "no-resolve":
            pass
        elif len(fields) != 2:
            return _invalid_rule_fields(rule_type)
    elif len(fields) != 2:
        return _invalid_rule_fields(rule_type)

    matcher = fields[1]
    if rule_type == "AND":
        children, problem = _logical_children(matcher)
        if problem:
            return None, problem
        if len(children) < 2:
            return None, "AND requires at least two sub-rules"
        for child in children:
            child_type, child_problem = validate_policy_free_rule(child)
            if child_problem:
                return None, f"invalid logical sub-rule: {child_problem}"
            if child_type not in LOGICAL_LEAF_TYPES:
                return None, "nested logical rules are not supported"
        return rule_type, None

    if rule_type == "DOMAIN":
        if matcher.startswith("."):
            return None, "DOMAIN matcher must not start with a dot"
        problem = validate_domain(matcher)
        if problem:
            return None, problem
    elif rule_type == "DOMAIN-WILDCARD":
        problem = validate_domain_wildcard(matcher)
        if problem:
            return None, problem
    elif rule_type == "DOMAIN-SUFFIX":
        if matcher.startswith("."):
            return None, "DOMAIN-SUFFIX matcher must not start with a dot"
        problem = validate_domain(f".{matcher}")
        if problem:
            return None, problem
    elif rule_type in {"IP-CIDR", "IP-CIDR6"}:
        try:
            network = ipaddress.ip_network(matcher, strict=True)
        except ValueError as exc:
            return None, f"invalid network: {exc}"
        expected_version = 6 if rule_type == "IP-CIDR6" else 4
        if network.version != expected_version:
            return None, f"{rule_type} requires an IPv{expected_version} network"
    elif rule_type == "PROTOCOL":
        if matcher not in LOCAL_PROTOCOLS:
            return None, "PROTOCOL must be TCP or UDP"
    elif rule_type == "DEST-PORT":
        problem = _validate_destination_port(matcher)
        if problem:
            return None, problem

    return rule_type, None


def parse_rule_set(
    root: Path,
    relative: str,
    policy: str,
    diagnostics: list[Diagnostic],
) -> list[RuleSetEntry]:
    try:
        path = _safe_repository_path(root, relative)
    except ConfigurationError as exc:
        _diag(diagnostics, "error", "UNSAFE_PATH", relative, 0, str(exc))
        return []

    try:
        payload = path.read_bytes()
    except OSError as exc:
        _diag(diagnostics, "error", "FILE_READ", relative, 0, str(exc))
        return []

    if payload.startswith(b"\xef\xbb\xbf"):
        _diag(diagnostics, "error", "UTF8_BOM", relative, 1, "UTF-8 BOM is not allowed")
        payload = payload[3:]
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        _diag(diagnostics, "error", "UTF8", relative, exc.start, str(exc))
        return []

    if payload and not payload.endswith((b"\n", b"\r")):
        _diag(
            diagnostics,
            "warning",
            "FINAL_NEWLINE",
            relative,
            len(text.splitlines()),
            "file should end with a newline",
        )

    entries: list[RuleSetEntry] = []
    first_seen: dict[str, RuleSetEntry] = {}
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        if not raw_line or raw_line.startswith("#"):
            continue
        rule_type, problem = validate_policy_free_rule(raw_line)
        if problem:
            _diag(
                diagnostics,
                "error",
                "RULE_SYNTAX",
                relative,
                line_number,
                problem,
            )
            continue
        assert rule_type is not None
        entry = RuleSetEntry(
            path=relative,
            line=line_number,
            raw=raw_line,
            rule_type=rule_type,
            policy=policy,
        )
        original = first_seen.get(raw_line)
        if original is not None:
            _diag(
                diagnostics,
                "error",
                "DUPLICATE",
                relative,
                line_number,
                f"duplicates line {original.line}: {raw_line}",
            )
            continue
        first_seen[raw_line] = entry
        entries.append(entry)
    return entries


def rule_set_domain_entries(entries: Sequence[RuleSetEntry]) -> list[DomainEntry]:
    """Expose simple RULE-SET domain records to overlap safety checks."""
    domains: list[DomainEntry] = []
    for entry in entries:
        if entry.rule_type not in {"DOMAIN", "DOMAIN-SUFFIX"}:
            continue
        fields, problem = split_rule_fields(entry.raw)
        if problem or len(fields) < 2:
            continue
        suffix = entry.rule_type == "DOMAIN-SUFFIX"
        domain = fields[1]
        domains.append(
            DomainEntry(
                path=entry.path,
                line=entry.line,
                raw=f".{domain}" if suffix else domain,
                domain=domain,
                suffix=suffix,
                policy=entry.policy,
            )
        )
    return domains


def domain_ancestors(domain: str) -> Iterable[str]:
    labels = domain.split(".")
    for index in range(0, len(labels) - 1):
        yield ".".join(labels[index:])


def detect_internal_redundancy(
    entries: Sequence[DomainEntry], diagnostics: list[Diagnostic]
) -> None:
    suffixes = {entry.domain: entry for entry in entries if entry.suffix}
    reported: set[tuple[str, int]] = set()
    for entry in entries:
        for ancestor in domain_ancestors(entry.domain):
            owner = suffixes.get(ancestor)
            if owner is None or owner == entry:
                continue
            marker = (entry.path, entry.line)
            if marker not in reported:
                _diag(
                    diagnostics,
                    "error",
                    "REDUNDANT",
                    entry.path,
                    entry.line,
                    f"{entry.raw} is already covered by {owner.raw} at line {owner.line}",
                )
                reported.add(marker)
            break


def detect_active_overlaps(
    entries: Sequence[DomainEntry], diagnostics: list[Diagnostic]
) -> None:
    exact_index: dict[str, list[DomainEntry]] = {}
    suffix_index: dict[str, list[DomainEntry]] = {}
    for entry in entries:
        target = suffix_index if entry.suffix else exact_index
        target.setdefault(entry.domain, []).append(entry)

    reported: set[tuple[str, int, str, int]] = set()

    def report(left: DomainEntry, right: DomainEntry, code: str) -> None:
        if left.path == right.path:
            return
        ordered = sorted(
            (left, right), key=lambda item: (item.path, item.line, item.raw)
        )
        marker = (
            ordered[0].path,
            ordered[0].line,
            ordered[1].path,
            ordered[1].line,
        )
        if marker in reported:
            return
        reported.add(marker)
        relation = (
            "cross-policy overlap"
            if left.policy != right.policy
            else "cross-file redundancy"
        )
        _diag(
            diagnostics,
            "error",
            code,
            right.path,
            right.line,
            (
                f"{relation}: {right.raw} ({right.policy}) conflicts with "
                f"{left.path}:{left.line} {left.raw} ({left.policy})"
            ),
        )

    for group in list(exact_index.values()) + list(suffix_index.values()):
        for index, left in enumerate(group):
            for right in group[index + 1 :]:
                report(left, right, "CROSS_FILE_DUPLICATE")

    for entry in entries:
        for ancestor in domain_ancestors(entry.domain):
            for owner in suffix_index.get(ancestor, []):
                if owner.semantic_key == entry.semantic_key:
                    continue
                report(owner, entry, "CROSS_FILE_OVERLAP")


def detect_shared_infrastructure(
    entries: Sequence[DomainEntry], diagnostics: list[Diagnostic]
) -> None:
    for entry in entries:
        if (
            entry.policy in SENSITIVE_POLICIES
            and entry.suffix
            and entry.domain in SHARED_INFRASTRUCTURE_SUFFIXES
            and (
                entry.path,
                entry.policy,
                entry.domain,
            )
            not in ALLOWED_SENSITIVE_SHARED_SUFFIX_ENTRIES
        ):
            _diag(
                diagnostics,
                "error",
                "SHARED_INFRASTRUCTURE",
                entry.path,
                entry.line,
                (
                    f"{entry.raw} is shared infrastructure and must not be "
                    f"globally pinned to {entry.policy}; add only an observed "
                    "first-party host if a narrow exception is required"
                ),
            )


def _read_main_rules(
    root: Path, relative: str, diagnostics: list[Diagnostic]
) -> list[tuple[int, str]]:
    try:
        path = _safe_repository_path(root, relative)
        payload = path.read_bytes()
    except (ConfigurationError, OSError) as exc:
        _diag(diagnostics, "error", "MAIN_READ", relative, 0, str(exc))
        return []

    if payload.startswith(b"\xef\xbb\xbf"):
        _diag(diagnostics, "error", "UTF8_BOM", relative, 1, "UTF-8 BOM is not allowed")
        payload = payload[3:]
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        _diag(diagnostics, "error", "UTF8", relative, exc.start, str(exc))
        return []

    section_headers = [
        (number, line.strip())
        for number, line in enumerate(text.splitlines(), 1)
        if line.strip().startswith("[") and line.strip().endswith("]")
    ]
    rule_headers = [item for item in section_headers if item[1] == "[Rule]"]
    if len(rule_headers) != 1:
        _diag(
            diagnostics,
            "error",
            "RULE_SECTION",
            relative,
            0,
            f"expected exactly one [Rule] section, found {len(rule_headers)}",
        )
        return []

    start = rule_headers[0][0]
    later_headers = [number for number, _ in section_headers if number > start]
    end = min(later_headers) if later_headers else len(text.splitlines()) + 1
    return [
        (number, line.strip())
        for number, line in enumerate(text.splitlines(), 1)
        if start < number < end and line.strip() and not line.lstrip().startswith("#")
    ]


def validate_rule_contract(
    root: Path,
    main_relative: str,
    contract_relative: str,
    rules: Sequence[tuple[int, str]],
    diagnostics: list[Diagnostic],
) -> None:
    try:
        contract_path = _safe_repository_path(root, contract_relative)
        main_path = _safe_repository_path(root, main_relative)
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        main_text = main_path.read_text(encoding="utf-8")
        sections = contract["sections"]
    except (
        ConfigurationError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
    ) as exc:
        _diag(
            diagnostics,
            "error",
            "RULE_CONTRACT_READ",
            contract_relative,
            0,
            str(exc),
        )
        return

    expected_numbers = list(range(1, len(sections) + 1))
    actual_numbers = [section.get("number") for section in sections]
    if actual_numbers != expected_numbers:
        _diag(
            diagnostics,
            "error",
            "RULE_CONTRACT_SECTIONS",
            contract_relative,
            0,
            (
                f"expected contiguous section numbers 1..{len(sections)}, "
                f"found {actual_numbers}"
            ),
        )
        return

    header_positions: list[int] = []
    main_lines = main_text.splitlines()
    expected_rules: list[str] = []
    for section in sections:
        number = section["number"]
        title = section["title"]
        header = f"# {number}. {title}"
        positions = [
            line_number
            for line_number, line in enumerate(main_lines, 1)
            if line.strip() == header
        ]
        if len(positions) != 1:
            _diag(
                diagnostics,
                "error",
                "RULE_SECTION_HEADER",
                main_relative,
                positions[0] if positions else 0,
                f"expected exactly one header {header!r}, found {len(positions)}",
            )
        else:
            header_positions.append(positions[0])
        section_rules = section.get("rules")
        if not isinstance(section_rules, list) or not all(
            isinstance(rule, str) and rule for rule in section_rules
        ):
            _diag(
                diagnostics,
                "error",
                "RULE_CONTRACT_CONTENT",
                contract_relative,
                0,
                f"section {number} has invalid rules",
            )
            return
        expected_rules.extend(section_rules)

    if header_positions != sorted(header_positions):
        _diag(
            diagnostics,
            "error",
            "RULE_SECTION_ORDER",
            main_relative,
            0,
            "numbered section headers are not in ascending order",
        )

    actual_rules = [rule for _, rule in rules]
    if actual_rules != expected_rules:
        mismatch = next(
            (
                index
                for index, (actual, expected) in enumerate(
                    zip(actual_rules, expected_rules)
                )
                if actual != expected
            ),
            min(len(actual_rules), len(expected_rules)),
        )
        line_number = rules[mismatch][0] if mismatch < len(rules) else 0
        actual = actual_rules[mismatch] if mismatch < len(actual_rules) else "<missing>"
        expected = (
            expected_rules[mismatch]
            if mismatch < len(expected_rules)
            else "<no additional rule>"
        )
        _diag(
            diagnostics,
            "error",
            "RULE_CONTRACT_MISMATCH",
            main_relative,
            line_number,
            (
                f"rule {mismatch + 1} differs from the rule contract; "
                f"expected {expected!r}, found {actual!r}"
            ),
        )


def validate_main_rules(
    root: Path,
    relative: str,
    repository: str,
    branch: str,
    contract_relative: str,
    bindings: Sequence[Binding],
    diagnostics: list[Diagnostic],
) -> tuple[int, int]:
    rules = _read_main_rules(root, relative, diagnostics)
    if not rules:
        return 0, 0

    validate_rule_contract(
        root,
        relative,
        contract_relative,
        rules,
        diagnostics,
    )

    canonical_base = f"https://raw.githubusercontent.com/{repository}/{branch}/"
    expected = {binding.file: binding for binding in bindings}
    references: list[tuple[int, str, str]] = []

    for line_number, rule in rules:
        fields = [field.strip() for field in rule.split(",")]
        if len(fields) >= 2 and fields[0] in {"DOMAIN-SET", "RULE-SET"}:
            url = fields[1]
            parsed = urlsplit(url)
            if "/archive/" in parsed.path:
                _diag(
                    diagnostics,
                    "error",
                    "ARCHIVE_REFERENCE",
                    relative,
                    line_number,
                    "archive files must never be loaded",
                )

            is_same_repository = (
                parsed.netloc == "raw.githubusercontent.com"
                and parsed.path.startswith(f"/{repository}/")
            )
            if is_same_repository:
                if (
                    parsed.scheme != "https"
                    or parsed.query
                    or parsed.fragment
                    or not url.startswith(canonical_base)
                ):
                    _diag(
                        diagnostics,
                        "error",
                        "NONCANONICAL_URL",
                        relative,
                        line_number,
                        f"expected URL under {canonical_base}",
                    )
                    continue
                file_name = url[len(canonical_base) :]
                if (
                    "/" in file_name
                    or file_name not in expected
                    or len(fields) < 3
                ):
                    _diag(
                        diagnostics,
                        "error",
                        "UNKNOWN_LOCAL_REFERENCE",
                        relative,
                        line_number,
                        f"unexpected repository rule reference: {url}",
                    )
                    continue
                references.append((line_number, file_name, fields[2]))
                binding = expected[file_name]
                if fields[0] != binding.type:
                    _diag(
                        diagnostics,
                        "error",
                        "LOCAL_REFERENCE_TYPE",
                        relative,
                        line_number,
                        f"{file_name} must use {binding.type}",
                    )
                if (
                    binding.type == "DOMAIN-SET"
                    and "extended-matching" not in fields[3:]
                ):
                    _diag(
                        diagnostics,
                        "error",
                        "EXTENDED_MATCHING",
                        relative,
                        line_number,
                        f"{file_name} must enable extended-matching",
                    )
                if binding.type == "RULE-SET" and fields[3:]:
                    _diag(
                        diagnostics,
                        "error",
                        "LOCAL_RULESET_OPTIONS",
                        relative,
                        line_number,
                        f"{file_name} must not use outer RULE-SET options",
                    )

        if fields[0] == "DOMAIN-KEYWORD" and rule not in ALLOWED_KEYWORD_RULES:
            _diag(
                diagnostics,
                "error",
                "UNAPPROVED_KEYWORD",
                relative,
                line_number,
                "DOMAIN-KEYWORD is too broad; use DOMAIN, DOMAIN-SUFFIX or DOMAIN-SET",
            )
    by_file: dict[str, list[tuple[int, str]]] = {}
    for line_number, file_name, policy in references:
        by_file.setdefault(file_name, []).append((line_number, policy))

    for binding in bindings:
        found = by_file.get(binding.file, [])
        if not found:
            _diag(
                diagnostics,
                "error",
                "MISSING_REFERENCE",
                relative,
                0,
                f"missing {binding.type} reference for {binding.file}",
            )
            continue
        if len(found) > 1:
            _diag(
                diagnostics,
                "error",
                "DUPLICATE_REFERENCE",
                relative,
                found[1][0],
                f"{binding.file} is referenced {len(found)} times",
            )
        for line_number, policy in found:
            if normalize_policy_name(policy) != binding.policy:
                _diag(
                    diagnostics,
                    "error",
                    "POLICY_MISMATCH",
                    relative,
                    line_number,
                    f"{binding.file} expects {binding.policy}, found {policy}",
                )

    actual_order = [file_name for _, file_name, _ in references]
    expected_order = [binding.file for binding in bindings]
    if actual_order != expected_order:
        _diag(
            diagnostics,
            "error",
            "LOCAL_REFERENCE_ORDER",
            relative,
            references[0][0] if references else 0,
            f"expected local rule order: {', '.join(expected_order)}",
        )

    anchors = [
        ("NTP", lambda value: value == "DEST-PORT,123,DIRECT"),
        ("MTProto", lambda value: value.startswith("PROTOCOL,MTProto,")),
        ("Apple update", lambda value: value.startswith("DOMAIN,gdmf.apple.com,")),
        ("DIRECT CN", lambda value: "direct-cn.conf" in value),
        ("Sukka DOMAIN-SET", lambda value: "/List/domainset/speedtest.conf" in value),
        ("Sukka non_ip", lambda value: "/List/non_ip/cdn.conf" in value),
        ("Sukka IP", lambda value: "/List/ip/stream.conf" in value),
        ("FINAL", lambda value: value.startswith("FINAL,")),
    ]
    positions: list[tuple[str, int]] = []
    for label, predicate in anchors:
        matches = [line_number for line_number, value in rules if predicate(value)]
        if not matches:
            _diag(
                diagnostics,
                "error",
                "MISSING_STAGE",
                relative,
                0,
                f"missing main-rule stage: {label}",
            )
        else:
            positions.append((label, matches[0]))
    for (left_label, left_line), (right_label, right_line) in zip(
        positions, positions[1:]
    ):
        if left_line >= right_line:
            _diag(
                diagnostics,
                "error",
                "STAGE_ORDER",
                relative,
                right_line,
                f"{left_label} must appear before {right_label}",
            )

    # Sukka's DNS-pollution protection relies on every domain and non_ip rule
    # appearing before the first IP rule. Keep this invariant independent of
    # the human-readable section contract so future edits cannot silently
    # reintroduce an early IP-CIDR/IP ruleset.
    ip_phase_started = False
    for line_number, rule in rules:
        fields = [field.strip() for field in rule.split(",")]
        rule_type = fields[0]
        is_ip_rule = (
            "/List/ip/" in rule
            or rule.startswith("RULE-SET,LAN,")
            or rule_type in {"IP-CIDR", "IP-CIDR6", "IP-ASN", "GEOIP"}
        )
        is_domain_or_non_ip = (
            rule_type in {
                "DOMAIN",
                "DOMAIN-SUFFIX",
                "DOMAIN-WILDCARD",
                "DOMAIN-KEYWORD",
                "DOMAIN-SET",
            }
            or "/List/non_ip/" in rule
        )
        if is_ip_rule:
            ip_phase_started = True
        elif ip_phase_started and is_domain_or_non_ip:
            _diag(
                diagnostics,
                "error",
                "SUKKA_PHASE_ORDER",
                relative,
                line_number,
                "domain/domainset/non_ip rule appears after the IP phase started",
            )

    final_rules = [
        (line_number, rule) for line_number, rule in rules if rule.startswith("FINAL,")
    ]
    if len(final_rules) != 1:
        _diag(
            diagnostics,
            "error",
            "FINAL_COUNT",
            relative,
            0,
            f"expected one FINAL rule, found {len(final_rules)}",
        )
    elif final_rules[0] != rules[-1]:
        _diag(
            diagnostics,
            "error",
            "FINAL_POSITION",
            relative,
            final_rules[0][0],
            "FINAL must be the last effective rule",
        )
    elif "dns-failed" not in final_rules[0][1].split(",")[2:]:
        _diag(
            diagnostics,
            "error",
            "FINAL_DNS_FAILED",
            relative,
            final_rules[0][0],
            "FINAL must include dns-failed",
        )

    return len(rules), len(references)


def validate_repository(root: Path, main_override: str | None = None) -> ValidationResult:
    root = root.resolve()
    repository, branch, manifest_main, contract, bindings = load_manifest(root)
    main = main_override or manifest_main
    diagnostics: list[Diagnostic] = []
    active_entries: list[DomainEntry] = []
    active_rule_entries: list[RuleSetEntry] = []

    for binding in bindings:
        if binding.type == "DOMAIN-SET":
            active_entries.extend(
                parse_domain_set(
                    root,
                    binding.file,
                    binding.semantic_policy,
                    archive=False,
                    diagnostics=diagnostics,
                )
            )
        else:
            active_rule_entries.extend(
                parse_rule_set(
                    root,
                    binding.file,
                    binding.semantic_policy,
                    diagnostics=diagnostics,
                )
            )

    archive_entries: list[DomainEntry] = []
    archive_root = root / "archive"
    if archive_root.exists():
        for path in sorted(archive_root.rglob("*.conf")):
            try:
                relative = str(path.relative_to(root))
            except ValueError:
                _diag(
                    diagnostics,
                    "error",
                    "UNSAFE_PATH",
                    str(path),
                    0,
                    "archive path escapes repository root",
                )
                continue
            archive_entries.extend(
                parse_domain_set(
                    root,
                    relative,
                    "ARCHIVE",
                    archive=True,
                    diagnostics=diagnostics,
                )
            )

    semantic_entries = active_entries + rule_set_domain_entries(active_rule_entries)
    detect_active_overlaps(semantic_entries, diagnostics)
    detect_shared_infrastructure(semantic_entries, diagnostics)
    main_rule_count, references = validate_main_rules(
        root,
        main,
        repository,
        branch,
        contract,
        bindings,
        diagnostics,
    )
    return ValidationResult(
        diagnostics=sorted_diagnostics(diagnostics),
        active_entries=active_entries,
        archive_entries=archive_entries,
        bindings=bindings,
        main_rule_count=main_rule_count,
        local_references=references,
        active_rule_entries=active_rule_entries,
    )


def _escape_annotation(value: str, property_value: bool = False) -> str:
    escaped = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    if property_value:
        escaped = escaped.replace(":", "%3A").replace(",", "%2C")
    return escaped


def print_diagnostics(
    diagnostics: Sequence[Diagnostic],
    github_annotations: bool,
    max_diagnostics: int,
) -> None:
    shown = diagnostics[:max_diagnostics]
    for item in shown:
        if github_annotations:
            location = f"file={_escape_annotation(item.path, True)}"
            if item.line > 0:
                location += f",line={item.line}"
            title = _escape_annotation(item.code, True)
            message = _escape_annotation(item.message)
            print(f"::{item.severity} {location},title={title}::{message}")
        else:
            line = f":{item.line}" if item.line > 0 else ""
            print(
                f"{item.severity.upper():7} {item.path}{line} "
                f"[{item.code}] {item.message}"
            )
    omitted = len(diagnostics) - len(shown)
    if omitted > 0:
        print(f"... {omitted} additional diagnostics omitted")


def print_summary(report: dict[str, object]) -> None:
    files = report["files"]
    entries = report["entries"]
    references = report["references"]
    diagnostics = report["diagnostics"]
    assert isinstance(files, dict)
    assert isinstance(entries, dict)
    assert isinstance(references, dict)
    assert isinstance(diagnostics, dict)
    print(f"Active local rule files : {files['active']}")
    print(f"  DOMAIN-SET files      : {files['domain_set']}")
    print(f"  RULE-SET files        : {files['rule_set']}")
    print(f"Active entries          : {entries['active']}")
    print(f"  DOMAIN-SET entries    : {entries['domain_set']}")
    print(f"    exact               : {entries['exact']}")
    print(f"    suffix              : {entries['suffix']}")
    print(f"  RULE-SET entries      : {entries['rule_set']}")
    print(f"Archive files           : {files['archive']}")
    print(f"Archive entries         : {entries['archive']} (not loaded)")
    print(f"Main rules              : {report['main_rules']}")
    print(
        f"Local references        : "
        f"{references['found']}/{references['expected']}"
    )
    print(
        f"Errors / warnings       : "
        f"{diagnostics['errors']} / {diagnostics['warnings']}"
    )
    print(f"Result                  : {'PASS' if report['ok'] else 'FAIL'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=REPOSITORY_ROOT,
        help="repository root (default: inferred from script path)",
    )
    parser.add_argument(
        "--main",
        help="main Surge rule file relative to the repository root",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat warnings as validation failures",
    )
    parser.add_argument(
        "--github-annotations",
        action="store_true",
        help="emit GitHub Actions error and warning annotations",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="write a deterministic JSON validation report",
    )
    parser.add_argument(
        "--max-diagnostics",
        type=int,
        default=100,
        help="maximum diagnostics printed to stdout",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.max_diagnostics < 1:
        print("--max-diagnostics must be positive", file=sys.stderr)
        return 2
    try:
        result = validate_repository(args.root, args.main)
    except ConfigurationError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2

    report = result.report(args.strict)
    print_diagnostics(
        result.diagnostics,
        github_annotations=args.github_annotations,
        max_diagnostics=args.max_diagnostics,
    )
    print_summary(report)
    if args.json_out:
        try:
            args.json_out.parent.mkdir(parents=True, exist_ok=True)
            args.json_out.write_text(
                json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        except OSError as exc:
            print(f"cannot write JSON report: {exc}", file=sys.stderr)
            return 2
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
