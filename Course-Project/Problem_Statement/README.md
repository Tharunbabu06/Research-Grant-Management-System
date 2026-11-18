# Problem Statement — Research Grant Management System

**Agentic AI (26ECAC401) · Worklet 13** (Chapter 13 of the *Agentic AI 15 Worklets — 14-Lab Build Book*,
included in [`../docs/originals/`](../docs/originals)).

*From funding-call discovery to a compliant, Dean-R&D-approved submission package.*

## Faculty problem cluster

Scattered funding calls, slow literature and novelty framing, and proposal, budget and compliance
work prepared in silos with no shared source of truth.

**Stakeholders:** Faculty, HoD, Dean R&D, Research Office

**Human authority:** the PI / Research Office, with Dean R&D authorising final submission

**Primary output:** grant proposal and compliance package

## Problems heard

- Faculty miss relevant funding calls because listings are scattered across agency websites and mailing lists.
- Literature review and novelty framing take days of manual searching.
- Proposal drafts, budgets and compliance checklists are prepared in silos with no shared source of truth.
- Dean R&D has no consolidated view of which proposals are in progress, their deadlines or compliance status.
- Compliance issues surface late, close to the submission deadline.

## AI solution direction

Build a Research Grant Management System, owned by the Dean R&D office, that discovers matched
calls, compiles a literature / novelty summary, drafts the proposal, prepares an agency-compliant
budget, runs a compliance check and packages the submission, turning a scattered, deadline-driven
process into one auditable, agency-compliant pipeline.

## Recommended workflow

1. Faculty specifies the research area, target funding types, and consent to use their profile / publication history for matching.
2. The Funding Discovery Agent surfaces matched calls while the Literature Review Agent compiles a related-work and novelty summary, in parallel.
3. The Proposal Drafting Agent drafts the narrative using the matched call's requirements and the literature summary.
4. The Budget Planning Agent prepares an agency-compliant budget while the Compliance Checking Agent runs an eligibility / format check, in parallel.
5. The Submission Agent packages the proposal, budget and compliance checklist into the agency's required format.
6. Dean R&D / HoD / Research Office reviews the package, approves or requests corrections, and authorises final submission.

## Agents, communication order and guardrails

| Order | Agent | Stage | Guardrails |
|---|---|---|---|
| 0 | apniLeap AURA Coordinator | Intake and orchestration | Never bypass human approval; enforce data scope, audit logging, source citation and exception routing |
| 1 | Funding Discovery Agent | Parallel discovery | Verified agencies only; never surface expired or unverified calls; cite source and deadline |
| 2 | Literature Review Agent | Parallel discovery | Every claim cited to a resolvable source; never fabricate; flag thin coverage instead of overstating novelty |
| 3 | Proposal Drafting Agent | Sequential drafting | Draft only within faculty scope; mark AI text; never present preliminary findings as results |
| 4 | Budget Planning Agent | Parallel budget and compliance | Agency templates and ceilings only; flag cap breaches; show the basis for every adjustment |
| 5 | Compliance Checking Agent | Parallel budget and compliance | Check only the matched call's published guidelines; no pass without evidence; ambiguous items go to a human |
| 6 | Submission Agent | Sequential packaging | No submission without sign-off; version-controlled record; no figure change after sign-off without re-review |
| 7 | Dean R&D / HoD / Research Office | Stakeholder approval | Final authority for authorising submission |

## Definition of done

The capstone (Lab 14) is complete when, for a real case, the worklet turns a request into a
validated, evidence-grounded grant proposal and compliance package that passes every check, is
reviewed and approved by the human authority, and is published with a full audit trail, with
light human edits rather than a rewrite.

**Success metrics**

- 100% of validation checks pass before human review (for example, budget totals reconcile).
- Every package is grounded in the funder's guidelines and institutional policy, with an evidence record.
- Zero consequential actions without human approval; a complete audit trail and one-click rollback.

## Constraints

Human approval, privacy and consent, audit log, source citations.
