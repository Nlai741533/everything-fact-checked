"""Tests for scripts/validate_evidence.py and the evidence schema."""
import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from efc import _validate_evidence as ve  # noqa: E402

SCHEMA = ve.load_schema()

VALID = {
    "claim_id": "C001",
    "claim_text": "Revenue was $2.1B in FY2024",
    "priority": "P0",
    "type": "financial_figure",
    "verdict": "verified",
    "source_url": "https://example.com/filing",
    "source_tier": "primary",
    "method": "Opened filing",
}


def errs(rec):
    return ve.validate_record(rec, SCHEMA)


class SchemaTest(unittest.TestCase):
    def test_valid_record_passes(self):
        self.assertEqual(errs(VALID), [])

    def test_missing_required_field(self):
        rec = copy.deepcopy(VALID)
        del rec["verdict"]
        self.assertTrue(any("verdict" in e for e in errs(rec)))

    def test_bad_enum(self):
        rec = copy.deepcopy(VALID)
        rec["priority"] = "P9"
        self.assertTrue(any("priority" in e for e in errs(rec)))

    def test_bad_claim_id_pattern(self):
        rec = copy.deepcopy(VALID)
        rec["claim_id"] = "X1"
        self.assertTrue(any("claim_id" in e for e in errs(rec)))

    def test_unexpected_field_rejected(self):
        rec = copy.deepcopy(VALID)
        rec["extra"] = "nope"
        self.assertTrue(any("unexpected" in e for e in errs(rec)))


class RuleTest(unittest.TestCase):
    def test_verified_requires_source_url(self):
        rec = copy.deepcopy(VALID)
        rec["source_url"] = None
        self.assertTrue(any("source_url" in e for e in errs(rec)))

    def test_verified_rejects_non_url_source(self):
        rec = copy.deepcopy(VALID)
        rec["source_url"] = "not a url"
        errs_list = errs(rec)
        self.assertTrue(
            any("does not look like a URL" in e for e in errs_list),
            f"Expected URL-format error, got: {errs_list}",
        )

    def test_verified_rejects_url_without_host(self):
        rec = copy.deepcopy(VALID)
        rec["source_url"] = "https:///missing-host"
        errs_list = errs(rec)
        self.assertTrue(
            any("does not look like a URL" in e for e in errs_list),
            f"Expected URL-format error for missing host, got: {errs_list}",
        )

    def test_verified_rejects_ftp_url(self):
        rec = copy.deepcopy(VALID)
        rec["source_url"] = "ftp://files.example.com/data.csv"
        errs_list = errs(rec)
        self.assertTrue(
            any("does not look like a URL" in e for e in errs_list),
            f"Expected URL-format error for ftp scheme, got: {errs_list}",
        )

    def test_verified_accepts_valid_http_url(self):
        rec = copy.deepcopy(VALID)
        rec["source_url"] = "http://sec.gov/filing"
        self.assertNotIn("does not look like a URL", " ".join(errs(rec)))

    def test_verified_accepts_valid_https_url(self):
        rec = copy.deepcopy(VALID)
        rec["source_url"] = "https://example.com/path?q=1#frag"
        self.assertEqual(errs(rec), [])

    def test_verified_p0_requires_primary_or_secondary(self):
        rec = copy.deepcopy(VALID)
        rec["source_tier"] = "tertiary"
        self.assertTrue(any("primary" in e for e in errs(rec)))

    def test_error_requires_both_values(self):
        rec = {
            "claim_id": "C002",
            "claim_text": "x",
            "priority": "P0",
            "verdict": "error",
            "reported_value": "$1B",
            "source_value": None,
        }
        self.assertTrue(any("reported_value and source_value" in e for e in errs(rec)))

    def test_unverifiable_requires_notes(self):
        rec = {
            "claim_id": "C003",
            "claim_text": "x",
            "priority": "P1",
            "verdict": "unverifiable",
        }
        self.assertTrue(any("notes" in e for e in errs(rec)))


if __name__ == "__main__":
    unittest.main()
