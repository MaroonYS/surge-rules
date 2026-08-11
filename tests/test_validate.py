from __future__ import annotations

import json
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
            self.entry(path, index, f".{domain}", policy)
            for path, policy, domains in (
                (
                    "identity-context.conf",
                    "Identity",
                    (
                        "socure.com",
                        "socure.co",
                        "withpersona.com",
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
                    "Risk",
                    (
                        "online-metrix.net",
                        "threatmetrix.com",
                        "iovation.com",
                        "iovation.io",
                        "biocatch.com",
                        "fingerprint.com",
                        "fingerprintjs.com",
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


class RuleSetSyntaxTests(unittest.TestCase):
    def test_policy_free_simple_and_logical_rules_are_accepted(self) -> None:
        diagnostics: list[validate.Diagnostic] = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "local.conf").write_text(
                "DOMAIN,buy.itunes.apple.com\n"
                "DOMAIN-WILDCARD,*-buy.itunes.apple.com\n"
                "DOMAIN-SUFFIX,example.com\n"
                "IP-CIDR,192.0.2.0/24,no-resolve\n"
                "AND,((PROTOCOL,UDP),(DEST-PORT,19302-19309),"
                "(IP-CIDR,192.0.2.0/24,no-resolve))\n",
                encoding="utf-8",
            )
            entries = validate.parse_rule_set(
                root,
                "local.conf",
                "TEST",
                diagnostics,
            )

        self.assertEqual(5, len(entries))
        self.assertEqual(
            [
                "DOMAIN",
                "DOMAIN-WILDCARD",
                "DOMAIN-SUFFIX",
                "IP-CIDR",
                "AND",
            ],
            [entry.rule_type for entry in entries],
        )
        self.assertEqual([], diagnostics)

    def test_domain_wildcard_validation_is_strict(self) -> None:
        valid = (
            "DOMAIN-WILDCARD,*-buy.itunes.apple.com",
            "DOMAIN-WILDCARD,api-??.example.com",
            "DOMAIN-WILDCARD,*.example.com",
        )
        for rule in valid:
            with self.subTest(rule=rule):
                rule_type, problem = validate.validate_policy_free_rule(rule)
                self.assertEqual("DOMAIN-WILDCARD", rule_type)
                self.assertIsNone(problem)

        invalid = {
            "DOMAIN-WILDCARD,*": "at least two",
            "DOMAIN-WILDCARD,*.com": "too broad",
            "DOMAIN-WILDCARD,*.*": "too broad",
            "DOMAIN-WILDCARD,*.apple.com": "too broad",
            "DOMAIN-WILDCARD,API-*.example.com": "lowercase",
            "DOMAIN-WILDCARD,https://*.example.com": "URLs",
            "DOMAIN-WILDCARD,example.com": "must contain",
            "DOMAIN-WILDCARD,*-buy.itunes.apple.com,DIRECT": (
                "embedded policy"
            ),
        }
        for rule, expected in invalid.items():
            with self.subTest(rule=rule):
                rule_type, problem = validate.validate_policy_free_rule(rule)
                self.assertIsNone(rule_type)
                self.assertIn(expected, problem or "")

    def test_embedded_policy_is_rejected(self) -> None:
        rule_type, problem = validate.validate_policy_free_rule(
            "DOMAIN-SUFFIX,example.com,DIRECT"
        )
        self.assertIsNone(rule_type)
        self.assertIn("embedded policy", problem or "")

    def test_embedded_policy_in_logical_child_is_rejected(self) -> None:
        rule_type, problem = validate.validate_policy_free_rule(
            "AND,((PROTOCOL,UDP,DIRECT),(DEST-PORT,19302))"
        )
        self.assertIsNone(rule_type)
        self.assertIn("logical sub-rule", problem or "")

    def test_unknown_types_and_invalid_matchers_are_rejected(self) -> None:
        invalid = {
            "PROTOCL,UDP": "unsupported",
            "PROTOCOL,BOGUS": "TCP or UDP",
            "DEST-PORT,abc": "one port",
            "DEST-PORT,65536": "65535",
            "DEST-PORT,200-100": "65535",
            "IP-CIDR,192.0.2.1/24,no-resolve": "host bits",
            "DOMAIN,example.com,no-resolve": "unsupported option",
        }
        for rule, expected in invalid.items():
            with self.subTest(rule=rule):
                rule_type, problem = validate.validate_policy_free_rule(rule)
                self.assertIsNone(rule_type)
                self.assertIn(expected, problem or "")


class RepositoryTests(unittest.TestCase):
    def test_repository_passes_strict_validation(self) -> None:
        result = validate.validate_repository(ROOT)
        report = result.report(strict=True)
        self.assertTrue(report["ok"], result.diagnostics)
        self.assertEqual(len(result.bindings), report["files"]["active"])
        self.assertEqual(len(result.bindings), report["references"]["found"])
        self.assertEqual(
            report["entries"]["active"],
            report["entries"]["domain_set"] + report["entries"]["rule_set"],
        )
        self.assertEqual(
            report["files"]["active"],
            report["files"]["domain_set"] + report["files"]["rule_set"],
        )
        self.assertEqual(
            {
                "apple-account-payment-rules.conf",
                "apple-push-rules.conf",
                "google-voice-media-rules.conf",
            },
            {
                binding.file
                for binding in result.bindings
                if binding.type == "RULE-SET"
            },
        )
        self.assertGreater(len(result.active_rule_entries), 0)
        self.assertEqual(
            len(result.active_rule_entries),
            report["entries"]["rule_set"],
        )

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

    def test_manifest_binding_type_defaults_and_allows_rule_set(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = {
                "repository": "owner/repository",
                "branch": "main",
                "main": "surge-main.conf",
                "contract": "rules-contract.json",
                "active": [
                    {"file": "domains.conf", "policy": "DIRECT"},
                    {
                        "file": "rules.conf",
                        "type": "RULE-SET",
                        "policy": "Proxy",
                    },
                ],
            }
            (root / "rules-manifest.json").write_text(
                json.dumps(manifest),
                encoding="utf-8",
            )
            *_, bindings = validate.load_manifest(root)

        self.assertEqual(
            ["DOMAIN-SET", "RULE-SET"],
            [binding.type for binding in bindings],
        )

    def test_manifest_separates_runtime_policy_from_semantic_role(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = {
                "repository": "owner/repository",
                "branch": "main",
                "main": "surge-main.conf",
                "contract": "rules-contract.json",
                "active": [
                    {
                        "file": "identity.conf",
                        "policy": "Res-Frontier",
                        "semantic_role": "Identity",
                    },
                    {"file": "direct.conf", "policy": "DIRECT"},
                ],
            }
            (root / "rules-manifest.json").write_text(
                json.dumps(manifest),
                encoding="utf-8",
            )
            *_, bindings = validate.load_manifest(root)

        self.assertEqual(
            [("Res-Frontier", "Identity"), ("DIRECT", "DIRECT")],
            [(binding.policy, binding.semantic_policy) for binding in bindings],
        )
        self.assertEqual(
            "United States",
            validate.normalize_policy_name('"United States"'),
        )

    def test_manifest_rejects_unknown_binding_type(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = {
                "repository": "owner/repository",
                "branch": "main",
                "main": "surge-main.conf",
                "contract": "rules-contract.json",
                "active": [
                    {
                        "file": "rules.conf",
                        "type": "IP-SET",
                        "policy": "Proxy",
                    }
                ],
            }
            (root / "rules-manifest.json").write_text(
                json.dumps(manifest),
                encoding="utf-8",
            )
            with self.assertRaises(validate.ConfigurationError):
                validate.load_manifest(root)

    def test_main_reference_must_match_binding_type(self) -> None:
        binding = validate.Binding(
            file="rules.conf",
            policy="Proxy",
            description="",
            type="RULE-SET",
        )
        raw_base = "https://raw.githubusercontent.com/owner/repository/main/"

        def diagnostics_for(
            reference_type: str,
            options: str = "",
        ) -> list[validate.Diagnostic]:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                sections = [
                    {"number": number, "title": f"Section {number}", "rules": []}
                    for number in range(1, 18)
                ]
                reference = (
                    f"{reference_type},{raw_base}rules.conf,Proxy{options}"
                )
                sections[0]["rules"] = [reference]
                sections[-1]["rules"] = ["FINAL,DIRECT,dns-failed"]
                (root / "rules-contract.json").write_text(
                    json.dumps({"sections": sections}),
                    encoding="utf-8",
                )
                main_lines = ["[Rule]"]
                for section in sections:
                    main_lines.append(
                        f"# {section['number']}. {section['title']}"
                    )
                    main_lines.extend(section["rules"])
                (root / "surge-main.conf").write_text(
                    "\n".join(main_lines) + "\n",
                    encoding="utf-8",
                )
                diagnostics: list[validate.Diagnostic] = []
                validate.validate_main_rules(
                    root,
                    "surge-main.conf",
                    "owner/repository",
                    "main",
                    "rules-contract.json",
                    [binding],
                    diagnostics,
                )
                return diagnostics

        valid_codes = {item.code for item in diagnostics_for("RULE-SET")}
        invalid_codes = {item.code for item in diagnostics_for("DOMAIN-SET")}
        option_codes = {
            item.code
            for item in diagnostics_for("RULE-SET", ",extended-matching")
        }
        self.assertNotIn("LOCAL_REFERENCE_TYPE", valid_codes)
        self.assertIn("LOCAL_REFERENCE_TYPE", invalid_codes)
        self.assertIn("LOCAL_RULESET_OPTIONS", option_codes)


if __name__ == "__main__":
    unittest.main()
