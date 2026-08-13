from __future__ import annotations

import json
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

    def test_financial_and_crypto_runtime_policies_are_fully_static(self) -> None:
        manifest = json.loads(
            (ROOT / "rules-manifest.json").read_text(encoding="utf-8")
        )
        policies = {
            entry["file"]: entry["policy"] for entry in manifest["active"]
        }
        self.assertEqual(
            {
                "direct-cn.conf": "DIRECT",
                "hk-finance.conf": "Hong Kong",
                "hk-finance-context.conf": "Hong Kong",
                "sg-finance.conf": "Singapore",
                "jp-finance.conf": "Japan",
                "kr-finance.conf": "Korea",
                "uk-finance.conf": "United Kingdom",
                "us-residential.conf": "Res-Frontier",
                "finance-context.conf": "Res-Frontier",
                "identity-context.conf": "Res-Frontier",
                "risk-context.conf": "Res-Frontier",
                "bybit.conf": "Bybit",
                "gate.conf": "REJECT",
                "crypto.conf": "Crypto",
                "web3.conf": "Web3",
            },
            {name: policies[name] for name in (
                "direct-cn.conf",
                "hk-finance.conf",
                "hk-finance-context.conf",
                "sg-finance.conf",
                "jp-finance.conf",
                "kr-finance.conf",
                "uk-finance.conf",
                "us-residential.conf",
                "finance-context.conf",
                "identity-context.conf",
                "risk-context.conf",
                "bybit.conf",
                "gate.conf",
                "crypto.conf",
                "web3.conf",
            )},
        )
        self.assertNotIn("Verification", policies.values())

    def test_removing_stun_rule_fails_contract(self) -> None:
        codes = self.validate_modified_main(
            "PROTOCOL,STUN,REJECT\n",
            "",
        )
        self.assertIn("RULE_CONTRACT_MISMATCH", codes)

    def test_ntp_and_google_account_precede_google_voice_and_stun(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        ntp = "DEST-PORT,123,DIRECT"
        x_residential = "/x-residential.conf,Res-Frontier,extended-matching"
        google_account = "/google-account.conf,Res-Frontier,extended-matching"
        voice = "/google-voice.conf,Res-Frontier,extended-matching"
        stun = "PROTOCOL,STUN,REJECT"
        self.assertEqual(
            {
                "accounts.google.com",
                "myaccount.google.com",
                "oauth2.googleapis.com",
                "oauthaccountmanager.googleapis.com",
                "openidconnect.googleapis.com",
                "oauth-redirect.googleusercontent.com",
            },
            {
                line
                for line in (ROOT / "google-account.conf").read_text(
                    encoding="utf-8"
                ).splitlines()
                if line and not line.startswith("#")
            },
        )
        self.assertLess(main.index(ntp), main.index(voice))
        self.assertLess(main.index(ntp), main.index(x_residential))
        self.assertLess(main.index(x_residential), main.index(google_account))
        self.assertLess(main.index(ntp), main.index(google_account))
        self.assertLess(main.index(google_account), main.index(voice))
        self.assertLess(main.index(ntp), main.index(stun))

    def test_x_first_party_surface_uses_early_residential_route(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        entries = {
            line
            for line in (ROOT / "x-residential.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        }
        self.assertEqual(
            {
                ".x.com",
                ".twitter.com",
                ".twimg.com",
                ".t.co",
                ".pscp.tv",
                ".periscope.tv",
            },
            entries,
        )
        x_residential = "/x-residential.conf,Res-Frontier,extended-matching"
        reject = "/domainset/reject.conf,REJECT,extended-matching"
        cdn = "/domainset/cdn.conf,PROXY"
        global_rule = "/non_ip/global.conf,PROXY"
        self.assertLess(main.index(x_residential), main.index(reject))
        self.assertLess(main.index(x_residential), main.index(cdn))
        self.assertLess(main.index(x_residential), main.index(global_rule))

    def test_google_voice_media_precedes_global_stun_block(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        control = (
            "/google-voice.conf,Res-Frontier,extended-matching"
        )
        stun_host = (
            "/google-voice-media.conf,DIRECT,extended-matching"
        )
        media_rule_set = (
            "/google-voice-media-rules.conf,DIRECT"
        )
        media_rules = [
            "AND,((PROTOCOL,UDP),(DEST-PORT,19302-19309),"
            "(IP-CIDR,74.125.39.0/24,no-resolve))",
            "AND,((PROTOCOL,UDP),(DEST-PORT,26500-26501),"
            "(IP-CIDR,74.125.39.0/24,no-resolve))",
            "AND,((PROTOCOL,UDP),(DEST-PORT,19302),"
            "(IP-CIDR,74.125.250.129/32,no-resolve))",
            "AND,((PROTOCOL,UDP),(DEST-PORT,19302-19309),"
            "(IP-CIDR6,2001:4860:4864:2::/64,no-resolve))",
            "AND,((PROTOCOL,UDP),(DEST-PORT,26500-26501),"
            "(IP-CIDR6,2001:4860:4864:2::/64,no-resolve))",
        ]
        stun = "PROTOCOL,STUN,REJECT"
        ordered = [control, stun_host, media_rule_set, stun]
        self.assertEqual(
            sorted(main.index(item) for item in ordered),
            [main.index(item) for item in ordered],
        )
        self.assertNotIn("AND,((PROTOCOL,UDP)", main)
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
            {
                "stun.l.google.com",
                "stun1.l.google.com",
                "stun2.l.google.com",
                "stun3.l.google.com",
                "stun4.l.google.com",
            },
            media_entries,
        )
        remote_media_rules = [
            line
            for line in (ROOT / "google-voice-media-rules.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        ]
        self.assertEqual(media_rules, remote_media_rules)
        self.assertTrue(
            all("GoogleVoice-Media" not in line for line in remote_media_rules)
        )

    def test_changing_private_relay_policy_fails_contract(self) -> None:
        codes = self.validate_modified_main(
            'icloud_private_relay.conf,"United States",extended-matching',
            "icloud_private_relay.conf,DIRECT,extended-matching",
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
        ai = (
            'RULE-SET,https://ruleset.skk.moe/List/non_ip/ai.conf,'
            '"United States"'
        )
        self.assertIn(github, main)
        self.assertLess(main.index(github), main.index(ai))
        self.assertNotIn("DOMAIN-KEYWORD,cr18", main)

    def test_financial_domain_adjustments_are_exact(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
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
        payment_rules = {
            line
            for line in (ROOT / "apple-account-payment-rules.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        }
        self.assertEqual(
            {
                "DOMAIN,account.apple.com",
                "DOMAIN,appleid.cdn-apple.com",
                "DOMAIN,idmsa.apple.com",
                "DOMAIN,gsa.apple.com",
                "DOMAIN,buy.itunes.apple.com",
                "DOMAIN-WILDCARD,*-buy.itunes.apple.com",
            },
            payment_rules,
        )
        payment_ref = "/apple-account-payment-rules.conf,Res-Frontier"
        residential_ref = "/us-residential.conf,Res-Frontier"
        system = "RULE-SET,SYSTEM,DIRECT"
        self.assertLess(main.index(payment_ref), main.index(residential_ref))
        self.assertLess(main.index(payment_ref), main.index(system))

    def test_identity_layers_are_exact_and_precede_crypto(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        expected_identity = {
            ".socure.com",
            ".socure.co",
            ".withpersona.com",
            ".jumio.com",
            ".jumio.ai",
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

        hk_context = '/hk-finance-context.conf,"Hong Kong",extended-matching'
        finance = "/finance-context.conf,Res-Frontier,extended-matching"
        identity = "/identity-context.conf,Res-Frontier,extended-matching"
        risk = "/risk-context.conf,Res-Frontier,extended-matching"
        crypto = "/crypto.conf,Crypto,extended-matching"
        positions = [
            main.index(fragment)
            for fragment in (hk_context, finance, identity, risk, crypto)
        ]
        self.assertEqual(sorted(positions), positions)
        self.assertNotIn("Verification", main)

        hk_context_entries = active_entries("hk-finance-context.conf")
        self.assertTrue(
            {
                ".hsbc.com",
                ".futunn.com",
                ".moomoo.com",
                ".longbridge.com",
            }.issubset(hk_context_entries)
        )
        finance_entries = active_entries("finance-context.conf")
        self.assertTrue(hk_context_entries.isdisjoint(finance_entries))

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
            main.index("/bybit.conf,Bybit,extended-matching"),
            main.index("/crypto.conf,Crypto,extended-matching"),
        )

    def test_gate_current_namespaces_fail_closed_before_crypto(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        gate_entries = {
            line
            for line in (ROOT / "gate.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        }
        crypto_entries = {
            line
            for line in (ROOT / "crypto.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        }
        expected_gate = {".gate.com", ".gate.io", ".gateio.ws"}
        self.assertEqual(expected_gate, gate_entries)
        self.assertTrue(expected_gate.isdisjoint(crypto_entries))
        gate = "/gate.conf,REJECT,extended-matching"
        crypto = "/crypto.conf,Crypto,extended-matching"
        self.assertLess(main.index(gate), main.index(crypto))

    def test_walletconnect_current_namespace_is_in_web3(self) -> None:
        entries = {
            line
            for line in (ROOT / "web3.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        }
        self.assertTrue(
            {
                ".walletconnect.com",
                ".walletconnect.network",
                ".walletconnect.org",
            }.issubset(entries)
        )

    def test_apple_push_override_precedes_system(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        push = '/apple-push.conf,"United States",extended-matching'
        push_rule_set = '/apple-push-rules.conf,"United States"'
        system = "RULE-SET,SYSTEM,DIRECT"
        self.assertLess(main.index(push), main.index(system))
        self.assertLess(main.index(push), main.index(push_rule_set))
        self.assertLess(main.index(push_rule_set), main.index(system))
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
        apple_ranges = [
            "17.249.0.0/16",
            "17.252.0.0/16",
            "17.57.144.0/22",
            "17.188.128.0/18",
            "17.188.20.0/23",
            "17.0.0.0/8",
            "2620:149:a44::/48",
            "2403:300:a42::/48",
            "2403:300:a51::/48",
            "2a01:b740:a42::/48",
        ]
        expected_rules = [
            "AND,((PROTOCOL,TCP),(DEST-PORT,5223),"
            f"(IP-CIDR{'6' if ':' in network else ''},{network},no-resolve))"
            for network in apple_ranges
        ]
        remote_rules = [
            line
            for line in (ROOT / "apple-push-rules.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        ]
        self.assertEqual(expected_rules, remote_rules)
        self.assertNotIn("AND,((PROTOCOL,TCP),(DEST-PORT,5223)", main)
        self.assertTrue(all("Apple-Push" not in line for line in remote_rules))

    def test_telegram_ip_precedes_general_ip_reject(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        telegram = "/ip/telegram.conf,Singapore"
        reject = "/ip/reject.conf,REJECT-DROP"
        self.assertLess(main.index(telegram), main.index(reject))

    def test_telegram_non_ip_precedes_shared_reject_stack(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        telegram = "/non_ip/telegram.conf,Singapore"
        reject = "/non_ip/reject-drop.conf,REJECT-DROP"
        self.assertLess(main.index(telegram), main.index(reject))

    def test_only_current_ios_mode_snippets_remain_copy_ready(self) -> None:
        self.assertFalse(
            (ROOT / "snippets" / "identity-policy-groups.conf").exists()
        )
        self.assertFalse(
            (ROOT / "snippets" / "service-policy-groups.conf").exists()
        )
        apns = (ROOT / "snippets" / "ios-apns-capture.conf").read_text(
            encoding="utf-8"
        )
        continuity = (ROOT / "snippets" / "ios-continuity.conf").read_text(
            encoding="utf-8"
        )
        self.assertIn("include-all-networks = true", apns)
        self.assertIn("include-apns = true", apns)
        self.assertIn("include-local-networks = false", apns)
        self.assertIn("include-cellular-services = false", apns)
        self.assertIn("include-all-networks = false", continuity)
        self.assertIn("include-apns = false", continuity)
        self.assertIn("include-local-networks = false", continuity)
        self.assertIn("include-cellular-services = false", continuity)

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
