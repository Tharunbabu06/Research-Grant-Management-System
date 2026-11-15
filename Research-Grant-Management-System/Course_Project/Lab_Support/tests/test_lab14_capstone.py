"""Lab 14 capstone/dashboard acceptance tests."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from graph.lab14_capstone import build_dashboard_summary, run_capstone, write_dashboard_files


class FakeGraph:
    def __init__(self, state):
        self.state = state
        self.received = None

    def invoke(self, payload):
        self.received = payload
        return self.state


class TestLab14Capstone(unittest.TestCase):
    def test_blocked_realistic_run_is_not_reported_as_published(self):
        state = {
            "funding_calls": [], "literature": [{"title": "paper"}],
            "proposal": None, "budget": {"total": 0},
            "compliance": {"status": "unknown"},
            "validation_passed": False, "acceptance_passed": False,
            "acceptance_report": {"all_pass": False},
            "human_review_status": "blocked_validation_failure",
            "governance_status": "blocked_review_gate",
            "evidence_table": [
                {"status": "accepted"}, {"status": "rejected"}, {"status": "pending_review"}
            ],
        }
        summary = build_dashboard_summary(state, run_id="test-run", timestamp="2026-01-01T00:00:00+00:00")
        self.assertFalse(summary["published"])
        self.assertEqual(summary["status"], "blocked_validation_or_acceptance")
        self.assertEqual(summary["evidence"], {"accepted_count": 1, "rejected_count": 1, "pending_review_count": 1})

    def test_published_requires_all_gates_and_release_version(self):
        state = {
            "validation_passed": True,
            "acceptance_passed": True,
            "acceptance_report": {"all_pass": True},
            "governance_status": "published_approved",
            "release_version": 2,
        }
        summary = build_dashboard_summary(state)
        self.assertTrue(summary["published"])
        self.assertEqual(summary["release_version"], 2)

    def test_governance_status_alone_cannot_mark_release_published(self):
        state = {"governance_status": "published_approved", "release_version": 1}
        summary = build_dashboard_summary(state)
        self.assertFalse(summary["published"])

    def test_dashboard_files_are_written_and_escaped(self):
        summary = build_dashboard_summary(
            {"validation_passed": False, "request": {"research_area": "<script>alert(1)</script>"}},
            request={"research_area": "<script>alert(1)</script>", "funding_type": "Government"},
            run_id="html-test",
        )
        with tempfile.TemporaryDirectory() as temp:
            paths = write_dashboard_files(summary, temp)
            self.assertTrue(Path(paths["json"]).exists())
            self.assertTrue(Path(paths["html"]).exists())
            self.assertTrue(Path(paths["history"]).exists())
            content = Path(paths["html"]).read_text(encoding="utf-8")
            self.assertNotIn("<script>alert(1)</script>", content)
            self.assertIn("&lt;script&gt;", content)
            reloaded = json.loads(Path(paths["json"]).read_text(encoding="utf-8"))
            self.assertEqual(reloaded["run_id"], "html-test")

    def test_runner_passes_request_to_graph_and_saves_dashboard(self):
        fake = FakeGraph({
            "funding_calls": [], "literature": [], "proposal": None,
            "validation_passed": False, "acceptance_passed": False,
            "acceptance_report": {"all_pass": False},
            "governance_status": "blocked_review_gate",
        })
        request = {"research_area": "AI cardiac monitoring", "funding_type": "Government"}
        with tempfile.TemporaryDirectory() as temp:
            result = run_capstone(request=request, output_dir=temp, graph=fake, record_runtime=False)
            self.assertEqual(fake.received, {"request": request})
            self.assertEqual(result["status"], "blocked_validation_or_acceptance")
            self.assertTrue(Path(result["dashboard_files"]["html"]).exists())
            self.assertFalse(result["published"])

    def test_summary_omits_proposal_body_and_private_fields(self):
        state = {
            "proposal": {"narrative": "confidential draft body", "owner_email": "person@example.test"},
            "validation_passed": False,
        }
        summary = build_dashboard_summary(state)
        dumped = json.dumps(summary)
        self.assertNotIn("confidential draft body", dumped)
        self.assertNotIn("person@example.test", dumped)


class TestLab14GraphIntegration(unittest.TestCase):
    def test_existing_langgraph_still_builds(self):
        try:
            from graph.langgraph_grant import build_grant_graph
        except ImportError as exc:
            self.skipTest(f"LangGraph dependency unavailable: {exc}")
        graph = build_grant_graph()
        self.assertTrue(hasattr(graph, "invoke"))


if __name__ == "__main__":
    unittest.main()
