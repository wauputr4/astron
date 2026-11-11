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

On subsequent Astron use, call `blind_due` for the selected profile before retrieving/displaying projection details. Offer at most 1–3 unresolved items, respecting a declined review and the current request. Show only the period and ask what actually happened without displaying the hypothesis, chart cues or prior star ratings. Offer to save this independent account with `checkin_add` before revealing the original. If the user already saw the projection, label exposure `unknown_or_exposed`; this is not a blinded scientific study. After the account, retrieve `history` and reveal the exact original hypothesis for comparison. Link the matching-period check-in ID to the review when available. Ask what did not fit and what other explanations may apply. Record only explicit feedback as `matched`, `partial`, `missed`, `unclear`, or `not_applicable`; silence is never a match. User can use their own words; do not force a score. Cite the original ID and distinguish early feedback from a completed-period review. `blind_due` and `due` use UTC calendar dates and are checked at invocation, not a background reminder. `unclear` stays unresolved. Choose `review_after` after the local period has ended (usually the following date to avoid UTC/local ambiguity).

A correction to feedback supplies `supersedes` pointing to the current review. Original feedback remains in history; only the current version counts. If feedback changes, restate/correct the lesson too; do not silently carry an outdated lesson over. Keep useful misses and counterexamples; never rewrite a hypothesis to fit an outcome.

**Done:** the owner's actual experience, attribution and outcome are recorded without altering the projection.

### Apply lessons cautiously

Before each new reading for a profile, retrieve `learning` and relevant `history` (but first complete any accepted independent check-in without revealing the old projection). Prioritize approved lessons about language, useful reflective actions, and which symbolic themes did or did not resonate. Preserve contradictions; one observation is anecdotal. Mention when a lesson is sparse, old or context-specific; do not generalize it to other people or claim predictive accuracy. Summarize counts including misses/unclear/not-applicable, not just successes. No automatic accuracy percentage: retrospective and self-reported samples are biased.

Propose a short lesson for owner approval. Store it with `lesson_add`, linked to the specific review, context, status and review date; set `approved:true` only after approval. The older review-level `lesson_approved` field remains compatible but is returned as `legacy_lessons` and must not automatically guide new readings until converted with the owner's confirmation. E.g. 'You said direct questions helped more than assuming this transit meant conflict; ask about workload first.' Keep calculated astronomy unchanged. Improving personalization is an aim, not a guaranteed outcome. New projections should explain when they use an approved prior lesson and still invite disagreement.

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

Run `python3 -m unittest discover -s <skill-dir>/tests -p test_journal.py -v` with a temporary private data root; tests never import or alter a real profile. Full regression additionally requires the pinned calculation dependencies. There is no scheduler: follow-ups happen when Astron is invoked. The journal provides a privacy-safe `widget_data` bridge; the separately installed macOS companion consumes it only after an explicit self-profile selection. Schedule private reminders only on explicit request with host scheduler verification. A CLI journal write alone does not reload WidgetKit; refresh through the companion app. Do not claim that compilation/registration proves desktop rendering.


## Six reflection improvements

### Independent check-in and three evaluation dimensions

Use `blind_due` (profile_id) instead of `due` before asking about experience. It returns only IDs, period boundaries and a neutral prompt; do not retrieve/display hypothesis, basis, star ratings or lesson summaries until the independent account is captured. If the user wants a fresh reading without evaluation, respect it. `checkin_add` requires `consent:true`, `profile_id`, `period_start`, `period_end`, `experience`, `source`; set `before_reveal:true` only if actually captured before revealing. Period boundaries are UTC dates and cannot end in the future. `checkins` lists them. This reduces prompting bias, not all memory/selection bias: the owner may remember the original reading.

After revealing the original, optional `review_add.ratings` has independent integer 1–5 fields `fit`, `usefulness`, `clarity`. 1 = not fitting/not helpful/too vague, 5 = strongly fitting/very helpful/clear and specific. Any field may be omitted; do not infer ratings or turn missing feedback into zero. `checkin_id`, when supplied, must belong to the same profile and exact period. Keep the categorical `outcome` as the owner's separate judgment. `learning.rating_summary` reports count and mean per dimension, never a prediction-success rate. A useful question does not validate its astrological basis.

**Done:** the independent account precedes reveal, exposure is honest, and each supplied dimension has explicit owner feedback.

### Contextual, revisitable lessons

`lesson_add`: `consent:true`, `profile_id`, `review_id`, `text`, `context`, `source`, `review_after` (ISO UTC date), optional `approved` (default false), `status` (`temporary` default, `recurring`, `needs_review`). A lesson is linked to actual feedback from the same profile; one anecdote is not a recurring personality trait. Choose the next review date with the owner, not forever. `lessons` lists all with derived `effective_status`.

At/past `review_after`, even recurring lessons become `needs_review` and stop guiding readings or appearing as active widget references. Corrected supporting feedback also marks them for review. `learning.lessons` contains only approved, non-expired temporary/recurring lessons. `lessons_needing_review` is distinct. Offer renewal, revision or retirement; never silently renew it.

`lesson_update`: `consent:true`, `lesson_id`, `source`, `changes` limited to `text`, `context`, `review_after`, `status`, `approved`; status also supports `retired`. Changed text/context loses approval unless explicitly reapproved. Previous values remain in revision history. If its evidence was superseded, retire it and create a new lesson linked to the corrected review. This makes updates auditable without deleting contradictory history.

**Done:** every applied lesson is approved, current, contextual and traceable; outdated interpretations are not permanent labels.

### Small experiments

Suggest one low-risk, optional, owner-controlled action rather than a deterministic life decision. Agree what to observe and a short period. No covert tests, manipulation, exposure of someone else's private data, or consequential medical/legal/financial experiments.

`experiment_add`: `consent:true`, `profile_id`, `action`, `observation` (what to observe), `context`, `period_start`, `period_end`, `source`; optional `projection_id` from the same profile. `experiments` lists status. `experiment_review`: `consent:true`, `experiment_id`, `performed` (`yes`, `partly`, `no`), `result`, `next_step`, `source`. Corrections preserve previous values. Not performed is not failure and is not evidence that the projection missed. Even a positive outcome is not proof of astrological causation. Offer an outcome question when the agreed period has ended; no unsolicited scheduling.

**Done:** action, observables and period are agreed; evaluation distinguishes whether it was attempted from what happened.

### Multiple relationship explanations

For a behavior such as a slow reply, start with the concrete observation and source, then offer at least two plausible non-sensitive explanations, not mind-reading or a verdict. Each must state what would support it, what would weaken it, and a respectful clarifying question. Include ordinary situational explanations and admit when evidence is insufficient. Prefer direct communication over covert experiments.

`relation_add`: `consent:true`, `profile_id`, `observation`, `source`, `context`, `alternatives` (at least two objects, each exactly `hypothesis`, `would_support`, `would_weaken`, `clarifying_question`), optional `helpful_communication`. `relations` retrieves notes for that profile only. These are the owner's reflective notes, not verified psychological facts about the subject. Supersede interpretations conversationally with a dated new sourced note; do not erase contrary evidence.

**Done:** facts, interpretation and alternatives are distinct; useful communication is recorded without sensitive inference.

### Private widget bridge

`widget_data` requires `profile_id` belonging to a self profile explicitly selected for the widget. Other relationships are rejected. The response has `question`, `action`, `lesson`, optional opaque `lesson_id` and `experiment_id`, `capture_url:astron://capture`, `privacy:generic_text_only`. It never exports the alias, birth data, original user text, experiment action, lesson content or relationship details. The widget shows a generic prompt, safe action cue and whether an approved current lesson is available. Raw personalized details are available only inside the companion app. Generic text sacrifices specificity intentionally; do not put raw private text in a desktop screenshot.

The separate macOS companion must map `astron://capture` to opening its experience form, not immediately writing. A save click needs chosen self profile and nonempty owner-provided experience; opening a URL is not consent to journal anything. If no self profile exists, explain private Astron onboarding rather than auto-creating or selecting another person. A generic widget can still display without a linked journal. Always distinguish verified bridge/build/app capture from unverified desktop WidgetKit rendering.

**Done:** desktop text contains no private profile content; capture is an intentional owner action linked to the correct journal, and missing data has an honest fallback.
