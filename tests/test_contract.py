from __future__ import annotations

import json
import re
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

    def test_current_documentation_tracks_manifest_inventory(self) -> None:
        manifest = json.loads(
            (ROOT / "rules-manifest.json").read_text(encoding="utf-8")
        )
        active = manifest["active"]
        domain_sets = [
            entry for entry in active if entry.get("type", "DOMAIN-SET") == "DOMAIN-SET"
        ]
        rule_sets = [entry for entry in active if entry.get("type") == "RULE-SET"]
        total_entries = 0
        domain_entries = 0
        rule_entries = 0
        for entry in active:
            count = sum(
                1
                for line in (ROOT / entry["file"]).read_text(
                    encoding="utf-8"
                ).splitlines()
                if line and not line.startswith("#")
            )
            total_entries += count
            if entry.get("type", "DOMAIN-SET") == "DOMAIN-SET":
                domain_entries += count
            else:
                rule_entries += count

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        matrix = (ROOT / "docs" / "requirements-matrix.md").read_text(
            encoding="utf-8"
        )
        parity = (ROOT / "docs" / "source-parity.md").read_text(encoding="utf-8")
        self.assertIn(
            f"通过 {len(active)} 个远程本仓库规则文件"
            f"（{len(domain_sets)} 个 `DOMAIN-SET`、{len(rule_sets)} 个 `RULE-SET`）",
            readme,
        )
        self.assertIn(f"确认 {len(active)} 个本仓库规则文件均成功加载", readme)
        self.assertIn(
            f"| 当前 DOMAIN-SET 条目 | {domain_entries} | "
            f"{len(domain_sets)} 个本仓库 `DOMAIN-SET` |",
            parity,
        )
        self.assertIn(
            f"| 当前 RULE-SET 条目 | {rule_entries} | "
            f"{len(rule_sets)} 个无策略列 `RULE-SET` |",
            parity,
        )
        self.assertIn(
            f"| 当前活动条目 | {total_entries} | {len(active)} 个本仓库活动文件 |",
            parity,
        )
        for entry in active:
            marker = f"`{entry['file']}`"
            self.assertIn(marker, readme)
            self.assertIn(marker, matrix)

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
                "bybit.conf": "Crypto",
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

    def test_watchos_update_and_validation_chain_is_exact_direct_and_early(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        ntp = "DEST-PORT,123,DIRECT"
        watchos_rules = [
            "DOMAIN,appldnld.apple.com,DIRECT,extended-matching",
            "DOMAIN,gdmf.apple.com,DIRECT,extended-matching",
            "DOMAIN,gg.apple.com,DIRECT,extended-matching",
            "DOMAIN,gs.apple.com,DIRECT,extended-matching",
            "DOMAIN,mesu.apple.com,DIRECT,extended-matching",
            "DOMAIN,bpapi.apple.com,DIRECT,extended-matching",
            "DOMAIN,certs.apple.com,DIRECT,extended-matching",
            "DOMAIN,crl.apple.com,DIRECT,extended-matching",
            "DOMAIN,crl3.digicert.com,DIRECT,extended-matching",
            "DOMAIN,crl4.digicert.com,DIRECT,extended-matching",
            "DOMAIN,ocsp.apple.com,DIRECT,extended-matching",
            "DOMAIN,ocsp.digicert.com,DIRECT,extended-matching",
            "DOMAIN,ocsp2.apple.com,DIRECT,extended-matching",
            "DOMAIN,valid.apple.com,DIRECT,extended-matching",
            "DOMAIN,ocsp.digicert.cn,DIRECT,extended-matching",
        ]
        github_rules = [
            'DOMAIN,github.com,"Hong Kong",extended-matching',
            'DOMAIN-SUFFIX,githubusercontent.com,"Hong Kong",extended-matching',
        ]
        x_residential = "/x-residential.conf,Res-Frontier,extended-matching"
        protected_rules = watchos_rules + github_rules
        positions = [main.index(rule) for rule in protected_rules]

        self.assertEqual(sorted(positions), positions)
        self.assertTrue(all(main.count(rule) == 1 for rule in protected_rules))
        self.assertTrue(all(main.index(ntp) < position for position in positions))
        self.assertTrue(all(position < main.index(x_residential) for position in positions))
        self.assertNotIn("DOMAIN-SUFFIX,apple.com,DIRECT", main)
        self.assertNotIn("DOMAIN-KEYWORD,apple,DIRECT", main)

    def test_weatherkit_country_fallback_is_coordinate_scoped(self) -> None:
        snippet = (
            ROOT / "snippets" / "weatherkit-country-fallback.conf"
        ).read_text(encoding="utf-8")
        rule = next(
            line
            for line in snippet.splitlines()
            if line and not line.startswith(("#", "["))
        )
        pattern, replacement, mode = rule.split()
        replacement = re.sub(r"\$(\d+)", r"\\g<\1>", replacement)
        missing_country = (
            "https://weatherkit.apple.com/api/v2/weather/zh-Hans-US/"
            "22.544577/113.94114?timezone=Asia/Shanghai&dataSets=airQuality"
        )
        existing_country = missing_country + "&country=CN"
        other_location = missing_country.replace("22.544577/113.94114", "40.7/-74.0")

        self.assertEqual("header", mode)
        self.assertRegex(missing_country, pattern)
        self.assertIn("country=CN", re.sub(pattern, replacement, missing_country))
        self.assertNotRegex(existing_country, pattern)
        self.assertNotRegex(other_location, pattern)

    def test_icloud_layers_are_complete_and_ordered_before_reject(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        account = (
            "RULE-SET,https://raw.githubusercontent.com/MaroonYS/surge-rules/main/"
            "apple-account-payment-rules.conf,Res-Frontier"
        )
        relay = (
            "DOMAIN-SET,https://ruleset.skk.moe/List/domainset/"
            'icloud_private_relay.conf,"United States",extended-matching'
        )
        sync = (
            "DOMAIN-SET,https://raw.githubusercontent.com/MaroonYS/surge-rules/main/"
            "icloud-sync.conf,DIRECT,extended-matching"
        )
        cdn = "DOMAIN-SUFFIX,cdn-apple.com,DIRECT,extended-matching"
        icloud = "DOMAIN-SUFFIX,icloud.com,DIRECT,extended-matching"
        reject = "DOMAIN-SET,https://ruleset.skk.moe/List/domainset/reject.conf,REJECT"
        domains = {
            line
            for line in (ROOT / "icloud-sync.conf").read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")
        }
        required = {
            ".apple-cloudkit.com",
            ".apple-livephotoskit.com",
            ".apzones.com",
            ".gc.apple.com",
            ".icloud.com.cn",
            ".icloud.apple.com",
            ".icloud-content.com",
            ".iwork.apple.com",
            ".apple-dns.net",
        }

        self.assertEqual(required, domains)
        self.assertLess(main.index(account), main.index(relay))
        self.assertLess(main.index(relay), main.index(cdn))
        self.assertLess(main.index(cdn), main.index(icloud))
        self.assertLess(main.index(icloud), main.index(sync))
        self.assertLess(main.index(sync), main.index(reject))
        self.assertEqual(1, main.count(account))
        self.assertEqual(1, main.count(sync))

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
        global_rule = '/non_ip/global.conf,"United States"'
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
        self.assertIn(
            "/polymarket-global.conf,Res-Frontier,extended-matching",
            main,
        )
        self.assertIn("/polymarket.conf,Res-Frontier,extended-matching", main)
        self.assertNotIn("DOMAIN-KEYWORD,polymarket", main)
        global_entries = {
            line
            for line in (ROOT / "polymarket-global.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        }
        us_entries = {
            line
            for line in (ROOT / "polymarket.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        }
        self.assertEqual(
            {
                ".polymarket.com",
                "pmx-prod.us.auth0.com",
                "polymarket-upload.s3.us-east-2.amazonaws.com",
            },
            global_entries,
        )
        self.assertEqual({".polymarket.us"}, us_entries)

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
        polymarket_global = (
            "/polymarket-global.conf,Res-Frontier,extended-matching"
        )
        polymarket_us = "/polymarket.conf,Res-Frontier,extended-matching"
        reject = "/domainset/reject.conf,REJECT,extended-matching"
        cdn = "/domainset/cdn.conf,PROXY"
        positions = [
            main.index(item)
            for item in (bilibili, polymarket_global, polymarket_us, reject, cdn)
        ]
        self.assertEqual(sorted(positions), positions)
        self.assertNotIn("DOMAIN-KEYWORD,bilivideo", main)

    def test_iphone_brawl_direct_exceptions_precede_shared_rules(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        brawl = "DOMAIN-SUFFIX,brawlstarsgame.com,DIRECT"
        collector = "DOMAIN,collector.snowplow.supercell.com,DIRECT"
        bilibili = "/bilibili-direct.conf,DIRECT,extended-matching"
        self.assertLess(main.index(brawl), main.index(collector))
        self.assertLess(main.index(collector), main.index(bilibili))

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
        nano_emby = "DOMAIN,nano.cr18.eu.org,Singapore"
        upstream_emby = (
            "RULE-SET,https://raw.githubusercontent.com/ddgksf2013/"
            "Filter/master/Emby.list,Singapore"
        )
        github = "DOMAIN,api.github.com,PROXY,extended-matching"
        ai = (
            'RULE-SET,https://ruleset.skk.moe/List/non_ip/ai.conf,'
            '"United States"'
        )
        global_rule = (
            "RULE-SET,https://ruleset.skk.moe/List/non_ip/global.conf,"
        )
        self.assertEqual(1, main.count(nano_emby))
        self.assertLess(main.index(nano_emby), main.index(upstream_emby))
        self.assertLess(main.index(nano_emby), main.index(global_rule))
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
                ".myequifax.com",
                "capitalone.md-apis.medallia.com",
                "capitalone-resources.digital-cloud.medallia.com",
            }.issubset(us_residential)
        )
        self.assertNotIn(".medallia.com", us_residential)
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
                ".futuhk8.com",
                ".futuhongkong.com",
                ".futunh.com",
            }.issubset(hk_context_entries)
        )
        self.assertTrue(
            {
                ".futu.com",
                ".futu0.com",
                ".futu1.com",
                ".futu2.com",
                ".futu3.com",
                ".futu4.com",
                ".futu6.com",
                ".futu7.com",
                ".futu9.com",
                ".futuinc.com",
                ".futuau.com",
                ".moomootrustee.com",
            }.isdisjoint(hk_context_entries)
        )
        self.assertIn(
            ".moomootrustee.com",
            active_entries("sg-finance.conf"),
        )
        self.assertIn(
            '/hk-finance.conf,"Hong Kong",extended-matching,'
            "update-interval=3600",
            main,
        )
        self.assertIn(
            '/hk-finance-context.conf,"Hong Kong",extended-matching,'
            "update-interval=3600",
            main,
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
        self.assertEqual(
            {
                ".byabcde.com",
                ".byapis.com",
                ".byapps.net",
                ".bybdc6.com",
                ".bybit-aws.com",
                ".bybit-global.com",
                ".bybit.biz",
                ".bybit.cloud",
                ".bybit.com",
                ".bybitglobal.com",
                ".bycbe.com",
                ".bycsi.com",
                ".byd3c3.com",
                ".bymj.io",
                ".bytick.com",
            },
            entries,
        )
        self.assertNotIn(".bybit.com", (ROOT / "crypto.conf").read_text(encoding="utf-8"))
        self.assertLess(
            main.index("/bybit.conf,Crypto,extended-matching"),
            main.index("/crypto.conf,Crypto,extended-matching"),
        )

    def test_unused_gate_override_is_not_reintroduced(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        manifest = (ROOT / "rules-manifest.json").read_text(encoding="utf-8")
        contract = (ROOT / "rules-contract.json").read_text(encoding="utf-8")
        self.assertFalse((ROOT / "gate.conf").exists())
        self.assertNotIn("/gate.conf", main)
        self.assertNotIn('"file": "gate.conf"', manifest)
        self.assertNotIn("/gate.conf", contract)
        crypto_entries = {
            line
            for line in (ROOT / "crypto.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith("#")
        }
        self.assertTrue(
            {
                ".gate.com",
                ".gate.io",
                ".gateio.ws",
                ".gatedata.org",
                ".gateimg.com",
                ".gateio.live",
                ".gateio.services",
            }.isdisjoint(crypto_entries)
        )

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
        complete = (ROOT / "snippets" / "ios-complete-routing.conf").read_text(
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
        self.assertIn("include-all-networks = true", complete)
        self.assertIn("include-apns = false", complete)
        self.assertIn("include-local-networks = false", complete)
        self.assertIn("include-cellular-services = false", complete)

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

    def test_chatgpt_voice_ip_rules_precede_global_stun_rejection(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        google_voice = "/google-voice-media-rules.conf,DIRECT"
        ai = '/List/ip/ai.conf,"United States"'
        stun = "PROTOCOL,STUN,REJECT"
        positions = [main.index(item) for item in (google_voice, ai, stun)]
        self.assertEqual(sorted(positions), positions)


if __name__ == "__main__":
    unittest.main()
