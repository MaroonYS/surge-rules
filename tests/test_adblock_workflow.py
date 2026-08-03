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
            'cron: "37 18 * * *"',
            "retry_count:",
            "actions: write",
            "contents: write",
            "ref: main",
            "python scripts/sync_adblock4limbo.py --write --timeout 30",
            "for attempt in 1 2 3",
            "sleep $((attempt * 15))",
            "python scripts/build_expanded.py --write",
            "python -m unittest discover -s tests -v",
            "python scripts/build_expanded.py --check",
            "--strict",
            "git diff --check",
            "git diff --name-only",
            "git fetch --no-tags origin \"$BASE_BRANCH\"",
            'git push origin "HEAD:refs/heads/${BASE_BRANCH}"',
            "Queue bounded automatic retry",
            "if: ${{ failure() && !cancelled() }}",
            "gh workflow run sync-adblock4limbo.yml",
            "RETRY_COUNT >= 2",
        ):
            self.assertIn(required, text)

        self.assertNotIn("pull_request_target:", text)
        self.assertNotIn("pull-requests: write", text)
        self.assertNotIn("UPDATE_BRANCH", text)
        self.assertNotIn("gh pr ", text)
        self.assertNotIn("--force", text)
        self.assertNotIn('cron: "37 */6 * * *"', text)
        self.assertRegex(
            text,
            r"- name: Commit and fast-forward main\n"
            r"\s+if: steps\.changes\.outputs\.changed == 'true'",
        )

        ordered_markers = (
            "python scripts/sync_adblock4limbo.py --write --timeout 30",
            "python scripts/build_expanded.py --write",
            "python -m unittest discover -s tests -v",
            "python scripts/build_expanded.py --check",
            "python scripts/validate.py",
            "git diff --check",
            "git add --",
            "git commit -m \"chore: refresh Adblock4limbo supplement\"",
            "git fetch --no-tags origin \"$BASE_BRANCH\"",
            'git push origin "HEAD:refs/heads/${BASE_BRANCH}"',
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

        self.assertIn(
            "Generator changed files outside the allowlist.",
            text,
        )
        self.assertIn(
            "main moved during synchronization; refusing to publish.",
            text,
        )
        self.assertIn("Unexpected staged files:", text)


if __name__ == "__main__":
    unittest.main()
