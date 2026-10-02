from __future__ import annotations

import fnmatch
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_expanded  # noqa: E402
import validate  # noqa: E402


FINANCE_ORDER = [
    "direct-cn.conf", "uk-finance.conf", "hk-finance.conf",
    "sg-finance.conf", "jp-finance.conf", "kr-finance.conf", "us-residential.conf",
]
MEXC_ENTRIES = {
    ".mexc.com", ".mexc.co", ".mexc.fm", ".mexcsensors.com", ".mexc.in",
    "static.mocortech.com", "public.mocortech.com", "customer-article.mocortech.com",
    "learn.mocortech.com", "s3-app-release.s3.ap-northeast-1.amazonaws.com",
    "mexc-front-static.s3.ap-northeast-1.amazonaws.com",
    "mexc-rainbown-activityimages.s3.ap-northeast-1.amazonaws.com",
    "mexc-static-learn.s3.ap-northeast-1.amazonaws.com",
    "mexc.onelink.me", "mexcdevelop.github.io", "download.mocortech.com",
    ".mexc.link", ".mexc.cg", ".mexc.ci", ".mexc.sg",
    ".mexc.me", ".mexc.cc", ".mexc.kr", ".mexc.io", ".mexc.ch",
    ".mexc.biz.tr", ".mexc.us",
    "watchman-sdk.gotoda.co", "watchman.gotoda.co",
    "trochilus-web.gotoda.co", "trochi.gotoda.co", "e.gotoda.co",
}


def first_inline_domain_policy(text: str, host: str) -> str | None:
    """Evaluate local domain rules only; not a full Surge runtime simulator."""
    for line in text.splitlines():
        fields = line.split(",")
        if len(fields) < 3:
            continue
        kind, matcher, policy = fields[:3]
        if (
            (kind == "DOMAIN" and host == matcher)
            or (kind == "DOMAIN-SUFFIX" and (host == matcher or host.endswith("." + matcher)))
            or (kind == "DOMAIN-WILDCARD" and fnmatch.fnmatchcase(host, matcher))
        ):
            return policy.strip('"')
    return None


class RoutingContractIntegrityTests(unittest.TestCase):
    def test_finance_order_is_locked_in_manifest_contract_and_main(self) -> None:
        manifest = json.loads((ROOT / "rules-manifest.json").read_text())
        bindings = manifest["active"]
        self.assertEqual(FINANCE_ORDER, [b["file"] for b in bindings if b["file"] in FINANCE_ORDER])
        self.assertEqual("Crypto", next(b["policy"] for b in bindings if b["file"] == "crypto.conf"))
        main = (ROOT / "surge-main.conf").read_text()
        contract = json.loads((ROOT / "rules-contract.json").read_text())
        contract_text = "\n".join(rule for section in contract["sections"] for rule in section["rules"])
        for text in (main, contract_text):
            positions = [text.index("/" + name + ",") for name in FINANCE_ORDER]
            self.assertEqual(positions, sorted(positions))
            self.assertNotIn("/ch-finance.conf,", text)
            self.assertEqual(1, text.count("/crypto.conf,Crypto,extended-matching"))
            self.assertLess(text.index("/web3.conf,"), text.index("/crypto.conf,"))

    def test_crypto_cannot_disappear_from_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "repo"
            shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            path = copied / "rules-manifest.json"
            manifest = json.loads(path.read_text())
            manifest["active"] = [b for b in manifest["active"] if b["file"] != "crypto.conf"]
            path.write_text(json.dumps(manifest))
            codes = {d.code for d in validate.validate_repository(copied).diagnostics}
        self.assertIn("UNKNOWN_LOCAL_REFERENCE", codes)

    def test_mexc_inventory_has_one_active_owner_and_retired_ch_is_empty(self) -> None:
        self.assertEqual(32, len(MEXC_ENTRIES))
        crypto = build_expanded.read_domain_entries(ROOT / "crypto.conf")
        self.assertEqual(43, len(crypto))
        self.assertEqual(len(crypto), len(set(crypto)))
        hk = build_expanded.read_domain_entries(ROOT / "hk-finance.conf")
        self.assertTrue(MEXC_ENTRIES.issubset(hk))
        self.assertEqual(len(hk), len(set(hk)))
        manifest = json.loads((ROOT / "rules-manifest.json").read_text())
        self.assertNotIn("ch-finance.conf", {item["file"] for item in manifest["active"]})
        self.assertEqual([], build_expanded.read_domain_entries(ROOT / "ch-finance.conf"))
        for item in manifest["active"]:
            if item["file"] != "hk-finance.conf":
                with self.subTest(source=item["file"]):
                    self.assertTrue(MEXC_ENTRIES.isdisjoint(
                        build_expanded.read_domain_entries(ROOT / item["file"])))

    def test_mexc_routes_to_hk_in_generated_and_committed_output(self) -> None:
        outputs = {
            "generated": build_expanded.render_expanded(ROOT),
            "committed": (ROOT / "surge-expanded.conf").read_text(),
        }
        for label, text in outputs.items():
            for entry in sorted(MEXC_ENTRIES):
                hosts = [entry.removeprefix(".")]
                if entry.startswith("."):
                    hosts.append("api" + entry)
                for host in hosts:
                    with self.subTest(output=label, host=host):
                        self.assertEqual("Hong Kong", first_inline_domain_policy(text, host))
                if not entry.startswith("."):
                    with self.subTest(output=label, exact_host=entry):
                        self.assertIsNone(first_inline_domain_policy(text, "child." + entry))
                with self.subTest(output=label, unrelated=entry):
                    self.assertIsNone(first_inline_domain_policy(
                        text, entry.removeprefix(".") + ".example.net"))

    def test_hsbc_expat_precedes_hk_without_capturing_hk_siblings(self) -> None:
        for text in (build_expanded.render_expanded(ROOT), (ROOT / "surge-expanded.conf").read_text()):
            for host in ("expat.hsbc.com", "online.expat.hsbc.com"):
                self.assertEqual("United Kingdom", first_inline_domain_policy(text, host))
            for host in ("hsbc.com", "www.hsbc.com", "hsbc.com.hk", "notexpat.hsbc.com"):
                self.assertEqual("Hong Kong", first_inline_domain_policy(text, host))

    def test_actual_reversed_order_revokes_overlap_exception(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "repo"
            shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            path = copied / "surge-main.conf"
            lines = path.read_text().splitlines()
            uk = next(i for i, line in enumerate(lines) if "/uk-finance.conf," in line)
            hk = next(i for i, line in enumerate(lines) if "/hk-finance.conf," in line)
            lines[uk], lines[hk] = lines[hk], lines[uk]
            path.write_text("\n".join(lines) + "\n")
            codes = {d.code for d in validate.validate_repository(copied).diagnostics}
        self.assertTrue({"CROSS_FILE_OVERLAP", "LOCAL_REFERENCE_ORDER", "RULE_CONTRACT_MISMATCH"}.issubset(codes))

    def test_apple_account_exception_is_retired(self) -> None:
        records = set(build_expanded.read_rule_entries(ROOT / "apple-account-payment-rules.conf"))
        self.assertEqual(set(), records)
        text = build_expanded.render_expanded(ROOT)
        for host in ("apple.com", "itunes.apple.com", "music.itunes.apple.com", "apple.com.evil.example",
                     "p71-buy.itunes.apple.com", "account.apple.com", "applecash.apple.com",
                     "applepay.apple.com", "apple-pay-gateway.apple.com"):
            self.assertNotEqual("Res-Frontier", first_inline_domain_policy(text, host))


class OrderedOverlapExceptionTests(unittest.TestCase):
    def entry(self, path: str, raw: str, policy: str) -> validate.DomainEntry:
        return validate.DomainEntry(path, 1, raw, raw.removeprefix("."), raw.startswith("."), policy)

    def test_photo_app_exact_exceptions_require_order_and_policies(self) -> None:
        cases = (
            ("hk-finance.conf", "www.usmartsecurities.com", "HK-FINANCE", "Hong Kong",
             "finance-context.conf", ".usmartsecurities.com", "Finance", "Res-Frontier"),
            ("web3.conf", "web3.bitget.com", "Web3", "Web3",
             "crypto.conf", ".bitget.com", "Crypto", "Crypto"),
            ("web3.conf", "portal-web3.bitget.com", "Web3", "Web3",
             "crypto.conf", ".bitget.com", "Crypto", "Crypto"),
        )
        for nf, host, ns, np, bf, parent, bs, bp in cases:
            records = [self.entry(nf, host, ns), self.entry(bf, parent, bs)]
            refs = [(nf, np), (bf, bp)]
            with self.subTest(host=host):
                diagnostics = []
                validate.detect_active_overlaps(records, diagnostics, refs)
                self.assertEqual([], diagnostics)
                for broken in ([], refs[::-1], refs + refs[:1],
                               [(nf, "DIRECT"), refs[1]], [refs[0], (bf, "DIRECT")]):
                    diagnostics = []
                    validate.detect_active_overlaps(records, diagnostics, broken)
                    self.assertEqual(["CROSS_FILE_OVERLAP"], [d.code for d in diagnostics])
                for changed in ("." + host, "other." + parent.lstrip(".")):
                    diagnostics = []
                    validate.detect_active_overlaps(
                        [self.entry(nf, changed, ns), records[1]], diagnostics, refs)
                    self.assertEqual(["CROSS_FILE_OVERLAP"], [d.code for d in diagnostics])

    def test_exact_exception_requires_order_and_runtime_policies(self) -> None:
        entries = [
            self.entry("uk-finance.conf", ".expat.hsbc.com", "UK-FINANCE"),
            self.entry("hk-finance.conf", ".hsbc.com", "HK-FINANCE"),
        ]
        correct = [("uk-finance.conf", "United Kingdom"), ("hk-finance.conf", "Hong Kong")]
        diagnostics: list[validate.Diagnostic] = []
        validate.detect_active_overlaps(entries, diagnostics, correct)
        self.assertEqual([], diagnostics)
        for refs in (
            [], list(reversed(correct)), correct + correct[:1],
            [("uk-finance.conf", "Crypto"), correct[1]],
            [correct[0], ("hk-finance.conf", "DIRECT")],
        ):
            with self.subTest(references=refs):
                diagnostics = []
                validate.detect_active_overlaps(entries, diagnostics, refs)
                self.assertEqual(["CROSS_FILE_OVERLAP"], [d.code for d in diagnostics])

    def test_exception_does_not_allow_other_hosts_files_or_semantic_policies(self) -> None:
        broad = self.entry("hk-finance.conf", ".hsbc.com", "HK-FINANCE")
        for narrow in (
            self.entry("uk-finance.conf", ".private.hsbc.com", "UK-FINANCE"),
            self.entry("uk-finance.conf", "expat.hsbc.com", "UK-FINANCE"),
            self.entry("other.conf", ".expat.hsbc.com", "UK-FINANCE"),
            self.entry("uk-finance.conf", ".expat.hsbc.com", "Crypto"),
        ):
            diagnostics: list[validate.Diagnostic] = []
            validate.detect_active_overlaps(
                [narrow, broad], diagnostics,
                [(narrow.path, "United Kingdom"), (broad.path, "Hong Kong")],
            )
            self.assertEqual(["CROSS_FILE_OVERLAP"], [d.code for d in diagnostics])


if __name__ == "__main__":
    unittest.main()
