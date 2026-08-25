from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
DEPENDABOT = ROOT / ".github" / "dependabot.yml"


class WorkflowTests(unittest.TestCase):
    def test_inactive_adblock_supplement_has_no_scheduled_publisher(self) -> None:
        self.assertFalse((WORKFLOWS / "sync-adblock4limbo.yml").exists())
        upstream = (WORKFLOWS / "upstream-health.yml").read_text(encoding="utf-8")
        self.assertNotIn("sync_adblock4limbo.py", upstream)

    def test_all_actions_are_immutable_and_dependabot_tracks_them(self) -> None:
        action_refs: list[str] = []
        for workflow in WORKFLOWS.glob("*.yml"):
            text = workflow.read_text(encoding="utf-8")
            action_refs.extend(
                re.findall(r"^\s*uses:\s*([^\s#]+)", text, flags=re.MULTILINE)
            )
        self.assertGreater(len(action_refs), 0)
        for action_ref in action_refs:
            self.assertRegex(action_ref, r"^[^@]+@[0-9a-f]{40}$")

        dependabot = DEPENDABOT.read_text(encoding="utf-8")
        self.assertIn("package-ecosystem: github-actions", dependabot)
        self.assertIn("interval: weekly", dependabot)


if __name__ == "__main__":
    unittest.main()
