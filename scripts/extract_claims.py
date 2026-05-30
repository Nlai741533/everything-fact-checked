#!/usr/bin/env python3
"""Extract verifiable claims from an AI-generated report for fact-check triage.

This does NOT verify anything — verification requires opening primary sources
(a judgment task for the agent/human). It mechanises the tedious first step:
finding every specific, checkable claim and giving each a priority guess so
nothing slips through unreviewed.

Detected claim types:
  - figure       : currency / scaled numbers (e.g. "$2.1B", "¥10.6 billion")
  - percentage   : "30%", "12.5 %"
  - date         : standalone years and Month-Year references
  - superlative  : "first", "only", "largest", "#1", etc.

Usage:
  python3 extract_claims.py REPORT.md              # markdown table
  python3 extract_claims.py REPORT.md --json       # JSON array
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict

# Currency-scaled figures: optional symbol, number, optional scale word.
FIGURE_RE = re.compile(
    r"(?P<sym>[$¥€£])?\s?"
    r"(?P<num>\d[\d,]*(?:\.\d+)?)"
    r"\s?(?P<scale>billion|million|thousand|trillion|bn|[KMB]\b|亿|万)?",
    re.IGNORECASE,
)
PERCENT_RE = re.compile(r"\d+(?:\.\d+)?\s?%")
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
MONTH_YEAR_RE = re.compile(
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(?:19|20)\d{2}\b",
    re.IGNORECASE,
)
SUPERLATIVE_RE = re.compile(
    r"\b(?:first|only|largest|biggest|leading|#1|number one|best[- ]selling|"
    r"world['’]?s\s+\w+est|most\s+\w+)\b",
    re.IGNORECASE,
)


@dataclass
class Claim:
    claim_id: str
    line: int
    type: str
    snippet: str
    priority: str


def _priority_for(claim_type: str, snippet: str) -> str:
    """Heuristic triage. Figures default high; superlatives need verification."""
    if claim_type == "figure":
        # A currency symbol or scale word signals a headline financial figure.
        if re.search(r"[$¥€£]|billion|million|trillion|bn|亿|万", snippet, re.IGNORECASE):
            return "P0"
        return "P2"
    if claim_type == "percentage":
        return "P1"
    if claim_type == "superlative":
        return "P1"
    return "P2"


def _context(line_text: str, start: int, end: int, width: int = 30) -> str:
    lo = max(0, start - width)
    hi = min(len(line_text), end + width)
    prefix = "…" if lo > 0 else ""
    suffix = "…" if hi < len(line_text) else ""
    return (prefix + line_text[lo:hi] + suffix).strip()


def _is_real_figure(m: re.Match) -> bool:
    """Filter out bare integers with no currency symbol and no scale word
    (those are usually list numbers, footnotes, etc., not claims)."""
    return bool(m.group("sym") or m.group("scale"))


def extract_claims(text: str) -> list[Claim]:
    """Return all detected claims, in document order. Pure function — no I/O."""
    claims: list[Claim] = []
    counter = 0

    def add(line_no: int, ctype: str, line_text: str, span: tuple[int, int]) -> None:
        nonlocal counter
        counter += 1
        snippet = _context(line_text, span[0], span[1])
        claims.append(
            Claim(
                claim_id=f"C{counter:03d}",
                line=line_no,
                type=ctype,
                snippet=snippet,
                priority=_priority_for(ctype, snippet),
            )
        )

    for line_no, line_text in enumerate(text.splitlines(), start=1):
        seen_spans: list[tuple[int, int]] = []
        for m in FIGURE_RE.finditer(line_text):
            if not _is_real_figure(m):
                continue
            seen_spans.append(m.span())
            add(line_no, "figure", line_text, m.span())
        for m in PERCENT_RE.finditer(line_text):
            add(line_no, "percentage", line_text, m.span())
        for m in MONTH_YEAR_RE.finditer(line_text):
            add(line_no, "date", line_text, m.span())
        # Plain years, but skip those already inside a Month-Year match.
        my_spans = [mm.span() for mm in MONTH_YEAR_RE.finditer(line_text)]
        for m in YEAR_RE.finditer(line_text):
            if any(s <= m.start() < e for s, e in my_spans):
                continue
            add(line_no, "date", line_text, m.span())
        for m in SUPERLATIVE_RE.finditer(line_text):
            add(line_no, "superlative", line_text, m.span())

    return claims


def to_markdown(claims: list[Claim]) -> str:
    if not claims:
        return "_No verifiable claims detected._"
    rows = [
        "| ID | Line | Priority | Type | Claim |",
        "|---|---:|---|---|---|",
    ]
    for c in claims:
        snippet = c.snippet.replace("|", "\\|")
        rows.append(f"| {c.claim_id} | {c.line} | {c.priority} | {c.type} | {snippet} |")
    return "\n".join(rows)


def to_json(claims: list[Claim]) -> str:
    return json.dumps([asdict(c) for c in claims], ensure_ascii=False, indent=2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", help="Path to the report file (markdown or text)")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of a table")
    args = parser.parse_args(argv)

    try:
        with open(args.report, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"error: cannot read {args.report}: {exc}", file=sys.stderr)
        return 2

    claims = extract_claims(text)
    print(to_json(claims) if args.json else to_markdown(claims))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
