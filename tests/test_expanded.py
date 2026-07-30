from __future__ import annotations

import sys
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
        self.assertIn(
            f"{expected} DOMAIN-SET entries expanded inline",
            rendered,
        )
        self.assertEqual(len(bindings), rendered.count("# BEGIN "))
        self.assertEqual(len(bindings), rendered.count("# END "))
        self.assertNotIn(
            "raw.githubusercontent.com/MaroonYS/surge-rules/main/",
            rendered,
        )


if __name__ == "__main__":
    unittest.main()
