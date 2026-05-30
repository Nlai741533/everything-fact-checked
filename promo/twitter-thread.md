# Twitter/X Thread

---

🧵 I caught my AI fabricating data in a research report.

The scary part? The errors weren't random — they were SYSTEMATIC.

After analyzing dozens of AI research reports, I found 5 repeatable failure modes. Let me show you 👇

1/10

---

Failure Mode #1: UNIT ERRORS

The AI turned $4.2 billion into $4,200 billion.

A single dropped unit conversion — and suddenly a mid-cap company has more revenue than most countries.

This is the most common and most dangerous error.

2/10

---

Failure Mode #2: FABRICATED INTERPOLATION

Your AI found 2 data points for 2024 and 2020. The chart shows 6 points.

Where did the other 4 come from? The AI filled in the gaps.

Real data has noise. A perfectly smooth trend line is a red flag.

3/10

---

Failure Mode #3: SOURCE CONFLATION

"App generated $1.2B in revenue" — but the source said GMV, not revenue.

GMV ≠ Revenue. Trade volume ≠ Exports. Analyst consensus ≠ Filed figures.

These are different metrics merged as if they're the same.

4/10

---

Failure Mode #4: STALE DATA AS CURRENT

2023 figures presented as "the latest data." Analyst forecasts presented as actual results.

A Feb 2026 article discussing "2025 results" is using estimates, not filings.

Your report looks authoritative. The data is outdated.

5/10

---

Failure Mode #5: ATTRIBUTION LAUNDERING

A fact from Source A (a blog) is cited as coming from Source B (an SEC filing).

A media summary treated as a primary source.

The citation chain is broken — and no one noticed.

6/10

---

I built EFC (Everything Fact-Checked) to catch these systematically.

It's a structured 6-step workflow:
1. Inventory every claim
2. Triage by risk (P0-P3)
3. Verify critical claims against primary sources
4. Cross-check charts & tables
5. Audit every source link
6. Produce a verdict report

7/10

---

The best part? It also VERIFIES SOURCE CONTENT.

Not just "does the link resolve?" but "does the page actually contain the number you claimed?"

```
$ efc verify evidence.json
✅ C002: found — 5 key terms match
🔌 C003: fetch_failed — source unreachable
```

8/10

---

3 ways to use it:

📄 Standalone SKILL.md — one file, zero dependencies, works with ANY AI agent (Claude, Cursor, Pi, etc.)

💻 CLI — pip install, run locally or in CI

🔄 GitHub Action — auto fact-check .md reports in every PR

All stdlib Python. No dependencies. MIT licensed.

9/10

---

🔗 Full plugin + CLI: github.com/Nlai741533/EFC-Plugin
📄 Standalone skill: github.com/Nlai741533/EFC-standalone

The repo even fact-checks itself before every release (FACTCHECK.md) — because the first version shipped with a hallucinated install command 🙃

If your team uses AI for research, try it. The 5 failure modes will show up.

10/10
