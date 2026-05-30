"""Tests for scripts/extract_claims.py (offline, no network)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import extract_claims as ec  # noqa: E402

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "mini-report.md")


def _load():
    with open(FIXTURE, encoding="utf-8") as fh:
        return fh.read()


class ExtractClaimsTest(unittest.TestCase):
    def setUp(self):
        self.claims = ec.extract_claims(_load())

    def _types(self):
        return [c.type for c in self.claims]

    def test_finds_currency_figure(self):
        figs = [c for c in self.claims if c.type == "figure"]
        snippets = " ".join(c.snippet for c in figs)
        self.assertIn("$2.1B", snippets)

    def test_finds_scaled_figure(self):
        snippets = " ".join(c.snippet for c in self.claims if c.type == "figure")
        self.assertIn("10.6 billion", snippets)

    def test_currency_figure_is_p0(self):
        fig = next(c for c in self.claims if "$2.1B" in c.snippet and c.type == "figure")
        self.assertEqual(fig.priority, "P0")

    def test_finds_percentage(self):
        pcts = [c for c in self.claims if c.type == "percentage"]
        self.assertEqual(len(pcts), 1)
        self.assertEqual(pcts[0].priority, "P1")

    def test_finds_superlative(self):
        sups = [c for c in self.claims if c.type == "superlative"]
        self.assertTrue(any("first" in c.snippet.lower() for c in sups))

    def test_finds_year_as_date(self):
        dates = [c for c in self.claims if c.type == "date"]
        self.assertTrue(any("2024" in c.snippet for c in dates))

    def test_ignores_bare_integers(self):
        # "page 12" and "section 3" must not be reported as figures.
        for c in self.claims:
            if c.type == "figure":
                self.assertNotIn("page 12", c.snippet)
                self.assertNotIn("section 3", c.snippet.lower())

    def test_ids_are_unique_and_ordered(self):
        ids = [c.claim_id for c in self.claims]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, sorted(ids))

    def test_json_output_is_valid(self):
        import json
        parsed = json.loads(ec.to_json(self.claims))
        self.assertEqual(len(parsed), len(self.claims))
        self.assertIn("priority", parsed[0])

    def test_empty_input(self):
        self.assertEqual(ec.extract_claims(""), [])
        self.assertIn("No verifiable claims", ec.to_markdown([]))


if __name__ == "__main__":
    unittest.main()
