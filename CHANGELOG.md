# Changelog

## Unreleased

- Completed the watchOS path with Apple's certificate-validation hosts, optional beta
  enrollment, extended hostname matching, and an early direct policy.
- Routed GitHub module release/content downloads through the verified residential path,
  preventing fresh devices from missing scripts when the ordinary US route times out.
- Added a coordinate-scoped WeatherKit URL fallback for upstream issue #100 so the retained
  module can classify the fixed China WLOC when iPhone/watchOS omits `country`.
- Split Apple Account, Private Relay and core iCloud traffic so billing remains residential,
  relay endpoints retain their configured US path, and sync/upload/download hosts go direct
  before the reject stack (including Apple's required `metrics.icloud.com`).
- Extended the protected MITM exclusion contract to every non-Apple-root iCloud service
  family in Apple's current enterprise network list.
- Unified Apple's five documented watchOS update catalog and payload hosts on an early
  exact `DIRECT` path, preventing the update transaction from crossing proxy exits.
- Added an exact Singapore exception for the observed `nano.cr18.eu.org` Emby host
  ahead of the broader SKK global rule, without routing the shared `eu.org` suffix.
- Pinned both Polymarket product rule sets to the owner's fixed residential policy while
  retaining separate international and US domain boundaries.
- Repaired the user-edited CEX expansion by moving every Bybit namespace into its dedicated
  file on the iPhone's existing Crypto policy, removing the accidentally restored Gate
  override, and rebuilding the stale expanded profile.
- Tightened the Futu/Moomoo Hong Kong context with three official compatibility domains,
  removed unrelated regional and parked namespaces, reassigned Moomoo Trustee to Singapore,
  and reduced the two Hong Kong resource refresh intervals to one hour.
- Aligned the canonical rule skeleton with the iPhone's Brawl exceptions and United States
  global fallback.
- Removed the unused Gate-specific routing override and resource so any incidental Gate
  traffic follows the normal rule stack, while retaining its TLS MITM exclusions.
- Fixed Sukka marker rotation handling with exact historical markers and provider-shape
  validation, preventing empty resources and real keyword rules from being misclassified.
- Added the official ChatGPT Voice IP RULE-SET ahead of the global STUN rejection without
  DNS expansion, and pinned the international Polymarket product to the reachability-tested
  Hong Kong context instead of the locally poisoned or blocked direct path.
- Split Polymarket by product: the international `.com` control plane now uses the real
  location while the separate US `.us` product retains the residential route.
- Replaced Gate's whole-brand rejection with deterministic `DIRECT` routing so its website,
  help and API return real eligibility results instead of a synthetic network failure.
- Added the two observed Capital One Medallia tenant hosts and the official myEquifax portal
  to the US residential set without widening shared Medallia infrastructure.
- Added an iOS complete-routing mode (`include-all-networks=true`, `include-apns=false`) and
  documented APNs capture as a separate, evidence-driven option.
- Replaced the manual `Verification` selector with deterministic rule routing: shared
  Identity and Risk infrastructure now uses `Res-Frontier`, while regional banks,
  Bybit, Crypto and Web3 retain their earlier first-party country or business policies.
- Documented that multi-tenant KYC roots cannot infer the calling app and may only be
  overridden by evidence-backed tenant-specific hostnames placed before the shared fallback.
- Fixed X account, API, Money, redirect, static-media and Live first-party traffic to the
  residential path without widening X MITM, and documented that routing cannot replace
  X Money identity or residency eligibility.
- Added Gate's current first-party `gate.com`, `gate.io` and `gateio.ws` namespaces to a
  dedicated fail-closed set because every currently available jurisdiction is restricted,
  preventing silent fallback through the generic proxy policy.
- Added a six-host Google Account sign-in/account/OAuth DOMAIN-SET ahead of Google Voice
  and kept both control planes on `Res-Frontier`.
- Expanded the narrow Apple Account payment RULE-SET with four exact sign-in control-plane
  hosts while retaining the exact billing root and dynamic `*-buy` shard family.
- Completed the direct Google Voice STUN host family (`stun` and `stun1` through `stun4`),
  added Jumio's current `.jumio.ai` namespace and WalletConnect's `.walletconnect.network`.
- Kept Apple Account PayPal linking on one United States residential path with a narrow
  RULE-SET for the exact billing root and observed dynamic `*-buy.itunes.apple.com` shard family,
  without widening the rule to shared Apple, iTunes or Braintree infrastructure.
- Made the daily Adblock synchronization semantic-only: volatile source hashes are reported
  in the Actions summary and no longer rewrite or commit an unchanged effective supplement.
- Added a machine-readable retained-module compatibility manifest and checker for the exact
  21 Apple MITM hosts used by iRingo, WLOC and DualSubs Apple TV handling.
- Documented separate evidence-based Mac and iPhone module orders while preserving all
  retained modules and their device-specific DNS winner.
- Hardened synchronization CI with the full validation, module-compatibility, BiliUniverse,
  upstream and immutable published-commit Raw checks before/after publication.
- Pinned every third-party GitHub Action to a full commit SHA and enabled weekly Dependabot
  updates for GitHub Actions.
- Removed obsolete copy-ready policy-group snippets that conflict with fixed-policy profiles;
  Git history remains the archive for those inactive examples.
- Aligned the canonical Rule, contract, manifest and generated expanded file with the
  fixed-policy profile: service traffic now uses existing residential or country groups
  instead of sixteen additional wrapper groups.
- Preserved Finance, Identity, Risk, regional-finance, Google Voice and APNs validation
  boundaries through manifest `semantic_role` metadata while separating them from runtime
  policy names.
- Fixed quoting of policy names containing whitespace in generated expanded rules.
- Taught the profile policy checker to parse modified/effective profiles, nested logical
  rules, regular-expression commas, rule options and module provenance annotations.
- Moved Telegram non-IP routing next to MTProto, before the shared reject stack, while
  retaining Telegram IP routing before the general IP rejection set.
- Added a per-device, all-modules-retained compatibility baseline with the exact Apple MITM
  allowlist required by iRingo, WLOC and DualSubs, without weakening financial/KYC or raw-IP
  exclusions.
- Documented irreducible module-first conflicts, including WeatherKit QUIC versus Private
  Relay and duplicate HTTPDNS/Bilibili/YouTube/Spotify processing chains.
- Added a dedicated Hong Kong account-context layer for HSBC HK, Futu/Moomoo HK and
  Longbridge HK shared infrastructure, ahead of cross-region Finance.
- Added Apple's recommended `17.0.0.0/8` APNs fallback while retaining the TCP 5223
  constraint and the published narrow IPv4/IPv6 ranges.
- Moved all Google Voice and APNs logical `AND` declarations into policy-free remote
  `RULE-SET` files and preserved their semantics during validation and expansion.
- Fixed Google Voice page/call-control traffic to `Res-Frontier` and its documented UDP
  media exceptions to `DIRECT`, ahead of the global STUN privacy rejection.
- Restored the single Taobao/Tmall interactive mini-app runtime suffix before the shared
  reject stack without broadly allowing Taobao advertising hosts.
- Split Bybit's documented application/API domains from the remaining centralized-exchange
  set so `api.bytick.com` no longer falls through to `FINAL`.

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
