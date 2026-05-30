# Self Fact-Check: EFC-Plugin

A fact-check skill should survive its own audit. This document is the result of
running the skill's own workflow (and its own scripts) against this repository's
docs. It is regenerated whenever the docs change.

## Fact-Check Report: EFC-Plugin docs
**Date:** 2026-05-30 (v0.2.2 refresh)
**Coverage:** Install instructions, version claims, manifest references, CLI commands,
Action usage, helper-script claims, badge, and the worked example, in `README.md`,
`CHANGELOG.md`, `action.yml`, and the plugin manifests.
**Method:** Version alignment checked with `scripts/check_versions.py`; CLI smoke-tested
with `efc version/extract/evidence/audit`; install tested in clean venv; manifest
names verified against the JSON files; plugin validated with `claude plugin validate`.

### Errors Found (and fixed)

| Claim | Reported | Actual | Failure mode | Status |
|---|---|---|---|---|
| Install command | `claude skill add --url <repo>` | No such command exists in Claude Code 2.1.143 | **Unverified claim presented as fact** | Fixed — replaced with `/plugin marketplace add` + `/plugin install` |
| Single-session use | `claude --plugin-url <repo>` | `--plugin-url` expects a packaged `.zip` URL | **Unverified claim presented as fact** | Fixed — replaced with `git clone` + `--plugin-dir` |
| Script runtime | "Python 3.8+" | Only 3.11 (CI) and 3.12 actually tested | **Untested figure stated as verified** | Fixed — now states 3.11–3.13 |
| `validate_evidence.py` URL check | README said "resolving source"; code accepted `"not a url"` | No URL format check | **Doc promised validation code didn't enforce** | Fixed — `urlparse` + tests |
| GitHub Action path | Action in `action/` subdirectory | `uses:` only works with root `action.yml` | **Action not usable as documented** | Fixed — moved to repo root |
| `fail-on-broken-links` | Referenced in README + action logic | Not declared as input in `action.yml` | **Undeclared input** | Fixed — added to inputs |

### Verified

| Claim | Verified against | Status |
|---|---|---|
| `/plugin install fact-check@everything-fact-checked` | `plugin.json` name=`fact-check`, `marketplace.json` name=`everything-fact-checked` | ✅ Consistent |
| `--plugin-dir <path>` loads a local plugin | `claude --help` | ✅ Confirmed |
| `efc version` | `pip install .` + `efc version` → `0.2.2` | ✅ Confirmed (clean venv) |
| `efc evidence evidence.json` | `pip install .` + run → `OK: 3 record(s) valid.` | ✅ Confirmed |
| CI badge resolves | HTTP 200 on the badge URL | ✅ Confirmed |
| 72 unit tests | `python3 -m unittest discover -s tests` → Ran 72 tests | ✅ Current |
| All 4 version locations match | `scripts/check_versions.py` → all 0.2.2 | ✅ Confirmed |
| Plugin validates | `claude plugin validate .` | ✅ Passed |

### Summary
- 6 errors found and fixed across v0.1.0–v0.2.2
- 8 claim groups verified against primary sources
- Overall reliability: **High** for install/usage, CLI, and validation claims

## Lesson

The two install-command errors are textbook cases of the failure mode this skill
exists to catch: a plausible-sounding command, emitted with confidence, never run.
The fix is process, not cleverness — run the check before publishing. That is now
part of the release routine (see the "Releasing" note in the README).
