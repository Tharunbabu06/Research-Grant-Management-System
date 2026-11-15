from pathlib import Path
import sys
SUPPORT = Path(__file__).resolve().parents[1] / "Course-Project" / "code" / "Lab_Support"
sys.path.insert(0, str(SUPPORT))

# ============================================================
# LAB 7 - LANGGRAPH EXECUTION
# Research Grant Management System
# ============================================================


from graph.langgraph_grant import (
    build_grant_graph
)


# ============================================================
# RUN LAB 7
# ============================================================

def run_lab7():

    print("\n" + "=" * 70)
    print("RESEARCH GRANT MANAGEMENT SYSTEM")
    print("LAB 7 - LANGGRAPH AGENTIC NODE GRAPH")
    print("=" * 70)

    # --------------------------------------------------------
    # BUILD LANGGRAPH
    # --------------------------------------------------------

    graph = build_grant_graph()

    print("\nLangGraph compiled successfully.")

    # --------------------------------------------------------
    # REQUEST
    # --------------------------------------------------------

    request = {

        "research_area":
            "AI-based cardiovascular monitoring",

        "funding_type":
            "Government research grant"
    }

    # --------------------------------------------------------
    # INVOKE GRAPH
    # --------------------------------------------------------

    result = graph.invoke(
        {
            "request": request
        }
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("LAB 7 RESULT")
    print("=" * 70)

    print(
        "\nFunding calls:",
        len(
            result.get(
                "funding_calls",
                []
            )
        )
    )

    print(
        "Literature records:",
        len(
            result.get(
                "literature",
                []
            )
        )
    )

    print(
        "Proposal created:",
        bool(
            result.get(
                "proposal"
            )
        )
    )

    budget = result.get(
        "budget",
        {}
    )

    print(
        "Budget total:",
        f"₹{budget.get('total', 0):,.2f}"
    )

    compliance = result.get(
        "compliance",
        {}
    )

    print(
        "Compliance:",
        compliance.get(
            "status",
            "unknown"
        )
    )

    print(
        "Validation:",
        "PASS"
        if result.get(
            "validation_passed",
            False
        )
        else "FAIL"
    )

    print(
        "Retry attempts:",
        result.get(
            "retry_count",
            0
        )
    )

    print(
        "Human review status:",
        result.get(
            "human_review_status",
            "not available"
        )
    )

    print("\n" + "=" * 70)
    print("LAB 7 COMPLETED USING LANGGRAPH")
    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_lab7()