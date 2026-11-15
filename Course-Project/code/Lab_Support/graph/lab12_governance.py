"""Lab 12 Safety & Governance: explicit approval, audit, versioning and rollback.

This module's role metadata is a local lab contract, not a production identity
provider. In a deployed system, derive actor roles from trusted authentication.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
import uuid

APPROVER_ROLES = {
    "pi", "principal_investigator", "research_office", "dean_rd",
    "dean_r_d", "hod", "head_of_department",
}
ROLLBACK_ROLES = APPROVER_ROLES


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _default_output_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "outputs"


def _normal_role(value: Any) -> str:
    raw = str(value or "").strip().casefold()
    if raw in {"dean r&d", "dean r and d", "dean rd", "dean-r&d"}:
        return "dean_rd"
    role = raw.replace("&", "and").replace(" ", "_").replace("-", "_")
    aliases = {
        "dean_rd": "dean_rd",
        "dean_randd": "dean_rd",
        "dean_r_and_d": "dean_rd",
        "dean_and_rd": "dean_rd",
        "research_office_approver": "research_office",
    }
    return aliases.get(role, role)


def _actor_is_authenticated(actor: Any) -> bool:
    return isinstance(actor, dict) and actor.get("is_authenticated") is True and bool(str(actor.get("user_id", "")).strip())


def authorize_review(actor: dict[str, Any]) -> tuple[bool, str]:
    """Check a trusted actor record before granting PI/Research Office authority."""
    if not _actor_is_authenticated(actor):
        return False, "Reviewer identity is missing or not authenticated."
    role = _normal_role(actor.get("role"))
    if role not in APPROVER_ROLES:
        return False, f"Role '{role or 'unknown'}' is not authorized to approve grant releases."
    if actor.get("can_approve") is not True:
        return False, "Reviewer does not have explicit approval permission."
    return True, "Reviewer is authorized."


def authorize_access(actor: dict[str, Any], resource: dict[str, Any], action: str = "read") -> tuple[bool, str]:
    """Apply a simple confidentiality boundary to owner/dept-scoped resources."""
    if not _actor_is_authenticated(actor):
        return False, "Access denied: actor is not authenticated."
    if action not in {"read", "edit", "approve", "rollback"}:
        return False, f"Access denied: unsupported action '{action}'."
    actor_id = str(actor.get("user_id", "")).strip()
    actor_dept = str(actor.get("department", "")).strip().casefold()
    owner_id = str(resource.get("owner_id", "")).strip()
    resource_dept = str(resource.get("department", "")).strip().casefold()
    role = _normal_role(actor.get("role"))
    office_override = role in {"research_office", "dean_rd", "hod", "head_of_department"} and actor.get("can_access_confidential") is True
    owner_match = bool(owner_id) and actor_id == owner_id
    department_match = bool(resource_dept) and actor_dept == resource_dept
    if office_override or owner_match or department_match:
        if action in {"approve", "rollback"}:
            return authorize_review(actor) if action == "approve" else (
                (True, "Rollback permission accepted.") if role in ROLLBACK_ROLES and actor.get("can_rollback") is True
                else (False, "Explicit rollback permission is required.")
            )
        return True, "Access allowed within the permitted ownership/department scope."
    return False, "Access denied: resource belongs to another owner or department."


def evaluation_metrics(state: dict[str, Any]) -> dict[str, Any]:
    """Summarize acceptance/evidence status without changing the state."""
    report = state.get("acceptance_report") if isinstance(state.get("acceptance_report"), dict) else {}
    checks = report.get("checks") if isinstance(report.get("checks"), dict) else {}
    passed = sum(value is True for value in checks.values())
    total = len(checks)
    evidence = state.get("evidence_records") if isinstance(state.get("evidence_records"), list) else []
    return {
        "acceptance_checks_passed": passed,
        "acceptance_checks_total": total,
        "acceptance_pass_rate": round(passed / total, 4) if total else 0.0,
        "evidence_record_count": len(evidence),
        "validation_passed": state.get("validation_passed") is True,
        "acceptance_passed": state.get("acceptance_passed") is True and report.get("all_pass") is True,
        "human_review_status": str(state.get("human_review_status", "unknown")),
    }


def _append_audit(event: dict[str, Any], output_dir: str | Path | None = None) -> Path:
    root = Path(output_dir) if output_dir is not None else _default_output_dir()
    root.mkdir(parents=True, exist_ok=True)
    path = root / "governance_audit.jsonl"
    record = {"event_id": str(uuid.uuid4()), "timestamp": _now(), **event}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def _release_files(output_dir: str | Path | None = None) -> list[Path]:
    root = Path(output_dir) if output_dir is not None else _default_output_dir()
    releases = root / "releases"
    if not releases.exists():
        return []
    result = []
    for path in releases.glob("release_v*.json"):
        try:
            number = int(path.stem.removeprefix("release_v"))
        except ValueError:
            continue
        if number > 0:
            result.append((number, path))
    return [path for _, path in sorted(result)]


def _load_release(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read release file {path.name}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("package"), dict):
        raise ValueError(f"Release file {path.name} has an invalid structure.")
    return data


def record_review_pending(state: dict[str, Any], output_dir: str | Path | None = None) -> dict[str, Any]:
    """Record that a draft awaits a real human decision; never publish it."""
    status = str(state.get("human_review_status", "pending_human_review"))
    if status.startswith("blocked"):
        governance_status = "blocked_review_gate"
    else:
        governance_status = "pending_human_approval"
    audit_path = _append_audit({
        "event": "human_review_pending_or_blocked",
        "governance_status": governance_status,
        "build_status": str(state.get("build_status", "unknown")),
        "metrics": evaluation_metrics(state),
        "published": False,
    }, output_dir)
    return {
        "governance_status": governance_status,
        "release_version": None,
        "release_path": None,
        "governance_audit_path": str(audit_path),
        "evaluation_metrics": evaluation_metrics(state),
    }


def publish_approved_artifact(
    state: dict[str, Any],
    actor: dict[str, Any],
    approval: dict[str, Any],
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Create a versioned release only after validation, acceptance and approval pass."""
    allowed, reason = authorize_review(actor)
    if not allowed:
        audit_path = _append_audit({"event": "release_denied", "reason": reason, "published": False}, output_dir)
        return {"ok": False, "governance_status": "approval_denied", "issues": [reason], "governance_audit_path": str(audit_path)}

    issues: list[str] = []
    if state.get("validation_passed") is not True:
        issues.append("Validation must pass before release.")
    report = state.get("acceptance_report") if isinstance(state.get("acceptance_report"), dict) else {}
    if state.get("acceptance_passed") is not True or report.get("all_pass") is not True:
        issues.append("The Lab 11 acceptance report must pass before release.")
    if not isinstance(approval, dict) or str(approval.get("decision", "")).strip().lower() not in {"approve", "approved"}:
        issues.append("An explicit human approval decision is required.")
    elif str(approval.get("approved_by", "")).strip() != str(actor.get("user_id", "")).strip():
        issues.append("Approval identity does not match the authenticated reviewer.")
    package = state.get("final_package")
    if not isinstance(package, dict) or not package:
        issues.append("A non-empty final package is required.")
    if str(state.get("human_review_status", "")).strip().lower() in {"blocked_validation_failure", "blocked_acceptance_failure"}:
        issues.append("The package is explicitly blocked by a previous hard gate.")

    if issues:
        audit_path = _append_audit({"event": "release_blocked", "issues": issues, "actor_id": actor.get("user_id"), "published": False}, output_dir)
        return {"ok": False, "governance_status": "blocked_release", "issues": issues, "governance_audit_path": str(audit_path)}

    root = Path(output_dir) if output_dir is not None else _default_output_dir()
    release_dir = root / "releases"
    release_dir.mkdir(parents=True, exist_ok=True)
    existing = _release_files(output_dir)
    version = 1
    if existing:
        version = max(int(path.stem.removeprefix("release_v")) for path in existing) + 1
    now = _now()
    released_package = deepcopy(package)
    released_package["status"] = "approved"
    released_package["release_version"] = version
    released_package["approved_at"] = now
    released_package["approved_by"] = str(actor["user_id"])
    release = {
        "schema_version": "lab12.release.v1",
        "version": version,
        "status": "published_approved",
        "published_at": now,
        "approved_by": str(actor["user_id"]),
        "approver_role": _normal_role(actor.get("role")),
        "approval_note": str(approval.get("note", "")).strip(),
        "rollback_of": None,
        "package": released_package,
        "metrics": evaluation_metrics(state),
    }
    target = release_dir / f"release_v{version}.json"
    target.write_text(json.dumps(release, ensure_ascii=False, indent=2), encoding="utf-8")
    audit_path = _append_audit({"event": "release_published", "release_version": version, "actor_id": actor["user_id"], "published": True, "metrics": release["metrics"]}, output_dir)
    return {"ok": True, "governance_status": "published_approved", "release_version": version, "release_path": str(target), "release": release, "governance_audit_path": str(audit_path)}


def rollback_release(
    target_version: int,
    actor: dict[str, Any],
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Restore content from a prior release as a NEW version; preserve all history."""
    allowed, reason = authorize_review(actor)
    if not allowed or actor.get("can_rollback") is not True:
        reason = reason if not allowed else "Reviewer does not have explicit rollback permission."
        audit_path = _append_audit({"event": "rollback_denied", "reason": reason, "target_version": target_version, "published": False}, output_dir)
        return {"ok": False, "governance_status": "rollback_denied", "issues": [reason], "governance_audit_path": str(audit_path)}

    files = _release_files(output_dir)
    target = next((path for path in files if path.name == f"release_v{target_version}.json"), None)
    if target is None:
        reason = f"Release version {target_version} does not exist."
        audit_path = _append_audit({"event": "rollback_denied", "reason": reason, "target_version": target_version, "published": False}, output_dir)
        return {"ok": False, "governance_status": "rollback_denied", "issues": [reason], "governance_audit_path": str(audit_path)}

    restored = _load_release(target)
    root = Path(output_dir) if output_dir is not None else _default_output_dir()
    release_dir = root / "releases"
    version = max(int(path.stem.removeprefix("release_v")) for path in files) + 1
    now = _now()
    package = deepcopy(restored["package"])
    package["status"] = "approved"
    package["release_version"] = version
    package["rollback_restored_from"] = target_version
    package["approved_at"] = now
    package["approved_by"] = str(actor["user_id"])
    release = {
        "schema_version": "lab12.release.v1",
        "version": version,
        "status": "published_rollback",
        "published_at": now,
        "approved_by": str(actor["user_id"]),
        "approver_role": _normal_role(actor.get("role")),
        "approval_note": f"Rollback to version {target_version}",
        "rollback_of": target_version,
        "package": package,
        "metrics": {},
    }
    target_path = release_dir / f"release_v{version}.json"
    target_path.write_text(json.dumps(release, ensure_ascii=False, indent=2), encoding="utf-8")
    audit_path = _append_audit({"event": "release_rollback", "release_version": version, "restored_from_version": target_version, "actor_id": actor["user_id"], "published": True}, output_dir)
    return {"ok": True, "governance_status": "rollback_published", "release_version": version, "restored_from_version": target_version, "release_path": str(target_path), "release": release, "governance_audit_path": str(audit_path)}
