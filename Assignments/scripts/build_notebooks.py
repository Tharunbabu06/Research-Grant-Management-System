"""
build_notebooks.py -- regenerate the Lab 1-14 notebooks from the lab scripts.

Each `labNN_*.py` script in this folder is the source of truth for a lab. This
tool turns it into a standalone Jupyter notebook in `Assignments/`:

  * the module docstring becomes the notebook header,
  * `seed_data.py` is written to disk by the notebook itself (so it runs in
    Colab with nothing else uploaded),
  * every top-level class / function becomes its own code cell,
  * the `if __name__ == "__main__":` block becomes the "Run the lab" cell,
  * a final cell runs the acceptance checks against the captured console
    trace and exports `labN_artifacts/`.

Usage (from the repository root):

    pip install -r requirements.txt
    python Assignments/scripts/build_notebooks.py            # build + execute
    python Assignments/scripts/build_notebooks.py --no-run   # build only
"""

import ast
import re
import shutil
import sys
import tempfile
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

HERE = Path(__file__).resolve().parent
ASSIGNMENTS = HERE.parent
EVIDENCE = ASSIGNMENTS.parent / "Course-Project" / "evidence"
WORKLET = 13

# file stem -> (notebook suffix, acceptance checks as (label, regex, min_count))
LABS = {
    "lab01_agent_vs_chatbot": ("Agent_vs_Chatbot", [
        ("Vague request triggers the clarify step before any plan", r"Step 1: Initial Run with Vague Inputs", 1),
        ("Feedback round 1 adds the Clinical Site Validation work package", r"Work packages after Round 1: .*Clinical Site Validation", 1),
        ("Feedback round 2 shortens data curation to 3 months", r"Data curation duration after Round 2: 3 months", 1),
        ("Both rounds mutate the same plan object (no regeneration)", r"Verification passed: Both rounds mutated the same plan instance", 1),
        ("Budget/ceiling conflict is detected before plan lock", r"CONFLICT DETECTED", 1),
        ("Iteration log records revisions without restarting the loop", r"revision applied without restarting loop", 2),
    ]),
    "lab02_tool_using_agent": ("Tool_Using_Agent", [
        ("Budget total is computed by a tool, not asserted", r"Grand Total = INR 5,433,600", 1),
        ("Unknown call id fails gracefully through the tool layer", r"Graceful failure reported", 1),
        ("Notification tool drafts but never sends", r"DRAFTED_NOT_SENT", 1),
        ("Three-tool chain completes with an eligibility verdict", r"3-Tool Chain Result: .*Eligible = True", 1),
        ("Every tool call is traced with a reason", r"^\d+\. tool=\w+ \| reason=", 8),
        ("Eligibility is checked by its own typed tool", r"tool=check_eligibility", 1),
    ]),
    "lab03_skill_creation": ("Skill_Creation", [
        ("Government plan is produced and locked", r"Locked: True", 1),
        ("Same plan skill serves the Industry/CSR domain", r"Generated Industry Plan: PLAN-INDUSTRY", 1),
        ("Both domains share one output schema", r"Identical Schema: True", 1),
        ("Each locked plan has its own integrity checksum", r"Distinct Integrity Checksums: True", 1),
        ("Skill is declared reusable across domains", r"SKILL IS REUSABLE ACROSS DOMAINS", 1),
        ("Format skill discloses AI-assisted drafting", r"AI-assisted drafting", 1),
        ("Contract violation (missing objectives) is refused", r"PASS: Contract violation caught as expected", 1),
    ]),
    "lab04_memory_and_retrieval": ("Memory_and_Retrieval", [
        ("Policy retrieval by tag returns stored reference", r"Initial Policy Retrieval", 1),
        ("Literature retrieved by TF-IDF cosine similarity", r"Literature Corpus Cosine Retrieval", 1),
        ("Topic scopes are isolated with zero leakage", r"Verification passed: Strict topic boundary enforced with zero leakage", 1),
        ("Stale records raise a warning instead of being trusted", r"Verification passed: Staleness policy warned user", 1),
    ]),
    "lab05_mcp_connector": ("MCP_Connector", [
        ("Capabilities are discovered from the manifest", r"\[TOOL\] query_guidelines", 1),
        ("Funding calls are read through the connector", r"Retrieved \d+ government calls", 1),
        ("A capability added later is discovered and invoked dynamically", r"Invoked 'history\.stats' dynamically", 1),
        ("A bad agent token is refused", r"Unauthorized: invalid agent token", 1),
        ("An unpermitted caller cannot read HR records", r"Permission denied: caller 'guest_agent'", 1),
        ("Every connector call lands in the server audit log", r"\| Caller: \w+ \| Endpoint: [\w.]+ \| Status: ok", 4),
    ]),
    "lab06_runtime": ("Runtime", [
        ("Budget skill runs two tools inside the runtime", r"'total': 5175000", 1),
        ("A third skill is registered after the runtime is built", r"Post-Hoc Registered Third Skill", 1),
        ("Per-user session rate limit rejects the 4th task", r"PASS: 4th task rejected as expected", 1),
        ("Two failures escalate to the human authority", r"ESCALATED TO HUMAN AUTHORITY", 1),
        ("Memory is scoped per user", r"Scoped Memory for User", 1),
        ("Checkpoints are captured after each skill", r"CKPT-\d{3} \| after_", 3),
    ]),
    "lab07_agentic_node_graph": ("Node_Graph", [
        ("Success path reaches the Dean human gate", r"\[NODE\] dean_human_gate .*Success: True", 1),
        ("Failed drafting node triggers the bounded retry back-edge", r"\[RECOVERY\] Bounded Retry \(1/2\)", 1),
        ("LangGraph StateGraph mapping is specified", r"StateGraph", 1),
        ("Added ethics-screening node halts the pipeline", r"Graph halted at node 'ethics_screening' as expected", 1),
        ("Retry limit on the budget node is enforced and recorded", r"Retry events captured: 1", 1),
        ("Run stops at awaiting_dean_review, never auto-submits", r"awaiting_dean_review", 1),
    ]),
    "lab08_parallel_swarm": ("Parallel_Swarm", [
        ("Four specialists fan out in a real thread pool", r"Launching 4 specialist agents in parallel via ThreadPoolExecutor", 1),
        ("Merge covers every unit required by the plan", r"All Required Units Covered: True", 1),
        ("Cross-agent conflict is detected and resolved by rule", r"Resolution applied", 1),
        ("Fifth role (data management) joins the swarm", r"Unit 'data_management': covered", 1),
        ("Specialist critique raises a blocking finding", r"\(BLOCKING\)", 1),
        ("Specialist critique raises an advisory finding", r"\(ADVISORY\)", 1),
    ]),
    "lab09_deep_research": ("Deep_Research_Grounding", [
        ("Evidence coverage is measured per claim", r"Evidence Coverage: [\d.]+% \(2/3 grounded\)", 1),
        ("Hallucinated source is rejected as out of scope", r"REJECTED \(OUT-OF-SCOPE\)", 1),
        ("Ungrounded claim is removed, not softened", r"Rejected Ungrounded Claims Count: 1", 1),
        ("Synthesis reports a literature gap", r"\[gap\]", 1),
        ("A directly contradicting source is surfaced", r"CONTRADICTION", 1),
        ("Lower-tier source is down-weighted and disclosed", r"down-weighted", 1),
    ]),
    "lab10_ops_resilience": ("Ops_Resilience", [
        ("Four deliberate faults are injected", r"Initial State Injected with 4 Deliberate Faults", 1),
        ("Self-healing loop succeeds", r"Self-Healing Outcome: SUCCESS", 1),
        ("Recovery stays inside the 3-attempt budget", r"Total Recovery Attempts Used: [1-3]/3", 1),
        ("Each fault is diagnosed and repaired surgically", r"\[Attempt \d\] [A-Z_]+ \(", 4),
        ("Repaired state has the methodology section", r"Methodology section present: True", 1),
        ("Expired call is diagnosed and swapped", r"is EXPIRED", 1),
        ("High-risk remediation halts at the human gate", r"AWAITING_DEAN_APPROVAL", 1),
    ]),
    "lab11_sdlc_factory": ("SDLC_Factory", [
        ("Acceptance suite derived from the spec runs green", r"\[PASS\] TC-\d\d", 7),
        ("Hard gate passes and advances to the Dean", r"Hard Acceptance Gate Outcome: PASSED", 1),
        ("Lineage is kept per concurrent user story", r"Verification passed: Lineage correctly attributed", 1),
        ("Deliberate bug makes the suite fail", r"Test Suite Passed: False", 1),
        ("The independent test catches the defect", r"\[DEFECT CAUGHT\] TC-03", 1),
    ]),
    "lab12_safety_governance": ("Safety_and_Governance", [
        ("Proposal without a rollback plan is rejected", r"No rollback contingency plan defined", 1),
        ("Unscrubbed patient data is rejected", r"unscrubbed patient data", 1),
        ("PI cannot approve their own proposal", r"does not hold 'review:approve' permission", 1),
        ("Dean R&D authorises publication", r"Dean R&D Authorizes Publication", 1),
        ("One-click rollback is demonstrated", r"One-Click Rollback Demonstration", 1),
        ("Finance clearance gate enforced above the threshold", r"Verification passed: Financial threshold control strictly enforced", 1),
        ("Periodic re-evaluation gate enforced", r"Verification passed: Periodic re-evaluation successfully enforced", 1),
    ]),
    "lab13_discipline_specialists": ("Domain_Specialists", [
        ("Government and Industry/CSR specialist contracts pass", r"^Contract Passed: True", 2),
        ("Domain transfer never auto-executes a risky action", r"Auto-Executed: False", 1),
        ("International (EU Horizon) specialist added and passes", r"International Specialist Contract Check: True", 1),
        ("Trend-based escalation succeeds", r"Verification passed: Trend-based escalation succeeded", 1),
    ]),
    "lab14_capstone": ("Capstone", [
        ("End-to-end run stops at the Dean review gate", r"Status after acceptance gate: awaiting_dean_review", 1),
        ("Package carries a SHA-256 integrity checksum", r"Integrity Checksum: [0-9a-f]{64}", 1),
        ("Dean approval publishes version v1", r"Status=published, Version=v1", 1),
        ("Sanctioned project portfolio (30 projects) is available", r"Sample from 30 Total", 1),
        ("Second reusable skill runs on pipeline state", r"Verification passed: Second skill executed cleanly", 1),
        ("Regression + adversarial cases all pass", r"\[PASS\] Case '", 3),
        ("PI self-approval is blocked", r"\[PASS\] Blocked unauthorized approval as expected", 1),
        ("Limitations and roadmap are stated", r"Stated Limitations & Next-Step Roadmap", 1),
    ]),
}

TEE_CELL = '''# Console capture: everything the lab prints is shown below AND kept in memory,
# so the acceptance checks in the last cell can assert on the real run.
import io
import sys


class ConsoleTee(io.StringIO):
    """Mirror stdout into a buffer while the lab runs."""

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self
        return self

    def __exit__(self, *exc):
        sys.stdout = self._stdout
        return False

    def write(self, text):
        self._stdout.write(text)
        return super().write(text)


console = ConsoleTee()'''

CHECK_CELL = '''import json
import re
from pathlib import Path

LAB = {lab}
CHECKS = {checks}

trace = console.getvalue()
universal = [
    ("Run produced console output", r"\\S", 1),
    ("Graded Assignment 1 executed", r"\\[Assignment 1\\]", 1),
    ("Graded Assignment 2 executed", r"\\[Assignment 2\\]", 1),
]
results = []
for label, pattern, minimum in universal + CHECKS:
    found = len(re.findall(pattern, trace, flags=re.MULTILINE))
    results.append({{"check": label, "pattern": pattern, "expected_min": minimum,
                    "found": found, "passed": found >= minimum}})
no_errors = "Traceback (most recent call last)" not in trace
results.append({{"check": "No unhandled exception in the run", "pattern": "Traceback",
                "expected_min": 0, "found": 0 if no_errors else 1, "passed": no_errors}})

for i, r in enumerate(results, 1):
    print(f"[{{'PASS' if r['passed'] else 'FAIL'}}] {{i:>2}}. {{r['check']}}")
passed = sum(r["passed"] for r in results)
print(f"\\nLab {{LAB}}: {{passed}}/{{len(results)}} acceptance checks passed")

outdir = Path(f"lab{{LAB}}_artifacts")
outdir.mkdir(exist_ok=True)
(outdir / f"lab{{LAB}}_console_trace.txt").write_text(trace, encoding="utf-8")
(outdir / f"lab{{LAB}}_acceptance_checks.json").write_text(
    json.dumps({{"lab": LAB, "passed": passed, "total": len(results), "checks": results}}, indent=2),
    encoding="utf-8")
print("Artifacts written to", outdir.as_posix())

assert passed == len(results), "acceptance checks failed"'''


def split_chunks(src):
    """Split a script into (docstring, [(title, code)], main_body)."""
    tree = ast.parse(src)
    lines = src.splitlines()
    doc = ast.get_docstring(tree)
    body = tree.body[1:]  # skip docstring
    main = next(n for n in body if isinstance(n, ast.If) and "__main__" in ast.unparse(n.test))

    def start_of(node):
        line = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
        i = line - 1  # 0-based index of first line
        while i > 0 and (lines[i - 1].strip() == "" or lines[i - 1].lstrip().startswith("#")):
            i -= 1
        while lines[i].strip() == "":
            i += 1
        return i

    first = start_of(body[0])
    defs = [n for n in body if isinstance(n, (ast.ClassDef, ast.FunctionDef))]
    cuts = [(first, "Imports and fixtures")]
    for n in defs:
        s = start_of(n)
        if s <= cuts[-1][0]:
            cuts[-1] = (cuts[-1][0], cuts[-1][1] if cuts[-1][1] != "Imports and fixtures" or s > first else f"`{n.name}`")
            continue
        kind = "class" if isinstance(n, ast.ClassDef) else "function"
        cuts.append((s, f"`{n.name}` ({kind})"))
    main_start = start_of(main)
    chunks = []
    for (s, title), nxt in zip(cuts, [c[0] for c in cuts[1:]] + [main_start]):
        code = "\n".join(lines[s:nxt]).rstrip()
        if code.strip():
            chunks.append((title, code))
    main_lines = lines[main.lineno:main.end_lineno]
    return doc, chunks, "\n".join(main_lines).rstrip()


def build(stem):
    suffix, checks = LABS[stem]
    n = int(stem[3:5])
    src = (HERE / f"{stem}.py").read_text(encoding="utf-8")
    doc, chunks, main_body = split_chunks(src)
    dl = doc.splitlines()
    title = dl[0].split(":", 1)[1].strip().replace("--", "—")
    meta = {k: v for k, v in (l.split(":", 1) for l in dl[1:] if l.startswith(("Phase", "Domain")))}
    phase, _, goal = meta.get("Phase", "").partition("|")
    rest = "\n".join(l for l in dl[1:] if not l.startswith(("Phase", "Domain", "=")))
    desc = re.sub(r"\n{3,}", "\n\n", rest).strip()
    desc = re.sub(r"^(Description|Assignments included|Key [^\n:]*|Core [^\n:]*|Features[^\n:]*):\s*$",
                  r"**\1**\n", desc, flags=re.MULTILINE)

    cells = [new_markdown_cell(
        f"# Agentic AI Systems — Worklet {WORKLET}\n"
        f"# Research Grant Management System (apniLeap AURA)\n"
        f"## Lab {n} · {title}\n\n"
        f"**Phase {phase.strip().replace(' - ', ' · ')}** &nbsp;|&nbsp; **{goal.strip().replace('Goal:', 'Goal:**')}\n\n"
        f"---\n\n{desc}\n\n---\n\n"
        f"*Runs standalone on Python 3.10+ (Jupyter or Google Colab): no API key, no network, "
        f"standard library only. Source script: [`scripts/{stem}.py`](./scripts/{stem}.py).*"
    )]
    k = 1
    if "seed_data" in src:
        cells.append(new_markdown_cell(
            f"### Cell {k} · Shared institutional seed data\n\n"
            "`seed_data.py` is written to disk so the notebook runs standalone. It is the Python mirror of "
            "the course project's `backend/src/seed.js`: funding calls, literature corpus, policies, "
            "personnel rate card, users and the sanctioned-project portfolio. *(Collapse — shared by all labs.)*"))
        cells.append(new_code_cell("%%writefile seed_data.py\n" + (HERE / "seed_data.py").read_text(encoding="utf-8")))
        k += 1
    for ctitle, code in chunks:
        cells.append(new_markdown_cell(f"### Cell {k} · {ctitle}"))
        cells.append(new_code_cell(code))
        k += 1
    cells.append(new_markdown_cell(
        f"### Cell {k} · Run the lab\n\nThe lab demo and both graded assignments, with the console captured for the checks below."))
    cells.append(new_code_cell(TEE_CELL + "\n\nwith console:\n" + main_body))
    k += 1
    cells.append(new_markdown_cell(
        f"### Cell {k} · Acceptance checks and deliverables\n\n"
        "Each check asserts on the trace of the run above. The trace and the check report are exported to "
        f"`lab{n}_artifacts/` (committed under `Course-Project/evidence/`)."))
    cells.append(new_code_cell(CHECK_CELL.format(lab=n, checks=repr(checks).replace("), (", "),\n    ("))))

    nb = new_notebook(cells=cells, metadata={
        "colab": {"provenance": [], "toc_visible": True},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    })
    return n, f"LAB_{n}_Worklet{WORKLET}_{suffix}.ipynb", nb, len(checks) + 4


def main():
    run = "--no-run" not in sys.argv
    summary = []
    for stem in sorted(LABS):
        n, name, nb, total = build(stem)
        if run:
            from nbclient import NotebookClient
            with tempfile.TemporaryDirectory() as tmp:
                NotebookClient(nb, timeout=300, kernel_name="python3",
                               resources={"metadata": {"path": tmp}}).execute()
                art = Path(tmp) / f"lab{n}_artifacts"
                dest = EVIDENCE / f"lab{n}_artifacts"
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(art, dest)
        nbformat.write(nb, ASSIGNMENTS / name)
        summary.append((n, name, total))
        print(f"Lab {n:>2}: {name}  ({total} checks){'  executed' if run else ''}")
    print(f"\n{len(summary)} notebooks, {sum(t for _, _, t in summary)} acceptance checks.")


if __name__ == "__main__":
    main()
