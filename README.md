# everything-fact-checked

**Your AI wrote a confident report. Is it actually *true*?**

`everything-fact-checked` is a Claude Code plugin that turns your agent into a rigorous fact-checker — catching hallucinated numbers, fabricated data points, and exaggerated claims *before* they reach your reader.

[![CI](https://github.com/Nlai741533/everything-fact-checked/actions/workflows/ci.yml/badge.svg)](https://github.com/Nlai741533/everything-fact-checked/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> 🪞 This repo eats its own dog food: it is fact-checked against itself before every release. See [`FACTCHECK.md`](FACTCHECK.md).

---

## Why you'll want this

LLM agents are great at producing reports that *look* authoritative. The trouble is the parts that aren't — and they fail in **predictable, repeatable ways**:

| Failure mode | What it looks like |
|---|---|
| 🔢 **Unit / scale errors** | $5.3B that should be $530M — a dropped conversion |
| 📈 **Fabricated interpolation** | A 6-point chart where only 2 points were ever found |
| 🔀 **Source conflation** | "GMV" reported as "revenue"; "trade" as "exports" |
| 🕰️ **Stale data as current** | 2023 figures presented as 2025 actuals |
| 🎭 **Attribution laundering** | A blog cited as if it were a regulatory filing |

These aren't random slips — they're systematic patterns that show up whenever an LLM does research at scale. This plugin gives your agent a **structured protocol** to hunt them down, plus small scripts that automate the tedious first steps.

## See it in action

Point it at a flawed report and it produces a verdict-by-verdict audit:

```
> fact-check examples/sample-report.md

❌ Errors Found
| Claim                         | Reported  | Actual              | Mode             |
|-------------------------------|-----------|---------------------|------------------|
| FY2024 revenue                | $4,200B   | $4.2B (per table)   | Unit/scale error |
| App "generated $1.2B revenue" | revenue   | marketplace GMV     | Source conflation|

⚠️ Unverifiable
| 2019–2023 revenue series      | only FY2024 had a source → likely interpolated     |

🔗 Broken links: 2 of 3 source URLs don't resolve
Overall reliability: Low — do not publish without correction
```

Try it yourself: [`examples/sample-report.md`](examples/sample-report.md) is a deliberately flawed (fictional) report with one of each failure mode, and [`examples/expected-fact-check.md`](examples/expected-fact-check.md) shows the target output.

## Quick start

It's a standard Claude Code plugin — two lines to install:

```
/plugin marketplace add Nlai741533/everything-fact-checked
/plugin install fact-check@everything-fact-checked
```

Or kick the tires for a single session, no install:

```bash
git clone https://github.com/Nlai741533/everything-fact-checked
claude --plugin-dir ./everything-fact-checked
```

> Verified against Claude Code 2.1.143. There is no `claude skill add` command —
> use the plugin commands above. (`--plugin-url` exists but expects a packaged
> `.zip` URL, not a repo page, so it is intentionally not shown here.)

Then just ask, in plain language:

```
fact-check this report
verify the numbers in the market analysis
audit the data in this deliverable
```

## How it works

The skill runs a structured 6-step workflow:

1. **Inventory** every specific, checkable claim
2. **Triage** by risk (P0 critical → P3 cosmetic)
3. **Verify** P0/P1 claims against *primary* sources
4. **Cross-check** charts and tables for internal consistency
5. **Audit** the source list (do the links even resolve?)
6. **Report** — every verdict backed by a record in a [standard evidence format](skills/fact-check/SKILL.md#standard-evidence-format)

It also treats all source content as **untrusted data, not instructions** — so a document can't sweet-talk the fact-checker into stamping itself "verified."

### What it is (and isn't)

- ✅ **A disciplined operating procedure** — triage, primary-source preference, chart/table tracing, marketing-claim labeling, a standard evidence format.
- ✅ **Helper scripts** that extract claims and check links so nothing goes unreviewed.
- ❌ **Not a push-button oracle.** Deciding whether a source *truly* supports a claim is a judgment call — the agent still opens the primary sources. The scripts tell you *what to check*, not *whether it's true*.

## Helper scripts

No third-party dependencies — standard library only. Tested on Python 3.11 (CI) and 3.12.

```bash
# Inventory every checkable claim with a priority guess
python3 scripts/extract_claims.py report.md
python3 scripts/extract_claims.py report.md --json

# Check that every source URL actually resolves
python3 scripts/check_links.py report.md
python3 scripts/check_links.py report.md --no-network   # list URLs only
```

## 🛠️ Build on it

This is designed to be a **foundation, not a finished product** — the skill is plain Markdown and the scripts are tiny, readable, and dependency-free. PRs and forks are very welcome. Some directions that would make it more powerful:

- **More extractors** — the inventory already covers figures, percentages, dates, and superlatives; add named entities, quotes, and currency-conversion pairs.
- **Source-content verification** — fetch a cited URL and check it actually contains the attributed figure (the current scripts only confirm the link resolves).
- **PDF & table parsing** — extract claims straight from filings and spreadsheets.
- **Exchange-rate sanity checks** — flag conversions made without a stated rate.
- **Domain packs** — tuned source hierarchies for finance, science, law, medicine, etc.
- **Editor / CI integrations** — run the audit automatically on every draft or pull request.

New to the repo? Good first issues: add a new claim type to `extract_claims.py` (with a test), or add a fixture for a failure mode that isn't covered yet.

## Contributing

```bash
python3 -m unittest discover -s tests -v
```

CI validates the plugin/marketplace manifests, runs the test suite, and smoke-tests the scripts on every push. Please add a test with any new behavior — and run the scripts on your own change, in the spirit of the project. 🙂

### Releasing

Before any doc change ships, the repo is fact-checked against itself: install commands are run against `claude --help`/`--version`, links are checked, and claims are verified against primary sources. The result lives in [`FACTCHECK.md`](FACTCHECK.md). (Round 1 shipped a fabricated `claude skill add` command — this routine exists so that never happens again.)

## License

[MIT](LICENSE) — use it, fork it, ship it. If it saves you from publishing a wrong number, ⭐ the repo so others can find it too.
