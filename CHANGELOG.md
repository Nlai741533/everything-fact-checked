# Changelog

All notable changes to this project are documented here.

## [0.2.3] - 2026-06-03

### Fixed
- **`efc audit --json` now returns the correct exit code.** Broken links set a
  non-zero exit in *both* human and `--json` modes (previously `--json` returned
  `0` on a failing report, silently passing in CI). Added an exit-code parity
  regression test.
- **CONTRIBUTING.md** no longer claims `scripts/*.py` run without installing
  `efc`; the scripts are thin shims around the `efc` package, so `pip install -e .`
  is required. Updated the good-first-issue file paths to `src/efc/`.

### Security
- **SSRF guard for `efc verify`.** Source URLs (which may come from untrusted
  reports/PRs) are now restricted to `http`/`https` and refused if the host
  resolves to a loopback, private, link-local (incl. cloud metadata
  `169.254.169.254`), reserved, multicast, or unspecified address. HTTP
  redirects are re-validated against the same rules. Documented in SECURITY.md;
  covered by new tests.

## [0.2.2] - 2026-05-30

### Fixed
- **GitHub Action moved to repo root** so `uses: Nlai741533/EFC-Plugin@vX.Y.Z`
  works directly (was broken when `action.yml` was in a subdirectory).
- **Added `fail-on-broken-links` input** to `action.yml` (was referenced but
  never declared).
- **Action scans all `.md`** files except docs (README, CHANGELOG, FACTCHECK,
  SECURITY, CONTRIBUTING), matching documented behavior.
- **Removed stale claim** that `scripts/*.py` work without `efc` installed.
- Updated README Action usage example.

## [0.2.1] - 2026-05-30

### Fixed
- **Packaging:** moved script modules into `src/efc/` so `pip install .` produces
  a working `efc` CLI outside the repo checkout.
- **Schema bundled** inside the package (`src/efc/schemas/`).
- **GitHub Action** uses `pip install` + `efc` CLI instead of `scripts/` paths.
- **Action broken-link counting** only counts actual broken categories.
- **`audit --no-network`** reports `unchecked` instead of misleading `ok`.
- **CI:** added `install-test` job, 4-location version consistency check.
- **Repo renamed** to `EFC-Plugin`.

## [0.2.0] - 2026-05-30

### Added — CLI
- **`efc` CLI command** with subcommands: `extract`, `links`, `evidence`, `audit`,
  `verify`, `version`. Installable via `pipx install .` or `pip install .`.
- `pyproject.toml` for standard Python packaging (hatchling backend).
- Stable exit codes: 0=success, 1=problems found, 2=usage/IO error.
- JSON output mode (`--json`) for all subcommands, suitable for CI pipelines.

### Added — Source-content verification
- `scripts/verify_source.py`: fetches cited URLs, extracts visible text,
  and checks whether the claimed value/key terms appear in the source.
  Verdicts: `found`, `not_found`, `ambiguous`, `skipped`, `fetch_failed`.
- Integrated as `efc verify` subcommand.

### Added — GitHub Action
- `action/action.yml`: composite action for fact-checking markdown reports
  in PRs. Extracts claims, checks links, posts results to the PR summary.

### Added — Repo hardening
- `SECURITY.md`: vulnerability reporting policy and secret scanning overview.
- `CONTRIBUTING.md`: development workflow, code style, commit conventions.
- Issue templates: bug report, feature request, new claim type proposal.
- `.github/copilot-instructions.md`: Copilot coding agent project guidance.

### Added — CI
- Python matrix testing: 3.11, 3.12, 3.13.
- CLI smoke test in CI.
- Source verification smoke test in CI.
- Scheduled weekly live link check (non-blocking).

### Changed
- Manifest versions bumped to 0.2.0.
- `.gitignore` updated to exclude build artifacts.

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
