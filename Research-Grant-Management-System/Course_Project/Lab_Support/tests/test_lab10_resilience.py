import contextlib
import io
import unittest

from graph.lab10_resilience import (
    apply_targeted_repairs,
    diagnose_check,
    is_repairable,
)

try:
    from graph.langgraph_grant import (
        MAX_RETRIES,
        regenerate_node,
        validation_node,
        validation_router,
    )
    NODE_INTEGRATION_AVAILABLE = True
except ModuleNotFoundError as exc:
    if exc.name != "langgraph":
        raise
    NODE_INTEGRATION_AVAILABLE = False


def good_state():
    return {
        "funding_calls": [{
            "call_title": "Verified test call",
            "eligibility_status": "eligible",
            "deadline": "2099-01-15",
        }],
        "proposal": {"title": "Test proposal"},
        "budget": {
            "items": {"personnel": 500, "equipment": 250},
            "total": 750,
            "ceiling": 1000,
            "within_ceiling": True,
        },
        "compliance": {"status": "pass", "checks": []},
        "submission": {"status": "package_ready_for_validation", "submitted": False},
        "evidence_records": [{"claim": "Test evidence", "verified": True, "in_scope": True}],
        "ungrounded_candidates": [],
        "retry_count": 0,
        "diagnosis_log": [],
    }


def run_node(node, state):
    with contextlib.redirect_stdout(io.StringIO()):
        state.update(node(state))


class TestLab10RepairHelpers(unittest.TestCase):
    def test_injected_budget_total_fault_is_repaired_without_changing_items(self):
        state = good_state()
        state["budget"]["total"] = 999  # deliberate fault injection
        before_items = dict(state["budget"]["items"])
        self.assertTrue(is_repairable("budget_totals_reconcile", state))

        updates = apply_targeted_repairs(state, ["budget_totals_reconcile"], retry_count=1)
        state.update(updates)
        self.assertEqual(state["budget"]["total"], 750)
        self.assertEqual(state["budget"]["items"], before_items)
        self.assertEqual(state["retry_count"], 1)
        self.assertEqual(state["diagnosis_log"][-1]["actions"][0]["action"], "recomputed_budget_total")

    def test_injected_ceiling_fault_changes_only_explicitly_adjustable_items(self):
        state = good_state()
        state["budget"] = {
            "items": {"personnel": 700, "equipment": 500, "travel": 200},
            "total": 1400,
            "ceiling": 1000,
            "within_ceiling": False,
            "adjustment_priority": ["travel", "equipment"],
            "adjustment_policy_approved": True,
        }
        self.assertTrue(is_repairable("budget_within_ceiling", state))
        state.update(apply_targeted_repairs(state, ["budget_within_ceiling"], retry_count=1))
        self.assertEqual(state["budget"]["total"], 1000)
        self.assertTrue(state["budget"]["within_ceiling"])
        self.assertEqual(state["budget"]["items"]["personnel"], 700)

    def test_compliance_failure_is_not_automatically_cleared(self):
        state = good_state()
        state["compliance"] = {"status": "fail", "checks": ["missing eligibility evidence"]}
        self.assertFalse(is_repairable("compliance_passed", state))
        self.assertIn("Never change the status to pass", diagnose_check("compliance_passed"))
        state.update(apply_targeted_repairs(state, ["compliance_passed"], retry_count=1))
        self.assertEqual(state["compliance"]["status"], "fail")
        self.assertEqual(state["diagnosis_log"][-1]["actions"][0]["action"], "escalation_required")

    def test_budget_ceiling_without_explicit_adjustment_policy_is_not_repairable(self):
        state = good_state()
        state["budget"].update({"total": 1250, "ceiling": 1000, "within_ceiling": False})
        self.assertFalse(is_repairable("budget_within_ceiling", state))


@unittest.skipUnless(NODE_INTEGRATION_AVAILABLE, "LangGraph is not installed in this test environment")
class TestLab10LangGraphFailureInjection(unittest.TestCase):
    def test_budget_total_fault_is_detected_repaired_and_revalidated_within_retry_budget(self):
        state = good_state()
        state["budget"]["total"] = 999  # deliberate fault injection
        before_items = dict(state["budget"]["items"])

        run_node(validation_node, state)
        self.assertFalse(state["validation_passed"])
        self.assertIn("budget_totals_reconcile", state["failing_checks"])
        self.assertEqual(validation_router(state), "regenerate")

        run_node(regenerate_node, state)
        self.assertEqual(state["retry_count"], 1)
        self.assertEqual(state["budget"]["total"], 750)
        self.assertEqual(state["budget"]["items"], before_items)
        run_node(validation_node, state)
        self.assertTrue(state["validation_passed"])
        self.assertLessEqual(state["retry_count"], MAX_RETRIES)

    def test_compliance_failure_routes_to_human_review(self):
        state = good_state()
        state["compliance"] = {"status": "fail", "checks": ["missing eligibility evidence"]}
        run_node(validation_node, state)
        self.assertIn("compliance_passed", state["failing_checks"])
        self.assertEqual(validation_router(state), "human_review")

    def test_retry_limit_routes_to_human_review(self):
        state = good_state()
        state["budget"]["total"] = 999
        state["retry_count"] = MAX_RETRIES
        run_node(validation_node, state)
        self.assertEqual(validation_router(state), "human_review")

    def test_untracked_deadline_routes_to_human_review(self):
        state = good_state()
        state["funding_calls"][0].pop("deadline")
        run_node(validation_node, state)
        self.assertIn("deadline_tracked", state["failing_checks"])
        self.assertEqual(validation_router(state), "human_review")

    def test_submitted_package_without_pi_approval_routes_to_human_review(self):
        state = good_state()
        state["submission"] = {"status": "submitted", "submitted": True}
        run_node(validation_node, state)
        self.assertIn("no_submission_without_approval", state["failing_checks"])
        self.assertEqual(validation_router(state), "human_review")


if __name__ == "__main__":
    unittest.main()
