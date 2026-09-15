"""LemFi's owner-selected residential route and narrow tenant boundaries.

These are offline ordinary-hostname regressions. They do not assert that a
particular device used these hosts, nor clear module or shared-authentication
session checks. The golden inventory is independent of the lists and matrix.
"""

from __future__ import annotations

import csv
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

from test_routing_completeness import (  # noqa: E402
    HOST_TYPES, UNKNOWN, Rule, entries, first_match, read_profile_rules,
)


# Fixed review contract: route/list/fixture changes must not silently redefine
# a LemFi suffix as an exact host, or widen a shared tenant to its provider.
LEMFI_ENTRIES = {
    ".lemfi.com",
    ".lemonade.finance",
    "lemfi.onelink.me",
    "lemonadefi.app.link",
    "lemonadefi-alternate.app.link",
    "d1c5a9xrl5sbk8.cloudfront.net",
    "lemonadefinancehelp.zendesk.com",
}
EXPECTED_ROUTE = ("Res-Frontier", "us-residential.conf")
NEGATIVE_HOSTS = {
    "lemonade.com", "www.lemonade.com", "api.lemonade.com",
    "notlemfi.com", "notlemonade.finance", "lemfi.com.example.net",
    "lemonade.finance.example.net", "cloudfront.net", "other.cloudfront.net",
    "onelink.me", "other.onelink.me", "app.link", "other.app.link",
    "zendesk.com", "other.zendesk.com", "lemonadefi.app.link.example.net",
}


def local_hostname_rules(path: Path) -> list[Rule]:
    """Read ordinary hostname records in active and legacy local list files.

    Main/expanded profiles are checked separately. Non-hostname rules in the
    optional Google Voice media list are outside this hostname-only contract.
    """
    rules = []
    for raw in entries(path):
        if "," not in raw:
            kind = "DOMAIN-SUFFIX" if raw.startswith(".") else "DOMAIN"
            rules.append(Rule(kind, raw.removeprefix("."), "fixture", path.name))
        else:
            fields = next(csv.reader([raw], skipinitialspace=True))
            if fields[0] in HOST_TYPES:
                rules.append(Rule(fields[0], fields[1], "fixture", path.name))
    return rules


class LemFiRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((ROOT / "rules-manifest.json").read_text())
        cls.profiles = {
            name: read_profile_rules(ROOT / cls.manifest[name], cls.manifest)
            for name in ("main", "expanded")
        }
        cls.local_lists = {
            path.name: local_hostname_rules(path)
            for path in ROOT.glob("*.conf")
            if path.name not in {cls.manifest["main"], cls.manifest["expanded"]}
        }

    def assert_route(self, host: str) -> None:
        for profile, rules in self.profiles.items():
            with self.subTest(profile=profile, host=host):
                self.assertEqual(EXPECTED_ROUTE, first_match(rules, host))

    def test_every_fixed_entry_is_present_once_in_residential_list(self) -> None:
        actual = entries(ROOT / "us-residential.conf")
        for entry in sorted(LEMFI_ENTRIES):
            with self.subTest(entry=entry):
                self.assertEqual(1, actual.count(entry))

    def test_every_fixed_entry_first_matches_residential_in_both_profiles(self) -> None:
        for entry in sorted(LEMFI_ENTRIES):
            self.assert_route(entry.removeprefix("."))

    def test_first_party_suffixes_cover_synthetic_subdomains(self) -> None:
        for entry in sorted(LEMFI_ENTRIES):
            if entry.startswith("."):
                for prefix in ("fixture-child", "deep.fixture-child"):
                    self.assert_route(prefix + entry)

    def test_no_other_active_or_legacy_list_absorbs_confirmed_lemfi_hosts(self) -> None:
        for entry in sorted(LEMFI_ENTRIES):
            hosts = [entry.removeprefix(".")]
            if entry.startswith("."):
                hosts.append("fixture-child" + entry)
            for host in hosts:
                owners = [
                    source for source, rules in self.local_lists.items()
                    for rule in rules if rule.matches(host)
                ]
                with self.subTest(host=host):
                    self.assertEqual(["us-residential.conf"], owners)

    def test_shared_tenants_do_not_expand_to_child_or_neighbor_hosts(self) -> None:
        for entry in sorted(LEMFI_ENTRIES):
            if entry.startswith("."):
                continue
            for host in ("fixture-child." + entry, "not" + entry, entry + ".example.net"):
                for profile, rules in self.profiles.items():
                    with self.subTest(profile=profile, host=host):
                        self.assertEqual(UNKNOWN, first_match(rules, host)[0])
                for source, rules in self.local_lists.items():
                    with self.subTest(source=source, host=host):
                        self.assertFalse(any(rule.matches(host) for rule in rules))

    def test_insurance_shared_providers_and_concatenated_names_are_not_captured(self) -> None:
        for host in sorted(NEGATIVE_HOSTS):
            for profile, rules in self.profiles.items():
                with self.subTest(profile=profile, host=host):
                    self.assertEqual(UNKNOWN, first_match(rules, host)[0])
            for source, rules in self.local_lists.items():
                with self.subTest(source=source, host=host):
                    self.assertFalse(any(rule.matches(host) for rule in rules))

    def test_matrix_keeps_every_confirmed_lemfi_anchor(self) -> None:
        matrix = json.loads((ROOT / "routing-acceptance.json").read_text())
        cases = [case for case in matrix["cases"] if case["app"] == "LemFi"]
        self.assertEqual(1, len(cases))
        self.assertEqual(EXPECTED_ROUTE, (cases[0]["policy"], cases[0]["file"]))
        expected_hosts = {entry.removeprefix(".") for entry in LEMFI_ENTRIES}
        self.assertTrue(expected_hosts.issubset(cases[0]["hosts"]))


if __name__ == "__main__":
    unittest.main()
