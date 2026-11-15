from pathlib import Path
import sys
SUPPORT = Path(__file__).resolve().parents[1] / "Course_Project" / "Lab_Support"
sys.path.insert(0, str(SUPPORT))

# ============================================================
# LAB 3 - SKILL CREATION
# Research Grant Management System
#
# Goal:
#   Create reusable:
#       1. Planning Skill
#       2. Formatting Skill
#
# ============================================================


from skills.planning_skill import (
    plan,
    lock_plan
)

from skills.formatting_skill import (
    format_grant
)


# ============================================================
# COORDINATOR
# ============================================================

class Coordinator:
    """
    Coordinator for Lab 3.

    The Coordinator uses reusable skills instead of
    keeping planning and formatting logic directly
    inside the main program.
    """

    def __init__(self):
        self.plan = None
        self.document = None

    # --------------------------------------------------------
    # STEP 1 - USE PLANNING SKILL
    # --------------------------------------------------------

    def create_plan(self, inputs):

        print("\n" + "=" * 70)
        print("PLANNING SKILL")
        print("=" * 70)

        print("\nCreating plan using reusable skill...")

        draft_plan = plan(inputs)

        self.plan = lock_plan(draft_plan)

        print("\nPlan created and locked.")

        return self.plan

    # --------------------------------------------------------
    # STEP 2 - DISPLAY PLAN
    # --------------------------------------------------------

    def display_plan(self):

        print("\n" + "=" * 70)
        print("LOCKED PLAN")
        print("=" * 70)

        print(
            "\nResearch Area:",
            self.plan["research_area"]
        )

        print(
            "Funding Type:",
            self.plan["funding_type"]
        )

        print(
            "Plan Status:",
            self.plan["status"]
        )

        print("\nProposal Outline:")

        for number, item in enumerate(
            self.plan["proposal_outline"],
            start=1
        ):
            print(f"{number}. {item}")

        print("\nCompliance Outline:")

        for number, item in enumerate(
            self.plan["compliance_outline"],
            start=1
        ):
            print(f"{number}. {item}")

    # --------------------------------------------------------
    # STEP 3 - USE FORMATTING SKILL
    # --------------------------------------------------------

    def format_document(self):

        print("\n" + "=" * 70)
        print("FORMATTING SKILL")
        print("=" * 70)

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

        self.document = format_grant(
            self.plan,
            template
        )

        print("\nGrant document shell created.")

        return self.document

    # --------------------------------------------------------
    # STEP 4 - DISPLAY DOCUMENT
    # --------------------------------------------------------

    def display_document(self):

        print("\n" + "=" * 70)
        print("FORMATTED GRANT DOCUMENT")
        print("=" * 70)

        print(
            "\nTitle:",
            self.document["title"]
        )

        print(
            "Status:",
            self.document["status"]
        )

        print("\nSections:")

        for number, section in enumerate(
            self.document["sections"],
            start=1
        ):

            print(
                f"{number}. "
                f"{section['section']}"
            )

            if section["content"]:

                print(
                    f"   Content: "
                    f"{section['content']}"
                )


# ============================================================
# CASE 1
# ============================================================

def run_case_1():

    print("\n" + "=" * 70)
    print("CASE 1")
    print("=" * 70)

    inputs = {
        "research_area":
            "AI-based cardiovascular monitoring",

        "funding_type":
            "Government research grant"
    }

    coordinator = Coordinator()

    coordinator.create_plan(inputs)

    coordinator.display_plan()

    coordinator.format_document()

    coordinator.display_document()


# ============================================================
# CASE 2
# ============================================================

def run_case_2():

    print("\n" + "=" * 70)
    print("CASE 2")
    print("=" * 70)

    inputs = {
        "research_area":
            "AI-based agricultural disease detection",

        "funding_type":
            "Government research grant"
    }

    coordinator = Coordinator()

    coordinator.create_plan(inputs)

    coordinator.display_plan()

    coordinator.format_document()

    coordinator.display_document()


# ============================================================
# MAIN LAB 3
# ============================================================

def run_lab3():

    print("\n" + "=" * 70)
    print("RESEARCH GRANT MANAGEMENT SYSTEM")
    print("LAB 3 - REUSABLE SKILLS")
    print("=" * 70)

    print("\nTesting Skill Reusability...")

    # --------------------------------------------------------
    # TEST CASE 1
    # --------------------------------------------------------

    run_case_1()

    # --------------------------------------------------------
    # TEST CASE 2
    # --------------------------------------------------------

    run_case_2()

    print("\n" + "=" * 70)
    print("LAB 3 COMPLETED")
    print("=" * 70)

    print("\nTwo different cases were processed")
    print("using the same planning skill.")
    print("Two different cases were formatted")
    print("using the same formatting skill.")

    print("\nSkill reuse test completed successfully.")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_lab3()