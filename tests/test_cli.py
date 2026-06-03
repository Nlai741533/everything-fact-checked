"""Tests for the efc CLI."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from efc.cli import main as cli_main  # noqa: E402

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")
SAMPLE_REPORT = os.path.join(EXAMPLES, "sample-report.md")
EVIDENCE_SAMPLE = os.path.join(EXAMPLES, "evidence-sample.json")


class VersionTest(unittest.TestCase):
    def test_version_output(self):
        # Capture stdout
        import io
        old = sys.stdout
        sys.stdout = buf = io.StringIO()
        try:
            rc = cli_main(["version"])
        finally:
            sys.stdout = old
        self.assertEqual(rc, 0)
        self.assertIn("0.2.4", buf.getvalue())


class ExtractTest(unittest.TestCase):
    def test_extract_returns_zero(self):
        rc = cli_main(["extract", SAMPLE_REPORT])
        self.assertEqual(rc, 0)

    def test_extract_json_is_valid(self):
        import io
        old = sys.stdout
        sys.stdout = buf = io.StringIO()
        try:
            cli_main(["extract", "--json", SAMPLE_REPORT])
        finally:
            sys.stdout = old
        data = json.loads(buf.getvalue())
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        self.assertIn("claim_id", data[0])


class LinksTest(unittest.TestCase):
    def test_links_no_network(self):
        rc = cli_main(["links", "--no-network", SAMPLE_REPORT])
        self.assertEqual(rc, 0)


class EvidenceTest(unittest.TestCase):
    def test_evidence_valid(self):
        import io
        old = sys.stdout
        sys.stdout = buf = io.StringIO()
        try:
            rc = cli_main(["evidence", EVIDENCE_SAMPLE])
        finally:
            sys.stdout = old
        self.assertEqual(rc, 0)
        self.assertIn("OK", buf.getvalue())

    def test_evidence_json_output(self):
        import io
        old = sys.stdout
        sys.stdout = buf = io.StringIO()
        try:
            rc = cli_main(["evidence", "--json", EVIDENCE_SAMPLE])
        finally:
            sys.stdout = old
        self.assertEqual(rc, 0)
        data = json.loads(buf.getvalue())
        self.assertTrue(data["valid"])


class AuditTest(unittest.TestCase):
    def test_audit_no_network(self):
        rc = cli_main(["audit", "--no-network", SAMPLE_REPORT])
        self.assertEqual(rc, 0)

    def test_audit_json_output(self):
        import io
        old = sys.stdout
        sys.stdout = buf = io.StringIO()
        try:
            rc = cli_main(["audit", "--no-network", "--json", SAMPLE_REPORT])
        finally:
            sys.stdout = old
        self.assertEqual(rc, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(data["claims"]["total"], 18)
        self.assertTrue(data["links"]["unchecked"] > 0)

    def test_audit_exit_code_parity_on_broken_links(self):
        """Human and --json modes must return the SAME exit code (regression:
        --json used to return 0 while human mode returned 1 on broken links)."""
        import io
        from efc import _check_links as cl

        original = cl.check_url
        cl.check_url = lambda url, timeout=10.0: (404, "not_found", "stubbed")
        try:
            for extra in ([], ["--json"]):
                sys.stdout, old = io.StringIO(), sys.stdout
                try:
                    rc = cli_main(["audit", *extra, SAMPLE_REPORT])
                finally:
                    sys.stdout = old
                self.assertEqual(rc, 1, f"audit {extra} should exit 1 on broken links")
        finally:
            cl.check_url = original


class NoCommandTest(unittest.TestCase):
    def test_no_command_returns_2(self):
        rc = cli_main([])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
