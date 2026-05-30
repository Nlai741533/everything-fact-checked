# Newsletter 投稿邮件（一封通用模板，发给多个 newsletter）

## Subject
Tool suggestion: EFC — catches the 5 systematic errors in AI-generated research reports

## Body
Hi,

I built a fact-checking tool that might be a good fit for your newsletter.

**One-line pitch:** EFC catches the 5 systematic ways AI errors creep into research reports — unit errors, fabricated data, source conflation, stale figures, and attribution laundering.

**Why it's interesting right now:**
- Every team using AI for research is hitting these same error patterns, but most don't realize it's systematic
- The tool started because the AI hallucinated its own install command (literally the failure mode it was built to catch)
- Available as CLI, GitHub Action, and a one-file agent skill
- Stdlib-only Python, MIT licensed, 72 tests, zero dependencies

**Links:**
- Full repo: https://github.com/Nlai741533/EFC-Plugin
- Standalone skill: https://github.com/Nlai741533/EFC-standalone
- Demo output: https://github.com/Nlai741533/EFC-Plugin#see-it-in-action

**Quick demo:**
```
$ efc audit report.md
Claims found: 18 (P0: 8, P1: 2)
Source URLs: 1 ok, 2 broken
  ❌ [not_found] 404 https://...
Reliability: Low
```

Happy to provide a longer writeup or guest post if that's more useful.

Thanks,
Nick

---

## 发送列表

| Newsletter | 投稿方式 | 预期响应时间 |
|---|---|---|
| TLDR AI | tips@tldrnewsletter.com | 1-3 天 |
| Ben's Bites | bensbites.com/submit | 1-2 天 |
| The Rundown AI | therundown.beehiiv.com | 2-3 天 |
| Bytes (Python) | bytes.vc/submit | 1 周 |
| AI Tool Report | aitoolreport.com/submit | 2-3 天 |
| There's An AI For That | theresanaiforthat.com/submit | 即时 |
| Future Tools | futuretools.io/submit | 即时 |
