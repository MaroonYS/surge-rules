from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_upstreams  # noqa: E402
import skk_markers  # noqa: E402


class PayloadTests(unittest.TestCase):
    def resource(self, rule_type: str = "RULE-SET") -> check_upstreams.Resource:
        return check_upstreams.Resource(
            "https://example.com/rules.conf",
            rule_type,
            1,
        )

    def skk_resource(self, rule_type: str = "RULE-SET") -> check_upstreams.Resource:
        suffix = (
            "domainset/example.conf"
            if rule_type == "DOMAIN-SET"
            else "non_ip/example.conf"
        )
        return check_upstreams.Resource(
            f"https://ruleset.skk.moe/List/{suffix}",
            rule_type,
            1,
        )

    def supercell_resource(self) -> check_upstreams.Resource:
        return check_upstreams.Resource(
            check_upstreams.SUPERCELL_UPSTREAM_URL,
            "RULE-SET",
            1,
        )

    def test_deprecated_header_is_rejected(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.resource(),
            "# Sukka's Ruleset - Deprecated\n# EOF\n",
        )
        self.assertEqual(0, count)
        self.assertIn("Deprecated", problem)

    def test_deprecated_domain_name_is_not_a_deprecation_marker(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.resource("DOMAIN-SET"),
            "# Active list\n.s3-deprecated.example.com\n",
        )
        self.assertEqual(1, count)
        self.assertEqual("", problem)

    def test_sentinel_only_resource_is_rejected(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.skk_resource(),
            f"DOMAIN,{skk_markers.CURRENT_SKK_MARKER}\n",
        )
        self.assertEqual(0, count)
        self.assertIn("marker", problem)

    def test_sentinel_is_ignored_when_real_rules_exist(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.skk_resource(),
            (
                f"DOMAIN,{skk_markers.CURRENT_SKK_MARKER}\n"
                "IP-CIDR,192.0.2.0/24,no-resolve\n"
            ),
        )
        self.assertEqual(1, count)
        self.assertEqual("", problem)

    def test_domain_set_marker_is_ignored(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.skk_resource("DOMAIN-SET"),
            f"{skk_markers.CURRENT_SKK_MARKER}\n.example.com\n",
        )
        self.assertEqual(1, count)
        self.assertEqual("", problem)

    def test_all_known_historical_markers_are_supported(self) -> None:
        for marker in skk_markers.SKK_MARKER_DOMAINS:
            with self.subTest(marker=marker):
                count, problem = check_upstreams.validate_payload(
                    self.skk_resource(),
                    f"DOMAIN,{marker}\nIP-CIDR,192.0.2.0/24,no-resolve\n",
                )
                self.assertEqual(1, count)
                self.assertEqual("", problem)

    def test_marker_like_business_rules_are_not_filtered(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.skk_resource(),
            (
                f"DOMAIN,{skk_markers.CURRENT_SKK_MARKER}\n"
                "DOMAIN-KEYWORD,this_rule_set_is_made_by_sukkaw\n"
            ),
        )
        self.assertEqual(1, count)
        self.assertEqual("", problem)

    def test_third_party_marker_domain_is_business_data(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.resource(),
            f"DOMAIN,{skk_markers.CURRENT_SKK_MARKER}\n",
        )
        self.assertEqual(1, count)
        self.assertEqual("", problem)

    def test_skk_marker_must_be_first(self) -> None:
        marker = f"DOMAIN,{skk_markers.CURRENT_SKK_MARKER}"
        count, problem = check_upstreams.validate_payload(
            self.skk_resource(),
            f"IP-CIDR,192.0.2.0/24,no-resolve\n{marker}\n",
        )
        self.assertEqual(2, count)
        self.assertIn("missing", problem)

    def test_later_marker_domains_remain_business_rules(self) -> None:
        marker = f"DOMAIN,{skk_markers.CURRENT_SKK_MARKER}"
        count, problem = check_upstreams.validate_payload(
            self.skk_resource(),
            f"{marker}\n{marker}\nIP-CIDR,192.0.2.0/24,no-resolve\n",
        )
        self.assertEqual(2, count)
        self.assertEqual("", problem)

    def test_skk_resource_requires_a_known_marker(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.skk_resource(),
            "DOMAIN,unknown-marker.example\n",
        )
        self.assertEqual(1, count)
        self.assertIn("missing", problem)

    def test_malformed_marker_rule_is_not_hidden(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.skk_resource(),
            f"DOMAIN,{skk_markers.CURRENT_SKK_MARKER},REJECT\n",
        )
        self.assertEqual(1, count)
        self.assertIn("embedded policy", problem)

    def test_embedded_ruleset_policy_is_rejected(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.resource(),
            "DOMAIN-SUFFIX,example.com,reject\n",
        )
        self.assertEqual(1, count)
        self.assertIn("embedded policy", problem)

    def test_ruleset_option_is_accepted(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.resource(),
            "IP-CIDR,192.0.2.0/24,no-resolve\n",
        )
        self.assertEqual(1, count)
        self.assertEqual("", problem)

    def test_supercell_upstream_contract_accepts_only_narrow_mixed_rules(self) -> None:
        valid = (
            "DOMAIN-SUFFIX,brawlstars.com\n"
            "DOMAIN-SUFFIX,brawlstarsgame.com\n"
            "IP-CIDR,192.0.2.1/32,no-resolve\n"
        )
        count, problem = check_upstreams.validate_payload(
            self.supercell_resource(),
            valid,
        )
        self.assertEqual(3, count)
        self.assertEqual("", problem)

        invalid_payloads = (
            valid + "DOMAIN-SUFFIX,example.com\n",
            valid.replace("192.0.2.1/32", "192.0.2.0/24"),
            valid + "IP-ASN,13335\n",
        )
        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                _, problem = check_upstreams.validate_payload(
                    self.supercell_resource(),
                    payload,
                )
                self.assertTrue(problem)

    def test_local_logical_rules_use_strict_policy_free_validation(self) -> None:
        valid = (
            "AND,((PROTOCOL,UDP),(DEST-PORT,19302-19309),"
            "(IP-CIDR,192.0.2.0/24,no-resolve))\n"
        )
        count, problem = check_upstreams.validate_payload(
            self.resource(),
            valid,
            strict_local_rule_set=True,
        )
        self.assertEqual(1, count)
        self.assertEqual("", problem)

        count, problem = check_upstreams.validate_payload(
            self.resource(),
            valid.rstrip("\n") + ",CustomPolicy\n",
            strict_local_rule_set=True,
        )
        self.assertEqual(1, count)
        self.assertIn("embedded policy", problem)

    def test_unexpected_ip_option_is_rejected(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.resource(),
            "IP-CIDR,192.0.2.0/24,Proxy\n",
        )
        self.assertEqual(1, count)
        self.assertIn("embedded policy", problem)

    def test_html_payload_is_rejected_even_as_text(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.resource(),
            "<!doctype html><html><body>error</body></html>\n",
        )
        self.assertEqual(0, count)
        self.assertIn("HTML", problem)

    def test_utf8_bom_is_rejected(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.resource("DOMAIN-SET"),
            "\ufeff.example.com\n",
        )
        self.assertEqual(0, count)
        self.assertIn("BOM", problem)

    def test_domain_set_policy_column_is_rejected(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.resource("DOMAIN-SET"),
            ".example.com,REJECT\n",
        )
        self.assertEqual(1, count)
        self.assertIn("invalid DOMAIN-SET", problem)

    def test_upstream_domain_set_can_contain_single_label_suffix(self) -> None:
        count, problem = check_upstreams.validate_payload(
            self.resource("DOMAIN-SET"),
            ".data\n",
        )
        self.assertEqual(1, count)
        self.assertEqual("", problem)


class CollectionTests(unittest.TestCase):
    def test_collects_resource_type_and_deduplicates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "surge.conf"
            path.write_text(
                "[Rule]\n"
                "DOMAIN-SET,https://example.com/domains,Proxy\n"
                "DOMAIN-SET,https://example.com/domains,Proxy\n"
                "RULE-SET,https://example.com/rules,DIRECT\n",
                encoding="utf-8",
            )
            resources = check_upstreams.collect_resources(path)
        self.assertEqual(
            [
                ("https://example.com/domains", "DOMAIN-SET"),
                ("https://example.com/rules", "RULE-SET"),
            ],
            [(item.url, item.rule_type) for item in resources],
        )

    def test_collects_resources_from_downloaded_configuration_text(self) -> None:
        resources = check_upstreams.collect_resources_text(
            "[Rule]\n"
            "DOMAIN-SET,https://example.com/domains,Proxy\n"
            "FINAL,Proxy\n"
        )
        self.assertEqual(1, len(resources))
        self.assertEqual("https://example.com/domains", resources[0].url)


class LocalReferenceTests(unittest.TestCase):
    def write_manifest(self, root: Path) -> None:
        (root / "rules-manifest.json").write_text(
            '{"repository": "MaroonYS/surge-rules", "branch": "main"}\n',
            encoding="utf-8",
        )

    def test_builds_immutable_raw_base_from_commit_sha(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_manifest(root)
            base = check_upstreams.local_raw_base_for_ref(root, "a" * 40)
        self.assertEqual(
            "https://raw.githubusercontent.com/MaroonYS/surge-rules/"
            f"{'a' * 40}/",
            base,
        )

    def test_builds_raw_base_for_slash_ref(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_manifest(root)
            base = check_upstreams.local_raw_base_for_ref(
                root,
                "refs/heads/codex/rule-hardening",
            )
        self.assertEqual(
            "https://raw.githubusercontent.com/MaroonYS/surge-rules/"
            "refs/heads/codex/rule-hardening/",
            base,
        )

    def test_rejects_unsafe_ref(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_manifest(root)
            with self.assertRaisesRegex(ValueError, "invalid Git ref"):
                check_upstreams.local_raw_base_for_ref(root, "../main")

    def test_extracts_only_safe_local_root_file(self) -> None:
        base = "https://raw.githubusercontent.com/MaroonYS/surge-rules/main/"
        self.assertEqual(
            "apple-ai.conf",
            check_upstreams.local_relative_path(
                f"{base}apple-ai.conf",
                base,
            ),
        )
        self.assertIsNone(
            check_upstreams.local_relative_path(
                "https://ruleset.skk.moe/List/non_ip/ai.conf",
                base,
            )
        )
        with self.assertRaisesRegex(ValueError, "unsafe local repository path"):
            check_upstreams.local_relative_path(f"{base}nested/file.conf", base)


if __name__ == "__main__":
    unittest.main()
