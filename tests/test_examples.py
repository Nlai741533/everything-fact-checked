"""Golden tests: pin the behavior of the scripts against the shipped examples."""
import collections
import json
import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from efc import _extract_claims as ec  # noqa: E402
from efc import _check_links as cl  # noqa: E402
from efc import _validate_evidence as ve  # noqa: E402

SAMPLE = os.path.join(ROOT, "examples", "sample-report.md")
EVIDENCE = os.path.join(ROOT, "examples", "evidence-sample.json")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class SampleReportGoldenTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.claims = ec.extract_claims(_read(SAMPLE))
        cls.counts = collections.Counter(c.type for c in cls.claims)

    def test_claim_type_counts(self):
        self.assertEqual(self.counts["figure"], 8)
        self.assertEqual(self.counts["percentage"], 1)
        self.assertEqual(self.counts["superlative"], 1)
        self.assertEqual(self.counts["date"], 8)

    def test_total_claims(self):
        self.assertEqual(len(self.claims), 18)

    def test_finds_the_inflated_revenue_figure(self):
        self.assertTrue(any("$4,200B" in c.snippet for c in self.claims))

    def test_finds_first_superlative(self):
        sups = [c for c in self.claims if c.type == "superlative"]
        self.assertEqual(len(sups), 1)
        self.assertIn("first", sups[0].snippet.lower())

    def test_headings_excluded(self):
        for c in self.claims:
            self.assertFalse(c.snippet.strip().startswith("#"))


class SampleLinksGoldenTest(unittest.TestCase):
    def test_three_source_urls(self):
        urls = cl.extract_urls(_read(SAMPLE))
        self.assertEqual(len(urls), 3)

    def test_query_string_url_intact(self):
        urls = cl.extract_urls(_read(SAMPLE))
        self.assertTrue(any("browse-edgar?action=getcompany" in u for u in urls))


class EvidenceSampleGoldenTest(unittest.TestCase):
    def test_sample_evidence_is_valid(self):
        schema = ve.load_schema()
        with open(EVIDENCE, encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertEqual(ve.validate_evidence(data, schema), [])

    def test_sample_evidence_covers_three_verdicts(self):
        with open(EVIDENCE, encoding="utf-8") as fh:
            data = json.load(fh)
        verdicts = {r["verdict"] for r in data}
        self.assertEqual(verdicts, {"verified", "error", "unverifiable"})


if __name__ == "__main__":
    unittest.main()
