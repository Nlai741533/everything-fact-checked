# Reddit Post — r/ClaudeAI

## Title
Built a Claude Code plugin that fact-checks AI research reports — catches 5 types of systematic errors

## Body

If you use Claude (or any AI) to generate research reports, market analysis, or data-heavy docs — this might save you from publishing something wrong.

**EFC (Everything Fact-Checked)** is a Claude Code plugin that catches the 5 ways AI systematically errors in research reports:

| Error type | What it looks like |
|---|---|
| Unit errors | $4.2B → $4,200B (happens a LOT with currency conversions) |
| Fabricated data | 6-point chart where only 2 points came from real sources |
| Source conflation | GMV cited as revenue — they're different metrics |
| Stale data | 2023 figures presented as current |
| Attribution laundering | Blog post cited as SEC filing |

**Install:**
```
/plugin marketplace add Nlai741533/EFC-Plugin
/plugin install fact-check@EFC-Plugin
```

Or try it once without installing:
```bash
git clone https://github.com/Nlai741533/EFC-Plugin
claude --plugin-dir ./EFC-Plugin
```

Then just say "fact-check this report" or "check the numbers in this document."

**There's also a standalone version** — one SKILL.md file, no install needed, works with any AI agent. Good if you use multiple tools and want consistent fact-checking across all of them.

The repo is public: https://github.com/Nlai741533/EFC-Plugin

Happy to answer questions about how it works or what kinds of errors it catches.
