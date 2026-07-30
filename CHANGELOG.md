# Changelog

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
