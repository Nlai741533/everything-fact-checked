# Contributing to EFC-Plugin

Thanks for your interest! This project is small and intentionally simple — stdlib Python, Markdown skills, JSON schemas. We welcome PRs that keep it that way.

## Quick Start

```bash
git clone https://github.com/Nlai741533/EFC-Plugin
cd EFC-Plugin

# Install pre-commit hooks (catches secrets + file hygiene)
pre-commit install

# Run tests
python3 -m unittest discover -s tests -v
```

## Development Workflow

1. **Fork and branch** — create a feature branch from `main`
2. **Write the test first** — every new behavior needs a test
3. **Make it pass** — keep scripts stdlib-only (no third-party dependencies)
4. **Run the full suite** — `python3 -m unittest discover -s tests -v`
5. **Update docs** — if you changed a script's behavior, update README and CHANGELOG
6. **Open a PR** — CI must pass (tests, secret scan, version consistency, plugin validation)

## Code Style

- **Source** (`src/efc/`): stdlib only, no third-party runtime dependencies. The
  `scripts/*.py` files are thin shims that import from the installed `efc`
  package, so run `pip install -e .` before invoking them directly.
- **Tests** (`tests/`): stdlib `unittest`. No pytest, no fixtures library.
- **Skill** (`skills/fact-check/SKILL.md`): pure Markdown.
- **Schemas** (`schemas/`): JSON Schema draft-07.

## What to Contribute

Good first issues:

- Add a new claim type to `src/efc/_extract_claims.py` (e.g., named entities, quotes, "according to" attribution) with matching tests
- Add a fixture for a failure mode that isn't covered yet
- Add a new example report (flawed policy brief, startup memo, etc.)
- Improve URL extraction edge cases in `src/efc/_check_links.py`

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add CAGR detection to claim extractor
fix: reject empty-host URLs in evidence validator
docs: update FACTCHECK.md with new test count
chore: bump CI Python versions
```

## Version Bumping

When changing version, update **all three** locations:

1. `.claude-plugin/plugin.json` → `version`
2. `.claude-plugin/marketplace.json` → `plugins[0].version`
3. Tag the release: `git tag -a v0.x.y`

CI checks these are in sync on every push.

## Questions?

Open an issue with the `question` label.
