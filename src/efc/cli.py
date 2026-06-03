#!/usr/bin/env python3
"""efc — the everything-fact-checked CLI.

Subcommands:
  efc extract   — inventory verifiable claims
  efc links     — check source URLs
  efc evidence  — validate evidence records
  efc audit     — full audit (extract + links + summary)
  efc verify    — verify source content matches claims
  efc version   — show version

Exit codes:
  0  success (no problems found)
  1  problems found (broken links, invalid evidence)
  2  usage / I/O error
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from efc import __version__
from efc import _extract_claims as extract_claims
from efc import _check_links as check_links
from efc import _validate_evidence as ve
from efc import _verify_source as vs


# ── helpers ──────────────────────────────────────────────────────────

def _default_schema_path() -> str:
    """Find evidence.schema.json relative to this package (works installed or dev)."""
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(pkg_dir, "schemas", "evidence.schema.json")


# ── extract ──────────────────────────────────────────────────────────

def _cmd_extract(args) -> int:
    try:
        with open(args.report, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    claims = extract_claims.extract_claims(text)
    if args.json:
        print(extract_claims.to_json(claims))
    else:
        print(extract_claims.to_markdown(claims))
    return 0


# ── links ────────────────────────────────────────────────────────────

def _cmd_links(args) -> int:
    try:
        with open(args.report, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    urls = check_links.extract_urls(text)
    if not urls:
        print("No URLs found.")
        return 0

    if args.no_network:
        for url in urls:
            print(url)
        return 0

    broken = 0
    for url in urls:
        status, cat, note = check_links.check_url(url, timeout=args.timeout)
        if cat not in check_links.RESOLVES:
            broken += 1
        code = str(status) if status is not None else "ERR"
        extra = f"  ({note})" if note else ""
        print(f"[{cat:<12}] {code:>3} {url}{extra}")

    print(f"\n{len(urls)} links, {broken} broken.")
    if args.max_broken is not None and broken <= args.max_broken:
        return 0
    return 1 if broken else 0


# ── evidence ─────────────────────────────────────────────────────────

def _cmd_evidence(args) -> int:
    schema_path = args.schema or _default_schema_path()
    try:
        schema = ve.load_schema(schema_path)
        with open(args.evidence, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    errors = ve.validate_evidence(data, schema)
    n = len(data) if isinstance(data, list) else 1
    if errors:
        for err in errors:
            print(f"INVALID: {err}")
        print(f"\n{len(errors)} problem(s) across {n} record(s).")
        return 1

    if args.json:
        print(json.dumps({"valid": True, "record_count": n}, indent=2))
    else:
        print(f"OK: {n} record(s) valid.")
    return 0


# ── audit ────────────────────────────────────────────────────────────

def _cmd_audit(args) -> int:
    exit_code = 0

    try:
        with open(args.report, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report_name = os.path.basename(args.report)

    # Step 1: Extract claims
    claims = extract_claims.extract_claims(text)
    n_claims = len(claims)
    p0 = sum(1 for c in claims if c.priority == "P0")
    p1 = sum(1 for c in claims if c.priority == "P1")

    # Step 2: Check links
    urls = check_links.extract_urls(text)
    broken_urls = []
    ok_urls = 0
    unchecked_urls = 0
    if urls and not args.no_network:
        for url in urls:
            status, cat, note = check_links.check_url(url, timeout=args.timeout)
            if cat not in check_links.RESOLVES:
                broken_urls.append((url, status, cat))
            else:
                ok_urls += 1
    elif urls:
        unchecked_urls = len(urls)

    # Broken links are a failure in any output mode (so --json works in CI too).
    if broken_urls:
        exit_code = 1

    # JSON mode: pure JSON output
    if args.json:
        result = {
            "report": report_name,
            "claims": {"total": n_claims, "p0": p0, "p1": p1},
            "links": {
                "total": len(urls),
                "ok": ok_urls,
                "broken": len(broken_urls),
                "unchecked": unchecked_urls,
                "broken_details": [
                    {"url": u, "status": s, "category": c}
                    for u, s, c in broken_urls
                ],
            },
        }
        print(json.dumps(result, indent=2))
        return exit_code

    # Human-readable mode
    print(f"## Audit: {report_name}")
    print(f"Claims found:   {n_claims} (P0: {p0}, P1: {p1})")
    if args.no_network and urls:
        print(f"Source URLs:    {unchecked_urls} unchecked (--no-network)")
    else:
        print(f"Source URLs:    {ok_urls} ok, {len(broken_urls)} broken")
    if broken_urls:
        for url, status, cat in broken_urls:
            code = str(status) if status is not None else "ERR"
            print(f"  ❌ [{cat}] {code} {url}")

    print(f"\nReliability: {'Low' if broken_urls or p0 > 0 else 'Medium' if p1 > 0 else 'High'}")

    return exit_code


# ── verify ────────────────────────────────────────────────────────────

def _cmd_verify(args) -> int:
    try:
        with open(args.evidence, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    results = vs.verify_evidence_records(
        data, timeout=args.timeout, claim_filter=args.claim
    )
    print(vs._format_results(results, use_json=args.json))

    bad = any(r["verification"]["verdict"] in ("not_found", "fetch_failed") for r in results)
    return 1 if bad else 0


# ── version ──────────────────────────────────────────────────────────

def _cmd_version(_args) -> int:
    print(f"efc {__version__}")
    return 0


# ── main ─────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="efc",
        description="Fact-check AI-generated research reports",
    )
    parser.add_argument("--version", action="version", version=f"efc {__version__}")
    sub = parser.add_subparsers(dest="command")

    # extract
    p_extract = sub.add_parser("extract", help="Inventory verifiable claims from a report")
    p_extract.add_argument("report", help="Path to the report file")
    p_extract.add_argument("--json", action="store_true", help="Output as JSON")

    # links
    p_links = sub.add_parser("links", help="Check that source URLs resolve")
    p_links.add_argument("report", help="Path to the report file")
    p_links.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout (s)")
    p_links.add_argument("--no-network", action="store_true", help="List URLs only")
    p_links.add_argument("--max-broken", type=int, default=None, help="Exit 0 if broken links <= N")

    # evidence
    p_evidence = sub.add_parser("evidence", help="Validate evidence records")
    p_evidence.add_argument("evidence", help="Path to evidence JSON")
    p_evidence.add_argument("--schema", default=None, help="Path to schema file")
    p_evidence.add_argument("--json", action="store_true", help="Machine-readable output")

    # audit
    p_audit = sub.add_parser("audit", help="Full audit: claims + links + summary")
    p_audit.add_argument("report", help="Path to the report file")
    p_audit.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout (s)")
    p_audit.add_argument("--no-network", action="store_true", help="Skip live link checking")
    p_audit.add_argument("--json", action="store_true", help="Machine-readable output")

    # verify
    p_verify = sub.add_parser("verify", help="Verify source content matches claims")
    p_verify.add_argument("evidence", help="Path to evidence JSON")
    p_verify.add_argument("--claim", default=None, help="Verify only this claim_id")
    p_verify.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout (s)")
    p_verify.add_argument("--json", action="store_true", help="Machine-readable output")

    # version
    sub.add_parser("version", help="Show version")

    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 2

    dispatch = {
        "extract": _cmd_extract,
        "links": _cmd_links,
        "evidence": _cmd_evidence,
        "audit": _cmd_audit,
        "verify": _cmd_verify,
        "version": _cmd_version,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
