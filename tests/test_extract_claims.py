"""Tests for scripts/extract_claims.py (offline, no network)."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from efc import _extract_claims as ec  # noqa: E402

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "mini-report.md")


def _load():
    with open(FIXTURE, encoding="utf-8") as fh:
        return fh.read()


class ExtractClaimsTest(unittest.TestCase):
    def setUp(self):
        self.claims = ec.extract_claims(_load())

    def test_finds_currency_figure(self):
        snippets = " ".join(c.snippet for c in self.claims if c.type == "figure")
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
        for c in self.claims:
            if c.type == "figure":
                self.assertNotIn("page 12", c.snippet)

    def test_ids_are_unique_and_ordered(self):
        ids = [c.claim_id for c in self.claims]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, sorted(ids))

    def test_json_output_is_valid(self):
        parsed = json.loads(ec.to_json(self.claims))
        self.assertEqual(len(parsed), len(self.claims))
        self.assertIn("priority", parsed[0])

    def test_empty_input(self):
        self.assertEqual(ec.extract_claims(""), [])
        self.assertIn("No verifiable claims", ec.to_markdown([]))


class NoiseReductionTest(unittest.TestCase):
    def test_skips_fenced_code_blocks(self):
        text = "Intro.\n```\nrevenue = $9.9B billion\n```\nReal claim: $1.0B billion.\n"
        snippets = " ".join(c.snippet for c in ec.extract_claims(text))
        self.assertNotIn("$9.9B", snippets)
        self.assertIn("$1.0B", snippets)

    def test_skips_headings(self):
        text = "# Revenue $5B billion\nBody revenue was $2.0B billion.\n"
        figs = [c for c in ec.extract_claims(text) if c.type == "figure"]
        joined = " ".join(c.snippet for c in figs)
        self.assertNotIn("$5B", joined)
        self.assertIn("$2.0B", joined)

    def test_drops_bare_only(self):
        text = "This report is for demonstration only.\n"
        self.assertEqual([c for c in ec.extract_claims(text) if c.type == "superlative"], [])

    def test_keeps_the_only(self):
        text = "Acme is the only vendor with this feature.\n"
        sups = [c for c in ec.extract_claims(text) if c.type == "superlative"]
        self.assertEqual(len(sups), 1)

    def test_snippet_is_full_sentence(self):
        text = "First sentence has no claim. Acme revenue hit $3.0B billion last year.\n"
        fig = next(c for c in ec.extract_claims(text) if c.type == "figure")
        self.assertTrue(fig.snippet.startswith("Acme revenue hit"))
        self.assertNotIn("First sentence", fig.snippet)


if __name__ == "__main__":
    unittest.main()
