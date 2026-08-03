from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "sync-adblock4limbo.yml"


class AdblockWorkflowTests(unittest.TestCase):
    def test_sync_workflow_is_safe_and_complete(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        for required in (
            "schedule:",
            "workflow_dispatch:",
            "contents: write",
            "pull-requests: write",
            "ref: main",
            "UPDATE_BRANCH: automation/adblock4limbo-sync",
            "python scripts/sync_adblock4limbo.py --write --timeout 30",
            "python scripts/build_expanded.py --write",
            "python -m unittest discover -s tests -v",
            "python scripts/build_expanded.py --check",
            "--strict",
            "git diff --check",
            "gh pr create",
            "--draft",
        ):
            self.assertIn(required, text)

        self.assertNotIn("pull_request_target:", text)
        self.assertNotIn("gh pr merge", text)
        self.assertNotIn("HEAD:main", text)

        ordered_markers = (
            "python scripts/sync_adblock4limbo.py --write --timeout 30",
            "python scripts/build_expanded.py --write",
            "python -m unittest discover -s tests -v",
            "python scripts/build_expanded.py --check",
            "python scripts/validate.py",
            "git diff --check",
            "gh pr create",
        )
        positions = [text.index(marker) for marker in ordered_markers]
        self.assertEqual(sorted(positions), positions)

        add_block = re.search(
            r"git add --\s+(.*?)\s+git commit",
            text,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(add_block)
        self.assertEqual(
            {
                "adblock4limbo-supplement.conf",
                "surge-expanded.conf",
            },
            set(re.findall(r"[a-z0-9-]+\.conf", add_block.group(1))),
        )


if __name__ == "__main__":
    unittest.main()
