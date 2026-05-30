"""Tests for scripts/check_links.py URL extraction and categorization (offline)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import check_links as cl  # noqa: E402

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "mini-report.md")


def _load():
    with open(FIXTURE, encoding="utf-8") as fh:
        return fh.read()


class ExtractUrlsTest(unittest.TestCase):
    def setUp(self):
        self.urls = cl.extract_urls(_load())

    def test_extracts_markdown_link(self):
        self.assertIn("https://www.sec.gov/edgar", self.urls)

    def test_extracts_bare_url(self):
        self.assertIn("https://example.com/tracker", self.urls)

    def test_deduplicates(self):
        self.assertEqual(self.urls.count("https://example.com/tracker"), 1)

    def test_strips_trailing_punctuation(self):
        urls = cl.extract_urls("See https://example.org/page, and https://example.org/two.")
        self.assertIn("https://example.org/page", urls)
        self.assertIn("https://example.org/two", urls)

    def test_markdown_link_with_title(self):
        urls = cl.extract_urls('[Filing](https://example.com/p "Annual report")')
        self.assertEqual(urls, ["https://example.com/p"])

    def test_markdown_link_angle_brackets(self):
        urls = cl.extract_urls("[x](<https://example.com/a>)")
        self.assertEqual(urls, ["https://example.com/a"])

    def test_url_with_balanced_parens(self):
        urls = cl.extract_urls("[wiki](https://en.wikipedia.org/wiki/Foo_(bar))")
        self.assertIn("https://en.wikipedia.org/wiki/Foo_(bar)", urls)

    def test_no_urls(self):
        self.assertEqual(cl.extract_urls("no links here"), [])

    def test_preserves_order(self):
        text = "https://a.example https://b.example https://a.example"
        self.assertEqual(cl.extract_urls(text), ["https://a.example", "https://b.example"])


class CategoryTest(unittest.TestCase):
    def test_status_mapping(self):
        cases = {
            200: "ok",
            204: "ok",
            301: "redirect",
            308: "redirect",
            403: "blocked",
            429: "blocked",
            404: "not_found",
            410: "not_found",
            500: "server_error",
            503: "server_error",
            418: "client_error",
            None: "unreachable",
        }
        for code, expected in cases.items():
            self.assertEqual(cl.category_for_status(code), expected, code)

    def test_blocked_counts_as_resolving(self):
        self.assertIn("blocked", cl.RESOLVES)
        self.assertIn("redirect", cl.RESOLVES)
        self.assertNotIn("not_found", cl.RESOLVES)
        self.assertNotIn("ssl_error", cl.RESOLVES)


if __name__ == "__main__":
    unittest.main()
