# Self Fact-Check: this repository

A fact-check skill should survive its own audit. This document is the result of
running the skill's own workflow (and its own scripts) against this repository's
docs. It is regenerated whenever the docs change.

## Fact-Check Report: everything-fact-checked docs
**Date:** 2026-05-30
**Coverage:** Install instructions, version claims, manifest references, helper-script
claims, badge, and the worked example, in `README.md`, `CHANGELOG.md`, and the
plugin manifests.
**Method:** Claims inventoried with `scripts/extract_claims.py`; links checked with
`scripts/check_links.py`; install/CLI claims verified against `claude --help` and
`claude --version` (2.1.143); manifest names verified against the JSON files.

### Errors Found (and fixed)

| Claim | Reported | Actual | Failure mode | Status |
|---|---|---|---|---|
| Install command | `claude skill add --url <repo>` | No such command exists in Claude Code 2.1.143 | **Unverified claim presented as fact** | Fixed — replaced with `/plugin marketplace add` + `/plugin install` |
| Single-session use | `claude --plugin-url https://github.com/.../<repo>` | `--plugin-url` expects a packaged `.zip` URL, not a repo page | **Unverified claim presented as fact** | Fixed — replaced with `git clone` + `--plugin-dir` |
| Script runtime | "Python 3.8+" | Only 3.11 (CI) and 3.12 actually tested | **Untested figure stated as verified** | Fixed — now states tested versions; 3.8 compatibility not claimed |

### Verified

| Claim | Verified against | Status |
|---|---|---|
| `/plugin install fact-check@everything-fact-checked` | `plugin.json` name=`fact-check`, `marketplace.json` name=`everything-fact-checked` | ✅ Consistent |
| `--plugin-dir <path>` loads a local plugin | `claude --help` | ✅ Confirmed |
| "Verified against Claude Code 2.1.143" | `claude --version` → 2.1.143 | ✅ Confirmed |
| CI badge resolves | HTTP 200 on the badge URL | ✅ Confirmed |
| "16 unit tests" | `python3 -m unittest discover -s tests` → Ran 16 tests | ✅ Confirmed |
| Example link predictions (sec.gov 200, httpstat.us/404 404, example.invalid unreachable) | `check_links.py examples/sample-report.md` | ✅ All match |

### Summary
- 3 errors found and fixed (2 high impact: both were wrong install commands)
- 6 claim groups verified against primary sources (the CLI itself, the manifests, the network)
- Overall reliability after fixes: **High** for the install/usage and example claims

## Lesson

The two install-command errors are textbook cases of the failure mode this skill
exists to catch: a plausible-sounding command, emitted with confidence, never run.
The fix is process, not cleverness — run the check before publishing. That is now
part of the release routine (see the "Releasing" note in the README).
