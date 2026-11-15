from pathlib import Path
import sys
SUPPORT = Path(__file__).resolve().parents[1] / "Course-Project" / "code" / "Lab_Support"
sys.path.insert(0, str(SUPPORT))

# ============================================================
# LAB 6 - RUNTIME
# Research Grant Management System
#
# Integrates:
#   Lab 3 -> Skills
#   Lab 4 -> Memory
#   Lab 5 -> Connector
#
# Adds:
#   Runtime
#   Budget
#   Audit
#   Checkpoint
#   Resume
#   Approval gate
# ============================================================


from runtime.runtime_controller import Runtime


from skills.planning_skill import (
    plan,
    lock_plan
)

from skills.formatting_skill import (
    format_grant
)

from memory.session_state import (
    SessionState
)

from connector.client import (
    read_funding_calls,
    read_budget_data,
    read_compliance_rules
)


# ============================================================
# COORDINATOR
# ============================================================

class Coordinator:

    def __init__(self, runtime):

        self.runtime = runtime

        # -----------------------------------------------
        # Lab 4 short-term memory
        # -----------------------------------------------

        self.session = SessionState()

    # --------------------------------------------------------
    # STEP 1 - PLANNING SKILL
    # --------------------------------------------------------

    def create_plan(self):

        inputs = {
            "research_area":
                "AI-based cardiovascular monitoring",

            "funding_type":
                "Government research grant"
        }

        def action():

            draft_plan = plan(inputs)

            locked_plan = lock_plan(
                draft_plan
            )

            self.session.set_plan(
                locked_plan
            )

            self.runtime.set_state(
                "plan",
                locked_plan
            )

            return locked_plan

        return self.runtime.run_step(
            intent="Create grant blueprint",
            action_name="planning_skill",
            action=action,
            input_data=inputs
        )

    # --------------------------------------------------------
    # STEP 2 - CONNECTOR: FUNDING
    # --------------------------------------------------------

    def read_funding_calls(self):

        def action():

            data = read_funding_calls()

            self.runtime.set_state(
                "funding_calls",
                data
            )

            return data

        return self.runtime.run_step(
            intent="Read funding calls and guidelines",
            action_name="read_funding_calls",
            action=action
        )

    # --------------------------------------------------------
    # STEP 3 - CONNECTOR: BUDGET
    # --------------------------------------------------------

    def read_budget_data(self):

        def action():

            data = read_budget_data()

            self.runtime.set_state(
                "budget_data",
                data
            )

            return data

        return self.runtime.run_step(
            intent="Read budget and personnel data",
            action_name="read_budget_data",
            action=action
        )

    # --------------------------------------------------------
    # STEP 4 - CONNECTOR: COMPLIANCE
    # --------------------------------------------------------

    def read_compliance_rules(self):

        def action():

            data = read_compliance_rules()

            self.runtime.set_state(
                "compliance_rules",
                data
            )

            return data

        return self.runtime.run_step(
            intent="Read compliance rules",
            action_name="read_compliance_rules",
            action=action
        )

    # --------------------------------------------------------
    # STEP 5 - FORMATTING SKILL
    # --------------------------------------------------------

    def create_document_shell(self):

        template = [
            "Research Area",
            "Funding Type",
            "Abstract",
            "Objectives",
            "Methodology",
            "Timeline",
            "Expected Outcomes",
            "Budget",
            "Compliance"
        ]

        def action():

            document = format_grant(
                self.session.current_plan,
                template
            )

            self.session.set_draft(
                document
            )

            self.runtime.set_state(
                "draft",
                document
            )

            return document

        return self.runtime.run_step(
            intent="Create grant document shell",
            action_name="format_grant",
            action=action
        )

    # --------------------------------------------------------
    # STEP 6 - CONTROLLED PUBLISH GATE
    # --------------------------------------------------------

    def publish_demo(self):

        def action():

            result = {
                "status": "published_demo",
                "message":
                    "Demo publish action approved."
            }

            self.runtime.set_state(
                "publish_status",
                result
            )

            return result

        return self.runtime.run_step(
            intent="Execute governed publish action",
            action_name="publish",
            action=action,
            risky=True
        )


# ============================================================
# LAB 6 EXECUTION
# ============================================================

def run_lab6():

    print("\n" + "=" * 70)
    print("RESEARCH GRANT MANAGEMENT SYSTEM")
    print("LAB 6 - CONTROLLED RUNTIME")
    print("=" * 70)

    # --------------------------------------------------------
    # CREATE RUNTIME
    # --------------------------------------------------------

    runtime = Runtime(
        budget=10,
        gates=["publish"]
    )

    coordinator = Coordinator(
        runtime
    )

    # --------------------------------------------------------
    # STEP 1 - SKILL
    # --------------------------------------------------------

    coordinator.create_plan()

    # --------------------------------------------------------
    # STEP 2 - CONNECTOR
    # --------------------------------------------------------

    coordinator.read_funding_calls()

    # --------------------------------------------------------
    # STEP 3 - CONNECTOR
    # --------------------------------------------------------

    coordinator.read_budget_data()

    # --------------------------------------------------------
    # STEP 4 - CONNECTOR
    # --------------------------------------------------------

    coordinator.read_compliance_rules()

    # --------------------------------------------------------
    # STEP 5 - SKILL
    # --------------------------------------------------------

    coordinator.create_document_shell()

    # --------------------------------------------------------
    # DISPLAY CHECKPOINT
    # --------------------------------------------------------

    runtime.show_checkpoint()

    # --------------------------------------------------------
    # DEMONSTRATE RESUME
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("RESUME TEST")
    print("=" * 70)

    resumed_runtime = Runtime(
        budget=10,
        gates=["publish"]
    )

    resumed_runtime.resume()

    # --------------------------------------------------------
    # SHOW AUDIT
    # --------------------------------------------------------

    resumed_runtime.show_audit()

    # --------------------------------------------------------
    # OPTIONAL APPROVAL GATE
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("APPROVAL GATE TEST")
    print("=" * 70)

    print(
        "\nThe next action is protected by the "
        "publish approval gate."
    )

    choice = input(
        "\nTest the publish gate? (yes/no): "
    ).strip().lower()

    if choice in ["yes", "y"]:

        try:

            # Use the original runtime because
            # it contains the coordinator's state.

            coordinator.publish_demo()

        except PermissionError as error:

            print(
                f"\nPublish blocked: {error}"
            )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("LAB 6 RESULT")
    print("=" * 70)

    print(
        "\nRuntime successfully demonstrated:"
    )

    print("1. Controlled execution")

    print("2. Runtime action budget")

    print("3. Input/output audit logging")

    print("4. Checkpoint creation")

    print("5. Resume from checkpoint")

    print("6. Approval gate for risky action")

    print(
        "\nLab 6 runtime test completed."
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_lab6()