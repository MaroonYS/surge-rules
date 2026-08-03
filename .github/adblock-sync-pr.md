## Summary

Automated refresh of the Adblock4limbo supplement.

- Re-fetches Adblock4limbo and both SKK reject baselines.
- Removes duplicate, invalid, internally redundant and baseline-covered records.
- Rebuilds `surge-expanded.conf` from the updated DOMAIN-SET.
- Runs unit tests, generated-file checks and strict repository validation before publishing.

This PR is intentionally left as a draft and is never auto-merged.
