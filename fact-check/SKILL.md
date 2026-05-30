---
name: fact-check
description: "Systematically fact-check AI-generated research reports and data-heavy documents. Trigger when the user asks to verify, fact-check, validate, or audit a report or document — especially those containing financial figures, market data, or claims sourced from web searches. Not for code review or general editing."
---

# Fact-Check Skill

A structured workflow for verifying AI-generated research reports against primary sources. Designed to catch the specific failure modes that LLM agents produce when doing web research at scale.

## When to use this skill

Trigger when the user:
- Asks to "fact-check" or "verify" a report, document, or deliverable
- Says "check the numbers" or "validate the data"
- Wants to audit an AI-generated research output
- Asks "are these figures correct?"
- Requests a source audit or provenance check

Do NOT trigger for:
- Code review
- General editing or proofreading
- Single factual questions (answer directly instead)

## The five failure modes of AI-generated reports

Every fact-check should look for these specific patterns, which are the most common errors in AI-generated research:

### 1. Unit and scale errors (HIGHEST PRIORITY)

**Pattern:** Numbers lose or gain a zero due to unit misinterpretation. Common in cross-language research where units differ (e.g., "million" vs "billion," local currency units like 万/亿/lakh/crore, metric vs imperial). Also common when LLMs summarize tables or charts and misread the unit label.

**How to detect:**
- Flag every financial figure and trace it back to the original source
- Check: does the number make sense given the entity's known scale?
- Sanity check: compare against publicly known benchmarks. A startup with $50B revenue would be Fortune 100 — that's almost certainly wrong.

**Test:** For every figure, confirm the unit in the original source matches what's reported. Pay special attention to currency conversions, scale words, and table/chart axis labels.

### 2. Fabricated interpolation

**Pattern:** When exact data is unavailable, LLMs interpolate or estimate values rather than flagging the gap. This shows up most in:
- Historical time series where only endpoints were found
- Sub-category breakdowns where only the total was disclosed
- Market size figures where only growth rates were cited

**How to detect:**
- For every data series (charts, tables), ask: "Was each data point explicitly found in a source, or was it derived?"
- If a chart shows 6 data points but only 2 were directly cited, the other 4 are suspect
- Compare totals against components — do sub-items sum to the reported total?

### 3. Source conflation

**Pattern:** Different metrics from different sources are merged as if they measure the same thing. Examples:
- "Trade volume" (imports + exports) cited as "exports"
- "Retail sales" confused with "wholesale revenue"
- "GMV" (gross merchandise value) treated as "revenue"
- "Analyst consensus" vs "filed figures" not distinguished

**How to detect:**
- For every cited figure, verify the source explicitly uses the same metric name
- Check if "revenue" means operating revenue, total revenue, or GMV
- Verify that the geographic scope matches (global vs domestic vs regional)

### 4. Stale or future data presented as current

**Pattern:** Data from an earlier period presented as if it's the latest, or analyst forecasts presented as actual results.

**How to detect:**
- Check date of source article vs. the period it describes
- Verify that "2025 data" comes from a source published after the reporting deadline
- If a source discusses future results before they could have been filed, it's likely using estimates, not actuals

### 5. Attribution laundering

**Pattern:** A fact found in Source A is cited as coming from Source B, or a secondary source is cited as if it were primary.

**How to detect:**
- Trace every claim to its earliest cited source
- Primary = official filing or dataset. Secondary = analyst report. Tertiary = media article.
- If a figure appears only in a media summary and not in any filing or official dataset, treat it as unverified

## Fact-check workflow

### Step 1: Inventory all specific claims

Extract every specific, verifiable claim from the document:
- Financial figures (revenue, profit, growth rates)
- Market data (market size, share percentages, rankings)
- Factual statements (dates, launches, partnerships, expansions)
- Quotations and attributed statements

### Step 2: Triage by risk

Rank claims by consequence of being wrong:

| Priority | Criteria | Example |
|---|---|---|
| **P0 — Critical** | Specific financial figure that drives a conclusion | "Company X revenue $2.1B" |
| **P1 — High** | Market data used for comparison or trend | "Global market size $180B" |
| **P2 — Medium** | Factual claim that shapes narrative | "Brand Y entered US retail in Q2" |
| **P3 — Low** | Qualitative assessment or editorial judgment | "The market is shifting toward premiumization" |

### Step 3: Verify P0 and P1 claims against primary sources

For each P0/P1 claim:
1. Identify the original source (filing, official report, dataset)
2. Open the source directly (not via a search summary)
3. Find the exact figure in the source document
4. Compare: reported value vs. source value
5. If discrepancy found, determine if it's a rounding difference, unit error, or fabrication

**Primary source hierarchy:**
1. Company filings (SEC, stock exchange filings, regulatory databases)
2. Official statistics (government bureaus, central banks, customs)
3. Analyst research PDFs (brokerage reports, research firms)
4. Company IR pages and press releases
5. Tier-1 financial media (Reuters, Bloomberg, FT, domain-specific outlets)
6. Everything else

### Step 3.5: Verify qualitative claims (events, partnerships, product launches)

Quantitative errors (wrong numbers) are the most visible failure mode, but qualitative claims — "Brand X entered Market Y" — can be equally wrong and harder to detect. Apply the **dual-source confirmation rule**:

**Rule: Every claimed event must be confirmed from two independent sides.**

| Source type | Example | Reliability |
|---|---|---|
| **Official side** | Company website, IR page, official social media | Confirms intent and framing |
| **Counterpart side** | Partner announcement, platform listing, press release | Confirms the event actually happened |
| **Third party** | Media report, user-generated content, data platform | Confirms visibility beyond the two parties |

**Minimum standard:**
- Official side + Counterpart side = Confirmed
- Official side only = "Per company announcement, not independently confirmed"
- Single media report with no primary source = "Unverified, per [media outlet]"
- Zero sources found after searching = Remove or flag as unverified

**Three common fabrication patterns in qualitative claims:**

1. **Entity contagion:** One company did X -> agent attributes X to multiple companies in the same sector.
   - *Detection:* When multiple entities in the same section claim the same type of event, verify each independently.

2. **Channel conflation:** A company entered Channel A -> agent upgrades it to Channel B (more prestigious).
   - *Detection:* When a claim involves a specific named location or partner, search for the company + that specific partner. If nothing comes up, the claim is suspect.

3. **Status inflation:** A company is "planning" or "discussing" X -> agent writes it as completed.
   - *Detection:* Check verb tense in the source. "Will launch" is not "has launched." "Plans to enter" is not "entered."

**Practical verification checklist for expansion/partnership claims:**

For each "Company X did Y in Market Z" claim:
1. Search in the local language of the target market (not just English)
2. Check the company's official channels for the target market
3. Check the partner/channel's website or social media for the company
4. If a specific number is given (e.g., "200+ locations"), find the source for that number
5. If a specific date is given, verify it against a dated source
6. If the claim includes superlatives ("first," "only," "largest"), verify no counterexamples exist

### Step 4: Cross-check chart and table data

For every chart and table:
1. Do the column totals / sub-items sum to the reported total?
2. Does each data point have a traceable source?
3. Are growth rates consistent with the absolute figures? (e.g., if 2024 is $3.89B and growth is 30%, then 2025 should be ~$5.06B)
4. Are units consistent across the visualization?

### Step 5: Audit the source list

Check every URL in the source list:
1. Does the URL actually resolve?
2. Does the linked document contain the attributed information?
3. Are primary sources (filings) distinguished from secondary sources (media)?
4. Is the source in the original language of the data?

### Step 6: Produce the fact-check report

Output format:

```
## Fact-Check Report: [Document Name]
**Date:** [Date]
**Coverage:** [What was checked]

### Verified
| Claim | Source | Status |
|---|---|---|
| [Exact claim] | [Source URL] | Confirmed |

### Errors Found
| Claim | Reported | Actual | Source | Impact |
|---|---|---|---|---|
| [Exact claim] | [Wrong value] | [Correct value] | [Correction source] | [High/Medium/Low] |

### Unverifiable
| Claim | Reason | Recommendation |
|---|---|---|
| [Claim] | [Why it can't be verified] | [Flag, remove, or hedge] |

### Summary
- [X] claims verified
- [Y] errors found ([Z] high impact)
- [W] claims unverifiable
- Overall reliability: [High/Medium/Low]
```

## Red flags that trigger deeper investigation

When you see these patterns in an AI-generated report, stop and verify:

1. **A number that appears in only one source** — especially if that source is a media summary, not a filing
2. **A perfect data series** — real data has noise; a perfectly smooth trend line may be interpolated
3. **Sub-category breakdowns for entities that don't disclose them** — if the annual report doesn't break out sub-categories, any breakdown is an estimate
4. **Market size figures without a clear methodology note** — "the market is $X billion" without saying whose estimate
5. **Historical data that wasn't explicitly searched for** — if the agent searched for "2025 revenue" but the chart shows 2020-2025, the earlier years may be fabricated
6. **Any figure from a rate-limited or failed search** — the agent may have filled in the gap from training data
7. **Currency conversions without a stated rate** — the conversion itself may be wrong
8. **Multiple entities claiming the same type of event** — entity contagion; verify each independently
9. **Expansion claims with a specific named location** — these are specific enough to search for directly. If you can't find it, it's likely fabricated
10. **Superlatives without a cited source** — "first/only/most" require exhaustive verification; if no third party confirms, downgrade to "among the first"
11. **Claims that originate from a sub-agent** — treat all sub-agent output as unverified until independently confirmed. Sub-agents operate with less context and more pressure to produce complete-looking output

## Product and service claims: a specialized protocol

Product/service claims in AI-generated reports have their own distinct failure modes. Apply these checks to every product card or launch mention:

### P1: Verify pricing against official sources

**Never estimate pricing.** AI agents routinely fabricate price points that "feel right" for a brand's positioning, but actual prices can be dramatically different — especially for new premium offerings.

**Protocol:**
1. Find the official store, website, or pricing page
2. Search for the specific product or service name
3. Record the exact listed price (not promotional/discounted price)
4. If not yet listed (pre-launch), state "pricing not yet publicly available"

**Common error:** Using a brand's average price range to estimate a new premium line's pricing. New lines are often priced 30-100% above the existing range. Estimating with the old range always underestimates.

### P2: Distinguish marketing claims from verified facts

AI agents cannot tell the difference between a company's marketing language and an independently verified claim. Both sound authoritative in a press release. The fact-checker must label accordingly:

| Signal phrase | What it likely means | How to report it |
|---|---|---|
| "First of its kind" / "industry first" | Company's own claim, no independent verification | "Marketed as the first [X], per company announcement" |
| "Co-developed with" / "in partnership with" | May mean anything from formal partnership to a single advisory meeting | "Collaborates with [institution], per company statement" |
| "Certified" / "accredited" | Could mean regulatory certification or in-house testing | Verify against regulatory databases; if not found, say "per company testing" |
| "Clinically proven" / "scientifically validated" | Likely company-commissioned study, not peer-reviewed research | "Company-commissioned testing shows..." |
| "#1 selling" / "market leader" | Check: by what metric, what time period, what geography? | Specify the exact scope: "#1 on [platform] in [category], [time period]" |

**Rule of thumb:** If a claim sounds impressive and appears only in company-owned channels (website, press releases, social media), treat it as a marketing claim. Only if the same claim appears in independent media or regulatory databases should it be treated as verified fact.

### P3: Check data freshness

Performance data (revenue, GMV, user counts) degrades quickly. A figure from a 2024 article is stale by the time a 2026 report is published.

**Protocol:**
1. Note the date of the source article providing the performance data
2. Compare to the report's stated data cut-off date
3. If the data is more than 6 months old, either find updated figures or explicitly state the vintage: "As of [date], [metric] was [value]; more recent data not yet available"

### P4: Verify strategic interpretation isn't over-reading

Strategic interpretation attached to events is editorial, not factual — it doesn't need fact-checking in the same way. But it can still be wrong in a specific way: **attributing strategic intent where none exists.**

| Interpretation | Risk |
|---|---|
| "Company's entry into [category] signals a diversification push" | Reasonable inference from a new category entry |
| "This launch signals the company sees [segment] as a growth lever" | Supported by the launch itself |
| "This is the first top-10 company to enter with a full [product] line" | Requires exhaustive verification of all other top-10 companies |

**Protocol:** For each strategic interpretation, ask: "Is this an inference from observable facts, or is it claiming a fact I haven't verified?" Inferences are fine; unverified factual claims within interpretations are not.

## Quality bar

Before signing off on a fact-check:
- Every P0 claim has been verified against a primary source
- Every chart's data points have been traced to either a source or flagged as estimated
- Unit conversions have been explicitly checked
- At least one source in the original language of the data was consulted
- The error report is honest about what could NOT be verified, not just what could
- Pricing has been checked against official sources
- Marketing claims are labeled as such, not presented as verified facts
- Performance data (revenue, GMV, user counts) is dated with its source vintage
