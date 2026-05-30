# Copilot Coding Agent Instructions

## Project Overview

This is `everything-fact-checked`, a Claude Code plugin that fact-checks AI-generated research reports. It is a small, stdlib-only Python project with a Markdown-based skill and JSON schemas.

## Critical Rules

### Security — NEVER commit secrets
- **Never** put tokens, API keys, or credentials in any file.
- **Never** set git remote URLs that contain embedded credentials.
- If you need to authenticate with GitHub, use `GITHUB_TOKEN` from the Actions environment.
- The repo uses gitleaks pre-commit hooks — they will block secret-containing commits.

### Test-First Development
- Always run `python3 -m unittest discover -s tests -v` before submitting a PR.
- Every new behavior must include a test. Tests use stdlib `unittest` only.
- The golden tests in `tests/test_examples.py` pin script output against fixtures — if you change a script, update the fixture too.

### Version Consistency
- When bumping version: update BOTH `.claude-plugin/plugin.json` AND `.claude-plugin/marketplace.json` `version` fields.
- CI checks that these two match, and that they match the git tag on release pushes.

### Code Style
- Python scripts in `scripts/` are stdlib-only (no third-party dependencies). Keep it that way.
- The skill is pure Markdown at `skills/fact-check/SKILL.md`.
- JSON schemas go in `schemas/`.

### Documentation Integrity
- `FACTCHECK.md` is the repo's self-audit. It must reflect current reality — test counts, validation rules, verified claims.
- `README.md` claims must be verifiable. If you add a claim about what a script does, test it.

### PR Conventions
- Keep PRs focused and small.
- Update `CHANGELOG.md` with every change.
- Run `gitleaks detect --source .` locally if you touched anything credential-adjacent.
