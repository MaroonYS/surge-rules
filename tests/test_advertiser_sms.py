"""Offline SMS guard semantics and byte-preserving patcher regressions."""

import contextlib
import hashlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "patch_advertiser_sms.py"
SPEC = importlib.util.spec_from_file_location("patch_advertiser_sms", SCRIPT)
patcher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(patcher)

# Independent review contract: do not derive this golden inventory from the
# patcher, or adding a production exception would also enlarge every fixture.
EXPECTED_WHITELIST = {
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


def fixture():
    lines = ["#!name=广告平台拦截器", "#!date=upstream-current", "", "[Rule]", "DOMAIN,keep.example,REJECT"]
    for suffix, hosts in patcher.WHITELIST.items():
        lines.extend(f"DOMAIN,{host},DIRECT,extended-matching" for host in hosts)
        lines.append(patcher.original_rule(suffix))
    lines += [
        "DOMAIN-SUFFIX,jpush.cn,REJECT,extended-matching,pre-matching",
        "DOMAIN-SUFFIX,jpush.io,REJECT,extended-matching,pre-matching",
        "", "[URL Rewrite]", "^https://keep.example/ - reject",
        "", "[MITM]", "hostname = %APPEND% keep.example", "",
    ]
    return "\n".join(lines).encode("utf-8")


def split_top(value):
    fields, start, depth = [], 0, 0
    for offset, char in enumerate(value):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise ValueError("Unbalanced rule")
        elif char == "," and depth == 0:
            fields.append(value[start:offset])
            start = offset + 1
    if depth:
        raise ValueError("Unbalanced rule")
    fields.append(value[start:])
    return fields


def unwrap(value):
    if not value.startswith("(") or not value.endswith(")"):
        raise ValueError("Expected parentheses")
    return value[1:-1]


def matches(fields, host):
    kind, value = fields[:2]
    host = host.lower()
    if kind == "DOMAIN":
        return host == value
    if kind == "DOMAIN-SUFFIX":
        return host == value or host.endswith("." + value)
    children = [split_top(unwrap(child)) for child in split_top(unwrap(value))]
    results = [matches(child, host) for child in children]
    if kind == "AND":
        return all(results)
    if kind == "OR":
        return any(results)
    if kind == "NOT" and len(results) == 1:
        return not results[0]
    raise ValueError("Unsupported rule")


class AdvertiserSmsTests(unittest.TestCase):
    def assert_whitelist_contract(self, actual):
        self.assertEqual(EXPECTED_WHITELIST, actual)
        self.assertEqual(2, len(actual))
        self.assertEqual(5, sum(len(hosts) for hosts in actual.values()))

    def test_whitelist_is_exactly_the_five_reviewed_hosts(self):
        self.assert_whitelist_contract(patcher.WHITELIST)

    def test_whitelist_contract_rejects_a_sixth_host(self):
        mutated = dict(patcher.WHITELIST)
        mutated["mob.com"] += ("new.sms.mob.com",)
        with self.assertRaises(AssertionError):
            self.assert_whitelist_contract(mutated)

    def test_only_two_lines_change_and_all_other_bytes_survive(self):
        before = fixture()
        after, patched = patcher.transform(before)
        self.assertFalse(patched)
        changed = [(a, b) for a, b in zip(before.splitlines(keepends=True), after.splitlines(keepends=True)) if a != b]
        self.assertEqual(len(changed), 2)
        expected = before
        for suffix in patcher.WHITELIST:
            expected = expected.replace(patcher.original_rule(suffix).encode(), patcher.guarded_rule(suffix).encode())
        self.assertEqual(after, expected)

    def test_idempotent(self):
        after, _ = patcher.transform(fixture())
        self.assertEqual(patcher.transform(after), (after, True))
        self.assertEqual(patcher.make_patch("example.sgmodule", after, after), "")

    def test_five_exact_hosts_are_excluded_but_not_their_subdomains(self):
        for suffix, hosts in patcher.WHITELIST.items():
            fields = split_top(patcher.guarded_rule(suffix))
            self.assertEqual(fields[2:], ["REJECT", "pre-matching"])
            for host in hosts:
                with self.subTest(host=host):
                    self.assertFalse(matches(fields, host))
                    self.assertFalse(matches(fields, host.upper()))
                    self.assertTrue(matches(fields, "sub." + host))
                    self.assertTrue(matches(fields, "not-" + host))

    def test_suffix_roots_and_unlisted_hosts_stay_blocked(self):
        for suffix in patcher.WHITELIST:
            fields = split_top(patcher.guarded_rule(suffix))
            for host in [suffix, "ads." + suffix, "sdk." + suffix, "other.sms." + suffix]:
                self.assertTrue(matches(fields, host))
            for host in ["example.com", "not" + suffix, suffix + ".example.com"]:
                self.assertFalse(matches(fields, host))

    def test_every_domain_leaf_keeps_extended_matching(self):
        def walk(fields):
            if fields[0] in {"DOMAIN", "DOMAIN-SUFFIX"}:
                self.assertEqual(fields[2:], ["extended-matching"])
            else:
                for child in split_top(unwrap(fields[1])):
                    walk(split_top(unwrap(child)))
        for suffix in patcher.WHITELIST:
            walk(split_top(patcher.guarded_rule(suffix)))

    def test_refuses_target_rule_drift(self):
        source = fixture()
        old = patcher.original_rule("mob.com").encode()
        for changed in [source.replace(old, b""), source.replace(old, old + b"\n" + old), source.replace(old, old.replace(b"REJECT,", b"REJECT-NO-DROP,")), source.replace(old, patcher.guarded_rule("mob.com").encode())]:
            with self.subTest(changed=changed[:20]):
                with self.assertRaises(patcher.ModuleDriftError):
                    patcher.transform(changed)

    def test_refuses_missing_changed_or_duplicate_whitelist(self):
        source = fixture()
        target = b"DOMAIN,init.sms.mob.com,DIRECT,extended-matching"
        for changed in [source.replace(target, b""), source.replace(target, target.replace(b"DIRECT", b"REJECT")), source.replace(target, target + b"\n" + target)]:
            with self.assertRaises(patcher.ModuleDriftError):
                patcher.transform(changed)

    def test_refuses_wrong_identity_section_encoding_or_newlines(self):
        source = fixture()
        for changed in [source.replace("广告平台拦截器".encode(), b"Other"), source.replace(b"[Rule]", b"[Host]"), source.replace(b"[Rule]", b"[Rule]\n[Rule]"), source.replace(b"\n", b"\r\n"), source.rstrip(b"\n"), b"\xff", source + b"\x00"]:
            with self.assertRaises(patcher.ModuleDriftError):
                patcher.transform(changed)

    def test_unrelated_upstream_changes_are_preserved(self):
        source = fixture().replace(b"#!date=upstream-current", b"#!date=upstream-newer").replace(b"[MITM]", b"# new upstream comment\n[MITM]")
        after, _ = patcher.transform(source)
        self.assertIn(b"#!date=upstream-newer", after)
        self.assertIn(b"# new upstream comment\n[MITM]", after)

    def test_patch_contains_only_two_replacements(self):
        before = fixture()
        after, _ = patcher.transform(before)
        payload = patcher.make_patch("/tmp/module with spaces.sgmodule", before, after)
        self.assertTrue(payload.startswith("*** Begin Patch\n*** Update File: /tmp/module with spaces.sgmodule\n"))
        self.assertEqual(sum(line.startswith("-") for line in payload.splitlines()), 2)
        self.assertEqual(sum(line.startswith("+") for line in payload.splitlines()), 2)
        self.assertNotIn("[MITM]", payload)
        with self.assertRaises(patcher.ModuleDriftError):
            patcher.make_patch("module\n*** Delete File: victim", before, after)

    def test_cli_never_writes_and_check_distinguishes_states(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "module.sgmodule"
            before = fixture()
            path.write_bytes(before)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                self.assertEqual(patcher.main([str(path)]), 0)
                self.assertEqual(patcher.main([str(path), "--check"]), 1)
                self.assertEqual(patcher.main([str(path), "--expect-sha256", "0" * 64]), 2)
                self.assertEqual(patcher.main([str(path), "--expect-sha256", hashlib.sha256(before).hexdigest()]), 0)
            self.assertEqual(path.read_bytes(), before)
            self.assertIn("*** Begin Patch", out.getvalue())
            self.assertIn("NEEDS_PATCH", err.getvalue())
            path.write_bytes(patcher.transform(before)[0])
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(patcher.main([str(path), "--check"]), 0)
            link = Path(folder) / "symlink.sgmodule"
            link.symlink_to(path)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(patcher.main([str(link)]), 2)


if __name__ == "__main__":
    unittest.main()
