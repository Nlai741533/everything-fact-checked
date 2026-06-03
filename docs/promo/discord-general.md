# Discord 社区帖子（通用版，适用于多个 Discord 服务器）

## 适用服务器
- MLOps Community
- Hugging Face Discord
- LangChain Discord
- Claude Discord
- Python Discord (#showcase)

## 帖子内容

Hey all 👋 I built a fact-checking tool for AI-generated research reports and wanted to share it here.

**The problem:** When LLMs produce research reports at scale, they don't fail randomly. They have 5 repeatable failure modes:

1. **Unit errors** — $4.2B → $4,200B (cross-language research is especially bad)
2. **Fabricated interpolation** — 6-point charts where only 2 data points were sourced
3. **Source conflation** — GMV cited as revenue, different metrics merged as same
4. **Stale data** — 2023 figures presented as 2025 actuals
5. **Attribution laundering** — blogs cited as SEC filings

**The tool:** EFC — CLI + GitHub Action + standalone agent skill

The killer feature is **source-content verification**: it fetches cited URLs and checks if the claimed numbers actually appear in the source text (not just whether the link resolves).

```bash
pip install everything-fact-checked
efc audit report.md
efc verify evidence.json
```

Stdlib-only Python, MIT, 72 tests.

**Links:**
- https://github.com/Nlai741533/EFC-Plugin
- https://github.com/Nlai741533/EFC-standalone (one-file version for any agent)

The repo fact-checks itself before every release — because the first version shipped with a hallucinated install command 😅

Would love to hear if others are seeing these same error patterns in AI output.
