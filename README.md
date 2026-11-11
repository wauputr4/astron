# Astron

A personal astrology agent skill for private, reflective conversations. Computes natal data, general sky events, transit windows, secondary progressions and natal SVG charts. Includes a private local projection journal and relationship profiles. Astrology is symbolic reflection, not a scientific personality test or a guarantee of future events.

## Install the skill

- **skills.sh / GitHub:** [`astron` on skills.sh](https://skills.sh/wauputr4/astron/astron)
  ```sh
  npx skills add wauputr4/astron --skill astron
  ```
- **ClawHub:** [Astron by @wauputr4](https://clawhub.ai/wauputr4/skills/astron), version 1.0.0. The listing is public, but its registry license label conflicts with this repository's license; see the license note below before relying on that distribution.

## Setup

Requires Python 3.12+ and local ephemeris support. Install in an isolated environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

Install this directory as an AgentSkill and invoke `astron`; follow [SKILL.md](SKILL.md) for the JSON inputs and onboarding. No account, hosted AI service, or Hermex installation is required for local calculations. The chat provider may process conversations. Personal profiles and generated exports should stay outside the repository.

## Reflective evaluation and people profiles

Astron can preserve a dated projection, revisit it with your feedback (matched, partial, missed, unclear, not applicable), and reuse your approved lessons in later conversations. Originals remain intact; retrospective reflection is not presented as an advance prediction. This is memory-based personalization, not model retraining or scientific evidence of predictive accuracy.

Store aliases for yourself, friends, colleagues, new acquaintances or partners, with sourced observations and optional voluntarily supplied birth data. Interpretations remain tentative and separate from facts. Without birth data, use behavior-based reflection, not a fabricated chart. No sensitive-trait or hidden-motive inference.

The standard-library helper `scripts/journal.py` uses a local SQLite journal outside this repository (directory 0700, file 0600); no new dependencies. Data is not encrypted by the helper. Storage requires permission; corrections keep history, and explicit profile deletion cascades to linked journal records. The chat provider and normal backups may still retain information. Existing birth profile files are not automatically migrated. Reviews are offered when Astron is invoked: no background reminder is created. An optional `widget_data` bridge supports a separately installed macOS companion; the skill does not install a native app. See [the workflow and CLI reference](references/reflective-learning.md).

```sh
python3 -m unittest discover -s tests -p test_journal.py -v
```

### Evaluation tools

- Independent check-in before revealing a projection (`blind_due`, `checkin_add`).
- Separate optional 1–5 fit, usefulness and clarity ratings, with denominators and no automatic accuracy claim.
- Approved lessons with context, temporary/recurring/review/retired lifecycle and review dates. Expired or corrected evidence stops automatic reuse; old records are preserved.
- Small owner-controlled experiments: action, observables, period, whether attempted and the actual result.
- Relationship notes with alternative explanations, supporting/counter-evidence and respectful clarifying questions.
- Privacy-safe `widget_data` (explicit self profile only): generic question/action/lesson reference, with no names or raw private text. Capture URL opens the separately installed app; opening never automatically writes.

The new SQLite tables are additive. Existing review-level lessons remain as `legacy_lessons`; owner-approved migration into contextual lessons is required before reuse. No real personal records are created by tests.

## Scope and limitations

Charts use tropical geocentric positions and Placidus houses. If time is unknown, the basic chart uses a disclosed noon snapshot without houses; advanced features require a known time. Transit windows use sampling and may be clipped; not every closest point is exact. Ephemeris coverage and per-body precision vary; inspect errors and provenance. Calendar calculations currently include lunations, planetary aspects and stations, not eclipse or personal-transit integration. SVGs contain birth data. Automations, PDF exports and synastry are not implemented.

## License

AGPL-3.0-only. Kerykeion and pyswisseph have their own license terms; consult their upstream licenses before distribution or public deployment.

**ClawHub license discrepancy:** ClawHub labels published skills MIT-0 by platform policy, while this repository and its bundled LICENSE state AGPL-3.0-only. The licensing implications of the ClawHub copy have not been resolved. Use the GitHub source and review applicable terms rather than assuming the registry label changes this repository's license.
