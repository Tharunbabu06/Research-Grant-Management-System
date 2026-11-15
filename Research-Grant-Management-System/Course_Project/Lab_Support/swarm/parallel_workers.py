# ============================================================
# LAB 8 - PARALLEL SWARM
# Research Grant Management System
#
# Purpose:
#   Process multiple proposal/grant work items in parallel
#   and merge the results according to the locked plan.
# ============================================================

from concurrent.futures import ThreadPoolExecutor


# ============================================================
# PROCESS ONE WORK ITEM
# ============================================================

def process_proposal(item, plan):
    """
    Process one proposal work item.

    Args:
        item: Proposal/grant work item
        plan: Locked plan

    Returns:
        Processed result
    """

    research_area = item["research_area"]
    funding_type = item["funding_type"]

    # Create result according to the locked plan.

    result = {
        "id": item["id"],

        "research_area": research_area,

        "funding_type": funding_type,

        "proposal_title":
            f"Research Proposal on {research_area}",

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

        "status": "processed"
    }

    # --------------------------------------------------------
    # Alignment to locked plan
    # --------------------------------------------------------

    required_area = plan["research_area"]

    required_funding_type = plan["funding_type"]

    area_match = (
        research_area.lower()
        ==
        required_area.lower()
    )

    funding_match = (
        funding_type.lower()
        ==
        required_funding_type.lower()
    )

    alignment_score = 0

    if area_match:
        alignment_score += 1

    if funding_match:
        alignment_score += 1

    result["alignment_score"] = alignment_score

    return result


# ============================================================
# PARALLEL FAN-OUT
# ============================================================

def parallel_process(items, plan):
    """
    Process multiple work items in parallel.
    """

    with ThreadPoolExecutor(
        max_workers=len(items)
    ) as executor:

        futures = [
            executor.submit(
                process_proposal,
                item,
                plan
            )
            for item in items
        ]

        results = [
            future.result()
            for future in futures
        ]

    return results


# ============================================================
# MERGE / SELECTOR
# ============================================================

def merge_results(results, plan):
    """
    Merge parallel results.

    Selection is based on alignment to the locked plan,
    not on which output simply looks nicer.
    """

    if not results:
        return None

    aligned_results = sorted(
        results,
        key=lambda result:
            result["alignment_score"],
        reverse=True
    )

    selected = aligned_results[0]

    merged_output = {
        "selected": selected,

        "all_results": results,

        "selection_reason":
            "Selected according to alignment "
            "with the locked plan."
    }

    return merged_output