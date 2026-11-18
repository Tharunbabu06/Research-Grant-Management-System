"""
Lab 2: Tool-Using Agent -- Call Data & Compute
==============================================
Domain: Research Grant Management System (Chapter 13 / Lab Guide Lab 2)
Phase: A - Foundations | Goal: Give the agent tools it must call to act, rather than answering from memory

Description:
A grant budget and data assistant that never invents numbers or policies from memory.
It must execute through structured, typed tools:
1. `read_funding_calls`: Reads published agency calls and their guideline constraints.
2. `compute_budget`: Performs precise arithmetic for direct costs, overheads, contingency, and totals.
3. `cap_report`: Audits category percentages (manpower, equipment, travel) against agency limits.
4. `check_eligibility`: Validates PI career stage and institution type against agency requirements.

Key concepts demonstrated:
- Strict tool contracts (structured inputs and typed dict outputs with result or explicit error).
- Single choke point `_call()` logging tool name, reason, input, and output.
- LangChain `@tool` / `StructuredTool` compatibility wrapper.
- Graceful error handling (honest reporting when records do not exist).

Assignments included:
- Assignment 1: Notification drafting tool (`draft_budget_alert`) with justified use when caps breach.
- Assignment 2: Three-tool chain: read call -> compute budget -> evaluate caps with non-empty validation.
"""

import json
from typing import Dict, Any, List, Optional
from seed_data import CALLS, PERSONNEL, RATE_CARD


# ==============================================================================
# Core Typed Tool Implementations
# ==============================================================================

def read_funding_call(call_id: str) -> Dict[str, Any]:
    """Tool: Reads an agency call and its guidelines from the database."""
    for call in CALLS:
        if call["id"] == call_id:
            return {"result": call}
    return {"error": f"Funding call '{call_id}' not found in verified registry"}


def read_personnel_rate(role: str) -> Dict[str, Any]:
    """Tool: Reads standard salary/rate card for research staff."""
    for person in PERSONNEL:
        if person["role"].lower() == role.lower():
            return {
                "result": {
                    "role": person["role"],
                    "monthlyCost": person.get("monthlyCost", 0),
                    "title": person.get("title", ""),
                }
            }
    return {"error": f"No standard rate found for staff role '{role}'"}


def compute_budget(lines: List[Dict[str, Any]], rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Tool: Performs exact financial arithmetic. Never done in LLM prose.
    Computes direct costs, overhead, contingency, and final total.
    """
    if not lines:
        return {"error": "No budget lines provided"}

    rules = rules or {}
    overhead_pct = float(rules.get("overheadPct", RATE_CARD["overheadPct"]))
    contingency_pct = float(rules.get("contingencyPct", RATE_CARD["contingencyPct"]))

    category_sums = {"personnel": 0, "equipment": 0, "consumables": 0, "travel": 0}
    for line in lines:
        cat = line.get("category", "consumables").lower()
        amt = float(line.get("amount", 0))
        if cat in category_sums:
            category_sums[cat] += amt
        else:
            category_sums["consumables"] += amt

    direct = sum(category_sums.values())
    overhead = round((direct * overhead_pct) / 100.0)
    contingency = round((direct * contingency_pct) / 100.0)
    total = direct + overhead + contingency

    return {
        "result": {
            "categories": category_sums,
            "direct": direct,
            "overhead": overhead,
            "overheadPct": overhead_pct,
            "contingency": contingency,
            "contingencyPct": contingency_pct,
            "total": total,
            "lineCount": len(lines),
        }
    }


def cap_report(lines: List[Dict[str, Any]], rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: Verifies category amounts against agency percentage ceilings.
    """
    b_res = compute_budget(lines, rules)
    if "error" in b_res:
        return b_res

    budget = b_res["result"]
    total = budget["total"]
    if total <= 0:
        return {"error": "Budget total is zero or negative"}

    caps = [
        {"key": "salary", "label": "Manpower", "category": "personnel", "capPct": float(rules.get("salaryCapPct", 100))},
        {"key": "equipment", "label": "Equipment", "category": "equipment", "capPct": float(rules.get("equipmentCapPct", 100))},
        {"key": "travel", "label": "Travel", "category": "travel", "capPct": float(rules.get("travelCapPct", 100))},
    ]

    report = []
    any_breach = False
    for c in caps:
        amt = budget["categories"].get(c["category"], 0)
        actual_pct = round((amt / total) * 100.0, 1)
        limit_amt = round((c["capPct"] / 100.0) * total)
        status = "over" if actual_pct > (c["capPct"] + 0.05) else "ok"
        if status == "over":
            any_breach = True
        report.append({
            "key": c["key"],
            "label": c["label"],
            "amount": amt,
            "actualPct": actual_pct,
            "capPct": c["capPct"],
            "limitAmount": limit_amt,
            "status": status,
        })

    return {"result": {"caps": report, "anyBreach": any_breach}}


def check_eligibility(call_id: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool: Checks career stage and institutional eligibility.
    """
    call_res = read_funding_call(call_id)
    if "error" in call_res:
        return call_res

    call = call_res["result"]
    elig = call.get("eligibility", {})
    career_stages = elig.get("careerStages", [])
    inst_types = elig.get("institutionTypes", [])

    pi_stage = profile.get("careerStage", "associate")
    inst_type = profile.get("institutionType", "university")

    stage_ok = pi_stage in career_stages
    inst_ok = inst_type in inst_types

    return {
        "result": {
            "eligible": stage_ok and inst_ok,
            "checks": [
                {"field": "careerStage", "candidate": pi_stage, "allowed": career_stages, "pass": stage_ok},
                {"field": "institutionType", "candidate": inst_type, "allowed": inst_types, "pass": inst_ok},
            ]
        }
    }


# ==============================================================================
# LangChain Tool Compatibility Adapter
# (Demonstrates how these tools seamlessly wrap into LangChain format)
# ==============================================================================

class LangChainToolAdapter:
    """
    Adapter demonstrating standard LangChain BaseTool / StructuredTool pattern
    without requiring third-party library installation.
    """
    def __init__(self, name: str, description: str, func, args_schema: Optional[Dict] = None):
        self.name = name
        self.description = description
        self.func = func
        self.args_schema = args_schema or {}

    def run(self, **kwargs):
        return self.func(**kwargs)

    def to_langchain_definition(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.args_schema,
        }


# ==============================================================================
# Agent Implementation with Single Choke Point
# ==============================================================================

TOOLS = {
    "read_funding_call": read_funding_call,
    "read_personnel_rate": read_personnel_rate,
    "compute_budget": compute_budget,
    "cap_report": cap_report,
    "check_eligibility": check_eligibility,
}

class GrantDataAssistant:
    def __init__(self):
        self.trace: List[Dict[str, Any]] = []

    def _call(self, tool_name: str, reason: str, **kwargs) -> Any:
        """
        The single choke point through which every tool invocation passes.
        Logs inputs, outputs, timestamps, and asserts output validity.
        """
        if tool_name not in TOOLS:
            raise ValueError(f"Unknown tool '{tool_name}'")

        result = TOOLS[tool_name](**kwargs)
        entry = {
            "tool": tool_name,
            "reason": reason,
            "input": kwargs,
            "output": result,
        }
        self.trace.append(entry)

        if "error" in result:
            raise RuntimeError(f"Tool '{tool_name}' failed: {result['error']}")
        return result["result"]

    def answer_question(self, question: str) -> str:
        """Processes questions requiring traceable tool execution."""
        q = question.lower()

        # Question 1: Budget computation
        if "budget" in q and "total" in q:
            # Sample proposed budget items from faculty
            sample_lines = [
                {"category": "personnel", "item": "Research Associate (3 yrs)", "amount": 1728000},
                {"category": "equipment", "item": "GPU Workstation", "amount": 1800000},
                {"category": "consumables", "item": "Data Storage & APIs", "amount": 600000},
                {"category": "travel", "item": "Clinic Visits", "amount": 400000},
            ]
            computed = self._call(
                "compute_budget",
                "Faculty submitted 4 budget lines; calculating total direct cost and statutory overhead",
                lines=sample_lines,
                rules={"overheadPct": 15, "contingencyPct": 5},
            )
            return (
                f"Computed Budget: Direct = INR {computed['direct']:,}, "
                f"Overhead (15%) = INR {computed['overhead']:,}, "
                f"Contingency (5%) = INR {computed['contingency']:,}, "
                f"Grand Total = INR {computed['total']:,}."
            )

        # Question 2: Funding Call Lookup
        if "guideline" in q or "serb" in q:
            call_data = self._call(
                "read_funding_call",
                "Looking up published guidelines and ceilings for SERB CRG call",
                call_id="call-serb-crg",
            )
            return (
                f"Call '{call_data['title']}' has ceiling INR {call_data['budgetMax']:,} "
                f"and deadline {call_data['deadline']}."
            )

        # Question 3: Graceful failure path
        if "non-existent" in q or "missing" in q:
            try:
                self._call(
                    "read_funding_call",
                    "Attempting lookup of unverified agency identifier",
                    call_id="call-fake-999",
                )
            except RuntimeError as e:
                return f"Graceful failure reported: {e}"

        return "I do not have a configured tool path for that question."


# ==============================================================================
# Graded Assignments
# ==============================================================================

def notification_tool(recipient: str, alert_message: str) -> Dict[str, Any]:
    """Assignment 1 Tool: Drafts a notification without external side effects."""
    return {
        "result": {
            "draft_id": "ALERT-001",
            "to": recipient,
            "message": alert_message,
            "status": "DRAFTED_NOT_SENT",
        }
    }

TOOLS["send_notification"] = notification_tool


def run_assignment_1_notification(assistant: GrantDataAssistant):
    """
    Assignment 1 -- Add Notification Tool with Justified Use:
    When equipment exceeds the agency cap, call send_notification to draft an alert.
    """
    print("\n--- [Assignment 1] Add Notification Tool with Justified Use ---")
    breaching_lines = [
        {"category": "personnel", "item": "RA", "amount": 1000000},
        {"category": "equipment", "item": "Supercomputer Cluster", "amount": 4500000},  # Breaches 40% cap
        {"category": "consumables", "item": "Reagents", "amount": 500000},
    ]
    caps = assistant._call(
        "cap_report",
        "Evaluating category percentages against SERB CRG limits",
        lines=breaching_lines,
        rules={"salaryCapPct": 45, "equipmentCapPct": 40, "travelCapPct": 10},
    )

    if caps["anyBreach"]:
        equip_cap = next(c for c in caps["caps"] if c["key"] == "equipment")
        alert = assistant._call(
            "send_notification",
            f"Equipment allocation ({equip_cap['actualPct']}%) exceeds {equip_cap['capPct']}% ceiling; drafting warning for PI",
            recipient="suneeta.v.budihal@mist.edu.in",
            alert_message=f"Equipment cost of INR {equip_cap['amount']:,} exceeds agency ceiling.",
        )
        print(f"Notification drafted successfully: {alert}")


def run_assignment_2_three_tool_chain(assistant: GrantDataAssistant):
    """
    Assignment 2 -- A Three-Tool Chain:
    1. Read funding call
    2. Check PI eligibility
    3. Calculate budget against call ceiling and caps
    """
    print("\n--- [Assignment 2] Three-Tool Chain Execution ---")
    # Step 1: Read call
    call = assistant._call(
        "read_funding_call",
        "Step 1: Fetching ICMR Ad-hoc call parameters",
        call_id="call-icmr-adhoc",
    )
    # Step 2: Check eligibility
    elig = assistant._call(
        "check_eligibility",
        "Step 2: Checking associate professor eligibility against ICMR requirements",
        call_id="call-icmr-adhoc",
        profile={"careerStage": "associate", "institutionType": "university"},
    )
    # Step 3: Compute budget using call-specific overhead rules
    budget_lines = [
        {"category": "personnel", "amount": 2000000},
        {"category": "equipment", "amount": 1500000},
        {"category": "consumables", "amount": 500000},
    ]
    budget = assistant._call(
        "compute_budget",
        "Step 3: Calculating total cost using call's 15% overhead rule",
        lines=budget_lines,
        rules=call["budgetRules"],
    )
    print(f"3-Tool Chain Result: Call = {call['id']}, Eligible = {elig['eligible']}, Total = INR {budget['total']:,}")


# ==============================================================================
# Main Demonstration
# ==============================================================================

if __name__ == "__main__":
    print("======================================================================")
    print("Lab 2: Tool-Using Agent -- Call Data & Compute")
    print("======================================================================")

    assistant = GrantDataAssistant()

    q1 = "What is the total budget for the proposed items?"
    print(f"\nQ: {q1}")
    print(f"A: {assistant.answer_question(q1)}")

    q2 = "What are the guidelines for SERB CRG?"
    print(f"\nQ: {q2}")
    print(f"A: {assistant.answer_question(q2)}")

    q3 = "Check status of non-existent call call-fake-999"
    print(f"\nQ: {q3}")
    print(f"A: {assistant.answer_question(q3)}")

    # Run assignments
    run_assignment_1_notification(assistant)
    run_assignment_2_three_tool_chain(assistant)

    # Full execution trace
    print("\n=== Full Tool Call Trace ===")
    for i, t in enumerate(assistant.trace, 1):
        print(f"{i}. tool={t['tool']} | reason=\"{t['reason']}\"")
        print(f"   input: {t['input']}")
        print(f"   output: {t['output']}")
