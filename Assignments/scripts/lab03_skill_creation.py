"""
Lab 3: Skill Creation -- Reusable Plan & Format Skills
======================================================
Domain: Research Grant Management System (Chapter 13 / Lab Guide Lab 3)
Phase: A - Foundations | Goal: Package repeatable capability as reusable, schema-typed skills

Description:
A skill is not a prompt string; it is a reusable, schema-constrained software unit.
This lab implements two core skills of the Research Grant Management System:
1. `plan_skill`: Transforms intake parameters and call requirements into a validated,
   locked execution plan with phased agent assignments and acceptance criteria.
2. `format_skill`: Renders the proposal narrative, itemized budget CSV, and compliance
   checklist into standard agency-submission documents.

Key concepts demonstrated:
- Explicit typed schemas (input & output specifications).
- Plan locking and SHA-256 integrity checksum.
- Cross-domain reusability test (verifying that the exact same skill handles
  Government, Industry/CSR, and International grant calls without code edits).
- Strict contract enforcement: rejection of plans missing mandatory units (objectives, references).

Assignments included:
- Assignment 1: Multi-domain template synthesis (handling Government vs Industry CSR).
- Assignment 2: Low-input / contract validation test (ensuring invalid plans raise structured errors).
"""

import hashlib
import json
from typing import Dict, Any, List, Optional
from seed_data import CALLS, INSTITUTION


# ==============================================================================
# Skill 1: Plan Skill (Specification, Lock, and Revision)
# ==============================================================================

PLAN_SCHEMA = {
    "name": "plan_skill",
    "version": "1.0.0",
    "description": "Expands research brief and matched call into a locked execution plan.",
    "required_input_fields": ["researchArea", "callId", "domain"],
    "required_output_fields": ["id", "units", "phases", "acceptance", "locked", "checksum"],
}

SECTION_SPECS = {
    "abstract": {"title": "Abstract", "min_words": 90, "purpose": "Problem, approach, outcomes"},
    "objectives": {"title": "Objectives & Aims", "min_words": 90, "purpose": "Measurable targets"},
    "background": {"title": "State of the Art & Gaps", "min_words": 130, "purpose": "Related work"},
    "methodology": {"title": "Methodology", "min_words": 160, "purpose": "Technical design & evaluation"},
    "timeline": {"title": "Work Plan & Milestones", "min_words": 100, "purpose": "Deliverable schedule"},
    "outcomes": {"title": "Expected Outcomes", "min_words": 110, "purpose": "Dissemination & IP"},
    "data-management": {"title": "Data Management & Ethics", "min_words": 110, "purpose": "DPDP compliance"},
    "budget-justification": {"title": "Budget Justification", "min_words": 80, "purpose": "Basis for costs"},
    "references": {"title": "References", "min_words": 30, "purpose": "Resolvable citations"},
    # Industry domain specific sections
    "executive-summary": {"title": "Executive Summary", "min_words": 90, "purpose": "CSR executive briefing"},
    "need-assessment": {"title": "Need Assessment", "min_words": 130, "purpose": "Beneficiary analysis"},
    "sustainability": {"title": "Sustainability Plan", "min_words": 100, "purpose": "Post-grant continuity"},
    "compliance": {"title": "Statutory Compliance", "min_words": 90, "purpose": "Schedule VII CSR declaration"},
}

DEFAULT_ACCEPTANCE_CHECKS = [
    "sections_complete",
    "sections_min_words",
    "claims_grounded",
    "citations_resolve",
    "budget_reconciles",
    "budget_caps",
    "compliance_blocking",
]


def apply_plan_skill(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the Plan Skill: validates inputs, expands sections, binds agents,
    and locks the plan with an immutable cryptographic checksum.
    """
    for req in PLAN_SCHEMA["required_input_fields"]:
        if req not in inputs or not inputs[req]:
            raise ValueError(f"Plan skill error: missing required input '{req}'")

    research_area = inputs["researchArea"]
    call_id = inputs["callId"]
    domain = inputs["domain"]
    sections = inputs.get("sections", [
        "abstract", "objectives", "background", "methodology",
        "timeline", "outcomes", "data-management", "budget-justification", "references"
    ])

    units = []
    for i, sec_key in enumerate(sections, 1):
        meta = SECTION_SPECS.get(sec_key, {"title": sec_key.replace("-", " ").title(), "min_words": 80, "purpose": ""})
        units.append({
            "id": f"U{i:02d}",
            "key": sec_key,
            "title": meta["title"],
            "purpose": meta["purpose"],
            "min_words": meta["min_words"],
            "agent": "proposal_drafting",
            "required": True,
            "evidence_required": True,
        })

    phases = [
        {"id": "gate-1", "label": "Profile intake", "agent": "coordinator", "mode": "sequential"},
        {"id": "discovery", "label": "Discovery & Literature", "agent": "funding+literature", "mode": "parallel"},
        {"id": "drafting", "label": "Proposal narrative", "agent": "drafting", "mode": "sequential"},
        {"id": "budget-compliance", "label": "Budget & Compliance", "agent": "budget+compliance", "mode": "parallel"},
        {"id": "validation", "label": "Validation & Repair", "agent": "coordinator", "mode": "sequential"},
        {"id": "packaging", "label": "Submission packaging", "agent": "submission", "mode": "sequential"},
        {"id": "approval", "label": "Dean R&D human approval", "agent": "dean_human_gate", "mode": "sequential"},
    ]

    plan = {
        "id": f"PLAN-{domain.upper()}-{abs(hash(research_area)) % 10000:04d}",
        "version": 1,
        "title": f"Grant Proposal Plan -- {research_area}",
        "callId": call_id,
        "domain": domain,
        "units": units,
        "phases": phases,
        "acceptance": list(DEFAULT_ACCEPTANCE_CHECKS),
        "locked": False,
        "checksum": None,
    }

    return lock_plan(plan)


def lock_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Validates structure and locks the plan against drift."""
    keys = {u["key"] for u in plan["units"]}
    if "objectives" not in keys:
        raise ValueError("Plan contract violation: mandatory unit 'objectives' missing")
    if not ({"methodology", "approach", "need-assessment"} & keys):
        raise ValueError("Plan contract violation: methodology/approach unit missing")
    if "references" not in keys:
        raise ValueError("Plan contract violation: mandatory unit 'references' missing")

    plan["locked"] = True
    serialized = json.dumps({"units": plan["units"], "acceptance": plan["acceptance"], "callId": plan["callId"]}, sort_keys=True)
    plan["checksum"] = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return plan


# ==============================================================================
# Skill 2: Format Skill (Render Proposal Narrative, Budget CSV, Compliance MD)
# ==============================================================================

def render_proposal_narrative(plan: Dict[str, Any], draft_sections: Dict[str, str]) -> str:
    """Formats full markdown proposal narrative with statutory AI-disclosure banner."""
    lines = [
        f"# {plan['title']}",
        f"**Target Agency Call:** {plan['callId']}",
        f"**Executing Institution:** {INSTITUTION['name']}",
        f"**Plan ID:** {plan['id']} (Checksum: {plan['checksum'][:12]}...)",
        "",
        "> **Notice:** AI-assisted drafting was utilized for initial synthesis. "
        "All scientific claims, methodology, and budgets are reviewed and verified by faculty.",
        "",
    ]
    for unit in plan["units"]:
        lines.append(f"## {unit['title']}")
        text = draft_sections.get(unit["key"], f"Section content for {unit['title']} meeting minimum {unit['min_words']} words.")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def render_budget_csv(budget_data: Dict[str, Any]) -> str:
    """Renders itemized CSV table of direct costs and overheads."""
    lines = ["Category,Item,Basis,Amount_INR"]
    for item in budget_data.get("items", []):
        lines.append(f"{item['category']},{item['item']},{item.get('basis', 'actual')},{item['amount']}")
    lines.append(f"Direct,Total Direct Costs,,{budget_data.get('direct', 0)}")
    lines.append(f"Overhead,Institutional Overhead (15%),,{budget_data.get('overhead', 0)}")
    lines.append(f"Total,Grand Total,,{budget_data.get('total', 0)}")
    return "\n".join(lines)


def render_compliance_markdown(compliance_checks: List[Dict[str, Any]]) -> str:
    """Renders formatted compliance checklist table."""
    lines = [
        "# Compliance Review Checklist",
        "",
        "| Status | Check ID | Requirement | Evidence Found |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for c in compliance_checks:
        lines.append(f"| {c['status'].upper()} | {c['id']} | {c['requirement']} | {c['evidence']} |")
    return "\n".join(lines)


# ==============================================================================
# Reusability Verification (Concept 3)
# ==============================================================================

def reusability_check(plan_gov: Dict[str, Any], plan_ind: Dict[str, Any]):
    """
    Verifies that both plans conform to the exact same top-level schema
    despite serving completely different funding domains.
    """
    keys_gov = set(plan_gov.keys())
    keys_ind = set(plan_ind.keys())
    same_schema = keys_gov == keys_ind
    both_locked = plan_gov["locked"] and plan_ind["locked"]
    distinct_checksums = plan_gov["checksum"] != plan_ind["checksum"]

    print("\n=== Reusability Check Across Domains ===")
    print(f"Identical Schema: {same_schema} ({keys_gov})")
    print(f"Both Plans Cryptographically Locked: {both_locked}")
    print(f"Distinct Integrity Checksums: {distinct_checksums}")
    conclusion = "SKILL IS REUSABLE ACROSS DOMAINS" if same_schema and both_locked and distinct_checksums else "REUSABILITY FAILED"
    print(f"Conclusion: {conclusion}")
    assert conclusion == "SKILL IS REUSABLE ACROSS DOMAINS"


# ==============================================================================
# Graded Assignments
# ==============================================================================

def run_assignment_1_multidomain():
    """
    Assignment 1 -- Multi-Domain Plan Synthesis:
    Demonstrate generating an Industry/CSR plan with CSR-specific sections
    using the exact same skill function.
    """
    print("\n--- [Assignment 1] Industry/CSR Plan Synthesis ---")
    industry_inputs = {
        "researchArea": "Assistive Smart Mobility for Specially-Abled Students",
        "callId": "call-tata-csr",
        "domain": "industry",
        "sections": [
            "executive-summary", "need-assessment", "objectives",
            "methodology", "sustainability", "compliance", "references"
        ],
    }
    plan_ind = apply_plan_skill(industry_inputs)
    print(f"Generated Industry Plan: {plan_ind['id']}")
    print(f"Sections defined: {[u['key'] for u in plan_ind['units']]}")
    print(f"Plan Checksum: {plan_ind['checksum']}")
    return plan_ind


def run_assignment_2_contract_failure():
    """
    Assignment 2 -- Test Against Missing Mandatory Unit:
    If a plan attempts to omit 'objectives', confirm the skill raises a
    contract violation error rather than outputting an invalid plan.
    """
    print("\n--- [Assignment 2] Contract Violation Test (Missing Objectives) ---")
    invalid_inputs = {
        "researchArea": "Autonomous Drones",
        "callId": "call-serb-crg",
        "domain": "government",
        "sections": ["abstract", "methodology", "references"],  # Missing 'objectives'!
    }
    try:
        apply_plan_skill(invalid_inputs)
        print("FAIL: Skill did not catch missing mandatory unit!")
    except ValueError as e:
        print(f"PASS: Contract violation caught as expected: '{e}'")


# ==============================================================================
# Main Demonstration
# ==============================================================================

if __name__ == "__main__":
    print("======================================================================")
    print("Lab 3: Skill Creation -- Reusable Plan & Format Skills")
    print("======================================================================")

    # 1. Apply plan skill for Government Domain (SERB)
    gov_inputs = {
        "researchArea": "Federated Learning for Diabetic Retinopathy",
        "callId": "call-serb-crg",
        "domain": "government",
        "sections": [
            "abstract", "objectives", "background", "methodology",
            "timeline", "outcomes", "data-management", "budget-justification", "references"
        ],
    }
    plan_gov = apply_plan_skill(gov_inputs)
    print("Government Grant Plan:")
    print(f"ID: {plan_gov['id']}, Checksum: {plan_gov['checksum']}")
    print(f"Units Count: {len(plan_gov['units'])}, Locked: {plan_gov['locked']}")

    # 2. Assignment 1: Generate Industry Plan
    plan_ind = run_assignment_1_multidomain()

    # 3. Check reusability
    reusability_check(plan_gov, plan_ind)

    # 4. Demonstrate Format Skill
    print("\n=== Formatted Proposal Narrative Sample ===")
    sample_text = render_proposal_narrative(
        plan_gov,
        {
            "abstract": "This project establishes a four-clinic federated screening pipeline for retinopathy...",
            "objectives": "1. Deploy edge fundus grading. 2. Evaluate clinical sensitivity in 2,400 rural patients.",
        }
    )
    print(sample_text[:400] + "...\n[Remaining sections rendered]")

    # 5. Assignment 2: Contract violation test
    run_assignment_2_contract_failure()
