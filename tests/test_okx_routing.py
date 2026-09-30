"""Owner-selected OKX US routing; offline matching, not an app-session test."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_lemfi_routing import local_hostname_rules  # noqa: E402
from test_routing_completeness import entries, first_match, read_profile_rules  # noqa: E402

# Independent fixed expectations, not inferred from the edited lists.
MIGRATED_SUFFIXES = {
    ".okx.com", ".okex.com", ".okx-dns.com", ".okx-dns1.com",
    ".okx-dns2.com", ".okx.ac", ".okx.cab",
}
EXACT_CDN_HOSTS = {
    "static.coinall.ltd", "static.jingyunyilian.com", "static.okx.reise",
}
REQUIRED_ENTRIES = MIGRATED_SUFFIXES | EXACT_CDN_HOSTS
PROBES = {
    "www.okx.com", "app.okx.com", "web3.okx.com", "us.okx.com",
    "wsus.okx.com", "wsuspap.okx.com", "ws.okx.com", "wspap.okx.com",
    "static.okx.com", "static.okx.ac", "static.okx.cab",
} | {entry.removeprefix(".") for entry in REQUIRED_ENTRIES}
# Synthetic labels exercise suffix semantics, not observed production traffic.
PROBES |= {prefix + entry for entry in MIGRATED_SUFFIXES
           for prefix in ("fixture-child", "deep.fixture-child")}


class OKXRoutingTests(unittest.TestCase):
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
        cls.local_lists = {
            path.name: local_hostname_rules(path)
            for path in ROOT.glob("*.conf")
            if path.name not in {cls.manifest["main"], cls.manifest["expanded"]}
        }

    def test_fixed_inventory_present_once_in_residential_list(self) -> None:
        actual = entries(ROOT / "us-residential.conf")
        for entry in REQUIRED_ENTRIES:
            self.assertEqual(1, actual.count(entry), entry)
        self.assertTrue(MIGRATED_SUFFIXES.isdisjoint(entries(ROOT / "crypto.conf")))

    def test_first_match_us_in_main_and_expanded(self) -> None:
        for name, rules in self.profiles.items():
            for host in PROBES:
                with self.subTest(profile=name, host=host):
                    self.assertEqual(("Res-Frontier", "us-residential.conf"),
                                     first_match(rules, host))

    def test_no_competing_or_duplicate_active_owner(self) -> None:
        for host in PROBES:
            owners = [source for source, rules in self.active.items()
                      for rule in rules if rule.matches(host)]
            self.assertEqual(["us-residential.conf"], owners, host)

    def test_no_legacy_list_retains_migrated_hosts(self) -> None:
        for host in PROBES:
            owners = [source for source, rules in self.local_lists.items()
                      for rule in rules if rule.matches(host)]
            self.assertEqual(["us-residential.conf"], owners, host)

    def test_no_lookalikes_or_whole_cdn_providers_captured(self) -> None:
        negatives = {
            "notokx.com", "okx.com.example.net", "notokex.com",
            "okex.com.example.net", "okx-dns3.com", "okxwallet.com",
            "okxcdn.com", "okxstatic.com", "okcoin.com",
            "oklink.com", "www.oklink.com", "auth0.com", "other.auth0.com",
            "amazonaws.com", "other.amazonaws.com", "cloudflare.com",
            "coinall.ltd", "other.coinall.ltd", "jingyunyilian.com",
            "other.jingyunyilian.com", "okx.reise", "other.okx.reise",
        } | {"child." + host for host in EXACT_CDN_HOSTS}
        negatives |= {host + ".example.net" for host in EXACT_CDN_HOSTS}
        for host in negatives:
            self.assertFalse(any(rule.matches(host)
                                 for rule in self.active["us-residential.conf"]), host)

    def test_other_crypto_web3_and_residential_policies_preserved(self) -> None:
        expected = {
            "api.bybit.com": ("Crypto", "crypto.conf"),
            "api.binance.com": ("Crypto", "crypto.conf"),
            "api.bitget.com": ("Crypto", "crypto.conf"),
            "api.mexc.com": ("Crypto", "crypto.conf"),
            "web3.bitget.com": ("Web3", "web3.conf"),
            "oklink.com": ("Web3", "web3.conf"),
            "www.oklink.com": ("Web3", "web3.conf"),
            "api.coinbase.com": ("Res-Frontier", "us-residential.conf"),
            "api.kraken.com": ("United Kingdom", "uk-finance.conf"),
        }
        for name, rules in self.profiles.items():
            for host, route in expected.items():
                with self.subTest(profile=name, host=host):
                    self.assertEqual(route, first_match(rules, host))


if __name__ == "__main__":
    unittest.main()
