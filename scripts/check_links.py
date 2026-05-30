#!/usr/bin/env python3
"""Check that every source URL in a report actually resolves.

Dead and redirected source links are a common symptom of fabricated or laundered
citations. This script extracts URLs and classifies their reachability. It does
NOT confirm the linked page contains the attributed claim - that is a reading
task for the agent/human.

Categories:
  ok           2xx, same URL
  redirect     2xx after a redirect to a different URL
  blocked      401/403/405/406/429 - host resolves but refuses bots (NOT a dead link)
  not_found    404/410
  server_error 5xx
  client_error other 4xx
  ssl_error    TLS/certificate failure
  unreachable  DNS / connection / timeout failure

"blocked" counts as resolving (the source exists); the rest of the non-ok
categories count as broken. HEAD is tried first, with a GET fallback for servers
that reject HEAD.

URL extraction is pure and offline-testable; only `check_url` touches the network.

Usage:
  python3 check_links.py REPORT.md                 # check all links
  python3 check_links.py REPORT.md --timeout 5     # per-request timeout (s)
  python3 check_links.py --no-network REPORT.md    # list URLs only
"""
from __future__ import annotations

import argparse
import re
import ssl
import sys
import urllib.error
import urllib.request

# URLs may contain one level of balanced parentheses (e.g. Wikipedia article URLs).
_URL_CORE = r"https?://(?:[^()\s<>\]]|\([^()\s]*\))+"
# Markdown links: [text](url), [text](<url>), [text](url "title").
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(\s*<?(" + _URL_CORE + r")>?(?:\s+\"[^\"]*\")?\s*\)")
BARE_URL_RE = re.compile(r"(?<![(\[\"])\b(" + _URL_CORE + r")")
_TRAILING = ".,;:!?”\"'>"

RESOLVES = {"ok", "redirect", "blocked"}
_USER_AGENT = "fact-check-linkcheck/0.2 (+https://github.com/Nlai741533/everything-fact-checked)"


def extract_urls(text: str) -> list:
    """Return unique URLs in document order. Pure function - no network."""
    seen = {}
    for m in MD_LINK_RE.finditer(text):
        seen.setdefault(m.group(1).rstrip(_TRAILING), None)
    for m in BARE_URL_RE.finditer(text):
        seen.setdefault(m.group(1).rstrip(_TRAILING), None)
    return list(seen)


def category_for_status(code) -> str:
    """Map an HTTP status code to a category. Pure function."""
    if code is None:
        return "unreachable"
    if 200 <= code < 300:
        return "ok"
    if code in (301, 302, 303, 307, 308):
        return "redirect"
    if code in (401, 403, 405, 406, 429):
        return "blocked"
    if code in (404, 410):
        return "not_found"
    if 500 <= code < 600:
        return "server_error"
    return "client_error"


def _categorize(status, final_url, requested):
    cat = category_for_status(status)
    note = ""
    if cat == "ok" and final_url.rstrip("/") != requested.rstrip("/"):
        cat, note = "redirect", f"-> {final_url}"
    return status, cat, note


def check_url(url: str, timeout: float = 10.0):
    """Return (status_code, category, note). Tries HEAD, falls back to GET."""
    last = (None, "unreachable", "no response")
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": _USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return _categorize(resp.status, resp.geturl(), url)
        except urllib.error.HTTPError as exc:
            cat = category_for_status(exc.code)
            if method == "HEAD" and exc.code in (403, 405, 406, 429, 501):
                last = (exc.code, cat, "HEAD rejected; retrying GET")
                continue
            return exc.code, cat, "HTTP error"
        except (urllib.error.URLError, OSError, ValueError) as exc:
            reason = getattr(exc, "reason", exc)
            if isinstance(reason, ssl.SSLError) or isinstance(exc, ssl.SSLError):
                return None, "ssl_error", str(reason)
            last = (None, "unreachable", str(reason))
            if method == "HEAD":
                continue
            return last
    return last


def main(argv=None) -> int:
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

    broken = 0
    for url in urls:
        status, cat, note = check_url(url, timeout=args.timeout)
        if cat not in RESOLVES:
            broken += 1
        code = str(status) if status is not None else "ERR"
        extra = f"  ({note})" if note else ""
        print(f"[{cat:<12}] {code:>3} {url}{extra}")

    print(f"\n{len(urls)} links, {broken} broken (categories outside {sorted(RESOLVES)}).")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
