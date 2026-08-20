#!/usr/bin/env python3
"""Strictly identify Sukka ruleset provenance markers."""

from __future__ import annotations

from urllib.parse import urlsplit


# Sukka rotates this marker periodically. Keep only exact, known historical
# values: broad suffix or substring matching could hide legitimate rules.
SKK_MARKER_DOMAINS = frozenset(
    {
        "7h15.ru1353t.1s.m4d3.by.5ukk4w.skk.moe",
        "7h15_ru1353t_1s_m4d3_by_5ukk4w.skk.moe",
        "7h1s_rul35et_i5_mad3_by_5ukk4w-ruleset.skk.moe",
        "th1s_rule5et_1s_m4d3_by_5ukk4w_ruleset.skk.moe",
        "this_ruleset_is_made_by_sukkaw.ruleset.skk.moe",
    }
)

CURRENT_SKK_MARKER = "7h15.ru1353t.1s.m4d3.by.5ukk4w.skk.moe"


def is_skk_list_url(url: str) -> bool:
    parsed = urlsplit(url)
    return (
        parsed.scheme == "https"
        and parsed.hostname == "ruleset.skk.moe"
        and parsed.path.startswith("/List/")
    )


def is_domain_set_marker(line: str) -> bool:
    return line.strip().casefold() in SKK_MARKER_DOMAINS


def is_rule_set_marker(line: str) -> bool:
    fields = [field.strip() for field in line.split(",")]
    return (
        len(fields) == 2
        and fields[0].upper() == "DOMAIN"
        and fields[1].casefold() in SKK_MARKER_DOMAINS
    )
