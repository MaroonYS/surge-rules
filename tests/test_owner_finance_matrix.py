"""Independent owner-selected routing contract for the 24 requested finance apps.

These checks model ordinary HTTPS hostname rules, not live app sessions, proxy
selection, injected pre-matching modules, DNS/IP routing, or KYC completion.
Expectations are intentionally independent of the editable acceptance JSON.
Historical inactive lists are not rewritten or treated as deployed owners.
"""

from __future__ import annotations

import json
import sys
import unittest
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

from test_lemfi_routing import local_hostname_rules  # noqa: E402
from test_routing_completeness import (  # noqa: E402
    UNKNOWN, entries, first_match, read_profile_rules,
)


@dataclass(frozen=True)
class Application:
    name: str
    policy: str
    hosts: tuple[str, ...]
    sources: frozenset[str]


HK = frozenset({"hk-finance.conf"})
US = frozenset({"us-residential.conf"})
US_CONTEXT = frozenset({"us-residential.conf", "finance-context.conf"})
CN = frozenset({"direct-cn.conf"})
UK = frozenset({"uk-finance.conf"})

# Region is the owner's explicit account context, not the company's home or
# a country guessed from its domain. Reward+ is HSBC Hong Kong's application.
APPLICATIONS = (
    Application("BOCHK", "Hong Kong", ("bochk.com", "www.bochk.com"), HK),
    Application("ZA", "Hong Kong", ("zabank.com", "za.group"), HK),
    Application("Reward+", "Hong Kong", ("hsbc.com.hk", "www.hsbc.com.hk"), HK),
    Application("Futubull", "Hong Kong", ("futuhk.com", "futunn.com", "futustatic.com"), HK),
    Application("HSBC HK", "Hong Kong", ("hsbc.com.hk", "hsbc.com"), HK),
    Application("Longbridge", "Hong Kong", ("longbridge.hk", "longbridge.com", "longbridge.sg", "longportapp.com"), HK),
    Application("IBKR", "Res-Frontier", ("ibkr.com", "interactivebrokers.com", "ibkrguides.com", "ibllc.com"), US),
    Application("Kalshi", "Res-Frontier", ("kalshi.com", "api.kalshi.com"), US),
    Application("SoFi", "Res-Frontier", ("sofi.com", "www.sofi.com"), US),
    Application("Wise", "Res-Frontier", ("wise.com", "www.wise.com"), US_CONTEXT),
    Application("Revolut", "Res-Frontier", ("revolut.com", "api.revolut.com"), US_CONTEXT),
    Application("Capital One", "Res-Frontier", ("capitalone.com", "capitalone360.com", "capitalonebank.com"), US),
    Application("Coinbase", "Res-Frontier", ("coinbase.com", "api.coinbase.com", "base.app"), US),
    Application("ether.fi", "Res-Frontier", ("ether.fi", "app.ether.fi", "etherfi.gitbook.io"), US),
    Application("LemFi", "Res-Frontier", ("lemfi.com", "mobile.lemfi.com", "lemonade.finance", "app.lemonade.finance"), US),
    Application("PayPal", "Res-Frontier", ("paypal.com", "api.paypal.com", "paypalobjects.com"), US),
    Application("Polymarket", "Res-Frontier", ("polymarket.com", "polymarket.us"), US),
    Application("Bank of China", "DIRECT", ("boc.cn", "bankofchina.com"), CN),
    Application("China Merchants Bank", "DIRECT", ("cmbchina.com", "cmbchina.com.cn"), CN),
    Application("UnionPay", "DIRECT", ("unionpay.com", "www.unionpay.com"), CN),
    Application("HSBC UK", "United Kingdom", ("hsbc.co.uk", "www.hsbc.co.uk"), UK),
    Application("Krak / Kraken", "United Kingdom", ("krak.app", "kraken.com", "kraken.onl", "kraken.zendesk.com"), UK),
    Application("Lloyds", "United Kingdom", ("lloydsbank.com", "lloydsbank.co.uk", "securemail.lloydsbanking.com"), UK),
    Application("Monzo", "United Kingdom", ("monzo.com", "monzo.me", "api.sta.monzo-alt.net"), UK),
)

# All 21 IBKR records that existed across Finance/HK/UK/SG/JP before this
# owner-directed move. Keep this golden inventory fixed; deriving it by scanning
# the new destination would silently bless dropped regional entries.
IBKR_ENTRIES = frozenset({
    ".ibkr.com", ".interactivebrokers.com", ".ibkr.ca", ".ibkr.co.in",
    ".ibkr.com.au", ".ibkr.eu", ".ibkr.ie", ".ibkrguides.com", ".ibllc.com",
    ".interactivebrokers.ca", ".interactivebrokers.co.in",
    ".interactivebrokers.com.au", ".interactivebrokers.eu", ".interactivebrokers.ie",
    ".ibkr.com.hk", ".interactivebrokers.com.hk", ".ibkr.co.uk",
    ".interactivebrokers.co.uk", ".ibkr.com.sg", ".interactivebrokers.com.sg",
    ".interactivebrokers.co.jp",
})

MOVED_ENTRIES = {
    **{entry: ("Res-Frontier", "us-residential.conf") for entry in IBKR_ENTRIES},
    ".bankofchina.com": ("DIRECT", "direct-cn.conf"),
    ".longbridge.sg": ("Hong Kong", "hk-finance.conf"),
}

# Separate from the preexisting/migrated inventory: each reviewed addition must
# exist as this exact record, not merely pass because a wider parent captures it.
ADDED_ENTRIES = {
    "za.onelink.me": ("Hong Kong", "hk-finance.conf"),
    "cdn.zaticdn.com": ("Hong Kong", "hk-finance.conf"),
    "alicdn.zaticdn.com": ("Hong Kong", "hk-finance.conf"),
    "s3gw.cmbimg.cn": ("DIRECT", "direct-cn.conf"),
    "cmbt.cn": ("DIRECT", "direct-cn.conf"),
    "forms.hsbc.gb": ("United Kingdom", "uk-finance.conf"),
    ".kalshi.com": ("Res-Frontier", "us-residential.conf"),
    ".transferwise.com": ("Res-Frontier", "us-residential.conf"),
    ".revolut.me": ("Res-Frontier", "us-residential.conf"),
    ".ibllc.com.cn": ("Res-Frontier", "us-residential.conf"),
    "wise-app.sng.link": ("Res-Frontier", "us-residential.conf"),
    "sofi.app.link": ("Res-Frontier", "us-residential.conf"),
    "sofi-alternate.app.link": ("Res-Frontier", "us-residential.conf"),
}

# Service tenants can be added as exact hosts; their multi-company parent
# namespaces must not become a blanket owner-specific routing shortcut.
SHARED_PROVIDERS = frozenset({
    "amazonaws.com", "app.link", "auth0.com", "azureedge.net",
    "cloudfront.net", "github.io", "gitbook.io", "googleapis.com",
    "googleusercontent.com", "medallia.com", "notion.site", "onelink.me",
    "sentry.io", "sng.link", "statuspage.io", "typeform.com", "zendesk.com",
})


class OwnerFinanceMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((ROOT / "rules-manifest.json").read_text())
        cls.profiles = {
            name: read_profile_rules(ROOT / cls.manifest[name], cls.manifest)
            for name in ("main", "expanded")
        }
        cls.active_rules = {
            item["file"]: local_hostname_rules(ROOT / item["file"])
            for item in cls.manifest["active"]
        }
        cls.active_entries = {
            item["file"]: entries(ROOT / item["file"])
            for item in cls.manifest["active"]
        }

    def test_fixed_inventory_has_all_24_requested_apps_and_region_counts(self) -> None:
        self.assertEqual(24, len(APPLICATIONS))
        self.assertEqual(24, len({app.name for app in APPLICATIONS}))
        self.assertEqual(
            {"Hong Kong": 6, "Res-Frontier": 11, "DIRECT": 3, "United Kingdom": 4},
            dict(Counter(app.policy for app in APPLICATIONS)),
        )
        self.assertTrue(all(app.hosts and app.sources for app in APPLICATIONS))

    def test_all_requested_apps_first_match_their_owner_selected_policy(self) -> None:
        for app in APPLICATIONS:
            for host in app.hosts:
                for profile, rules in self.profiles.items():
                    with self.subTest(app=app.name, host=host, profile=profile):
                        policy, source = first_match(rules, host)
                        self.assertEqual(app.policy, policy)
                        self.assertIn(source, app.sources)

    def test_all_21_preexisting_ibkr_records_are_in_us_residential_once(self) -> None:
        self.assertEqual(21, len(IBKR_ENTRIES))
        for entry in IBKR_ENTRIES:
            with self.subTest(entry=entry):
                self.assertEqual(1, self.active_entries["us-residential.conf"].count(entry))

    def test_migrated_entries_have_one_exact_record_in_one_active_list(self) -> None:
        for entry, (_, expected_source) in MOVED_ENTRIES.items():
            owners = [
                source for source, records in self.active_entries.items()
                for record in records if record == entry
            ]
            with self.subTest(entry=entry):
                self.assertEqual([expected_source], owners)

    def test_migrated_suffixes_have_no_shadow_or_redundant_active_owner(self) -> None:
        for entry, expected in MOVED_ENTRIES.items():
            root = entry.removeprefix(".")
            for host in (root, "fixture-child." + root, "deep.fixture-child." + root):
                owners = [
                    source for source, rules in self.active_rules.items()
                    for rule in rules if rule.matches(host)
                ]
                with self.subTest(entry=entry, host=host):
                    self.assertEqual([expected[1]], owners)
                for profile, rules in self.profiles.items():
                    with self.subTest(entry=entry, host=host, profile=profile):
                        self.assertEqual(expected, first_match(rules, host))

    def test_shared_cloud_and_service_namespaces_are_not_blanket_captured(self) -> None:
        for provider in SHARED_PROVIDERS:
            for host in (provider, "unrelated-tenant." + provider):
                for source, rules in self.active_rules.items():
                    with self.subTest(host=host, source=source):
                        self.assertFalse(any(rule.matches(host) for rule in rules))
                for profile, rules in self.profiles.items():
                    with self.subTest(host=host, profile=profile):
                        self.assertEqual(UNKNOWN, first_match(rules, host)[0])

    def test_migrated_names_do_not_capture_lookalikes_or_suffixed_attack_domains(self) -> None:
        for entry in MOVED_ENTRIES:
            root = entry.removeprefix(".")
            for host in ("not" + root, root + ".example.net"):
                for source, rules in self.active_rules.items():
                    with self.subTest(host=host, source=source):
                        self.assertFalse(any(rule.matches(host) for rule in rules))
                for profile, rules in self.profiles.items():
                    with self.subTest(host=host, profile=profile):
                        self.assertEqual(UNKNOWN, first_match(rules, host)[0])

    def test_all_13_reviewed_additions_exist_once_with_exact_matcher_type(self) -> None:
        self.assertEqual(13, len(ADDED_ENTRIES))
        self.assertEqual(4, sum(entry.startswith(".") for entry in ADDED_ENTRIES))
        for entry, (_, expected_source) in ADDED_ENTRIES.items():
            owners = [
                source for source, records in self.active_entries.items()
                for record in records if record == entry
            ]
            host = entry.removeprefix(".")
            expected_kind = "DOMAIN-SUFFIX" if entry.startswith(".") else "DOMAIN"
            matches = [
                (source, rule.kind, rule.value)
                for source, rules in self.active_rules.items()
                for rule in rules if rule.matches(host)
            ]
            with self.subTest(entry=entry):
                self.assertEqual([expected_source], owners)
                self.assertEqual([(expected_source, expected_kind, host)], matches)

    def test_reviewed_additions_and_only_suffix_children_use_selected_policy(self) -> None:
        for entry, expected in ADDED_ENTRIES.items():
            root = entry.removeprefix(".")
            hosts = [root]
            if entry.startswith("."):
                hosts.extend(("fixture-child." + root, "deep.fixture-child." + root))
            for host in hosts:
                owners = [
                    source for source, rules in self.active_rules.items()
                    for rule in rules if rule.matches(host)
                ]
                with self.subTest(entry=entry, host=host):
                    self.assertEqual([expected[1]], owners)
                for profile, rules in self.profiles.items():
                    with self.subTest(entry=entry, host=host, profile=profile):
                        self.assertEqual(expected, first_match(rules, host))

    def test_exact_additions_do_not_absorb_children_neighbors_or_parent_namespace(self) -> None:
        for entry in ADDED_ENTRIES:
            if entry.startswith("."):
                continue
            hosts = {"fixture-child." + entry, "deep.fixture-child." + entry,
                     "not" + entry, entry + ".example.net"}
            parent = entry.split(".", 1)[1]
            if "." in parent:
                hosts.update((parent, "unrelated-tenant." + parent))
            for host in hosts:
                for source, rules in self.active_rules.items():
                    with self.subTest(entry=entry, host=host, source=source):
                        self.assertFalse(any(rule.matches(host) for rule in rules))
                for profile, rules in self.profiles.items():
                    with self.subTest(entry=entry, host=host, profile=profile):
                        self.assertEqual(UNKNOWN, first_match(rules, host)[0])

    def test_new_suffixes_reject_lookalikes_and_kalshi_demo_is_not_added(self) -> None:
        hosts = {"kalshi.co", "demo.kalshi.co"}
        for entry in ADDED_ENTRIES:
            if entry.startswith("."):
                root = entry.removeprefix(".")
                hosts.update(("not" + root, root + ".example.net"))
        for host in hosts:
            for source, rules in self.active_rules.items():
                with self.subTest(host=host, source=source):
                    self.assertFalse(any(rule.matches(host) for rule in rules))
            for profile, rules in self.profiles.items():
                with self.subTest(host=host, profile=profile):
                    self.assertEqual(UNKNOWN, first_match(rules, host)[0])


if __name__ == "__main__":
    unittest.main()
