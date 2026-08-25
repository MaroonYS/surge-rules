from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_module_compatibility  # noqa: E402


class ModuleCompatibilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads(
            (ROOT / "module-compatibility.json").read_text(encoding="utf-8")
        )
        self.positives, self.negatives = (
            check_module_compatibility.manifest_contract(self.data)
        )

    def test_manifest_and_documentation_are_current(self) -> None:
        self.assertEqual(24, len(self.positives))
        self.assertEqual(121, len(self.negatives))
        self.assertIn("-capitalone.md-apis.medallia.com", self.negatives)
        self.assertIn("-*.myequifax.com", self.negatives)
        self.assertIn("-*.polymarket.com", self.negatives)
        self.assertIn("-*.gate.com", self.negatives)
        self.assertNotIn("-*.apple.com", self.negatives)
        self.assertNotIn("-*.apple-livephotoskit.com", self.negatives)
        self.assertNotIn("-*.icloud.com.cn", self.negatives)
        self.assertNotIn("-*.apple-dns.net", self.negatives)
        self.assertIn("gsp-ssl.ls.apple.com", self.positives)
        self.assertIn("bluedot.is.autonavi.com", self.positives)
        self.assertNotIn("conditional_mitm_disables", self.data)
        documentation = ROOT / self.data["documentation"]
        self.assertEqual(
            self.positives,
            check_module_compatibility.documented_hosts(documentation),
        )

    def test_manifest_rejects_missing_retained_module(self) -> None:
        changed = copy.deepcopy(self.data)
        changed["modules"] = [
            module
            for module in changed["modules"]
            if module["id"] != "wloc"
        ]
        with self.assertRaisesRegex(ValueError, "module ids drifted"):
            check_module_compatibility.manifest_contract(changed)

    def test_effective_profile_requires_positive_hosts_before_exclusions(self) -> None:
        valid = (
            "[MITM]\n"
            "hostname = "
            + ", ".join(self.positives + self.negatives)
            + "\n"
        )
        self.assertEqual(
            [],
            check_module_compatibility.validate_profile_order(
                valid,
                self.positives,
                self.negatives,
            ),
        )

        invalid = (
            "[MITM]\n"
            "hostname = "
            + ", ".join(self.negatives + self.positives)
            + "\n"
        )
        problems = check_module_compatibility.validate_profile_order(
            invalid,
            self.positives,
            self.negatives,
        )
        self.assertTrue(any("appears after" in problem for problem in problems))

    def test_effective_profile_reports_missing_host(self) -> None:
        profile = "[MITM]\nhostname = " + ", ".join(
            self.positives[1:] + self.negatives
        )
        problems = check_module_compatibility.validate_profile_order(
            profile,
            self.positives,
            self.negatives,
        )
        self.assertIn(
            f"missing positive MITM host: {self.positives[0]}",
            problems,
        )

    def test_effective_profile_preserves_all_protected_exclusions(self) -> None:
        profile = "[MITM]\nhostname = " + ", ".join(
            self.positives + self.negatives[1:]
        )
        problems = check_module_compatibility.validate_profile_order(
            profile,
            self.positives,
            self.negatives,
        )
        self.assertIn(
            f"missing protected MITM exclusion: {self.negatives[0]}",
            problems,
        )

    def test_base_profile_contract_delegates_positive_hosts_to_modules(self) -> None:
        profile = (
            "[MITM]\n"
            "h2 = true\n"
            "hostname = "
            + ", ".join(self.negatives)
            + "\n"
        )
        self.assertEqual(
            [],
            check_module_compatibility.validate_base_profile(
                profile,
                self.negatives,
            ),
        )

        broken = profile.replace("h2 = true", "h2 = false").replace(
            "hostname = ",
            f"hostname = {self.positives[0]}, ",
        )
        problems = check_module_compatibility.validate_base_profile(
            broken,
            self.negatives,
        )
        self.assertIn("base MITM must enable h2", problems)
        self.assertTrue(
            any("must not duplicate module-owned" in problem for problem in problems)
        )


if __name__ == "__main__":
    unittest.main()
