# Dataset use and provenance

The supplied audit ZIP was read as an audit and fixture source. Its warnings are preserved in the implementation: historical awards are not current calls; synthetic sources remain unverified; missing official facts are not fabricated.

## Import results

| Source | How used |
|---|---|
| 2022–23 publication workbook | Master Copy, dynamic header discovery; 90 title rows; summary cell states 91 |
| 2023–24 publication workbook | MASTER; 106 title rows |
| 2024–25 publication workbook | Master Data; 100 title rows |
| 2025–26 publication workbook | Master Copy as it is Reserg; 233 title rows |
| External_Funded_Project_List.xlsx | 19 detailed award rows; other sheets retained as original row evidence, excluded from headline sums |
| Applied_Sanctioned_Grants_2025-26-Format.xlsx | 2 application records; no outcome inferred from application |
| Sanctioned_External Funded Projects 2013-2024 updated.doc | Word binary piece-table text extraction with table-cell boundaries; separate searchable legacy text, not a normalized financial table |
| Grant_Agent_Dataset_Audit_and_Mock_Data.zip | Original audit and mock JSON retained, provenance warning respected |

The workbook-only catalog had **529 rows**. The merged catalog has **527 publications**. Three complete publications from subsidiary CSV sheets were added. Four DOI-only workbook rows were attached to their complete publication records as source locations. One chapter with two publication IDs and DOI spellings was consolidated. The importer retained the authoritative master record for one malformed subsidiary row and flagged the conflicting title. The 2022–23 summary discrepancy (91 stated, 90 master rows) is still recorded. One copy of each relevant CSV export is kept in `data/supplement`. The duplicate archive copies, duplicate Word document, grant workbook exports and duplicate summary CSVs add no separate rows.

The structured legacy details supply **60 separately searchable legacy records**. Another 20 source rows with an exact normalized title match were linked to existing detailed awards as related provenance. Those links do not overwrite official amounts or establish that the date or amount is identical. The 19 historical awards and 2 applications continue to supply the modern register. The original legacy Word file and its extracted text are retained for traceability.

Each publication carries file, sheet, row, original IDs, DOI/link, year, title, authors, abstract, type and tags where provided. Missing values remain empty. Metadata was not independently verified against every publisher's full text. Authors are not automatically turned into authenticated faculty identities or treated as consenting users.

## Financial normalization

- Detailed award amounts are interpreted according to their INR column headers.
- Application amounts in the INR-lakhs column are multiplied by 100,000. `1.5L` is parsed as ₹1,50,000, not ₹1.50 or multiplied twice.
- The `14/8/2026` application date is retained and flagged outside the stated 2025–26 cycle.
- Recurring + non-recurring discrepancies are flagged and preserved; no “repair” rewrites source figures.
- The overview shows sanctioned totals from the 19 detailed awards only. It does not sum applied amounts, received amounts, legacy Word figures or duplicate department summaries into that total.
- Legacy Word text chunks are not one-to-one grant counts; the UI never calls the chunk count an award count.

## Reproduce

From the project folder, with dependencies installed:

```powershell
.\.venv\Scripts\python.exe scripts/import_data.py
```

This reads originals without modification and rewrites `data/catalog.json` plus the extracted legacy text. SHA-256 checksums are stored in the source inventory. Restart the server after changing the catalog, because it is loaded once at startup. Back up before reimporting an expanded dataset, and review new header layouts rather than silently assuming compatibility.

## Mock-data boundary

Original fixture files in `data/mock` are unchanged. Their `verified: false`, `production_usable: false` and `example.invalid` evidence are not promoted. Additional sandbox fixtures are generated in `app.connector.demo_calls` for software practice workflows and are explicitly marked `mock: true`. They use an artificial 2099 deadline only so the practice remains usable over time. They are excluded from the real registry and all real historical financial totals.

Missing current official calls, approved policies, salary rules, ethics decisions, faculty eligibility and signed approvals are not replaced with fake “college” facts. The real workflow requires genuine office evidence.
