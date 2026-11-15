# ============================================================
# LAB 3 - FORMATTING SKILL
# Reusable Grant Proposal Formatting Skill
# ============================================================


def format_grant(result, template):
    """
    Format a grant proposal and compliance package
    using a supplied template.

    Input:
        result   -> grant plan/result
        template -> template specification

    Output:
        formatted document
    """

    if not isinstance(result, dict):
        raise TypeError("result must be a dictionary")

    if not isinstance(template, list):
        raise TypeError(
            "template must be a list of sections"
        )

    document = {
        "title": "Grant Proposal and Compliance Package",
        "status": "draft",
        "sections": []
    }

    for section in template:

        section_data = {
            "section": section,
            "content": ""
        }

        # Fill known information from the plan.
        if section == "Research Area":
            section_data["content"] = result.get(
                "research_area",
                ""
            )

        elif section == "Funding Type":
            section_data["content"] = result.get(
                "funding_type",
                ""
            )

        document["sections"].append(section_data)

    return document