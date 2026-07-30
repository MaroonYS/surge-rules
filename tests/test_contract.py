from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate  # noqa: E402


class RuleContractTests(unittest.TestCase):
    def validate_modified_main(self, old: str, new: str) -> set[str]:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "repo"
            shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns(".git"))
            main_path = copied / "surge-main.conf"
            original = main_path.read_text(encoding="utf-8")
            self.assertIn(old, original)
            main_path.write_text(
                original.replace(old, new, 1),
                encoding="utf-8",
            )
            result = validate.validate_repository(copied)
        return {item.code for item in result.diagnostics}

    def test_removing_stun_rule_fails_contract(self) -> None:
        codes = self.validate_modified_main(
            "PROTOCOL,STUN,REJECT\n",
            "",
        )
        self.assertIn("RULE_CONTRACT_MISMATCH", codes)

    def test_changing_private_relay_policy_fails_contract(self) -> None:
        codes = self.validate_modified_main(
            "icloud_private_relay.conf,Apple,extended-matching",
            "icloud_private_relay.conf,AIGC,extended-matching",
        )
        self.assertIn("RULE_CONTRACT_MISMATCH", codes)

    def test_deprecated_and_empty_upstreams_are_not_reintroduced(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        self.assertNotIn("/non_ip/apple_cdn.conf", main)
        self.assertNotIn("/ip/stream_us.conf", main)
        self.assertNotIn("/non_ip/stream_us.conf", main)

    def test_polymarket_uses_precise_domain_set(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        self.assertIn("/polymarket.conf,Res-Frontier,extended-matching", main)
        self.assertNotIn("DOMAIN-KEYWORD,polymarket", main)

    def test_sukkaw_reject_stack_uses_documented_order(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        expected = [
            "/non_ip/reject-drop.conf,REJECT-DROP,pre-matching",
            "/domainset/reject.conf,REJECT,extended-matching",
            "/adblock4limbo-supplement.conf,REJECT,extended-matching",
            "/non_ip/reject.conf,REJECT,extended-matching",
            "/non_ip/reject-no-drop.conf,REJECT-NO-DROP,extended-matching",
        ]
        positions = [main.index(fragment) for fragment in expected]
        self.assertEqual(sorted(positions), positions)

    def test_sukkaw_ip_resolution_semantics_are_not_overridden(self) -> None:
        lines = (ROOT / "surge-main.conf").read_text(encoding="utf-8").splitlines()
        ip_rules = [
            line
            for line in lines
            if "ruleset.skk.moe/List/ip/" in line and not line.startswith("#")
        ]
        self.assertTrue(ip_rules)
        self.assertTrue(all(",no-resolve" not in line for line in ip_rules))


if __name__ == "__main__":
    unittest.main()
