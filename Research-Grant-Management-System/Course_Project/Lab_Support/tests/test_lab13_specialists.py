from __future__ import annotations

import unittest
from pathlib import Path

from graph.lab13_specialists import (
    SPECIALIST_PROFILES,
    get_specialist_profile,
    infer_specialist_profile,
    specialize_proposal,
    validate_specialist_output,
)

BASE_PROPOSAL = {
    "title": "Cardiovascular Monitoring Research",
    "research_area": "AI-based cardiovascular monitoring",
    "funding_type": "Government research grant",
    "abstract": "A draft abstract.",
    "objectives": ["Evaluate a research prototype"],
    "methodology": "Develop and evaluate a prototype.",
    "timeline": "24 months",
    "expected_outcomes": ["Prototype", "Evaluation report"],
}
PLAN = {
    "research_area": "AI-based cardiovascular monitoring",
    "funding_type": "Government research grant",
}


class TestLab13Specialists(unittest.TestCase):
    def test_three_profiles_are_registered(self):
        self.assertEqual(set(SPECIALIST_PROFILES), {"government", "industry", "international"})

    def test_government_profile_inferred_from_current_plan(self):
        self.assertEqual(infer_specialist_profile(funding_type="Government research grant"), "government")

    def test_industry_profile_inferred_from_industry_call(self):
        self.assertEqual(infer_specialist_profile(funding_type="Industry partnership grant"), "industry")

    def test_international_profile_has_priority_for_cross_border_call(self):
        self.assertEqual(infer_specialist_profile(funding_type="Government grant", call_title="International collaboration"), "international")

    def test_explicit_supported_profile_overrides_inference(self):
        self.assertEqual(infer_specialist_profile(funding_type="Government research grant", requested_profile="industry"), "industry")

    def test_unknown_profile_inference_fails_closed(self):
        self.assertIsNone(infer_specialist_profile(funding_type="Special programme"))

    def test_profile_lookup_returns_defensive_copy(self):
        profile = get_specialist_profile("government")
        profile["focus_areas"].append("mutated")
        self.assertNotIn("mutated", get_specialist_profile("government")["focus_areas"])

    def test_specialist_output_is_checkable_and_does_not_claim_compliance(self):
        result = specialize_proposal(BASE_PROPOSAL, PLAN, [])
        self.assertEqual(result["profile"], "government")
        self.assertTrue(result["report"]["passed"], result["report"]["issues"])
        metadata = result["proposal"]["specialist_metadata"]
        self.assertEqual(metadata["schema_version"], "lab13.specialist-output.v1")
        self.assertEqual(metadata["call_specific_compliance_status"], "requires_official_call_review")
        self.assertFalse(metadata["mandatory_rules_asserted"])
        self.assertFalse(result["report"]["source_specific_ready"])
        self.assertTrue(result["report"].get("notes"))

    def test_verified_source_is_referenced_but_compliance_stays_pending(self):
        calls = [{
            "agency": "Example Agency",
            "call_title": "Example Government Research Call",
            "source": {"verified": True, "source_url": "https://example.gov/call", "source_title": "Official call"},
        }]
        result = specialize_proposal(BASE_PROPOSAL, PLAN, calls)
        metadata = result["proposal"]["specialist_metadata"]
        self.assertTrue(result["report"]["source_specific_ready"])
        self.assertEqual(metadata["source_reference"], "https://example.gov/call")
        self.assertEqual(metadata["call_specific_compliance_status"], "requires_official_call_review")

    def test_unverified_call_does_not_become_source_ready(self):
        calls = [{"agency": "Example Agency", "call_title": "Demo", "source": {"verified": False, "source_url": "https://example.gov/demo"}}]
        result = specialize_proposal(BASE_PROPOSAL, PLAN, calls)
        self.assertFalse(result["report"]["source_specific_ready"])

    def test_missing_required_proposal_field_fails_contract(self):
        result = specialize_proposal({"title": "Only title"}, PLAN, [])
        self.assertFalse(result["report"]["passed"])
        self.assertTrue(any("research_area" in issue for issue in result["report"]["issues"]))

    def test_unsupported_profile_does_not_apply_a_specialist(self):
        result = specialize_proposal(BASE_PROPOSAL, {"research_area": "x", "funding_type": "special programme"}, [], requested_profile="unknown")
        self.assertIsNone(result["profile"])
        self.assertFalse(result["report"]["passed"])

    def test_original_proposal_is_not_mutated(self):
        proposal = dict(BASE_PROPOSAL)
        result = specialize_proposal(proposal, PLAN, [])
        self.assertNotIn("specialist_metadata", proposal)
        self.assertIn("specialist_metadata", result["proposal"])


class TestLab13GraphWiring(unittest.TestCase):
    def test_specialist_node_is_registered_and_wired_between_drafting_and_budget(self):
        source = (Path(__file__).resolve().parents[1] / "graph" / "langgraph_grant.py").read_text(encoding="utf-8")
        self.assertIn('"lab13_specialist"', source)
        self.assertRegex(source, r'builder\.add_edge\(\s*"proposal_drafting"\s*,\s*"lab13_specialist"\s*\)')
        self.assertRegex(source, r'builder\.add_edge\(\s*"lab13_specialist"\s*,\s*"budget_planning"\s*\)')

    def test_langgraph_compiles_when_dependency_is_available(self):
        try:
            from graph.langgraph_grant import build_grant_graph
        except (ImportError, ModuleNotFoundError) as exc:
            self.skipTest(f"LangGraph/runtime dependency unavailable in this environment: {exc}")
        graph = build_grant_graph()
        self.assertIsNotNone(graph)


if __name__ == "__main__":
    unittest.main()
