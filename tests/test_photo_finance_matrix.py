"""Independent contract for 26 photo-listed apps and 3 preserved crypto apps.

This is an offline, ordinary HTTPS/TCP-443 hostname model. Fixtures are not
evidence of logged-in app requests, KYC/payment completion, selected proxies,
module pre-matching, DNS/IP routing, or remote Sukka contents. TenPayGo fixtures
cover two verified public hosts, not its complete authenticated API surface.
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
    source: str
    hosts: tuple[str, ...]


# These choices come from the owner, not the institution's country of domicile.
# In particular, SGB stays SG and N26 stays UK. The inventory is intentionally
# independent of both editable rule files and routing-acceptance.json.
APPLICATIONS = (
    Application("AlipayHK", "Hong Kong", "hk-finance.conf", ("alipayhk.com", "alipay.hk", "alipayhk.co")),
    Application("ANT BANK", "Hong Kong", "hk-finance.conf", ("antbank.hk", "www.antbank.hk")),
    Application("EleBank", "Hong Kong", "hk-finance.conf", ("elebank.com", "airstarbank.com")),
    Application("FSM", "Hong Kong", "hk-finance.conf", ("fsmone.com.hk", "fsmglobal.hk", "secure.fundsupermart.com.hk")),
    Application("Futubull", "Hong Kong", "hk-finance.conf", ("futuhk.com", "futunn.com", "futustatic.com")),
    Application("Longbridge", "Hong Kong", "hk-finance.conf", ("longbridge.hk", "longbridge.com", "longbridge.sg", "longportapp.com")),
    Application("uSMART HK", "Hong Kong", "hk-finance.conf", ("usmart.hk", "hk.usmartglobal.com", "www.usmartsecurities.com")),
    Application("VBrokers", "Hong Kong", "hk-finance.conf", ("vbkr.com", "valuable.com.hk", "hstong.com")),
    Application("Avalanche Card", "Res-Frontier", "us-residential.conf", ("avalanchecard.com", "www.avalanchecard.com")),
    Application("BBAE Pro", "Res-Frontier", "us-residential.conf", ("bbae.com", "www.bbae.com")),
    Application("Credit Karma", "Res-Frontier", "us-residential.conf", ("creditkarma.com", "www.creditkarma.com")),
    Application("Firstrade", "Res-Frontier", "us-residential.conf", ("firstrade.com", "www.firstrade.com")),
    Application("IBKR", "Res-Frontier", "us-residential.conf", ("ibkr.com", "ibkr.com.hk", "ibkr.com.sg", "interactivebrokers.com", "ibkrguides.com")),
    Application("moomoo", "Res-Frontier", "us-residential.conf", ("moomoo.com", "moomooapp.com", "moomoocn.com", "api.moomoobull.com")),
    Application("myEquifax", "Res-Frontier", "us-residential.conf", ("myequifax.com", "equifax.com")),
    Application("myFICO", "Res-Frontier", "us-residential.conf", ("myfico.com", "www.myfico.com")),
    Application("Neverless", "Res-Frontier", "us-residential.conf", ("neverless.com", "www.neverless.com")),
    Application("Schwab", "Res-Frontier", "us-residential.conf", ("schwab.com", "schwabcdn.com")),
    Application("dtcpay", "Singapore", "sg-finance.conf", ("dtcpay.com", "personal.dtcpay.com", "business.dtcpay.com")),
    Application("SGB", "Singapore", "sg-finance.conf", ("sgb.com", "www.sgb.com", "download.sgb.com")),
    Application("Starryblu", "Singapore", "sg-finance.conf", ("starryblu.com", "h2static.wotransfer.com", "starryblu-public.oss-accelerate.aliyuncs.com")),
    Application("uSMART SG", "Singapore", "sg-finance.conf", ("usmart.sg", "sg.usmartglobal.com", "web-static-sg-prd-singapore-1437682127.cos.accelerate.myqcloud.com", "jy-common-sg-prd-singapore-1437682127.cos.accelerate.myqcloud.com")),
    Application("iFAST GB", "United Kingdom", "uk-finance.conf", ("ifastgb.com", "www.ifastgb.com", "static.ifastgb.com")),
    Application("N26", "United Kingdom", "uk-finance.conf", ("n26.com", "app.n26.com", "api.tech26.n26.com", "cdn.number26.de")),
    Application("Kraken", "United Kingdom", "uk-finance.conf", ("kraken.com", "api.kraken.com", "krak.app", "kraken.onl", "kraken.zendesk.com")),
    Application("TenPayGo", "DIRECT", "direct-cn.conf", ("gtimg.wechatpay.cn", "posts.tenpay.com")),
    Application("Bitget", "Crypto", "crypto.conf", ("bitget.com", "www.bitget.com", "api.bitget.com", "bitgetapp.com")),
    Application("Bybit", "Crypto", "crypto.conf", ("bybit.com", "api.bybit.com", "bybit-global.com", "byapis.com", "byapps.net", "bytick.com")),
    Application("Bitget Wallet", "Web3", "web3.conf", ("web3.bitget.com", "portal-web3.bitget.com", "bitkeep.com", "docs.bitkeep.io", "cdn.bitkeep.vip", "static.bitkeep.vip", "www.bgw.live", "newshare.bwb.global")),
)


REVIEWED_ENTRIES = {
    "hk-finance.conf": frozenset({
        ".alipayhk.com", ".alipay.hk", ".alipayhk.co", ".elebank.com",
        ".fsmone.com.hk", ".fsmglobal.hk", "secure.fundsupermart.com.hk",
        "hk.usmartglobal.com", "www.usmartsecurities.com",
    }),
    "sg-finance.conf": frozenset({
        ".sgb.com", ".starryblu.com", "sg.usmartglobal.com",
        "h2static.wotransfer.com", "starryblu-public.oss-accelerate.aliyuncs.com",
        "web-static-sg-prd-singapore-1437682127.cos.accelerate.myqcloud.com",
        "jy-common-sg-prd-singapore-1437682127.cos.accelerate.myqcloud.com",
    }),
    "uk-finance.conf": frozenset({".ifastgb.com"}),
    "us-residential.conf": frozenset({
        ".avalanchecard.com", ".neverless.com", ".moomoo.com",
        ".moomooapp.com", ".moomoocn.com", ".api.moomoobull.com",
    }),
    "web3.conf": frozenset({
        "web3.bitget.com", "portal-web3.bitget.com", ".bitkeep.com",
        "docs.bitkeep.io", "cdn.bitkeep.vip", "static.bitkeep.vip", "www.bgw.live",
        "newshare.bwb.global",
    }),
    "direct-cn.conf": frozenset({"gtimg.wechatpay.cn", "posts.tenpay.com"}),
}

POLICIES = {
    "hk-finance.conf": "Hong Kong",
    "sg-finance.conf": "Singapore",
    "uk-finance.conf": "United Kingdom",
    "us-residential.conf": "Res-Frontier",
    "web3.conf": "Web3",
    "direct-cn.conf": "DIRECT",
}

# Only these exact-before-broad overlaps are deliberate within this new matrix.
# Their precise kind, value and source are checked, not merely an owner count.
INTENTIONAL_OVERLAPS = {
    "www.usmartsecurities.com": {
        ("hk-finance.conf", "DOMAIN", "www.usmartsecurities.com"),
        ("finance-context.conf", "DOMAIN-SUFFIX", "usmartsecurities.com"),
    },
    "web3.bitget.com": {
        ("web3.conf", "DOMAIN", "web3.bitget.com"),
        ("crypto.conf", "DOMAIN-SUFFIX", "bitget.com"),
    },
    "portal-web3.bitget.com": {
        ("web3.conf", "DOMAIN", "portal-web3.bitget.com"),
        ("crypto.conf", "DOMAIN-SUFFIX", "bitget.com"),
    },
}

SHARED_NEGATIVES = frozenset({
    "usmartglobal.com", "other.usmartglobal.com",
    "fundsupermart.com.hk", "other.fundsupermart.com.hk",
    "wotransfer.com", "other.wotransfer.com",
    "aliyuncs.com", "oss-accelerate.aliyuncs.com",
    "other.oss-accelerate.aliyuncs.com",
    "myqcloud.com", "cos.accelerate.myqcloud.com",
    "other.cos.accelerate.myqcloud.com",
    "bitkeep.io", "other.bitkeep.io", "bitkeep.vip", "other.bitkeep.vip",
    "bgw.live", "other.bgw.live", "number26.de", "other.number26.de",
    "zendesk.com", "other.zendesk.com", "cloudfront.net", "other.cloudfront.net",
    "onelink.me", "other.onelink.me", "amazonaws.com", "other.amazonaws.com",
    "geetest.com", "static.geetest.com", "website-files.com",
    "cdn.prod.website-files.com",
    "wechatpay.cn", "other.wechatpay.cn", "tenpay.com", "other.tenpay.com",
    "moomoobull.com", "www.moomoobull.com", "other.moomoobull.com",
    "bwb.global", "other.bwb.global",
})


class PhotoFinanceMatrixTests(unittest.TestCase):
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
        cls.records = {
            item["file"]: entries(ROOT / item["file"])
            for item in cls.manifest["active"]
        }

    def matches(self, host: str) -> list[tuple[str, str, str]]:
        return [
            (source, rule.kind, rule.value)
            for source, rules in self.active.items()
            for rule in rules if rule.matches(host)
        ]

    def assert_route(self, host: str, policy: str, source: str) -> None:
        for profile, rules in self.profiles.items():
            with self.subTest(profile=profile, host=host):
                self.assertEqual((policy, source), first_match(rules, host))

    def test_fixed_inventory_has_26_selected_apps_and_three_crypto_apps(self) -> None:
        self.assertEqual(29, len(APPLICATIONS))
        self.assertEqual(29, len({app.name for app in APPLICATIONS}))
        self.assertEqual(
            {"Hong Kong": 8, "Res-Frontier": 10, "Singapore": 4,
             "United Kingdom": 3, "DIRECT": 1, "Crypto": 2, "Web3": 1},
            dict(Counter(app.policy for app in APPLICATIONS)),
        )
        self.assertTrue(all(app.hosts for app in APPLICATIONS))

    def test_all_29_apps_first_match_the_selected_policy_in_both_profiles(self) -> None:
        for app in APPLICATIONS:
            for host in app.hosts:
                with self.subTest(app=app.name):
                    self.assert_route(host, app.policy, app.source)

    def test_app_hosts_have_no_duplicate_or_competing_active_owner(self) -> None:
        for app in APPLICATIONS:
            for host in app.hosts:
                matches = self.matches(host)
                with self.subTest(app=app.name, host=host):
                    if host in INTENTIONAL_OVERLAPS:
                        self.assertEqual(2, len(matches))
                        self.assertEqual(INTENTIONAL_OVERLAPS[host], set(matches))
                    else:
                        self.assertEqual([app.source], [item[0] for item in matches])

    def test_all_33_reviewed_records_exist_once_with_the_exact_matcher(self) -> None:
        self.assertEqual(33, sum(map(len, REVIEWED_ENTRIES.values())))
        for source, records in REVIEWED_ENTRIES.items():
            for entry in records:
                root = entry.removeprefix(".")
                kind = "DOMAIN-SUFFIX" if entry.startswith(".") else "DOMAIN"
                owners = [
                    name for name, actual in self.records.items()
                    for record in actual if record == entry
                ]
                expected = INTENTIONAL_OVERLAPS.get(root, {(source, kind, root)})
                with self.subTest(source=source, entry=entry):
                    self.assertEqual([source], owners)
                    actual = self.matches(root)
                    self.assertEqual(len(expected), len(actual))
                    self.assertEqual(expected, set(actual))

    def test_reviewed_roots_and_suffix_children_first_match_expected_source(self) -> None:
        for source, records in REVIEWED_ENTRIES.items():
            for entry in records:
                root = entry.removeprefix(".")
                probes = [root]
                if entry.startswith("."):
                    # Synthetic hosts exercise suffix semantics, not live traffic.
                    probes.extend(("fixture-child." + root, "deep.fixture-child." + root))
                for host in probes:
                    with self.subTest(entry=entry):
                        self.assert_route(host, POLICIES[source], source)

    def test_exact_tenants_never_expand_to_children_or_neighbors(self) -> None:
        for source, records in REVIEWED_ENTRIES.items():
            for entry in records:
                if entry.startswith("."):
                    continue
                for host in ("fixture-child." + entry, "not" + entry, entry + ".example.net"):
                    with self.subTest(entry=entry, host=host):
                        self.assertFalse(any(rule.matches(host) for rule in self.active[source]))
                    # The three documented exceptions deliberately fall back to
                    # another local owner; unrelated exact tenants stay unresolved.
                    if entry not in INTENTIONAL_OVERLAPS:
                        self.assertEqual([], self.matches(host), host)
                        for profile, rules in self.profiles.items():
                            with self.subTest(profile=profile, host=host):
                                self.assertEqual(UNKNOWN, first_match(rules, host)[0])

    def test_shared_provider_roots_and_siblings_are_not_locally_captured(self) -> None:
        for host in SHARED_NEGATIVES:
            with self.subTest(host=host):
                self.assertEqual([], self.matches(host))
            for profile, rules in self.profiles.items():
                with self.subTest(profile=profile, host=host):
                    self.assertEqual(UNKNOWN, first_match(rules, host)[0])

    def test_new_first_party_suffixes_reject_lookalike_and_attack_domains(self) -> None:
        for records in REVIEWED_ENTRIES.values():
            for entry in records:
                if not entry.startswith("."):
                    continue
                root = entry.removeprefix(".")
                for host in ("not" + root, root + ".example.net"):
                    with self.subTest(host=host):
                        self.assertEqual([], self.matches(host))
                    for profile, rules in self.profiles.items():
                        with self.subTest(profile=profile, host=host):
                            self.assertEqual(UNKNOWN, first_match(rules, host)[0])

    def test_usmart_hk_exact_exception_preserves_shared_finance_fallback(self) -> None:
        self.assert_route("www.usmartsecurities.com", "Hong Kong", "hk-finance.conf")
        for host in ("usmartsecurities.com", "api.usmartsecurities.com",
                     "fixture-child.www.usmartsecurities.com"):
            self.assert_route(host, "Res-Frontier", "finance-context.conf")
        self.assert_route("hk.usmartglobal.com", "Hong Kong", "hk-finance.conf")
        self.assert_route("sg.usmartglobal.com", "Singapore", "sg-finance.conf")

    def test_wallet_exact_exceptions_do_not_move_bitget_exchange_or_children(self) -> None:
        for host in ("web3.bitget.com", "portal-web3.bitget.com"):
            self.assert_route(host, "Web3", "web3.conf")
        for host in ("bitget.com", "www.bitget.com", "api.bitget.com",
                     "fixture-child.web3.bitget.com", "fixture-child.portal-web3.bitget.com"):
            self.assert_route(host, "Crypto", "crypto.conf")

    def test_entire_web3_layer_precedes_crypto_without_changing_other_crypto_routes(self) -> None:
        for profile, rules in self.profiles.items():
            positions = {
                source: [index for index, rule in enumerate(rules) if rule.source == source]
                for source in ("web3.conf", "crypto.conf")
            }
            with self.subTest(profile=profile):
                self.assertTrue(positions["web3.conf"])
                self.assertTrue(positions["crypto.conf"])
                self.assertLess(max(positions["web3.conf"]), min(positions["crypto.conf"]))
        self.assert_route("metamask.io", "Web3", "web3.conf")
        self.assert_route("bybit.com", "Crypto", "crypto.conf")
        self.assert_route("binance.com", "Crypto", "crypto.conf")


if __name__ == "__main__":
    unittest.main()
