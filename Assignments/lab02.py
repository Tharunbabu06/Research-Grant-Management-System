from pathlib import Path
import sys
SUPPORT = Path(__file__).resolve().parents[1] / "Course-Project" / "code" / "Lab_Support"
sys.path.insert(0, str(SUPPORT))

from tools.grant_tools import (
    read_funding_calls,
    read_budget_data,
    compute_budget,
    validate_budget
)


# ============================================================
# LAB 2 - TOOL USING AGENT
# ============================================================

class Coordinator:
    """
    Lab 2 Coordinator.

    The Coordinator now uses typed tools to:
        1. Read funding calls
        2. Read budget data
        3. Compute budget
        4. Validate budget
    """

    def __init__(self):
        self.funding_calls = []
        self.budget_data = {}
        self.budget_result = {}
        self.validation_result = {}

    # --------------------------------------------------------
    # STEP 1 - READ FUNDING CALLS USING TOOL
    # --------------------------------------------------------

    def get_funding_information(self):

        print("\n" + "=" * 70)
        print("TOOL 1 - READING FUNDING CALLS")
        print("=" * 70)

        self.funding_calls = read_funding_calls()

        print(f"\nFunding calls found: {len(self.funding_calls)}")

        for call in self.funding_calls:

            print("\nAgency:", call["agency"])
            print("Call:", call["call_title"])
            print("Deadline:", call["deadline"])
            print("Funding Type:", call["funding_type"])
            print("Budget Ceiling:", call["budget_ceiling"])

        return self.funding_calls

    # --------------------------------------------------------
    # STEP 2 - READ BUDGET DATA USING TOOL
    # --------------------------------------------------------

    def get_budget_information(self):

        print("\n" + "=" * 70)
        print("TOOL 2 - READING BUDGET DATA")
        print("=" * 70)

        self.budget_data = read_budget_data()

        for category, amount in self.budget_data.items():

            print(f"{category}: ₹{amount:,.2f}")

        return self.budget_data

    # --------------------------------------------------------
    # STEP 3 - COMPUTE USING TOOL
    # --------------------------------------------------------

    def calculate_budget(self):

        print("\n" + "=" * 70)
        print("TOOL 3 - COMPUTING BUDGET")
        print("=" * 70)

        self.budget_result = compute_budget(
            self.budget_data
        )

        print(
            f"\nCalculated Total: "
            f"₹{self.budget_result['total']:,.2f}"
        )

        return self.budget_result

    # --------------------------------------------------------
    # STEP 4 - VALIDATE USING TOOL
    # --------------------------------------------------------

    def validate_budget(self):

        print("\n" + "=" * 70)
        print("TOOL 4 - VALIDATING BUDGET")
        print("=" * 70)

        # For Lab 2 we use the first funding call
        # from our controlled demo dataset.

        budget_ceiling = self.funding_calls[0][
            "budget_ceiling"
        ]

        total = self.budget_result["total"]

        self.validation_result = validate_budget(
            total,
            budget_ceiling
        )

        print(
            f"\nBudget Total: "
            f"₹{self.validation_result['total']:,.2f}"
        )

        print(
            f"Budget Ceiling: "
            f"₹{self.validation_result['budget_ceiling']:,.2f}"
        )

        if self.validation_result["valid"]:

            print("\nSTATUS: VALID")
            print("Budget is within the allowed ceiling.")

        else:

            print("\nSTATUS: INVALID")
            print("Budget exceeds the allowed ceiling.")

        return self.validation_result


# ============================================================
# MAIN LAB 2
# ============================================================

def run_lab2():

    print("\n" + "=" * 70)
    print("RESEARCH GRANT MANAGEMENT SYSTEM")
    print("LAB 2 - TOOL-USING AGENT")
    print("=" * 70)

    coordinator = Coordinator()

    # --------------------------------------------------------
    # TOOL 1
    # --------------------------------------------------------

    coordinator.get_funding_information()

    # --------------------------------------------------------
    # TOOL 2
    # --------------------------------------------------------

    coordinator.get_budget_information()

    # --------------------------------------------------------
    # TOOL 3
    # --------------------------------------------------------

    coordinator.calculate_budget()

    # --------------------------------------------------------
    # TOOL 4
    # --------------------------------------------------------

    coordinator.validate_budget()

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("LAB 2 RESULT")
    print("=" * 70)

    print(
        "\nFunding calls successfully retrieved using tool."
    )

    print(
        "Budget data successfully retrieved using tool."
    )

    print(
        "Budget successfully calculated using tool."
    )

    print(
        "Budget successfully validated using tool."
    )

    print("\nLab 2 tool execution completed.")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_lab2()