"""
Lab 12: Safety, Evaluation, and Governance -- Approval, Evaluation, and Rollback
==============================================================================
Domain: Research Grant Management System (Chapter 13 / Lab Guide Lab 12)
Phase: D - Governance & Capstone | Goal: Add confidentiality, approval, evaluation, and rollback

Description:
High-stakes institutional actions (submitting a grant proposal to a national agency,
allocating institute funds, signing binding legal terms) must never be executed autonomously
by an AI agent. This lab implements all six governance controls:
1. Least Privilege Permissions: The AI agent only holds draft-generation permissions;
   agency portal submission credentials are held exclusively by the Dean R&D.
2. Pre-Flight Diagnostic Evaluation Gate: The agent must pass a benchmark evaluation
   suite (accuracy >= 80%) before its proposals can be routed for review.
3. Named Human Approval Gate: Only users with the 'review:approve' permission
   (Dean R&D / Research Office) can authorize submission; PI self-approval is rejected.
4. Comprehensive Audit Trail: Every evaluation, rejection, approval, and edit is logged.
5. Immutable Releases & One-Click Rollback: Releases are versioned with SHA-256 checksums;
   any post-approval defect can be rolled back cleanly to a prior snapshot.
6. Privacy & Confidentiality: Rejection if raw patient/faculty private data is not scrubbed.

Assignments included:
- Assignment 1: Cost-Category / Financial Clearance Gate (requiring finance approval for > 50L INR).
- Assignment 2: Mandatory Re-Evaluation Gate after every 5 proposals.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from seed_data import USERS, INSTITUTION


# Benchmark evaluation accuracy for the diagnostic drafting agent
REGRESSION_SUITE_RESULT = {"passed": 9, "total": 10}  # 90% accuracy


@dataclass
class ProposalRelease:
    version: int
    run_id: str
    checksum: str
    approved_by: str
    snapshot: Dict[str, Any]
    timestamp: str


class GovernedGrantAgent:
    """
    Enforces the six governance and safety controls.
    """
    permissions = {"can_write": "draft_only"}  # Control 1: Least Privilege

    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []
        self.evaluated: bool = False
        self.proposals_processed_since_eval: int = 0
        self.version_history: List[ProposalRelease] = []

    def evaluate_readiness(self) -> bool:
        """Control 2: Diagnostic Evaluation Gate (must pass >= 80% threshold)."""
        pass_rate = REGRESSION_SUITE_RESULT["passed"] / REGRESSION_SUITE_RESULT["total"]
        self.evaluated = pass_rate >= 0.8
        self._log("evaluation_gate", {"pass_rate": pass_rate, "gate_passed": self.evaluated})
        self.proposals_processed_since_eval = 0
        return self.evaluated

    def _log(self, step: str, data: Dict[str, Any]):
        """Control 4: Audit Logging for all decision points."""
        self.audit_log.append({
            "step": step,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "data": data,
        })

    def propose_submission_package(self, run_id: str, title: str, budget_total: float,
                                   rollback_plan: Optional[str], privacy_scrubbed: bool,
                                   finance_approved: bool = True) -> Dict[str, Any]:
        """Validates safety evidence before drafting an approval request."""
        # Checkpoint: Evaluation Gate
        if not self.evaluated:
            self._log("propose_rejected", {"reason": "agent_not_evaluated"})
            return {"rejected": True, "reason": "Evaluation gate not passed; agent cannot propose packages."}

        # Checkpoint: Periodic Re-evaluation (Assignment 2)
        if self.proposals_processed_since_eval >= 5:
            self._log("propose_rejected", {"reason": "mandatory_reevaluation_required"})
            return {"rejected": True, "reason": "5 proposals processed since last evaluation; re-evaluation required."}

        # Checkpoint: Least Privilege assertion
        if self.permissions["can_write"] != "draft_only":
            raise PermissionError("Security Violation: Agent must never hold production portal submission rights.")

        # Checkpoint 6: Privacy Scrubbing
        if not privacy_scrubbed:
            self._log("propose_rejected", {"reason": "privacy_unscrubbed_patient_data"})
            return {"rejected": True, "reason": "Diagnostic input contains unscrubbed patient data; rejecting."}

        # Checkpoint 5: Mandatory Rollback Plan
        if not rollback_plan:
            self._log("propose_rejected", {"reason": "missing_rollback_plan"})
            return {"rejected": True, "reason": "No rollback contingency plan defined; rejecting."}

        # Assignment 1: Financial threshold clearance
        if budget_total > 5000000 and not finance_approved:
            self._log("propose_rejected", {"reason": "finance_clearance_missing"})
            return {"rejected": True, "reason": "Grants exceeding 50 Lakh INR require explicit Finance Committee clearance."}

        # Control 3: Human Approval Request creation
        self.proposals_processed_since_eval += 1
        approval_request = {
            "run_id": run_id,
            "title": title,
            "budget_total": budget_total,
            "rollback_plan": rollback_plan,
            "privacy_scrubbed": privacy_scrubbed,
            "category": "agency_grant_submission",
            "requires_human_approval": True,
            "status": "AWAITING_DEAN_APPROVAL",
        }
        self._log("approval_requested", approval_request)
        return approval_request

    def authorize_and_publish(self, approval_request: Dict[str, Any], actor: Dict[str, Any],
                              decision: str, notes: str = "") -> Dict[str, Any]:
        """
        Human gate: Evaluates actor permissions.
        Only users with 'review:approve' can authorize publication.
        """
        self._log("human_decision_received", {"actor": actor["name"], "decision": decision})

        # Role-based Access Control Check
        if "review:approve" not in actor.get("permissions", []):
            self._log("authorization_blocked", {"actor": actor["name"], "reason": "insufficient_permissions"})
            raise PermissionError(f"Access Denied: Actor '{actor['name']}' ({actor['role']}) does not hold 'review:approve' permission.")

        if decision != "approved":
            return {"published": False, "status": "changes_requested", "notes": notes}

        # Proceed with Release & Cryptographic Versioning
        new_version = len(self.version_history) + 1
        serialized = json.dumps(approval_request, sort_keys=True)
        checksum = hashlib.sha256(serialized.encode()).hexdigest()

        release = ProposalRelease(
            version=new_version,
            run_id=approval_request["run_id"],
            checksum=checksum,
            approved_by=actor["name"],
            snapshot=approval_request,
            timestamp=datetime.now().isoformat(),
        )
        self.version_history.append(release)

        self._log("published_version", {"version": new_version, "checksum": checksum, "approver": actor["name"]})

        return {
            "published": True,
            "version": new_version,
            "checksum": checksum,
            "approver": actor["name"],
            "status": "PUBLISHED_TO_PORTAL_BY_RESEARCH_OFFICE",
            "auto_submitted_by_agent": False,  # Agent never submits directly!
        }

    def rollback(self, target_version: int, actor: Dict[str, Any]) -> Dict[str, Any]:
        """
        One-click rollback: Restores a previous version snapshot and records a new version entry.
        """
        if "version:rollback" not in actor.get("permissions", []):
            raise PermissionError(f"Access Denied: Actor '{actor['name']}' lacks 'version:rollback' permission.")

        target = next((v for v in self.version_history if v.version == target_version), None)
        if not target:
            raise ValueError(f"Version {target_version} not found in immutable history.")

        # Publishing a rollback creates a new version with the restored snapshot
        restored_version = len(self.version_history) + 1
        new_release = ProposalRelease(
            version=restored_version,
            run_id=target.run_id,
            checksum=target.checksum,
            approved_by=actor["name"],
            snapshot=target.snapshot,
            timestamp=datetime.now().isoformat(),
        )
        self.version_history.append(new_release)
        self._log("rollback_executed", {"from_version": target_version, "new_version": restored_version, "actor": actor["name"]})

        return {
            "status": "rolled_back",
            "restored_from_version": target_version,
            "new_published_version": restored_version,
            "checksum": target.checksum,
        }


# ==============================================================================
# Graded Assignments
# ==============================================================================

def run_assignment_1_cost_category_gate(agent: GovernedGrantAgent):
    """
    Assignment 1 -- Cost-Category Control:
    A grant exceeding 50 Lakh INR must have finance_approved=True.
    Adversarial test with missing flag must be rejected.
    """
    print("\n--- [Assignment 1] Cost-Category Financial Clearance Gate ---")
    res = agent.propose_submission_package(
        run_id="RUN-2026-0005",
        title="High-End AI Supercomputer Grant",
        budget_total=6500000,  # 65L > 50L threshold
        rollback_plan="Revert to prior draft v1",
        privacy_scrubbed=True,
        finance_approved=False,  # Missing clearance!
    )
    print(f"Adversarial Test (Missing Finance Clearance): {res}")
    assert res.get("rejected") is True, "Proposal should have been rejected for missing finance clearance!"
    print("Verification passed: Financial threshold control strictly enforced.")


def run_assignment_2_periodic_reevaluation(agent: GovernedGrantAgent):
    """
    Assignment 2 -- Mandatory Re-Evaluation Gate After N Proposals:
    After processing 5 proposals, confirm the 6th is blocked until
    evaluate_readiness() is called again.
    """
    print("\n--- [Assignment 2] Mandatory Periodic Re-Evaluation Gate ---")
    # Simulate processing 5 proposals
    agent.proposals_processed_since_eval = 5

    res = agent.propose_submission_package(
        run_id="RUN-2026-0006",
        title="6th Consecutive Proposal",
        budget_total=3000000,
        rollback_plan="Revert to v1",
        privacy_scrubbed=True,
    )
    print(f"6th Proposal Attempt without re-evaluation: {res}")
    assert res.get("rejected") is True, "6th proposal should be blocked without re-evaluation!"

    # Re-evaluate
    agent.evaluate_readiness()
    print("Re-evaluated readiness benchmark: gate passed.")

    res_retry = agent.propose_submission_package(
        run_id="RUN-2026-0006",
        title="6th Consecutive Proposal",
        budget_total=3000000,
        rollback_plan="Revert to v1",
        privacy_scrubbed=True,
    )
    print(f"6th Proposal Attempt after re-evaluation: Status = {res_retry.get('status')}")
    assert res_retry.get("requires_human_approval") is True, "Should succeed after re-evaluation!"
    print("Verification passed: Periodic re-evaluation successfully enforced.")


# ==============================================================================
# Main Demonstration
# ==============================================================================

if __name__ == "__main__":
    print("======================================================================")
    print("Lab 12: Safety, Evaluation, and Governance (Approval & Rollback)")
    print("======================================================================")

    agent = GovernedGrantAgent()

    # 1. Control 2: Pre-flight Evaluation Gate
    print("=== Control 2: Pre-Flight Evaluation Gate ===")
    eval_passed = agent.evaluate_readiness()
    print(f"Agent evaluated against benchmark test suite: {eval_passed}")

    # 2. Rejection Test 1: Missing Rollback Plan
    print("\n=== Attempt 1: Missing Rollback Plan (Must Reject) ===")
    rej1 = agent.propose_submission_package(
        run_id="RUN-2026-0001",
        title="Diabetic Retinopathy Grant",
        budget_total=4500000,
        rollback_plan=None,  # Missing!
        privacy_scrubbed=True,
    )
    print(f"Result: {rej1}")

    # 3. Rejection Test 2: Unscrubbed Patient Data
    print("\n=== Attempt 2: Unscrubbed Patient Data (Must Reject) ===")
    rej2 = agent.propose_submission_package(
        run_id="RUN-2026-0001",
        title="Diabetic Retinopathy Grant",
        budget_total=4500000,
        rollback_plan="Revert to v1",
        privacy_scrubbed=False,  # Raw clinical identifiers present!
    )
    print(f"Result: {rej2}")

    # 4. Valid Proposal drafted
    print("\n=== Attempt 3: Valid Proposal Drafted ===")
    valid_request = agent.propose_submission_package(
        run_id="RUN-2026-0001",
        title="Diabetic Retinopathy Grant",
        budget_total=4500000,
        rollback_plan="Revert to initial seed v1 on agency rejection",
        privacy_scrubbed=True,
    )
    print(f"Status: {valid_request['status']} (Run: {valid_request['run_id']})")

    # 5. Authorization Attempt 1: PI Attempting to Approve (Must Fail)
    print("\n=== Human Gate: PI Attempts Self-Approval (Must Reject) ===")
    pi_user = next(u for u in USERS if u["role"] == "pi")
    try:
        agent.authorize_and_publish(valid_request, actor=pi_user, decision="approved")
    except PermissionError as e:
        print(f"Blocked as expected: {e}")

    # 6. Authorization Attempt 2: Dean R&D Approves (Must Pass)
    print("\n=== Human Gate: Dean R&D Authorizes Publication ===")
    dean_user = next(u for u in USERS if u["role"] == "dean")
    release_info = agent.authorize_and_publish(valid_request, actor=dean_user, decision="approved")
    print(f"Published Version: v{release_info['version']} | Checksum: {release_info['checksum'][:16]}...")

    # 7. Rollback Demonstration
    print("\n=== One-Click Rollback Demonstration ===")
    rollback_info = agent.rollback(target_version=1, actor=dean_user)
    print(f"Rollback complete: {rollback_info}")

    # 8. Run Assignments
    run_assignment_1_cost_category_gate(agent)
    run_assignment_2_periodic_reevaluation(agent)

    # 9. Audit Log Inspection
    print("\n=== Full Governance Audit Trail (Sample) ===")
    for entry in agent.audit_log[:5]:
        print(f"  {entry['timestamp']} | Step: {entry['step']} | Data: {entry['data']}")
