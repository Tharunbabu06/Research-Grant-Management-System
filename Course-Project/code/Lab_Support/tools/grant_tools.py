import json
from pathlib import Path


# ============================================================
# DATA PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FUNDING_FILE = BASE_DIR / "data" / "funding_calls.json"
BUDGET_FILE = BASE_DIR / "data" / "budget_data.json"


# ============================================================
# TOOL 1 - READ FUNDING CALLS
# ============================================================

def read_funding_calls():
    """
    Read funding calls and guidelines from the data source.

    Returns:
        list: Funding call records
    """

    with open(FUNDING_FILE, "r", encoding="utf-8") as file:
        funding_calls = json.load(file)

    return funding_calls


# ============================================================
# TOOL 2 - READ BUDGET DATA
# ============================================================

def read_budget_data():
    """
    Read budget and personnel information.

    Returns:
        dict: Budget information
    """

    with open(BUDGET_FILE, "r", encoding="utf-8") as file:
        budget_data = json.load(file)

    return budget_data


# ============================================================
# TOOL 3 - COMPUTE BUDGET
# ============================================================

def compute_budget(budget_data):
    """
    Calculate the total budget from individual categories.

    Args:
        budget_data (dict): Budget categories and values

    Returns:
        dict: Computed budget result
    """

    total = sum(budget_data.values())

    return {
        "total": total,
        "currency": "INR",
        "valid_calculation": True
    }


# ============================================================
# TOOL 4 - VALIDATE BUDGET
# ============================================================

def validate_budget(total, budget_ceiling):
    """
    Check whether the total budget is within the
    funding call's allowed ceiling.

    Args:
        total (float): Calculated budget
        budget_ceiling (float): Maximum allowed budget

    Returns:
        dict: Validation result
    """

    valid = total <= budget_ceiling

    return {
        "total": total,
        "budget_ceiling": budget_ceiling,
        "valid": valid,
        "difference": budget_ceiling - total
    }