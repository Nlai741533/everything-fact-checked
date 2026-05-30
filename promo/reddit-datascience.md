# Reddit r/datascience Post

## Title
I catalogued the 5 systematic error patterns in AI-generated data analysis reports — and built a tool to catch them

## Body

I work with a lot of AI-generated research and data analysis reports, and I started noticing the same errors showing up over and over. Not random mistakes — *systematic* patterns.

After tracking them across dozens of reports, I identified 5 repeatable failure modes:

**1. Unit/scale errors (most common, highest impact)**
Numbers lose or gain zeros. $4.2B becomes $4,200B. Cross-language research is especially bad — Chinese "亿" (100M) vs "billion" introduces a 10x error.

**2. Fabricated interpolation**
You ask the AI for a 5-year trend. It finds 2 data points and interpolates the rest. The chart looks clean and plausible — but 60% of the data is made up.

**3. Source conflation**
GMV reported as revenue. "Trade volume" as "exports." The metrics are related but not interchangeable. For marketplace businesses, GMV can be 5-20x revenue.

**4. Stale data as current**
2023 figures in a 2025 report, presented as "latest available." Or analyst forecasts treated as filed actuals.

**5. Attribution laundering**
A blog post cited as if it were an SEC filing. Secondary source treated as primary. Two levels of telephone game.

---

I built a tool called **EFC** that catches these systematically:

```bash
pip install everything-fact-checked

# Extract claims with priority triage
efc extract report.md --json

# Full audit
efc audit report.md

# Verify source content (fetches URLs, checks if claims appear in the text)
efc verify evidence.json
```

The source-content verification is the most useful part — it doesn't just check if a URL resolves, it fetches the page, extracts text, and checks whether the claimed figures actually appear near relevant terms.

There's also a GitHub Action for auto-checking .md reports in PRs, and a standalone Markdown skill file that works with any AI agent.

Stdlib-only Python, MIT license, 72 tests, zero dependencies.

**Repo:** https://github.com/Nlai741533/EFC-Plugin
**Standalone:** https://github.com/Nlai741533/EFC-standalone

Has anyone else here noticed these same patterns? I'm especially interested in:
- Other systematic failure modes I might be missing
- Whether fabricated interpolation shows up in your workflows too (I see it constantly)
- Better approaches to source-content verification
