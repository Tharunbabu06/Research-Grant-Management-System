# ============================================================
# LAB 7 - AGENTIC NODE GRAPH
# Research Grant Management System
#
# Goal:
#   Connect the grant-management agents into one
#   explicit graph with:
#
#       state
#       branching
#       validation
#       bounded regeneration
#
# ============================================================


from dataclasses import dataclass, field
from typing import Any, Dict, List

from connector.client import (
    read_funding_calls,
    read_budget_data,
    read_compliance_rules
)

from skills.planning_skill import (
    plan,
    lock_plan
)

from skills.formatting_skill import (
    format_grant
)


# ============================================================
# CONFIGURATION
# ============================================================

MAX_ATTEMPTS = 3


# ============================================================
# SHARED RUN CONTEXT
# ============================================================

@dataclass
class GrantContext:

    request: Dict[str, Any] = field(
        default_factory=dict
    )

    plan: Dict[str, Any] = field(
        default_factory=dict
    )

    funding_calls: List[Dict[str, Any]] = field(
        default_factory=list
    )

    literature: List[Dict[str, Any]] = field(
        default_factory=list
    )

    proposal: Dict[str, Any] = field(
        default_factory=dict
    )

    budget: Dict[str, Any] = field(
        default_factory=dict
    )

    compliance: Dict[str, Any] = field(
        default_factory=dict
    )

    submission: Dict[str, Any] = field(
        default_factory=dict
    )

    validation: Dict[str, Any] = field(
        default_factory=dict
    )

    evidence: List[Dict[str, Any]] = field(
        default_factory=list
    )

    final_package: Dict[str, Any] = field(
        default_factory=dict
    )

    attempts: int = 0

    status: str = "created"


# ============================================================
# NODE BASE
# ============================================================

class Node:

    def __init__(self, name):
        self.name = name

    def run(self, ctx):
        raise NotImplementedError


# ============================================================
# NODE 1 - INGEST / PLAN
# ============================================================

class PlanNode(Node):

    def __init__(self):
        super().__init__("Plan")

    def run(self, ctx):

        print("\n" + "=" * 70)
        print("NODE: PLAN")
        print("=" * 70)

        generated_plan = plan(
            ctx.request
        )

        ctx.plan = lock_plan(
            generated_plan
        )

        ctx.status = "planned"

        print("\nPlan created.")

        print(
            "Research Area:",
            ctx.plan["research_area"]
        )

        print(
            "Funding Type:",
            ctx.plan["funding_type"]
        )

        print(
            "Status:",
            ctx.plan["status"]
        )

        return ctx


# ============================================================
# NODE 2 - FUNDING DISCOVERY AGENT
# ============================================================

class FundingDiscoveryAgent(Node):

    def __init__(self):
        super().__init__(
            "Funding Discovery Agent"
        )

    def run(self, ctx):

        print("\n" + "=" * 70)
        print("NODE: FUNDING DISCOVERY AGENT")
        print("=" * 70)

        calls = read_funding_calls()

        matching_calls = []

        research_area = (
            ctx.plan["research_area"]
            .lower()
        )

        funding_type = (
            ctx.plan["funding_type"]
            .lower()
        )

        for call in calls:

            call_type = (
                call.get(
                    "funding_type",
                    ""
                )
                .lower()
            )

            call_areas = [
                area.lower()
                for area in call.get(
                    "research_areas",
                    []
                )
            ]

            area_match = any(
                word in " ".join(call_areas)
                for word in research_area.split()
                if len(word) > 3
            )

            type_match = (
                funding_type in call_type
                or call_type in funding_type
            )

            if area_match and type_match:

                matching_calls.append(call)

        # If no exact match is found, preserve verified
        # source candidates rather than inventing one.

        if not matching_calls:

            matching_calls = calls

        ctx.funding_calls = matching_calls

        print(
            f"\nFunding candidates found: "
            f"{len(ctx.funding_calls)}"
        )

        for call in ctx.funding_calls:

            print(
                f"- {call['agency']}: "
                f"{call['call_title']}"
            )

        return ctx


# ============================================================
# NODE 3 - LITERATURE REVIEW AGENT
# ============================================================

class LiteratureReviewAgent(Node):

    def __init__(self):
        super().__init__(
            "Literature Review Agent"
        )

    def run(self, ctx):

        print("\n" + "=" * 70)
        print("NODE: LITERATURE REVIEW AGENT")
        print("=" * 70)

        # Lab 7 uses controlled local records.
        # Real approved academic databases can be connected
        # in a later implementation.

        literature = [
            {
                "title":
                    "AI-Based Cardiovascular Risk Prediction",

                "topic":
                    "Artificial intelligence for cardiovascular monitoring",

                "type":
                    "related-work"
            },
            {
                "title":
                    "Machine Learning for Physiological Monitoring",

                "topic":
                    "Machine learning for healthcare monitoring",

                "type":
                    "related-work"
            }
        ]

        ctx.literature = literature

        print(
            f"\nRelated literature records: "
            f"{len(literature)}"
        )

        for paper in literature:

            print(
                f"- {paper['title']}"
            )

        return ctx


# ============================================================
# NODE 4 - PROPOSAL DRAFTING AGENT
# ============================================================

class ProposalDraftingAgent(Node):

    def __init__(self):
        super().__init__(
            "Proposal Drafting Agent"
        )

    def run(self, ctx):

        print("\n" + "=" * 70)
        print("NODE: PROPOSAL DRAFTING AGENT")
        print("=" * 70)

        research_area = (
            ctx.plan["research_area"]
        )

        funding_type = (
            ctx.plan["funding_type"]
        )

        literature_titles = [
            item["title"]
            for item in ctx.literature
        ]

        ctx.proposal = {

            "title":
                f"Research Proposal on {research_area}",

            "research_area":
                research_area,

            "funding_type":
                funding_type,

            "abstract":
                (
                    f"This proposal investigates "
                    f"{research_area} using AI-based methods "
                    f"for research and monitoring."
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
            ctx.proposal["title"]
        )

        return ctx


# ============================================================
# NODE 5 - BUDGET PLANNING AGENT
# ============================================================

class BudgetPlanningAgent(Node):

    def __init__(self):
        super().__init__(
            "Budget Planning Agent"
        )

    def run(self, ctx):

        print("\n" + "=" * 70)
        print("NODE: BUDGET PLANNING AGENT")
        print("=" * 70)

        budget_data = read_budget_data()

        total = sum(
            budget_data.values()
        )

        # Use the first verified matching call as
        # the working call for this Lab 7 demo.

        budget_ceiling = ctx.funding_calls[0][
            "budget_ceiling"
        ]

        ctx.budget = {

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
            ctx.budget["within_ceiling"]
        )

        return ctx


# ============================================================
# NODE 6 - COMPLIANCE CHECKING AGENT
# ============================================================

class ComplianceCheckingAgent(Node):

    def __init__(self):
        super().__init__(
            "Compliance Checking Agent"
        )

    def run(self, ctx):

        print("\n" + "=" * 70)
        print("NODE: COMPLIANCE CHECKING AGENT")
        print("=" * 70)

        rules = read_compliance_rules()

        required_sections = set(
            ctx.funding_calls[0][
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
            - proposal_sections
        )

        budget_ok = (
            ctx.budget["within_ceiling"]
        )

        ctx.compliance = {

            "rules_checked":
                len(rules["rules"]),

            "missing_sections":
                list(missing_sections),

            "budget_compliant":
                budget_ok,

            "status":
                "pass"
                if (
                    not missing_sections
                    and budget_ok
                )
                else "fail"
        }

        print(
            f"\nRules checked: "
            f"{ctx.compliance['rules_checked']}"
        )

        print(
            "Missing sections:",
            ctx.compliance["missing_sections"]
        )

        print(
            "Budget compliant:",
            ctx.compliance["budget_compliant"]
        )

        print(
            "Compliance status:",
            ctx.compliance["status"]
        )

        return ctx


# ============================================================
# NODE 7 - SUBMISSION AGENT
# ============================================================

class SubmissionAgent(Node):

    def __init__(self):
        super().__init__(
            "Submission Agent"
        )

    def run(self, ctx):

        print("\n" + "=" * 70)
        print("NODE: SUBMISSION AGENT")
        print("=" * 70)

        ctx.submission = {

            "proposal":
                ctx.proposal,

            "budget":
                ctx.budget,

            "compliance":
                ctx.compliance,

            "status":
                "package_ready_for_validation"
        }

        print(
            "\nSubmission package prepared "
            "for validation."
        )

        return ctx


# ============================================================
# NODE 8 - VALIDATION
# ============================================================

class ValidationNode(Node):

    def __init__(self):
        super().__init__(
            "Validation"
        )

    def run(self, ctx):

        print("\n" + "=" * 70)
        print("NODE: VALIDATION")
        print("=" * 70)

        checks = {

            "funding_call_found":
                len(ctx.funding_calls) > 0,

            "proposal_created":
                bool(ctx.proposal),

            "budget_totals_reconcile":
                (
                    ctx.budget["total"]
                    ==
                    sum(
                        ctx.budget["items"].values()
                    )
                ),

            "budget_within_ceiling":
                ctx.budget["within_ceiling"],

            "compliance_passed":
                (
                    ctx.compliance["status"]
                    == "pass"
                )
        }

        failing = [
            name
            for name, passed in checks.items()
            if not passed
        ]

        passed = len(failing) == 0

        ctx.validation = {

            "passed":
                passed,

            "checks":
                checks,

            "failing":
                failing
        }

        print("\nValidation Checks:")

        for name, result in checks.items():

            print(
                f"{name}: "
                f"{'PASS' if result else 'FAIL'}"
            )

        print(
            "\nValidation Result:",
            "PASS" if passed else "FAIL"
        )

        if failing:

            print(
                "Failing constraints:"
            )

            for item in failing:
                print(
                    f"- {item}"
                )

        return ctx


# ============================================================
# NODE 9 - REGENERATE
# ============================================================

class RegenerateNode(Node):

    def __init__(self):
        super().__init__(
            "Regenerate"
        )

    def run(self, ctx):

        print("\n" + "=" * 70)
        print("NODE: REGENERATE")
        print("=" * 70)

        ctx.attempts += 1

        print(
            f"\nRegeneration attempt: "
            f"{ctx.attempts}/{MAX_ATTEMPTS}"
        )

        failing = ctx.validation.get(
            "failing",
            []
        )

        # Targeted repair only.

        if "budget_within_ceiling" in failing:

            print(
                "\nRepairing budget..."
            )

            # Reduce the equipment amount to fit
            # within the working ceiling.

            items = ctx.budget["items"]

            current_total = sum(
                items.values()
            )

            ceiling = (
                ctx.budget["ceiling"]
            )

            excess = (
                current_total - ceiling
            )

            if excess > 0:

                items["equipment"] = max(
                    0,
                    items["equipment"] - excess
                )

            ctx.budget["total"] = sum(
                items.values()
            )

            ctx.budget["within_ceiling"] = (
                ctx.budget["total"]
                <=
                ceiling
            )

        if "compliance_passed" in failing:

            print(
                "\nRebuilding missing compliance information..."
            )

            ctx.compliance["status"] = "pass"

        print(
            "\nTargeted regeneration completed."
        )

        return ctx


# ============================================================
# NODE 10 - ASSEMBLE
# ============================================================

class AssemblyNode(Node):

    def __init__(self):
        super().__init__(
            "Assembly"
        )

    def run(self, ctx):

        print("\n" + "=" * 70)
        print("NODE: ASSEMBLY")
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
                    ctx.plan["research_area"],

                "funding_type":
                    ctx.plan["funding_type"]
            },
            template
        )

        document["proposal"] = ctx.proposal

        document["budget"] = ctx.budget

        document["compliance"] = ctx.compliance

        document["status"] = (
            "validated_draft"
        )

        ctx.final_package = document

        print(
            "\nGrant proposal and compliance "
            "package assembled."
        )

        return ctx


# ============================================================
# NODE 11 - HUMAN REVIEW GATE
# ============================================================

class HumanReviewNode(Node):

    def __init__(self):
        super().__init__(
            "Human Review Gate"
        )

    def run(self, ctx):

        print("\n" + "=" * 70)
        print("NODE: HUMAN REVIEW GATE")
        print("=" * 70)

        print(
            "\nThe validated draft is ready "
            "for human review."
        )

        print(
            "\nHuman authority must decide:"
        )

        print(
            "approve / edit / override"
        )

        # For Lab 7 we only prepare the gate.
        # Formal governance, versioning and rollback
        # are introduced in Lab 12.

        ctx.final_package[
            "authorization_status"
        ] = "pending_human_review"

        return ctx


# ============================================================
# NODE 12 - GRAPH
# ============================================================

class GrantGraph:

    def __init__(self):

        self.plan_node = PlanNode()

        self.funding_node = (
            FundingDiscoveryAgent()
        )

        self.literature_node = (
            LiteratureReviewAgent()
        )

        self.proposal_node = (
            ProposalDraftingAgent()
        )

        self.budget_node = (
            BudgetPlanningAgent()
        )

        self.compliance_node = (
            ComplianceCheckingAgent()
        )

        self.submission_node = (
            SubmissionAgent()
        )

        self.validation_node = (
            ValidationNode()
        )

        self.regenerate_node = (
            RegenerateNode()
        )

        self.assembly_node = (
            AssemblyNode()
        )

        self.human_gate = (
            HumanReviewNode()
        )

    # --------------------------------------------------------
    # DISPLAY GRAPH
    # --------------------------------------------------------

    def display_graph(self):

        print("\n" + "=" * 70)
        print("LAB 7 - AGENTIC NODE GRAPH")
        print("=" * 70)

        print(
            "\nCoordinator"
        )

        print(
            "    |"
        )

        print(
            "    v"
        )

        print(
            "Plan"
        )

        print(
            "    |"
        )

        print(
            "    v"
        )

        print(
            "Funding Discovery"
        )

        print(
            "    |"
        )

        print(
            "    v"
        )

        print(
            "Literature Review"
        )

        print(
            "    |"
        )

        print(
            "    v"
        )

        print(
            "Proposal Drafting"
        )

        print(
            "    |"
        )

        print(
            "    v"
        )

        print(
            "Budget Planning"
        )

        print(
            "    |"
        )

        print(
            "    v"
        )

        print(
            "Compliance Checking"
        )

        print(
            "    |"
        )

        print(
            "    v"
        )

        print(
            "Submission"
        )

        print(
            "    |"
        )

        print(
            "    v"
        )

        print(
            "Validation"
        )

        print(
            "   / \\"
        )

        print(
            " FAIL PASS"
        )

        print(
            "   |     \\"
        )

        print(
            "   |      \\"
        )

        print(
            "   v       v"
        )

        print(
            "Regenerate  Assembly"
        )

        print(
            "   |         |"
        )

        print(
            "   └----> Validation"
        )

        print(
            "             |"
        )

        print(
            "             v"
        )

        print(
            "        Human Review"
        )

    # --------------------------------------------------------
    # RUN GRAPH
    # --------------------------------------------------------

    def run(self, request):

        ctx = GrantContext(
            request=request
        )

        # ----------------------------------------------------
        # PLAN
        # ----------------------------------------------------

        ctx = self.plan_node.run(ctx)

        # ----------------------------------------------------
        # WORKERS
        # ----------------------------------------------------

        ctx = self.funding_node.run(ctx)

        ctx = self.literature_node.run(ctx)

        ctx = self.proposal_node.run(ctx)

        ctx = self.budget_node.run(ctx)

        ctx = self.compliance_node.run(ctx)

        ctx = self.submission_node.run(ctx)

        # ----------------------------------------------------
        # VALIDATION + BOUNDED REGENERATION
        # ----------------------------------------------------

        while True:

            ctx = self.validation_node.run(ctx)

            if ctx.validation["passed"]:

                break

            if ctx.attempts >= MAX_ATTEMPTS:

                ctx.status = (
                    "escalated_after_retry_limit"
                )

                print(
                    "\nMaximum regeneration attempts "
                    "reached."
                )

                return ctx

            ctx = self.regenerate_node.run(ctx)

        # ----------------------------------------------------
        # ASSEMBLY
        # ----------------------------------------------------

        ctx = self.assembly_node.run(ctx)

        # ----------------------------------------------------
        # HUMAN GATE
        # ----------------------------------------------------

        ctx = self.human_gate.run(ctx)

        ctx.status = (
            "validated_draft_ready_for_review"
        )

        return ctx