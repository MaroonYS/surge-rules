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

    def test_google_voice_media_precedes_global_stun_block(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        control = (
            "/google-voice.conf,GoogleVoice-Control,extended-matching"
        )
        stun_host = (
            "/google-voice-media.conf,GoogleVoice-Media,extended-matching"
        )
        media_rules = [
            "AND,((PROTOCOL,UDP),(DEST-PORT,19302-19309),"
            "(IP-CIDR,74.125.39.0/24,no-resolve)),GoogleVoice-Media",
            "AND,((PROTOCOL,UDP),(DEST-PORT,26500-26501),"
            "(IP-CIDR,74.125.39.0/24,no-resolve)),GoogleVoice-Media",
            "AND,((PROTOCOL,UDP),(DEST-PORT,19302),"
            "(IP-CIDR,74.125.250.129/32,no-resolve)),GoogleVoice-Media",
            "AND,((PROTOCOL,UDP),(DEST-PORT,19302-19309),"
            "(IP-CIDR6,2001:4860:4864:2::/64,no-resolve)),"
            "GoogleVoice-Media",
            "AND,((PROTOCOL,UDP),(DEST-PORT,26500-26501),"
            "(IP-CIDR6,2001:4860:4864:2::/64,no-resolve)),"
            "GoogleVoice-Media",
        ]
        stun = "PROTOCOL,STUN,REJECT"
        ordered = [control, stun_host, *media_rules, stun]
        self.assertEqual(
            sorted(main.index(item) for item in ordered),
            [main.index(item) for item in ordered],
        )
        for media_rule in media_rules:
            with self.subTest(media_rule=media_rule):
                self.assertLess(main.index(media_rule), main.index(stun))
                self.assertTrue(media_rule.endswith("GoogleVoice-Media"))
        self.assertNotIn(",GoogleVoice\n", main)
        control_entries = {
            line
            for line in (ROOT / "google-voice.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        }
        self.assertEqual(
            {".voice.google.com", ".telephony.goog"},
            control_entries,
        )
        media_entries = {
            line
            for line in (ROOT / "google-voice-media.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        }
        self.assertEqual(
            {"stun.l.google.com"},
            media_entries,
        )

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
        entries = {
            line
            for line in (ROOT / "polymarket.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        }
        self.assertEqual(
            {
                ".polymarket.com",
                ".polymarket.us",
                "pmx-prod.us.auth0.com",
                "polymarket-upload.s3.us-east-2.amazonaws.com",
            },
            entries,
        )

    def test_bilibili_uses_early_precise_domain_set(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        entries = {
            line
            for line in (ROOT / "bilibili-direct.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        }
        self.assertEqual(
            {
                ".bilivideo.com",
                ".bilivideo.cn",
                ".bilivideo.net",
            },
            entries,
        )

        bilibili = "/bilibili-direct.conf,DIRECT,extended-matching"
        polymarket = "/polymarket.conf,Res-Frontier,extended-matching"
        reject = "/domainset/reject.conf,REJECT,extended-matching"
        cdn = "/domainset/cdn.conf,PROXY"
        positions = [main.index(item) for item in (bilibili, polymarket, reject, cdn)]
        self.assertEqual(sorted(positions), positions)
        self.assertNotIn("DOMAIN-KEYWORD,bilivideo", main)

    def test_taobao_miniapp_runtime_precedes_shared_reject(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        entries = {
            line
            for line in (ROOT / "taobao-functional.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        }
        self.assertEqual({".hybrid.miniapp.taobao.com"}, entries)
        taobao = "/taobao-functional.conf,DIRECT,extended-matching"
        reject = "/domainset/reject.conf,REJECT,extended-matching"
        domestic = "/non_ip/domestic.conf,DIRECT"
        self.assertLess(main.index(taobao), main.index(reject))
        self.assertLess(main.index(taobao), main.index(domestic))

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
            ".online-metrix.net",
            ".threatmetrix.com",
            ".iovation.com",
            ".iovation.io",
            ".biocatch.com",
            ".fingerprint.com",
            ".fingerprintjs.com",
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

    def test_bybit_documented_api_fallback_is_not_left_to_final(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        entries = {
            line
            for line in (ROOT / "bybit.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        }
        self.assertEqual({".bybit.com", ".bytick.com"}, entries)
        self.assertNotIn(".bybit.com", (ROOT / "crypto.conf").read_text(encoding="utf-8"))
        self.assertLess(
            main.index("/bybit.conf,Crypto,extended-matching"),
            main.index("/crypto.conf,Crypto,extended-matching"),
        )

    def test_apple_push_override_precedes_system(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        push = "/apple-push.conf,Apple-Push,extended-matching"
        system = "RULE-SET,SYSTEM,DIRECT"
        self.assertLess(main.index(push), main.index(system))
        self.assertEqual(
            {
                ".push.apple.com",
                ".courier-push-apple.com.akadns.net",
                ".push-apple.com.akadns.net",
            },
            {
                line
                for line in (ROOT / "apple-push.conf").read_text(
                    encoding="utf-8"
                ).splitlines()
                if line and not line.startswith("#")
            },
        )
        apple_ranges = {
            "17.249.0.0/16",
            "17.252.0.0/16",
            "17.57.144.0/22",
            "17.188.128.0/18",
            "17.188.20.0/23",
            "2620:149:a44::/48",
            "2403:300:a42::/48",
            "2403:300:a51::/48",
            "2a01:b740:a42::/48",
        }
        for network in apple_ranges:
            with self.subTest(network=network):
                self.assertIn(
                    f"(DEST-PORT,5223),(IP-CIDR{'6' if ':' in network else ''},{network},no-resolve)",
                    main,
                )

    def test_telegram_ip_precedes_general_ip_reject(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        telegram = "/ip/telegram.conf,Telegram"
        reject = "/ip/reject.conf,REJECT-DROP"
        self.assertLess(main.index(telegram), main.index(reject))

    def test_identity_policy_group_snippet_is_copy_ready(self) -> None:
        snippet = (
            ROOT / "snippets" / "identity-policy-groups.conf"
        ).read_text(encoding="utf-8")
        self.assertEqual(
            [
                "# Paste this line inside the existing [Proxy Group] section.",
                'Identity = select, Res-Frontier, "United States", Finance',
            ],
            snippet.splitlines(),
        )

    def test_service_policy_group_snippet_is_copy_ready(self) -> None:
        snippet = (
            ROOT / "snippets" / "service-policy-groups.conf"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'GoogleVoice-Control = select, Res-Frontier, "United States"',
            snippet,
        )
        self.assertIn(
            'GoogleVoice-Media = select, DIRECT, "United States"',
            snippet,
        )
        self.assertIn(
            'Apple-Push = fallback, "Hong Kong", "United States", DIRECT, '
            "interval=600, timeout=5",
            snippet,
        )
        ios = (ROOT / "snippets" / "ios-apns-capture.conf").read_text(
            encoding="utf-8"
        )
        self.assertIn("include-all-networks = true", ios)
        self.assertIn("include-apns = true", ios)
        self.assertIn("include-local-networks = false", ios)
        self.assertIn("include-cellular-services = false", ios)

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
