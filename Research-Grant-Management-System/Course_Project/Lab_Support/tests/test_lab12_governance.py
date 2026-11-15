import json
import tempfile
import unittest
from pathlib import Path

from graph.lab12_governance import (
    authorize_access,
    authorize_review,
    evaluation_metrics,
    publish_approved_artifact,
    record_review_pending,
    rollback_release,
)


def valid_state(title="Grant draft"):
    report = {"all_pass": True, "checks": {"budget": True, "evidence": True, "compliance": True}}
    return {
        "validation_passed": True,
        "acceptance_passed": True,
        "acceptance_report": report,
        "human_review_status": "pending_human_review",
        "plan": {"status": "locked", "research_area": "AI cardiovascular monitoring"},
        "evidence_records": [{"claim": "topic support"}],
        "final_package": {"title": title, "status": "validated_draft", "proposal": {"title": title}, "budget": {"total": 750}, "compliance": {"status": "pass"}},
    }


def reviewer(**overrides):
    result = {"user_id": "reviewer-1", "role": "research_office", "is_authenticated": True, "can_approve": True, "can_rollback": True, "can_access_confidential": True, "department": "research"}
    result.update(overrides)
    return result


class TestLab12Governance(unittest.TestCase):
    def test_approved_validated_artifact_creates_versioned_release_and_audit(self):
        with tempfile.TemporaryDirectory() as temp:
            result = publish_approved_artifact(valid_state(), reviewer(), {"decision": "approve", "approved_by": "reviewer-1", "note": "Reviewed"}, temp)
            self.assertTrue(result["ok"], result.get("issues"))
            self.assertEqual(result["release_version"], 1)
            release = json.loads(Path(result["release_path"]).read_text(encoding="utf-8"))
            self.assertEqual(release["status"], "published_approved")
            self.assertEqual(release["package"]["status"], "approved")
            self.assertTrue(Path(temp, "governance_audit.jsonl").exists())

    def test_unauthorized_role_cannot_publish(self):
        with tempfile.TemporaryDirectory() as temp:
            actor = reviewer(role="student", can_approve=False)
            result = publish_approved_artifact(valid_state(), actor, {"decision": "approve", "approved_by": actor["user_id"]}, temp)
            self.assertFalse(result["ok"])
            self.assertEqual(result["governance_status"], "approval_denied")
            self.assertEqual(list(Path(temp, "releases").glob("release_v*.json")) if Path(temp, "releases").exists() else [], [])

    def test_validation_failure_blocks_release(self):
        with tempfile.TemporaryDirectory() as temp:
            state = valid_state()
            state["validation_passed"] = False
            result = publish_approved_artifact(state, reviewer(), {"decision": "approve", "approved_by": "reviewer-1"}, temp)
            self.assertFalse(result["ok"])
            self.assertIn("Validation must pass", " ".join(result["issues"]))

    def test_acceptance_failure_blocks_release(self):
        with tempfile.TemporaryDirectory() as temp:
            state = valid_state()
            state["acceptance_passed"] = False
            result = publish_approved_artifact(state, reviewer(), {"decision": "approve", "approved_by": "reviewer-1"}, temp)
            self.assertFalse(result["ok"])
            self.assertTrue(any("acceptance" in item.lower() for item in result["issues"]))

    def test_missing_explicit_human_approval_blocks_release(self):
        with tempfile.TemporaryDirectory() as temp:
            result = publish_approved_artifact(valid_state(), reviewer(), {"decision": "pending", "approved_by": "reviewer-1"}, temp)
            self.assertFalse(result["ok"])
            self.assertTrue(any("explicit human approval" in item.lower() for item in result["issues"]))

    def test_approval_identity_must_match_reviewer(self):
        with tempfile.TemporaryDirectory() as temp:
            result = publish_approved_artifact(valid_state(), reviewer(), {"decision": "approve", "approved_by": "someone-else"}, temp)
            self.assertFalse(result["ok"])
            self.assertTrue(any("identity" in item.lower() for item in result["issues"]))

    def test_cross_department_confidential_access_is_denied(self):
        actor = reviewer(role="faculty", can_approve=False, can_access_confidential=False, department="biology")
        resource = {"owner_id": "another-user", "department": "engineering"}
        allowed, reason = authorize_access(actor, resource, "read")
        self.assertFalse(allowed)
        self.assertIn("another owner or department", reason)

    def test_owner_can_read_owned_resource(self):
        actor = reviewer(role="faculty", user_id="faculty-1", department="biology", can_access_confidential=False, can_approve=False)
        allowed, _ = authorize_access(actor, {"owner_id": "faculty-1", "department": "chemistry"}, "read")
        self.assertTrue(allowed)

    def test_rollback_creates_new_version_and_preserves_old_releases(self):
        with tempfile.TemporaryDirectory() as temp:
            first = publish_approved_artifact(valid_state("Version One"), reviewer(), {"decision": "approve", "approved_by": "reviewer-1"}, temp)
            self.assertTrue(first["ok"])
            second = publish_approved_artifact(valid_state("Version Two"), reviewer(), {"decision": "approve", "approved_by": "reviewer-1"}, temp)
            self.assertTrue(second["ok"])
            rollback = rollback_release(1, reviewer(), temp)
            self.assertTrue(rollback["ok"], rollback.get("issues"))
            self.assertEqual(rollback["release_version"], 3)
            self.assertEqual(rollback["release"]["package"]["title"], "Version One")
            self.assertEqual(len(list(Path(temp, "releases").glob("release_v*.json"))), 3)

    def test_rollback_requires_explicit_permission(self):
        with tempfile.TemporaryDirectory() as temp:
            first = publish_approved_artifact(valid_state(), reviewer(), {"decision": "approve", "approved_by": "reviewer-1"}, temp)
            self.assertTrue(first["ok"])
            actor = reviewer(can_rollback=False)
            result = rollback_release(1, actor, temp)
            self.assertFalse(result["ok"])
            self.assertEqual(result["governance_status"], "rollback_denied")

    def test_pending_review_does_not_publish(self):
        with tempfile.TemporaryDirectory() as temp:
            result = record_review_pending(valid_state(), temp)
            self.assertEqual(result["governance_status"], "pending_human_approval")
            self.assertIsNone(result["release_version"])
            self.assertFalse(Path(temp, "releases").exists())

    def test_metrics_are_reported_without_changing_state(self):
        state = valid_state()
        result = evaluation_metrics(state)
        self.assertEqual(result["acceptance_checks_passed"], 3)
        self.assertEqual(result["acceptance_checks_total"], 3)
        self.assertEqual(result["acceptance_pass_rate"], 1.0)
        self.assertEqual(result["evidence_record_count"], 1)


try:
    from graph.langgraph_grant import build_grant_graph, governance_node
    LANGGRAPH_AVAILABLE = True
except ModuleNotFoundError as exc:
    if exc.name != "langgraph":
        raise
    LANGGRAPH_AVAILABLE = False


@unittest.skipUnless(LANGGRAPH_AVAILABLE, "LangGraph is not installed in this environment")
class TestLab12GraphIntegration(unittest.TestCase):
    def test_graph_compiles_with_governance_node(self):
        self.assertIsNotNone(build_grant_graph())

    def test_governance_node_leaves_unapproved_package_unpublished(self):
        with tempfile.TemporaryDirectory() as temp:
            state = valid_state()
            # Tell the governance module to use a temporary output dir by replacing its default path in this test.
            import graph.lab12_governance as governance
            original = governance._default_output_dir
            governance._default_output_dir = lambda: Path(temp)
            try:
                result = governance_node(state)
            finally:
                governance._default_output_dir = original
            self.assertEqual(result["governance_status"], "pending_human_approval")
            self.assertIsNone(result["release_version"])
            self.assertFalse(Path(temp, "releases").exists())


if __name__ == "__main__":
    unittest.main()
