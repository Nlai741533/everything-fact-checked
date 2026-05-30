# HN Launch Post

## Title
Show HN: EFC – A fact-checker that catches the 5 systematic ways AI lies in research reports

## Body

I caught my AI fabricating data in a research report. The scary part wasn't that it was wrong — it was that the errors were systematic and predictable.

After analyzing dozens of AI-generated research reports, I found 5 repeatable failure modes:

| # | Failure mode | Example |
|---|---|---|
| 1 | Unit/scale errors | $4.2B becomes $4,200B — a dropped conversion |
| 2 | Fabricated interpolation | 6-point chart where only 2 data points were actually sourced |
| 3 | Source conflation | GMV reported as revenue; "trade volume" as "exports" |
| 4 | Stale data as current | 2023 figures presented as 2025 actuals |
| 5 | Attribution laundering | A blog post cited as if it were an SEC filing |

These aren't random. They show up every time an LLM does research at scale.

I built EFC (Everything Fact-Checked) to catch them. It started as a Claude Code plugin, but the core insight is agent-agnostic — so I packaged it three ways:

1. **Standalone SKILL.md** — one file, zero dependencies, works with any AI agent (Pi, Claude, OpenClaw, Cursor, etc.) [1]
2. **CLI (`efc`)** — `pip install`, run locally or in CI
3. **GitHub Action** — auto fact-check markdown reports in PRs

Here's what a real audit looks like:

```
$ efc audit report.md
## Audit: report.md
Claims found:   18 (P0: 8, P1: 2)
Source URLs:    1 ok, 2 broken

  ❌ [not_found] 404 https://httpstat.us/404
  ❌ [unreachable] ERR https://example.invalid/acme/units-q4

Reliability: Low
```

And source-content verification (the most useful feature — fetches cited URLs and checks if the claimed figure actually appears):

```
$ efc verify evidence.json
✅ C002: found — Source contains 5 key terms from claim
🔌 C003: fetch_failed — Could not fetch source: unreachable host
```

The whole thing is stdlib-only Python (no dependencies), MIT licensed, and the repo fact-checks itself before every release (yes, really — FACTCHECK.md).

The standalone skill is intentionally just a Markdown file — no code, no install. You drop it in your agent's skill directory and it gets a structured 6-step verification workflow. This is the format I'd most like feedback on: is a protocol-only approach useful, or do people want more automation?

Repo: https://github.com/Nlai741533/EFC-Plugin
Standalone: https://github.com/Nlai741533/EFC-standalone

Happy to answer questions about the failure-mode taxonomy, the source-content verification approach, or the agent skill format.
