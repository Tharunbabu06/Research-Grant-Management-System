# ============================================================
# LAB 7 - LANGGRAPH AGENTIC NODE GRAPH
# Research Grant Management System
#
# Purpose:
#   Replace the custom Python graph from the earlier Lab 7
#   with a real LangGraph StateGraph.
#
# LangGraph concepts used:
#   - StateGraph
#   - TypedDict shared state
#   - Nodes
#   - Normal edges
#   - Conditional edges
#   - START / END
#
# Build Book requirements:
#   Coordinator -> specialist agents
#   -> validation
#   -> bounded regeneration on failure
#   -> human review
# ============================================================


import json
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List

from typing_extensions import TypedDict

from graph.evidence import (
    build_funding_evidence_record,
    validate_evidence_record,
)

from langgraph.graph import (
    StateGraph,
    START,
    END
)


# ============================================================
# EXISTING PROJECT COMPONENTS
# ============================================================

from skills.planning_skill import (
    plan,
    lock_plan
)

from skills.formatting_skill import (
    format_grant
)

from connector.client import (
    read_funding_calls,
    read_budget_data,
    read_compliance_rules,
    read_literature,
    read_funding_call_candidates,
)


# ============================================================
# CONFIGURATION
# ============================================================

MAX_RETRIES = 3


# ============================================================
# SHARED LANGGRAPH STATE
# ============================================================

class GrantState(TypedDict, total=False):

    # -----------------------------------------------
    # Input
    # -----------------------------------------------

    request: Dict[str, Any]

    # -----------------------------------------------
    # Planning
    # -----------------------------------------------

    plan: Dict[str, Any]

    # -----------------------------------------------
    # Funding
    # -----------------------------------------------

    funding_calls: List[Dict[str, Any]]

    # -----------------------------------------------
    # Literature
    # -----------------------------------------------

    literature: List[Dict[str, Any]]

    # -----------------------------------------------
    # Proposal
    # -----------------------------------------------

    proposal: Dict[str, Any]
    specialist_profile: str
    specialist_report: Dict[str, Any]

    # -----------------------------------------------
    # Budget
    # -----------------------------------------------

    budget: Dict[str, Any]

    # -----------------------------------------------
    # Compliance
    # -----------------------------------------------

    compliance: Dict[str, Any]

    # -----------------------------------------------
    # Submission
    # -----------------------------------------------

    submission: Dict[str, Any]

    # -----------------------------------------------
    # Validation
    # -----------------------------------------------

    validation: Dict[str, Any]

    validation_passed: bool

    acceptance_report: Dict[str, Any]
    acceptance_passed: bool
    build_status: str
    governance_status: str
    release_version: int
    release_path: str
    governance_audit_path: str
    review_actor: Dict[str, Any]
    human_approval: Dict[str, Any]

    failing_checks: List[str]

    diagnosis_log: List[Dict[str, Any]]

    # -----------------------------------------------
    # Retry
    # -----------------------------------------------

    retry_count: int

    # -----------------------------------------------
    # Final package
    # -----------------------------------------------

    final_package: Dict[str, Any]

    # -----------------------------------------------
    # Human review
    # -----------------------------------------------

    human_review_status: str

    # Lab 9: Evidence grounding
    evidence_records: List[Dict[str, Any]]
    evidence_table: List[Dict[str, Any]]
    ungrounded_candidates: List[Dict[str, Any]]
    funding_review_required: List[Dict[str, Any]]
    funding_rejected_candidates: List[Dict[str, Any]]


# ============================================================
# NODE 1 - PLAN
# ============================================================

def plan_node(state: GrantState):

    print("\n" + "=" * 70)
    print("LANGGRAPH NODE: PLAN")
    print("=" * 70)

    request = state["request"]

    created_plan = plan(request)

    locked_plan = lock_plan(
        created_plan
    )

    print(
        "\nPlan created and locked."
    )

    print(
        "Research Area:",
        locked_plan["research_area"]
    )

    print(
        "Funding Type:",
        locked_plan["funding_type"]
    )

    print(
        "Status:",
        locked_plan["status"]
    )

    return {
        "plan": locked_plan,
        "retry_count": 0
    }


# ============================================================
# HELPER - RESEARCH AREA MATCHING
# ============================================================

def research_area_matches(
    research_area: str,
    candidate_texts: list,
) -> bool:
    """Match related research terms without verifying sources."""
    query = research_area.lower().replace("-", " ")
    candidate = " ".join(
        str(item) for item in candidate_texts
    ).lower().replace("-", " ")

    query_words = set(query.split())
    candidate_words = set(candidate.split())

    ai_related = (
        "ai" in query_words
        or "artificial intelligence" in query
        or "machine learning" in query
        or "deep learning" in query
    )

    cardiovascular_related = any(
        term in query_words
        for term in ("cardiovascular", "cardiac", "heart")
    )

    # For AI-based cardiovascular research,
    # require both a technology and a health-domain match.
    if ai_related and cardiovascular_related:
        technology_match = (
            "artificial intelligence" in candidate
            or "machine learning" in candidate
            or "deep learning" in candidate
            or "ai" in candidate_words
        )
        health_match = any(
            term in candidate
            for term in (
                "cardiovascular",
                "cardiac",
                "heart",
                "healthcare",
                "biomedical",
                "medical",
                "physiological",
                "monitoring",
            )
        )
        return technology_match and health_match

    # Basic keyword matching for other research areas.
    terms = [
        word
        for word in query_words
        if len(word) > 3
        and word not in {"based", "grant", "research", "project"}
    ]

    return any(term in candidate for term in terms)


# ============================================================
# NODE 2 - FUNDING DISCOVERY AGENT
# ============================================================

def funding_discovery_node(state: GrantState):

    print("\n" + "=" * 70)
    print("LANGGRAPH NODE: FUNDING DISCOVERY AGENT")
    print("=" * 70)

    # Read both sources through the existing connector.
    existing_calls = read_funding_calls()
    candidate_calls = read_funding_call_candidates()

    records = [
        (call, "existing")
        for call in existing_calls
    ] + [
        (call, "candidate")
        for call in candidate_calls
    ]

    plan = state["plan"]
    research_area = plan["research_area"].lower()
    funding_type = plan["funding_type"].lower()

    matching_calls = []
    review_required = []
    rejected_calls = []

    for call, record_type in records:
        agency = call.get("agency", "")
        title = call.get("call_title", "")
        source = call.get("source", {})

        required_fields = [
            "source_title",
            "source_url",
            "source_locator",
            "supporting_excerpt",
            "retrieved_at",
        ]
        missing_fields = [
            field
            for field in required_fields
            if not isinstance(source.get(field), str)
            or not source.get(field, "").strip()
        ]

        # A source must be checked before it is marked verified.
        if (
            source.get("verified") is not True
            or missing_fields
            or not source.get("source_url", "").startswith("https://")
        ):
            print(
                f"Skipping unverified call: {agency} - {title}"
            )
            if missing_fields:
                print(
                    "Missing source fields:",
                    ", ".join(missing_fields),
                )
            rejection_issues = []
            if source.get("verified") is not True:
                rejection_issues.append(
                    "Source has not been verified"
                )
            rejection_issues.extend(
                f"Missing required source field: {field}"
                for field in missing_fields
            )
            source_url = source.get("source_url", "")
            if (
                not isinstance(source_url, str)
                or not source_url.startswith("https://")
            ):
                rejection_issues.append(
                    "Missing or invalid HTTPS source URL"
                )
            rejected_calls.append({
                "candidate_type": "funding_call",
                "candidate_title": title,
                "agency": agency,
                "status": "rejected_unverified_source",
                "issues": rejection_issues,
            })
            if record_type == "candidate":
                review_required.append(call)
            continue

        # Check that the deadline is valid and has not passed.
        try:
            deadline = datetime.strptime(
                call.get("deadline", ""),
                "%Y-%m-%d",
            ).date()
        except (ValueError, TypeError):
            print(
                f"Skipping call with invalid deadline: {title}"
            )
            continue

        if deadline < date.today():
            print(f"Skipping expired call: {title}")
            continue

        # Pending candidates must be reviewed by a human.
        if record_type == "candidate":
            eligibility = str(
                call.get("eligibility_status", "")
            ).lower()
            novelty = str(
                call.get("novelty_status", "")
            ).lower()
            if (
                eligibility != "eligible"
                or novelty not in {"approved", "cleared"}
            ):
                review_required.append(call)
                print(
                    f"Candidate needs human review: "
                    f"{agency} - {title}"
                )
                print(
                    f"Eligibility status: "
                    f"{eligibility or 'not reviewed'}"
                )
                print(
                    f"Novelty status: "
                    f"{novelty or 'not reviewed'}"
                )
                continue

        # Match the research area.
        call_areas = call.get("research_areas", [])
        area_match = research_area_matches(
            research_area,
            call_areas,
        )

        # Match the funding type.
        call_type = str(
            call.get("funding_type", "")
        ).lower()
        type_match = bool(call_type) and (
            funding_type in call_type
            or call_type in funding_type
        )

        if area_match and type_match:
            matching_calls.append(call)

    print(
        "\nVerified matching calls:",
        len(matching_calls),
    )
    print(
        "Candidates requiring review:",
        len(review_required),
    )

    for call in matching_calls:
        print(
            f"- {call['agency']}: "
            f"{call['call_title']}"
        )

    for call in review_required:
        print(
            f"- REVIEW: {call['agency']}: "
            f"{call['call_title']}"
        )

    if not matching_calls:
        print(
            "\nNo fully cleared matching funding calls found."
        )

    return {
        "funding_calls": matching_calls,
        "funding_review_required": review_required,
        "funding_rejected_candidates": rejected_calls,
    }


# ============================================================
# NODE 3 - LITERATURE REVIEW AGENT
# ============================================================

def literature_review_node(state: GrantState):

    print("\n" + "=" * 70)
    print("LANGGRAPH NODE: LITERATURE REVIEW AGENT")
    print("=" * 70)

    research_area = state.get(
        "plan", {}
    ).get("research_area", "")

    # Focus the search on AI-based cardiovascular research.
    query = (
        '("cardiovascular"[Title/Abstract] OR '
        '"cardiac"[Title/Abstract] OR '
        '"heart"[Title/Abstract]) AND '
        '("artificial intelligence"[Title/Abstract] OR '
        '"machine learning"[Title/Abstract] OR '
        '"deep learning"[Title/Abstract]) AND '
        '(monitoring[Title/Abstract] OR '
        'prediction[Title/Abstract] OR '
        'detection[Title/Abstract])'
    )

    print("Research area:", research_area)
    print("Source: PubMed through the Grant Connector")
    print("Retrieving publication records...")

    try:
        literature = read_literature(
            query=query,
            limit=10,
        )
    except Exception as error:
        print("Literature retrieval failed:", error)
        # Do not substitute invented papers.
        return {
            "literature": []
        }

    print(
        "\nPublication records retrieved:",
        len(literature),
    )

    for paper in literature:
        print(
            f"- {paper.get('title', 'Untitled')} "
            f"(PMID: {paper.get('pmid', 'N/A')})"
        )

    return {
        "literature": literature
    }


# ============================================================
# NODE 4 - PROPOSAL DRAFTING AGENT
# ============================================================

def proposal_drafting_node(
    state: GrantState
):

    print("\n" + "=" * 70)
    print(
        "LANGGRAPH NODE: PROPOSAL DRAFTING AGENT"
    )
    print("=" * 70)

    research_area = (
        state["plan"]["research_area"]
    )

    funding_type = (
        state["plan"]["funding_type"]
    )

    literature_titles = [
        paper["title"]
        for paper in state["literature"]
    ]

    proposal = {

        "title":
            f"Research Proposal on {research_area}",

        "research_area":
            research_area,

        "funding_type":
            funding_type,

        "abstract":
            (
                f"This proposal investigates "
                f"{research_area} using AI-based "
                f"methods for research and monitoring."
            ),

        "objectives": [
            "Define the research problem",
            "Develop the proposed research approach",
            "Evaluate the proposed methodology"
        ],

        "methodology":
            (
                "Develop the research methodology, "
                "implement the proposed system, "
                "and evaluate the results."
            ),

        "timeline":
            "24 months",

        "expected_outcomes": [
            "Research prototype",
            "Evaluation results",
            "Research findings"
        ],

        "related_literature":
            literature_titles,

        "status":
            "draft"
    }

    print(
        "\nProposal draft created."
    )

    print(
        "Title:",
        proposal["title"]
    )

    return {
        "proposal": proposal
    }


# ============================================================
# NODE 5 - BUDGET PLANNING AGENT
# ============================================================

def budget_planning_node(
    state: GrantState
):

    print("\n" + "=" * 70)
    print(
        "LANGGRAPH NODE: BUDGET PLANNING AGENT"
    )
    print("=" * 70)

    budget_data = read_budget_data()

    total = sum(
        budget_data.values()
    )

    funding_calls = state[
        "funding_calls"
    ]

    budget_ceiling = funding_calls[0][
        "budget_ceiling"
    ]

    budget = {

        "items":
            budget_data,

        "total":
            total,

        "ceiling":
            budget_ceiling,

        "within_ceiling":
            total <= budget_ceiling
    }

    print(
        f"\nBudget Total: "
        f"₹{total:,.2f}"
    )

    print(
        f"Budget Ceiling: "
        f"₹{budget_ceiling:,.2f}"
    )

    print(
        "Within Ceiling:",
        budget["within_ceiling"]
    )

    return {
        "budget": budget
    }


# ============================================================
# NODE 6 - COMPLIANCE CHECKING AGENT
# ============================================================

def compliance_checking_node(
    state: GrantState
):

    print("\n" + "=" * 70)
    print(
        "LANGGRAPH NODE: COMPLIANCE CHECKING AGENT"
    )
    print("=" * 70)

    rules = read_compliance_rules()

    funding_call = state[
        "funding_calls"
    ][0]

    required_sections = set(
        funding_call[
            "required_sections"
        ]
    )

    proposal_sections = {
        "Abstract",
        "Objectives",
        "Methodology",
        "Timeline",
        "Expected Outcomes",
        "Budget"
    }

    missing_sections = (
        required_sections
        -
        proposal_sections
    )

    budget_ok = (
        state["budget"]["within_ceiling"]
    )

    compliance_status = (
        "pass"
        if (
            not missing_sections
            and budget_ok
        )
        else "fail"
    )

    compliance = {

        "rules_checked":
            len(rules["rules"]),

        "missing_sections":
            list(missing_sections),

        "budget_compliant":
            budget_ok,

        "status":
            compliance_status
    }

    print(
        "\nRules checked:",
        len(rules["rules"])
    )

    print(
        "Missing sections:",
        compliance["missing_sections"]
    )

    print(
        "Budget compliant:",
        compliance["budget_compliant"]
    )

    print(
        "Compliance status:",
        compliance["status"]
    )

    return {
        "compliance": compliance
    }


# ============================================================
# NODE 7 - SUBMISSION AGENT
# ============================================================

def submission_node(
    state: GrantState
):

    print("\n" + "=" * 70)
    print(
        "LANGGRAPH NODE: SUBMISSION AGENT"
    )
    print("=" * 70)

    submission = {

        "proposal":
            state["proposal"],

        "budget":
            state["budget"],

        "compliance":
            state["compliance"],

        "status":
            "package_ready_for_validation"
    }

    print(
        "\nSubmission package prepared "
        "for validation."
    )

    return {
        "submission": submission
    }


# ============================================================
# NODE 8 - GROUNDING
# ============================================================

def grounding_node(state: GrantState):
    """Ground candidate records and write a complete, status-aware evidence table."""
    import json
    from datetime import datetime, timezone
    from pathlib import Path

    from graph.evidence import (
        build_funding_evidence_record,
        validate_evidence_record,
        literature_relevance_issues,
    )

    print("\n" + "=" * 70)
    print("LANGGRAPH NODE: GROUNDING")
    print("=" * 70)

    plan_data = state.get("plan", {})
    research_area = str(plan_data.get("research_area", ""))
    evidence_records = []
    evidence_table = []
    ungrounded_output_candidates = []

    # 1. Ground selected funding calls. These have already passed discovery
    # filters, so a failure here means the selected funding input is unsafe.
    for call in state.get("funding_calls", []):
        title = str(call.get("call_title", "Unknown funding call"))
        agency = str(call.get("agency", "Unknown agency"))
        source = call.get("source", {}) or {}
        call_text = " ".join(
            [title, agency]
            + [str(item) for item in call.get("research_areas", [])]
        )
        try:
            in_scope = bool(research_area_matches(research_area, [call_text]))
        except Exception:
            in_scope = any(
                term in call_text.lower()
                for term in ("cardiovascular", "cardiac", "heart", "medical", "healthcare", "biomedical", "artificial intelligence")
            )

        evidence = build_funding_evidence_record(call, in_scope=in_scope)
        is_valid, issues = validate_evidence_record(evidence)
        if not str(evidence.get("source_reference", "")).startswith("https://"):
            issues.append("Missing or invalid HTTPS source reference")
        accepted = bool(is_valid and not issues)
        row = {
            **evidence,
            "candidate_type": "funding_call",
            "candidate_title": title,
            "agency": agency,
            "accepted": accepted,
            "status": "accepted" if accepted else "rejected",
            "issues": issues,
        }
        evidence_table.append(row)
        if accepted:
            evidence_records.append(evidence)
        else:
            # These were selected as usable funding calls. Their grounding
            # failure must block downstream proposal/budget processing.
            ungrounded_output_candidates.append({
                "candidate_type": "funding_call",
                "candidate_title": title,
                "agency": agency,
                "issues": issues,
            })

    # 2. Preserve rejected funding discovery candidates in the audit trail.
    # They are excluded from downstream work and do not, by themselves, turn
    # an otherwise grounded package into a failure.
    for rejected in state.get("funding_rejected_candidates", []):
        raw_call = rejected.get("record", {}) or {}
        source = raw_call.get("source", {}) or {}
        issues = rejected.get("issues", []) or ["Funding candidate failed source verification"]
        evidence_table.append({
            "candidate_type": "funding_call",
            "candidate_title": rejected.get("candidate_title") or raw_call.get("call_title", "Unknown funding call"),
            "agency": rejected.get("agency") or raw_call.get("agency", "Unknown agency"),
            "source_type": source.get("source_type", ""),
            "source_title": source.get("source_title", ""),
            "source_reference": source.get("source_url", ""),
            "source_locator": source.get("source_locator", ""),
            "excerpt": source.get("supporting_excerpt", ""),
            "verified": source.get("verified") is True,
            "in_scope": False,
            "accepted": False,
            "status": "rejected",
            "rejection_code": rejected.get("status", "rejected_unverified_source"),
            "issues": list(issues),
        })

    # 3. Keep funding calls needing eligibility/novelty review distinct from
    # rejected records. A pending candidate is never treated as approved.
    for call in state.get("funding_review_required", []):
        source = call.get("source", {}) or {}
        title = str(call.get("call_title", "Unknown funding call"))
        agency = str(call.get("agency", "Unknown agency"))
        eligibility = str(call.get("eligibility_status", "pending_human_review"))
        novelty = str(call.get("novelty_status", "pending_human_review"))
        issues = []
        if eligibility.lower() != "eligible":
            issues.append(f"Eligibility requires review (status: {eligibility})")
        if novelty.lower() not in {"approved", "cleared"}:
            issues.append(f"Novelty requires review (status: {novelty})")
        candidate_text = " ".join(
            [title, agency] + [str(item) for item in call.get("research_areas", [])]
        )
        try:
            in_scope = bool(research_area_matches(research_area, [candidate_text]))
        except Exception:
            in_scope = False
        evidence_table.append({
            "candidate_type": "funding_call",
            "candidate_title": title,
            "agency": agency,
            "source_type": source.get("source_type", ""),
            "source_title": source.get("source_title", title),
            "source_reference": source.get("source_url", ""),
            "source_locator": source.get("source_locator", ""),
            "excerpt": source.get("supporting_excerpt", ""),
            "verified": source.get("verified") is True,
            "in_scope": in_scope,
            "accepted": False,
            "status": "pending_review",
            "eligibility_status": eligibility,
            "novelty_status": novelty,
            "issues": issues,
        })

    # 4. Check each PubMed result using its title and abstract, not title-only
    # keyword matching. Metadata verification proves record retrieval only;
    # it does not prove relevance or that the paper supports every claim.
    for paper in state.get("literature", []):
        source = paper.get("source", {}) or {}
        title = str(paper.get("title", source.get("source_title", "Untitled paper")))
        abstract = str(paper.get("abstract") or paper.get("topic") or source.get("supporting_excerpt") or "")
        paper_text = f"{title}. {abstract}"
        source_url = str(source.get("source_url") or paper.get("source_url") or "")
        pmid = str(paper.get("pmid") or "").strip()
        locator = str(source.get("source_locator") or (f"PMID:{pmid}" if pmid else ""))
        evidence = {
            "claim": f"Publication record: {title}",
            "source_type": str(source.get("source_type", "pubmed_record")),
            "source_title": str(source.get("source_title") or title),
            "source_reference": source_url,
            "source_locator": locator,
            "excerpt": str(source.get("supporting_excerpt") or abstract),
            "verified": source.get("verified") is True,
            "in_scope": False,
        }
        issues = literature_relevance_issues(research_area, paper_text)
        in_scope = not any(
            issue.startswith("No explicit cardiovascular-domain term")
            or issue.startswith("No explicit AI/ML method")
            or issue.startswith("No monitoring, prediction, detection, or assessment task")
            or issue.startswith("No meaningful research-area term")
            for issue in issues
        )
        evidence["in_scope"] = in_scope
        is_valid, metadata_issues = validate_evidence_record(evidence)
        issues.extend(metadata_issues)
        if not source_url.startswith("https://"):
            issues.append("Missing or invalid HTTPS PubMed source URL")
        # De-duplicate the issue list while retaining readable order.
        issues = list(dict.fromkeys(issues))
        accepted = bool(is_valid and in_scope and not issues)

        row = {
            **evidence,
            "candidate_type": "literature",
            "candidate_title": title,
            "pmid": pmid,
            "accepted": accepted,
            "status": "accepted" if accepted else "rejected",
            "issues": issues,
        }
        evidence_table.append(row)
        if accepted:
            evidence_records.append(evidence)

    # 5. Persist the complete audit trail. Counts are status-driven so
    # pending review is not mixed into accepted/rejected totals.
    accepted_count = sum(row.get("status") == "accepted" for row in evidence_table)
    rejected_count = sum(row.get("status") == "rejected" for row in evidence_table)
    pending_review_count = sum(row.get("status") == "pending_review" for row in evidence_table)
    output_dir = Path(__file__).resolve().parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "evidence_table.json"
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "research_area": research_area,
        "summary": {
            "accepted_count": accepted_count,
            "rejected_count": rejected_count,
            "pending_review_count": pending_review_count,
            "total_records": len(evidence_table),
        },
        # Keep top-level count keys for compatibility with earlier Lab 9 output.
        "accepted_count": accepted_count,
        "rejected_count": rejected_count,
        "pending_review_count": pending_review_count,
        "records": evidence_table,
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Evidence records accepted: {accepted_count}")
    print(f"Rejected candidates: {rejected_count}")
    print(f"Candidates pending human review: {pending_review_count}")
    print(f"Evidence table saved to: {report_path}")

    return {
        "evidence_records": evidence_records,
        "evidence_table": evidence_table,
        "ungrounded_candidates": ungrounded_output_candidates,
    }


def validation_node(state: GrantState):
    """Validate the package, diagnose each failure, and record an audit trail."""
    from graph.lab10_resilience import diagnose_check, is_repairable

    print("\n" + "=" * 70)
    print("LANGGRAPH NODE: VALIDATION")
    print("=" * 70)

    budget = state.get("budget") or {}
    items = budget.get("items") or {}
    total = budget.get("total")
    ceiling = budget.get("ceiling")
    numeric_items = isinstance(items, dict) and bool(items) and all(
        isinstance(value, (int, float)) and not isinstance(value, bool) for value in items.values()
    )
    numeric_total = isinstance(total, (int, float)) and not isinstance(total, bool)
    numeric_ceiling = isinstance(ceiling, (int, float)) and not isinstance(ceiling, bool)

    funding_calls = state.get("funding_calls") or []
    compliance = state.get("compliance") or {}
    eligible_statuses = {"eligible", "approved", "pass"}
    eligibility_confirmed = bool(funding_calls) and all(
        str(call.get("eligibility_status", "")).strip().lower() in eligible_statuses
        for call in funding_calls
    )
    compliance_passed = compliance.get("status") == "pass"

    from datetime import date
    def has_tracked_deadline(call):
        raw_deadline = call.get("deadline") or call.get("deadline_date")
        if not isinstance(raw_deadline, str) or not raw_deadline.strip():
            return False
        try:
            date.fromisoformat(raw_deadline.strip()[:10])
            return True
        except ValueError:
            return False

    submission = state.get("submission") or {}
    submission_status = str(submission.get("status", "")).lower()
    submission_was_sent = submission.get("submitted") is True or submission_status in {
        "submitted", "sent", "published", "transmitted"
    }
    human_approved = (
        state.get("pi_approved") is True
        or submission.get("pi_approved") is True
        or str(state.get("human_review_status", "")).lower() in {"approved", "approved_for_submission"}
    )

    checks = {
        "funding_call_found": bool(funding_calls),
        "proposal_created": bool(state.get("proposal")),
        "eligibility_and_compliance_met": eligibility_confirmed and compliance_passed,
        "budget_totals_reconcile": bool(
            numeric_items and numeric_total and total == sum(items.values())
        ),
        "budget_within_ceiling": bool(
            numeric_total and numeric_ceiling and total <= ceiling and budget.get("within_ceiling") is True
        ),
        "compliance_passed": compliance_passed,
        "no_submission_without_approval": bool(not submission_was_sent or human_approved),
        "deadline_tracked": bool(funding_calls) and all(has_tracked_deadline(call) for call in funding_calls),
        "evidence_grounded": bool(state.get("evidence_records")) and not bool(state.get("ungrounded_candidates")),
    }
    failing = [name for name, passed in checks.items() if not passed]
    passed = not failing
    diagnoses = [
        {
            "check": name,
            "diagnosis": diagnose_check(name),
            "repairable_now": is_repairable(name, state),
        }
        for name in failing
    ]
    validation = {
        "checks": checks,
        "passed": passed,
        "failing": failing,
        "diagnoses": diagnoses,
    }
    log = list(state.get("diagnosis_log") or [])
    log.append({
        "event": "validation",
        "attempt": state.get("retry_count", 0),
        "passed": passed,
        "failing_checks": list(failing),
        "diagnoses": diagnoses,
    })

    print("\nValidation Checks:")
    for name, result in checks.items():
        print(f"{name}: {'PASS' if result else 'FAIL'}")
    if failing:
        print("\nFailure diagnosis:")
        for item in diagnoses:
            print(f"- {item['check']}: {item['diagnosis']}")
            print(f"  Safe targeted repair available now: {item['repairable_now']}")
    print("\nValidation Result:", "PASS" if passed else "FAIL")
    return {
        "validation": validation,
        "validation_passed": passed,
        "failing_checks": failing,
        "diagnosis_log": log,
    }

# ============================================================
# NODE 9 - REGENERATE
# ============================================================

def regenerate_node(state: GrantState):
    """Perform a bounded, targeted repair; never fabricate compliance success."""
    from graph.lab10_resilience import apply_targeted_repairs

    print("\n" + "=" * 70)
    print("LANGGRAPH NODE: REGENERATE")
    print("=" * 70)
    retry_count = state.get("retry_count", 0) + 1
    failing = list(state.get("failing_checks") or (state.get("validation") or {}).get("failing", []))
    print(f"\nRegeneration attempt: {retry_count}/{MAX_RETRIES}")
    print("Failing checks:", ", ".join(failing) if failing else "none")

    updates = apply_targeted_repairs(state, failing, retry_count)
    for action in updates["diagnosis_log"][-1].get("actions", []):
        print(f"Repair action: {action.get('action')} | {action.get('check', '')}")
    return updates

# ============================================================
# NODE 10 - ASSEMBLY
# ============================================================

def assembly_node(
    state: GrantState
):

    print("\n" + "=" * 70)
    print(
        "LANGGRAPH NODE: ASSEMBLY"
    )
    print("=" * 70)

    template = [

        "Research Area",
        "Funding Type",
        "Abstract",
        "Objectives",
        "Methodology",
        "Timeline",
        "Expected Outcomes",
        "Budget",
        "Compliance"
    ]

    document = format_grant(

        {
            "research_area":
                state["plan"]["research_area"],

            "funding_type":
                state["plan"]["funding_type"]
        },

        template
    )

    document["proposal"] = (
        state["proposal"]
    )

    document["budget"] = (
        state["budget"]
    )

    document["compliance"] = (
        state["compliance"]
    )

    document["status"] = (
        "validated_draft"
    )

    print(
        "\nGrant proposal and compliance "
        "package assembled."
    )

    return {
        "final_package": document
    }


# ============================================================
# NODE 11 - HUMAN REVIEW GATE
# ============================================================

def human_review_node(state: GrantState):
    """Hard gate: expose a package for review only after validation and Lab 11 acceptance pass."""
    from graph.lab11_acceptance import acceptance_suite

    print("\n" + "=" * 70)
    print("LANGGRAPH NODE: HUMAN REVIEW GATE")
    print("=" * 70)

    report = state.get("acceptance_report")
    if not isinstance(report, dict):
        report = acceptance_suite(state, state.get("plan"))

    validation_passed = state.get("validation_passed") is True
    acceptance_passed = state.get("acceptance_passed") is True and report.get("all_pass") is True

    if not validation_passed:
        print("\nVALIDATION FAILED. The package is NOT validated and will not be presented for review.")
        return {
            "acceptance_report": report,
            "acceptance_passed": False,
            "build_status": "blocked_validation_failure",
            "human_review_status": "blocked_validation_failure",
        }

    if not acceptance_passed:
        print("\nACCEPTANCE FAILED. The package will NOT be presented to the PI / Research Office.")
        return {
            "acceptance_report": report,
            "acceptance_passed": False,
            "build_status": "blocked_acceptance_failure",
            "human_review_status": "blocked_acceptance_failure",
        }

    print("\nValidation and Lab 11 acceptance passed.")
    print("A draft is ready for human review; this is NOT final approval or submission.")
    print("Decision authority: PI / Research Office / Dean R&D / HoD")
    return {
        "acceptance_report": report,
        "acceptance_passed": True,
        "build_status": "ready_for_human_review",
        "human_review_status": "pending_human_review",
    }


# ============================================================

def route_after_funding_discovery(state: GrantState) -> str:
    """Continue only when funding calls were matched."""
    if state.get("funding_calls"):
        return "continue"
    return "no_funding"

def no_funding_node(state: GrantState):
    """Stop safely when no matching funding call exists."""
    print("\n" + "=" * 70)
    print("LANGGRAPH NODE: NO MATCHING FUNDING CALL")
    print("=" * 70)
    print("No suitable funding call was found.")
    print("Budget planning and proposal processing are stopped.")
    print("The funding search must be reviewed.")

    pending = state.get("funding_review_required", [])
    if pending:
        print("\nFunding candidates awaiting review:")
        for call in pending:
            print(
                f"- {call.get('agency')}: "
                f"{call.get('call_title')}"
            )
        print(
            "Review eligibility and novelty before "
            "using these candidates."
        )

    return {
        "validation": {
            "checks": {
                "funding_call_found": False
            },
            "passed": False,
            "failing": ["funding_call_found"],
        },
        "validation_passed": False,
        "failing_checks": ["funding_call_found"],
    }

def governance_node(state: GrantState):
    """Lab 12: log the review state and publish only with explicit authorized approval."""
    from graph.lab12_governance import publish_approved_artifact, record_review_pending

    print("\n" + "=" * 70)
    print("LANGGRAPH NODE: LAB 12 SAFETY & GOVERNANCE")
    print("=" * 70)

    actor = state.get("review_actor")
    approval = state.get("human_approval")
    if isinstance(actor, dict) and isinstance(approval, dict):
        result = publish_approved_artifact(state, actor, approval)
        print("Governance result:", result.get("governance_status"))
        for issue in result.get("issues", []):
            print("-", issue)
        updates = {
            "governance_status": result.get("governance_status", "blocked_release"),
            "release_version": result.get("release_version"),
            "release_path": result.get("release_path"),
            "governance_audit_path": result.get("governance_audit_path"),
        }
        if result.get("ok") is True:
            updates["final_package"] = result["release"]["package"]
        return updates

    result = record_review_pending(state)
    print("No explicit reviewer decision supplied; no release was published.")
    print("Governance status:", result["governance_status"])
    return result


# CONDITIONAL ROUTER
# ============================================================

def validation_router(state: GrantState):
    """Route pass, safe repair, or human escalation with a bounded retry count."""
    from graph.lab10_resilience import is_repairable, diagnose_check

    if state.get("validation_passed", False):
        print("\nROUTER: Validation PASS -> Assembly")
        return "assembly"

    failing = list(state.get("failing_checks") or (state.get("validation") or {}).get("failing", []))
    retry_count = state.get("retry_count", 0)
    safe_checks = [name for name in failing if is_repairable(name, state)]

    if retry_count >= MAX_RETRIES:
        print(f"\nROUTER: Retry budget exhausted ({retry_count}/{MAX_RETRIES}) -> Human Review")
        return "human_review"

    if safe_checks:
        print("\nROUTER: Validation FAIL -> Targeted Regenerate")
        print("Repairable checks:", ", ".join(safe_checks))
        return "regenerate"

    print("\nROUTER: No safe automated repair exists -> Human Review")
    for name in failing:
        print(f"- {name}: {diagnose_check(name)}")
    return "human_review"

# ============================================================
def acceptance_node(state: GrantState):
    """Run the Lab 11 acceptance suite after assembly and before review."""
    from graph.lab11_acceptance import acceptance_suite

    print("\n" + "=" * 70)
    print("LANGGRAPH NODE: LAB 11 ACCEPTANCE SUITE")
    print("=" * 70)
    report = acceptance_suite(state, state.get("plan"))
    for name, passed in report["checks"].items():
        print(f"{name}: {'PASS' if passed else 'FAIL'}")
    print(f"Acceptance report: {report['passed_count']}/{report['total_checks']} checks passed")
    print("Acceptance result:", "PASS" if report["all_pass"] else "FAIL")
    if report["failing"]:
        print("Failing acceptance checks:")
        for item in report["diagnoses"]:
            print(f"- {item['check']}: {item['diagnosis']}")
    return {
        "acceptance_report": report,
        "acceptance_passed": report["all_pass"],
        "build_status": "ready_for_human_review" if report["all_pass"] else "blocked_acceptance_failure",
    }


def acceptance_router(state: GrantState):
    """Only route a fully accepted artifact to the PI / Research Office gate."""
    report = state.get("acceptance_report") or {}
    if state.get("acceptance_passed") is True and report.get("all_pass") is True:
        print("\nLAB 11 GATE: Acceptance PASS -> Human Review")
        return "human_review"
    print("\nLAB 11 GATE: Acceptance FAIL -> Blocked; package will not be presented for review")
    return "blocked"


def acceptance_blocked_node(state: GrantState):
    """Record a failed build without presenting the package to the human reviewer."""
    import copy
    package = copy.deepcopy(state.get("final_package") or {})
    if package:
        package["status"] = "blocked_not_for_human_review"
    report = state.get("acceptance_report") or {}
    print("\n" + "=" * 70)
    print("LAB 11 BUILD BLOCKED")
    print("=" * 70)
    print("Acceptance report did not pass. The package must not advance to PI / Research Office review.")
    print("Failing checks:", ", ".join(report.get("failing", [])) or "acceptance report missing")
    return {
        "final_package": package,
        "build_status": "blocked_acceptance_failure",
        "human_review_status": "blocked_acceptance_failure",
    }

# BUILD LANGGRAPH
# ============================================================


def lab13_specialist_node(state: GrantState):
    """Lab 13: apply a funder-profile specialist while keeping call rules unapproved."""
    from graph.lab13_specialists import specialize_proposal

    print("\n" + "=" * 70)
    print("LANGGRAPH NODE: LAB 13 DISCIPLINE-SPECIFIC SPECIALIST")
    print("=" * 70)

    request = state.get("request") if isinstance(state.get("request"), dict) else {}
    result = specialize_proposal(
        proposal=state.get("proposal", {}),
        plan=state.get("plan", {}),
        funding_calls=state.get("funding_calls", []),
        requested_profile=state.get("specialist_profile") or request.get("specialist_profile"),
    )
    report = result["report"]
    print("Selected specialist profile:", result.get("profile") or "none")
    print("Specialist output contract:", "PASS" if report.get("passed") else "FAIL")
    print("Call-specific compliance ready:", bool(report.get("source_specific_ready")))
    for issue in report.get("issues", []):
        print("-", issue)
    for note in report.get("notes", []):
        print("NOTE:", note)

    return {
        "proposal": result["proposal"],
        "specialist_profile": result.get("profile"),
        "specialist_report": report,
    }


def build_grant_graph():

    builder = StateGraph(
        GrantState
    )

    # --------------------------------------------------------
    # ADD NODES
    # --------------------------------------------------------

    builder.add_node(
        "plan",
        plan_node
    )

    builder.add_node(
        "funding_discovery",
        funding_discovery_node
    )

    builder.add_node(
        "no_funding",
        no_funding_node
    )

    builder.add_node(
        "literature_review",
        literature_review_node
    )

    builder.add_node(
        "proposal_drafting",
        proposal_drafting_node
    )

    builder.add_node(
        "lab13_specialist",
        lab13_specialist_node
    )

    builder.add_node(
        "budget_planning",
        budget_planning_node
    )

    builder.add_node(
        "compliance_checking",
        compliance_checking_node
    )

    builder.add_node(
        "submission",
        submission_node
    )

    builder.add_node(
        "grounding",
        grounding_node
    )

    builder.add_node(
        "candidate_grounding",
        grounding_node
    )

    builder.add_node(
        "validation",
        validation_node
    )

    builder.add_node(
        "regenerate",
        regenerate_node
    )

    builder.add_node(
        "assembly",
        assembly_node
    )

    builder.add_node(
        "acceptance",
        acceptance_node
    )

    builder.add_node(
        "acceptance_blocked",
        acceptance_blocked_node
    )

    builder.add_node(
        "human_review",
        human_review_node
    )


    builder.add_node(

        "governance",

        governance_node

    )

    # --------------------------------------------------------
    # FIXED EDGES — LAB 9 PARALLEL DISCOVERY
    # --------------------------------------------------------

    builder.add_edge(
        START,
        "plan"
    )

    # Start both research tasks after the plan is locked.
    builder.add_edge(
        "plan",
        "funding_discovery"
    )

    builder.add_edge(
        "plan",
        "literature_review"
    )

    # Wait until BOTH research tasks have finished.
    builder.add_edge(
        ["funding_discovery", "literature_review"],
        "candidate_grounding"
    )

    # Continue only when a cleared funding call exists.
    builder.add_conditional_edges(
        "candidate_grounding",
        route_after_funding_discovery,
        {
            "continue": "proposal_drafting",
            "no_funding": "no_funding",
        }
    )

    builder.add_edge(
        "no_funding",
        "human_review"
    )

    builder.add_edge(
        "proposal_drafting",
        "lab13_specialist"
    )

    builder.add_edge(
        "lab13_specialist",
        "budget_planning"
    )

    builder.add_edge(
        "budget_planning",
        "compliance_checking"
    )

    builder.add_edge(
        "compliance_checking",
        "submission"
    )

    builder.add_edge(
        "submission",
        "grounding"
    )

    builder.add_edge(
        "grounding",
        "validation"
    )

    # --------------------------------------------------------
    # CONDITIONAL VALIDATION ROUTING
    # --------------------------------------------------------

    builder.add_conditional_edges(

        "validation",

        validation_router,

        {
            "assembly":
                "assembly",

            "regenerate":
                "regenerate",

            "human_review":
                "human_review"
        }
    )

    # --------------------------------------------------------
    # REGENERATION BACK-EDGE
    # --------------------------------------------------------

    builder.add_edge(
        "regenerate",
        "validation"
    )

    # --------------------------------------------------------
    # ASSEMBLY -> HUMAN REVIEW
    # --------------------------------------------------------

    builder.add_edge(
        "assembly",
        "acceptance"
    )

    builder.add_conditional_edges(
        "acceptance",
        acceptance_router,
        {
            "human_review": "human_review",
            "blocked": "acceptance_blocked",
        }
    )

    builder.add_edge(
        "acceptance_blocked",
        END
    )

    # --------------------------------------------------------
    # HUMAN REVIEW -> END
    # --------------------------------------------------------

    builder.add_edge(
        "human_review",
        "governance"
    )

    builder.add_edge(
        "governance",
        END
    )

    # --------------------------------------------------------
    # COMPILE
    # --------------------------------------------------------

    graph = builder.compile()

    return graph