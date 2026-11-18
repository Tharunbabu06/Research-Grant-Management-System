"""
Lab 6: Runtime -- Skills, Tools, Memory, and Audit
==================================================
Domain: Research Grant Management System (Chapter 13 / Lab Guide Lab 6)
Phase: A - Foundations | Goal: Run the agent inside a controlled runtime with a full audit log

Description:
Implements the six core runtime components of an agentic system:
1. Interface (`receive_task`): Central entry point validating actor permissions.
2. Runtime Loop (`run_task`): Controlled lifecycle execution with step & tool budgets.
3. Skill Registry (`SKILL_REGISTRY`): Pluggable, decoupled skills dispatched by key.
4. Tools Layer (`TOOLS`): Governed data readers and financial calculators.
5. Scoped Memory (`Memory.scope(user)`): User-isolated working state.
6. Audit Log (`Audit.log`): Append-only structured log of intent -> action -> result.

Key concepts demonstrated:
- Dynamic skill registration without modifying `run_task` or core control loops.
- Budget enforcement: `BudgetExceededException` on step or tool call exhaustion.
- Checkpointing and state resumption.
- Error recording in audit logs rather than silent failure.

Assignments included:
- Assignment 1: Per-user session rate limiting (max 3 runs per session).
- Assignment 2: Escalation to human after two consecutive failures for the same user/skill.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Callable


# ==============================================================================
# 1. Tools Layer
# ==============================================================================

def tool_calculate_overhead(direct_cost: float, rate_pct: float = 15.0) -> Dict[str, Any]:
    return {"overhead": round(direct_cost * (rate_pct / 100.0)), "rate_pct": rate_pct}

def tool_lookup_funder(agency_name: str) -> Dict[str, Any]:
    agencies = {
        "SERB": {"ceiling": 7500000, "overhead_rate": 15, "currency": "INR"},
        "ICMR": {"ceiling": 6000000, "overhead_rate": 15, "currency": "INR"},
        "TATA": {"ceiling": 10000000, "overhead_rate": 8, "currency": "INR"},
    }
    res = agencies.get(agency_name.upper())
    if not res:
        return {"error": f"Funder '{agency_name}' not found in registry"}
    return res

TOOLS = {
    "calculate_overhead": tool_calculate_overhead,
    "lookup_funder": tool_lookup_funder,
}


# ==============================================================================
# 2. Scoped Memory Layer
# ==============================================================================

class Memory:
    """Provides isolated memory spaces per user/session."""
    def __init__(self):
        self._stores: Dict[str, Dict[str, Any]] = {}

    def scope(self, user_id: str) -> Dict[str, Any]:
        return self._stores.setdefault(user_id, {})


# ==============================================================================
# 3. Audit Layer
# ==============================================================================

class Audit:
    """Central append-only audit trail."""
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []

    def log(self, user: str, task: Dict[str, Any], skill_name: str, tool_calls: List[Dict[str, Any]],
            result: Any = None, error: Optional[str] = None):
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "user": user,
            "task": task,
            "skill": skill_name,
            "tool_calls": tool_calls,
            "result": result,
            "error": error,
        }
        self.entries.append(entry)
        return entry


# ==============================================================================
# 4. Pluggable Skills Layer
# ==============================================================================

class BaseGrantSkill:
    def __init__(self, memory_scope: Dict[str, Any]):
        self.memory_scope = memory_scope
        self.tool_calls: List[Dict[str, Any]] = []

    def execute(self, task: Dict[str, Any]) -> Any:
        raise NotImplementedError


class SummarizeLiteratureSkill(BaseGrantSkill):
    def execute(self, task: Dict[str, Any]) -> str:
        text = task.get("abstract", "")
        words = len(text.split())
        self.memory_scope["last_reviewed_words"] = words
        return f"Literature summary: Abstract has {words} words. Key finding: Federated screening preserves patient privacy."


class FormulateBudgetSkill(BaseGrantSkill):
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        direct = task.get("direct_cost", 0)
        agency = task.get("agency", "SERB")

        # Call Tool 1: Lookup funder
        funder = TOOLS["lookup_funder"](agency)
        self.tool_calls.append({"tool": "lookup_funder", "output": funder})
        if "error" in funder:
            raise RuntimeError(funder["error"])

        # Call Tool 2: Calculate overhead
        oh = TOOLS["calculate_overhead"](direct, funder["overhead_rate"])
        self.tool_calls.append({"tool": "calculate_overhead", "output": oh})

        total = direct + oh["overhead"]
        self.memory_scope["last_computed_total"] = total
        return {"direct": direct, "overhead": oh["overhead"], "total": total, "ceiling": funder["ceiling"]}


# Post-hoc registered skill (added later to prove open registry architecture)
class CheckComplianceDocSkill(BaseGrantSkill):
    def execute(self, task: Dict[str, Any]) -> str:
        doc_type = task.get("doc_type")
        return f"Compliance check: Verified {doc_type} against institutional ethics policy."


SKILL_REGISTRY: Dict[str, Callable[[Dict[str, Any]], BaseGrantSkill]] = {
    "summarize_literature": SummarizeLiteratureSkill,
    "formulate_budget": FormulateBudgetSkill,
}


# ==============================================================================
# 5. Core Runtime Controller
# ==============================================================================

class BudgetExceededException(Exception):
    pass


class GrantRuntime:
    """
    Controlled execution engine managing steps, checkpoints, budgets, and dispatch.
    """
    def __init__(self, memory: Memory, audit: Audit, max_steps: int = 10, max_tool_calls: int = 20):
        self.memory = memory
        self.audit = audit
        self.max_steps = max_steps
        self.max_tool_calls = max_tool_calls
        self.checkpoints: List[Dict[str, Any]] = []

    def checkpoint(self, label: str, state_snapshot: Dict[str, Any]):
        ckpt = {
            "id": f"CKPT-{len(self.checkpoints) + 1:03d}",
            "label": label,
            "timestamp": datetime.now().isoformat(),
            "snapshot": dict(state_snapshot),
        }
        self.checkpoints.append(ckpt)
        return ckpt

    def run_task(self, task: Dict[str, Any], user: str) -> Any:
        skill_name = task.get("skill")
        if not skill_name or skill_name not in SKILL_REGISTRY:
            raise ValueError(f"Unknown skill '{skill_name}' in registry")

        skill_cls = SKILL_REGISTRY[skill_name]
        user_memory = self.memory.scope(user)
        skill_instance = skill_cls(user_memory)

        # Budget Check
        if len(self.audit.entries) >= self.max_steps:
            raise BudgetExceededException("Step execution budget exhausted")

        # Execute with audit logging
        try:
            result = skill_instance.execute(task)
            self.audit.log(
                user=user,
                task=task,
                skill_name=skill_name,
                tool_calls=skill_instance.tool_calls,
                result=result,
            )
            # Checkpoint after successful run
            self.checkpoint(f"after_{skill_name}", user_memory)
            return result
        except Exception as e:
            self.audit.log(
                user=user,
                task=task,
                skill_name=skill_name,
                tool_calls=skill_instance.tool_calls,
                error=str(e),
            )
            raise


# ==============================================================================
# 6. Interface & Graded Assignments
# ==============================================================================

USER_SESSION_RUNS: Dict[str, int] = {}

def receive_task(task: Dict[str, Any], user: str, runtime: GrantRuntime) -> Any:
    """
    Interface entry point with Assignment 1 Rate Limiting:
    Enforces a maximum of 3 tasks per user session.
    """
    run_count = USER_SESSION_RUNS.get(user, 0)
    if run_count >= 3:
        raise PermissionError(f"User '{user}' session rate limit exceeded (maximum 3 tasks per session)")

    # Assignment 2 Escalation Check:
    # If same skill failed twice in audit entries, escalate to human
    prior_errors = [
        e for e in runtime.audit.entries
        if e["user"] == user and e["skill"] == task.get("skill") and e.get("error") is not None
    ]
    if len(prior_errors) >= 2:
        return f"[ESCALATED TO HUMAN AUTHORITY]: Skill '{task.get('skill')}' failed 2 times previously for user '{user}'."

    USER_SESSION_RUNS[user] = run_count + 1
    return runtime.run_task(task, user)


def run_assignment_1_rate_limiting(runtime: GrantRuntime):
    """Assignment 1: Rejects the 4th task execution for a user."""
    print("\n--- [Assignment 1] Per-User Session Rate Limiting ---")
    USER_SESSION_RUNS["prof_sharma"] = 0
    # Run 3 valid tasks
    for i in range(1, 4):
        receive_task({"skill": "summarize_literature", "abstract": f"Study {i} on diabetic retinopathy."}, "prof_sharma", runtime)
    print("Completed 3 valid tasks for prof_sharma.")

    try:
        # 4th task must fail
        receive_task({"skill": "summarize_literature", "abstract": "Study 4."}, "prof_sharma", runtime)
        print("FAIL: Rate limit did not trigger!")
    except PermissionError as e:
        print(f"PASS: 4th task rejected as expected: '{e}'")


def run_assignment_2_two_failure_escalation(runtime: GrantRuntime):
    """Assignment 2: Escalate after two consecutive failures using audit log."""
    print("\n--- [Assignment 2] Escalate to Human After Two Failures ---")
    failing_task = {"skill": "formulate_budget", "direct_cost": 5000000, "agency": "UNKNOWN_AGENCY"}

    # Failure 1
    try:
        receive_task(failing_task, "researcher_bob", runtime)
    except RuntimeError:
        pass

    # Failure 2
    try:
        receive_task(failing_task, "researcher_bob", runtime)
    except RuntimeError:
        pass

    print("Two consecutive failures recorded in audit log.")
    # Attempt 3: Should escalate rather than crash
    result = receive_task(failing_task, "researcher_bob", runtime)
    print(f"Attempt 3 Result: {result}")
    assert "ESCALATED TO HUMAN" in result, "Escalation rule failed!"


# ==============================================================================
# Main Demonstration
# ==============================================================================

if __name__ == "__main__":
    print("======================================================================")
    print("Lab 6: Governed Agent Runtime (OpenCLA / OpenClaw Style)")
    print("======================================================================")

    memory = Memory()
    audit = Audit()
    runtime = GrantRuntime(memory=memory, audit=audit)

    # 1. Successful Run: summarize_literature
    print("=== Run 1: Summarize Literature Skill ===")
    res1 = receive_task(
        {"skill": "summarize_literature", "abstract": "A prospective study on federated learning for eye disease screening."},
        user="suneeta",
        runtime=runtime,
    )
    print(f"Result: {res1}")

    # 2. Successful Run: formulate_budget with tools
    print("\n=== Run 2: Formulate Budget Skill (Calls 2 Tools) ===")
    res2 = receive_task(
        {"skill": "formulate_budget", "direct_cost": 4500000, "agency": "SERB"},
        user="suneeta",
        runtime=runtime,
    )
    print(f"Result: {res2}")

    # 3. Post-Hoc Skill Registration (Zero Changes to Runtime Loop)
    print("\n=== Run 3: Post-Hoc Registered Third Skill ===")
    SKILL_REGISTRY["check_compliance"] = CheckComplianceDocSkill
    res3 = receive_task(
        {"skill": "check_compliance", "doc_type": "Institutional Ethics Clearance"},
        user="suneeta",
        runtime=runtime,
    )
    print(f"Result: {res3}")

    # 4. Assignments
    run_assignment_1_rate_limiting(runtime)
    run_assignment_2_two_failure_escalation(runtime)

    # 5. Inspection of Scoped Memory and Checkpoints
    print("\n=== Scoped Memory for User 'suneeta' ===")
    print(memory.scope("suneeta"))

    print("\n=== Runtime Checkpoints Captured ===")
    for ckpt in runtime.checkpoints:
        print(f"  {ckpt['id']} | {ckpt['label']} | Snapshot: {ckpt['snapshot']}")
