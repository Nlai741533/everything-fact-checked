# LinkedIn Post

I caught my AI fabricating data in a research report. The errors weren't random — they were systematic.

After analyzing dozens of AI-generated research reports, I found 5 repeatable failure modes:

1️⃣ Unit errors — $4.2B becomes $4,200B. A dropped conversion that makes a mid-cap company look larger than most countries.

2️⃣ Fabricated interpolation — Chart shows 6 data points but only 2 came from real sources. The rest were filled in with a smooth curve. (Real data has noise.)

3️⃣ Source conflation — GMV reported as revenue. "Trade volume" cited as "exports." Related but different metrics merged as the same thing.

4️⃣ Stale data as current — 2023 figures presented as 2025 actuals. Analyst forecasts treated as filed results.

5️⃣ Attribution laundering — A blog post cited as if it were an SEC filing. Two levels of telephone game, and nobody noticed.

These patterns show up every time an LLM does research at scale. They're not random — they're structural.

So I built EFC (Everything Fact-Checked) to catch them:
• CLI tool (pip install, run locally or in CI)
• GitHub Action (auto fact-check reports in PRs)
• Standalone skill file (one Markdown file, works with any AI agent)

The first version literally shipped with a hallucinated install command — which is exactly the failure mode it exists to catch. Now the repo fact-checks itself before every release.

If your team uses AI to produce research, reports, or data-heavy content — these 5 error types are already in your output. You just haven't looked yet.

Try it: https://github.com/Nlai741533/EFC-Plugin

#AI #LLM #FactChecking #Research #DataQuality #OpenSource
