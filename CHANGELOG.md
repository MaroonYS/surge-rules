# Changelog

## 1.3.0 - 2026-07-30

- Replaced broad Polymarket keyword matching with three precise DOMAIN-SET entries.
- Corrected the SukkaW reject stack order and per-resource matching parameters.
- Replaced the deprecated Apple CDN resource and removed empty or redundant Streaming resources.
- Restored upstream-controlled IP resolution semantics, including China IP hostname resolution.
- Added high-confidence first-party regional financial domains and removed shared risk infrastructure from the US residential set.
- Added a policy-free, deduplicated Adblock4limbo supplement with MIT attribution and source hashes.
- Upgraded upstream checks from a one-byte probe to full payload, format, sentinel, deprecation and embedded-policy validation.

## 1.2.0 - 2026-07-30

- Restored the exact requested 17-section rule order and policy names.
- Added a machine-readable contract that rejects any missing, extra, reordered or changed rule.
- Restored STUN rejection and both required keyword rules.
- Routed Private Relay through `Apple` and Apple Intelligence through `AIGC`.
- Moved Apple Cash/Pay and PayPal into the United States DOMAIN-SET.

## 1.1.1 - 2026-07-30

- Added a generated `surge-expanded.conf` with every active DOMAIN-SET entry restored inline.
- Added a deterministic generator and CI equivalence check for compact and expanded rules.

## 1.1.0 - 2026-07-30

- Replaced the broad Polymarket keyword with the official `.com` and `.us` suffixes.
- Added six exact Private Relay endpoints before the updateable remote set.
- Moved specific service, platform and download rules before broad rejection lists.
- Moved Telegram and streaming IP rules before the general IP rejection list.
- Added CI guards against broad shared suffixes and unapproved keyword rules.
- Added a requirement-by-requirement implementation matrix.

## 1.0.0 - 2026-07-30

- Split the monolithic Surge rule section into 11 policy-oriented DOMAIN-SET files.
- Migrated the complete effective Web3 coverage from the supplied 555-line rule set.
- Added dedicated Private Relay and Apple Intelligence policy groups.
- Removed the global STUN rejection from the main rule skeleton.
- Kept Apple Cash/Pay on the Apple system path.
- Stopped globally routing shared payment, KYC, CAPTCHA, fingerprint and anti-fraud providers.
- Added an archive policy without assuming that any institution is unused.
- Added deterministic local validation, unit tests and GitHub Actions.
