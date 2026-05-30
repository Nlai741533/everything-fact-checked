# Expected fact-check output for `sample-report.md`

This is the kind of result the fact-check skill should produce on the fictional
sample report. It illustrates each of the five failure modes plus a broken link.

## Fact-Check Report: Acme Robotics Market Brief (FICTIONAL)
**Date:** 2026-05-30
**Coverage:** All P0/P1 claims, the revenue table, and the source list.

### Errors Found

| Claim | Reported | Actual | Failure mode | Impact |
|---|---|---|---|---|
| FY2024 revenue | $4,200B | (fictional — but $4.2B per the table) | **Unit/scale error**: $4,200B would exceed global GDP-scale sanity; the table says $4.2B | High |
| "first consumer robotics company to ship 1M units in a quarter" | stated as fact | no independent source | **Superlative without verification** | Medium |
| App "generated $1.2B in revenue" | revenue | the source describes marketplace GMV, not revenue | **Source conflation** (GMV ≠ revenue) | High |

### Unverifiable

| Claim | Reason | Recommendation |
|---|---|---|
| 2019–2023 revenue series | Only FY2024 appears in any cited source; earlier points may be interpolated | **Fabricated interpolation** — flag each year or cite per-year source |
| Dubai Airport duty-free entry | Specific named location, no resolving source | Search brand + "Dubai Airport"; if nothing, remove |
| Store openings "in 2024" | No dated source; could be a plan, not completed | Verify verb tense and date against a primary source |

### Broken links

| URL | Status |
|---|---|
| https://example.invalid/acme/units-q4 | unreachable (host does not resolve) |
| https://httpstat.us/404 | 404 Not Found |

### Summary
- 0 claims verified against primary sources (sample has no real sources)
- 3 errors found (2 high impact)
- 3 claims unverifiable, 2 source links broken
- Overall reliability: **Low** — do not publish without correction

---

### Sample evidence record (per the skill's standard evidence format)

```json
{
  "claim_id": "C001",
  "claim_text": "Acme Robotics reported revenue of $4,200B in FY2024",
  "location": "Summary, line 9",
  "priority": "P0",
  "type": "financial_figure",
  "verdict": "error",
  "reported_value": "$4,200B",
  "source_value": "$4.2B (per revenue table)",
  "source_url": null,
  "source_tier": "tertiary",
  "source_date": null,
  "method": "Internal inconsistency: summary says $4,200B, table says $4.2B; sanity check fails",
  "impact": "high",
  "notes": "Unit/scale error — 1000x inflation, likely a 'billion vs million' or stray comma"
}
```
