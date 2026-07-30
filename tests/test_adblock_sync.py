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


if __name__ == "__main__":
    unittest.main()
