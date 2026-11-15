from pathlib import Path
import sys
SUPPORT = Path(__file__).resolve().parents[1] / "Course_Project" / "Lab_Support"
sys.path.insert(0, str(SUPPORT))

# ============================================================
# LAB 5 - MCP-STYLE CONNECTOR
# Research Grant Management System
#
# Goal:
#   Verify that all data access happens through
#   one governed connector.
# ============================================================


from connector.client import (
    read_funding_calls,
    read_budget_data,
    read_compliance_rules
)


# ============================================================
# COORDINATOR
# ============================================================

class Coordinator:

    """
    Lab 5 Coordinator.

    The Coordinator DOES NOT read JSON files directly.

    All data access goes through the connector.
    """

    def __init__(self):

        self.funding_calls = []
        self.budget_data = {}
        self.compliance_rules = {}

    # --------------------------------------------------------
    # FUNDING CALLS
    # --------------------------------------------------------

    def get_funding_calls(self):

        print("\n" + "=" * 70)
        print("CONNECTOR -> FUNDING CALLS & GUIDELINES")
        print("=" * 70)

        self.funding_calls = read_funding_calls()

        print(
            f"\nFunding calls received: "
            f"{len(self.funding_calls)}"
        )

        for call in self.funding_calls:

            print("\nAgency:")
            print(call["agency"])

            print("Call:")
            print(call["call_title"])

            print("Deadline:")
            print(call["deadline"])

            print("Budget Ceiling:")
            print(
                f"₹{call['budget_ceiling']:,.2f}"
            )

        return self.funding_calls

    # --------------------------------------------------------
    # BUDGET DATA
    # --------------------------------------------------------

    def get_budget_data(self):

        print("\n" + "=" * 70)
        print("CONNECTOR -> BUDGET & PERSONNEL DATA")
        print("=" * 70)

        self.budget_data = read_budget_data()

        for category, amount in self.budget_data.items():

            print(
                f"{category}: "
                f"₹{amount:,.2f}"
            )

        return self.budget_data

    # --------------------------------------------------------
    # COMPLIANCE RULES
    # --------------------------------------------------------

    def get_compliance_rules(self):

        print("\n" + "=" * 70)
        print("CONNECTOR -> COMPLIANCE RULES")
        print("=" * 70)

        self.compliance_rules = (
            read_compliance_rules()
        )

        for rule in self.compliance_rules["rules"]:

            print(
                f"{rule['id']}: "
                f"{rule['rule']}"
            )

        return self.compliance_rules

    # --------------------------------------------------------
    # SHOW CONNECTOR USAGE
    # --------------------------------------------------------

    def show_connector_architecture(self):

        print("\n" + "=" * 70)
        print("GOVERNED DATA ACCESS")
        print("=" * 70)

        print(
            "\nCoordinator / Agents"
        )

        print(
            "        |"
        )

        print(
            "        v"
        )

        print(
            "Connector Client"
        )

        print(
            "        |"
        )

        print(
            "        v"
        )

        print(
            "Connector Server"
        )

        print(
            "        |"
        )

        print(
            "   +----+----+-------------+"
        )

        print(
            "   |         |             |"
        )

        print(
            "   v         v             v"
        )

        print(
            "Funding   Budget      Compliance"
        )

        print(
            "Calls     Data        Rules"
        )


# ============================================================
# LAB 5 EXECUTION
# ============================================================

def run_lab5():

    print("\n" + "=" * 70)
    print("RESEARCH GRANT MANAGEMENT SYSTEM")
    print("LAB 5 - MCP-STYLE CONNECTOR")
    print("=" * 70)

    coordinator = Coordinator()

    # --------------------------------------------------------
    # ALL DATA ACCESS THROUGH CONNECTOR
    # --------------------------------------------------------

    coordinator.get_funding_calls()

    coordinator.get_budget_data()

    coordinator.get_compliance_rules()

    # --------------------------------------------------------
    # SHOW ARCHITECTURE
    # --------------------------------------------------------

    coordinator.show_connector_architecture()

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("LAB 5 RESULT")
    print("=" * 70)

    print(
        "\nFunding data accessed through connector."
    )

    print(
        "Budget/personnel data accessed through connector."
    )

    print(
        "Compliance rules accessed through connector."
    )

    print(
        "\nAll three data sources use one "
        "governed connector surface."
    )

    print("\nLab 5 connector test completed.")


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_lab5()