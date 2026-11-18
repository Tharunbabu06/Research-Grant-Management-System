# Data, provenance and distinct counts

## Source inventory

[Catalog](../../langgraph_edition/data/catalog.json) has 527 established scholarly records, 19 detailed historical awards, two applications and retained legacy sources. [Historical register](../../backend/src/projects.js) has 30 rows. Sources overlap; counts/amounts cannot simply be added.

[Original inputs](../../langgraph_edition/data/originals/) and [CSV supplements](../../langgraph_edition/data/supplement/) contain annual college publication workbooks 2022–26, External_Funded_Project_List.xlsx, Applied_Sanctioned_Grants_2025-26-Format.xlsx and the legacy sanctioned-project document/CSV. Filenames, sheets and rows remain inspectable. These materials were already supplied with the repository; no new open-data license or broader redistribution permission is implied.

[Importer](../../langgraph_edition/scripts/import_data.py), [supplement merger](../../langgraph_edition/scripts/merge_supplement.py) and [audit](../../tools/audit_data.py) normalize whitespace, authors, DOI identities and financial fields. The catalog-bound [sidecar](../../langgraph_edition/data/reconciliation.json) retains provenance/conflict candidates without silently promoting them. Its SHA-256 must match the catalog. Originals remain unchanged. Null amounts mean unknown; sanctioned, received and requested amounts differ. Legacy summaries, applications and mocks are excluded from detailed sanctioned-award financial totals.

## Identity and overlapping awards

[Directory](../../backend/src/researcher-directory.js) derives researchers separately from accounts; [explicit aliases](../../backend/src/faculty.js) support known variants. Authors, home_authors, PI/co-PI evidence and original rows are considered. A first-name match is insufficient; homonyms stay ambiguous.

Saroja Siddamal / Dr. Saroja V Siddamal resolve together on supported evidence. Saroja S Bhusare remains separate, without invented papers. Two source-specific reviewed overlaps connect e-Krushi and MATOMAC register/catalog rows after title, investigator and source-year checks. Both records remain; e-Krushi's INR 600 discrepancy is visible. Other fuzzy candidates remain unresolved. Scholarly attribution does not establish verified campus authentication.

## Counter definitions

| Counter | Basis |
| --- | --- |
| Research publications | Resolved scholarly record IDs, never proposal status |
| Proposals created | Unique visible proposal IDs linked by owner/explicit stable faculty IDs |
| Awaiting review | Visible records currently awaiting_review |
| Internally approved proposals | Current approval and matching artifact/context hashes; exact historical Restore keeps historical provenance |
| Funded awards | Supported sanctioned source groups, excluding applications/internal approvals |
| Versions | Saved entries; several versions remain one proposal |

[Activity](../../backend/src/proposal-activity.js) filters by viewer permissions before returning details/counts. Edits invalidate current approval but retain history. [Tests](../../backend/tests/correctness.test.js) derive 1 approved proposal / 0 papers / 0 awards and unique counts across versions.

## Search and practice fixtures

[Archive search](../../backend/src/research-sources.js) is offline, searches supported normalized fields and returns total/page/displayed/totalPages. Default page size 20; maximum 100. OpenAlex topic search and Crossref enrichment have separate labels/outcomes; college fallback is never OpenAlex success.

[Seed corpus](../../backend/src/seed.js), [Python mocks](../../langgraph_edition/data/mock/) and lab seeds contain practice calls, policies, costs, quotations and literature. These are not official agency rules. Authentic metadata does not prove scientific entailment or novelty. Private workflow/account databases are excluded from Git.
