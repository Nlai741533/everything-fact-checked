# everything-fact-checked

A skill for Claude Code that systematically fact-checks AI-generated reports — catching hallucinated numbers, fabricated data points, and exaggerated claims before they ship.

## The problem

LLM agents are increasingly used to produce research reports, market analyses, and data-heavy documents. These reports *look* authoritative but contain predictable failure modes that are hard to catch by reading alone:

- **Unit errors** — a $5.3B figure that should be $530M because a unit conversion was dropped
- **Fabricated interpolation** — a chart shows 6 data points but only 2 were actually found; the rest were silently made up
- **Source conflation** — "trade volume" cited as "exports," or "GMV" reported as "revenue"
- **Stale data as current** — 2023 figures presented as 2025 actuals
- **Attribution laundering** — a media blog cited as if it were a regulatory filing

These aren't random errors. They're systematic patterns that emerge whenever an LLM does web research at scale. This skill gives your agent a structured protocol to catch them.

## Install

```bash
claude skill add --url https://github.com/Nlai741533/everything-fact-checked
```

## Usage

After installing, simply ask Claude Code to fact-check any document:

```
fact-check this report
```
```
verify the numbers in the market analysis
```
```
audit the data in this deliverable
```

The skill automatically triggers when it detects fact-checking intent and runs a structured 6-step workflow:

1. **Inventory** all specific claims (financial figures, market data, factual statements)
2. **Triage** by risk (P0 critical through P3 low)
3. **Verify** P0/P1 claims against primary sources
4. **Cross-check** charts and tables for internal consistency
5. **Audit** the source list for broken links and attribution accuracy
6. **Report** findings in a structured format with clear verdicts

## What it catches

### Quantitative errors
- Numbers with wrong units or scale (the #1 source of errors in cross-language research)
- Interpolated data points presented as real (smooth trend lines are a red flag)
- Growth rates that don't match the absolute figures
- Currency conversions without stated rates

### Qualitative fabrication
- **Entity contagion** — one company did X, so the agent says three companies did X
- **Channel conflation** — entered retailer A, reported as entering retailer B (more prestigious)
- **Status inflation** — "plans to launch" becomes "has launched"
- Superlatives ("first," "only," "largest") without verification

### Source problems
- Secondary sources cited as primary
- URLs that don't resolve or don't contain the attributed information
- Marketing claims reported as verified facts
- Stale data presented without vintage dates

## Output

The skill produces a structured fact-check report:

| Section | What it contains |
|---|---|
| **Verified** | Claims confirmed against primary sources |
| **Errors Found** | Discrepancies with reported vs. actual values and impact rating |
| **Unverifiable** | Claims that couldn't be confirmed, with recommendations (flag, remove, or hedge) |
| **Summary** | Claim counts, error counts, and overall reliability rating |

## When NOT to use this

- Code review (use a code review tool)
- General editing or proofreading
- Single factual questions (just ask directly)

## Why this exists

This skill was built from real experience fact-checking AI-generated research reports at scale. Every rule in it exists because an AI agent made that exact mistake in production — and the mistake was only caught after manual review. The goal is to make that manual review systematic and teachable to another AI agent.

## License

MIT
