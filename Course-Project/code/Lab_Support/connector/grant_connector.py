# ============================================================
# LAB 5 - MCP-STYLE CONNECTOR SERVER
# Research Grant Management System
#
# Purpose:
#   Expose all data sources through one governed server.
#
# Endpoints:
#   GET /funding-calls
#   GET /budget-data
#   GET /compliance-rules
#
# Authentication:
#   X-API-Key header
#
# Agents must NOT access JSON files directly.
# ============================================================

import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

HOST = "127.0.0.1"
PORT = 8000

API_KEY = "LAB5-GRANT-KEY"


# ============================================================
# HELPER - LOAD JSON
# ============================================================

def load_json(filename):
    """
    Load one data source from the data directory.
    """

    filepath = DATA_DIR / filename

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# CONNECTOR DATA FUNCTIONS
# ============================================================

def get_funding_calls():
    """
    Connector surface for funding calls and guidelines.
    """

    return load_json("funding_calls.json")


def get_funding_call_candidates():
    """Read source-backed funding candidates."""
    return load_json("funding_call_candidates.json")


def get_budget_data():
    """
    Connector surface for budget and personnel data.
    """

    return load_json("budget_data.json")


def get_compliance_rules():
    """
    Connector surface for compliance rules.
    """
    return load_json("compliance_rules.json")


def get_literature(query: str, limit: int = 5):
    headers = {
        "User-Agent": "GrantAgentProject/1.0 (research use)"
    }

    search_params = urlencode({
        "db": "pubmed",
        "term": query,
        "retmax": limit,
        "retmode": "json",
    })

    search_url = (
        "https://eutils.ncbi.nlm.nih.gov/"
        "entrez/eutils/esearch.fcgi?"
        + search_params
    )

    request = Request(search_url, headers=headers)
    with urlopen(request, timeout=20) as response:
        search_data = json.loads(
            response.read().decode("utf-8")
        )

    ids = search_data.get(
        "esearchresult", {}
    ).get("idlist", [])

    if not ids:
        return []

    # Retrieve the full available PubMed records.
    fetch_params = urlencode({
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "xml",
    })

    fetch_url = (
        "https://eutils.ncbi.nlm.nih.gov/"
        "entrez/eutils/efetch.fcgi?"
        + fetch_params
    )

    request = Request(fetch_url, headers=headers)
    with urlopen(request, timeout=20) as response:
        root = ET.fromstring(response.read())

    papers = []

    for item in root.findall(".//PubmedArticle"):
        citation = item.find("./MedlineCitation")
        if citation is None:
            continue

        article = citation.find("./Article")
        if article is None:
            continue

        pmid = (
            citation.findtext("./PMID") or ""
        ).strip()

        title_element = article.find("./ArticleTitle")
        title = (
            "".join(title_element.itertext()).strip()
            if title_element is not None
            else ""
        )

        abstract_parts = []
        for part in article.findall(
            "./Abstract/AbstractText"
        ):
            text = "".join(part.itertext()).strip()
            label = part.get("Label", "")
            if label:
                abstract_parts.append(f"{label}: {text}")
            else:
                abstract_parts.append(text)

        abstract = " ".join(abstract_parts).strip()

        # Extract publication date separately from retrieval time.
        pub_date = item.find(
            ".//PubMedPubDate[@PubStatus='pubmed']"
        )
        publication_date = ""
        if pub_date is not None:
            year = pub_date.findtext("Year") or ""
            month = pub_date.findtext("Month") or "01"
            day = pub_date.findtext("Day") or "01"
            if year:
                publication_date = (
                    f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                )

        # Extract DOI when it is available.
        doi = ""
        for article_id in item.findall(
            "./PubmedData/ArticleIdList/ArticleId"
        ):
            if article_id.get("IdType") == "doi":
                doi = (article_id.text or "").strip()
                break

        # Build the official PubMed record URL.
        source_url = (
            f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            if pmid else ""
        )

        papers.append({
            "title": title,
            "topic": abstract,
            "abstract": abstract,
            "type": "related-work",
            "pmid": pmid,
            "doi": doi,
            "publication_date": publication_date,
            "source": {
                "source_type": "pubmed_record",
                "source_title": title,
                "source_url": source_url,
                "source_locator": (
                    f"PMID:{pmid}" if pmid else ""
                ),
                "supporting_excerpt": abstract,
                "retrieved_at": datetime.now(
                    timezone.utc
                ).isoformat(),
                # This records successful metadata retrieval,
                # not proof that the paper supports a claim.
                "verified": bool(
                    pmid and title and source_url
                ),
            },
        })

    return papers


# ============================================================
# RESPONSE HELPER
# ============================================================

def send_json(handler, status_code, data):

    response = json.dumps(
        data,
        indent=2
    ).encode("utf-8")

    handler.send_response(status_code)

    handler.send_header(
        "Content-Type",
        "application/json"
    )

    handler.send_header(
        "Content-Length",
        str(len(response))
    )

    handler.end_headers()

    handler.wfile.write(response)


# ============================================================
# REQUEST HANDLER
# ============================================================

class ConnectorHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        # ----------------------------------------------------
        # AUTHENTICATION
        # ----------------------------------------------------

        api_key = self.headers.get("X-API-Key")

        if api_key != API_KEY:

            send_json(
                self,
                401,
                {
                    "success": False,
                    "error": "Unauthorized"
                }
            )

            return

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/literature":
            query = params.get(
                "q",
                [
                    "cardiovascular AND "
                    "(artificial intelligence OR "
                    "machine learning OR monitoring)"
                ],
            )[0]
            try:
                limit = int(
                    params.get("limit", ["5"])[0]
                )
                papers = get_literature(query, limit)
                send_json(
                    self,
                    200,
                    {
                        "success": True,
                        "source": "PubMed",
                        "query": query,
                        "data": papers,
                    },
                )
            except Exception as error:
                send_json(
                    self,
                    502,
                    {
                        "success": False,
                        "source": "PubMed",
                        "error": str(error),
                    },
                )
            return

        # ----------------------------------------------------
        # FUNDING CALLS
        # ----------------------------------------------------

        if parsed.path == "/funding-calls":

            data = get_funding_calls()

            send_json(
                self,
                200,
                {
                    "success": True,
                    "source": "funding_calls",
                    "data": data
                }
            )

            return

        # ----------------------------------------------------
        # FUNDING CANDIDATES
        # ----------------------------------------------------

        if parsed.path == "/funding-candidates":
            try:
                data = get_funding_call_candidates()
                send_json(
                    self,
                    200,
                    {
                        "success": True,
                        "source": "funding_call_candidates",
                        "data": data,
                    },
                )
            except Exception as error:
                send_json(
                    self,
                    500,
                    {
                        "success": False,
                        "error": str(error),
                    },
                )
            return

        # ----------------------------------------------------
        # BUDGET DATA
        # ----------------------------------------------------

        if parsed.path == "/budget-data":

            data = get_budget_data()

            send_json(
                self,
                200,
                {
                    "success": True,
                    "source": "budget_data",
                    "data": data
                }
            )

            return

        # ----------------------------------------------------
        # COMPLIANCE RULES
        # ----------------------------------------------------

        if parsed.path == "/compliance-rules":

            try:
                data = get_compliance_rules()

                send_json(
                    self,
                    200,
                    {
                        "success": True,
                        "source": "compliance_rules",
                        "data": data
                    }
                )

            except Exception as error:

                send_json(
                    self,
                    500,
                    {
                        "success": False,
                        "source": "compliance_rules",
                        "error": str(error)
                    }
                )

            return

        # ----------------------------------------------------
        # HEALTH CHECK
        # ----------------------------------------------------

        if parsed.path == "/health":

            send_json(
                self,
                200,
                {
                    "success": True,
                    "service": "Grant Connector",
                    "status": "running"
                }
            )

            return

        # ----------------------------------------------------
        # UNKNOWN ENDPOINT
        # ----------------------------------------------------

        send_json(
            self,
            404,
            {
                "success": False,
                "error": "Endpoint not found"
            }
        )

    # --------------------------------------------------------
    # REMOVE DEFAULT SERVER LOGGING
    # --------------------------------------------------------

    def log_message(self, format, *args):
        return


# ============================================================
# START SERVER
# ============================================================

def start_server():

    server = HTTPServer(
        (HOST, PORT),
        ConnectorHandler
    )

    print("=" * 70)
    print("LAB 5 - GRANT CONNECTOR SERVER")
    print("=" * 70)

    print(f"\nServer running at:")
    print(f"http://{HOST}:{PORT}")

    print("\nAvailable endpoints:")
    print("GET /health")
    print("GET /funding-calls")
    print("GET /budget-data")
    print("GET /compliance-rules")

    print("\nAuthentication:")
    print("X-API-Key: LAB5-GRANT-KEY")

    print("\nPress CTRL+C to stop the server.")

    try:
        server.serve_forever()

    except KeyboardInterrupt:

        print("\nStopping connector server...")

    finally:

        server.server_close()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    start_server()
