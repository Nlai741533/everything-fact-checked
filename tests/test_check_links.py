"""Tests for scripts/check_links.py URL extraction (offline, no network)."""
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

    def test_no_urls(self):
        self.assertEqual(cl.extract_urls("no links here"), [])

    def test_preserves_order(self):
        text = "https://a.example https://b.example https://a.example"
        self.assertEqual(cl.extract_urls(text), ["https://a.example", "https://b.example"])


if __name__ == "__main__":
    unittest.main()
