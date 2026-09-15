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
    "direct-cn.conf", "ch-finance.conf", "uk-finance.conf", "hk-finance.conf",
    "sg-finance.conf", "jp-finance.conf", "kr-finance.conf", "us-residential.conf",
]
MEXC_ENTRIES = {
    ".mexc.com", ".mexc.co", ".mexc.fm", ".mexcsensors.com", ".mexc.in",
    "static.mocortech.com", "public.mocortech.com", "customer-article.mocortech.com",
    "learn.mocortech.com", "s3-app-release.s3.ap-northeast-1.amazonaws.com",
    "mexc-front-static.s3.ap-northeast-1.amazonaws.com",
    "mexc-rainbown-activityimages.s3.ap-northeast-1.amazonaws.com",
    "mexc-static-learn.s3.ap-northeast-1.amazonaws.com",
    "mexc.onelink.me", "mexcdevelop.github.io",
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
        self.assertEqual("Switzerland", next(b["policy"] for b in bindings if b["file"] == "ch-finance.conf"))
        main = (ROOT / "surge-main.conf").read_text()
        contract = json.loads((ROOT / "rules-contract.json").read_text())
        contract_text = "\n".join(rule for section in contract["sections"] for rule in section["rules"])
        for text in (main, contract_text):
            positions = [text.index("/" + name + ",") for name in FINANCE_ORDER]
            self.assertEqual(positions, sorted(positions))
            self.assertEqual(1, text.count("/ch-finance.conf,Switzerland,extended-matching"))

    def test_ch_cannot_disappear_from_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "repo"
            shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            path = copied / "rules-manifest.json"
            manifest = json.loads(path.read_text())
            manifest["active"] = [b for b in manifest["active"] if b["file"] != "ch-finance.conf"]
            path.write_text(json.dumps(manifest))
            codes = {d.code for d in validate.validate_repository(copied).diagnostics}
        self.assertIn("UNKNOWN_LOCAL_REFERENCE", codes)

    def test_mexc_routes_to_switzerland_in_generated_and_committed_output(self) -> None:
        self.assertEqual(MEXC_ENTRIES, set(build_expanded.read_domain_entries(ROOT / "ch-finance.conf")))
        for name in ("uk-finance.conf", "crypto.conf"):
            self.assertTrue(MEXC_ENTRIES.isdisjoint(build_expanded.read_domain_entries(ROOT / name)))
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
                        self.assertEqual("Switzerland", first_inline_domain_policy(text, host))

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

    def test_apple_account_exception_has_only_six_narrow_records(self) -> None:
        records = set(build_expanded.read_rule_entries(ROOT / "apple-account-payment-rules.conf"))
        self.assertEqual({
            "DOMAIN,account.apple.com,extended-matching",
            "DOMAIN,appleid.cdn-apple.com,extended-matching",
            "DOMAIN,idmsa.apple.com,extended-matching",
            "DOMAIN,gsa.apple.com,extended-matching",
            "DOMAIN,buy.itunes.apple.com,extended-matching",
            "DOMAIN-WILDCARD,*-buy.itunes.apple.com,extended-matching",
        }, records)
        text = build_expanded.render_expanded(ROOT)
        self.assertEqual("Res-Frontier", first_inline_domain_policy(text, "p71-buy.itunes.apple.com"))
        self.assertEqual("Res-Frontier", first_inline_domain_policy(text, "account.apple.com"))
        for host in ("apple.com", "itunes.apple.com", "music.itunes.apple.com", "apple.com.evil.example"):
            self.assertNotEqual("Res-Frontier", first_inline_domain_policy(text, host))


class OrderedOverlapExceptionTests(unittest.TestCase):
    def entry(self, path: str, raw: str, policy: str) -> validate.DomainEntry:
        return validate.DomainEntry(path, 1, raw, raw.removeprefix("."), raw.startswith("."), policy)

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
