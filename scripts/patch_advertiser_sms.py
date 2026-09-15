#!/usr/bin/env python3
"""Read an installed advertiser module and emit a two-rule apply_patch payload.

This tool never writes files, reloads Surge, or changes module enabled state.
Unknown target-rule/whitelist drift is rejected; unrelated upstream edits survive.
"""

import argparse
import difflib
import hashlib
from pathlib import Path
import sys


WHITELIST = {
    "mob.com": (
        "init.sms.mob.com",
        "sdkapi.sms.mob.com",
        "code.sms.mob.com",
    ),
    "jiguang.cn": (
        "smartop-sdkapi.jiguang.cn",
        "sdk.verification.jiguang.cn",
    ),
}


class ModuleDriftError(ValueError):
    """The narrowly reviewed input contract is no longer satisfied."""


def original_rule(suffix):
    return f"DOMAIN-SUFFIX,{suffix},REJECT,extended-matching,pre-matching"


def guarded_rule(suffix):
    leaves = ",".join(
        f"(DOMAIN,{host},extended-matching)" for host in WHITELIST[suffix]
    )
    return (
        f"AND,((DOMAIN-SUFFIX,{suffix},extended-matching),"
        f"(NOT,((OR,({leaves}))))),REJECT,pre-matching"
    )


def transform(data):
    """Return (candidate bytes, already_patched), preserving all other bytes."""
    try:
        source = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ModuleDriftError("Expected a UTF-8 module") from error
    if "\r" in source or "\x00" in source:
        raise ModuleDriftError("Expected LF-only text; refusing newline conversion")
    if not source.endswith("\n"):
        raise ModuleDriftError("Expected final LF; refusing implicit newline changes")
    lines = source.splitlines(keepends=True)
    plain = [line.removesuffix("\n") for line in lines]
    if plain.count("#!name=广告平台拦截器") != 1:
        raise ModuleDriftError("Expected the existing advertiser module identity")
    if plain.count("[Rule]") != 1:
        raise ModuleDriftError("Expected exactly one canonical [Rule] section")
    section = None
    rules = []
    for index, line in enumerate(plain):
        if line.strip().startswith("["):
            section = line.strip()
        elif section == "[Rule]" and line.strip() and not line.lstrip().startswith("#"):
            rules.append((index, line))
    rule_values = [line for _, line in rules]
    for hosts in WHITELIST.values():
        for host in hosts:
            expected = f"DOMAIN,{host},DIRECT,extended-matching"
            host_rules = [line for line in rule_values if line.lstrip().startswith(f"DOMAIN,{host},")]
            if host_rules != [expected]:
                raise ModuleDriftError(f"Exact DIRECT whitelist changed: {host}")
    states = []
    replacements = []
    for suffix in WHITELIST:
        old, new = original_rule(suffix), guarded_rule(suffix)
        candidates = [(i, line) for i, line in rules if f"DOMAIN-SUFFIX,{suffix}," in line]
        if len(candidates) != 1 or candidates[0][1] not in (old, new):
            raise ModuleDriftError(f"Missing, duplicate, or changed suffix guard: {suffix}")
        index, value = candidates[0]
        states.append(value == new)
        replacements.append((index, new))
    if any(states) and not all(states):
        raise ModuleDriftError("Partially patched module; review before continuing")
    if all(states):
        return data, True
    for index, value in replacements:
        lines[index] = value + ("\n" if lines[index].endswith("\n") else "")
    return "".join(lines).encode("utf-8"), False


def make_patch(path, before, after):
    """Emit apply_patch syntax with only changed lines (no unrelated content)."""
    if before == after:
        return ""
    path = str(path)
    if any(char in path for char in "\r\n"):
        raise ModuleDriftError("Unsafe patch target path")
    changes = list(difflib.unified_diff(
        before.decode("utf-8").splitlines(),
        after.decode("utf-8").splitlines(), n=0, lineterm="",
    ))[2:]
    chunks = ["@@" if line.startswith("@@") else line for line in changes]
    return "\n".join(["*** Begin Patch", f"*** Update File: {path}", *chunks, "*** End Patch", ""])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", type=Path, help="Existing advertiser .sgmodule; never written")
    parser.add_argument("--check", action="store_true", help="Exit 0 if patched, 1 if needed, 2 on drift")
    parser.add_argument("--expect-sha256", help="Refuse an input changed since review")
    args = parser.parse_args(argv)
    try:
        if args.module.is_symlink() or not args.module.is_file():
            raise ModuleDriftError("Target must be an existing regular, non-symlink file")
        path = args.module.absolute()
        before = path.read_bytes()
        before_hash = hashlib.sha256(before).hexdigest()
        if args.expect_sha256 and args.expect_sha256.lower() != before_hash:
            raise ModuleDriftError("Input SHA-256 does not match reviewed bytes")
        after, already_patched = transform(before)
        status = "PATCHED" if already_patched else "NEEDS_PATCH"
        print(f"{status} input_sha256={before_hash} candidate_sha256={hashlib.sha256(after).hexdigest()}", file=sys.stderr)
        if args.check:
            return 0 if already_patched else 1
        sys.stdout.write(make_patch(path, before, after))
        return 0
    except (OSError, ModuleDriftError) as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
