#!/usr/bin/env python3
"""Extract verifiable claims from an AI-generated report for fact-check triage.

This does NOT verify anything - verification requires opening primary sources
(a judgment task for the agent/human). It mechanises the tedious first step:
finding every specific, checkable claim and giving each a priority guess so
nothing slips through unreviewed.

To keep noise down it skips fenced code blocks and Markdown headings, and reports
the whole sentence a match sits in (not an isolated regex snippet).

Detected claim types:
  - figure       : currency / scaled numbers (e.g. "$2.1B", "10.6 billion")
  - percentage   : "30%", "12.5 %"
  - date         : standalone years and Month-Year references
  - superlative  : "first", "largest", "the only", "#1", etc.

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
# High-signal superlatives only. Bare "only" is excluded (too noisy: "for
# demonstration only", "list URLs only"); "the only" / "only X to" are kept.
SUPERLATIVE_RE = re.compile(
    r"\b(?:first|largest|biggest|smallest|fastest|leading|#1|number one|"
    r"best[- ]selling|world['’]?s\s+\w+est|the\s+only|only\s+\w+\s+to|"
    r"most\s+\w+|highest|lowest)\b",
    re.IGNORECASE,
)
_CODE_FENCE_RE = re.compile(r"^\s*(```|~~~)")
_HEADING_RE = re.compile(r"^\s*#{1,6}\s")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


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
        if re.search(r"[$¥€£]|billion|million|trillion|bn|亿|万", snippet, re.IGNORECASE):
            return "P0"
        return "P2"
    if claim_type in ("percentage", "superlative"):
        return "P1"
    return "P2"


def _sentence(line_text: str, start: int) -> str:
    """Return the sentence within line_text that contains offset `start`."""
    cursor = 0
    for part in _SENTENCE_SPLIT_RE.split(line_text):
        seg_start = line_text.find(part, cursor)
        if seg_start == -1:
            continue
        seg_end = seg_start + len(part)
        if seg_start <= start < seg_end:
            return part.strip()
        cursor = seg_end
    return line_text.strip()


def _is_real_figure(m: "re.Match") -> bool:
    """Bare integers with no currency symbol and no scale word are not claims
    (list numbers, page references, etc.)."""
    return bool(m.group("sym") or m.group("scale"))


def _content_lines(text: str):
    """Yield (line_no, line_text) for lines that are not code fences or headings."""
    in_code = False
    for line_no, line_text in enumerate(text.splitlines(), start=1):
        if _CODE_FENCE_RE.match(line_text):
            in_code = not in_code
            continue
        if in_code or _HEADING_RE.match(line_text):
            continue
        yield line_no, line_text


def extract_claims(text: str) -> list:
    """Return all detected claims, in document order. Pure function - no I/O."""
    claims = []
    counter = 0

    def add(line_no, ctype, line_text, span):
        nonlocal counter
        counter += 1
        snippet = _sentence(line_text, span[0])
        claims.append(
            Claim(
                claim_id=f"C{counter:03d}",
                line=line_no,
                type=ctype,
                snippet=snippet,
                priority=_priority_for(ctype, snippet),
            )
        )

    for line_no, line_text in _content_lines(text):
        for m in FIGURE_RE.finditer(line_text):
            if _is_real_figure(m):
                add(line_no, "figure", line_text, m.span())
        for m in PERCENT_RE.finditer(line_text):
            add(line_no, "percentage", line_text, m.span())
        my_spans = [mm.span() for mm in MONTH_YEAR_RE.finditer(line_text)]
        for m in MONTH_YEAR_RE.finditer(line_text):
            add(line_no, "date", line_text, m.span())
        for m in YEAR_RE.finditer(line_text):
            if any(s <= m.start() < e for s, e in my_spans):
                continue
            add(line_no, "date", line_text, m.span())
        for m in SUPERLATIVE_RE.finditer(line_text):
            add(line_no, "superlative", line_text, m.span())

    return claims


def to_markdown(claims: list) -> str:
    if not claims:
        return "_No verifiable claims detected._"
    rows = ["| ID | Line | Priority | Type | Claim |", "|---|---:|---|---|---|"]
    for c in claims:
        snippet = c.snippet.replace("|", "\\|")
        rows.append(f"| {c.claim_id} | {c.line} | {c.priority} | {c.type} | {snippet} |")
    return "\n".join(rows)


def to_json(claims: list) -> str:
    return json.dumps([asdict(c) for c in claims], ensure_ascii=False, indent=2)


def main(argv=None) -> int:
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
