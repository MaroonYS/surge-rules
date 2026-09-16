"""Apple is delegated to Sukka without weakening owner-selected finance routes.

This is a local routing contract, not a live Surge/session test or an evaluation
of downloaded Sukka content. UNKNOWN means no custom rule captured the hostname
before the first external resource; it does not claim which upstream rule wins.
"""

from __future__ import annotations

import csv
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

from test_lemfi_routing import local_hostname_rules  # noqa: E402
from test_owner_finance_matrix import APPLICATIONS  # noqa: E402
from test_routing_completeness import (  # noqa: E402
    UNKNOWN, entries, first_match, read_profile_rules,
)


RETIRED_RESOURCE = "apple-account-payment-rules.conf"
SUKKA_APPLE_RULES = (
    ("DOMAIN-SET", "https://ruleset.skk.moe/List/domainset/apple_cdn.conf", "DIRECT"),
    ("DOMAIN-SET", "https://ruleset.skk.moe/List/domainset/icloud_private_relay.conf", "United States", "extended-matching"),
    ("RULE-SET", "https://ruleset.skk.moe/List/non_ip/apple_intelligence.conf", "United States", "extended-matching"),
    ("RULE-SET", "https://ruleset.skk.moe/List/non_ip/apple_cn.conf", "DIRECT"),
    ("RULE-SET", "https://ruleset.skk.moe/List/non_ip/apple_services.conf", "United States"),
)

# Frozen minimum inventory: preserve every already-enabled Sukka resource, not
# just equivalent hostname coverage. Private Relay was previously device-only.
SUKKA_REQUIRED_RESOURCES = {
    "domainset": (
        "reject", "reject_extra", "reject_phishing", "speedtest", "cdn",
        "apple_cdn", "icloud_private_relay", "download",
    ),
    "non_ip": (
        "reject-drop", "reject", "reject-no-drop", "cdn", "stream", "ai",
        "apple_intelligence", "telegram", "apple_cn", "apple_services",
        "microsoft_cdn", "microsoft", "download", "lan", "domestic", "direct",
        "global",
    ),
    "ip": ("reject", "stream", "ai", "telegram", "lan", "domestic", "china_ip"),
}

# These are namespace boundaries, not newly installed routing suffixes.
APPLE_NAMESPACES = frozenset({
    "apple.com", "cdn-apple.com", "aaplimg.com", "mzstatic.com",
    "icloud.com", "icloud-content.com", "apple-cloudkit.com", "apple-dns.net",
    "apple-mapkit.com", "apple.news",
})

# Three retired finance records and six retired account/billing matchers.
# Exact and suffix semantics are explicit so a renamed resource, changed policy,
# or narrower-looking reintroduction cannot silently reinstate the override.
REMOVED_MATCHERS = (
    ("DOMAIN-SUFFIX", "applecash.apple.com"),
    ("DOMAIN-SUFFIX", "applepay.apple.com"),
    ("DOMAIN", "apple-pay-gateway.apple.com"),
    ("DOMAIN", "account.apple.com"),
    ("DOMAIN", "appleid.cdn-apple.com"),
    ("DOMAIN", "idmsa.apple.com"),
    ("DOMAIN", "gsa.apple.com"),
    ("DOMAIN", "buy.itunes.apple.com"),
    ("DOMAIN-WILDCARD", "*-buy.itunes.apple.com"),
)

# Independent minimum contract, not copied from the mutable JSON acceptance
# fixture or inferred from current lists. The owner finance tests may grow their
# coverage but must retain all 24 applications, policies, and these anchors.
FINANCE_ANCHORS = {
    "BOCHK": ("Hong Kong", "bochk.com"),
    "ZA": ("Hong Kong", "zabank.com"),
    "Reward+": ("Hong Kong", "hsbc.com.hk"),
    "Futubull": ("Hong Kong", "futunn.com"),
    "HSBC HK": ("Hong Kong", "hsbc.com.hk"),
    "Longbridge": ("Hong Kong", "longbridge.sg"),
    "IBKR": ("Res-Frontier", "interactivebrokers.com"),
    "Kalshi": ("Res-Frontier", "kalshi.com"),
    "SoFi": ("Res-Frontier", "sofi.com"),
    "Wise": ("Res-Frontier", "wise.com"),
    "Revolut": ("Res-Frontier", "revolut.com"),
    "Capital One": ("Res-Frontier", "capitalone.com"),
    "Coinbase": ("Res-Frontier", "coinbase.com"),
    "ether.fi": ("Res-Frontier", "ether.fi"),
    "LemFi": ("Res-Frontier", "lemfi.com"),
    "PayPal": ("Res-Frontier", "paypal.com"),
    "Polymarket": ("Res-Frontier", "polymarket.us"),
    "Bank of China": ("DIRECT", "bankofchina.com"),
    "China Merchants Bank": ("DIRECT", "cmbchina.com"),
    "UnionPay": ("DIRECT", "unionpay.com"),
    "HSBC UK": ("United Kingdom", "hsbc.co.uk"),
    "Krak / Kraken": ("United Kingdom", "krak.app"),
    "Lloyds": ("United Kingdom", "lloydsbank.com"),
    "Monzo": ("United Kingdom", "monzo.com"),
}


def parsed_rules(text: str) -> list[tuple[str, ...]]:
    return [
        tuple(next(csv.reader([line.strip()], skipinitialspace=True)))
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "["))
    ]


def apple_probes() -> set[str]:
    probes = {
        "itunes.apple.com", "music.apple.com", "courier.push.apple.com",
        "mask.icloud.com", "gateway.icloud.com", "p71.itunes.apple.com",
    }
    for namespace in APPLE_NAMESPACES:
        probes.update((namespace, "fixture-child." + namespace))
    for kind, value in REMOVED_MATCHERS:
        if kind == "DOMAIN-WILDCARD":
            probes.update(value.replace("*", prefix) for prefix in ("p71", "p12", "fixture"))
        else:
            probes.add(value)
            if kind == "DOMAIN-SUFFIX":
                probes.add("fixture-child." + value)
    return probes


class AppleSukkaOnlyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((ROOT / "rules-manifest.json").read_text())
        cls.profile_texts = {
            key: (ROOT / cls.manifest[key]).read_text()
            for key in ("main", "expanded")
        }
        cls.profiles = {
            key: read_profile_rules(ROOT / cls.manifest[key], cls.manifest)
            for key in ("main", "expanded")
        }
        contract = json.loads((ROOT / "rules-contract.json").read_text())
        cls.contract_text = "\n".join(
            rule for section in contract["sections"] for rule in section["rules"]
        )
        cls.active_rules = {
            item["file"]: local_hostname_rules(ROOT / item["file"])
            for item in cls.manifest["active"]
        }

    def test_manifest_has_15_domain_sets_and_no_local_apple_ruleset(self) -> None:
        active = self.manifest["active"]
        self.assertEqual(15, len(active))
        self.assertEqual(15, len({item["file"] for item in active}))
        self.assertTrue(all(item.get("type", "DOMAIN-SET") == "DOMAIN-SET" for item in active))
        self.assertNotIn(RETIRED_RESOURCE, {item["file"] for item in active})
        self.assertFalse(any("APPLE" in item.get("semantic_role", "").upper() for item in active))

    def test_retired_resource_is_not_referenced_or_expanded_and_if_kept_is_empty(self) -> None:
        for label, text in {**self.profile_texts, "contract": self.contract_text}.items():
            with self.subTest(source=label):
                self.assertNotIn(RETIRED_RESOURCE, text)
        compatibility_file = ROOT / RETIRED_RESOURCE
        if compatibility_file.exists():
            self.assertEqual([], entries(compatibility_file))

    def test_exactly_five_existing_sukka_apple_bindings_remain_in_order(self) -> None:
        for label, text in {**self.profile_texts, "contract": self.contract_text}.items():
            rules = parsed_rules(text)
            apple_refs = [
                rule for rule in rules
                if rule[0] in {"DOMAIN-SET", "RULE-SET"}
                and ("apple" in rule[1].lower() or "icloud_private_relay.conf" in rule[1])
            ]
            with self.subTest(source=label):
                self.assertEqual(list(SUKKA_APPLE_RULES), apple_refs)
                first_ip = next(
                    index for index, rule in enumerate(rules)
                    if rule[0] == "RULE-SET" and "/List/ip/" in rule[1]
                )
                self.assertLess(max(rules.index(rule) for rule in SUKKA_APPLE_RULES), first_ip)

    def test_all_existing_sukka_resources_are_retained_once(self) -> None:
        required = {
            ("DOMAIN-SET" if category == "domainset" else "RULE-SET",
             f"https://ruleset.skk.moe/List/{category}/{name}.conf")
            for category, names in SUKKA_REQUIRED_RESOURCES.items()
            for name in names
        }
        self.assertEqual(32, len(required))
        for label, text in {**self.profile_texts, "contract": self.contract_text}.items():
            references = [
                rule[:2] for rule in parsed_rules(text)
                if rule[0] in {"DOMAIN-SET", "RULE-SET"}
                and rule[1].startswith("https://ruleset.skk.moe/")
            ]
            with self.subTest(source=label):
                self.assertTrue(required.issubset(set(references)), required - set(references))
                self.assertEqual(len(references), len(set(references)))

    def test_no_active_custom_matcher_targets_known_apple_namespaces(self) -> None:
        for source, rules in self.active_rules.items():
            for rule in rules:
                value = rule.value.lower().lstrip("*.")
                with self.subTest(source=source, kind=rule.kind, value=rule.value):
                    self.assertFalse(any(
                        value == namespace or value.endswith("." + namespace)
                        for namespace in APPLE_NAMESPACES
                    ))
                    self.assertFalse(any(rule.matches(host) for host in apple_probes()))

    def test_retired_three_plus_six_cannot_return_under_another_resource_or_policy(self) -> None:
        self.assertEqual(9, len(REMOVED_MATCHERS))
        for source, rules in self.active_rules.items():
            for kind, value in REMOVED_MATCHERS:
                with self.subTest(source=source, kind=kind, value=value):
                    self.assertNotIn((kind, value), [(rule.kind, rule.value) for rule in rules])
        for profile, rules in self.profiles.items():
            local = [rule for rule in rules if rule.kind != "EXTERNAL"]
            for host in apple_probes():
                with self.subTest(profile=profile, host=host):
                    self.assertFalse(any(rule.matches(host) for rule in local))
                    self.assertEqual(UNKNOWN, first_match(rules, host)[0])

    def test_owner_finance_matrix_keeps_all_24_non_apple_app_contracts(self) -> None:
        self.assertEqual(24, len(FINANCE_ANCHORS))
        self.assertEqual(24, len(APPLICATIONS))
        indexed = {app.name: app for app in APPLICATIONS}
        self.assertEqual(set(FINANCE_ANCHORS), set(indexed))
        for app_name, (policy, host) in FINANCE_ANCHORS.items():
            with self.subTest(app=app_name):
                self.assertEqual(policy, indexed[app_name].policy)
                self.assertIn(host, indexed[app_name].hosts)
            for profile, rules in self.profiles.items():
                with self.subTest(app=app_name, host=host, profile=profile):
                    self.assertEqual(policy, first_match(rules, host)[0])


if __name__ == "__main__":
    unittest.main()
