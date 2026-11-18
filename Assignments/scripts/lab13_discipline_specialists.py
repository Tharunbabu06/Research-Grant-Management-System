"""
Lab 13: Discipline-Specific Agents -- Domain Specialisation
===========================================================
Domain: Research Grant Management System (Chapter 13 / Lab Guide Lab 13)
Phase: D - Governance & Capstone | Goal: Specialise the worklet to its domain variants

Description:
Generic agents produce vague, unusable proposals. Real-world grants require domain
specialisation, where pluggable specialist modules enforce domain-specific templates,
costing schemes, and checkable validation contracts.

This lab implements the three core Funder Domain Specialists from Chapter 13:
1. `Government Specialist` (DST, SERB, ICMR):
   - Sections: Merit, methodology, timeline, Indian costing norms.
   - Budget Scheme: 42% personnel, 30% equipment, 18% consumables, 10% travel.
   - Contract Check: >= 3 numbered objectives, dated milestones, measurable targets.
2. `Industry / CSR Specialist` (Tata Trusts, Infosys Foundation):
   - Sections: Need assessment, monitoring & evaluation, sustainability, Schedule VII.
   - Budget Scheme: 48% personnel, 18% equipment, 22% consumables, 12% travel.
   - Contract Check: >= 2 outcome indicators, sustainability plan, statutory CSR statement.
3. `International Specialist` (EU Horizon Europe, Gates Foundation):
   - Sections: Excellence, impact, work packages, consortium, open science.
   - Budget Scheme: 50% personnel, 24% equipment, 16% consumables, 10% travel.
   - Contract Check: Consortium of >= 3 partners, open-science statement, ethics assessment.

Also bridges the Lab Guide's Engineering Sensor Domain Transfer concept:
- Implements predictive sensor evaluation with safety review gates.

Assignments included:
- Assignment 1: Pluggable International EU Horizon specialist with consortium validation.
- Assignment 2: Trend-based escalation (escalating on multi-metric warnings before alarm).
"""

from typing import Dict, Any, List


# ==============================================================================
# Funder Domain Specialists Registry
# ==============================================================================

class DomainSpecialist:
    def __init__(self, domain_id: str, label: str, sections: List[str],
                 budget_scheme: Dict[str, float], contract_rules: List[Dict[str, Any]]):
        self.domain_id = domain_id
        self.label = label
        self.sections = sections
        self.budget_scheme = budget_scheme
        self.contract_rules = contract_rules

    def check_contract(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Validates domain-specific output contract."""
        results = []
        for rule in self.contract_rules:
            test_fn = rule["test"]
            passed = bool(test_fn(output))
            results.append({
                "label": rule["label"],
                "passed": passed,
                "detail": "satisfied" if passed else rule["fail_msg"],
            })
        all_passed = all(r["passed"] for r in results)
        return {"passed": all_passed, "results": results}


SPECIALIST_REGISTRY: Dict[str, DomainSpecialist] = {
    "government": DomainSpecialist(
        domain_id="government",
        label="Government Agency (SERB / DST / ICMR)",
        sections=["abstract", "objectives", "background", "methodology", "timeline", "outcomes", "budget-justification", "references"],
        budget_scheme={"personnel": 0.42, "equipment": 0.30, "consumables": 0.18, "travel": 0.10},
        contract_rules=[
            {"label": "At least 3 measurable objectives", "test": lambda o: o.get("objectives_count", 0) >= 3, "fail_msg": "Fewer than 3 objectives"},
            {"label": "Milestones with target dates defined", "test": lambda o: o.get("has_milestones", False), "fail_msg": "No dated milestones"},
            {"label": "Measurable clinical/scientific targets", "test": lambda o: o.get("has_measurable_targets", False), "fail_msg": "No target metrics found"},
        ],
    ),
    "industry": DomainSpecialist(
        domain_id="industry",
        label="Industry / CSR (Tata Trusts / Infosys Foundation)",
        sections=["executive-summary", "need-assessment", "objectives", "approach", "implementation-plan", "monitoring-evaluation", "sustainability", "compliance", "references"],
        budget_scheme={"personnel": 0.48, "equipment": 0.18, "consumables": 0.22, "travel": 0.12},
        contract_rules=[
            {"label": "At least 2 outcome indicators", "test": lambda o: o.get("indicators_count", 0) >= 2, "fail_msg": "Fewer than 2 outcome indicators"},
            {"label": "Post-grant sustainability plan", "test": lambda o: o.get("has_sustainability_plan", False), "fail_msg": "Missing sustainability plan"},
            {"label": "Companies Act Schedule VII compliance", "test": lambda o: o.get("has_csr_statement", False), "fail_msg": "Missing Schedule VII statement"},
        ],
    ),
}


# ==============================================================================
# Engineering Domain Transfer (Lab Guide Bridge)
# ==============================================================================

def engineering_sensor_agent(sensor_readings: List[Dict[str, float]]) -> Dict[str, Any]:
    """
    Predictive maintenance agent for research lab equipment (e.g. liquid helium cryostat or GPU servers).
    Demonstrates that ALARM conditions never auto-shutdown; they recommend for human sign-off.
    """
    latest = sensor_readings[-1]
    temp = latest.get("temp_c", 0.0)
    vibration = latest.get("vibration_mm_s", 0.0)

    # Threshold classification
    condition = "NORMAL"
    if vibration >= 4.5 or temp >= 80.0:
        condition = "ALARM"
    elif vibration >= 2.8 or temp >= 70.0:
        condition = "WARNING"

    # Domain safety check (Never auto-executes destructive shutdown)
    if condition == "ALARM":
        action = {"action_allowed": "recommend_shutdown_for_human_engineer_review", "auto_execute": False}
    elif condition == "WARNING":
        action = {"action_allowed": "schedule_preventive_inspection", "auto_execute": False}
    else:
        action = {"action_allowed": "continue_monitoring", "auto_execute": True}

    return {
        "domain": "Mechanical / Infrastructure Research Lab",
        "latest_reading": latest,
        "condition": condition,
        "recommended_action": action["action_allowed"],
        "auto_executed": action["auto_execute"],
    }


# ==============================================================================
# Graded Assignments
# ==============================================================================

def run_assignment_1_international_specialist():
    """
    Assignment 1 -- Add International EU Horizon Specialist:
    Adds the EU Horizon Europe specialist with consortium validation
    (requires at least 3 international partners and open science plan).
    """
    print("\n--- [Assignment 1] Add International Domain Specialist (EU Horizon) ---")
    international_specialist = DomainSpecialist(
        domain_id="international",
        label="International Funder (EU Horizon Europe)",
        sections=["excellence", "impact", "implementation", "consortium", "ethics-security", "data-management", "references"],
        budget_scheme={"personnel": 0.50, "equipment": 0.24, "consumables": 0.16, "travel": 0.10},
        contract_rules=[
            {"label": "Consortium of at least 3 partners", "test": lambda o: o.get("partner_count", 0) >= 3, "fail_msg": "Consortium smaller than 3 partners"},
            {"label": "FAIR open-science plan", "test": lambda o: o.get("open_science", False), "fail_msg": "Missing open-science plan"},
        ],
    )
    SPECIALIST_REGISTRY["international"] = international_specialist

    # Test proposal against international contract
    candidate_output = {
        "partner_count": 3,
        "open_science": True,
    }
    report = international_specialist.check_contract(candidate_output)
    print(f"International Specialist Contract Check: {report['passed']}")
    for r in report["results"]:
        print(f"  {r['label']}: {r['detail']}")
    assert report["passed"], "International specialist check failed!"


def run_assignment_2_trend_escalation():
    """
    Assignment 2 -- Escalate on a Trend, Not Just a Single Threshold:
    If three consecutive readings show WARNING, escalate to inspection
    even if none has breached the ALARM threshold.
    """
    print("\n--- [Assignment 2] Trend-Based Multi-Reading Escalation ---")
    rising_sensor_log = [
        {"temp_c": 65.0, "vibration_mm_s": 2.2},
        {"temp_c": 71.0, "vibration_mm_s": 2.9},  # Warning 1
        {"temp_c": 73.0, "vibration_mm_s": 3.1},  # Warning 2
        {"temp_c": 76.0, "vibration_mm_s": 3.4},  # Warning 3 (Still below 4.5 Alarm)
    ]
    # Check last 3 readings
    warnings = [r for r in rising_sensor_log[-3:] if r["vibration_mm_s"] >= 2.8 or r["temp_c"] >= 70.0]
    if len(warnings) >= 3:
        escalated_action = "ESCALATED_SCHEDULE_IMMEDIATE_INSPECTION"
        print(f"Trend Detected: 3 consecutive warnings. Action escalated to: '{escalated_action}'")
    else:
        escalated_action = "CONTINUE_MONITORING"

    assert escalated_action == "ESCALATED_SCHEDULE_IMMEDIATE_INSPECTION"
    print("Verification passed: Trend-based escalation succeeded.")


# ==============================================================================
# Main Demonstration
# ==============================================================================

if __name__ == "__main__":
    print("======================================================================")
    print("Lab 13: Discipline-Specific Engineering Agents (Domain Specialisation)")
    print("======================================================================")

    # 1. Government Specialist Verification
    print("=== 1. Government Funder Specialist Check ===")
    gov_spec = SPECIALIST_REGISTRY["government"]
    gov_candidate = {
        "objectives_count": 3,
        "has_milestones": True,
        "has_measurable_targets": True,
    }
    gov_check = gov_spec.check_contract(gov_candidate)
    print(f"Domain: {gov_spec.label}")
    print(f"Contract Passed: {gov_check['passed']}")
    for res in gov_check["results"]:
        print(f"  - {res['label']}: {res['detail']}")

    # 2. Industry Specialist Verification
    print("\n=== 2. Industry / CSR Funder Specialist Check ===")
    ind_spec = SPECIALIST_REGISTRY["industry"]
    ind_candidate = {
        "indicators_count": 2,
        "has_sustainability_plan": True,
        "has_csr_statement": True,
    }
    ind_check = ind_spec.check_contract(ind_candidate)
    print(f"Domain: {ind_spec.label}")
    print(f"Contract Passed: {ind_check['passed']}")
    for res in ind_check["results"]:
        print(f"  - {res['label']}: {res['detail']}")

    # 3. Engineering Domain Transfer Demonstration
    print("\n=== 3. Engineering Sensor Domain Transfer ===")
    sample_sensor_log = [
        {"t": 0, "vibration_mm_s": 1.8, "temp_c": 61},
        {"t": 1, "vibration_mm_s": 3.2, "temp_c": 72},
        {"t": 2, "vibration_mm_s": 4.8, "temp_c": 83},  # ALARM!
    ]
    diag = engineering_sensor_agent(sample_sensor_log)
    print(f"Condition Detected: {diag['condition']}")
    print(f"Recommended Action: {diag['recommended_action']}")
    print(f"Auto-Executed: {diag['auto_executed']} (Human sign-off required)")
    assert diag["auto_executed"] is False, "Safety gate violation: ALARM auto-executed!"

    # 4. Assignments
    run_assignment_1_international_specialist()
    run_assignment_2_trend_escalation()
