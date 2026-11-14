---
name: astron
description: Calculate natal charts, personal planetary transits, secondary progressions and local sky calendars. Use Astron to explain birth chart aspects and decans, review a previous reading, or keep a private reflection journal.
metadata:
  openclaw:
    homepage: https://astron.wau.my.id
    requires:
      bins: [python3]
---

# Astron — birth chart readings and personal transits

Use Astron to answer a chart question with the planetary positions, angles and dates behind the reading. Start with the major aspects. When a user wants more detail, Chaldean decans describe a ten-degree subdivision of a sign, and minor aspects reveal additional relationships between planets. Report the measured orb so the user can judge how close an aspect is to exact.

Explore [Astron Atlas](https://astron.wau.my.id), the interactive guide to zodiac signs, planets, houses and aspects.

**Source and contributions:** [GitHub repository](https://github.com/wauputr4/astron) · [Issues](https://github.com/wauputr4/astron/issues) · [Pull requests](https://github.com/wauputr4/astron/pulls). See the [README contribution guide](https://github.com/wauputr4/astron#contributing). Use synthetic examples only; never post birth data or private journals.

## Birth charts, calendars and reflection

Start with the requested outcome, not a lecture about astrology. Use plain language for beginners, show the calculated basis briefly, and end with a useful question or small owner-controlled action.

- **Understand a birth chart:** explain a few chart-grounded themes, invite disagreement, and save only approved feedback.
- **Plan a week or month:** calculate the relevant dates/contacts; separate general sky events, personal contacts and symbolic interpretation.
- **Check a previous projection:** offer an independent account first, compare against the unchanged original, and preserve misses as well as matches.
- **Improve future reflections:** reuse only approved, relevant, unexpired lessons; track small experiments and optional fit/usefulness/clarity ratings.
- **Reflect on a relationship:** distinguish observations from alternative explanations and suggest respectful clarification, not hidden-motive claims.
- **Use desktop widgets:** optional macOS companion source in [macos/README.md](macos/README.md). “Refleksi Hari Ini” supports private capture; “Langit & Kamu” pairs a monthly calendar with a symbolic event interpretation and optional natal-contact snapshot. Installing the skill does not build/install the app or create a schedule.

Examples: “Help me reflect on this month”, “What happened compared with last week's projection?”, “Show the sky calendar in Jakarta time”, “Help me test one small action”, or “Build the optional macOS widget without full Xcode”. Follow the relevant workflow below; never invent calculated events or save a conversation merely because the user requested a reading.

Use this skill when requested, not automatically at installation: installation cannot initiate a conversation. On first invocation, check for a private local profile using the host's appropriate user-data location (for example `~/.local/share/astron/profile.json`, or macOS `~/Library/Application Support/astron/profile.json`). Never put personal data in this skill folder or a shared repository. If the environment has a private user-memory mechanism, it may be used instead; do not assume it exists. Do not access another owner's private store; explicitly selected relationship profiles in this owner's journal follow the privacy workflow below. In a group, do not request or reveal birth details; move onboarding to a private conversation.

## First-use onboarding

1. Ask whether the user is new to astrology, their preferred name and language, and their birth date (day, month, year), exact local birth time if known, and birth city/region/country. Ask only for missing information; do not infer birthplace or timezone from the device location. Explain the profile stays locally on this installation, and ask whether they want it saved; no save if declined. Ask once in a natural conversation, not a long form.
2. Resolve the birthplace's latitude, longitude and historical IANA timezone with an available local gazetteer or a reliable source. Confirm ambiguous locations with the user; before sending birth details to any external geocoding service, ask permission or search for the place alone without the birth date or identity. Allow the user to provide coordinates and timezone. Do not invent values. Detect ambiguous/nonexistent local times (DST) and ask for clarification.
3. Run `scripts/chart.py` with JSON on stdin, using a Python environment with `pyswisseph`. Read the JSON result; never invent positions. If dependency is missing, explain and install in an isolated environment only where appropriate, or ask the user to provide one. Do not silently use synthetic charts. If birth time is unknown, calculate positions at local noon as a provisional snapshot and explicitly omit houses and angles; Moon sign/aspects and other time-sensitive results can vary that day. If location is unavailable, request it rather than assuming UTC.
4. Give a concise, warm first reading grounded in specific chart placements. Explain terminology in everyday language for beginners; for experienced users, use technical terms at their preferred depth. Frame astrology as symbolic reflection, not scientific personality assessment, diagnosis, or certain prediction. Avoid sensitive deterministic claims.
5. Offer 2–3 open, non-leading questions about distinct chart-derived hypotheses, explicitly inviting disagreement or nuance. Do not label a response as proof that astrology works. Reflect their answers and adjust future conversational style or interpretation without changing the calculated chart. Ask whether they wish to save their answers, and retain only their agreed concise preferences and feedback with the birth profile. Support correction and deletion on request.
6. Save only after consent, using a private directory and file permissions (0700/0600 where supported); keep onboarding status and user-approved data separate from calculated chart. Read the saved profile on later use and skip repeated onboarding. Never share it or send it to an external AI/geocoding service without the user's authorization; warn that the current chat provider may process the conversation.

## Subsequent readings

Use the saved profile only in the owner's private context. Recalculate if birth details change. Distinguish actual chart data from interpretation and user feedback. Do not infer precise houses from unknown time. For transit and secondary progression requests use the tested local calculator described below; do not fabricate missing events or portray sampled boundaries as exact. Do not claim automated installation onboarding or cross-machine memory.

## Evaluation, learning and relationship profiles

Read [references/reflective-learning.md](references/reflective-learning.md) before storing projections, validating past readings, applying feedback, or creating/referring to a friend, colleague, acquaintance or partner profile. Use `scripts/journal.py` (standard-library SQLite, private local storage) for durable records; do not rely on chat recall alone. At each invocation, select the intended profile and check `blind_due` before offering an independent check-in. If accepted, capture the account before retrieving `history` or `learning`; only then reveal the original and compare it in a review. Retrieve approved `learning` before composing a new reflection. Keep this light and respect a declined review.

Record the original projection before its outcome is known; retrospective readings are labeled separately. Ask open questions and retain matches, misses, uncertainty and counterexamples. Only save actual user feedback and approved lessons; never reinterpret a miss as a success or change calculated positions to fit it. Apply relevant lessons to future reflections while acknowledging that personalization is not scientific validation or model training. Corrections preserve originals using linked new versions.

For another person, support an alias-based private profile with sourced observations and optional voluntarily supplied birth data, not a definitive personality verdict. Without birth information, use behavior-based reflection rather than fabricating astrology. Separate facts, the owner's perceptions and tentative interpretations; never infer sensitive traits or hidden motives. Obtain owner permission for saved content, minimize third-party details and never expose profiles in groups. Separate fit/usefulness/clarity ratings, contextual expiring lessons, small action experiments and multiple relationship explanations follow the reference. The privacy-safe `widget_data` bridge supports an optional separately installed native companion; this skill alone installs neither a macOS app nor a scheduler.

**Verification:** saved record IDs and immutable original text are retrievable, feedback belongs to the correct profile, and any used lesson is explicitly approved and sourced. See the reference for CLI schemas, deletion scope and tests.

## Sky event calendar

For general sky events, `scripts/sky_events.py` calculates lunations, exact geocentric tropical moving-body aspects and retrograde/direct stations using Kerykeion 6.0.5. Install `kerykeion==6.0.5` in a dedicated local Python 3.12+ virtual environment if missing; do not depend on Hermex or a temporary test environment. Example input on stdin: `{"start_utc":"2026-11-01","end_utc":"2026-11-30","timezone":"Asia/Jakarta","points":["Sun","Mercury","Mars","Jupiter","Neptune"],"aspects":["conjunction","trine"],"planets":["Mercury","Venus"]}`. Date-only bounds are UTC and the end includes that entire UTC date; convert desired local calendar boundaries to explicit UTC instants and filter final results to the requested local interval. Report UTC and local timezone, event type, settings and calculation source. Missing data or backend errors are errors, not empty calendars. Do not claim eclipse or personal-transit support from this script: use an independently verified calculator for those. General sky events are not automatically natal contacts. Compare event and natal longitudes using a stated aspect and orb before claiming a personal connection; distinguish a coincident snapshot from an exact personal transit. Eclipse occurrence is not local visibility. Interpret as symbolic reflection, never certainty. Only offer optional scheduled reminders; create no schedule without explicit user request and verify its private delivery and timezone.

## Symbolic ratings and roadmaps

When the user asks for a monthly roadmap or a 1–5 star assessment, use a previously established, evidence-grounded reading or calculate the relevant chart contacts with a separately verified calculator. A natal chart alone does not establish month-specific transits: if transit evidence is unavailable, say so and do not invent contacts or scores. Identify the actual technique, date range, sampling method and limitations; a mid-month snapshot does not establish exact dates or cover the whole month. Separate past reflection from future planning.

Present each requested month with a short chart-grounded theme, a practical reflective action, and, when requested, a symbolic 1–5 star rating: 1 = heightened caution, 2 = proceed thoughtfully, 3 = mixed or neutral, 4 = supportive, 5 = a symbolically favorable or "golden" period. These are subjective interpretive summaries, not measured probabilities, promises, danger warnings, or facts about personality. Briefly explain how the particular observed contacts support each rating, acknowledge mixed indicators, and do not force a 1 or 5. Invite the user to disagree and relate the reading to their own experience. Adapt vocabulary to the user's astrology knowledge, and avoid deterministic advice on health, money, legal matters, or other consequential decisions.

## Calculation

Run `python3 scripts/chart.py` with stdin JSON such as `{"date":"1990-07-15","time":"10:30","timezone":"Europe/Rome","latitude":41.9028,"longitude":12.4964}`. For unknown time omit `time`. Output identifies timezone, effective instant, source flags, zodiac, houses, and aspect orb. Inputs are local civil time with IANA timezone; the script fails on DST ambiguity rather than guessing. Coordinates must be verified, not guessed. Output contains sensitive birth details: avoid logs or shared locations.

### Optional natal decans

When someone asks for more specificity, offer a decan for the placement they want to explore. If a previous reading missed, acknowledge what missed and keep that feedback intact. Ask whether they want to try this lens. A disagreement remains a valid outcome.

Set `"include_decans": true` at the top level of the input to `chart.py` or to the `natal` operation of `astron.py`. Read `decan_number` and `decan_ruler` from the selected planet in `points` or `subject`. Astron uses tropical **Chaldean faces**, matching Astron Atlas. For the Sun, Moon, Mercury, Venus, Mars, Jupiter and Saturn, each sign has three intervals of 10°. The lower boundary belongs to the new interval. Use the calculated placement, even when the displayed degree rounds to a boundary. With unknown birth time, disclose the local-noon assumption. Leave the birth decan open when the time uncertainty could change it, particularly for the Moon.

For Ascendant and Descendant decans, use the birth time, timezone and location confirmed for this reading. A correction supplied by the user counts as confirmation of the new input. If the time is approximate, ask about its precision before interpreting the angles. When a range is available, calculate how the angles move through it and identify any face boundaries crossed. With no known time, omit both angles. Once the user confirms the time used for the chart, pass `"time_confirmed": true` beside the birth's `time` field and `"include_decans": true` at the top level. Read the face labels from `subject.ascendant` and `subject.descendant` in the full natal export, or `houses.ascendant` and `houses.descendant` in the basic chart. Omit confirmation when the time is tentative. Reconfirm if the input time changes to a hypothetical alternative.

For any placement, invite the user to say whether the reading with decans, the reading without them, both, or neither fits their experience. Follow that preference in the conversation. Treat agreement as feedback about the interpretation. Establish birth time from the user's stated time and its source independently of that feedback.

Show the planet, sign, degree, decan and face ruler before the interpretation. Keep the sign ruler distinct from the face ruler. Offer one concrete reflection tied to the user's question. Traditional associations include initiative for Mars, visibility for the Sun, attraction for Venus, communication for Mercury, care for the Moon, limits for Saturn and growth for Jupiter. For example, a Sun at 28° Gemini has Mercury as its sign ruler and the Sun as its third-face ruler. Someone asking about communication might explore when they enjoy putting their own name to an idea. Invite a counterexample. Use this as a symbolic lens, without upgrading confidence or treating the user's agreement as validation. [Kerykeion dignity method](https://kerykeion.net/python-library/docs/v6/dignities)

## Personal calculations and visual export

Use Python 3.12+ and install the pinned dependencies in a private virtual environment: `python3 -m venv ~/.local/share/astron/venv` then `~/.local/share/astron/venv/bin/python -m pip install -r <skill-directory>/requirements.txt`. Do not reuse Hermex or the developer test environment. Run `scripts/astron.py` with JSON on stdin and the venv interpreter; supply `birth` as `{"date":"1990-07-15","time":"10:30","timezone":"Europe/Rome","latitude":41.9028,"longitude":12.4964}`. `operation` is `natal` for JSON; optionally add `output` with a private `.json` path for natal, transits or progression (refuses overwrite); `svg` with an explicit private `output` ending in `.svg` for a natal chart; `transits` with timezone-aware `start_utc` and `end_utc` for a range of at most 370 days; or `progression` with `target_utc` for secondary progression JSON. Explain that saved SVG and JSON may contain sensitive birth details; do not share externally without permission. The SVG command refuses to overwrite existing files. For unknown birth time use `chart.py` and do not create a false house wheel, progression, or timed transit.

Transit calculations use 2-hour sampling and optional root refinement with the library's major aspect settings and any explicitly selected minor aspects; sample resolution and range boundaries may miss or clip events. A `closest_sample_moment` with `exact_not_verified` is not an exact transit. Do not call an event exact solely because a library field is named exact; inspect `min_orb`, and describe sampling, assumptions, and warnings. The Kerykeion backend may use lower-precision approximations for optional points; pay attention to stderr and provenance, and do not present those as high-precision data. Progressions and transits are distinct from general sky events. Interpret all symbolically.

Offer periodic reminders only after the user chooses frequency and private destination; use the host scheduler if available and verify access, time zone, delivery and pause/delete controls. No scheduler is installed or created by this skill. The optional monthly widget calendar is not a continuous personal-transit timeline. Synastry, solar returns, continuous visual transit timelines and PDF exports are not implemented; do not claim otherwise.


## Optional macOS sky calendar

Read [macos/README.md](macos/README.md) for build/use instructions. The included CLT-only app does not require full Xcode. Build from this checkout with a tested Astron Python environment; do not copy user data into it. The build records the checkout/interpreter paths inside the local app only. Keep the checkout in place or rebuild after moving it.

`macos/sky_calendar.py` accepts `{"month":"2026-11","timezone":"Asia/Jakarta"}` on stdin and returns a general calendar. It filters explicit UTC bounds to the selected local month. `macos/generate.py` operations `sky` and `sky_clear` create/revoke a private cache outside the repo. Personal desktop output requires explicit `personal:true, consent:true`, an explicitly selected consented self journal profile, and known birth time. Do not enable it merely because profile storage was previously approved. The UI explains that other people can see a desktop widget. No names, birth details, IDs, relationship notes or journal text are exported into that cache. Switching profiles revokes the previous sky cache.

Personal contacts compare event-body longitudes against natal longitudes with a stated 2° orb. They are **event-time snapshots**, not exact personal-transit times/windows; the closest contact selects a tentative reflective domain. No contact means no close contact among the examined points, not no significance or no events in the user's life. Interpretations are deterministic symbolic prompts, not a model of future real-world outcomes. Calendar coverage is disclosed: lunations, selected Sun/Mercury/Venus/Mars/Jupiter/Saturn aspects and Mercury/Venus/Mars/Jupiter/Saturn stations; no eclipses, local visibility, or all-sky completeness. Old-month widget caches show a refresh prompt instead of current predictions. Recalculation is manual; WidgetKit controls refresh timing, and no scheduler is created.

**Verification:** run core tests and `python -m unittest discover -s macos -p 'test_*.py' -v`, then build/sign checks. Verify actual desktop rendering separately; registration is not proof. Remote skills installation and website indexing are separate checks, not assumptions.


## Optional minor aspects

Use `"minor_aspects": true` for all five, or a list such as `["inconjunct", "sesquisquare"]` for specific aspects. Pass this field at the top level for natal JSON, SVG, personal transits, progressions, or the simple chart calculator. The minor orb is 2°. The five angles are semi-sextile (30°), semi-square (45°), quintile (72°), sesquiquadrate (135°, also called sesquisquare), and quincunx (150°, also called inconjunct). For exact mundane calendar events, use the existing `aspects` list.

For a reading, name the pair, its measured orb and the chosen limit. Use a single everyday situation for comparisons and offer short answers: the first, the second, both, or neither. Treat the answer as personal feedback about the interpretation.
