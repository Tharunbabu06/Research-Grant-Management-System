"""
Lab 8: Parallel Swarm -- Multi-Agent Fan-Out & Alignment Merge
==============================================================
Domain: Research Grant Management System (Chapter 13 / Lab Guide Lab 8)
Phase: B - Orchestration | Goal: Parallelise the per-unit work and select/merge the best

Description:
Demonstrates genuine parallel agent execution (fan-out) via a thread pool,
followed by an explicit, schema-driven merge and conflict resolution stage (fan-in).
In the Research Grant System:
1. Narrative sections ('abstract', 'background', 'methodology', 'budget') are authored
   concurrently by parallel drafting workers.
2. An explicit Merge stage evaluates outputs against the locked plan constraints.
3. A Critique stage checks for inter-agent conflicts (e.g., equipment proposed by
   Methodology exceeding the ceiling enforced by the Budget agent).
4. A Conflict Resolution stage resolves tensions using deterministic priority rules.
5. Wall-clock concurrency vs sequential estimate is benchmarked to report speedup.

Assignments included:
- Assignment 1: Add a fifth role / section ('data_management_agent') proposing secure storage cost.
- Assignment 2: Distributed critique where each specialist independently audits the merged plan.
"""

import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List


# ==============================================================================
# Role Specialist Workers (Genuinely Independent)
# ==============================================================================

def literature_scout_agent(goal: str) -> Dict[str, Any]:
    time.sleep(0.05)  # simulate processing
    return {
        "role": "literature_scout",
        "output": {
            "key": "background",
            "text": "State-of-the-art review: Federated learning reduces central hospital data exposure. 4 papers cited.",
            "citations": ["lit-001", "lit-002", "lit-003", "lit-004"],
            "word_count": 140,
        }
    }

def methodology_agent(goal: str) -> Dict[str, Any]:
    time.sleep(0.06)
    return {
        "role": "methodology_specialist",
        "output": {
            "key": "methodology",
            "text": "Four clinical screening sites will run edge inference on non-mydriatic fundus cameras with local training.",
            "hardware_requested": "High-Performance GPU Cluster (INR 3,500,000)",
            "word_count": 175,
        }
    }

def budget_agent(goal: str) -> Dict[str, Any]:
    time.sleep(0.04)
    return {
        "role": "budget_planner",
        "output": {
            "key": "budget",
            "equipment_ceiling": 2500000,  # 25 Lakh ceiling under SERB guidelines
            "total_budget_cap": 6000000,
            "proposed_direct": 5000000,
            "word_count": 95,
        }
    }

def compliance_agent(goal: str) -> Dict[str, Any]:
    time.sleep(0.05)
    return {
        "role": "compliance_officer",
        "output": {
            "key": "compliance",
            "ethics_clearance_required": True,
            "dpdp_plan_required": True,
            "word_count": 85,
        }
    }

ROLES = {
    "literature": literature_scout_agent,
    "methodology": methodology_agent,
    "budget": budget_agent,
    "compliance": compliance_agent,
}


# ==============================================================================
# Swarm Execution & Plan-Alignment Merge
# ==============================================================================

def run_grant_swarm(goal: str, active_roles: Dict) -> Dict[str, Any]:
    """Runs all specialist agents concurrently using ThreadPoolExecutor."""
    start_time = time.time()
    outputs = {}

    with ThreadPoolExecutor(max_workers=len(active_roles)) as executor:
        futures = {name: executor.submit(fn, goal) for name, fn in active_roles.items()}
        for name, future in futures.items():
            outputs[name] = future.result()

    wall_clock = time.time() - start_time
    return {"outputs": outputs, "wall_clock_sec": wall_clock}


def merge_by_plan(swarm_results: Dict[str, Any], target_sections: List[str]) -> Dict[str, Any]:
    """
    Combines independent outputs into a single draft proposal package.
    Audits coverage against target units in the locked plan.
    """
    outputs = swarm_results["outputs"]
    merged_sections = {}
    coverage = []

    for sec in target_sections:
        # Find which role produced this section
        found = None
        for role_name, res in outputs.items():
            if res["output"].get("key") == sec:
                found = res["output"]
                break

        if found:
            merged_sections[sec] = found
            coverage.append({"section": sec, "status": "covered", "words": found.get("word_count", 0)})
        else:
            coverage.append({"section": sec, "status": "missing", "words": 0})

    return {
        "sections": merged_sections,
        "coverage": coverage,
        "all_covered": all(c["status"] == "covered" for c in coverage),
    }


def critique_draft(merged_draft: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Audits cross-agent constraints and surfaces explicit conflicts.
    """
    conflicts = []
    secs = merged_draft["sections"]

    # Tension 1: Methodology hardware request vs Budget agency ceiling
    if "methodology" in secs and "budget" in secs:
        meth = secs["methodology"]
        bgt = secs["budget"]
        if "GPU Cluster (INR 3,500,000)" in meth.get("hardware_requested", ""):
            requested_cost = 3500000
            allowed_ceiling = bgt.get("equipment_ceiling", 0)
            if requested_cost > allowed_ceiling:
                conflicts.append({
                    "conflict_id": "CONF-001",
                    "conflict": "Equipment cost in methodology exceeds agency ceiling",
                    "roles_involved": ["methodology_specialist", "budget_planner"],
                    "requested_value": requested_cost,
                    "ceiling_value": allowed_ceiling,
                })

    return conflicts


def resolve_conflict(conflict: Dict[str, Any], priority_rule: str = "agency_ceiling_over_spec") -> Dict[str, Any]:
    """
    Resolves identified tensions using documented governance rules.
    """
    if conflict["conflict_id"] == "CONF-001":
        return {
            "rule_applied": priority_rule,
            "resolution": (
                f"Cap equipment at INR {conflict['ceiling_value']:,}; "
                f"direct methodology agent to utilize institutional shared cloud compute for remaining capacity."
            ),
            "revised_equipment_cost": conflict["ceiling_value"],
        }
    return {"rule_applied": "none", "resolution": "no rule matched"}


# ==============================================================================
# Graded Assignments
# ==============================================================================

def data_management_agent(goal: str) -> Dict[str, Any]:
    """Assignment 1 Role: Proposes data storage and DPDP compliance infrastructure."""
    time.sleep(0.04)
    return {
        "role": "data_management_officer",
        "output": {
            "key": "data_management",
            "storage_cost": 800000,
            "text": "Data Management Plan: Encrypted on-premise vault with biometric access logging.",
            "word_count": 115,
        }
    }


def run_assignment_1_fifth_role():
    """
    Assignment 1 -- Add a Fifth Role (Data Management):
    Extends the swarm with a data management officer, runs in parallel,
    and incorporates it into the merged draft.
    """
    print("\n--- [Assignment 1] Add Fifth Role: Data Management ---")
    roles_5 = dict(ROLES)
    roles_5["data_management"] = data_management_agent

    swarm_res = run_grant_swarm("Plan SERB CRG Grant", roles_5)
    merged = merge_by_plan(swarm_res, ["background", "methodology", "budget", "compliance", "data_management"])
    print(f"5-Agent Swarm completed in {swarm_res['wall_clock_sec']:.3f} seconds.")
    print("Coverage report across 5 units:")
    for c in merged["coverage"]:
        print(f"  Unit '{c['section']}': {c['status']} ({c['words']} words)")
    assert merged["all_covered"], "All 5 units should be covered!"


def run_assignment_2_distributed_critique(merged_draft: Dict[str, Any]):
    """
    Assignment 2 -- Distributed Critique:
    Instead of a single monolith function, each specialist independently audits
    the merged plan against their domain rules and logs objections.
    """
    print("\n--- [Assignment 2] Distributed Specialist Critique ---")
    objections = []

    # 1. Budget Specialist checks equipment ceiling
    bgt = merged_draft["sections"].get("budget", {})
    meth = merged_draft["sections"].get("methodology", {})
    if "3,500,000" in meth.get("hardware_requested", "") and bgt.get("equipment_ceiling", 0) < 3500000:
        objections.append({
            "auditing_role": "budget_planner",
            "severity": "blocking",
            "objection": f"Methodology requested hardware of 35L exceeding budget cap of {bgt['equipment_ceiling']} INR.",
        })

    # 2. Compliance Specialist checks ethics requirement in methodology
    comp = merged_draft["sections"].get("compliance", {})
    if comp.get("ethics_clearance_required") and "fundus" in meth.get("text", ""):
        objections.append({
            "auditing_role": "compliance_officer",
            "severity": "advisory",
            "objection": "Methodology involves human clinical fundus imaging; verified ethics document must be attached.",
        })

    for obj in objections:
        print(f"  [{obj['auditing_role']}] ({obj['severity'].upper()}): {obj['objection']}")
    assert len(objections) >= 2, "Expected multiple independent objections!"


# ==============================================================================
# Main Demonstration
# ==============================================================================

if __name__ == "__main__":
    print("======================================================================")
    print("Lab 8: Parallel Swarm -- Multi-Agent Fan-Out & Alignment Merge")
    print("======================================================================")

    # 1. Execute concurrent swarm
    print("Launching 4 specialist agents in parallel via ThreadPoolExecutor...")
    swarm_result = run_grant_swarm("Draft SERB CRG Grant for Retinopathy Screening", ROLES)
    print(f"Execution complete. Wall-clock time: {swarm_result['wall_clock_sec']:.3f}s")
    for role, r in swarm_result["outputs"].items():
        print(f"  [{role}] produced section '{r['output'].get('key')}' ({r['output'].get('word_count')} words)")

    # 2. Alignment Merge against target units
    target_units = ["background", "methodology", "budget", "compliance"]
    merged_plan = merge_by_plan(swarm_result, target_units)
    print("\n=== Plan Alignment Merge ===")
    print(f"All Required Units Covered: {merged_plan['all_covered']}")

    # 3. Conflict Critique & Resolution
    print("\n=== Cross-Agent Conflict Critique ===")
    conflicts = critique_draft(merged_plan)
    conflict_log = []
    for c in conflicts:
        print(f"Detected: {c['conflict']} (between {c['roles_involved']})")
        res = resolve_conflict(c)
        conflict_log.append({**c, **res})
        print(f"  -> Resolution applied: {res['resolution']}")

    # 4. Assignments
    run_assignment_1_fifth_role()
    run_assignment_2_distributed_critique(merged_plan)

    print("\n=== Final Conflict Log (Swarm Report Artifact) ===")
    for log_entry in conflict_log:
        print(f"Conflict: {log_entry['conflict']}")
        print(f"  Rule: {log_entry['rule_applied']}")
        print(f"  Action: {log_entry['resolution']}")
