"""
Lab 4: Memory and Retrieval -- State vs Stored (Context Design)
==============================================================
Domain: Research Grant Management System (Chapter 13 / Lab Guide Lab 4)
Phase: A - Foundations | Goal: Separate short-term run state from long-term stored knowledge

Description:
Separates short-term session state (the active proposal draft, temporary calculations)
from long-term stored knowledge (approved literature corpus, historical grant outcomes,
and institutional policy decisions).

Key concepts demonstrated:
- Strict separation of working memory (session state) and long-term persistent store.
- Structured MemoryRecord with topic, fact, date, author, and source attribution.
- Scoped retrieval (no full memory dumping; topic-scoped and tag-filtered lookup).
- TF-IDF / keyword similarity retrieval over the academic literature corpus.
- Conflict detection: flags conflicts with existing policy rather than silently overwriting.
- Permission-gated write access: only authorized roles ('dean', 'research_office') may write.
- LangChain Retriever adapter demonstration.

Assignments included:
- Assignment 1: Isolated topic retrieval (proving zero leakage between 'overhead_rate' and 'ethics').
- Assignment 2: Staleness / retention check (warning when retrieved decisions exceed age threshold).
"""

import math
import re
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from seed_data import LITERATURE, HISTORY, POLICIES


# ==============================================================================
# Structured Memory Models & Record Types
# ==============================================================================

@dataclass
class MemoryRecord:
    topic: str
    fact: str
    date: str
    source: str = "memory"
    author_role: str = "research_office"
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProjectMemoryStore:
    """
    Long-term persistent memory store with role-gated write permissions
    and scoped retrieval.
    """
    def __init__(self):
        self.records: List[MemoryRecord] = []
        self.allowed_writers = {"dean", "research_office"}

    def write(self, record: MemoryRecord, user_role: str):
        """Permission-gated write path."""
        if user_role not in self.allowed_writers:
            raise PermissionError(f"Role '{user_role}' is not permitted to write to institutional memory.")
        self.records.append(record)

    def retrieve(self, topic: str) -> List[MemoryRecord]:
        """Scoped retrieval: returns only records matching the topic."""
        return [r for r in self.records if r.topic.lower() == topic.lower()]


# ==============================================================================
# TF-IDF Cosine Retrieval over Academic Corpus (from backend/src/core.js)
# ==============================================================================

STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'have',
    'in', 'into', 'is', 'it', 'its', 'of', 'on', 'or', 'that', 'the', 'their', 'this',
    'to', 'was', 'were', 'will', 'with', 'within', 'we', 'our', 'can', 'not', 'but'
}

def tokenize(text: str) -> List[str]:
    clean = re.sub(r'[^a-zA-Z0-9\s-]', ' ', str(text).lower())
    return [w for w in clean.split() if len(w) > 2 and w not in STOPWORDS]


class CorpusRetriever:
    """
    Retrieves relevant prior literature and proposal history using TF-IDF cosine similarity.
    Matches the algorithm in backend/src/core.js.
    """
    def __init__(self, docs: List[Dict[str, Any]], text_field_fn):
        self.docs = docs
        self.tfs = [self._term_freq(tokenize(text_field_fn(d))) for d in docs]
        self.df = {}
        for tf in self.tfs:
            for term in tf:
                self.df[term] = self.df.get(term, 0) + 1
        n = len(docs) or 1
        self.idf = {term: math.log(1 + n / (1 + freq)) for term, freq in self.df.items()}
        self.vectors = []
        for tf in self.tfs:
            vec = {t: f * self.idf.get(t, 1.0) for t, f in tf.items()}
            self.vectors.append(vec)

    @staticmethod
    def _term_freq(tokens: List[str]) -> Dict[str, int]:
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t, 0) + 1
        return tf

    @staticmethod
    def _cosine(v1: Dict[str, float], v2: Dict[str, float]) -> float:
        dot = sum(v1[k] * v2[k] for k in v1 if k in v2)
        norm1 = math.sqrt(sum(v * v for v in v1.values()))
        norm2 = math.sqrt(sum(v * v for v in v2.values()))
        if not norm1 or not norm2:
            return 0.0
        return dot / (norm1 * norm2)

    def retrieve_similar(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        q_tokens = tokenize(query)
        q_tf = self._term_freq(q_tokens)
        q_vec = {t: f * self.idf.get(t, math.log(2)) for t, f in q_tf.items()}

        scored = []
        for i, doc in enumerate(self.docs):
            score = self._cosine(q_vec, self.vectors[i])
            if score > 0:
                scored.append({"doc": doc, "similarity": round(score, 4)})

        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:k]


# ==============================================================================
# LangChain Retriever Adapter Pattern
# ==============================================================================

class LangChainRetrieverAdapter:
    """
    Adapter demonstrating standard LangChain BaseRetriever contract:
    get_relevant_documents(query) -> List[Document].
    """
    def __init__(self, corpus_retriever: CorpusRetriever):
        self.retriever = corpus_retriever

    def get_relevant_documents(self, query: str):
        results = self.retriever.retrieve_similar(query)
        # Convert to LangChain-style Document format
        return [
            {
                "page_content": f"{r['doc']['title']} - {r['doc'].get('abstract', '')}",
                "metadata": {"id": r["doc"]["id"], "score": r["similarity"]},
            }
            for r in results
        ]


# ==============================================================================
# Project Assistant (Working Memory vs Stored Memory)
# ==============================================================================

class ProjectAssistant:
    def __init__(self, memory_store: ProjectMemoryStore, lit_retriever: CorpusRetriever):
        self.memory_store = memory_store
        self.lit_retriever = lit_retriever
        self.session_state = {}  # Working state (current active draft)

    def answer_topic(self, topic: str, staleness_days: Optional[int] = None) -> str:
        """Answers from scoped long-term memory with explicit source citation."""
        hits = self.memory_store.retrieve(topic)
        if not hits:
            return f"[session] No stored institutional decision on '{topic}' yet."

        latest = hits[-1]
        warning = ""
        if staleness_days:
            rec_date = datetime.strptime(latest.date, "%Y-%m-%d").date()
            age_days = (date.today() - rec_date).days
            if age_days > staleness_days:
                warning = f"[STALENESS WARNING: decision is {age_days} days old and may be out of date] "

        return f"{warning}[memory, dated {latest.date}] Per institutional decision on '{latest.topic}': {latest.fact}"

    def receive_new_statement(self, topic: str, new_fact: str, user_role: str) -> Dict[str, Any]:
        """
        Conflict detection: compares against latest decision before writing.
        """
        hits = self.memory_store.retrieve(topic)
        if hits and hits[-1].fact.lower() != new_fact.lower():
            return {
                "conflict": True,
                "stored": hits[-1].fact,
                "stored_date": hits[-1].date,
                "new": new_fact,
                "message": (
                    f"CONFLICT DETECTED: Proposed fact '{new_fact}' conflicts with "
                    f"existing decision from {hits[-1].date} ('{hits[-1].fact}'). "
                    f"Requires Dean approval to overwrite."
                ),
            }

        # Safe to write (still permission checked)
        record = MemoryRecord(
            topic=topic,
            fact=new_fact,
            date=str(date.today()),
            author_role=user_role,
        )
        self.memory_store.write(record, user_role)
        return {"conflict": False, "written": True, "message": f"Recorded new fact for '{topic}'."}


# ==============================================================================
# Graded Assignments
# ==============================================================================

def run_assignment_1_isolated_topics(assistant: ProjectAssistant):
    """
    Assignment 1 -- Two Isolated Topics:
    Demonstrate that querying 'overhead_rate' returns only overhead facts and never
    leaks facts from 'ethics_policy', and vice versa.
    """
    print("\n--- [Assignment 1] Isolated Topic Scoping Test ---")
    assistant.receive_new_statement(
        "overhead_rate", "Institutional overhead is set to 15% of direct costs", user_role="dean"
    )
    assistant.receive_new_statement(
        "ethics_policy", "Clinical trials must have Institutional Ethics Committee clearance", user_role="dean"
    )

    ans_overhead = assistant.answer_topic("overhead_rate")
    ans_ethics = assistant.answer_topic("ethics_policy")

    print(f"Query 'overhead_rate': {ans_overhead}")
    print(f"Query 'ethics_policy': {ans_ethics}")

    assert "ethics" not in ans_overhead.lower(), "Leakage detected: ethics mentioned in overhead answer!"
    assert "overhead" not in ans_ethics.lower(), "Leakage detected: overhead mentioned in ethics answer!"
    print("Verification passed: Strict topic boundary enforced with zero leakage.")


def run_assignment_2_staleness_policy(assistant: ProjectAssistant):
    """
    Assignment 2 -- Staleness / Retention Policy:
    Add a retention_days threshold. If retrieved record exceeds threshold,
    warn the user before answering.
    """
    print("\n--- [Assignment 2] Staleness & Retention Policy Test ---")
    # Fresh record (today)
    assistant.receive_new_statement("salary_ceiling", "JRF salary capped at 37,000 INR/month", user_role="dean")
    # Artificially old record (2 years ago)
    old_date = str(date.today() - timedelta(days=730))
    assistant.memory_store.records.append(
        MemoryRecord(topic="legacy_hardware_grant", fact="Servers require local physical rack", date=old_date, author_role="dean")
    )

    fresh_ans = assistant.answer_topic("salary_ceiling", staleness_days=365)
    stale_ans = assistant.answer_topic("legacy_hardware_grant", staleness_days=365)

    print(f"Fresh Record (under 365 days): {fresh_ans}")
    print(f"Stale Record (over 365 days): {stale_ans}")
    assert "STALENESS WARNING" in stale_ans, "Staleness policy failed to trigger warning!"
    print("Verification passed: Staleness policy warned user about outdated record.")


# ==============================================================================
# Main Demonstration
# ==============================================================================

if __name__ == "__main__":
    print("======================================================================")
    print("Lab 4: Memory and Retrieval -- State vs Stored")
    print("======================================================================")

    # 1. Initialize persistent memory store with seed policy
    mem_store = ProjectMemoryStore()
    mem_store.write(
        MemoryRecord(
            topic="data_residency",
            fact="Patient health data must remain inside participating hospital firewalls",
            date="2026-07-03",
            author_role="dean",
        ),
        user_role="dean",
    )

    # 2. Build TF-IDF retriever for literature corpus
    lit_retriever = CorpusRetriever(
        docs=LITERATURE,
        text_field_fn=lambda d: f"{d['title']} {d['abstract']} {' '.join(d['tags'])}"
    )

    assistant = ProjectAssistant(mem_store, lit_retriever)

    # 3. Retrieve policy fact
    print("\n=== Initial Policy Retrieval ===")
    print(assistant.answer_topic("data_residency"))

    # 4. Conflict detection test
    print("\n--- Conflict Detection: Faculty member proposes cloud migration ---")
    conflict_result = assistant.receive_new_statement(
        topic="data_residency",
        new_fact="Migrate all raw patient fundus images to public US cloud bucket",
        user_role="pi",
    )
    print(conflict_result["message"])

    # 5. Permission violation test
    print("\n--- Permission Gate: Unauthorized role attempting to write ---")
    try:
        mem_store.write(
            MemoryRecord(topic="grant_decision", fact="Approve immediately", date="2026-11-15"),
            user_role="student",
        )
    except PermissionError as e:
        print(f"Blocked as expected: {e}")

    # 6. TF-IDF Literature retrieval demo
    print("\n=== Literature Corpus Cosine Retrieval ===")
    query = "federated learning diabetic retinopathy screening"
    top_lit = lit_retriever.retrieve_similar(query, k=2)
    for hit in top_lit:
        print(f"[{hit['doc']['id']}] Score: {hit['similarity']} | {hit['doc']['title']}")

    # 7. Run Assignments 1 and 2
    run_assignment_1_isolated_topics(assistant)
    run_assignment_2_staleness_policy(assistant)
