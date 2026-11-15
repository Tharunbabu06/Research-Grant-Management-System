"""Safe diagnosis and targeted repair helpers for Agentic AI Lab 10."""
from __future__ import annotations

from copy import deepcopy
import math
from typing import Any


DIAGNOSES = {
    "funding_call_found": (
        "No fully cleared funding call is available. Recheck source verification, deadline, "
        "research-area fit, eligibility, and novelty; do not invent a match."
    ),
    "proposal_created": (
        "The proposal is missing. Check the proposal-drafting inputs and error output before retrying."
    ),
    "eligibility_and_compliance_met": (
        "Eligibility and compliance are not both confirmed. Check the selected call's explicit eligibility "
        "status and the compliance checklist against the call's guidelines."
    ),
    "deadline_tracked": (
        "At least one selected funding call has no parseable deadline. Verify the deadline from its source."
    ),
    "no_submission_without_approval": (
        "The package appears submitted without recorded PI / Research Office approval. Stop external actions "
        "and escalate for human review."
    ),
    "budget_totals_reconcile": (
        "The stored budget total differs from the sum of its itemized amounts. Recompute the total "
        "from the existing line items; preserve the line items."
    ),
    "budget_within_ceiling": (
        "The budget exceeds the recorded ceiling. A repair is safe only when the budget contains "
        "an explicit adjustment_priority approved by the budget-planning policy; otherwise escalate."
    ),
    "compliance_passed": (
        "Compliance has not passed. Inspect the individual failed rules and their evidence. Never "
        "change the status to pass without resolving and rechecking those rules."
    ),
    "evidence_grounded": (
        "Evidence is missing or ungrounded. Re-check source validity and scope; unsupported claims "
        "must be rejected or sent for human review."
    ),
}


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def diagnose_check(check_name: str) -> str:
    """Provide a deterministic human-readable diagnosis for a failed check."""
    return DIAGNOSES.get(
        check_name,
        f"Validation check '{check_name}' failed. Inspect its inputs and escalate if no safe repair is defined.",
    )


def is_repairable(check_name: str, state: dict[str, Any]) -> bool:
    """Return whether the current state has enough information for a safe repair."""
    budget = state.get("budget") or {}
    items = budget.get("items") or {}

    if check_name == "budget_totals_reconcile":
        return (
            isinstance(items, dict)
            and bool(items)
            and all(_finite_number(value) and value >= 0 for value in items.values())
        )

    if check_name == "budget_within_ceiling":
        priority = budget.get("adjustment_priority")
        ceiling = budget.get("ceiling")
        return (
            isinstance(items, dict)
            and budget.get("adjustment_policy_approved") is True
            and isinstance(priority, list)
            and bool(priority)
            and _finite_number(ceiling)
            and ceiling >= 0
            and all(
                isinstance(key, str) and key in items and _finite_number(items[key]) and items[key] >= 0
                for key in priority
            )
        )

    # Funding eligibility, proposal generation, compliance, and evidence need
    # domain-specific evidence; do not auto-clear them by toggling a status.
    return False


def apply_targeted_repairs(
    state: dict[str, Any], failing_checks: list[str], retry_count: int
) -> dict[str, Any]:
    """Repair only explicitly repairable budget constraints and return LangGraph updates."""
    budget = deepcopy(state.get("budget") or {})
    items = deepcopy(budget.get("items") or {})
    actions: list[dict[str, Any]] = []

    if "budget_totals_reconcile" in failing_checks and is_repairable("budget_totals_reconcile", state):
        previous_total = budget.get("total")
        budget["items"] = items
        budget["total"] = sum(items.values())
        ceiling = budget.get("ceiling")
        if _finite_number(ceiling):
            budget["within_ceiling"] = budget["total"] <= ceiling
        actions.append({
            "action": "recomputed_budget_total",
            "before": previous_total,
            "after": budget["total"],
            "line_items_changed": False,
            "reason": "Sum of existing validated line items; no line item was changed.",
        })

    if "budget_within_ceiling" in failing_checks and is_repairable("budget_within_ceiling", {**state, "budget": budget}):
        ceiling = budget["ceiling"]
        total = sum(items.values())
        excess = max(0, total - ceiling)
        reductions: list[dict[str, Any]] = []
        # Reduce only categories expressly listed as adjustable, in the supplied order.
        for key in budget["adjustment_priority"]:
            if excess <= 0:
                break
            before = items[key]
            reduction = min(before, excess)
            if reduction > 0:
                items[key] = before - reduction
                excess -= reduction
                reductions.append({"item": key, "before": before, "after": items[key], "reduction": reduction})
        budget["items"] = items
        budget["total"] = sum(items.values())
        budget["within_ceiling"] = budget["total"] <= ceiling
        if budget["within_ceiling"]:
            actions.append({
                "action": "adjusted_budget_within_ceiling",
                "reductions": reductions,
                "after_total": budget["total"],
                "ceiling": ceiling,
                "reason": "Only categories in the explicit adjustment_priority were changed.",
            })
        else:
            actions.append({
                "action": "budget_ceiling_repair_incomplete",
                "reductions": reductions,
                "remaining_excess": max(0, budget["total"] - ceiling),
                "reason": "Priority categories were insufficient; human review is required.",
            })

    log = list(state.get("diagnosis_log") or [])
    for check in failing_checks:
        if check not in {"budget_totals_reconcile", "budget_within_ceiling"}:
            actions.append({
                "action": "escalation_required",
                "check": check,
                "diagnosis": diagnose_check(check),
            })

    log.append({
        "event": "targeted_repair",
        "attempt": retry_count,
        "failing_checks": list(failing_checks),
        "actions": actions,
    })
    return {"budget": budget, "retry_count": retry_count, "diagnosis_log": log}
