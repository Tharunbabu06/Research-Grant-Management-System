# ============================================================
# LAB 8 - LANGGRAPH PARALLEL SWARM
# Research Grant Management System
#
# Goal:
#   Locked plan
#       ->
#   Fan-out
#       ->
#   Parallel workers
#       ->
#   Fan-in / Merge
#       ->
#   Best aligned result
#
# LangGraph concepts used:
#   - StateGraph
#   - Shared State
#   - Conditional routing
#   - Send
#   - Reducer
#   - Parallel execution
# ============================================================


from typing import Any, Dict, List, Annotated
from operator import add
from time import perf_counter, sleep

from typing_extensions import TypedDict

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from langgraph.types import Send

from skills.planning_skill import (
    plan,
    lock_plan
)


# ============================================================
# SHARED SWARM STATE
# ============================================================

class SwarmState(TypedDict, total=False):

    # Locked plan
    plan: Dict[str, Any]

    # Work items to distribute
    work_items: List[Dict[str, Any]]

    # One result comes from each worker.
    #
    # 'add' is the reducer.
    # It combines results from parallel branches
    # into one list.
    worker_results: Annotated[
        List[Dict[str, Any]],
        add
    ]

    # Final merged result
    merged_result: Dict[str, Any]

    # Timing information
    parallel_time: float


# ============================================================
# NODE 1 - CREATE LOCKED PLAN
# ============================================================

def create_plan_node(
    state: SwarmState
):

    print("\n" + "=" * 70)
    print("LANGGRAPH NODE: LOCKED PLAN")
    print("=" * 70)

    inputs = {

        "research_area":
            "AI-based cardiovascular monitoring",

        "funding_type":
            "Government research grant"
    }

    created_plan = plan(
        inputs
    )

    locked_plan = lock_plan(
        created_plan
    )

    print(
        "\nResearch Area:",
        locked_plan["research_area"]
    )

    print(
        "Funding Type:",
        locked_plan["funding_type"]
    )

    print(
        "Plan Status:",
        locked_plan["status"]
    )

    return {
        "plan": locked_plan,
        "worker_results": []
    }


# ============================================================
# NODE 2 - CREATE WORK ITEMS
# ============================================================

def create_work_items_node(
    state: SwarmState
):

    print("\n" + "=" * 70)
    print("LANGGRAPH NODE: CREATE WORK ITEMS")
    print("=" * 70)

    work_items = [

        {
            "id": "W001",

            "research_area":
                "AI-based cardiovascular monitoring",

            "funding_type":
                "Government research grant"
        },

        {
            "id": "W002",

            "research_area":
                "Medical artificial intelligence",

            "funding_type":
                "Government research grant"
        },

        {
            "id": "W003",

            "research_area":
                "AI-based biomedical sensing",

            "funding_type":
                "Government research grant"
        }
    ]

    print(
        "\nWork items created:",
        len(work_items)
    )

    for item in work_items:

        print(
            f"{item['id']}: "
            f"{item['research_area']}"
        )

    return {
        "work_items": work_items
    }


# ============================================================
# FAN-OUT ROUTER
# ============================================================

def fan_out_workers(
    state: SwarmState
):
    """
    Create one Send object per work item.

    Each Send creates an independent execution of
    the proposal_worker node.

    This is LangGraph's map/fan-out mechanism.
    """

    sends = []

    for item in state["work_items"]:

        sends.append(

            Send(

                "proposal_worker",

                {
                    "plan":
                        state["plan"],

                    "work_item":
                        item
                }
            )
        )

    print("\n" + "=" * 70)
    print("LANGGRAPH FAN-OUT")
    print("=" * 70)

    print(
        f"\nCreated {len(sends)} parallel worker tasks."
    )

    return sends


# ============================================================
# PARALLEL WORKER
# ============================================================

def proposal_worker(
    state: Dict[str, Any]
):
    """
    Process ONE work item.

    Each invocation receives:
        - the locked plan
        - one work item

    Multiple invocations run in parallel.
    """

    plan_data = state["plan"]

    item = state["work_item"]

    worker_id = item["id"]

    print(
        f"\nWorker {worker_id} started."
    )

    # --------------------------------------------------------
    # Controlled delay
    #
    # This makes parallel execution easy to observe
    # during the lab demonstration.
    # --------------------------------------------------------

    sleep(1)

    research_area = item[
        "research_area"
    ]

    funding_type = item[
        "funding_type"
    ]

    required_area = plan_data[
        "research_area"
    ]

    required_funding = plan_data[
        "funding_type"
    ]

    # --------------------------------------------------------
    # Calculate alignment
    # --------------------------------------------------------

    area_match = (
        research_area.lower()
        ==
        required_area.lower()
    )

    funding_match = (
        funding_type.lower()
        ==
        required_funding.lower()
    )

    alignment_score = 0

    if area_match:
        alignment_score += 1

    if funding_match:
        alignment_score += 1

    # --------------------------------------------------------
    # Create candidate proposal
    # --------------------------------------------------------

    result = {

        "id":
            worker_id,

        "research_area":
            research_area,

        "funding_type":
            funding_type,

        "proposal_title":
            (
                f"Research Proposal on "
                f"{research_area}"
            ),

        "objectives": [

            "Define the research problem",

            "Develop the proposed research approach",

            "Evaluate the proposed methodology"
        ],

        "methodology":
            (
                "Develop the research methodology, "
                "implement the proposed approach, "
                "and evaluate the results."
            ),

        "expected_outcomes": [

            "Research prototype",

            "Evaluation results",

            "Research findings"
        ],

        "alignment_score":
            alignment_score,

        "status":
            "processed"
    }

    print(
        f"Worker {worker_id} completed. "
        f"Alignment = {alignment_score}"
    )

    # Because worker_results has an 'add' reducer,
    # every parallel worker contributes one result.
    return {
        "worker_results": [result]
    }


# ============================================================
# MERGE NODE
# ============================================================

def merge_results_node(
    state: SwarmState
):

    print("\n" + "=" * 70)
    print("LANGGRAPH NODE: MERGE / SELECTOR")
    print("=" * 70)

    results = state.get(
        "worker_results",
        []
    )

    if not results:

        raise ValueError(
            "No parallel worker results received."
        )

    # --------------------------------------------------------
    # Sort according to alignment with locked plan
    # --------------------------------------------------------

    ranked = sorted(

        results,

        key=lambda result:
            result["alignment_score"],

        reverse=True
    )

    selected = ranked[0]

    merged = {

        "selected":
            selected,

        "all_results":
            results,

        "selection_reason":
            (
                "Selected the result with the highest "
                "alignment to the locked plan."
            )
    }

    print(
        "\nParallel results received:",
        len(results)
    )

    print(
        "\nRanked results:"
    )

    for rank, result in enumerate(
        ranked,
        start=1
    ):

        print(
            f"{rank}. "
            f"{result['id']} - "
            f"Alignment: "
            f"{result['alignment_score']}"
        )

    print(
        "\nSelected:",
        selected["id"]
    )

    print(
        "Selected title:",
        selected["proposal_title"]
    )

    print(
        "Selection reason:",
        merged["selection_reason"]
    )

    return {
        "merged_result": merged
    }


# ============================================================
# BUILD LANGGRAPH
# ============================================================

def build_swarm_graph():

    builder = StateGraph(
        SwarmState
    )

    # --------------------------------------------------------
    # Add nodes
    # --------------------------------------------------------

    builder.add_node(
        "create_plan",
        create_plan_node
    )

    builder.add_node(
        "create_work_items",
        create_work_items_node
    )

    builder.add_node(
        "proposal_worker",
        proposal_worker
    )

    builder.add_node(
        "merge_results",
        merge_results_node
    )

    # --------------------------------------------------------
    # Fixed edges
    # --------------------------------------------------------

    builder.add_edge(
        START,
        "create_plan"
    )

    builder.add_edge(
        "create_plan",
        "create_work_items"
    )

    # --------------------------------------------------------
    # Fan-out
    #
    # The router returns multiple Send objects.
    # Each Send runs proposal_worker for one item.
    # --------------------------------------------------------

    builder.add_conditional_edges(
        "create_work_items",
        fan_out_workers
    )

    # --------------------------------------------------------
    # Fan-in
    #
    # All proposal_worker executions update
    # worker_results. The reducer combines them.
    #
    # After all parallel workers finish,
    # LangGraph continues to merge_results.
    # --------------------------------------------------------

    builder.add_edge(
        "proposal_worker",
        "merge_results"
    )

    # --------------------------------------------------------
    # End
    # --------------------------------------------------------

    builder.add_edge(
        "merge_results",
        END
    )

    # --------------------------------------------------------
    # Compile
    # --------------------------------------------------------

    graph = builder.compile()

    return graph