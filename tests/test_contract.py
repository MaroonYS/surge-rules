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
    def active_entries(self, name: str) -> set[str]:
        return {
            line
            for line in (ROOT / name).read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")
        }

    def validate_modified_main(self, old: str, new: str) -> set[str]:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "repo"
            shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns(".git"))
            main_path = copied / "surge-main.conf"
            original = main_path.read_text(encoding="utf-8")
            self.assertIn(old, original)
            main_path.write_text(original.replace(old, new, 1), encoding="utf-8")
            result = validate.validate_repository(copied)
        return {item.code for item in result.diagnostics}

    def test_current_documentation_tracks_manifest_inventory(self) -> None:
        manifest = json.loads(
            (ROOT / "rules-manifest.json").read_text(encoding="utf-8")
        )
        active = manifest["active"]
        total_entries = sum(len(self.active_entries(item["file"])) for item in active)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        matrix = (ROOT / "docs" / "requirements-matrix.md").read_text(
            encoding="utf-8"
        )
        parity = (ROOT / "docs" / "source-parity.md").read_text(encoding="utf-8")

        self.assertEqual(12, len(active))
        self.assertIn("12 个远程本仓库 `DOMAIN-SET`", readme)
        self.assertIn("确认 12 个本仓库规则文件均成功加载", readme)
        self.assertIn(
            f"| 当前 DOMAIN-SET 条目 | {total_entries} | 12 个本仓库 `DOMAIN-SET` |",
            parity,
        )
        for item in active:
            marker = f"`{item['file']}`"
            self.assertIn(marker, readme)
            self.assertIn(marker, matrix)

    def test_contract_has_five_contiguous_stages(self) -> None:
        contract = json.loads(
            (ROOT / "rules-contract.json").read_text(encoding="utf-8")
        )
        sections = contract["sections"]
        self.assertEqual([1, 2, 3, 4, 5], [item["number"] for item in sections])
        self.assertIn("DOMAIN-SET", sections[2]["title"])
        self.assertIn("non_ip", sections[3]["title"])
        self.assertIn("IP", sections[4]["title"])
        self.assertTrue(sections[4]["rules"][-1].startswith("FINAL,"))

    def test_contract_detects_mutation(self) -> None:
        codes = self.validate_modified_main(
            "DEST-PORT,123,DIRECT\n",
            "DEST-PORT,123,PROXY\n",
        )
        self.assertIn("RULE_CONTRACT_MISMATCH", codes)

    def test_sukka_phase_order_is_strict(self) -> None:
        rules = [
            line
            for line in (ROOT / "surge-main.conf").read_text(
                encoding="utf-8"
            ).splitlines()
            if line and not line.startswith(("#", "["))
        ]
        domain_indexes = [
            index
            for index, rule in enumerate(rules)
            if rule.startswith(("DOMAIN,", "DOMAIN-SUFFIX,", "DOMAIN-WILDCARD,", "DOMAIN-SET,"))
        ]
        non_ip_indexes = [
            index for index, rule in enumerate(rules) if "/List/non_ip/" in rule
        ]
        ip_indexes = [
            index
            for index, rule in enumerate(rules)
            if "/List/ip/" in rule or rule.startswith("RULE-SET,LAN,")
        ]
        final_index = next(index for index, rule in enumerate(rules) if rule.startswith("FINAL,"))

        self.assertTrue(domain_indexes and non_ip_indexes and ip_indexes)
        self.assertLess(max(domain_indexes), min(non_ip_indexes))
        self.assertLess(max(non_ip_indexes), min(ip_indexes))
        self.assertLess(max(ip_indexes), final_index)
        self.assertEqual(final_index, len(rules) - 1)

    def test_only_supported_sukka_list_formats_are_used(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        self.assertNotIn("ruleset.skk.moe/Source/", main)
        self.assertNotIn("ruleset.skk.moe/Clash/", main)
        self.assertNotIn("ruleset.skk.moe/sing-box/", main)
        self.assertNotIn("icloud_private_relay.conf", main)
        self.assertNotIn("telegram_asn.conf", main)

    def test_mobile_reject_stack_is_not_duplicated(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        self.assertNotIn("/reject", main)
        self.assertNotIn("adblock4limbo-supplement.conf", main)
        self.assertNotIn("PROTOCOL,STUN,REJECT", main)
        self.assertNotIn("RULE-SET,SYSTEM", main)

    def test_apple_software_update_hosts_are_exact_and_inline(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        expected = {
            "appldnld.apple.com",
            "configuration.apple.com",
            "fcs-keys-pub-prod.cdn-apple.com",
            "gdmf-ados.apple.com",
            "gdmf.apple.com",
            "gg.apple.com",
            "gs.apple.com",
            "gsra.apple.com",
            "ig.apple.com",
            "mesu.apple.com",
            "oscdn.apple.com",
            "osrecovery.apple.com",
            "skl.apple.com",
            "swcdn.apple.com",
            "swdist.apple.com",
            "swdownload.apple.com",
            "swscan.apple.com",
            "updates-http.cdn-apple.com",
            "updates.cdn-apple.com",
            "wkms-public.apple.com",
            "xp.apple.com",
        }
        actual = {
            line.split(",")[1]
            for line in main.splitlines()
            if line.startswith("DOMAIN,") and ",DIRECT,extended-matching" in line
        }
        self.assertTrue(expected.issubset(actual))
        self.assertEqual(21, len(expected))
        self.assertNotIn("apple-software-update.conf", main)
        self.assertNotIn("DOMAIN-SUFFIX,apple.com,DIRECT", main)

    def test_private_relay_precedes_icloud_direct(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        relay_hosts = [
            "mask.icloud.com",
            "mask-h2.icloud.com",
            "mask-api.icloud.com",
            "mask-canary.icloud.com",
            "mask.apple-dns.net",
            "canary.mask.apple-dns.net",
        ]
        relay_positions = [
            main.index(f'DOMAIN,{host},"United States",extended-matching')
            for host in relay_hosts
        ]
        icloud = main.index("DOMAIN-SUFFIX,icloud.com,DIRECT,extended-matching")
        apple_dns = main.index("DOMAIN-SUFFIX,apple-dns.net,DIRECT,extended-matching")
        self.assertTrue(all(position < icloud for position in relay_positions[:4]))
        self.assertTrue(all(position < apple_dns for position in relay_positions[4:]))

    def test_apple_account_payment_is_precise_and_early(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        expected = [
            "DOMAIN,account.apple.com,Res-Frontier,extended-matching",
            "DOMAIN,appleid.cdn-apple.com,Res-Frontier,extended-matching",
            "DOMAIN,idmsa.apple.com,Res-Frontier,extended-matching",
            "DOMAIN,gsa.apple.com,Res-Frontier,extended-matching",
            "DOMAIN,buy.itunes.apple.com,Res-Frontier,extended-matching",
            "DOMAIN-WILDCARD,*-buy.itunes.apple.com,Res-Frontier",
        ]
        apple_services = main.index("/non_ip/apple_services.conf")
        self.assertTrue(all(main.count(rule) == 1 for rule in expected))
        self.assertTrue(all(main.index(rule) < apple_services for rule in expected))
        self.assertNotIn("apple-account-payment-rules.conf", main)

    def test_apple_cn_precedes_broad_apple_services(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        self.assertLess(
            main.index("/non_ip/apple_cn.conf,DIRECT"),
            main.index('/non_ip/apple_services.conf,"United States"'),
        )

    def test_active_resources_are_consolidated_by_policy(self) -> None:
        manifest = json.loads(
            (ROOT / "rules-manifest.json").read_text(encoding="utf-8")
        )
        policies = {item["file"]: item["policy"] for item in manifest["active"]}
        self.assertEqual(
            {
                "direct-cn.conf": "DIRECT",
                "hk-finance.conf": "Hong Kong",
                "sg-finance.conf": "Singapore",
                "jp-finance.conf": "Japan",
                "kr-finance.conf": "Korea",
                "uk-finance.conf": "United Kingdom",
                "us-residential.conf": "Res-Frontier",
                "finance-context.conf": "Res-Frontier",
                "identity-context.conf": "Res-Frontier",
                "risk-context.conf": "Res-Frontier",
                "crypto.conf": "Crypto",
                "web3.conf": "Web3",
            },
            policies,
        )
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        for inactive in (
            "x-residential.conf",
            "google-account.conf",
            "google-voice.conf",
            "polymarket-global.conf",
            "polymarket.conf",
            "hk-finance-context.conf",
            "bybit.conf",
            "apple-push.conf",
            "apple-push-rules.conf",
        ):
            self.assertNotIn(f"/{inactive}", main)

    def test_consolidated_domains_preserve_required_surfaces(self) -> None:
        residential = self.active_entries("us-residential.conf")
        self.assertTrue(
            {
                ".capitalone.com",
                "capitalone.md-apis.medallia.com",
                "capitalone-resources.digital-cloud.medallia.com",
                ".equifax.com",
                ".myequifax.com",
                ".x.com",
                ".twitter.com",
                "accounts.google.com",
                ".voice.google.com",
                ".polymarket.com",
                ".polymarket.us",
                "pmx-prod.us.auth0.com",
            }.issubset(residential)
        )
        self.assertNotIn(".medallia.com", residential)

        hk = self.active_entries("hk-finance.conf")
        self.assertTrue(
            {
                ".hsbc.com.hk",
                ".hsbc.com",
                ".futunn.com",
                ".moomoo.com",
                ".longbridge.com",
            }.issubset(hk)
        )

        crypto = self.active_entries("crypto.conf")
        self.assertTrue({".bybit.com", ".byapis.com", ".binance.com"}.issubset(crypto))
        self.assertTrue({".gate.com", ".gate.io", ".gateio.ws"}.isdisjoint(crypto))

    def test_identity_and_risk_layers_remain_narrow(self) -> None:
        identity = self.active_entries("identity-context.conf")
        risk = self.active_entries("risk-context.conf")
        self.assertIn(".socure.com", identity)
        self.assertIn(".withpersona.com", identity)
        self.assertIn(".threatmetrix.com", risk)
        self.assertIn(".fingerprint.com", risk)
        self.assertNotIn(".auth0.com", identity)
        self.assertNotIn(".cloudflare.com", risk)

    def test_required_service_specific_rules_remain(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        self.assertEqual(1, main.count("DOMAIN,nano.cr18.eu.org,Singapore"))
        self.assertNotIn("Emby.list", main)
        self.assertNotIn("DOMAIN-KEYWORD,cr18", main)
        web3 = self.active_entries("web3.conf")
        self.assertTrue(
            {
                ".walletconnect.com",
                ".walletconnect.network",
                ".walletconnect.org",
            }.issubset(web3)
        )

    def test_gate_override_is_not_reintroduced(self) -> None:
        main = (ROOT / "surge-main.conf").read_text(encoding="utf-8")
        manifest = (ROOT / "rules-manifest.json").read_text(encoding="utf-8")
        self.assertFalse((ROOT / "gate.conf").exists())
        self.assertNotIn("/gate.conf", main)
        self.assertNotIn('"file": "gate.conf"', manifest)

    def test_sukka_ip_rules_keep_author_semantics(self) -> None:
        lines = (ROOT / "surge-main.conf").read_text(encoding="utf-8").splitlines()
        ip_rules = [line for line in lines if "ruleset.skk.moe/List/ip/" in line]
        self.assertTrue(ip_rules)
        self.assertTrue(all(",no-resolve" not in line for line in ip_rules))
        self.assertIn("RULE-SET,https://ruleset.skk.moe/List/ip/telegram.conf,Singapore", lines)
        self.assertNotIn("RULE-SET,https://ruleset.skk.moe/List/non_ip/telegram.conf,Singapore", lines)

    def test_only_current_ios_mode_snippets_remain_copy_ready(self) -> None:
        complete = (ROOT / "snippets" / "ios-complete-routing.conf").read_text(
            encoding="utf-8"
        )
        self.assertIn("include-all-networks = true", complete)
        self.assertIn("include-apns = false", complete)
        self.assertIn("include-local-networks = false", complete)
        self.assertIn("include-cellular-services = false", complete)


if __name__ == "__main__":
    unittest.main()
