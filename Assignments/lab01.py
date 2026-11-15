from pathlib import Path
import sys
SUPPORT = Path(__file__).resolve().parents[1] / "Course-Project" / "code" / "Lab_Support"
sys.path.insert(0, str(SUPPORT))

# ============================================================
# LAB 1 - AGENT VS CHATBOT
# Research Grant Management System
#
# Goal:
#   Clarify -> Plan -> Revise
#
# Based strictly on the Lab 1 requirements in the Build Book.
#
# Lab 1 contains:
#   1. Free-text user request
#   2. Clarification questions
#   3. Structured grant proposal + compliance package plan
#   4. User feedback
#   5. Plan revision
#
# No API
# No LLM
# No tools
# No database
# No memory
# No specialist agents
# ============================================================


# ============================================================
# 1. COORDINATOR
# ============================================================

class Coordinator:
    """
    Lab 1 Coordinator.

    The Coordinator is responsible for:
        - Clarifying the user's request
        - Creating a structured plan
        - Revising the plan using user feedback
    """

    def __init__(self):
        self.user_request = ""
        self.clarified_request = {}
        self.plan = {}

    # --------------------------------------------------------
    # STEP 1: RECEIVE USER REQUEST
    # --------------------------------------------------------

    def receive_request(self):
        print("\n" + "=" * 70)
        print("RESEARCH GRANT MANAGEMENT SYSTEM")
        print("LAB 1 - AGENT VS CHATBOT")
        print("=" * 70)

        print("\nEnter your grant-related request.")
        print("Example:")
        print("I want to prepare a research grant proposal for healthcare AI.")

        while True:
            request = input("\nUser Request:\n> ").strip()

            if request:
                self.user_request = request
                return request

            print("Request cannot be empty. Please enter a request.")

    # --------------------------------------------------------
    # STEP 2: CLARIFY REQUEST
    # --------------------------------------------------------

    def clarify_request(self):
        print("\n" + "=" * 70)
        print("COORDINATOR - CLARIFYING REQUEST")
        print("=" * 70)

        print("\nInitial request:")
        print(self.user_request)

        print(
            "\nThe request does not contain all the information "
            "needed to create the grant plan."
        )

        # Question 1
        while True:
            research_area = input(
                "\nClarifying Question 1:\n"
                "What research area should the grant proposal focus on?\n"
                "> "
            ).strip()

            if research_area:
                self.clarified_request["research_area"] = research_area
                break

            print("Please provide a research area.")

        # Question 2
        while True:
            funding_type = input(
                "\nClarifying Question 2:\n"
                "What type of funding opportunity are you targeting?\n"
                "Example: Government / Industry / International\n"
                "> "
            ).strip()

            if funding_type:
                self.clarified_request["funding_type"] = funding_type
                break

            print("Please provide a funding type.")

        # Question 3
        while True:
            consent = input(
                "\nClarifying Question 3:\n"
                "Do you consent to using your profile/publication history "
                "for grant matching? (yes/no)\n"
                "> "
            ).strip().lower()

            if consent in ["yes", "y"]:
                self.clarified_request["publication_consent"] = True
                break

            if consent in ["no", "n"]:
                self.clarified_request["publication_consent"] = False
                break

            print("Please enter yes or no.")

        print("\nRequest clarification completed.")

        return self.clarified_request

    # --------------------------------------------------------
    # STEP 3: PROPOSE PLAN
    # --------------------------------------------------------

    def propose_plan(self):
        """
        Create an editable outline plan.

        This is a PLAN only.
        It does not actually perform funding discovery,
        literature review, budgeting, compliance checking,
        or submission.
        """

        self.plan = {
            "user_request": self.user_request,

            "research_area":
                self.clarified_request["research_area"],

            "funding_type":
                self.clarified_request["funding_type"],

            "publication_consent":
                self.clarified_request["publication_consent"],

            "proposal_outline": [
                "Define the research problem",
                "Prepare research objectives",
                "Prepare methodology",
                "Prepare project timeline",
                "Prepare expected outcomes"
            ],

            "compliance_outline": [
                "Identify applicable proposal requirements",
                "Prepare required supporting information",
                "Review the proposal against the requirements"
            ],

            "final_output":
                "Grant proposal and compliance package"
        }

        return self.plan

    # --------------------------------------------------------
    # STEP 4: DISPLAY PLAN
    # --------------------------------------------------------

    def display_plan(self, title="PROPOSED PLAN"):
        print("\n" + "=" * 70)
        print(title)
        print("=" * 70)

        print("\nOriginal Request:")
        print(self.plan["user_request"])

        print("\nResearch Area:")
        print(self.plan["research_area"])

        print("\nFunding Type:")
        print(self.plan["funding_type"])

        print("\nPublication History Consent:")
        print(
            "Yes"
            if self.plan["publication_consent"]
            else "No"
        )

        print("\nGrant Proposal Outline:")

        for number, step in enumerate(
            self.plan["proposal_outline"],
            start=1
        ):
            print(f"  {number}. {step}")

        print("\nCompliance Package Outline:")

        for number, step in enumerate(
            self.plan["compliance_outline"],
            start=1
        ):
            print(f"  {number}. {step}")

        print("\nFinal Planned Output:")
        print(self.plan["final_output"])

        print("=" * 70)

    # --------------------------------------------------------
    # STEP 5: REVISE PLAN
    # --------------------------------------------------------

    def revise_plan(self):
        """
        Revise the plan according to user feedback.
        """

        while True:

            print("\n" + "=" * 70)
            print("PLAN REVISION")
            print("=" * 70)

            choice = input(
                "\nWould you like to revise the plan? (yes/no)\n"
                "> "
            ).strip().lower()

            if choice in ["no", "n"]:
                print("\nNo further changes requested.")
                return self.plan

            if choice not in ["yes", "y"]:
                print("Please enter yes or no.")
                continue

            print("\nWhat would you like to change?")

            print("1. Research area")
            print("2. Funding type")
            print("3. Publication-history consent")
            print("4. Add a proposal step")
            print("5. Remove a proposal step")
            print("6. Add a compliance step")
            print("7. Remove a compliance step")

            option = input("\nChoose an option (1-7): ").strip()

            # ------------------------------------------------
            # CHANGE RESEARCH AREA
            # ------------------------------------------------

            if option == "1":

                new_area = input(
                    "\nEnter the new research area:\n> "
                ).strip()

                if new_area:
                    self.plan["research_area"] = new_area
                    print("\nResearch area updated.")

                else:
                    print("\nResearch area cannot be empty.")

            # ------------------------------------------------
            # CHANGE FUNDING TYPE
            # ------------------------------------------------

            elif option == "2":

                new_type = input(
                    "\nEnter the new funding type:\n"
                    "Example: Government / Industry / International\n"
                    "> "
                ).strip()

                if new_type:
                    self.plan["funding_type"] = new_type
                    print("\nFunding type updated.")

                else:
                    print("\nFunding type cannot be empty.")

            # ------------------------------------------------
            # CHANGE CONSENT
            # ------------------------------------------------

            elif option == "3":

                while True:

                    new_consent = input(
                        "\nUse publication history for matching? "
                        "(yes/no)\n> "
                    ).strip().lower()

                    if new_consent in ["yes", "y"]:

                        self.plan["publication_consent"] = True
                        print("\nConsent updated to Yes.")
                        break

                    elif new_consent in ["no", "n"]:

                        self.plan["publication_consent"] = False
                        print("\nConsent updated to No.")
                        break

                    else:
                        print("Please enter yes or no.")

            # ------------------------------------------------
            # ADD PROPOSAL STEP
            # ------------------------------------------------

            elif option == "4":

                new_step = input(
                    "\nEnter the proposal step to add:\n> "
                ).strip()

                if new_step:

                    self.plan["proposal_outline"].append(
                        new_step
                    )

                    print("\nProposal step added.")

                else:
                    print("\nStep cannot be empty.")

            # ------------------------------------------------
            # REMOVE PROPOSAL STEP
            # ------------------------------------------------

            elif option == "5":

                if not self.plan["proposal_outline"]:

                    print("\nNo proposal steps available.")
                    continue

                print("\nCurrent Proposal Steps:")

                for number, step in enumerate(
                    self.plan["proposal_outline"],
                    start=1
                ):
                    print(f"{number}. {step}")

                try:

                    remove_number = int(
                        input(
                            "\nEnter the number to remove:\n> "
                        ).strip()
                    )

                    if 1 <= remove_number <= len(
                        self.plan["proposal_outline"]
                    ):

                        removed = self.plan[
                            "proposal_outline"
                        ].pop(remove_number - 1)

                        print(
                            f"\nRemoved proposal step: {removed}"
                        )

                    else:
                        print("\nInvalid step number.")

                except ValueError:
                    print("\nPlease enter a valid number.")

            # ------------------------------------------------
            # ADD COMPLIANCE STEP
            # ------------------------------------------------

            elif option == "6":

                new_step = input(
                    "\nEnter the compliance step to add:\n> "
                ).strip()

                if new_step:

                    self.plan["compliance_outline"].append(
                        new_step
                    )

                    print("\nCompliance step added.")

                else:
                    print("\nStep cannot be empty.")

            # ------------------------------------------------
            # REMOVE COMPLIANCE STEP
            # ------------------------------------------------

            elif option == "7":

                if not self.plan["compliance_outline"]:

                    print("\nNo compliance steps available.")
                    continue

                print("\nCurrent Compliance Steps:")

                for number, step in enumerate(
                    self.plan["compliance_outline"],
                    start=1
                ):
                    print(f"{number}. {step}")

                try:

                    remove_number = int(
                        input(
                            "\nEnter the number to remove:\n> "
                        ).strip()
                    )

                    if 1 <= remove_number <= len(
                        self.plan["compliance_outline"]
                    ):

                        removed = self.plan[
                            "compliance_outline"
                        ].pop(remove_number - 1)

                        print(
                            f"\nRemoved compliance step: {removed}"
                        )

                    else:
                        print("\nInvalid step number.")

                except ValueError:
                    print("\nPlease enter a valid number.")

            else:

                print("\nInvalid option.")

                continue

            # ---------------------------------------------
            # SHOW UPDATED PLAN AFTER EVERY CHANGE
            # ---------------------------------------------

            self.display_plan("UPDATED PLAN")


# ============================================================
# MAIN LAB 1 EXECUTION
# ============================================================

def run_lab1():

    coordinator = Coordinator()

    # --------------------------------------------------------
    # STEP 1 - RECEIVE FREE-TEXT REQUEST
    # --------------------------------------------------------

    coordinator.receive_request()

    # --------------------------------------------------------
    # STEP 2 - CLARIFY
    # --------------------------------------------------------

    coordinator.clarify_request()

    # --------------------------------------------------------
    # STEP 3 - CREATE PLAN
    # --------------------------------------------------------

    coordinator.propose_plan()

    # --------------------------------------------------------
    # STEP 4 - DISPLAY PLAN
    # --------------------------------------------------------

    coordinator.display_plan("PROPOSED GRANT PLAN")

    # --------------------------------------------------------
    # STEP 5 - REVISE PLAN
    # --------------------------------------------------------

    coordinator.revise_plan()

    # --------------------------------------------------------
    # STEP 6 - FINAL PLAN
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL EDITABLE GRANT PLAN")
    print("=" * 70)

    coordinator.display_plan("FINAL PLAN")

    print("\nLab 1 completed successfully.")
    print("The Coordinator completed:")
    print("  1. Clarification")
    print("  2. Planning")
    print("  3. Revision")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_lab1()