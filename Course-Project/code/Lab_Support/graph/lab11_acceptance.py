"""Lab 11 acceptance suite: locked plan -> tested grant artifact."""
from __future__ import annotations

from datetime import date, datetime
import math
from typing import Any

ELIGIBLE_STATUSES = {"eligible", "approved", "pass"}
SUBMITTED_STATUSES = {"submitted", "sent", "published", "transmitted"}
EVIDENCE_FIELDS = (
    "claim", "source_type", "source_title", "source_reference",
    "source_locator", "excerpt",
)

DIAGNOSES = {
    "plan_locked": "The locked plan is missing or is not marked locked. Rebuild the plan before generation.",
    "funding_call_found": "No suitable funding call is selected. Do not generate a grant package without a cleared call.",
    "funding_sources_verified": "At least one selected funding call lacks complete, verified source metadata.",
    "funding_eligibility_cleared": "Funding eligibility is not explicitly cleared for every selected call.",
    "deadlines_tracked_and_active": "A selected funding call has a missing, invalid, or expired deadline.",
    "proposal_created": "The proposal draft is missing. Review drafting inputs and errors.",
    "budget_items_present": "The budget is missing itemized, numeric line items.",
    "budget_totals_reconcile": "The budget total does not equal the sum of its line items.",
    "budget_within_ceiling": "The budget is not confirmed within its documented ceiling.",
    "compliance_passed": "Compliance has not explicitly passed. Resolve each failed rule against the call guidelines.",
    "evidence_grounded": "Evidence records are missing, incomplete, unverified, or out of scope.",
    "no_ungrounded_candidates": "One or more ungrounded candidates remain in the output state.",
    "package_created": "The assembled grant proposal and compliance package is missing.",
    "package_contains_required_parts": "The package does not contain proposal, budget, and compliance components.",
    "package_matches_plan": "The package research area or funding type does not match the locked plan.",
    "no_submission_without_approval": "The package appears to have been submitted without explicit PI / Research Office approval.",
}


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _source_is_verified(call: dict[str, Any]) -> bool:
    source = call.get("source") if isinstance(call.get("source"), dict) else {}
    required = ("source_title", "source_url", "source_locator", "supporting_excerpt", "retrieved_at")
    url = source.get("source_url", "")
    return (
        source.get("verified") is True
        and isinstance(url, str)
        and url.startswith("https://")
        and all(isinstance(source.get(k), str) and source.get(k, "").strip() for k in required)
    )


def _deadline_is_active(call: dict[str, Any]) -> bool:
    raw = call.get("deadline") or call.get("deadline_date")
    if not isinstance(raw, str) or not raw.strip():
        return False
    try:
        parsed = date.fromisoformat(raw.strip()[:10])
    except ValueError:
        return False
    return parsed >= date.today()


def _package_section(package: dict[str, Any], section_name: str) -> str:
    direct = package.get(section_name.lower().replace(" ", "_"))
    if isinstance(direct, str):
        return direct.strip()
    sections = package.get("sections")
    if isinstance(sections, list):
        for section in sections:
            if not isinstance(section, dict):
                continue
            if str(section.get("section", "")).strip().casefold() == section_name.casefold():
                value = section.get("content", "")
                return value.strip() if isinstance(value, str) else ""
    return ""


def acceptance_suite(state: dict[str, Any], plan: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a deterministic build acceptance report without changing state."""
    plan = plan if isinstance(plan, dict) else (state.get("plan") if isinstance(state.get("plan"), dict) else {})
    calls = state.get("funding_calls") if isinstance(state.get("funding_calls"), list) else []
    proposal = state.get("proposal") if isinstance(state.get("proposal"), dict) else {}
    budget = state.get("budget") if isinstance(state.get("budget"), dict) else {}
    items = budget.get("items") if isinstance(budget.get("items"), dict) else {}
    compliance = state.get("compliance") if isinstance(state.get("compliance"), dict) else {}
    evidence = state.get("evidence_records") if isinstance(state.get("evidence_records"), list) else []
    ungrounded = state.get("ungrounded_candidates") if isinstance(state.get("ungrounded_candidates"), list) else []
    package = state.get("final_package") if isinstance(state.get("final_package"), dict) else {}
    submission = state.get("submission") if isinstance(state.get("submission"), dict) else {}

    total = budget.get("total")
    ceiling = budget.get("ceiling")
    numeric_items = bool(items) and all(_finite_number(v) and v >= 0 for v in items.values())
    numeric_total = _finite_number(total)
    numeric_ceiling = _finite_number(ceiling)
    eligible = bool(calls) and all(
        str(call.get("eligibility_status", "")).strip().lower() in ELIGIBLE_STATUSES
        for call in calls if isinstance(call, dict)
    ) and all(isinstance(call, dict) for call in calls)
    sources_ok = bool(calls) and all(isinstance(call, dict) and _source_is_verified(call) for call in calls)
    deadlines_ok = bool(calls) and all(isinstance(call, dict) and _deadline_is_active(call) for call in calls)
    evidence_ok = bool(evidence) and all(
        isinstance(record, dict)
        and all(isinstance(record.get(field), str) and record.get(field, "").strip() for field in EVIDENCE_FIELDS)
        and record.get("verified") is True
        and record.get("in_scope") is True
        for record in evidence
    )
    submission_status = str(submission.get("status", "")).strip().lower()
    submission_was_sent = submission.get("submitted") is True or submission_status in SUBMITTED_STATUSES
    pi_approved = (
        state.get("pi_approved") is True
        or submission.get("pi_approved") is True
        or str(state.get("human_review_status", "")).strip().lower() in {"approved", "approved_for_submission"}
    )
    research_area = str(plan.get("research_area", "")).strip()
    funding_type = str(plan.get("funding_type", "")).strip()
    package_area = _package_section(package, "Research Area")
    package_funding_type = _package_section(package, "Funding Type")

    checks = {
        "plan_locked": bool(plan) and str(plan.get("status", "")).strip().lower() == "locked",
        "funding_call_found": bool(calls),
        "funding_sources_verified": sources_ok,
        "funding_eligibility_cleared": eligible,
        "deadlines_tracked_and_active": deadlines_ok,
        "proposal_created": bool(proposal),
        "budget_items_present": numeric_items,
        "budget_totals_reconcile": numeric_items and numeric_total and math.isclose(float(total), float(sum(items.values())), rel_tol=0.0, abs_tol=1e-6),
        "budget_within_ceiling": numeric_total and numeric_ceiling and total <= ceiling and budget.get("within_ceiling") is True,
        "compliance_passed": str(compliance.get("status", "")).strip().lower() == "pass",
        "evidence_grounded": evidence_ok,
        "no_ungrounded_candidates": len(ungrounded) == 0,
        "package_created": bool(package),
        "package_contains_required_parts": bool(package.get("proposal")) and bool(package.get("budget")) and bool(package.get("compliance")),
        "package_matches_plan": bool(research_area and funding_type and package_area and package_funding_type)
            and package_area.casefold() == research_area.casefold()
            and package_funding_type.casefold() == funding_type.casefold(),
        "no_submission_without_approval": not submission_was_sent or pi_approved,
    }
    failing = [name for name, passed in checks.items() if not passed]
    report = {
        "schema_version": "lab11.acceptance.v1",
        "passed": not failing,
        "all_pass": not failing,
        "checks": checks,
        "failing": failing,
        "diagnoses": [{"check": name, "diagnosis": DIAGNOSES.get(name, "Acceptance check failed.")} for name in failing],
        "passed_count": sum(bool(value) for value in checks.values()),
        "total_checks": len(checks),
        "failing_count": len(failing),
        "evaluated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    return report
