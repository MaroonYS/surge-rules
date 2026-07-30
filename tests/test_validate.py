from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate  # noqa: E402


class DomainSyntaxTests(unittest.TestCase):
    def test_valid_entries(self) -> None:
        for value in (
            "example.com",
            ".example.com",
            "login.example.co.uk",
            "xn--bcher-kva.example",
            "apple-relay.apple.com",
            ".smoot.apple.com",
        ):
            with self.subTest(value=value):
                self.assertIsNone(validate.validate_domain(value))

    def test_invalid_entries(self) -> None:
        for value in (
            "Example.com",
            "例子.com",
            "https://example.com",
            "*.example.com",
            "example.com/path",
            "example.com:443",
            "127.0.0.1",
            "singlelabel",
            "bad_label.example",
            "-bad.example",
            "bad-.example",
            "double..example",
            "example.com.",
            " example.com",
            "example.com # comment",
            ".apple.com",
            ".auth0.com",
            ".co.uk",
        ):
            with self.subTest(value=value):
                self.assertIsNotNone(validate.validate_domain(value))


class SemanticTests(unittest.TestCase):
    def entry(
        self,
        path: str,
        line: int,
        raw: str,
        policy: str,
    ) -> validate.DomainEntry:
        return validate.DomainEntry(
            path=path,
            line=line,
            raw=raw,
            domain=raw.removeprefix("."),
            suffix=raw.startswith("."),
            policy=policy,
        )

    def test_cross_policy_suffix_overlap(self) -> None:
        diagnostics: list[validate.Diagnostic] = []
        validate.detect_active_overlaps(
            [
                self.entry("a.conf", 1, ".example.com", "A"),
                self.entry("b.conf", 2, "login.example.com", "B"),
            ],
            diagnostics,
        )
        self.assertEqual(["CROSS_FILE_OVERLAP"], [item.code for item in diagnostics])

    def test_dns_label_boundary_is_respected(self) -> None:
        diagnostics: list[validate.Diagnostic] = []
        validate.detect_active_overlaps(
            [
                self.entry("a.conf", 1, ".example.com", "A"),
                self.entry("b.conf", 2, ".notexample.com", "B"),
            ],
            diagnostics,
        )
        self.assertEqual([], diagnostics)

    def test_archive_does_not_take_part_in_active_overlap(self) -> None:
        diagnostics: list[validate.Diagnostic] = []
        active = [self.entry("active.conf", 1, ".example.com", "A")]
        archive = self.entry("archive/old.conf", 1, ".example.com", "ARCHIVE")
        archive = validate.DomainEntry(**{**archive.__dict__, "archive": True})
        validate.detect_active_overlaps(active, diagnostics)
        self.assertEqual([], diagnostics)

    def test_shared_provider_suffix_is_rejected_in_sensitive_policy(self) -> None:
        diagnostics: list[validate.Diagnostic] = []
        validate.detect_shared_infrastructure(
            [self.entry("finance.conf", 1, ".stripe.com", "Finance")],
            diagnostics,
        )
        self.assertEqual(
            ["SHARED_INFRASTRUCTURE"],
            [item.code for item in diagnostics],
        )

    def test_narrow_shared_provider_host_can_be_log_driven(self) -> None:
        diagnostics: list[validate.Diagnostic] = []
        validate.detect_shared_infrastructure(
            [self.entry("finance.conf", 1, "tenant.auth0.com", "Finance")],
            diagnostics,
        )
        self.assertEqual([], diagnostics)

    def test_selected_us_shared_suffixes_are_explicitly_allowed(self) -> None:
        diagnostics: list[validate.Diagnostic] = []
        entries = [
            self.entry(
                "us-residential.conf",
                index,
                f".{domain}",
                "Res-Frontier",
            )
            for index, domain in enumerate(
                ("apexclearing.com", "earlywarning.com", "id.me", "login.gov"),
                1,
            )
        ]
        validate.detect_shared_infrastructure(entries, diagnostics)
        self.assertEqual([], diagnostics)

    def test_selected_us_shared_suffix_is_not_globally_exempt(self) -> None:
        diagnostics: list[validate.Diagnostic] = []
        validate.detect_shared_infrastructure(
            [
                self.entry(
                    "finance-context.conf",
                    1,
                    ".id.me",
                    "Finance",
                )
            ],
            diagnostics,
        )
        self.assertEqual(
            ["SHARED_INFRASTRUCTURE"],
            [item.code for item in diagnostics],
        )

    def test_selected_identity_layers_are_explicitly_allowed(self) -> None:
        diagnostics: list[validate.Diagnostic] = []
        entries = [
            self.entry(path, index, f".{domain}", "Identity")
            for path, domains in (
                (
                    "identity-context.conf",
                    (
                        "socure.com",
                        "socure.co",
                        "withpersona.com",
                        "persona.com",
                        "jumio.com",
                        "netverify.com",
                        "onfido.com",
                        "trulioo.com",
                        "idology.com",
                        "au10tix.com",
                        "alloy.com",
                        "sentilink.com",
                        "middesk.com",
                        "prove.com",
                        "proveidentity.com",
                        "miteksystems.com",
                        "mitekcloud.com",
                        "veriff.com",
                        "sumsub.com",
                        "vouched.id",
                        "ekata.com",
                    ),
                ),
                (
                    "risk-context.conf",
                    (
                        "sardine.ai",
                        "sift.com",
                        "siftcdn.net",
                        "online-metrix.net",
                        "threatmetrix.com",
                        "iovation.com",
                        "iovation.io",
                        "biocatch.com",
                        "fingerprint.com",
                        "fingerprintjs.com",
                        "riskified.com",
                        "forter.com",
                        "castle.io",
                        "seon.io",
                        "incognia.com",
                    ),
                ),
            )
            for index, domain in enumerate(domains, 1)
        ]
        validate.detect_shared_infrastructure(entries, diagnostics)
        self.assertEqual([], diagnostics)

    def test_identity_layer_allowlist_is_path_scoped(self) -> None:
        diagnostics: list[validate.Diagnostic] = []
        validate.detect_shared_infrastructure(
            [
                self.entry(
                    "other.conf",
                    1,
                    ".socure.com",
                    "Identity",
                )
            ],
            diagnostics,
        )
        self.assertEqual(
            ["SHARED_INFRASTRUCTURE"],
            [item.code for item in diagnostics],
        )


class RepositoryTests(unittest.TestCase):
    def test_repository_passes_strict_validation(self) -> None:
        result = validate.validate_repository(ROOT)
        report = result.report(strict=True)
        self.assertTrue(report["ok"], result.diagnostics)
        self.assertEqual(len(result.bindings), report["files"]["active"])
        self.assertEqual(len(result.bindings), report["references"]["found"])

    def test_parser_rejects_bom_and_duplicate(self) -> None:
        diagnostics: list[validate.Diagnostic] = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "rules.conf").write_bytes(
                b"\xef\xbb\xbf.example.com\n.example.com\n"
            )
            validate.parse_domain_set(
                root,
                "rules.conf",
                "TEST",
                archive=False,
                diagnostics=diagnostics,
            )
        self.assertEqual(
            {"UTF8_BOM", "DUPLICATE"},
            {item.code for item in diagnostics},
        )


if __name__ == "__main__":
    unittest.main()
