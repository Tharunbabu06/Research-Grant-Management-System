# ============================================================
# LAB 3 - PLANNING SKILL
# Reusable Plan / Blueprint Skill
# ============================================================


def plan(inputs):
    """
    Create a structured grant plan from input data.

    Input:
        Dictionary containing grant request information.

    Output:
        Structured Plan dictionary.

    The skill is case-agnostic.
    The input values can change without changing the code.
    """

    if not isinstance(inputs, dict):
        raise TypeError("inputs must be a dictionary")

    required_fields = [
        "research_area",
        "funding_type"
    ]

    for field in required_fields:
        if field not in inputs:
            raise ValueError(
                f"Missing required input: {field}"
            )

    proposal_outline = [
        "Define the research problem",
        "Prepare research objectives",
        "Prepare methodology",
        "Prepare project timeline",
        "Prepare expected outcomes"
    ]

    compliance_outline = [
        "Identify applicable proposal requirements",
        "Prepare required supporting information",
        "Review the proposal against the requirements"
    ]

    result = {
        "research_area": inputs["research_area"],
        "funding_type": inputs["funding_type"],
        "proposal_outline": proposal_outline,
        "compliance_outline": compliance_outline,
        "final_output": (
            "Grant proposal and compliance package"
        ),
        "status": "draft"
    }

    return result


def lock_plan(plan_result):
    """
    Lock the plan so that it becomes the blueprint
    for later processing.
    """

    if not isinstance(plan_result, dict):
        raise TypeError("plan_result must be a dictionary")

    plan_result["status"] = "locked"

    return plan_result