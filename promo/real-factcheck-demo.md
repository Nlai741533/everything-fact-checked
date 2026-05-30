# Real Fact-Check Demo Post
# For: HN follow-up, Twitter, or standalone blog post

## Title
I fact-checked an AI-generated market report. Here's what I found.

## Body

AI research reports look authoritative. The numbers line up, the charts are clean, and every claim has a source citation.

But when you actually open those sources, things fall apart.

I ran EFC (a fact-checking tool I built) against a typical AI-generated market report. Here's what it caught:

### Error #1: $4,200 Billion vs $4.2 Billion

The report said: "Acme Robotics reported revenue of $4,200B in FY2024."

The source table said: $4.2B.

This is a unit/scale error — the AI dropped a conversion somewhere. $4,200B would make this fictional company larger than most countries' GDPs. A simple sanity check catches it, but humans read right past it because the number *looks* right in context.

### Error #2: GMV cited as Revenue

The report said: "The Acme app generated $1.2B in revenue."

The source described marketplace GMV (Gross Merchandise Value) — the total value of transactions flowing through the platform. Revenue is what the company keeps. For marketplace businesses, GMV is typically 5-20x revenue.

This is source conflation — two related but different metrics merged as if they're the same thing.

### Error #3: A 6-year revenue trend with 1 real data point

The report showed a clean revenue trend from 2019–2024:

| Year | Revenue |
|---|---|
| 2019 | $0.9B |
| 2020 | $1.4B |
| 2021 | $1.9B |
| 2022 | $2.4B |
| 2023 | $3.1B |
| 2024 | $4.2B |

But only FY2024 had a cited source. The other 5 data points? Fabricated interpolation — the AI filled in a smooth curve between two endpoints. Real financial data doesn't look this clean.

### Error #4: Two broken source links, one unverifiable claim

Of 3 source URLs:
- One resolved (SEC Edgar search page — generic, not the specific filing)
- One returned 404
- One host didn't resolve at all

The claim "first consumer robotics company to ship 1M units in a quarter" had zero corroborating sources.

### The audit output

```
$ efc audit report.md
## Audit: report.md
Claims found:   18 (P0: 8, P1: 2)
Source URLs:    1 ok, 2 broken
  ❌ [not_found] 404 https://httpstat.us/404
  ❌ [unreachable] ERR https://example.invalid/acme/units-q4

Reliability: Low
```

### What's systematic about these errors?

None of these are random mistakes. They're the 5 failure modes that show up whenever an LLM does research at scale:

1. **Unit errors** — dropped conversions, especially cross-language
2. **Fabricated interpolation** — filling gaps with smooth curves
3. **Source conflation** — merging related-but-different metrics
4. **Stale data** — old figures presented as current
5. **Attribution laundering** — weak sources cited as strong ones

A fact-checker that knows these patterns can catch them systematically, instead of hoping a human notices.

---

**Try it yourself:**
- CLI: `pip install everything-fact-checked` → `efc audit your-report.md`
- Any AI agent: [one-file skill](https://github.com/Nlai741533/EFC-standalone)
- GitHub PRs: [Action](https://github.com/Nlai741533/EFC-Plugin)

*Note: The report above is deliberately fictional (Acme Robotics doesn't exist), but the errors are real patterns found in actual AI-generated reports.*
