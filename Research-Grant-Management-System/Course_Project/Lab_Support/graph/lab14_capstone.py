"""Lab 14 capstone wrapper: connect the existing graph, runtime, governance, and dashboard.

The dashboard is a local, static PI / Research Office prototype. It never approves,
publishes, or submits a grant. A release is labeled published only when the existing
workflow reports passing validation + acceptance and an approved governance release.
"""
from __future__ import annotations

import html
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = BASE_DIR / "outputs"
DEFAULT_REQUEST = {
    "research_area": "AI-based cardiovascular monitoring",
    "funding_type": "Government research grant",
}


def _as_count(value: Any) -> int:
    try:
        return len(value) if value is not None else 0
    except TypeError:
        return 0


def _evidence_records(state: dict[str, Any]) -> list[dict[str, Any]]:
    value = state.get("evidence_table", [])
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    if isinstance(value, dict):
        rows = value.get("records", [])
        return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []
    return []


def build_dashboard_summary(
    state: dict[str, Any],
    request: dict[str, Any] | None = None,
    run_id: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Create a privacy-minimised, JSON-serialisable view of a graph run."""
    request = dict(request or state.get("request") or DEFAULT_REQUEST)
    validation_passed = state.get("validation_passed") is True
    acceptance_report = state.get("acceptance_report") or {}
    acceptance_passed = (
        state.get("acceptance_passed") is True
        and isinstance(acceptance_report, dict)
        and acceptance_report.get("all_pass") is True
    )
    governance_status = str(state.get("governance_status") or "not_started")
    release_version = state.get("release_version")
    approved_release = (
        validation_passed
        and acceptance_passed
        and governance_status == "published_approved"
        and isinstance(release_version, int)
        and release_version > 0
    )

    calls = state.get("funding_calls", [])
    literature = state.get("literature", [])
    evidence_records = _evidence_records(state)
    accepted_evidence = sum(1 for row in evidence_records if row.get("status") == "accepted")
    rejected_evidence = sum(1 for row in evidence_records if row.get("status") == "rejected")
    pending_evidence = sum(1 for row in evidence_records if row.get("status") == "pending_review")
    # Use persisted summary counts when the table is an aggregate object and does not
    # expose individual records; do not infer acceptance from raw retrieval counts.
    evidence_summary = state.get("evidence_summary") or {}
    if not evidence_records and isinstance(state.get("evidence_table"), dict):
        evidence_summary = state["evidence_table"].get("summary", evidence_summary)
    accepted_evidence = int(evidence_summary.get("accepted_count", accepted_evidence))
    rejected_evidence = int(evidence_summary.get("rejected_count", rejected_evidence))
    pending_evidence = int(evidence_summary.get("pending_review_count", pending_evidence))

    budget = state.get("budget") or {}
    try:
        budget_total = float(budget.get("total", 0) or 0)
    except (TypeError, ValueError):
        budget_total = 0.0

    human_review_status = str(state.get("human_review_status") or "not_available")
    if approved_release:
        run_status = "published_approved"
    elif not validation_passed or not acceptance_passed:
        run_status = "blocked_validation_or_acceptance"
    elif governance_status != "published_approved":
        run_status = "awaiting_human_governance"
    else:
        run_status = "not_published"

    proposal = state.get("proposal") or {}
    specialist_metadata = proposal.get("specialist_metadata", {}) if isinstance(proposal, dict) else {}
    specialist_report = state.get("specialist_report") or {}
    profile_name = (
        specialist_metadata.get("profile_name")
        or specialist_metadata.get("display_name")
        or specialist_report.get("profile_name")
        or specialist_report.get("selected_profile")
    )

    return {
        "schema_version": "lab14.capstone-dashboard.v1",
        "run_id": run_id or str(uuid.uuid4()),
        "timestamp_utc": timestamp or datetime.now(timezone.utc).isoformat(),
        "request": {
            "research_area": str(request.get("research_area", "")),
            "funding_type": str(request.get("funding_type", "")),
        },
        "status": run_status,
        "funding_call_count": _as_count(calls),
        "literature_record_count": _as_count(literature),
        "evidence": {
            "accepted_count": accepted_evidence,
            "rejected_count": rejected_evidence,
            "pending_review_count": pending_evidence,
        },
        "proposal_created": bool(proposal),
        "budget_total": budget_total,
        "compliance_status": str((state.get("compliance") or {}).get("status", "unknown")),
        "validation_passed": validation_passed,
        "acceptance_passed": acceptance_passed,
        "human_review_status": human_review_status,
        "governance_status": governance_status,
        "published": approved_release,
        "release_version": release_version if approved_release else None,
        "specialist_profile": str(profile_name or "not_applied"),
        "retry_count": int(state.get("retry_count", 0) or 0),
        "warnings": [],
    }


def render_dashboard_html(summary: dict[str, Any]) -> str:
    """Render a simple local dashboard; all dynamic strings are HTML-escaped."""
    request = summary.get("request", {})
    rows = [
        ("Overall status", summary.get("status", "unknown")),
        ("Funding calls", summary.get("funding_call_count", 0)),
        ("Literature records retrieved", summary.get("literature_record_count", 0)),
        ("Accepted evidence", summary.get("evidence", {}).get("accepted_count", 0)),
        ("Rejected evidence", summary.get("evidence", {}).get("rejected_count", 0)),
        ("Pending evidence review", summary.get("evidence", {}).get("pending_review_count", 0)),
        ("Proposal created", summary.get("proposal_created", False)),
        ("Budget total (INR)", f"₹{float(summary.get('budget_total', 0)):,.2f}"),
        ("Compliance", summary.get("compliance_status", "unknown")),
        ("Validation passed", summary.get("validation_passed", False)),
        ("Acceptance passed", summary.get("acceptance_passed", False)),
        ("Human review", summary.get("human_review_status", "unknown")),
        ("Governance", summary.get("governance_status", "unknown")),
        ("Published", summary.get("published", False)),
        ("Specialist profile", summary.get("specialist_profile", "not_applied")),
        ("Retry count", summary.get("retry_count", 0)),
    ]
    body = "\n".join(
        "<tr><th>{}</th><td>{}</td></tr>".format(html.escape(str(key)), html.escape(str(value)))
        for key, value in rows
    )
    run_id = html.escape(str(summary.get("run_id", "unknown")))
    area = html.escape(str(request.get("research_area", "")))
    funding_type = html.escape(str(request.get("funding_type", "")))
    status = html.escape(str(summary.get("status", "unknown")))
    published_note = (
        "An approved versioned release is recorded."
        if summary.get("published") is True
        else "No grant was published or submitted by this dashboard. Human approval and all validation gates remain mandatory."
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Research Grant Management — Lab 14 Dashboard</title>
<style>body{{font-family:Segoe UI,Arial,sans-serif;max-width:960px;margin:32px auto;padding:0 18px;color:#182230}}h1{{margin-bottom:6px}}.muted{{color:#596579}}.status{{display:inline-block;padding:5px 9px;border:1px solid #9aa4b2;border-radius:7px;font-weight:600}}table{{width:100%;border-collapse:collapse;margin-top:20px}}th,td{{text-align:left;padding:11px;border-bottom:1px solid #d8dde5}}th{{width:42%;font-weight:600;background:#f6f8fb}}.note{{margin-top:18px;padding:12px;background:#f6f8fb;border-radius:8px}}code{{overflow-wrap:anywhere}}</style></head>
<body><h1>Research Grant Management System</h1><p class="muted">Lab 14 — local capstone dashboard</p>
<p><strong>Research area:</strong> {area}<br><strong>Funding type:</strong> {funding_type}</p>
<p>Run ID: <code>{run_id}</code></p><p>Overall status: <span class="status">{status}</span></p>
<table><tbody>{body}</tbody></table><p class="note">{html.escape(published_note)}</p>
<p class="muted">Generated at {html.escape(str(summary.get('timestamp_utc', 'unknown')))}. This dashboard summarizes workflow state; it is not proof that scientific claims or eligibility decisions are correct.</p></body></html>"""


def write_dashboard_files(summary: dict[str, Any], output_dir: str | Path | None = None) -> dict[str, str]:
    output = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / "capstone_dashboard.json"
    html_path = output / "capstone_dashboard.html"
    history_path = output / "capstone_runs.jsonl"
    # Atomic replacement avoids leaving a partial dashboard after interruption.
    temp_json = json_path.with_suffix(".json.tmp")
    temp_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    temp_json.replace(json_path)
    temp_html = html_path.with_suffix(".html.tmp")
    temp_html.write_text(render_dashboard_html(summary), encoding="utf-8")
    temp_html.replace(html_path)
    with history_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(summary, ensure_ascii=False) + "\n")
    return {"json": str(json_path), "html": str(html_path), "history": str(history_path)}


def _record_runtime_audit(request: dict[str, Any], summary: dict[str, Any]) -> tuple[bool, str | None]:
    """Record a small summary in the existing Lab 6 runtime audit/checkpoint files."""
    try:
        from runtime.runtime_controller import Runtime
        runtime = Runtime(budget=10, gates=["publish"])
        runtime.check_budget()
        runtime.current_step += 1
        runtime.log(
            intent="Run integrated Lab 14 capstone",
            action="langgraph_run_completed",
            input_data={"request": request},
            result={
                "run_id": summary["run_id"],
                "status": summary["status"],
                "validation_passed": summary["validation_passed"],
                "acceptance_passed": summary["acceptance_passed"],
                "published": summary["published"],
            },
        )
        runtime.set_state("latest_capstone_run", {
            "run_id": summary["run_id"],
            "status": summary["status"],
            "dashboard_json": str(DEFAULT_OUTPUT_DIR / "capstone_dashboard.json"),
        })
        runtime.save_checkpoint()
        return True, None
    except Exception as exc:  # preserve the result but surface the audit failure clearly
        return False, f"Runtime audit/checkpoint failed: {type(exc).__name__}: {exc}"


def run_capstone(
    request: dict[str, Any] | None = None,
    output_dir: str | Path | None = None,
    graph: Any | None = None,
    record_runtime: bool = True,
) -> dict[str, Any]:
    """Run the existing LangGraph and save a PI / Research Office dashboard snapshot.

    This is an orchestration/observability wrapper. It never fakes reviewer approval,
    and it never sends or submits anything to a funding agency.
    """
    request = dict(request or DEFAULT_REQUEST)
    if graph is None:
        from graph.langgraph_grant import build_grant_graph
        graph = build_grant_graph()
    result = graph.invoke({"request": request})
    summary = build_dashboard_summary(result, request=request)
    if record_runtime:
        audit_ok, audit_issue = _record_runtime_audit(request, summary)
        summary["runtime_audit_recorded"] = audit_ok
        if audit_issue:
            summary["warnings"].append(audit_issue)
            # If the audit/checkpoint cannot be recorded, don't claim a clean capstone run.
            if summary.get("status") == "published_approved":
                summary["status"] = "published_but_audit_warning"
    else:
        summary["runtime_audit_recorded"] = False
        summary["warnings"].append("Runtime audit was disabled for this run.")
    summary["dashboard_files"] = write_dashboard_files(summary, output_dir=output_dir)
    return summary


def print_dashboard(summary: dict[str, Any]) -> None:
    print("\n" + "=" * 70)
    print("LAB 14 — RESEARCH GRANT CAPSTONE DASHBOARD")
    print("=" * 70)
    print(f"Run ID: {summary.get('run_id')}")
    print(f"Status: {summary.get('status')}")
    print(f"Research area: {summary.get('request', {}).get('research_area', '')}")
    print(f"Funding calls: {summary.get('funding_call_count', 0)}")
    print(f"Literature records: {summary.get('literature_record_count', 0)}")
    print(f"Evidence accepted/rejected/pending: {summary.get('evidence', {})}")
    print(f"Proposal created: {summary.get('proposal_created')}")
    print(f"Budget total: ₹{summary.get('budget_total', 0):,.2f}")
    print(f"Validation: {'PASS' if summary.get('validation_passed') else 'FAIL'}")
    print(f"Acceptance: {'PASS' if summary.get('acceptance_passed') else 'FAIL'}")
    print(f"Governance: {summary.get('governance_status')}")
    print(f"Published: {summary.get('published')}")
    print(f"Runtime audit recorded: {summary.get('runtime_audit_recorded')}")
    print("Dashboard HTML:", summary.get("dashboard_files", {}).get("html", "not written"))
    print("No submission action was performed by Lab 14.")
