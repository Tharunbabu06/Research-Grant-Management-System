"""
Lab 9: Deep Research Agent -- Evidence Grounding & Synthesis
============================================================
Domain: Research Grant Management System (Chapter 13 / Lab Guide Lab 9)
Phase: C - Applied Reliability | Goal: Ground every output in cited, in-scope evidence

Description:
In high-stakes academic grant applications, hallucinated citations or fabricated
results lead to immediate desk rejection and ethics violations.
This lab enforces strict evidence grounding:
1. Every claim in the proposal narrative must link to a verified in-scope source
   (approved academic literature, matched agency call guidelines, or institutional policy).
2. Unresolved or fabricated source IDs are rejected outright, not softened.
3. Compiles an explicit Evidence Table linking claims to source locators and direct quotes.
4. Generates an executive briefing comparing consensus findings, direct contradictions,
   and research gaps.

Key concepts demonstrated:
- Strict evidence resolver and in-scope verification.
- Claim-level citation indexing.
- Rejection of ungrounded or out-of-scope claims.
- Traceable synthesis: every sentence in the final summary cites its source ID.

Assignments included:
- Assignment 1: Adding a directly contradicting source (S4 reporting high communication latency).
- Assignment 2: Quality-tier source weighting (Peer-Reviewed Journal > Engineering Report).
"""

from typing import Dict, Any, List, Set
from seed_data import LITERATURE, POLICIES, CALLS


# ==============================================================================
# Evidence Grounding & Scope Resolver
# ==============================================================================

class EvidenceResolver:
    """
    Verifies whether a cited source ID exists in approved institutional databases.
    """
    def __init__(self, selected_call: Dict[str, Any]):
        self.lit_ids: Set[str] = {doc["id"] for doc in LITERATURE}
        self.policy_ids: Set[str] = {p["id"] for p in POLICIES}
        self.guideline_ids: Set[str] = {g["id"] for g in selected_call.get("guidelines", [])}
        self.record_ids: Set[str] = {"rec-personnel", "rec-rates", "rec-institution"}

    def is_in_scope(self, source_id: str, source_type: str, quote: str) -> bool:
        # Quote must be non-empty and substantive
        if not quote or len(quote.strip()) < 10:
            return False

        if source_type == "literature":
            return source_id in self.lit_ids
        elif source_type == "guideline":
            return source_id in self.guideline_ids
        elif source_type == "policy":
            return source_id in self.policy_ids
        elif source_type == "record":
            return source_id in self.record_ids
        return False


def build_evidence_table(claims: List[Dict[str, Any]], resolver: EvidenceResolver) -> Dict[str, Any]:
    """
    Evaluates claims, tags each with grounding status, and rejects ungrounded items.
    """
    records = []
    ungrounded = []

    for c in claims:
        evidence_list = c.get("evidence", [])
        grounded = False
        if evidence_list:
            for ev in evidence_list:
                in_scope = resolver.is_in_scope(ev["sourceId"], ev["sourceType"], ev.get("quote", ""))
                record_entry = {
                    "claim_id": c["id"],
                    "claim_text": c["text"],
                    "section": c["sectionKey"],
                    "source_id": ev["sourceId"],
                    "source_type": ev["sourceType"],
                    "locator": ev.get("locator", ""),
                    "quote": ev.get("quote", ""),
                    "in_scope": in_scope,
                }
                records.append(record_entry)
                if in_scope:
                    grounded = True

        if grounded:
            c["grounded"] = True
        else:
            c["grounded"] = False
            ungrounded.append(c)

    coverage_pct = round(((len(claims) - len(ungrounded)) / len(claims)) * 100, 1) if claims else 0.0

    return {
        "records": records,
        "total_claims": len(claims),
        "grounded_count": len(claims) - len(ungrounded),
        "ungrounded_claims": ungrounded,
        "coverage_pct": coverage_pct,
    }


# ==============================================================================
# Synthesis Engine (Consensus, Contradictions, and Gaps)
# ==============================================================================

def synthesize_literature(sources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Performs deep research synthesis across multiple sources.
    Identifies agreements, contradictions, and gaps.
    """
    agreements = []
    contradictions = []
    gaps = []

    # Agreement check: Federated learning reduces privacy risks
    fl_sources = [s for s in sources if "federated learning" in s.get("abstract", "").lower()]
    if len(fl_sources) >= 2:
        ids = [s["id"] for s in fl_sources[:2]]
        agreements.append(f"[{','.join(ids)}] S1 and S2 agree that federated training avoids centralizing patient fundus images.")

    # Gap detection: Clinical trial validation vs technical testbed
    has_clinical = any("clinical" in s.get("abstract", "").lower() for s in sources)
    has_cost = any("cost" in s.get("abstract", "").lower() for s in sources)
    if not has_cost:
        gaps.append("[gap] Current literature does not evaluate deployment costs of non-mydriatic cameras in sub-district clinics.")

    return {
        "agreements": agreements,
        "contradictions": contradictions,
        "gaps": gaps,
    }


# ==============================================================================
# Graded Assignments
# ==============================================================================

def run_assignment_1_contradicting_source():
    """
    Assignment 1 -- Add a Directly Contradicting Source:
    Introduce source S4 reporting communication latency overhead that contradicts
    claims of zero-overhead edge federated learning.
    """
    print("\n--- [Assignment 1] Add Directly Contradicting Source ---")
    s4 = {
        "id": "lit-099",
        "title": "Network contention in low-bandwidth rural clinical nodes",
        "abstract": "Federated model aggregation introduces severe communication bottlenecks over 4G links, delaying rounds by up to 14 hours.",
        "quality_tier": "journal",
    }
    extended_sources = list(LITERATURE[:2]) + [s4]

    # Synthesis with contradiction
    synth = synthesize_literature(extended_sources)
    synth["contradictions"].append(
        f"[{extended_sources[0]['id']} vs {s4['id']}] CONTRADICTION: S1 claims seamless decentralized training, "
        f"whereas S4 proves significant communication delays under rural bandwidth constraints."
    )

    print("Synthesis with Contradiction:")
    for a in synth["agreements"]:
        print(f"  Agreement: {a}")
    for c in synth["contradictions"]:
        print(f"  Contradiction: {c}")


def run_assignment_2_source_quality_weighting():
    """
    Assignment 2 -- Weight Sources by Quality Tier:
    Peer-Reviewed Journal > Conference > Vendor Whitepaper.
    """
    print("\n--- [Assignment 2] Source Quality Tier Weighting ---")
    weighted_sources = [
        {"id": "S1", "tier": "peer_reviewed_journal", "weight": 1.0, "claim": "92% sensitivity achieved"},
        {"id": "S2", "tier": "vendor_whitepaper", "weight": 0.4, "claim": "99% sensitivity claimed"},
    ]
    # Reconcile claim leaning toward peer-reviewed journal
    preferred = max(weighted_sources, key=lambda x: x["weight"])
    downweighted = min(weighted_sources, key=lambda x: x["weight"])
    print(f"Synthesis resolves toward {preferred['id']} ({preferred['tier']}, weight={preferred['weight']}): '{preferred['claim']}'")
    print(f"Explicit disclosure: {downweighted['id']} ({downweighted['tier']}, weight={downweighted['weight']}) was down-weighted.")


# ==============================================================================
# Main Demonstration
# ==============================================================================

if __name__ == "__main__":
    print("======================================================================")
    print("Lab 9: Deep Research Agent -- Evidence Grounding & Synthesis")
    print("======================================================================")

    call = CALLS[0]  # SERB CRG
    resolver = EvidenceResolver(selected_call=call)

    # Candidate claims generated for proposal
    candidate_claims = [
        {
            "id": "C-001",
            "sectionKey": "background",
            "text": "Federated learning enables 4-site screening without centralizing patient fundus images.",
            "evidence": [
                {
                    "sourceId": "lit-001",
                    "sourceType": "literature",
                    "locator": "Journal of Medical AI Research 2024",
                    "quote": "A four-site federated study reports comparable sensitivity to centralised training while keeping 1.2 million images inside clinics.",
                }
            ],
        },
        {
            "id": "C-002",
            "sectionKey": "compliance",
            "text": "The project requires Institutional Ethics Committee clearance before fund release.",
            "evidence": [
                {
                    "sourceId": "pol-ethics",
                    "sourceType": "policy",
                    "locator": "Institutional Ethics Policy",
                    "quote": "Any proposal involving human participants requires Institutional Ethics Committee approval.",
                }
            ],
        },
        {
            "id": "C-003",
            "sectionKey": "methodology",
            "text": "The system achieves 100% diagnostic accuracy on all retinal disease stages.",
            "evidence": [
                {
                    "sourceId": "lit-hallucinated-999",  # FAKE SOURCE
                    "sourceType": "literature",
                    "locator": "Unpublished blog post",
                    "quote": "We achieved 100% accuracy.",
                }
            ],
        },
    ]

    # 1. Grounding Verification
    print("=== 1. Grounding Evaluation of Proposal Claims ===")
    table = build_evidence_table(candidate_claims, resolver)
    print(f"Evidence Coverage: {table['coverage_pct']}% ({table['grounded_count']}/{table['total_claims']} grounded)")

    print("\nEvidence Table Records:")
    for r in table["records"]:
        status = "IN-SCOPE" if r["in_scope"] else "REJECTED (OUT-OF-SCOPE)"
        print(f"  [{r['claim_id']}] -> Source: {r['source_id']} ({r['source_type']}) | Status: {status}")

    print(f"\nRejected Ungrounded Claims Count: {len(table['ungrounded_claims'])}")
    for uc in table["ungrounded_claims"]:
        print(f"  REJECTED CLAIM: '{uc['text']}' (Source '{uc['evidence'][0]['sourceId']}' not found in approved corpus)")

    # 2. Evidence Synthesis
    print("\n=== 2. Literature Synthesis & Traceable Briefing ===")
    synthesis = synthesize_literature(LITERATURE[:4])
    for ag in synthesis["agreements"]:
        print(f"  Agreement: {ag}")
    for gp in synthesis["gaps"]:
        print(f"  Gap: {gp}")

    # 3. Assignments
    run_assignment_1_contradicting_source()
    run_assignment_2_source_quality_weighting()
