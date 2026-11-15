# Practice and example requests

## Practice 1 — cardiovascular proposal, end to end

Click New proposal → Load sample proposal. Research area: `Artificial Intelligence cardiovascular monitoring digital health`. Duration: 12 months. Funding profile: government. Workspace: practice.

The sample costs are invented: 12 × ₹25,000 for a research assistant, ₹75,000 equipment and ₹15,000 travel = **₹3,90,000**. The app must identify them as synthetic and compare them only to sandbox rules. Consent is required.

Expected: discovery and literature finish before drafting; budget and compliance complete before validation; every acceptance check passes; status stops at **awaiting review**. Faculty cannot approve. HoD may approve, request changes or reject. Approved practice exports retain the **NOT FOR SUBMISSION** watermark.

## Practice 2 — cybersecurity

Title: `DDoS detection and resilience for edge-hosted inference services`

Brief: `Prepare a feasibility proposal for detecting DDoS against edge-hosted AI services using our cybersecurity publication history. Include measurable evaluation and reproducible experiments.`

Research area: `DDoS cybersecurity machine learning network security`. Government profile, 12 months, practice. Keep or edit the synthetic budget and acknowledge consent. The archive includes actual DDoS/network-security-related metadata; inspect the returned source rows rather than assuming all nearby papers establish novelty.

## Practice 3 — industry specialist

Title: `Clinical AI prototype for cardiovascular monitoring`

Area: `cardiovascular artificial intelligence digital health`. Select **industry** and practice. Inspect the specialist's prototype/adoption/IP framing and the selected synthetic industry call.

## Practice 4 — validation blocks an excessive budget

Set the equipment cost to ₹60,00,000, exceeding the synthetic overall ceiling. The result must be **blocked**, show the failing checks and offer no validated package or approval. Correct the figure only when you have a valid cost basis. A human cannot override a failed financial or evidence check by approving anyway.

## Practice 5 — expired fixture

Enter `MOCK-CALL-002` as the specific call ID. That supplied fixture has an expired deadline. It must not be selected as open, even in practice mode. The selected-call check fails and the workflow blocks.

## Practice 6 — separate evidence from history

Search the Research archive for `Micromitra` or `ATAL`. These are historical application records, not current funding calls. The amount written as `1.5L` was normalized to ₹1,50,000. The application dated 14/08/2026 is flagged outside the stated cycle; its date was not silently changed.

## Practice 7 — privacy

Create a draft as faculty, then sign in as ece_faculty. The other department account must not see it in its pipeline or retrieve it using a guessed run URL. HoD sees only the assigned department. Research Office/Dean have institution-wide review authority.

## Practice 8 — versioning

Approve version 1. In Review & versions, edit the narrative and record a change reason. The active approval is cleared; a new LangGraph thread runs validation and pauses again. Approve version 2, then restore version 1. Download and compare the narrative. Restore changes the internal release pointer, not a manually submitted external application.

## Research assistant examples

- `Find cardiovascular and heart disease publications`
- `Find DDoS cybersecurity publications`
- `Find machine learning publications`
- `Find historical agriculture grants`
- `Find historical robotics grants`

The assistant retrieves college records and can use the configured local LLM to answer with source references. Its status indicates whether a model actually ran or retrieval fallback was used. Review the cited records. Use New proposal for planning, drafting and workflow execution.

## Real case setup

The Research Office must supply genuine documents; do not convert test fixtures into “official” evidence.

1. Add a policy evidence record and the original attachment where available.
2. Register its immutable policy version in Office settings.
3. Add the actual official call guideline and retained excerpt, including the official URL and locator.
4. Register the call, timezone-aware deadline, allowable categories, verified ceilings, required document kinds, eligibility rules and template sections. Registration records the research-office attestation and timestamp.
5. Faculty adds the PI CV, eligibility evidence and ethics evidence if applicable. Attach their evidence IDs to the intake. If an evidence item was omitted, add its ID when revising the draft.
6. Run the proposal. The owner reads the draft and records PI confirmation in **Review & versions**. Research Office or Dean assesses every call eligibility rule and attaches supporting evidence for each passing rule. A failed or unknown rule keeps the draft blocked. Changes to the reviewed content require new reviews.
7. The Research Office or Dean approves the passing package. The HoD can request changes or reject a departmental proposal. Check the funder's official format before manual submission.

Verification expires after seven days. Record a newly checked call version and start a revised real proposal when sources become stale. Do not reinterpret an old sanction date as an application deadline.


## Optional public literature search

Set `OPENALEX_API_KEY` in the environment of the server process, then restart it. In **New proposal**, enter public research keywords in the optional literature field. Only those keywords are sent to OpenAlex. Crossref looks up up to two discovered DOIs for citation metadata. The Literature tab shows each provider's status and links. Institutional retrieval remains available when the key is missing or a request fails.

The dashboard uses the merged catalog. The proposal workspace shows failed checks, the selected call's verification date and the current draft's review status. Sample and institutional runs keep their separate labels.

[OpenAlex authentication](https://help.openalex.org/api/authentication/) · [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/)
