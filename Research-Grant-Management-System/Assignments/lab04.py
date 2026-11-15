from pathlib import Path
import sys
SUPPORT = Path(__file__).resolve().parents[1] / "Course_Project" / "Lab_Support"
sys.path.insert(0, str(SUPPORT))

# ============================================================
# LAB 4 - MEMORY & RETRIEVAL
# Research Grant Management System
#
# Goal:
#   Separate short-term run state from long-term memory.
#
# Short-term:
#   Current request
#   Current plan
#   Current draft
#
# Long-term:
#   Previous proposals
#   Stored knowledge
#
# Retrieval:
#   Tag-based
#   Similarity-based
# ============================================================


from memory.session_state import SessionState

from memory.retrieval import (
    load_history,
    retrieve_by_tags,
    retrieve_by_similarity
)


# ============================================================
# COORDINATOR
# ============================================================

class Coordinator:

    def __init__(self):

        # Short-term memory
        self.state = SessionState()

        # Long-term memory
        self.history = load_history()

    # --------------------------------------------------------
    # STEP 1 - CREATE CURRENT REQUEST
    # --------------------------------------------------------

    def create_current_request(self):

        request = (
            "Prepare a government research grant "
            "proposal for AI-based cardiovascular "
            "monitoring."
        )

        self.state.set_request(request)

        return request

    # --------------------------------------------------------
    # STEP 2 - CREATE CURRENT PLAN
    # --------------------------------------------------------

    def create_current_plan(self):

        plan = {
            "research_area":
                "AI-based cardiovascular monitoring",

            "funding_type":
                "Government research grant",

            "duration":
                "24 months"
        }

        self.state.set_plan(plan)

        return plan

    # --------------------------------------------------------
    # STEP 3 - CREATE CURRENT DRAFT
    # --------------------------------------------------------

    def create_current_draft(self):

        draft = (
            "This research proposes an AI-based "
            "cardiovascular monitoring system for "
            "early identification of cardiovascular "
            "abnormalities using physiological and "
            "health-related data."
        )

        self.state.set_draft(draft)

        return draft

    # --------------------------------------------------------
    # STEP 4 - TAG RETRIEVAL
    # --------------------------------------------------------

    def tag_retrieval(self):

        print("\n" + "=" * 70)
        print("LONG-TERM MEMORY - TAG RETRIEVAL")
        print("=" * 70)

        search_tags = [
            "AI",
            "healthcare",
            "cardiovascular"
        ]

        results = retrieve_by_tags(
            self.history,
            search_tags
        )

        print("\nSearch Tags:")

        for tag in search_tags:
            print(f"  - {tag}")

        print(
            f"\nMatching records: {len(results)}"
        )

        for record in results:

            print("\nID:", record["id"])
            print("Title:", record["title"])
            print(
                "Research Area:",
                record["research_area"]
            )
            print("Tags:", ", ".join(record["tags"]))

        return results

    # --------------------------------------------------------
    # STEP 5 - SIMILARITY RETRIEVAL
    # --------------------------------------------------------

    def similarity_retrieval(self):

        print("\n" + "=" * 70)
        print("LONG-TERM MEMORY - SIMILARITY RETRIEVAL")
        print("=" * 70)

        results = retrieve_by_similarity(
            self.history,
            self.state.draft,
            k=5
        )

        print("\nCurrent Draft Used for Similarity:")

        print(self.state.draft)

        print("\nSimilar Historical Proposals:")

        for rank, item in enumerate(
            results,
            start=1
        ):

            record = item["record"]
            score = item["similarity"]

            print(
                f"\n{rank}. {record['title']}"
            )

            print(
                f"   Similarity: {score:.4f}"
            )

            print(
                f"   Research Area: "
                f"{record['research_area']}"
            )

        return results

    # --------------------------------------------------------
    # STEP 6 - DISPLAY SHORT-TERM STATE
    # --------------------------------------------------------

    def show_session_state(self):

        self.state.show_state()

    # --------------------------------------------------------
    # STEP 7 - SHOW MEMORY SEPARATION
    # --------------------------------------------------------

    def show_memory_separation(self):

        print("\n" + "=" * 70)
        print("MEMORY SEPARATION")
        print("=" * 70)

        print("\nSHORT-TERM SESSION STATE")
        print("-----------------------")

        print("Current request:")
        print(self.state.current_request)

        print("\nCurrent draft:")
        print(self.state.draft)

        print("\nLONG-TERM MEMORY")
        print("----------------")

        print(
            f"Historical records stored: "
            f"{len(self.history)}"
        )

        print(
            "\nPrevious proposals are stored separately "
            "from the current draft."
        )


# ============================================================
# MAIN LAB 4
# ============================================================

def run_lab4():

    print("\n" + "=" * 70)
    print("RESEARCH GRANT MANAGEMENT SYSTEM")
    print("LAB 4 - MEMORY & RETRIEVAL")
    print("=" * 70)

    coordinator = Coordinator()

    # --------------------------------------------------------
    # CURRENT RUN
    # --------------------------------------------------------

    coordinator.create_current_request()

    coordinator.create_current_plan()

    coordinator.create_current_draft()

    # --------------------------------------------------------
    # SHOW SHORT-TERM STATE
    # --------------------------------------------------------

    coordinator.show_session_state()

    # --------------------------------------------------------
    # TAG RETRIEVAL
    # --------------------------------------------------------

    coordinator.tag_retrieval()

    # --------------------------------------------------------
    # SIMILARITY RETRIEVAL
    # --------------------------------------------------------

    coordinator.similarity_retrieval()

    # --------------------------------------------------------
    # SHOW SEPARATION
    # --------------------------------------------------------

    coordinator.show_memory_separation()

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("LAB 4 COMPLETED")
    print("=" * 70)

    print("\nThe system demonstrated:")

    print("1. Short-term session state")

    print("2. Long-term stored history")

    print("3. Tag-based retrieval")

    print("4. Similarity-based retrieval")

    print(
        "\nCurrent draft and historical records "
        "are kept separate."
    )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    run_lab4()