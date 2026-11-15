import unittest

from graph.evidence import validate_evidence_record
from graph.evidence import build_funding_evidence_record


class TestEvidenceValidation(unittest.TestCase):

    def setUp(self):
        # Synthetic example for testing only.
        self.record = {
            "claim": "A methodology section is required",
            "source_type": "funding_guideline",
            "source_title": "Example guideline for testing",
            "source_reference": "example_guideline.pdf",
            "source_locator": "Page 2, Section 3",
            "excerpt": "The proposal must include methodology.",
            "verified": True,
            "in_scope": True,
        }

    def test_valid_evidence_is_accepted(self):
        accepted, issues = validate_evidence_record(
            self.record
        )

        self.assertTrue(accepted)
        self.assertEqual(issues, [])

    def test_missing_excerpt_is_rejected(self):
        self.record["excerpt"] = ""

        accepted, issues = validate_evidence_record(
            self.record
        )

        self.assertFalse(accepted)
        self.assertTrue(issues)

    def test_unverified_source_is_rejected(self):
        self.record["verified"] = False

        accepted, issues = validate_evidence_record(
            self.record
        )

        self.assertFalse(accepted)
        self.assertTrue(issues)

    def test_irrelevant_evidence_is_rejected(self):
        self.record["in_scope"] = False

        accepted, issues = validate_evidence_record(
            self.record
        )

        self.assertFalse(accepted)
        self.assertTrue(issues)


    def test_unverified_funding_call_is_rejected(self):
        call = {
            "agency": "SERB",
            "call_title": "Example Healthcare AI Call",
            "source": {
                "source_type": "unverified_demo_record",
                "source_title": "",
                "source_url": "",
                "source_locator": "",
                "supporting_excerpt": "",
                "retrieved_at": "",
                "verified": False,
            },
        }
        record = build_funding_evidence_record(
            call,
            in_scope=True,
        )
        accepted, issues = validate_evidence_record(record)
        self.assertFalse(accepted)
        self.assertTrue(issues)

    def test_funding_source_fields_are_mapped(self):
        call = {
            "call_title": "Example Call",
            "source": {
                "source_type": "funding_guideline",
                "source_title": "Example Guideline",
                "source_url": "https://example.org/guideline",
                "source_locator": "Section 2",
                "supporting_excerpt": "Example supporting text",
                "verified": True,
            },
        }
        record = build_funding_evidence_record(
            call,
            in_scope=True,
        )
        self.assertEqual(
            record["source_reference"],
            "https://example.org/guideline",
        )
        self.assertEqual(
            record["excerpt"],
            "Example supporting text",
        )


if __name__ == "__main__":
    unittest.main()