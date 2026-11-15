# Pilot ownership and operations

## Intended initial deployment

A single local HoD/research-office workstation, served at 127.0.0.1 with one application worker. Do not enable multiple uvicorn workers: graph mutations currently use a process-local lock. No automatic emails, public publishing or external grant submission is configured.

The original institutional datasets are bundled for your requested local project. Treat the full ZIP, runtime databases, exports, attachments and backups as internal college material. The app does not publish originals through an unauthenticated static directory. On a shared computer, apply OS account permissions to the project and runtime directory.

## Real office rollout checklist

- Replace practice identities with named authorized staff, verified roles and department scope; change generated passwords.
- Obtain the institution's permission to use the retained personal/research records. Record profile consent in each intake.
- Populate only genuine source-backed calls, policy versions and evidence. Require actual PI review and agency-template completion.
- Configure HTTPS, trusted identity/SSO, proxy limits, backups, retention and monitoring before exposing to a network.
- Review authentication hardening: this pilot has in-memory login throttling, hashed passwords and expiring sessions, but no MFA/SSO or account disabling UI; local-operator and office-admin password recovery are provided.
- Review confidentiality and the difference between immutable source snapshots and editable drafts with office staff.
- Test Windows launch and dependencies on the actual target PC; Windows scripts were authored here, but native Windows execution was not available in the build environment.
- Evaluate proposal quality and manual editing time on one real call. Software tests cannot establish that a proposal meets a funder's substantive standards.

## Backup and restore

Stop the server for a consistent application/checkpoint snapshot, then run:

```powershell
.\.venv\Scripts\python.exe scripts/backup.py
```

The script uses SQLite's backup API and includes evidence attachments. It excludes the plaintext first-login file. Store the resulting backup securely. To restore, stop the app, preserve a copy of current runtime, extract the chosen backup into the project so its `runtime` folder is restored, and restart. Check authentication, active versions, audit-chain verification and one pending-review checkpoint before allowing new work.

Never delete runtime as a routine troubleshooting step. It contains the complete workflow history.

## Logs and metrics

Each run's Agent audit shows connector queries, evidence IDs, numerical tool input/output, node results, timings, plan locking, reviewer decisions and release events. `/api/dashboard` reports scope-filtered proposal statuses and institutional archive totals. `/api/system` verifies the audit hash chain.

Track validation-pass rate, blocked causes, proposal turnaround, human edit time, reviewed proposal quality and deadline compliance during the pilot. The software records elapsed graph time, but does not claim performance/service-level KPIs have been validated for a production workload.

## Institutional evidence changes

Calls and policies are immutable version IDs. Create a new version when a rule, deadline or verification changes; start a revised proposal using the new call ID. Seven-day freshness is an application pilot control, not a claimed funder policy. If a call is withdrawn before its deadline, staff must stop using it and review affected proposals; the system has no live cancellation feed.

## Explicit exclusions

No proprietary AURA SDK, no general-purpose web crawling, no guaranteed exact-format generation for every agency, no independent legal/ethics certification, no automatic scientific novelty determination and no external-submission API. These are intentional boundaries documented for the office, not silently simulated capabilities.
