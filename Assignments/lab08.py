from pathlib import Path
import sys
SUPPORT = Path(__file__).resolve().parents[1] / "Course-Project" / "code" / "Lab_Support"
sys.path.insert(0, str(SUPPORT))

# ============================================================
# LAB 8 - LANGGRAPH PARALLEL SWARM
# Research Grant Management System
# ============================================================


from time import perf_counter

from graph.langgraph_swarm import (
    build_swarm_graph
)


# ============================================================
# MAIN LAB 8
# ============================================================

def run_lab8():

    print("\n" + "=" * 70)
    print("RESEARCH GRANT MANAGEMENT SYSTEM")
    print("LAB 8 - LANGGRAPH PARALLEL SWARM")
    print("=" * 70)

    # --------------------------------------------------------
    # BUILD GRAPH
    # --------------------------------------------------------

    graph = build_swarm_graph()

    print(
        "\nLangGraph swarm compiled successfully."
    )

    # --------------------------------------------------------
    # START TIME
    # --------------------------------------------------------

    start_time = perf_counter()

    # --------------------------------------------------------
    # RUN GRAPH
    # --------------------------------------------------------

    result = graph.invoke({})

    # --------------------------------------------------------
    # END TIME
    # --------------------------------------------------------

    end_time = perf_counter()

    elapsed_time = (
        end_time - start_time
    )

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    worker_results = result.get(
        "worker_results",
        []
    )

    merged_result = result.get(
        "merged_result",
        {}
    )

    selected = merged_result.get(
        "selected",
        {}
    )

    print("\n" + "=" * 70)
    print("LAB 8 RESULT")
    print("=" * 70)

    print(
        "\nTotal work items:",
        len(
            result.get(
                "work_items",
                []
            )
        )
    )

    print(
        "Parallel worker results:",
        len(worker_results)
    )

    print(
        "Selected result:",
        selected.get(
            "id",
            "None"
        )
    )

    print(
        "Selected research area:",
        selected.get(
            "research_area",
            "None"
        )
    )

    print(
        "Selected alignment score:",
        selected.get(
            "alignment_score",
            "None"
        )
    )

    print(
        f"Parallel execution time: "
        f"{elapsed_time:.2f} seconds"
    )

    print(
        "\nSelection method:"
    )

    print(
        merged_result.get(
            "selection_reason",
            "Not available"
        )
    )

    # --------------------------------------------------------
    # ACCEPTANCE CHECKS
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("LAB 8 ACCEPTANCE CHECKS")
    print("=" * 70)

    total_items = len(
        result.get(
            "work_items",
            []
        )
    )

    check_1 = (
        total_items == 3
    )

    check_2 = (
        len(worker_results)
        ==
        total_items
    )

    check_3 = (
        bool(selected)
    )

    check_4 = (
        selected.get(
            "alignment_score",
            0
        )
        ==
        max(
            worker["alignment_score"]
            for worker in worker_results
        )
    )

    print(
        "Three work items:",
        "PASS" if check_1 else "FAIL"
    )

    print(
        "All workers returned results:",
        "PASS" if check_2 else "FAIL"
    )

    print(
        "Merge selected a result:",
        "PASS" if check_3 else "FAIL"
    )

    print(
        "Selection uses highest plan alignment:",
        "PASS" if check_4 else "FAIL"
    )

    # --------------------------------------------------------
    # FINAL
    # --------------------------------------------------------

    all_passed = all([
        check_1,
        check_2,
        check_3,
        check_4
    ])

    print("\n" + "=" * 70)

    if all_passed:

        print(
            "LAB 8 COMPLETED USING LANGGRAPH"
        )

    else:

        print(
            "LAB 8 ACCEPTANCE TEST FAILED"
        )

    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_lab8()