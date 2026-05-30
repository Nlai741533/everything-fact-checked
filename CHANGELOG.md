# Changelog

All notable changes to this project are documented here.

## [0.1.2] - 2026-05-30

### Fixed
- **URL validation hardened:** replaced regex `^https?://\S+$` with
  `urllib.parse.urlparse()` — now requires `scheme in {"http", "https"}`
  and non-empty `netloc`. Rejects `https:///missing-host`, `ftp://...`, etc.
- **Docstring alignment:** validator module docstring no longer claims
  "resolving" sources — accurately describes format + tier checks.
- **FACTCHECK.md:** live link results now labeled as environment/date-specific;
  test count updated.
- Added 2 new tests (URL-without-host, ftp scheme rejected).

## [0.1.1] - 2026-05-30

### Fixed
- **Security:** Removed embedded GitHub token from git remote URL. Token must be
  revoked in GitHub → Settings → Developer settings → Personal access tokens.
- **Validation:** `validate_evidence.py` now rejects `source_url` values that are
  not valid http/https URLs (e.g. `"not a url"` no longer passes). Added
  `_looks_like_url()` helper with 3 new tests.
- **Docs:** README evidence-format description now accurately reflects what the
  validator checks (URL format, not reachability).
- **Docs:** `FACTCHECK.md` refreshed — test count updated from stale "16" to 47,
  URL-validation doc/code mismatch logged as a found-and-fixed error.
- **Housekeeping:** Added `feedback-log.md` to `.gitignore` (private repo-management
  notes, not for publication).

## [0.1.0] - 2026-05-30

### Added
- Packaged as a proper Claude Code plugin: `.claude-plugin/plugin.json` and
  `.claude-plugin/marketplace.json`; skill moved to `skills/fact-check/SKILL.md`.
- Verified install path: `/plugin marketplace add` + `/plugin install`, with
  `--plugin-dir` for loading a local clone (checked against `claude --help`).
- `scripts/extract_claims.py` — claim inventory extractor with priority triage;
  skips fenced code blocks and headings and reports the full sentence around a
  match (fewer false positives, e.g. no longer flags "for demonstration only").
- `scripts/check_links.py` — source-link checker with a GET fallback and explicit
  categories (ok, redirect, blocked, not_found, server_error, ssl_error,
  unreachable); handles titled markdown links and URLs containing parentheses.
- `schemas/evidence.schema.json` + `scripts/validate_evidence.py` — a
  machine-checkable evidence format with cross-field fact-check rules.
- `examples/` — deliberately flawed fictional report, expected fact-check output,
  and a valid evidence sample.
- `tests/` — stdlib `unittest` suite incl. golden tests that pin the scripts'
  behavior against the shipped examples.
- GitHub Actions CI: JSON/schema validation, unit tests, evidence-sample
  validation, script smoke tests, plus a job that runs the real
  `claude plugin validate` on the plugin and marketplace manifests.
- SKILL.md: prompt-injection defense (treat source content as data, not
  instructions) and a standard machine-readable evidence format.

### Changed
- Generalized the skill from a single domain to any data-heavy report.
- LICENSE now includes copyright holder.
- README rewritten with correct install instructions, limitations, and a
  "what this is / isn't" section.
