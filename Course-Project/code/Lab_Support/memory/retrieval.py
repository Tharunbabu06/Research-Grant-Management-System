# ============================================================
# LAB 4 - RETRIEVAL
# Long-term memory retrieval
#
# Supports:
#   1. Tag-based retrieval
#   2. Similarity-based retrieval
# ============================================================

import json
import math
import re
from collections import Counter
from pathlib import Path


# ============================================================
# FILE PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

HISTORY_FILE = BASE_DIR / "data" / "proposal_history.json"


# ============================================================
# LOAD LONG-TERM HISTORY
# ============================================================

def load_history():
    """
    Load previous proposals from long-term storage.
    """

    with open(
        HISTORY_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# TAG-BASED RETRIEVAL
# ============================================================

def retrieve_by_tags(records, tags):
    """
    Retrieve records whose tags match the requested tags.

    Args:
        records: Long-term memory records
        tags: List of tags to search for

    Returns:
        Matching records
    """

    requested_tags = {
        tag.lower()
        for tag in tags
    }

    results = []

    for record in records:

        record_tags = {
            tag.lower()
            for tag in record.get("tags", [])
        }

        if requested_tags.intersection(record_tags):

            results.append(record)

    return results


# ============================================================
# CREATE LOCAL EMBEDDING
# ============================================================

def create_embedding(text):
    """
    Create a simple deterministic text embedding.

    This is an offline demonstration embedding.
    It uses normalized word-frequency vectors.
    """

    words = re.findall(
        r"\b[a-zA-Z0-9]+\b",
        text.lower()
    )

    return Counter(words)


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(vector_a, vector_b):
    """
    Calculate cosine similarity between two
    frequency-based vectors.
    """

    all_words = set(vector_a) | set(vector_b)

    dot_product = sum(
        vector_a[word] * vector_b[word]
        for word in all_words
    )

    magnitude_a = math.sqrt(
        sum(
            value ** 2
            for value in vector_a.values()
        )
    )

    magnitude_b = math.sqrt(
        sum(
            value ** 2
            for value in vector_b.values()
        )
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )


# ============================================================
# SIMILARITY-BASED RETRIEVAL
# ============================================================

def retrieve_by_similarity(records, query, k=5):
    """
    Retrieve the k most similar historical records.

    Args:
        records: Long-term history
        query: Current proposal/draft text
        k: Number of results

    Returns:
        Ranked list of similar records
    """

    query_vector = create_embedding(query)

    scored_records = []

    for record in records:

        searchable_text = " ".join(
            [
                record.get("title", ""),
                record.get("research_area", ""),
                record.get("summary", "")
            ]
        )

        record_vector = create_embedding(
            searchable_text
        )

        score = cosine_similarity(
            query_vector,
            record_vector
        )

        scored_records.append(
            {
                "record": record,
                "similarity": score
            }
        )

    scored_records.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    return scored_records[:k]