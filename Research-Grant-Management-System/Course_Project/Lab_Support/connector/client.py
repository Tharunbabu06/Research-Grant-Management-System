# ============================================================
# LAB 5 - CONNECTOR CLIENT
# ============================================================

import json
from urllib.parse import urlencode
from urllib.request import (
    Request,
    urlopen
)
from urllib.error import (
    HTTPError,
    URLError
)


# ============================================================
# CONNECTOR CONFIGURATION
# ============================================================

CONNECTOR_URL = "http://127.0.0.1:8000"

API_KEY = "LAB5-GRANT-KEY"


# ============================================================
# GENERIC CONNECTOR CALL
# ============================================================

def connector_get(endpoint):
    """
    Make an authenticated GET request to the connector.
    """

    url = CONNECTOR_URL + endpoint

    request = Request(
        url,
        headers={
            "X-API-Key": API_KEY
        },
        method="GET"
    )

    try:

        with urlopen(
            request,
            timeout=5
        ) as response:

            body = response.read().decode(
                "utf-8"
            )

            return json.loads(body)

    except HTTPError as error:

        raise RuntimeError(
            f"Connector returned HTTP {error.code}"
        )

    except URLError as error:

        raise RuntimeError(
            "Could not connect to connector server."
        ) from error


# ============================================================
# TYPED CONNECTOR SURFACES
# ============================================================

def read_funding_calls():
    """
    Read funding calls and guidelines
    through the connector.
    """

    response = connector_get(
        "/funding-calls"
    )

    return response["data"]


def read_budget_data():
    """
    Read budget and personnel data
    through the connector.
    """

    response = connector_get(
        "/budget-data"
    )

    return response["data"]


def read_compliance_rules():
    """
    Read compliance rules
    through the connector.
    """

    response = connector_get(
        "/compliance-rules"
    )

    return response["data"]


def read_literature(
    query: str,
    limit: int = 5,
):
    """Read research publications through the connector."""
    params = urlencode({
        "q": query,
        "limit": limit,
    })
    response = connector_get(
        "/literature?" + params
    )
    if not response.get("success"):
        raise RuntimeError(
            "Literature retrieval failed"
        )
    return response["data"]


def read_funding_call_candidates():
    """Read funding candidates through the connector."""
    response = connector_get("/funding-candidates")
    if not response.get("success"):
        raise RuntimeError(
            "Funding-candidate retrieval failed"
        )
    return response["data"]