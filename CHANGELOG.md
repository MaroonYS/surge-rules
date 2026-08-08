# Changelog

## Unreleased

- Added precise Google Voice control, STUN and media exceptions before the global STUN rejection rule.
- Restored the single Taobao/Tmall interactive mini-app runtime suffix before the shared reject stack without broadly allowing Taobao advertising hosts.
- Split Bybit's documented application/API domains from the remaining centralized-exchange set so `api.bytick.com` no longer falls through to `FINAL`.
- Added a dedicated APNs layer before `SYSTEM`, limited to push hostnames/CNAMEs and TCP 5223 on Apple's published APNs ranges.
- Added copy-ready policy and iOS APNs-capture snippets, plus regression coverage for rule ordering and policy completeness.
- Restored Telegram IP routing before the general IP rejection set.

## 1.7.1 - 2026-08-04

- Changed Adblock4limbo polling from every six hours to once daily at 02:37 Asia/Hong_Kong.
- Replaced the manual draft-PR gate with a fully automatic, validated, non-force fast-forward to `main`.
- Added fail-closed guards for unexpected generated files and concurrent changes to `main`.
- Added bounded download and whole-workflow retries without force-pushing or bypassing validation.
- Removed the obsolete synchronization pull-request template and pull-request permission.

## 1.7.0 - 2026-08-04

- Added a six-hour Adblock4limbo synchronization workflow that rebuilds and deduplicates the supplement against both SKK reject baselines.
- Added pre-publication unit, generated-file and strict repository validation with change-scoped draft pull requests.
- Upgraded all official GitHub Actions to their Node.js 24 major versions.
- Removed volatile current-rule totals from usage documentation while retaining versioned count snapshots.

## 1.6.0 - 2026-08-01

- Restored Bilibili video CDN direct routing with three precise suffixes instead of the former broad keyword.
- Placed the dedicated Bilibili DOMAIN-SET before Polymarket and all shared Reject, Streaming, CDN and Global rules.
- Added contract and regression coverage for the Bilibili domain set, policy and ordering.
- Added live CI compatibility checks for the latest official BiliUniverse Global Surge module.
- Refreshed Adblock4limbo/SKK derivation hashes after the upstream sources changed without altering the 224-entry supplement.

## 1.5.0 - 2026-07-30

- Added the observed Polymarket S3 upload host as an exact residential-route entry.
- Removed the broad Persona root while retaining the product-specific WithPersona domain.
- Removed the redundant intermediate US finance group and expanded its choices directly into `Identity`.
- Reduced Risk to eight device intelligence and fingerprinting providers.

## 1.4.0 - 2026-07-30

- Added separate `Identity` and `Risk` DOMAIN-SET layers with copy-ready stable policy groups.
- Added four selected US identity and clearing services to the residential set and narrowed ICBC to its mainland domain.
- Kept GitHub API traffic out of the generic AI policy and removed the broad cr18 keyword.
- Removed reject-drop pre-matching so explicit financial and identity rules retain priority.
- Removed invalid or already-covered Adblock entries and added a second SKK baseline.
- Added immutable commit Raw checks, production deployment checks and live Adblock validation to PR CI.
- Added a secret-safe full-profile policy and stability checker.

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
