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


class RepositoryTests(unittest.TestCase):
    def test_repository_passes_strict_validation(self) -> None:
        result = validate.validate_repository(ROOT)
        report = result.report(strict=True)
        self.assertTrue(report["ok"], result.diagnostics)
        self.assertEqual(11, report["files"]["active"])
        self.assertEqual(11, report["references"]["found"])

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
