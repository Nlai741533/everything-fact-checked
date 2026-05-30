# Dev.to / Hashnode 技术博客

## Title
The 5 Systematic Failure Modes of AI Research Reports (and How to Catch Them)

## Tags
ai, llm, debugging, opensource

## Body

AI research reports look authoritative. The numbers line up, the charts are clean, and every claim has a source citation.

But when you actually open those sources, things fall apart.

After analyzing dozens of AI-generated research reports, I found that LLMs don't fail randomly when doing research at scale. They fail in **5 predictable, repeatable ways** — and once you know the patterns, you can catch them systematically.

---

## Failure Mode #1: Unit and Scale Errors (HIGHEST PRIORITY)

**What happens:** Numbers lose or gain zeros due to unit misinterpretation.

A report says "revenue was $4,200B." The source says $4.2B. Somewhere between reading the source and writing the report, the AI dropped a unit conversion.

This is extremely common in cross-language research:
- Chinese "亿" (100 million) vs "billion" — off by 10x
- "万" (10,000) dropped entirely — off by 10,000x
- Axis label on a chart misread — $4.2B → $4,200B

**How to catch it:** For every financial figure, trace it back to the original source and confirm the unit. Sanity check: does the number make sense given the entity's known scale? A startup with $50B revenue would be Fortune 100 — that's almost certainly wrong.

---

## Failure Mode #2: Fabricated Interpolation

**What happens:** When exact data is unavailable, the AI fills in the gaps.

Your report shows a clean 6-year revenue trend:

| Year | Revenue |
|---|---|
| 2019 | $0.9B |
| 2020 | $1.4B |
| 2021 | $1.9B |
| 2022 | $2.4B |
| 2023 | $3.1B |
| 2024 | $4.2B |

Looks great. But only FY2024 has a cited source. The other 5 points? The AI interpolated a smooth curve.

Real financial data has noise, acquisitions, currency effects. A perfectly smooth trend line is a red flag.

**How to catch it:** For every data series, ask: "Was each data point explicitly found in a source, or was it derived?" Compare totals against components — do sub-items actually sum to the reported total?

---

## Failure Mode #3: Source Conflation

**What happens:** Different metrics from different sources are merged as if they measure the same thing.

"The Acme app generated $1.2B in revenue" — but the source described **marketplace GMV** (Gross Merchandise Value), not revenue. For marketplace businesses, GMV is typically 5-20x revenue.

Other examples I've seen:
- "Cosmetics trade" (imports + exports) cited as "cosmetics exports"
- "Analyst consensus" treated as "filed figures"
- "Retail sales" confused with "wholesale revenue"

**How to catch it:** For every cited figure, verify the source explicitly uses the same metric name with the same definition and geographic scope.

---

## Failure Mode #4: Stale Data as Current

**What happens:** Data from an earlier period presented as the latest, or forecasts presented as actual results.

A report in 2026 cites "2025 revenue" from a source published in February 2025 — months before the fiscal year ended. That's an estimate, not a filing.

Or worse: 2023 data presented as "the latest available" when 2024 filings are already public.

**How to catch it:** Check the source date vs. the period it describes. If a source discusses future results before they could have been filed, it's using estimates.

---

## Failure Mode #5: Attribution Laundering

**What happens:** A fact found in a media article is cited as if it came from an official filing.

The report says "per SEC filings" but the actual source is a TechCrunch summary that itself cited a second-hand analyst note. Two levels of telephone game.

Or: a company press release cited as "industry data." Press releases are company statements, not independent verification.

**How to catch it:** Trace every claim to its earliest cited source. Primary = official filing/dataset. Secondary = analyst report. Tertiary = media article. A figure appearing only in media is unverified.

---

## I Built a Tool to Catch These

After seeing these patterns repeat, I built **EFC (Everything Fact-Checked)** — a fact-checking tool that knows these 5 failure modes and checks for them systematically.

It's available in three formats:

### CLI (`efc`)
```bash
pip install everything-fact-checked

# Full audit
efc audit report.md

# Verify source content (fetches URLs, checks if claims appear)
efc verify evidence.json
```

### GitHub Action
Auto fact-check markdown reports in every PR:
```yaml
- uses: Nlai741533/EFC-Plugin@v0.2.2
```

### Standalone SKILL.md (for any AI agent)
One Markdown file, zero dependencies. Drop it in your agent's skill directory and it gets a structured 6-step fact-check workflow. Works with Claude, Cursor, Pi, or any agent.

### Example output

```
$ efc audit report.md
## Audit: report.md
Claims found:   18 (P0: 8, P1: 2)
Source URLs:    1 ok, 2 broken
  ❌ [not_found] 404 https://...
  ❌ [unreachable] ERR https://...
Reliability: Low
```

```
$ efc verify evidence.json
✅ C002: found — Source contains 5 key terms from claim
🔌 C003: fetch_failed — source unreachable
```

---

## The Meta Part

The first version of this tool shipped with a hallucinated install command — a `claude skill add` command that doesn't exist. The AI made it up with complete confidence.

That's literally the failure mode this tool exists to catch.

Now the repo fact-checks itself before every release (see [FACTCHECK.md](https://github.com/Nlai741533/EFC-Plugin/blob/main/FACTCHECK.md)).

---

**Links:**
- Full repo (CLI + Action + Claude plugin): [EFC-Plugin](https://github.com/Nlai741533/EFC-Plugin)
- Standalone skill (one file, any agent): [EFC-Standalone](https://github.com/Nlai741533/EFC-standalone)

Both are MIT licensed, stdlib-only Python (no dependencies), 72 tests.

If you've seen other systematic failure modes in AI research output, I'd love to hear about them in the comments.
