from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate  # noqa: E402


class RuleContractTests(unittest.TestCase):
    def validate_modified_main(self, old: str, new: str) -> set[str]:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "repo"
            shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns(".git"))
            main_path = copied / "surge-main.conf"
            original = main_path.read_text(encoding="utf-8")
            self.assertIn(old, original)
            main_path.write_text(
                original.replace(old, new, 1),
                encoding="utf-8",
            )
            result = validate.validate_repository(copied)
        return {item.code for item in result.diagnostics}

    def test_removing_stun_rule_fails_contract(self) -> None:
        codes = self.validate_modified_main(
            "PROTOCOL,STUN,REJECT\n",
            "",
        )
        self.assertIn("RULE_CONTRACT_MISMATCH", codes)

    def test_changing_private_relay_policy_fails_contract(self) -> None:
        codes = self.validate_modified_main(
            "icloud_private_relay.conf,Apple,extended-matching",
            "icloud_private_relay.conf,AIGC,extended-matching",
        )
        self.assertIn("RULE_CONTRACT_MISMATCH", codes)


if __name__ == "__main__":
    unittest.main()
