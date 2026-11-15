"""Lab 13: pluggable funder-profile specialists with checkable output contracts.

Profile recommendations are drafting guidance, NOT a substitute for the selected
call's official guidelines. The specialist never marks eligibility/compliance as
approved and never publishes or submits a proposal.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

SPECIALIST_PROFILES: dict[str, dict[str, Any]] = {
    "government": {
        "display_name": "Government Research Grant Specialist",
        "domain": "government research funding",
        "focus_areas": [
            "research problem and public/scientific value",
            "objectives and measurable outcomes",
            "methodology and work plan",
            "milestones and deliverables",
            "budget justification and eligible-cost checks",
            "institutional approvals and ethics/data governance where applicable",
            "impact, dissemination, and reporting",
        ],
        "review_checklist": [
            "Verify eligibility and institutional requirements against the selected call.",
            "Verify eligible cost heads, budget ceiling, and funding duration against the selected call.",
            "Verify mandatory documents, institutional endorsements, and deadline against the official source.",
            "Record evidence for each call-specific rule; do not infer compliance from this profile.",
        ],
    },
    "industry": {
        "display_name": "Industry Partnership Specialist",
        "domain": "industry and applied research funding",
        "focus_areas": [
            "industry problem and intended value",
            "technical approach and feasibility",
            "prototype, validation, and technology-readiness milestones where relevant",
            "deliverables, ownership, and partner responsibilities",
            "intellectual-property and commercialization questions for human/legal review",
            "industry contribution or co-funding when the call requires it",
            "budget justification and measurable impact",
        ],
        "review_checklist": [
            "Verify partner eligibility and required letters or agreements against the selected call.",
            "Verify IP, data ownership, confidentiality, and commercialization terms with authorized reviewers.",
            "Verify any co-funding or industry contribution requirement from the official source.",
            "Do not invent a partner commitment, contribution, or IP agreement.",
        ],
    },
    "international": {
        "display_name": "International Collaboration Specialist",
        "domain": "international or cross-border research funding",
        "focus_areas": [
            "collaboration objectives and partner roles",
            "work packages, milestones, and cross-site deliverables",
            "budget currency, indirect costs, and consortium allocation where relevant",
            "ethics, privacy, data transfer, and cross-border governance where applicable",
            "international impact and dissemination",
            "partner eligibility and required consortium documentation",
        ],
        "review_checklist": [
            "Verify country, institution, consortium, and partner eligibility against the selected call.",
            "Verify currency, indirect-cost, and cost-sharing rules from the official guidelines.",
            "Verify data-transfer, ethics, and collaboration agreements with authorized reviewers.",
            "Do not assume every international call has the same rules or documentation.",
        ],
    },
}

PROFILE_ALIASES = {
    "government_grant": "government",
    "government_research": "government",
    "public_funding": "government",
    "industry_partnership": "industry",
    "corporate": "industry",
    "cross_border": "international",
    "international_collaboration": "international",
}


def _norm(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().replace("_", " ").replace("-", " ").split())


def infer_specialist_profile(
    funding_type: str = "",
    agency: str = "",
    call_title: str = "",
    requested_profile: str | None = None,
) -> str | None:
    """Prefer an explicit valid selection, otherwise infer from supplied metadata."""
    explicit = _norm(requested_profile)
    explicit_key = explicit.replace(" ", "_")
    explicit_key = PROFILE_ALIASES.get(explicit_key, explicit_key)
    if explicit_key in SPECIALIST_PROFILES:
        return explicit_key

    text = _norm(f"{funding_type} {agency} {call_title}")
    # Check international before government because some public agencies issue
    # international collaboration calls.
    if any(term in text for term in ("international", "cross border", "cross country", "multinational", "consortium", "horizon europe")):
        return "international"
    if any(term in text for term in ("industry", "industrial", "corporate", "commercial", "csr", "private sector", "industry partnership")):
        return "industry"
    if any(term in text for term in ("government", "governmental", "public funding", "serb", "dbt", "icmr", "anrf", "dst", "ministry")):
        return "government"
    return None


def get_specialist_profile(profile_name: str) -> dict[str, Any]:
    """Return a defensive copy of a supported specialist profile."""
    key = _norm(profile_name).replace(" ", "_")
    key = PROFILE_ALIASES.get(key, key)
    if key not in SPECIALIST_PROFILES:
        raise ValueError(f"Unknown specialist profile: {profile_name!r}. Choose one of {', '.join(SPECIALIST_PROFILES)}.")
    return deepcopy(SPECIALIST_PROFILES[key])


def validate_specialist_output(proposal: dict[str, Any]) -> dict[str, Any]:
    """Validate structure and traceability metadata, not funding-call compliance."""
    issues: list[str] = []
    if not isinstance(proposal, dict) or not proposal:
        return {"passed": False, "issues": ["Proposal must be a non-empty object."], "source_specific_ready": False}

    for field in ("title", "research_area", "abstract", "objectives", "methodology", "timeline", "expected_outcomes"):
        value = proposal.get(field)
        if isinstance(value, str) and value.strip():
            continue
        if isinstance(value, list) and value:
            continue
        issues.append(f"Missing or empty proposal field: {field}")

    metadata = proposal.get("specialist_metadata")
    if not isinstance(metadata, dict):
        issues.append("Missing specialist_metadata object.")
        metadata = {}
    profile = str(metadata.get("profile", ""))
    if profile not in SPECIALIST_PROFILES:
        issues.append("Specialist profile must be one of government, industry, international.")
    if metadata.get("schema_version") != "lab13.specialist-output.v1":
        issues.append("Unsupported or missing specialist output schema version.")
    if not isinstance(metadata.get("focus_areas"), list) or not metadata.get("focus_areas"):
        issues.append("Specialist output must include checkable focus_areas.")
    if not isinstance(metadata.get("review_checklist"), list) or not metadata.get("review_checklist"):
        issues.append("Specialist output must include a review checklist.")
    if metadata.get("call_specific_compliance_status") != "requires_official_call_review":
        issues.append("Call-specific compliance must remain explicitly pending official guideline review.")

    source_ready = metadata.get("source_verified") is True and bool(metadata.get("source_reference"))
    return {
        "passed": not issues,
        "issues": issues,
        "profile": profile or None,
        "source_specific_ready": source_ready,
        "note": "Structural validation only; profile guidance does not establish eligibility or compliance.",
    }


def specialize_proposal(
    proposal: dict[str, Any],
    plan: dict[str, Any],
    funding_calls: list[dict[str, Any]] | None = None,
    requested_profile: str | None = None,
) -> dict[str, Any]:
    """Attach a selected domain specialist's checkable guidance to a draft."""
    proposal_copy = deepcopy(proposal) if isinstance(proposal, dict) else {}
    plan = plan if isinstance(plan, dict) else {}
    calls = funding_calls if isinstance(funding_calls, list) else []
    call = calls[0] if calls and isinstance(calls[0], dict) else {}
    source = call.get("source") if isinstance(call.get("source"), dict) else {}

    profile_name = infer_specialist_profile(
        funding_type=str(plan.get("funding_type", proposal_copy.get("funding_type", ""))),
        agency=str(call.get("agency", "")),
        call_title=str(call.get("call_title", call.get("title", ""))),
        requested_profile=requested_profile or plan.get("specialist_profile"),
    )
    if profile_name is None:
        return {
            "proposal": proposal_copy,
            "profile": None,
            "report": {
                "passed": False,
                "issues": ["Could not safely infer the specialist profile. Select government, industry, or international explicitly."],
                "source_specific_ready": False,
                "note": "No specialist has been applied; do not claim domain-specialist output.",
            },
        }

    profile = get_specialist_profile(profile_name)
    source_verified = source.get("verified") is True
    source_reference = str(source.get("source_url", source.get("source_reference", ""))).strip()
    metadata = {
        "schema_version": "lab13.specialist-output.v1",
        "profile": profile_name,
        "profile_display_name": profile["display_name"],
        "profile_version": "1.0",
        "domain": profile["domain"],
        "research_area": str(plan.get("research_area", proposal_copy.get("research_area", ""))),
        "funding_type": str(plan.get("funding_type", proposal_copy.get("funding_type", ""))),
        "selected_agency": str(call.get("agency", "")).strip() or None,
        "selected_call_title": str(call.get("call_title", call.get("title", ""))).strip() or None,
        "source_reference": source_reference or None,
        "source_verified": source_verified and bool(source_reference),
        "focus_areas": deepcopy(profile["focus_areas"]),
        "review_checklist": deepcopy(profile["review_checklist"]),
        "call_specific_compliance_status": "requires_official_call_review",
        "mandatory_rules_asserted": False,
        "disclaimer": "Profile guidance only. Confirm every mandatory requirement against the selected call's official guidelines and institutional policy.",
    }
    proposal_copy["specialist_metadata"] = metadata
    report = validate_specialist_output(proposal_copy)
    if not calls:
        report["notes"] = ["No cleared funding call is attached; output is generic profile guidance, not a matched-call-specific proposal."]
    elif not metadata["source_verified"]:
        report.setdefault("notes", []).append("The selected call lacks a verified source; call-specific requirements remain unconfirmed.")
    return {"proposal": proposal_copy, "profile": profile_name, "report": report}
