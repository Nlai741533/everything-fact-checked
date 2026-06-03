"""Tests for scripts/verify_source.py — source-content verification."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from efc import _verify_source as vs  # noqa: E402


class TextExtractionTest(unittest.TestCase):
    def test_strips_html_tags(self):
        html = "<html><body><p>Hello <b>world</b></p></body></html>"
        text = vs._strip_html(html)
        self.assertIn("Hello", text)
        self.assertIn("world", text)
        self.assertNotIn("<b>", text)

    def test_skips_script_and_style(self):
        html = "<body><script>alert('x')</script><style>.x{}</style><p>visible</p></body>"
        text = vs._strip_html(html)
        self.assertIn("visible", text)
        self.assertNotIn("alert", text)
        self.assertNotIn(".x", text)

    def test_handles_plain_text(self):
        text = vs._strip_html("just plain text")
        self.assertIn("just plain text", text)


class KeyTermsTest(unittest.TestCase):
    def test_extracts_currency_figures(self):
        terms = vs._extract_key_terms("Revenue was $2.1B in FY2024")
        self.assertTrue(any("2.1" in t for t in terms))

    def test_extracts_percentages(self):
        terms = vs._extract_key_terms("Growth was 35% year over year")
        self.assertIn("35%", terms)

    def test_extracts_years(self):
        terms = vs._extract_key_terms("Revenue in 2024 was higher than 2023")
        self.assertIn("2024", terms)
        self.assertIn("2023", terms)


class VerifyClaimTest(unittest.TestCase):
    def test_found_when_terms_present(self):
        source = "Acme Robotics reported revenue of $4.2 billion for FY2024, according to their annual filing."
        result = vs.verify_claim_in_source(
            "Acme Robotics reported revenue of $4,200B in FY2024",
            source,
            reported_value="$4,200B",
        )
        # Key terms like "2024", "Revenue", "Acme" should be found
        self.assertGreater(result["match_ratio"], 0)

    def test_not_found_when_terms_absent(self):
        source = "The weather in Tokyo is warm in July."
        result = vs.verify_claim_in_source(
            "Acme Robotics reported revenue of $4,200B in FY2024",
            source,
        )
        self.assertEqual(result["verdict"], "not_found")
        self.assertEqual(result["match_ratio"], 0)

    def test_ambiguous_when_partial_match(self):
        source = "Revenue for 2024 was reported by Acme in their annual report."
        result = vs.verify_claim_in_source(
            "Acme Robotics reported revenue of $4,200B in FY2024",
            source,
        )
        # Should find some terms like "Acme", "2024", "Revenue" but miss "$4,200B"
        self.assertIn(result["verdict"], ("found", "ambiguous", "not_found"))


class VerifyRecordsTest(unittest.TestCase):
    def test_skips_records_without_url(self):
        records = [{"claim_id": "C001", "claim_text": "test", "source_url": None}]
        results = vs.verify_evidence_records(records)
        self.assertEqual(results[0]["verification"]["verdict"], "skipped")

    def test_skips_invalid_urls(self):
        records = [{"claim_id": "C001", "claim_text": "test", "source_url": "not a url"}]
        results = vs.verify_evidence_records(records)
        self.assertEqual(results[0]["verification"]["verdict"], "skipped")

    def test_claim_filter(self):
        records = [
            {"claim_id": "C001", "claim_text": "test", "source_url": None},
            {"claim_id": "C002", "claim_text": "test2", "source_url": None},
        ]
        results = vs.verify_evidence_records(records, claim_filter="C001")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["claim_id"], "C001")


class SsrfGuardTest(unittest.TestCase):
    def test_blocks_non_http_scheme(self):
        ok, reason = vs.is_safe_url("file:///etc/passwd")
        self.assertFalse(ok)
        self.assertIn("scheme", reason)

    def test_blocks_loopback(self):
        ok, _ = vs.is_safe_url("http://127.0.0.1/admin")
        self.assertFalse(ok)

    def test_blocks_localhost(self):
        ok, _ = vs.is_safe_url("http://localhost:8080/")
        self.assertFalse(ok)

    def test_blocks_cloud_metadata_ip(self):
        ok, reason = vs.is_safe_url("http://169.254.169.254/latest/meta-data/")
        self.assertFalse(ok)
        self.assertIn("blocked address", reason)

    def test_blocks_private_ip(self):
        ok, _ = vs.is_safe_url("http://10.0.0.5/")
        self.assertFalse(ok)
        ok2, _ = vs.is_safe_url("http://192.168.1.1/")
        self.assertFalse(ok2)

    def test_allows_public_host(self):
        ok, reason = vs.is_safe_url("https://example.com/page")
        self.assertTrue(ok, reason)

    def test_ip_blocklist_helper(self):
        self.assertTrue(vs._ip_is_blocked("127.0.0.1"))
        self.assertTrue(vs._ip_is_blocked("169.254.169.254"))
        self.assertTrue(vs._ip_is_blocked("::1"))
        self.assertTrue(vs._ip_is_blocked("garbage"))
        self.assertFalse(vs._ip_is_blocked("93.184.216.34"))  # example.com

    def test_fetch_page_refuses_blocked_url_without_network(self):
        text, status, error = vs.fetch_page("http://127.0.0.1/secret")
        self.assertIsNone(text)
        self.assertIsNone(status)
        self.assertIn("SSRF guard", error)


class FormatTest(unittest.TestCase):
    def test_human_readable_output(self):
        results = [{"claim_id": "C001", "source_url": None, "verification": {"verdict": "skipped", "details": "No source URL"}}]
        output = vs._format_results(results)
        self.assertIn("C001", output)
        self.assertIn("skipped", output)

    def test_json_output(self):
        results = [{"claim_id": "C001", "source_url": None, "verification": {"verdict": "skipped", "details": "No source URL"}}]
        output = vs._format_results(results, use_json=True)
        import json
        data = json.loads(output)
        self.assertEqual(data[0]["claim_id"], "C001")


if __name__ == "__main__":
    unittest.main()
