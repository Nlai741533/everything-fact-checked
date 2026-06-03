# Reddit Post — r/LocalLLaMA

## Title
I built a fact-checking skill/CLI that catches systematic errors in AI-generated research reports — works with any agent

## Body

Hey all — I've been working on something that might be useful to folks here who use agents for research.

**The problem:** When LLMs do research at scale (web search → synthesize → report), they don't fail randomly. They fail in 5 predictable, repeatable ways:

1. **Unit/scale errors** — $4.2B becomes $4,200B (dropped conversion, very common with cross-language research)
2. **Fabricated interpolation** — Chart shows 6 data points but only 2 were actually found in sources; the rest were filled in
3. **Source conflation** — GMV reported as revenue, "trade volume" as "exports" — different metrics merged as the same
4. **Stale data as current** — 2023 figures presented as 2025 actuals, or forecasts presented as real results
5. **Attribution laundering** — A blog cited as if it were a regulatory filing; secondary source treated as primary

**The solution:** EFC (Everything Fact-Checked). Three formats:

1. **Standalone SKILL.md** — literally one Markdown file, zero code, zero dependencies. Drop it in your agent's skill directory and it gets a structured 6-step fact-check workflow. Works with Claude, Cursor, Pi, OpenClaw, or any agent that reads skill/system prompt files.

2. **CLI (`efc`)** — `pip install everything-fact-checked`, then `efc audit report.md`. Stdlib-only Python, no third-party deps. Includes source-content verification: it fetches cited URLs and checks whether the claimed figures actually appear in the source text.

3. **GitHub Action** — auto fact-check .md files in PRs. Extracts claims, checks links, posts results to PR summary.

**Demo output:**
```
$ efc audit --no-network sample-report.md
## Audit: sample-report.md
Claims found:   18 (P0: 8, P1: 2)
Source URLs:    3 unchecked (--no-network)
Reliability: Low
```

```
$ efc verify evidence.json
✅ C002: found — Source contains 5 key terms from claim
🔌 C003: fetch_failed — Could not fetch source: unreachable
```

The standalone skill is what I'm most curious to get feedback on from this community. It's just a protocol — no executable code — but it gives any agent a consistent workflow for: inventory claims → triage → verify against primary sources → cross-check tables → audit source links → produce a verdict report.

Links:
- Full repo (CLI + Action + plugin): https://github.com/Nlai741533/EFC-Plugin
- Standalone skill (one file): https://github.com/Nlai741533/EFC-standalone

Both MIT licensed, 72 tests, zero dependencies.

Would love feedback on:
- Is a protocol-only skill (no code) useful, or do people want more automation baked in?
- The 5 failure modes — has anyone catalogued these differently?
- What claim types would you want the extractor to catch beyond figures/percentages/dates/superlatives?
