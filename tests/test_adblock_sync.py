from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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

    def test_write_ignores_provenance_only_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.conf"
            baseline = root / "baseline.conf"
            ruleset_baseline = root / "ruleset.conf"
            output = root / "output.conf"
            metadata = root / "metadata.json"
            source.write_text(
                "DOMAIN-SUFFIX,keep.example,reject\n",
                encoding="utf-8",
            )
            baseline.write_text(".unrelated.example\n", encoding="utf-8")
            ruleset_baseline.write_text(
                "DOMAIN-SUFFIX,also-unrelated.example\n",
                encoding="utf-8",
            )
            original = "# stale volatile hash\n.keep.example\n"
            output.write_text(original, encoding="utf-8")

            real_write_text = Path.write_text
            written_paths: list[Path] = []

            def tracked_write(path: Path, *args: object, **kwargs: object) -> int:
                written_paths.append(path)
                return real_write_text(path, *args, **kwargs)

            with mock.patch.object(Path, "write_text", tracked_write):
                result = sync_adblock4limbo.main(
                    [
                        "--write",
                        "--source-file",
                        str(source),
                        "--baseline-file",
                        str(baseline),
                        "--ruleset-baseline-file",
                        str(ruleset_baseline),
                        "--output",
                        str(output),
                        "--metadata-json",
                        str(metadata),
                    ]
                )

            self.assertEqual(0, result)
            self.assertEqual(original, output.read_text(encoding="utf-8"))
            self.assertNotIn(output, written_paths)
            self.assertIn(metadata, written_paths)
            recorded = json.loads(metadata.read_text(encoding="utf-8"))
            self.assertEqual(
                sync_adblock4limbo.SOURCE_URL,
                recorded["source"]["url"],
            )
            self.assertRegex(recorded["source"]["sha256"], r"^[0-9a-f]{64}$")

    def test_rendered_header_has_no_volatile_hashes(self) -> None:
        rendered, _ = sync_adblock4limbo.build(
            "DOMAIN-SUFFIX,keep.example,reject\n",
            ".unrelated.example\n",
            "DOMAIN-SUFFIX,also-unrelated.example\n",
        )
        self.assertNotIn("SHA-256:", rendered)


if __name__ == "__main__":
    unittest.main()
