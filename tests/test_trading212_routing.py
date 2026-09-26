"""Owner-selected Trading 212 UK routing; no claim of live app verification."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_lemfi_routing import local_hostname_rules  # noqa: E402
from test_routing_completeness import entries, first_match, read_profile_rules  # noqa: E402

REQUIRED_ENTRIES = {".trading212.com", ".t212.cc"}
EXPECTED_ROUTE = ("United Kingdom", "uk-finance.conf")
PROBES = {
    "trading212.com", "www.trading212.com", "app.trading212.com",
    "live.trading212.com", "demo.trading212.com", "docs.trading212.com",
    "helpcentre.trading212.com", "community.trading212.com",
    "info.trading212.com", "t212.cc",
    # Synthetic subdomains test suffix semantics, not observed app requests.
    "fixture-child.trading212.com", "deep.fixture-child.trading212.com",
    "fixture-child.t212.cc",
}


class Trading212RoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((ROOT / "rules-manifest.json").read_text())
        cls.profiles = {
            key: read_profile_rules(ROOT / cls.manifest[key], cls.manifest)
            for key in ("main", "expanded")
        }
        cls.active = {
            item["file"]: local_hostname_rules(ROOT / item["file"])
            for item in cls.manifest["active"]
        }

    def test_confirmed_namespaces_occur_once_in_uk(self) -> None:
        actual = entries(ROOT / "uk-finance.conf")
        for entry in REQUIRED_ENTRIES:
            self.assertEqual(1, actual.count(entry), entry)

    def test_first_match_is_uk_in_both_profiles(self) -> None:
        for name, rules in self.profiles.items():
            for host in PROBES:
                with self.subTest(profile=name, host=host):
                    self.assertEqual(EXPECTED_ROUTE, first_match(rules, host))

    def test_no_competing_or_duplicate_active_owner(self) -> None:
        for host in PROBES:
            owners = [source for source, rules in self.active.items()
                      for rule in rules if rule.matches(host)]
            self.assertEqual(["uk-finance.conf"], owners, host)

    def test_no_lookalike_or_shared_provider_is_assigned_to_uk(self) -> None:
        negative_hosts = {
            "nottrading212.com", "trading212.com.example.net", "nott212.cc",
            "t212.cc.example.net", "onelink.me", "other.onelink.me",
            "cloudfront.net", "other.cloudfront.net", "zendesk.com",
            "other.zendesk.com", "api.sumsub.com", "stationapi.veriff.com",
        }
        for host in negative_hosts:
            self.assertFalse(any(r.matches(host) for r in self.active["uk-finance.conf"]), host)


if __name__ == "__main__":
    unittest.main()
