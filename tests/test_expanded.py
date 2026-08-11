from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_expanded  # noqa: E402


class ExpandedRuleTests(unittest.TestCase):
    def test_committed_file_matches_generator(self) -> None:
        rendered = build_expanded.render_expanded(ROOT)
        committed = (ROOT / "surge-expanded.conf").read_text(encoding="utf-8")
        self.assertEqual(rendered, committed)

    def test_all_active_entries_are_expanded(self) -> None:
        rendered = build_expanded.render_expanded(ROOT)
        _, _, _, bindings = build_expanded.load_configuration(ROOT)
        expected = sum(
            len(build_expanded.read_domain_entries(ROOT / binding["file"]))
            for binding in bindings
        )
        self.assertGreater(expected, 0)
        binding_types = {
            binding.get("type", "DOMAIN-SET") for binding in bindings
        }
        label = (
            "DOMAIN-SET entries"
            if binding_types == {"DOMAIN-SET"}
            else "local rule entries"
        )
        self.assertIn(f"{expected} {label} expanded inline", rendered)
        self.assertEqual(len(bindings), rendered.count("# BEGIN "))
        self.assertEqual(len(bindings), rendered.count("# END "))
        self.assertNotIn(
            "raw.githubusercontent.com/MaroonYS/surge-rules/main/",
            rendered,
        )

    def test_mixed_binding_types_expand_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_base = (
                "https://raw.githubusercontent.com/owner/repository/main/"
            )
            manifest = {
                "repository": "owner/repository",
                "branch": "main",
                "main": "surge-main.conf",
                "active": [
                    {"file": "domains.conf", "policy": "DIRECT"},
                    {
                        "file": "rules.conf",
                        "type": "RULE-SET",
                        "policy": "Media",
                    },
                    {
                        "file": "regional.conf",
                        "policy": "United States",
                    },
                ],
            }
            (root / "rules-manifest.json").write_text(
                json.dumps(manifest),
                encoding="utf-8",
            )
            (root / "domains.conf").write_text(
                ".example.com\n",
                encoding="utf-8",
            )
            (root / "rules.conf").write_text(
                "AND,((PROTOCOL,UDP),(DEST-PORT,19302))\n"
                "IP-CIDR,192.0.2.0/24,no-resolve\n"
                "DOMAIN,api.example.net,extended-matching\n"
                "DOMAIN,buy.itunes.apple.com\n"
                "DOMAIN-WILDCARD,*-buy.itunes.apple.com\n",
                encoding="utf-8",
            )
            (root / "regional.conf").write_text(
                ".example.org\n",
                encoding="utf-8",
            )
            (root / "surge-main.conf").write_text(
                "[Rule]\n"
                f"DOMAIN-SET,{raw_base}domains.conf,DIRECT,extended-matching\n"
                f"RULE-SET,{raw_base}rules.conf,Media\n"
                f'DOMAIN-SET,{raw_base}regional.conf,"United States",'
                "extended-matching\n"
                "FINAL,DIRECT,dns-failed\n",
                encoding="utf-8",
            )

            rendered = build_expanded.render_expanded(root)

        expected_rules = [
            "DOMAIN-SUFFIX,example.com,DIRECT,extended-matching",
            "AND,((PROTOCOL,UDP),(DEST-PORT,19302)),Media",
            "IP-CIDR,192.0.2.0/24,Media,no-resolve",
            "DOMAIN,api.example.net,Media,extended-matching",
            "DOMAIN,buy.itunes.apple.com,Media",
            "DOMAIN-WILDCARD,*-buy.itunes.apple.com,Media",
            'DOMAIN-SUFFIX,example.org,"United States",extended-matching',
        ]
        positions = [rendered.index(rule) for rule in expected_rules]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("7 local rule entries expanded inline", rendered)
        self.assertNotIn(raw_base, rendered)

    def test_local_rule_set_outer_options_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_base = "https://raw.githubusercontent.com/o/r/main/"
            (root / "rules-manifest.json").write_text(
                json.dumps(
                    {
                        "repository": "o/r",
                        "branch": "main",
                        "main": "surge-main.conf",
                        "active": [
                            {
                                "file": "rules.conf",
                                "type": "RULE-SET",
                                "policy": "Media",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (root / "rules.conf").write_text(
                "AND,((PROTOCOL,UDP),(DEST-PORT,19302))\n",
                encoding="utf-8",
            )
            (root / "surge-main.conf").write_text(
                "[Rule]\n"
                f"RULE-SET,{raw_base}rules.conf,Media,extended-matching\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "outer RULE-SET options"):
                build_expanded.render_expanded(root)


if __name__ == "__main__":
    unittest.main()
