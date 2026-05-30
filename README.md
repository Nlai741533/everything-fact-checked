# everything-fact-checked

A Claude Code plugin that systematically fact-checks AI-generated reports — catching hallucinated numbers, fabricated data points, and exaggerated claims before they ship.

[![CI](https://github.com/Nlai741533/everything-fact-checked/actions/workflows/ci.yml/badge.svg)](https://github.com/Nlai741533/everything-fact-checked/actions/workflows/ci.yml)

## The problem

LLM agents are increasingly used to produce research reports, market analyses, and data-heavy documents. These reports *look* authoritative but contain predictable failure modes that are hard to catch by reading alone:

- **Unit / scale errors** — a $5.3B figure that should be $530M because a unit conversion was dropped
- **Fabricated interpolation** — a chart shows 6 data points but only 2 were actually found; the rest were silently made up
- **Source conflation** — "trade volume" cited as "exports," or "GMV" reported as "revenue"
- **Stale data as current** — 2023 figures presented as 2025 actuals
- **Attribution laundering** — a media blog cited as if it were a regulatory filing

These aren't random errors. They're systematic patterns that emerge whenever an LLM does web research at scale. This plugin gives your agent a structured protocol to catch them — plus small scripts that mechanise the tedious first steps.

## What this is (and isn't)

- ✅ **A disciplined operating procedure** for an agent (or person) doing verification: triage, primary-source preference, chart/table tracing, marketing-claim labeling, and a standard evidence format.
- ✅ **Helper scripts** that extract claims and check links so nothing goes unreviewed.
- ❌ **Not** a push-button oracle. Verification of whether a source actually supports a claim is a judgment task; the agent still has to open primary sources. The scripts find *what to check*, not *whether it's true*.

## Install

This is a standard Claude Code plugin. Add the repo as a marketplace, then install:

```
/plugin marketplace add Nlai741533/everything-fact-checked
/plugin install fact-check@everything-fact-checked
```

Or try it for a single session without installing:

```bash
claude --plugin-url https://github.com/Nlai741533/everything-fact-checked
```

For local development on a clone:

```bash
claude --plugin-dir /path/to/everything-fact-checked
```

> Requires Claude Code with plugin support (tested on 2.1.x). There is no
> `claude skill add` command — use the plugin commands above.

## Usage

Once installed, ask Claude Code to fact-check any document:

```
fact-check this report
verify the numbers in the market analysis
audit the data in this deliverable
```

The skill runs a structured 6-step workflow: inventory claims → triage by risk (P0–P3) → verify P0/P1 against primary sources → cross-check charts/tables → audit the source list → produce a report. Every verdict is backed by a record in a [standard evidence format](skills/fact-check/SKILL.md#standard-evidence-format).

It also treats all source content as **untrusted data**, not instructions — so a document can't talk the fact-checker into marking itself "verified."

## Helper scripts

Dependency-free (Python 3.8+ stdlib). Run them directly on a report:

```bash
# Inventory every checkable claim with a priority guess
python3 scripts/extract_claims.py report.md
python3 scripts/extract_claims.py report.md --json

# Check that every source URL actually resolves
python3 scripts/check_links.py report.md
python3 scripts/check_links.py report.md --no-network   # list URLs only
```

## Example

[`examples/sample-report.md`](examples/sample-report.md) is a deliberately flawed (fictional) report containing one of each failure mode plus broken links. [`examples/expected-fact-check.md`](examples/expected-fact-check.md) shows the kind of output the skill should produce on it.

## Development

```bash
python3 -m unittest discover -s tests -v
```

CI runs the test suite, validates the plugin/marketplace manifests, and smoke-tests the scripts on every push.

## Repository layout

```
.claude-plugin/
  plugin.json          # plugin manifest
  marketplace.json     # lets the repo be added as a marketplace
skills/fact-check/
  SKILL.md             # the fact-check operating procedure
scripts/
  extract_claims.py    # claim inventory extractor
  check_links.py       # source-link checker
examples/              # sample flawed report + expected output
tests/                 # unit tests + fixtures
.github/workflows/     # CI
```

## Limitations

- The scripts use heuristics; they will miss claims phrased in words ("one million") and may surface borderline matches. They are a triage aid, not a guarantee.
- Link checking confirms a URL resolves, not that the page contains the attributed claim.
- The skill's quality depends on the agent following it and having access to primary sources (web/search tools).

## License

MIT — see [LICENSE](LICENSE).
