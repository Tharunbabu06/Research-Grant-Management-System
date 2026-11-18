"""
Lab 1: Agent vs Chatbot -- Research Grant Proposal Planner Loop
==============================================================
Domain: Research Grant Management System (Chapter 13 / Lab Guide Lab 1)
Phase: A - Foundations | Goal: Establish the agent loop (clarify -> plan -> revise)

Description:
A planning agent for a faculty member preparing an agency-compliant research grant
proposal. A simple chatbot would answer in one shot with vague advice. An agent:
1. Clarifies missing details first (asking at least two specific questions),
2. Proposes a structured outline plan once requirements are satisfied,
3. Reads existing institutional context,
4. Accepts feedback and mutates the existing plan object rather than regenerating from scratch.

Assignments included:
- Assignment 1: Two independent rounds of feedback mutating the same plan object.
- Assignment 2: Detecting a budget/scope constraint clash before finalizing the plan.
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# ---- Simulated User Inputs (Stand-in for interactive UI or user prompts) ----
SIMULATED_INITIAL_VAGUE_REQUEST = {
    "research_area": "AI for healthcare",
    "funding_type": None,
    "requested_budget": None,
    "duration_months": None,
    "consent": False,
}

SIMULATED_CLARIFICATIONS = {
    "research_area": "Federated learning for diabetic retinopathy screening in rural primary care",
    "funding_type": "government",
    "requested_budget": 5800000,  # 58 Lakh INR
    "duration_months": 36,
    "consent": True,
}

SIMULATED_FEEDBACK_1 = "Include a dedicated Work Package for Clinical Site Validation in year 2."
SIMULATED_FEEDBACK_2 = "Shorten the data curation phase from 6 months to 3 months."


class GrantPlannerAgent:
    """
    Implements the complete Goal -> Plan -> Act -> Observe -> Revise loop
    for the Research Grant Management System.
    """
    def __init__(self, existing_institutional_history: Dict[str, Any]):
        # Goal modeled as structured data -- a checkable predicate, not prose
        self.goal = {
            "research_area": None,
            "funding_type": None,
            "requested_budget": None,
            "duration_months": None,
            "consent": None,
            "plan_generated": False,
        }
        self.institutional_history = existing_institutional_history
        self.plan: Optional[Dict[str, Any]] = None
        self.log: List[Dict[str, Any]] = []

    def satisfied(self) -> bool:
        """Predicate: Is the goal condition met?"""
        return self.goal["plan_generated"] is True

    def next_step(self):
        """Planner: inspect state and decide next action."""
        # 1. Clarification check: ask only for whatever goal field is still missing
        for field_name in ("research_area", "funding_type", "requested_budget", "duration_months", "consent"):
            if self.goal[field_name] is None:
                return ("ask", field_name)
        # 2. Once all inputs exist, generate the plan
        return ("generate_plan", None)

    def read_institutional_history(self) -> Dict[str, Any]:
        """Tool call (Act): inspect prior grant outcomes and lessons learned."""
        result = self.institutional_history
        if "error" in result:
            raise RuntimeError(f"Tool error: {result['error']}")
        return result

    def run(self, user_inputs: Dict[str, Any]):
        """Core agent loop: clarify -> plan -> observe."""
        while not self.satisfied():
            step, arg = self.next_step()

            if step == "ask":
                # Check if provided in initial inputs or simulated answers
                answer = user_inputs.get(arg) or SIMULATED_CLARIFICATIONS.get(arg)
                self.goal[arg] = answer  # Observe: record answer
                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": f"clarify missing requirement '{arg}'",
                    "action": f"asked user for {arg}",
                    "observed": answer,
                    "stopped": False,
                })

            elif step == "generate_plan":
                # Tool call to retrieve past lessons
                history_data = self.read_institutional_history()
                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": "read institutional grant history before generating outline",
                    "action": "tool call: read_institutional_history()",
                    "observed": f"Retrieved {len(history_data.get('prior_grants', []))} past records",
                    "stopped": False,
                })

                # Build the plan object
                self.plan = self._build_plan(history_data)
                self.goal["plan_generated"] = True
                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": "generate structured grant outline from gathered requirements",
                    "action": "built grant proposal and compliance plan",
                    "observed": self.plan["id"],
                    "stopped": True,
                    "stop_reason": "goal.plan_generated is now True",
                })
                return self.plan

    def _build_plan(self, history: Dict[str, Any]) -> Dict[str, Any]:
        """Assembles the initial structured proposal outline."""
        # Incorporate lessons from past grants to avoid repeat mistakes
        past_lessons = []
        for g in history.get("prior_grants", []):
            if "lessons" in g:
                past_lessons.append(g["lessons"])

        return {
            "id": "PLAN-AURA-2026-001",
            "title": f"Grant Package -- {self.goal['research_area']}",
            "funder_domain": self.goal["funding_type"],
            "target_budget": self.goal["requested_budget"],
            "duration_months": self.goal["duration_months"],
            "sections": [
                {"key": "abstract", "title": "Abstract", "min_words": 90},
                {"key": "objectives", "title": "Objectives & Specific Aims", "min_words": 90},
                {"key": "background", "title": "Background & State of the Art", "min_words": 130},
                {"key": "methodology", "title": "Methodology & Work Packages", "min_words": 160},
                {"key": "timeline", "title": "Work Plan & Milestones", "min_words": 100},
                {"key": "data_management", "title": "Data Management & Ethics", "min_words": 110},
                {"key": "budget_justification", "title": "Budget Justification", "min_words": 80},
                {"key": "references", "title": "References", "min_words": 30},
            ],
            "work_packages": [
                {"id": "WP1", "name": "Data Curation & De-identification", "duration_months": 6},
                {"id": "WP2", "name": "Federated Learning Model Architecture", "duration_months": 18},
                {"id": "WP3", "name": "Multi-Clinic Evaluation & Dissemination", "duration_months": 12},
            ],
            "incorporated_lessons": past_lessons,
        }

    def revise(self, feedback: str) -> Dict[str, Any]:
        """
        Revise on user feedback by mutating existing self.plan object.
        CRITICAL: Does NOT recreate plan from scratch.
        """
        self.log.append({
            "iteration": len(self.log) + 1,
            "planned": "apply user feedback to existing plan",
            "action": f"feedback received: '{feedback}'",
            "observed": None,
            "stopped": False,
        })

        # Apply specific mutations based on feedback
        fb = feedback.lower()
        if "clinical site validation" in fb:
            self.plan["work_packages"].append({
                "id": f"WP{len(self.plan['work_packages']) + 1}",
                "name": "Clinical Site Validation",
                "duration_months": 12,
            })
            self.log.append({
                "iteration": len(self.log) + 1,
                "planned": "confirm revised plan (added WP for Clinical Site Validation)",
                "action": "mutated existing plan.work_packages (not regenerated from scratch)",
                "observed": [wp["name"] for wp in self.plan["work_packages"]],
                "stopped": True,
                "stop_reason": "revision applied without restarting loop",
            })

        elif "shorten" in fb and "data curation" in fb:
            for wp in self.plan["work_packages"]:
                if "Data Curation" in wp["name"]:
                    wp["duration_months"] = 3
            self.log.append({
                "iteration": len(self.log) + 1,
                "planned": "confirm revised plan (shortened data curation duration)",
                "action": "mutated existing plan.work_packages duration to 3 months",
                "observed": self.plan["work_packages"][0],
                "stopped": True,
                "stop_reason": "revision applied without restarting loop",
            })

        return self.plan


# ==============================================================================
# Graded Assignments
# ==============================================================================

def run_assignment_1_two_rounds_of_feedback(agent: GrantPlannerAgent):
    """
    Assignment 1 -- Two Rounds of Feedback:
    Demonstrate that two independent rounds of feedback mutate the exact same
    in-memory plan object without restarting the planner loop.
    """
    print("\n--- [Assignment 1] Round 1 Feedback ---")
    revised_1 = agent.revise(SIMULATED_FEEDBACK_1)
    print(f"Work packages after Round 1: {[wp['name'] for wp in revised_1['work_packages']]}")

    print("\n--- [Assignment 1] Round 2 Feedback ---")
    revised_2 = agent.revise(SIMULATED_FEEDBACK_2)
    print(f"Data curation duration after Round 2: {revised_2['work_packages'][0]['duration_months']} months")
    assert id(revised_1) == id(revised_2), "Plan object identity must be preserved across revisions!"
    print("Verification passed: Both rounds mutated the same plan instance.")


def run_assignment_2_detect_conflict(existing_history: Dict[str, Any]):
    """
    Assignment 2 -- Detect a Scheduling / Budget Conflict:
    If requested budget exceeds the maximum institutional limit or agency ceiling
    found in history, flag the conflict to the user rather than silently accepting it.
    """
    print("\n--- [Assignment 2] Detect Constraint Conflict ---")
    conflict_agent = GrantPlannerAgent(existing_history)
    excessive_inputs = {
        "research_area": "Quantum AI for Drug Discovery",
        "funding_type": "government",
        "requested_budget": 15000000,  # 1.5 Cr (Above typical SERB CRG 75L ceiling)
        "duration_months": 36,
        "consent": True,
    }

    # Pre-generation constraint check
    max_agency_ceiling = 7500000  # 75 Lakh INR
    if excessive_inputs["requested_budget"] > max_agency_ceiling:
        conflict_msg = (
            f"CONFLICT DETECTED: Requested budget INR {excessive_inputs['requested_budget']:,} "
            f"exceeds standard agency ceiling of INR {max_agency_ceiling:,}. "
            f"Flagging for budget de-scoping before plan lock."
        )
        print(f"Pre-flight Check: {conflict_msg}")
        return conflict_msg
    return "No conflict"


# ==============================================================================
# Main Demonstration
# ==============================================================================

if __name__ == "__main__":
    print("======================================================================")
    print("Lab 1: Agent vs Chatbot -- Research Grant Management System Planner")
    print("======================================================================")

    # 1. Mock Institutional Prior Grant History
    mock_history = {
        "prior_grants": [
            {
                "id": "hist-fl-2023",
                "title": "Federated learning testbed for medical imaging",
                "lessons": "Clinical validation was out of scope in phase 1; must be explicit in follow-up proposals.",
            }
        ]
    }

    # 2. Instantiate Agent
    agent = GrantPlannerAgent(existing_institutional_history=mock_history)
    print("Stopping condition declared before loop runs:")
    print("  goal['plan_generated'] is True\n")

    # 3. Run Loop with initially vague request (simulating clarify step)
    print("=== Step 1: Initial Run with Vague Inputs ===")
    plan = agent.run(user_inputs=SIMULATED_INITIAL_VAGUE_REQUEST)
    print("Initial Plan Generated:")
    print(json.dumps(plan, indent=2))

    # 4. Assignment 1: Two rounds of feedback
    run_assignment_1_two_rounds_of_feedback(agent)

    # 5. Assignment 2: Constraint clash detection
    run_assignment_2_detect_conflict(mock_history)

    # 6. Display full iteration log
    print("\n=== Full Agent Iteration Log ===")
    for entry in agent.log:
        print(json.dumps(entry, indent=2))
