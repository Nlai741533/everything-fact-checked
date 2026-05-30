#!/usr/bin/env python3
"""Check that every source URL in a report actually resolves.

Dead and redirected source links are a common symptom of fabricated or
laundered citations. This script extracts URLs and reports their HTTP status.

It does NOT confirm the linked page contains the attributed claim — that is a
reading task for the agent/human. It only catches the cheap, mechanical failure:
the link is broken, blocked, or redirects elsewhere.

URL extraction is a pure, offline-testable function. Only `check_url` and the
CLI touch the network.

Usage:
  python3 check_links.py REPORT.md                 # check all links
  python3 check_links.py REPORT.md --timeout 5     # per-request timeout (s)
  python3 check_links.py --no-network REPORT.md    # list URLs only, no requests
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request

# Markdown links [text](url) and bare http(s) URLs.
MD_LINK_RE = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")
BARE_URL_RE = re.compile(r"(?<![(\[])\bhttps?://[^\s)<>\]]+")
_TRAILING = ".,;:!?”\"'"


def extract_urls(text: str) -> list[str]:
    """Return unique URLs in document order. Pure function — no network."""
    seen: dict[str, None] = {}
    for m in MD_LINK_RE.finditer(text):
        seen.setdefault(m.group(1).rstrip(_TRAILING), None)
    for m in BARE_URL_RE.finditer(text):
        seen.setdefault(m.group(0).rstrip(_TRAILING), None)
    return list(seen)


def check_url(url: str, timeout: float = 10.0) -> tuple[int | None, str]:
    """Return (status_code, note). status_code is None on connection failure."""
    req = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "fact-check-linkcheck/0.1 (+https://github.com/Nlai741533/everything-fact-checked)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            final = resp.geturl()
            note = "ok" if final.rstrip("/") == url.rstrip("/") else f"redirected -> {final}"
            return resp.status, note
    except urllib.error.HTTPError as exc:
        # Some servers reject HEAD; a 405/403 still means the host resolves.
        return exc.code, "HTTP error"
    except (urllib.error.URLError, ValueError, OSError) as exc:
        return None, f"unreachable: {exc}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", help="Path to the report file")
    parser.add_argument("--timeout", type=float, default=10.0, help="Per-request timeout in seconds")
    parser.add_argument("--no-network", action="store_true", help="List URLs only; make no requests")
    args = parser.parse_args(argv)

    try:
        with open(args.report, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        print(f"error: cannot read {args.report}: {exc}", file=sys.stderr)
        return 2

    urls = extract_urls(text)
    if not urls:
        print("No URLs found.")
        return 0

    if args.no_network:
        for url in urls:
            print(url)
        return 0

    failures = 0
    for url in urls:
        status, note = check_url(url, timeout=args.timeout)
        ok = status is not None and status < 400
        if not ok:
            failures += 1
        mark = "OK " if ok else "BAD"
        code = str(status) if status is not None else "ERR"
        print(f"[{mark}] {code} {url}  ({note})")

    print(f"\n{len(urls)} links, {failures} broken/unreachable.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
