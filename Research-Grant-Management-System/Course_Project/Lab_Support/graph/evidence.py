import re
"""
Lab 9: Evidence Grounding

Checks whether a claim has traceable, verified,
relevant evidence before it is accepted.
"""

from typing import Any


REQUIRED_FIELDS = [
    "claim",
    "source_type",
    "source_title",
    "source_reference",
    "source_locator",
    "excerpt",
]


def validate_evidence_record(
    record: dict[str, Any],
) -> tuple[bool, list[str]]:
    """
    Return (True, []) when evidence is acceptable.
    Otherwise, return (False, reasons).
    """

    issues = []

    # 1. Check that all required evidence fields exist.
    for field in REQUIRED_FIELDS:
        value = record.get(field)

        if not isinstance(value, str) or not value.strip():
            issues.append(f"Missing required field: {field}")

    # 2. Evidence must have been verified.
    if record.get("verified") is not True:
        issues.append("Source has not been verified")

    # 3. Evidence must be relevant to the claim.
    if record.get("in_scope") is not True:
        issues.append("Evidence is not in scope")

    # 4. Return the decision and reasons.
    return len(issues) == 0, issues
def build_funding_evidence_record(
    call: dict[str, Any],
    in_scope: bool,
) -> dict[str, Any]:
    """
    Convert a funding-call record into the
    evidence format used by the Lab 9 checker.
    """

    source = call.get("source", {})

    return {
        "claim": (
            f"Funding-call information for "
            f"{call.get('call_title', 'Unknown call')}"
        ),
        "source_type": source.get("source_type", ""),
        "source_title": source.get("source_title", ""),
        "source_reference": source.get("source_url", ""),
        "source_locator": source.get("source_locator", ""),
        "excerpt": source.get("supporting_excerpt", ""),
        "verified": source.get("verified") is True,
        "in_scope": in_scope is True,
    }

# Conservative topical relevance checks for Lab 9 literature evidence.
# A plain phrase such as "at the heart of endourology" is not cardiovascular evidence.
_CARDIOVASCULAR_RE = re.compile(
    r"\b(cardiovascular|cardiac|myocardial|myocardium|coronary|"
    r"electrocardiogram|electrocardiography|ecg|ekg|echocardiogram|"
    r"echocardiography|ventricular|arrhythmia|atrial fibrillation|"
    r"cardiomyopathy|myocarditis|heart rate|heart rhythm|heart failure|"
    r"heart disease|cardiac output|cardiac function)\b",
    re.IGNORECASE,
)
_AI_METHOD_RE = re.compile(
    r"\b(artificial intelligence|machine[- ]learning|deep[- ]learning|"
    r"neural networks?|\bAI\b|\bML\b|computer vision|"
    r"representation learning|transformer model)\b",
    re.IGNORECASE,
)
_MONITORING_TASK_RE = re.compile(
    r"\b(monitor(?:ed|ing|s)?|predict(?:ed|ion|ive|ing|s)?|"
    r"detect(?:ed|ion|ing|s)?|classif(?:y|ies|ied|ication)|"
    r"diagnos(?:e|ed|is|tic)|screen(?:ed|ing|s)?|sensing|tracking|"
    r"surveillance|risk[- ](?:prediction|stratification|assessment)|"
    r"signal processing|electrocardiogram|electrocardiography|ecg|ekg|"
    r"echocardiogram|echocardiography|motion estimation|imaging|"
    r"real[- ]time|continuous)\b",
    re.IGNORECASE,
)


def literature_relevance_issues(research_area: str, candidate_text: str) -> list[str]:
    """Return topical-screen issues for a paper title plus abstract.

    For AI-based cardiovascular monitoring, a paper must have a specific
    cardiovascular signal, an explicit AI/ML method, and a relevant task.
    This title/abstract screen is a triage step, not proof that a paper supports
    a scientific claim. Full-text review is still needed before citing claims.
    """
    target = (research_area or "").lower()
    text = candidate_text or ""
    is_cardiovascular_target = any(
        term in target for term in ("cardiovascular", "cardiac", "heart", "cardio")
    )
    issues: list[str] = []

    if is_cardiovascular_target:
        if not _CARDIOVASCULAR_RE.search(text):
            issues.append("No explicit cardiovascular-domain term found")
        if not _AI_METHOD_RE.search(text):
            issues.append("No explicit AI/ML method found")
        if not _MONITORING_TASK_RE.search(text):
            issues.append("No monitoring, prediction, detection, or assessment task found")
        return issues

    stop_words = {
        "based", "using", "with", "from", "into", "research", "study",
        "system", "data", "model", "analysis", "method", "methods",
    }
    terms = [
        term for term in re.findall(r"[a-zA-Z][a-zA-Z0-9+-]{2,}", target)
        if term not in stop_words
    ]
    if terms and not any(
        re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE)
        for term in terms
    ):
        issues.append("No meaningful research-area term found in the paper")
    return issues
