# Reflective learning and relationship profiles

## Workflow contract

This is retrieval-based personalization, not model training or proof that astrology predicts events. Use Python's maintained standard-library SQLite implementation; no external journal service, paid platform or new runtime dependency is needed. No journal content is sent over the network by the helper. The host chat provider can still process the conversation and tool results.

### Select a private subject

Only use the current owner's journal in their private conversation. `profiles` lists locally stored subjects; disambiguate aliases before selecting a `profile_id`. Never reuse another owner's private profile. Existing `profile.json` remains the owner's birth profile, not automatically migrated or overwritten. With permission, create a journal `self` profile referencing only the necessary agreed details.

Allow `self`, `friend`, `colleague`, `acquaintance`, `partner`, `other`. Prefer aliases, minimal context and user-supplied non-sensitive observations; record their source. Subject consent may be unknown: owner consent is not the subject's consent. Do not scrape, covertly investigate, infer secret birth data, or infer health/diagnoses, sexuality, religion, politics, criminality, trustworthiness, or other sensitive traits. Do not use astrology to decide employment, credit, healthcare, or other consequential eligibility. Do not claim to know someone's intentions or feelings. Avoid manipulative compatibility advice.

For a tentative personality reflection, separate (1) verified birth/chart data if voluntarily provided, (2) the owner's observations and direct quotations, (3) explicitly uncertain symbolic hypotheses. Without birth details, offer behavior-based reflection, not a fabricated natal reading. Invite counterexamples. Describe relationship feedback as the owner's perspective, not confirmation by the subject. Share nothing with that person or other users without explicit authorization. Real birth data must use the existing validation/calculation workflow; profile storage alone does not verify it. Group context: do not list, inspect or reveal the journal.

**Done:** the intended subject and provenance are unambiguous, and storage scope has consent.

### Record before evaluation

For a new projection, store the original hypothesis, period, actual calculated basis (or explicitly observation-only), uncertainties, what would not fit, and review date. A period already started is marked `retrospective_or_ongoing`; never backdate or call a retrospective interpretation an advance prediction. Include technique, source, sample limitations and chart assumptions in `basis`/`uncertainty`. If real transit evidence is missing, do not fabricate it. Store no certainty probability from symbolic star ratings.

Ask permission to retain the agreed concise text, unless the owner has explicitly authorized ongoing journal storage. The helper's `consent:true` represents actual conversational consent, not a substitute for asking. Corrections create a new projection with `supersedes`; originals remain unchanged. Do not reconstruct old projections as authentic historical records without a reliable original source: identify a user-recalled reconstruction as such in `context`.

**Done:** saved record ID, creation timestamp and original wording are available independently of later feedback.

### Review without leading

On subsequent Astron use, call `due` for the selected profile. Offer at most 1–3 unresolved items, respecting a declined review and the current request. Show the original period and hypothesis, then ask what actually happened *before* suggesting a match. Ask what did not fit and what other explanations may apply. Record only explicit feedback as `matched`, `partial`, `missed`, `unclear`, or `not_applicable`; silence is never a match. User can use their own words; do not force a score. Cite the original ID and distinguish early feedback from a completed-period review. `due` uses UTC calendar dates and is checked at invocation, not a background reminder. `unclear` stays unresolved. Choose `review_after` after the local period has ended (usually the following date to avoid UTC/local ambiguity).

A correction to feedback supplies `supersedes` pointing to the current review. Original feedback remains in history; only the current version counts. If feedback changes, restate/correct the lesson too; do not silently carry an outdated lesson over. Keep useful misses and counterexamples; never rewrite a hypothesis to fit an outcome.

**Done:** the owner's actual experience, attribution and outcome are recorded without altering the projection.

### Apply lessons cautiously

Before each reading for a profile, retrieve `learning` and relevant `history`. Prioritize approved lessons about language, useful reflective actions, and which symbolic themes did or did not resonate. Preserve contradictions; one observation is anecdotal. Mention when a lesson is sparse, old or context-specific; do not generalize it to other people or claim predictive accuracy. Summarize counts including misses/unclear/not-applicable, not just successes. No automatic accuracy percentage: retrospective and self-reported samples are biased.

Propose a short lesson for owner approval (`lesson_approved:true` only after approval). E.g. 'You said direct questions helped more than assuming this transit meant conflict; ask about workload first.' Keep calculated astronomy unchanged. Improving personalization is an aim, not a guaranteed outcome. New projections should explain when they use an approved prior lesson and still invite disagreement.

**Done:** new reflection distinguishes calculation, original hypothesis, user feedback and the specific approved lesson used.

## Local helper

Run `python3 <skill-dir>/scripts/journal.py` with JSON on stdin. Python standard library only. Default database: macOS `~/Library/Application Support/astron/journal.sqlite3`, otherwise `~/.local/share/astron/journal.sqlite3`. Directory 0700, database 0600; refuses insecure existing permissions, database symlinks and paths inside this skill. It is not encrypted at rest; normal backups may retain copies. Use only an explicitly chosen private `ASTRON_DATA_DIR` to override. Do not put transcripts or secrets in journal fields or logs. Read outputs privately and avoid exposing entire profiles unnecessarily.

Operations (required fields):

- `profile_add`: `consent:true`, `alias`, `relationship`, `source`; optional `notes`, `birth`, `subject_consent`. Returns a UUID. Additive storage, not silent merge by name.
- `profiles`: list profiles in the current private owner store.
- `profile_get`: `profile_id`.
- `profile_update`: `consent:true`, `profile_id`, `source`, `changes` with one or more of `alias`, `notes`, `birth`, `subject_consent`. Previous changed values remain in revision history; linked journal records stay intact. Recalculate charts after birth corrections.
- `projection_add`: `consent:true`, `profile_id`, `period_start`, `period_end`, `review_after` (ISO dates), `hypothesis`, `basis`, `uncertainty`, `would_not_fit`; optional `context`, `supersedes`. Returns a UUID.
- `review_add`: `consent:true`, `projection_id`, `outcome`, `experience`, `source`; optional `lesson`, `lesson_approved` (default false), `supersedes` for corrections.
- `history`, `due`, `learning`: `profile_id`. History retains all versions; learning returns latest review outcomes and approved lessons scoped to that profile.
- `profile_delete`: `profile_id`, `confirm_delete:true` only after explicit owner deletion request/confirmation. Deletes linked journal records, not legacy profile.json, exports, backups or chat history. Explain scope; do not promise forensic erasure.

Example with synthetic data (never run it against a real journal just to demonstrate):

```json
{"operation":"profile_add","consent":true,"alias":"Friend A","relationship":"friend","source":"Owner observations; no birth data","notes":"Prefers short practical conversations","subject_consent":"unknown"}
```

Use returned IDs, never invent them. A future projection is only saved when there is actual content to preserve. This helper stores and retrieves records, not generates astrology calculations or standalone AI lessons. Use `profile_update` for sourced profile corrections without losing linked records. Revision history also contains private data and is deleted with the profile.

## Verification and boundaries

Run `python3 -m unittest discover -s <skill-dir>/tests -p test_journal.py -v` with a temporary private data root; tests never import or alter a real profile. Full regression additionally requires the pinned calculation dependencies. There is no scheduler and no widget integration in this feature: follow-ups happen when Astron is invoked. Schedule private reminders only on explicit request with host scheduler verification. Do not claim this helper updates the separate macOS widget automatically.
