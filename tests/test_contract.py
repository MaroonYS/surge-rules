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
            "/non_ip/reject-drop.conf,REJECT-DROP",
            "/domainset/reject.conf,REJECT,extended-matching",
            "/adblock4limbo-supplement.conf,REJECT,extended-matching",
            "/non_ip/reject.conf,REJECT,extended-matching",
            "/non_ip/reject-no-drop.conf,REJECT-NO-DROP,extended-matching",
        ]
        positions = [main.index(fragment) for fragment in expected]
        self.assertEqual(sorted(positions), positions)

    def test_service_specific_rules_are_precise_and_ordered(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        github = "DOMAIN,api.github.com,PROXY,extended-matching"
        ai = "RULE-SET,https://ruleset.skk.moe/List/non_ip/ai.conf,AIGC"
        self.assertIn(github, main)
        self.assertLess(main.index(github), main.index(ai))
        self.assertNotIn("DOMAIN-KEYWORD,cr18", main)

    def test_financial_domain_adjustments_are_exact(self) -> None:
        direct_cn = set(
            (ROOT / "direct-cn.conf").read_text(encoding="utf-8").splitlines()
        )
        us_residential = set(
            (ROOT / "us-residential.conf").read_text(encoding="utf-8").splitlines()
        )
        self.assertNotIn(".icbc.com", direct_cn)
        self.assertIn(".icbc.com.cn", direct_cn)
        self.assertTrue(
            {
                ".apexclearing.com",
                ".earlywarning.com",
                ".id.me",
                ".login.gov",
            }.issubset(us_residential)
        )

    def test_identity_layers_are_exact_and_precede_crypto(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        expected_identity = {
            ".socure.com",
            ".socure.co",
            ".withpersona.com",
            ".persona.com",
            ".jumio.com",
            ".netverify.com",
            ".onfido.com",
            ".trulioo.com",
            ".idology.com",
            ".au10tix.com",
            ".alloy.com",
            ".sentilink.com",
            ".middesk.com",
            ".prove.com",
            ".proveidentity.com",
            ".miteksystems.com",
            ".mitekcloud.com",
            ".veriff.com",
            ".sumsub.com",
            ".vouched.id",
            ".ekata.com",
        }
        expected_risk = {
            ".sardine.ai",
            ".sift.com",
            ".siftcdn.net",
            ".online-metrix.net",
            ".threatmetrix.com",
            ".iovation.com",
            ".iovation.io",
            ".biocatch.com",
            ".fingerprint.com",
            ".fingerprintjs.com",
            ".riskified.com",
            ".forter.com",
            ".castle.io",
            ".seon.io",
            ".incognia.com",
        }

        def active_entries(name: str) -> set[str]:
            return {
                line
                for line in (ROOT / name).read_text(encoding="utf-8").splitlines()
                if line and not line.startswith("#")
            }

        self.assertEqual(expected_identity, active_entries("identity-context.conf"))
        self.assertEqual(expected_risk, active_entries("risk-context.conf"))

        finance = "/finance-context.conf,Finance,extended-matching"
        identity = "/identity-context.conf,Identity,extended-matching"
        risk = "/risk-context.conf,Identity,extended-matching"
        crypto = "/crypto.conf,Crypto,extended-matching"
        positions = [main.index(fragment) for fragment in (finance, identity, risk, crypto)]
        self.assertEqual(sorted(positions), positions)

    def test_identity_policy_group_snippet_is_copy_ready(self) -> None:
        snippet = (
            ROOT / "snippets" / "identity-policy-groups.conf"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'US-FINANCE = select, Res-Frontier, "United States"',
            snippet,
        )
        self.assertIn(
            "Identity = select, Res-Frontier, US-FINANCE, Finance",
            snippet,
        )

    def test_reject_drop_does_not_use_pre_matching(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        reject_drop = next(
            line
            for line in main.splitlines()
            if "/non_ip/reject-drop.conf" in line and not line.startswith("#")
        )
        self.assertEqual(
            "RULE-SET,https://ruleset.skk.moe/List/non_ip/"
            "reject-drop.conf,REJECT-DROP",
            reject_drop,
        )

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
