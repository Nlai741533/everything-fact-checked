#!/usr/bin/env python3
"""Verify that a cited source actually contains the attributed claim.

This is the most important Phase 2 feature. It goes beyond link-checking (does
the URL resolve?) to answer: does the linked page actually contain the number,
phrase, or fact that was attributed to it?

How it works:
  1. Read an evidence record (or a report + extracted claims)
  2. For each claim with a source_url, fetch the page
  3. Extract visible text (strip HTML tags)
  4. Search for the claimed value / key terms near the claim context
  5. Report: found / not_found / ambiguous

This does NOT prove the claim is correct — it proves the source contains the
attributed information. That is a necessary but not sufficient condition.

Stdlib only (urllib for fetching, html.parser for text extraction).

Usage:
  python3 verify_source.py evidence.json                    # verify all evidence records
  python3 verify_source.py --claim C001 evidence.json       # verify one claim
  python3 verify_source.py --timeout 10 evidence.json
  python3 verify_source.py --json evidence.json
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
import socket
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urlparse

_USER_AGENT = "fact-check-source-verify/0.1 (+https://github.com/Nlai741533/EFC-Plugin)"

# SSRF guard: `verify` fetches URLs that may come from untrusted reports/PRs.
# Refuse non-web schemes and any host that resolves to a private, loopback,
# link-local (incl. cloud metadata 169.254.169.254), or otherwise reserved IP.
_ALLOWED_SCHEMES = ("http", "https")


def _ip_is_blocked(ip_str: str) -> bool:
    """True if an IP is loopback/private/link-local/reserved (not publicly routable)."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True  # unparseable -> refuse
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def is_safe_url(url: str) -> tuple[bool, str]:
    """Return (ok, reason). Refuses non-http(s) schemes and hosts that resolve
    to non-public IPs. Pure-ish: performs DNS resolution but no HTTP request."""
    parsed = urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        return False, f"scheme '{parsed.scheme}' not allowed (http/https only)"
    host = parsed.hostname
    if not host:
        return False, "missing host"
    # A literal IP in the URL bypasses DNS; check it directly too.
    try:
        infos = socket.getaddrinfo(host, parsed.port or None, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        return False, f"DNS resolution failed: {exc}"
    for info in infos:
        ip_str = info[4][0]
        if _ip_is_blocked(ip_str):
            return False, f"host resolves to blocked address {ip_str}"
    return True, "ok"


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Re-validate each redirect target so a public URL can't bounce to an
    internal one."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        ok, reason = is_safe_url(newurl)
        if not ok:
            raise urllib.error.URLError(f"blocked redirect to {newurl}: {reason}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class _TextExtractor(HTMLParser):
    """Strip HTML tags, return visible text."""

    _SKIP_TAGS = frozenset(("script", "style", "noscript", "head", "meta", "link"))

    def __init__(self):
        super().__init__()
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag in self._SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            self._parts.append(data)

    def get_text(self) -> str:
        return " ".join(self._parts)


def _strip_html(html: str) -> str:
    """Extract visible text from HTML."""
    extractor = _TextExtractor()
    try:
        extractor.feed(html)
    except Exception:
        # If HTML parsing fails, return raw text (may be non-HTML)
        return html
    return extractor.get_text()


def fetch_page(url: str, timeout: float = 10.0) -> tuple:
    """Fetch a URL and return (text, status, error).

    Returns (visible_text, http_status, error_message).
    text is None if fetch failed.
    """
    ok, reason = is_safe_url(url)
    if not ok:
        return None, None, f"blocked by SSRF guard: {reason}"

    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    opener = urllib.request.build_opener(_SafeRedirectHandler)
    try:
        with opener.open(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            text = _strip_html(raw)
            return text, resp.status, None
    except urllib.error.HTTPError as exc:
        return None, exc.code, str(exc)
    except Exception as exc:
        return None, None, str(exc)


def _extract_key_terms(text: str) -> list:
    """Extract key searchable terms from a claim text.

    Returns a list of terms that are likely to appear in the source if
    the claim is accurately cited.
    """
    # Extract numbers (with optional scale words)
    terms = []

    # Numbers with currency/scale
    for m in re.finditer(
        r"([$¥€£]?\s?\d[\d,]*(?:\.\d+)?\s?(?:billion|million|trillion|thousand|bn|%)?)",
        text, re.IGNORECASE
    ):
        terms.append(m.group(1).strip())

    # Percentages
    for m in re.finditer(r"\d+(?:\.\d+)?\s?%", text):
        terms.append(m.group(0))

    # Years
    for m in re.finditer(r"\b(?:19|20)\d{2}\b", text):
        terms.append(m.group(0))

    # Named entities: capitalized words of 3+ chars (crude but useful)
    for m in re.finditer(r"\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*\b", text):
        word = m.group(0)
        # Skip common non-entity words
        if word.lower() not in {"the", "and", "for", "was", "has", "had", "its", "but", "not", "are", "been", "they", "this", "that", "with", "from", "into", "also", "over", "only"}:
            terms.append(word)

    return terms


def verify_claim_in_source(claim_text: str, source_text: str, reported_value: str = None) -> dict:
    """Check whether source_text supports the claim.

    Returns a dict with:
      found_terms: list of terms from the claim found in the source
      missing_terms: list of terms NOT found
      match_ratio: fraction of key terms found
      verdict: "found" | "not_found" | "ambiguous"
      details: human-readable explanation
    """
    source_lower = source_text.lower()
    key_terms = _extract_key_terms(claim_text)

    # Also search for the reported value specifically
    if reported_value:
        key_terms.append(str(reported_value))

    found = []
    missing = []
    for term in key_terms:
        if term.lower() in source_lower:
            found.append(term)
        else:
            missing.append(term)

    ratio = len(found) / len(key_terms) if key_terms else 0

    if ratio >= 0.6 and len(found) >= 2:
        verdict = "found"
    elif ratio >= 0.3:
        verdict = "ambiguous"
    else:
        verdict = "not_found"

    return {
        "found_terms": found,
        "missing_terms": missing,
        "match_ratio": round(ratio, 2),
        "verdict": verdict,
        "details": _explain(verdict, found, missing, claim_text),
    }


def _explain(verdict: str, found: list, missing: list, claim: str) -> str:
    if verdict == "found":
        return f"Source contains {len(found)} key terms from claim: {', '.join(found[:5])}"
    if verdict == "ambiguous":
        return f"Partial match ({len(found)}/{len(found)+len(missing)} terms). Found: {', '.join(found[:5])}. Missing: {', '.join(missing[:5])}"
    return f"Source does not contain key terms from claim. Missing: {', '.join(missing[:5])}"


def verify_evidence_records(data, timeout: float = 10.0, claim_filter: str = None) -> list:
    """Verify all evidence records that have a source_url.

    Returns a list of result dicts.
    """
    records = data if isinstance(data, list) else [data]
    results = []

    for rec in records:
        cid = rec.get("claim_id", "???")
        if claim_filter and cid != claim_filter:
            continue

        url = rec.get("source_url")
        claim_text = rec.get("claim_text", "")
        reported = rec.get("reported_value")

        if not url:
            results.append({
                "claim_id": cid,
                "source_url": None,
                "fetch_status": None,
                "fetch_error": "no source_url",
                "verification": {"verdict": "skipped", "details": "No source URL to verify"},
            })
            continue

        # Check URL format first
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            results.append({
                "claim_id": cid,
                "source_url": url,
                "fetch_status": None,
                "fetch_error": "invalid URL format",
                "verification": {"verdict": "skipped", "details": f"URL is not a valid http/https URL: {url}"},
            })
            continue

        # Fetch page
        text, status, error = fetch_page(url, timeout=timeout)
        if text is None:
            results.append({
                "claim_id": cid,
                "source_url": url,
                "fetch_status": status,
                "fetch_error": error,
                "verification": {"verdict": "fetch_failed", "details": f"Could not fetch source: {error}"},
            })
            continue

        # Verify content
        verification = verify_claim_in_source(claim_text, text, reported)
        results.append({
            "claim_id": cid,
            "source_url": url,
            "fetch_status": status,
            "fetch_error": None,
            "source_text_length": len(text),
            "verification": verification,
        })

    return results


def _format_results(results: list, use_json: bool = False) -> str:
    if use_json:
        return json.dumps(results, ensure_ascii=False, indent=2)

    lines = []
    for r in results:
        cid = r["claim_id"]
        url = r.get("source_url", "N/A")
        v = r["verification"]

        icon = {"found": "✅", "not_found": "❌", "ambiguous": "⚠️", "skipped": "⏭️", "fetch_failed": "🔌"}.get(v["verdict"], "?")
        lines.append(f"{icon} {cid}: {v['verdict']}")
        if url:
            lines.append(f"   Source: {url}")
        if r.get("fetch_error"):
            lines.append(f"   Error: {r['fetch_error']}")
        lines.append(f"   {v['details']}")
        lines.append("")

    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", help="Path to evidence JSON (array or single record)")
    parser.add_argument("--claim", default=None, help="Verify only this claim_id (e.g. C001)")
    parser.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout (s)")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args(argv)

    try:
        with open(args.evidence, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    results = verify_evidence_records(data, timeout=args.timeout, claim_filter=args.claim)
    print(_format_results(results, use_json=args.json))

    # Exit 1 if any verification failed
    bad = any(r["verification"]["verdict"] in ("not_found", "fetch_failed") for r in results)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
