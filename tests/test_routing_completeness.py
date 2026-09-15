"""Offline ordinary-hostname acceptance, not an effective Surge/login trace.

The model assumes HTTPS over TCP port 443. It stops at the FIRST external
resource: skipping unknown remote content would create false first matches.
Injected modules/pre-matching, IP/DNS, the chosen proxy, and app sessions are
deliberately outside this test. Passing does not clear the pending device items.
"""

from __future__ import annotations

import csv
import copy
import fnmatch
import json
import unittest
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UNKNOWN = "unresolved_before_external"
HOST_TYPES = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-WILDCARD"}
MEXC_ENTRIES = {
    ".mexc.com", ".mexc.co", ".mexc.fm", ".mexcsensors.com", ".mexc.in",
    "static.mocortech.com", "public.mocortech.com",
    "customer-article.mocortech.com", "learn.mocortech.com",
    "s3-app-release.s3.ap-northeast-1.amazonaws.com",
    "mexc-front-static.s3.ap-northeast-1.amazonaws.com",
    "mexc-rainbown-activityimages.s3.ap-northeast-1.amazonaws.com",
    "mexc-static-learn.s3.ap-northeast-1.amazonaws.com",
    "mexc.onelink.me", "mexcdevelop.github.io",
}
# Independent acceptance expectations: do not derive these from the manifest or
# from the editable JSON fixture being checked. Route + fixture changes together
# must not silently bless a new policy, owner, or missing requested application.
REQUIRED_CASES = {
    "Mainland China finance": ("DIRECT", "direct-cn.conf", {"boc.cn", "icbc.com.cn", "unionpay.com"}),
    "MEXC": ("Switzerland", "ch-finance.conf", {"mexc.com", "static.mocortech.com"}),
    "N26": ("United Kingdom", "uk-finance.conf", {"n26.com", "app.n26.com", "cdn.number26.de"}),
    "Loqbox": ("United Kingdom", "uk-finance.conf", {"loqbox.com", "app.uk.loqbox.com"}),
    "Kraken and Krak": ("United Kingdom", "uk-finance.conf", {"kraken.com", "krak.app"}),
    "Monzo": ("United Kingdom", "uk-finance.conf", {"monzo.com", "api.sta.monzo-alt.net"}),
    "Lloyds": ("United Kingdom", "uk-finance.conf", {"lloydsbank.com", "securemail.lloydsbanking.com"}),
    "HSBC Expat narrow UK exception": ("United Kingdom", "uk-finance.conf", {"expat.hsbc.com"}),
    "HSBC Hong Kong and shared parent": ("Hong Kong", "hk-finance.conf", {"hsbc.com", "hsbc.com.hk"}),
    "Coinbase and Base App": ("Res-Frontier", "us-residential.conf", {"coinbase.com", "base.app"}),
    "ether.fi": ("Res-Frontier", "us-residential.conf", {"ether.fi", "etherfi.gitbook.io"}),
    "LemFi": ("Res-Frontier", "us-residential.conf", {"lemfi.com", "mobile.lemfi.com", "asset.lemfi.com", "support.lemfi.com", "lemonade.finance", "app.lemonade.finance", "referral.lemonade.finance", "lemfi.onelink.me", "lemonadefi.app.link", "lemonadefi-alternate.app.link", "d1c5a9xrl5sbk8.cloudfront.net", "lemonadefinancehelp.zendesk.com"}),
    "OnePay": ("Res-Frontier", "us-residential.conf", {"onepay.com", "onefinance.com"}),
    "Capital One and Equifax": ("Res-Frontier", "us-residential.conf", {"capitalone.com", "equifax.com"}),
    "PayPal": ("Res-Frontier", "us-residential.conf", {"paypal.com", "api.paypal.com"}),
    "X": ("Res-Frontier", "us-residential.conf", {"x.com", "twitter.com"}),
    "Google Account and Voice control plane": ("Res-Frontier", "us-residential.conf", {"accounts.google.com", "voice.google.com"}),
    "Polymarket international and US": ("Res-Frontier", "us-residential.conf", {"polymarket.com", "polymarket.us"}),
    "Hong Kong brokerage context": ("Hong Kong", "hk-finance.conf", {"futuhk.com", "moomoo.com", "longbridge.hk"}),
    "Singapore brokerage exceptions": ("Singapore", "sg-finance.conf", {"futusg.com", "moomootrustee.com", "longbridge.sg"}),
    "Japan finance": ("Japan", "jp-finance.conf", {"mufg.jp", "smbc.co.jp", "sonybank.net"}),
    "Korea finance": ("Korea", "kr-finance.conf", {"kakaobank.com", "shinhan.com", "tossbank.com"}),
    "Revolut preserved financial context": ("Res-Frontier", "finance-context.conf", {"revolut.com", "api.revolut.com"}),
    "Bybit preserved Crypto selection": ("Crypto", "crypto.conf", {"bybit.com", "api.bybit.com"}),
    "Apple account and billing narrow override": ("Res-Frontier", "apple-account-payment-rules.conf", {"account.apple.com", "buy.itunes.apple.com", "p71-buy.itunes.apple.com"}),
    "Preserved shared identity fallback, not per-app session evidence": ("Res-Frontier", "identity-context.conf", {"api.sumsub.com", "api.uae.sumsub.com", "stationapi.veriff.com"}),
}


def validate_acceptance_cases(matrix: dict) -> None:
    """Reject vacuous, duplicate, weakened, or self-redefined positive cases."""
    cases = matrix.get("cases")
    if not isinstance(cases, list) or len(cases) != len(REQUIRED_CASES):
        raise ValueError("The complete required application inventory must remain present")
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict) or case.get("app") not in REQUIRED_CASES:
            raise ValueError("Unknown or malformed application case")
        app = case["app"]
        if app in seen:
            raise ValueError(f"Duplicate application case: {app}")
        seen.add(app)
        policy, source, required_hosts = REQUIRED_CASES[app]
        if (case.get("policy"), case.get("file")) != (policy, source):
            raise ValueError(f"Application route expectation changed: {app}")
        hosts = case.get("hosts")
        if not isinstance(hosts, list) or not hosts:
            raise ValueError(f"Application hosts must be a nonempty list: {app}")
        if any(not isinstance(host, str) or not host or host != host.strip()
               for host in hosts):
            raise ValueError(f"Malformed application hostname: {app}")
        if len(hosts) != len(set(hosts)):
            raise ValueError(f"Duplicate application hostname: {app}")
        if not required_hosts.issubset(hosts):
            raise ValueError(f"Required application hostname removed: {app}")
    if seen != set(REQUIRED_CASES):
        raise ValueError("Required application case missing")


def entries(path: Path) -> list[str]:
    return [
        line.strip() for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


@dataclass(frozen=True)
class Rule:
    kind: str
    value: str
    policy: str
    source: str

    def matches(self, host: str) -> bool:
        host = host.lower().rstrip(".")
        value = self.value.lower()
        if self.kind == "DOMAIN":
            return host == value
        if self.kind == "DOMAIN-SUFFIX":
            return host == value or host.endswith("." + value)
        if self.kind == "DOMAIN-WILDCARD":
            return fnmatch.fnmatchcase(host, value)
        return False


def read_profile_rules(path: Path, manifest: dict) -> list[Rule]:
    """Independently resolve local lists, without using the tested generator."""
    base = (
        "https://raw.githubusercontent.com/"
        f"{manifest['repository']}/{manifest['branch']}/"
    )
    bindings = {base + item["file"]: item for item in manifest["active"]}
    rules: list[Rule] = []
    source = path.name
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if raw.startswith("# BEGIN "):
            source = raw[len("# BEGIN "):].split(" -> ", 1)[0]
        elif raw.startswith("# END "):
            source = path.name
        if not raw or raw.startswith(("#", "[")):
            continue
        fields = next(csv.reader([raw], skipinitialspace=True))
        kind, value = fields[:2]
        if kind in {"DOMAIN-SET", "RULE-SET"}:
            binding = bindings.get(value)
            if binding is None:
                if value.startswith(base):
                    raise ValueError(f"Unregistered local resource: {value}")
                rules.append(Rule("EXTERNAL", value, UNKNOWN, value))
                continue
            policy = fields[2]
            if policy != binding["policy"]:
                raise ValueError(f"Policy binding mismatch: {value}")
            if kind != binding.get("type", "DOMAIN-SET"):
                raise ValueError(f"Resource type mismatch: {value}")
            for entry in entries(path.parent / binding["file"]):
                if kind == "DOMAIN-SET":
                    rule_kind = "DOMAIN-SUFFIX" if entry.startswith(".") else "DOMAIN"
                    domain = entry.removeprefix(".")
                else:
                    parts = next(csv.reader([entry], skipinitialspace=True))
                    rule_kind, domain = parts[:2]
                    if rule_kind not in HOST_TYPES:
                        raise ValueError(f"Unmodelled local matcher: {entry}")
                rules.append(Rule(rule_kind, domain, policy, binding["file"]))
        elif kind in HOST_TYPES:
            rules.append(Rule(kind, value, fields[2], source))
        elif kind == "DEST-PORT" and value == "123":
            continue  # Does not match the explicitly modelled HTTPS port 443.
        elif kind == "PROTOCOL" and value == "MTProto":
            continue  # Does not match the explicitly modelled HTTPS protocol.
        elif kind == "FINAL":
            rules.append(Rule("EXTERNAL", "FINAL", UNKNOWN, "FINAL"))
        else:
            raise ValueError(f"Unmodelled profile matcher: {raw}")
    return rules


def first_match(rules: list[Rule], host: str) -> tuple[str, str]:
    for rule in rules:
        if rule.kind == "EXTERNAL":
            return UNKNOWN, rule.source
        if rule.matches(host):
            return rule.policy, rule.source
    return UNKNOWN, "end-of-model"


class RoutingCompletenessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((ROOT / "rules-manifest.json").read_text())
        cls.matrix = json.loads((ROOT / "routing-acceptance.json").read_text())
        validate_acceptance_cases(cls.matrix)
        cls.main = read_profile_rules(ROOT / cls.manifest["main"], cls.manifest)
        cls.expanded = read_profile_rules(
            ROOT / cls.manifest["expanded"], cls.manifest
        )

    def assert_route(self, host: str, policy: str, source: str) -> None:
        for profile, rules in (("main", self.main), ("expanded", self.expanded)):
            with self.subTest(profile=profile, host=host):
                self.assertEqual((policy, source), first_match(rules, host))

    def test_known_app_hostname_matrix_in_both_profiles(self) -> None:
        for case in self.matrix["cases"]:
            for host in case["hosts"]:
                with self.subTest(app=case["app"]):
                    self.assert_route(host, case["policy"], case["file"])

    def test_application_inventory_cannot_be_emptied_removed_or_duplicated(self) -> None:
        for replacement in ([], self.matrix["cases"][:-1],
                            self.matrix["cases"][:-1] + self.matrix["cases"][:1]):
            matrix = copy.deepcopy(self.matrix)
            matrix["cases"] = replacement
            with self.subTest(case_count=len(replacement)), self.assertRaises(ValueError):
                validate_acceptance_cases(matrix)

    def test_each_application_cannot_redefine_policy_source_or_clear_hosts(self) -> None:
        for index, case in enumerate(self.matrix["cases"]):
            for field, value in (("policy", "unexpected-policy"),
                                 ("file", "unexpected-source.conf"), ("hosts", [])):
                matrix = copy.deepcopy(self.matrix)
                matrix["cases"][index][field] = value
                with self.subTest(app=case["app"], field=field), self.assertRaises(ValueError):
                    validate_acceptance_cases(matrix)

    def test_nonempty_hosts_cannot_disguise_a_removed_business_anchor(self) -> None:
        for index, case in enumerate(self.matrix["cases"]):
            matrix = copy.deepcopy(self.matrix)
            matrix["cases"][index]["hosts"] = ["unrelated.example.net"]
            with self.subTest(app=case["app"]), self.assertRaises(ValueError):
                validate_acceptance_cases(matrix)

    def test_mexc_inventory_and_every_current_record(self) -> None:
        current = entries(ROOT / "ch-finance.conf")
        self.assertEqual(len(current), len(set(current)))
        self.assertEqual(MEXC_ENTRIES, set(current))
        self.assertEqual(15, len(current))
        for entry in current:
            # Every current record is exercised, not only the hand-picked matrix.
            host = entry.removeprefix(".")
            self.assert_route(host, "Switzerland", "ch-finance.conf")
            if entry.startswith("."):
                self.assert_route("fixture-child." + host, "Switzerland", "ch-finance.conf")
            else:
                for rules in (self.main, self.expanded):
                    self.assertEqual(UNKNOWN, first_match(rules, "fixture-child." + host)[0])
            for rules in (self.main, self.expanded):
                self.assertEqual(UNKNOWN, first_match(rules, host + ".example.net")[0])

    def test_adjacent_domains_and_shared_tenants_not_captured(self) -> None:
        for host in self.matrix["negative_hosts"]:
            for profile, rules in (("main", self.main), ("expanded", self.expanded)):
                with self.subTest(profile=profile, host=host):
                    self.assertEqual(UNKNOWN, first_match(rules, host)[0])

    def test_apple_rule_set_remains_exactly_six_narrow_matchers(self) -> None:
        expected = {
            "DOMAIN,account.apple.com,extended-matching",
            "DOMAIN,appleid.cdn-apple.com,extended-matching",
            "DOMAIN,idmsa.apple.com,extended-matching",
            "DOMAIN,gsa.apple.com,extended-matching",
            "DOMAIN,buy.itunes.apple.com,extended-matching",
            "DOMAIN-WILDCARD,*-buy.itunes.apple.com,extended-matching",
        }
        actual = entries(ROOT / "apple-account-payment-rules.conf")
        self.assertEqual(6, len(actual))
        self.assertEqual(expected, set(actual))

    def test_financial_order_and_apple_override_precede_unknown_upstreams(self) -> None:
        expected = [
            "direct-cn.conf", "ch-finance.conf", "uk-finance.conf", "hk-finance.conf",
            "sg-finance.conf", "jp-finance.conf", "kr-finance.conf", "us-residential.conf",
            "apple-account-payment-rules.conf", "finance-context.conf",
            "identity-context.conf", "risk-context.conf", "crypto.conf", "web3.conf",
        ]
        for profile, rules in (("main", self.main), ("expanded", self.expanded)):
            with self.subTest(profile=profile):
                positions = [next(i for i, rule in enumerate(rules) if rule.source == source)
                             for source in expected]
                self.assertEqual(sorted(positions), positions)
                boundary = next(i for i, rule in enumerate(rules) if rule.kind == "EXTERNAL")
                self.assertLess(max(positions), boundary)

    def test_shared_authentication_preserved_and_unresolved_items_stay_explicit(self) -> None:
        pending = {item["host"]: item for item in self.matrix["pending_device_verification"]}
        expected_hosts = {
            "authentication-service.eks.core-production.keyless.technology",
            "cdn.veriff.me", "api.sumsub.com", "stationapi.veriff.com",
        }
        self.assertEqual(expected_hosts, set(pending))
        for host, item in pending.items():
            self.assertEqual("pending", item["status"])
            self.assertTrue(item["reason"])
            if item["static_expectation"] == UNKNOWN:
                for rules in (self.main, self.expanded):
                    self.assertEqual(UNKNOWN, first_match(rules, host)[0])
            else:
                self.assertEqual("preserved_identity_fallback", item["static_expectation"])
                self.assert_route(host, "Res-Frontier", "identity-context.conf")

    def test_shared_identity_roots_cannot_be_assigned_to_uk_or_switzerland(self) -> None:
        providers = ("sumsub.com", "veriff.com", "veriff.me", "keyless.technology")
        for source in ("uk-finance.conf", "ch-finance.conf"):
            for entry in entries(ROOT / source):
                domain = entry.removeprefix(".")
                with self.subTest(source=source, entry=entry):
                    self.assertFalse(any(domain == root or domain.endswith("." + root)
                                         for root in providers))

    def test_main_and_committed_expanded_agree_for_the_entire_acceptance_matrix(self) -> None:
        hosts = list(self.matrix["negative_hosts"])
        hosts += [host for case in self.matrix["cases"] for host in case["hosts"]]
        hosts += [item["host"] for item in self.matrix["pending_device_verification"]]
        for host in hosts:
            with self.subTest(host=host):
                self.assertEqual(first_match(self.main, host), first_match(self.expanded, host))

    def test_unknown_external_content_is_never_silently_skipped(self) -> None:
        rules = [Rule("EXTERNAL", "https://example.net/rules", UNKNOWN, "remote"),
                 Rule("DOMAIN", "mexc.com", "Switzerland", "ch-finance.conf")]
        self.assertEqual((UNKNOWN, "remote"), first_match(rules, "mexc.com"))

    def test_suffix_and_exact_match_boundaries(self) -> None:
        suffix = Rule("DOMAIN-SUFFIX", "mexc.com", "Switzerland", "fixture")
        exact = Rule("DOMAIN", "cdn.veriff.me", "fixture", "fixture")
        self.assertTrue(suffix.matches("API.MEXC.COM."))
        self.assertFalse(suffix.matches("notmexc.com"))
        self.assertFalse(suffix.matches("mexc.com.example.net"))
        self.assertTrue(exact.matches("cdn.veriff.me"))
        self.assertFalse(exact.matches("child.cdn.veriff.me"))

    def test_matrix_declares_its_non_runtime_scope(self) -> None:
        self.assertEqual(1, self.matrix["schema_version"])
        self.assertIn("not evidence", self.matrix["evidence_scope"])
        self.assertIn("module injection and pre-matching", self.matrix["excluded_layers"])
        self.assertIn("iPhone capture and login/KYC/payment sessions", self.matrix["excluded_layers"])


if __name__ == "__main__":
    unittest.main()
