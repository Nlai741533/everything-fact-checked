# Changelog

All notable changes to this project are documented here.

## [0.1.0] - 2026-05-30

### Added
- Packaged as a proper Claude Code plugin: `.claude-plugin/plugin.json` and
  `.claude-plugin/marketplace.json`; skill moved to `skills/fact-check/SKILL.md`.
- Verified install path: `/plugin marketplace add` + `/plugin install`, with
  `--plugin-dir` for loading a local clone (checked against `claude --help`).
- `scripts/extract_claims.py` — claim inventory extractor with priority triage.
- `scripts/check_links.py` — source-link resolver/checker.
- `examples/` — deliberately flawed fictional report plus expected fact-check output.
- `tests/` — unit tests and fixtures for the helper scripts (stdlib `unittest`).
- GitHub Actions CI: manifest validation, unit tests, script smoke tests.
- SKILL.md: prompt-injection defense (treat source content as data, not
  instructions) and a standard machine-readable evidence format.

### Changed
- Generalized the skill from a single domain to any data-heavy report.
- LICENSE now includes copyright holder.
- README rewritten with correct install instructions, limitations, and a
  "what this is / isn't" section.
