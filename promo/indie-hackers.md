# Indie Hackers Post

## Title
I built a fact-checker after my AI hallucinated its own install command

## Body

### The Story

I asked an AI to write install instructions for a plugin. It confidently gave me:

```
claude skill add --url https://github.com/...
```

That command doesn't exist. The AI made it up with complete confidence.

This isn't a one-off. When LLMs do research at scale, they don't fail randomly — they have **5 systematic failure modes**:

1. **Unit errors**: $4.2 billion becomes $4,200 billion. Cross-language research (亿 vs billion) makes this worse.
2. **Fabricated data**: Charts with 6 data points where only 2 were sourced. The rest are interpolated.
3. **Metric conflation**: GMV reported as revenue. They're different things.
4. **Stale data**: 2023 figures presented as "the latest."
5. **Source laundering**: A blog post cited as if it were an official filing.

### The Product

I built **EFC (Everything Fact-Checked)** — a fact-checking tool that catches these 5 patterns:

- **CLI**: `pip install`, run locally or in CI
- **GitHub Action**: auto-checks markdown reports in PRs
- **Standalone skill**: one Markdown file, works with any AI agent

The most useful feature is source-content verification — it fetches cited URLs and checks whether the claimed figures actually appear in the source text.

### The Meta Twist

The repo now fact-checks itself before every release. Because of course the first version shipped with a hallucinated command.

### Tech Stack
- Python stdlib only (no dependencies)
- 72 tests, MIT licensed
- Works as a Claude Code plugin, standalone CLI, or GitHub Action

### Links
- **Full repo**: https://github.com/Nlai741533/EFC-Plugin
- **Standalone (one file)**: https://github.com/Nlai741533/EFC-standalone

Would love feedback from other indie hackers who work with AI-generated content. What error patterns have you seen?
