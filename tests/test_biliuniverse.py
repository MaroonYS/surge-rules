from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_biliuniverse  # noqa: E402


COMPATIBLE_MODULE = """\
#!version = 0.8.21
#!arguments = ForceHost:"1",Locales:"CHN,HKG"
[Script]
Global = type=http-request, pattern=^https://api\\.bilibili\\.com/, ability=http-client-policy
[MITM]
hostname = %APPEND% api.bilibili.com, api.biliapi.net
"""


class BiliUniverseCompatibilityTests(unittest.TestCase):
    def test_current_shape_is_compatible(self) -> None:
        result = check_biliuniverse.validate_module(
            COMPATIBLE_MODULE,
            ("bilivideo.cn", "bilivideo.com", "bilivideo.net"),
        )
        self.assertEqual((), result.problems)
        self.assertEqual("0.8.21", result.version)

    def test_script_interception_of_bilivideo_is_rejected(self) -> None:
        module = COMPATIBLE_MODULE.replace(
            "api\\.bilibili\\.com",
            "cdn\\.bilivideo\\.com",
        )
        result = check_biliuniverse.validate_module(
            module,
            ("bilivideo.com",),
        )
        self.assertIn(
            "official module now intercepts bilivideo traffic",
            result.problems,
        )

    def test_mitm_overlap_is_rejected(self) -> None:
        module = COMPATIBLE_MODULE.replace(
            "api.bilibili.com, api.biliapi.net",
            "api.bilibili.com, media.bilivideo.com",
        )
        result = check_biliuniverse.validate_module(
            module,
            ("bilivideo.com",),
        )
        self.assertIn(
            "DIRECT suffix bilivideo.com overlaps module MITM host "
            "media.bilivideo.com",
            result.problems,
        )

    def test_required_module_capabilities_are_enforced(self) -> None:
        module = COMPATIBLE_MODULE.replace('ForceHost:"1"', 'ForceHost:"0"')
        module = module.replace(", ability=http-client-policy", "")
        result = check_biliuniverse.validate_module(
            module,
            ("bilivideo.com",),
        )
        self.assertIn(
            "official module no longer defaults ForceHost to HTTP domains",
            result.problems,
        )
        self.assertIn(
            "official module no longer exposes dynamic HTTP client policy",
            result.problems,
        )

    def test_domain_set_parser_requires_suffixes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "domains.conf"
            path.write_text("# comment\n.bilivideo.com\n", encoding="utf-8")
            self.assertEqual(
                ("bilivideo.com",),
                check_biliuniverse.parse_direct_suffixes(path),
            )
            path.write_text("exact.bilivideo.com\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                check_biliuniverse.parse_direct_suffixes(path)


if __name__ == "__main__":
    unittest.main()
