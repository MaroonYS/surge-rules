from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_profile_policies  # noqa: E402


class ProfilePolicyTests(unittest.TestCase):
    PROFILE = """\
[Proxy]
Residential = socks5, 192.0.2.1, 1080

[Proxy Group]
PROXY = select, Residential
Finance = select, Residential
"""

    def test_all_referenced_policies_exist(self) -> None:
        rules = """\
[Rule]
DOMAIN-SET,https://example.com/finance.conf,Finance,extended-matching
PROTOCOL,STUN,REJECT
FINAL,PROXY,dns-failed
"""
        missing, unstable, count = check_profile_policies.check(
            self.PROFILE,
            rules,
            ("Finance", "Residential"),
        )
        self.assertEqual([], missing)
        self.assertEqual([], unstable)
        self.assertEqual(3, count)

    def test_missing_policy_is_reported_without_profile_contents(self) -> None:
        rules = """\
[Rule]
DOMAIN,example.com,Missing
FINAL,PROXY
"""
        missing, unstable, count = check_profile_policies.check(
            self.PROFILE,
            rules,
        )
        self.assertEqual(["Missing"], missing)
        self.assertEqual([], unstable)
        self.assertEqual(2, count)

    def test_dynamic_group_is_rejected_when_stability_is_required(self) -> None:
        profile = self.PROFILE + "Dynamic = url-test, Residential\n"
        rules = "[Rule]\nDOMAIN,example.com,Dynamic\n"
        missing, unstable, count = check_profile_policies.check(
            profile,
            rules,
            ("Dynamic",),
        )
        self.assertEqual([], missing)
        self.assertEqual(["Dynamic"], unstable)
        self.assertEqual(1, count)

    def test_policy_group_snippet_completes_profile(self) -> None:
        rules = "[Rule]\nDOMAIN,example.com,Identity\n"
        snippet = 'Identity = select, Residential, "United States", Finance\n'
        missing, unstable, count = check_profile_policies.check(
            self.PROFILE,
            rules,
            ("Identity",),
            (snippet,),
        )
        self.assertEqual([], missing)
        self.assertEqual([], unstable)
        self.assertEqual(1, count)

    def test_select_policy_can_be_required_stable(self) -> None:
        rules = "[Rule]\nDOMAIN,example.com,Apple-Push\n"
        snippet = 'Apple-Push = select, "Hong Kong", "United States", DIRECT\n'
        missing, unstable, count = check_profile_policies.check(
            self.PROFILE,
            rules,
            ("Apple-Push",),
            (snippet,),
        )
        self.assertEqual([], missing)
        self.assertEqual([], unstable)
        self.assertEqual(1, count)

    def test_private_and_bybit_groups_are_manual_and_stable(self) -> None:
        rules = """\
[Rule]
DOMAIN-SET,https://example.com/private.conf,Private,extended-matching
DOMAIN-SET,https://example.com/bybit.conf,Bybit,extended-matching
"""
        snippet = """\
Private = select, \"United States\", DIRECT
Bybit = select, REJECT, DIRECT
"""
        missing, unstable, count = check_profile_policies.check(
            self.PROFILE,
            rules,
            ("Private", "Bybit"),
            (snippet,),
        )
        self.assertEqual([], missing)
        self.assertEqual([], unstable)
        self.assertEqual(2, count)

    def test_logical_rule_policy_is_checked(self) -> None:
        rules = """\
[Rule]
AND,((PROTOCOL,UDP),(DEST-PORT,19302-19309)),GoogleVoice-Media
"""
        missing, unstable, count = check_profile_policies.check(
            self.PROFILE,
            rules,
        )
        self.assertEqual(["GoogleVoice-Media"], missing)
        self.assertEqual([], unstable)
        self.assertEqual(1, count)


if __name__ == "__main__":
    unittest.main()
