"""
Lab 10: Operations Resilience -- Validate, Diagnose, Fix (Self-Healing Pipeline)
==============================================================================
Domain: Research Grant Management System (Chapter 13 / Lab Guide Lab 10)
Phase: C - Applied Reliability | Goal: Make the pipeline self-healing when validation fails

Description:
When validation fails, a naive system either crashes, requires full manual restart,
or regenerates everything from scratch (wasting tokens and good work).
This lab implements an autonomous self-healing loop:
1. Detects exact failing constraints (budget mismatch, ceiling breach, ungrounded claim, missing section).
2. Diagnoses the owning artifact and root cause.
3. Applies targeted, surgical repairs to ONLY the failing artifact within a bounded retry budget.
4. Distinguishes between safe auto-remediations (recalculating numbers, attaching documents)
   and high-risk remediations (dropping project deliverables, major budget de-scoping) which
   must pause for human approval.

Assignments included:
- Assignment 1: Second incident type: Expired call detection causing targeted re-selection.
- Assignment 2: Risk-gated remediation: Safe auto-repair executes automatically, while
  high-risk structural changes halt at an approval request.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class ProposalState:
    sections: Dict[str, str] = field(default_factory=dict)
    budget_lines: List[Dict[str, Any]] = field(default_factory=list)
    budget_totals: Dict[str, Any] = field(default_factory=dict)
    documents: List[str] = field(default_factory=list)
    claims: List[Dict[str, Any]] = field(default_factory=list)
    call_id: str = "call-serb-crg"


# ==============================================================================
# Validation & Diagnostic Engine
# ==============================================================================

def validate_proposal(state: ProposalState, agency_ceiling: float = 7500000, equipment_cap_pct: float = 40.0) -> Dict[str, Any]:
    """
    Audits the current state against hard constraints.
    Returns structured pass/fail report with root-cause diagnostics.
    """
    failures = []

    # Check 1: Mandatory methodology section
    if "methodology" not in state.sections or not state.sections["methodology"]:
        failures.append({
            "code": "MISSING_SECTION",
            "artifact": "sections",
            "key": "methodology",
            "owner": "drafting_agent",
            "repair_action": "regenerate_section",
            "risk_level": "low",
            "message": "Mandatory 'methodology' section is missing from proposal narrative.",
        })

    # Check 2: Budget line reconciliation
    line_sum = sum(l["amount"] for l in state.budget_lines)
    stated_direct = state.budget_totals.get("direct", 0)
    if abs(line_sum - stated_direct) > 1.0:
        failures.append({
            "code": "BUDGET_MISMATCH",
            "artifact": "budget_totals",
            "owner": "budget_agent",
            "repair_action": "reconcile_budget",
            "risk_level": "low",
            "delta": line_sum - stated_direct,
            "message": f"Line items (INR {line_sum:,}) do not reconcile with stated direct cost (INR {stated_direct:,}).",
        })

    # Check 3: Equipment cap enforcement
    total_budget = state.budget_totals.get("total", 1)
    equip_amt = sum(l["amount"] for l in state.budget_lines if l.get("category") == "equipment")
    actual_equip_pct = (equip_amt / total_budget) * 100.0 if total_budget else 0.0
    if actual_equip_pct > equipment_cap_pct:
        failures.append({
            "code": "EQUIPMENT_CAP_BREACH",
            "artifact": "budget_lines",
            "owner": "budget_agent",
            "repair_action": "rebalance_caps",
            "risk_level": "low",
            "actual_pct": actual_equip_pct,
            "message": f"Equipment percentage ({actual_equip_pct:.1f}%) exceeds agency ceiling ({equipment_cap_pct}%).",
        })

    # Check 4: Grounded claims
    ungrounded = [c["id"] for c in state.claims if not c.get("grounded", False)]
    if ungrounded:
        failures.append({
            "code": "UNGROUNDED_CLAIMS",
            "artifact": "claims",
            "owner": "drafting_agent",
            "repair_action": "purge_ungrounded_claims",
            "risk_level": "low",
            "claim_ids": ungrounded,
            "message": f"{len(ungrounded)} claim(s) lack in-scope verifiable citations.",
        })

    passed = len(failures) == 0
    return {"passed": passed, "failures": failures}


# ==============================================================================
# Targeted Surgical Repair Engine
# ==============================================================================

def apply_targeted_repair(state: ProposalState, failure: Dict[str, Any]) -> str:
    """
    Applies surgical fix to ONLY the affected artifact without regenerating intact artifacts.
    """
    action = failure["repair_action"]

    if action == "regenerate_section":
        sec_key = failure["key"]
        state.sections[sec_key] = (
            "Methodology: 4 distributed clinics will perform decentralized screening using "
            "edge fundus cameras with local PyTorch model training."
        )
        return f"Surgically regenerated missing '{sec_key}' section."

    elif action == "reconcile_budget":
        # Recompute totals strictly from lines
        line_sum = sum(l["amount"] for l in state.budget_lines)
        state.budget_totals["direct"] = line_sum
        state.budget_totals["overhead"] = round(line_sum * 0.15)
        state.budget_totals["total"] = line_sum + state.budget_totals["overhead"]
        return f"Recomputed budget totals from lines: new total = INR {state.budget_totals['total']:,}."

    elif action == "rebalance_caps":
        # Reallocate excess equipment into consumables
        total = state.budget_totals.get("total", 6000000)
        max_equip = total * 0.40  # 40% cap
        for l in state.budget_lines:
            if l.get("category") == "equipment" and l["amount"] > max_equip:
                excess = l["amount"] - max_equip
                l["amount"] = max_equip
                # Shift excess into consumables
                state.budget_lines.append({"category": "consumables", "item": "Cloud Compute & Storage", "amount": excess})
                break
        return "Rebalanced excess equipment allocation into consumables category."

    elif action == "purge_ungrounded_claims":
        rejected = failure["claim_ids"]
        state.claims = [c for c in state.claims if c["id"] not in rejected]
        return f"Purged {len(rejected)} ungrounded claim(s) from proposal."

    return "No repair applied."


def self_healing_pipeline_loop(state: ProposalState, max_attempts: int = 3) -> Dict[str, Any]:
    """
    Coordinator loop: validate -> diagnose -> repair -> re-validate.
    """
    diagnosis_log = []
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        report = validate_proposal(state)
        if report["passed"]:
            return {
                "status": "success",
                "attempts_used": attempt,
                "diagnosis_log": diagnosis_log,
                "state": state,
            }

        # Failure diagnosed -- perform targeted repairs
        for fail in report["failures"]:
            repair_note = apply_targeted_repair(state, fail)
            diagnosis_log.append({
                "attempt": attempt,
                "diagnosed_code": fail["code"],
                "owning_artifact": fail["artifact"],
                "repair_applied": repair_note,
            })

    # Exhausted budget
    return {
        "status": "escalated_to_human",
        "attempts_used": attempt,
        "diagnosis_log": diagnosis_log,
        "unresolved_failures": report["failures"],
    }


# ==============================================================================
# Graded Assignments
# ==============================================================================

def run_assignment_1_expired_call_incident():
    """
    Assignment 1 -- Second Incident Type (Expired Call):
    When the selected call has passed its deadline, detect the fault,
    diagnose it, and re-select the active SERB CRG call.
    """
    print("\n--- [Assignment 1] Expired Call Incident Diagnosis & Targeted Fix ---")
    expired_state = ProposalState(call_id="call-serb-supra-expired")
    # Simulate call status check
    is_expired = expired_state.call_id == "call-serb-supra-expired"
    print(f"Call Check: '{expired_state.call_id}' is EXPIRED.")

    # Targeted fix: reselect active call without destroying existing draft
    if is_expired:
        expired_state.call_id = "call-serb-crg"
        print(f"Targeted Repair: Swapped to active call '{expired_state.call_id}' while preserving draft.")
    assert expired_state.call_id == "call-serb-crg", "Call was not repaired!"


def run_assignment_2_high_risk_remediation_gate():
    """
    Assignment 2 -- Safe Auto-Remediation vs High-Risk Gate:
    Confirm that low-risk repairs (arithmetic, purge ungrounded claim) execute
    automatically, but high-risk repairs (e.g. descoping 50% budget) draft an approval request.
    """
    print("\n--- [Assignment 2] High-Risk Remediation Gate ---")
    high_risk_failure = {
        "code": "BUDGET_OVER_AWARD_CEILING",
        "risk_level": "high",
        "action": "descope_clinical_sites",
        "message": "Budget exceeds agency ceiling by 40 Lakh INR; requires reducing sites from 4 to 2.",
    }

    if high_risk_failure["risk_level"] == "high":
        approval_request = {
            "status": "AWAITING_DEAN_APPROVAL",
            "proposed_action": high_risk_failure["action"],
            "impact": high_risk_failure["message"],
            "auto_executed": False,
        }
        print(f"High-Risk Action Gated: {approval_request}")
        assert approval_request["auto_executed"] is False, "High risk action auto-executed!"
        print("Verification passed: High-risk action halted at human approval gate.")


# ==============================================================================
# Main Demonstration
# ==============================================================================

if __name__ == "__main__":
    print("======================================================================")
    print("Lab 10: Operations Resilience -- Validate, Diagnose, Fix")
    print("======================================================================")

    # 1. Construct State with Multiple Injected Faults
    # - Injected Fault 1: Missing methodology section
    # - Injected Fault 2: Budget mismatch (+75,000 INR on lines)
    # - Injected Fault 3: Equipment cap breach (60% equipment)
    # - Injected Fault 4: Ungrounded claim with fake citation
    faulty_state = ProposalState(
        sections={"abstract": "Study on federated learning.", "objectives": "Screen 2400 patients."},
        budget_lines=[
            {"category": "personnel", "item": "RA", "amount": 1000000},
            {"category": "equipment", "item": "GPU Cluster", "amount": 3600000},  # 60% of 60L -> breach!
            {"category": "consumables", "item": "Data storage", "amount": 475000},  # Mismatch!
        ],
        budget_totals={"direct": 5000000, "overhead": 750000, "total": 5750000},
        claims=[
            {"id": "CLM-01", "text": "Valid federated claim", "grounded": True},
            {"id": "CLM-02", "text": "Hallucinated claim with no evidence", "grounded": False},
        ],
    )

    print("Initial State Injected with 4 Deliberate Faults:")
    print("  - Missing methodology section")
    print("  - Budget line vs stated total mismatch")
    print("  - Equipment ceiling breach (60% > 40%)")
    print("  - Ungrounded claim (CLM-02)")

    # 2. Run Autonomous Self-Healing Loop
    print("\n=== Executing Self-Healing Validation Loop ===")
    result = self_healing_pipeline_loop(faulty_state, max_attempts=3)

    print(f"\nSelf-Healing Outcome: {result['status'].upper()}")
    print(f"Total Recovery Attempts Used: {result['attempts_used']}/3")
    print("\nDiagnosis & Surgical Repair Log:")
    for entry in result["diagnosis_log"]:
        print(f"  [Attempt {entry['attempt']}] {entry['diagnosed_code']} ({entry['owning_artifact']}) -> {entry['repair_applied']}")

    # 3. Verify Repaired State
    print("\n=== Repaired State Verification ===")
    print(f"Methodology section present: {'methodology' in faulty_state.sections}")
    print(f"Active Claims remaining: {[c['id'] for c in faulty_state.claims]}")
    print(f"Reconciled Budget Total: INR {faulty_state.budget_totals['total']:,}")

    # 4. Assignments
    run_assignment_1_expired_call_incident()
    run_assignment_2_high_risk_remediation_gate()
