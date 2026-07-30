from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import sync_adblock4limbo  # noqa: E402


class AdblockBuildTests(unittest.TestCase):
    def test_builds_minimal_policy_free_domain_set(self) -> None:
        source = "\n".join(
            [
                "DOMAIN,exact.example,reject",
                "DOMAIN,exact.example,reject",
                "DOMAIN-SUFFIX,covered.example,reject",
                "DOMAIN,child.parent.example,reject",
                "DOMAIN-SUFFIX,parent.example,reject",
                "DOMAIN-KEYWORD,broad,reject",
                "DOMAIN,192.0.2.1,reject",
            ]
        )
        baseline = ".covered.example\n"
        rendered, stats = sync_adblock4limbo.build(source, baseline)

        entries = [
            line
            for line in rendered.splitlines()
            if line and not line.startswith("#")
        ]
        self.assertEqual(["exact.example", ".parent.example"], entries)
        self.assertEqual(1, stats.keyword_rules)
        self.assertEqual(1, stats.invalid_rules)
        self.assertEqual(1, stats.duplicate_rules)
        self.assertEqual(1, stats.baseline_covered)
        self.assertEqual(1, stats.internally_redundant)

    def test_rejects_unexpected_upstream_policy(self) -> None:
        with self.assertRaisesRegex(ValueError, "unexpected Adblock4limbo rule"):
            sync_adblock4limbo.parse_adblock(
                "DOMAIN,example.com,DIRECT\n"
            )

    def test_excludes_pseudo_domains_and_non_ip_baseline_coverage(self) -> None:
        source = "\n".join(
            [
                "DOMAIN-SUFFIX,ingest.sentry,reject",
                "DOMAIN-SUFFIX,sentry,reject",
                "DOMAIN-SUFFIX,histats.com,reject",
                "DOMAIN-SUFFIX,keep.example,reject",
            ]
        )
        domain_set_baseline = ".unrelated.example\n"
        ruleset_baseline = "\n".join(
            [
                "DOMAIN-KEYWORD,ignored",
                "DOMAIN-SUFFIX,histats.com",
                "IP-CIDR,192.0.2.0/24,no-resolve",
            ]
        )

        rendered, stats = sync_adblock4limbo.build(
            source,
            domain_set_baseline,
            ruleset_baseline,
        )
        entries = [
            line
            for line in rendered.splitlines()
            if line and not line.startswith("#")
        ]

        self.assertEqual([".keep.example"], entries)
        self.assertNotIn(".ingest.sentry", entries)
        self.assertNotIn(".sentry", entries)
        self.assertNotIn(".histats.com", entries)
        self.assertEqual(2, stats.explicitly_excluded)
        self.assertEqual(1, stats.ruleset_baseline_covered)
        self.assertIn(
            "# Explicit invalid pseudo-domain exclusions: "
            ".ingest.sentry, .sentry",
            rendered,
        )

    def test_rejects_embedded_policy_in_ruleset_baseline(self) -> None:
        with self.assertRaisesRegex(ValueError, "invalid baseline RULE-SET"):
            sync_adblock4limbo.parse_ruleset_domains(
                "DOMAIN-SUFFIX,example.com,REJECT\n"
            )


if __name__ == "__main__":
    unittest.main()
