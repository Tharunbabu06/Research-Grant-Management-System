import contextlib
import copy
import io
import unittest

from graph.lab11_acceptance import acceptance_suite

try:
    from graph.langgraph_grant import (
        acceptance_node, acceptance_router, acceptance_blocked_node,
        human_review_node, build_grant_graph,
    )
    NODE_INTEGRATION_AVAILABLE = True
except ModuleNotFoundError as exc:
    if exc.name != "langgraph":
        raise
    NODE_INTEGRATION_AVAILABLE = False


def good_state():
    plan = {
        "research_area": "AI-based cardiovascular monitoring",
        "funding_type": "Government research grant",
        "status": "locked",
    }
    source = {
        "source_title": "Official Government Funding Guidelines",
        "source_url": "https://agency.example.gov/calls/2027.pdf",
        "source_locator": "Page 1, eligibility and deadline section",
        "supporting_excerpt": "Eligible cardiovascular research projects may apply.",
        "retrieved_at": "2026-10-26T10:00:00+00:00",
        "verified": True,
    }
    call = {
        "call_title": "AI Cardiovascular Research Grant",
        "agency": "Example Agency",
        "eligibility_status": "eligible",
        "deadline": "2099-01-15",
        "source": source,
    }
    proposal = {"title": "AI-based cardiovascular monitoring", "objectives": ["Evaluate a model"]}
    budget = {"items": {"personnel": 500, "equipment": 250}, "total": 750, "ceiling": 1000, "within_ceiling": True}
    compliance = {"status": "pass", "checks": [{"name": "eligibility", "passed": True}]}
    evidence = [{
        "claim": "The funding call supports the stated project type",
        "source_type": "official_funding_guideline",
        "source_title": source["source_title"],
        "source_reference": source["source_url"],
        "source_locator": source["source_locator"],
        "excerpt": source["supporting_excerpt"],
        "verified": True,
        "in_scope": True,
    }]
    package = {
        "title": "Grant Proposal and Compliance Package",
        "status": "validated_draft",
        "sections": [
            {"section": "Research Area", "content": plan["research_area"]},
            {"section": "Funding Type", "content": plan["funding_type"]},
        ],
        "proposal": copy.deepcopy(proposal),
        "budget": copy.deepcopy(budget),
        "compliance": copy.deepcopy(compliance),
    }
    return {
        "plan": plan,
        "funding_calls": [call],
        "proposal": proposal,
        "budget": budget,
        "compliance": compliance,
        "submission": {"status": "package_ready_for_validation", "submitted": False},
        "evidence_records": evidence,
        "ungrounded_candidates": [],
        "final_package": package,
        "validation_passed": True,
        "acceptance_passed": False,
        "retry_count": 0,
    }


class TestLab11AcceptanceSuite(unittest.TestCase):
    def test_complete_artifact_passes_every_acceptance_check(self):
        report = acceptance_suite(good_state())
        self.assertTrue(report["all_pass"], report["diagnoses"])
        self.assertEqual(report["failing"], [])
        self.assertEqual(report["passed_count"], report["total_checks"])

    def test_unverified_funding_source_fails_acceptance(self):
        state = good_state()
        state["funding_calls"][0]["source"]["verified"] = False
        report = acceptance_suite(state)
        self.assertFalse(report["all_pass"])
        self.assertIn("funding_sources_verified", report["failing"])

    def test_pending_eligibility_fails_acceptance(self):
        state = good_state()
        state["funding_calls"][0]["eligibility_status"] = "pending_human_review"
        report = acceptance_suite(state)
        self.assertIn("funding_eligibility_cleared", report["failing"])

    def test_budget_mismatch_fails_acceptance(self):
        state = good_state()
        state["budget"]["total"] = 999
        report = acceptance_suite(state)
        self.assertIn("budget_totals_reconcile", report["failing"])

    def test_compliance_cannot_be_assumed_passed(self):
        state = good_state()
        state["compliance"]["status"] = "fail"
        state["final_package"]["compliance"]["status"] = "fail"
        report = acceptance_suite(state)
        self.assertIn("compliance_passed", report["failing"])

    def test_missing_grounding_fails_acceptance(self):
        state = good_state()
        state["evidence_records"] = []
        report = acceptance_suite(state)
        self.assertIn("evidence_grounded", report["failing"])

    def test_package_plan_mismatch_fails_acceptance(self):
        state = good_state()
        state["final_package"]["sections"][0]["content"] = "Different research area"
        report = acceptance_suite(state)
        self.assertIn("package_matches_plan", report["failing"])

    def test_submission_without_pi_approval_fails_acceptance(self):
        state = good_state()
        state["submission"] = {"status": "submitted", "submitted": True, "pi_approved": False}
        report = acceptance_suite(state)
        self.assertIn("no_submission_without_approval", report["failing"])


@unittest.skipUnless(NODE_INTEGRATION_AVAILABLE, "LangGraph is not installed in this environment")
class TestLab11GateIntegration(unittest.TestCase):
    def test_graph_compiles_with_acceptance_gate(self):
        graph = build_grant_graph()
        self.assertIsNotNone(graph)

    def test_failed_acceptance_does_not_route_to_human_review(self):
        state = good_state()
        state["acceptance_report"] = acceptance_suite(state)
        state["acceptance_report"]["all_pass"] = False
        state["acceptance_passed"] = False
        with contextlib.redirect_stdout(io.StringIO()):
            route = acceptance_router(state)
        self.assertEqual(route, "blocked")
        with contextlib.redirect_stdout(io.StringIO()):
            blocked = acceptance_blocked_node(state)
        self.assertEqual(blocked["human_review_status"], "blocked_acceptance_failure")

    def test_human_review_gate_blocks_when_acceptance_was_not_recorded(self):
        state = good_state()
        state.pop("acceptance_report", None)
        state["acceptance_passed"] = False
        with contextlib.redirect_stdout(io.StringIO()):
            result = human_review_node(state)
        self.assertEqual(result["human_review_status"], "blocked_acceptance_failure")

    def test_human_review_gate_allows_only_a_validated_accepted_artifact(self):
        state = good_state()
        state["acceptance_report"] = acceptance_suite(state)
        state["acceptance_passed"] = True
        with contextlib.redirect_stdout(io.StringIO()):
            result = human_review_node(state)
        self.assertEqual(result["human_review_status"], "pending_human_review")
        self.assertEqual(result["build_status"], "ready_for_human_review")


if __name__ == "__main__":
    unittest.main()
