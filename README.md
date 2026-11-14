# Astron — natal charts, personal transits and astrology journaling

Astron is an astrology skill for AI agents. It calculates your birth chart locally, explains the planetary placements behind a reading, and lets you revisit an interpretation after you have written down what happened.

Explore a fictional birth chart, select a planet, or measure the angle between two bodies in [Astron Atlas](https://astron.wau.my.id). You can try the atlas before installing the skill.

## What can I do with Astron?

| Feature | Why use it? |
| --- | --- |
| Natal chart | Find a planet’s sign, degree and house. Read the five major aspects first, then explore Chaldean decans or five optional minor aspects when a placement deserves a closer look. The measured orb tells you how close a pair is to the exact angle. |
| Personal transits and secondary progressions | Explore a period in relation to your birth chart. Transit windows show when a planet approaches and leaves a contact. Progressions offer a separate symbolic timeline for a chosen date. |
| Local sky calendar | Find new and full moons, planetary aspects and retrograde or direct stations in your timezone. Compare a sky event with a natal placement to see whether it makes a personal contact. |
| Private reflection journal | Write down your experience before reopening an earlier reading. Review matches, misses and uncertainties, keep lessons you approve, or use aliases to reflect on relationships. |
| Chart exports and macOS widgets | Save a natal wheel as SVG or calculation results as JSON for later inspection. The optional desktop companion puts the sky calendar and a reflection prompt within reach. |

Astron uses tropical, geocentric positions and Placidus houses. When birth time is unknown, it gives a provisional noon snapshot and omits houses and angles. A confirmed birth time unlocks decans for the Ascendant and Descendant. Each reading distinguishes calculated positions from symbolic interpretation.

## Install

For a compatible AI agent, run this command in your project and follow the setup prompts.

```sh
npx skills add wauputr4/astron --skill astron
```

[Find Astron on skills.sh](https://skills.sh/wauputr4/astron/astron) · [Local Python setup](#local-calculation-setup)

For OpenClaw, install the [Astron instructions from ClawHub](https://clawhub.ai/wauputr4/skills/astron). The MIT-0 package guides the agent. Install the AGPL Astron engine separately to perform calculations. [Distribution details](distribution/clawhub/README.md)

## Start a conversation

- “Explain my Sun and Moon using one everyday situation. Show the chart positions you used.”
- “Show any quintiles or quincunxes in my chart. How far is each one from exact?”
- “Compare next month’s sky calendar with my personal transit windows.”
- “Let me describe my week before we reopen my earlier reading.”

You can use Astron for one conversation or choose which records to keep locally. See the [calculation methods and input fields](SKILL.md) for reproducible exports.

## Local calculation setup

Requirements: **Python 3.12+**, the pinned packages in [`requirements.txt`](requirements.txt), and an agent that can run local scripts. Keep a dedicated environment outside the repository:

```sh
# Run from the installed Astron directory (the folder containing SKILL.md).

python3 --version
python3 -m venv "$HOME/.local/share/astron/venv"
"$HOME/.local/share/astron/venv/bin/python" -m pip install -r requirements.txt
"$HOME/.local/share/astron/venv/bin/python" -m unittest discover -s tests -v
```

Ensure `python3` is version 3.12 or later, or substitute your Python 3.12+ executable. Tell your agent to use this environment for Astron. No Astron account, hosted calculation service, or Hermex installation is required. Package installation and your chat provider still involve their respective services.

The script entry points are `scripts/chart.py` (basic chart and unknown-time support), `scripts/astron.py` (natal JSON, transits, progressions, SVG), `scripts/sky_events.py` (general sky calendar), and `scripts/journal.py` (optional local journal). They accept JSON on stdin. Agent workflows and input schemas are in [SKILL.md](SKILL.md); journal operations are in [the reflective-learning reference](references/reflective-learning.md).

## Optional minor aspects

Astron can check the semi-sextile (30°), semi-square (45°), quintile (72°), sesquiquadrate or sesquisquare (135°), and quincunx or inconjunct (150°). These five use a 2° orb. For example, two bodies at 150.47° form a quincunx with a measured orb of 0.47°. The [minor aspect options](SKILL.md#optional-minor-aspects) cover natal exports, transit windows and progressions.

## Optional macOS companion

Astron’s core features work without a desktop app. The optional [macOS companion](macos/README.md) includes two WidgetKit configurations:

- **Daily Reflection** (*Refleksi Hari Ini* in the app): a compact reflective question and capture shortcut. Expanded app controls connect an existing self journal, save only with consent, and review approved lessons privately.
- **The Sky and You** (*Langit & Kamu* in the app): a monthly event calendar; medium/large widgets put the next event and symbolic interpretation beside it. Click a date for details, choose a month/timezone, and optionally enable natal-contact snapshots with a stated 2° orb.

The source builds with Swift and Apple Command Line Tools, without full Xcode. From `macos/`, run `rtk proxy /usr/bin/python3 build.py --install` after completing Python setup. The local installer backs up the existing app, ad-hoc signs/verifies the bundles and registers the extension. It records the checkout/interpreter paths; keep the checkout in place or rebuild after moving it. `rtk` is required by this build wrapper. No notarized binary release is supplied.

The companion is separate from `npx skills add`. Personal desktop output is off by default and requires a selected consented self profile, known birth time and separate display opt-in. Names, birth details and raw journal text do not enter widget caches. Opening capture never automatically saves. Calendars refresh manually; no scheduler is installed.


## Privacy and control

- **Saving is optional and requires permission.** Keep profiles, the journal, and exports outside the skill directory and any shared repository. Saved profiles do not automatically migrate between machines.
- **Local does not mean encrypted.** The SQLite helper uses a private directory/file (0700/0600 where supported), but does not encrypt the data. Normal backups may retain copies.
- **Chat is a separate privacy boundary.** Your agent/chat provider may process the conversation. Do not assume local calculations make chat contents local. Do not send birth details to external geocoding or AI services without authorization; resolving a place alone need not disclose identity or birth date.
- **Exports can identify people.** Chart SVGs and JSON may contain birth details. Choose private paths and approve any sharing explicitly.
- **Review and correct your records.** Originals remain available through linked corrections. Explicit profile deletion cascades to linked journal records; it cannot delete provider-side conversations or backups.
- **Minimize information about others.** Use aliases, obtain permission for saved notes, and avoid sensitive-trait or hidden-motive inference. Keep onboarding and private profiles out of group chats.
- **No background activity is installed.** Reviews are offered when you invoke Astron. Reminders require your explicit choice of schedule, timezone, and private destination, plus a separately available host scheduler.

The journal uses Python’s standard-library SQLite support. Existing birth-profile files are not automatically imported. Older review-level lessons remain `legacy_lessons` until you approve migration into contextual lessons. Tests use synthetic records, not your personal data.

## Calculation limits

- Charts use tropical geocentric positions and Placidus houses. Unknown birth time means no houses or angles; even the Moon and aspects may change during that day. Timed transit and progression operations require a known birth time.
- Personal transit windows use two-hour sampling with optional refinement. Sampling and range edges may miss or clip events. A closest sample is not necessarily an exact contact.
- General sky-calendar calculations cover lunations, planetary aspects, and stations—not eclipse prediction or local eclipse visibility. Optional natal comparisons must disclose their own method and precision.
- Ephemeris coverage and precision vary by body and backend. Inspect errors, warnings, and calculation provenance rather than treating a failed calculation as an empty calendar.
- Symbolic ratings are subjective summaries, not probabilities or guarantees. Do not use readings to make consequential medical, financial, or legal decisions.
- Synastry, solar returns, continuous personal-transit timelines, and PDF export are not implemented. No scheduler or automatic cross-machine memory is bundled.

## Contributing

Astron is developed at **[github.com/wauputr4/astron](https://github.com/wauputr4/astron)**. Bug reports, clearer documentation, calculation tests, accessibility improvements, and code contributions are welcome.

- Open an [issue](https://github.com/wauputr4/astron/issues) with expected/actual behavior and a minimal **synthetic** example. Never attach real birth details, journal databases, or private widget caches.
- For code changes, fork the repository and open a [pull request](https://github.com/wauputr4/astron/pulls). Keep changes focused and add regression tests.
- Run the core tests and optional companion tests using the dedicated Python environment described above:
  ```sh
  "$HOME/.local/share/astron/venv/bin/python" -m unittest discover -s tests -v
  "$HOME/.local/share/astron/venv/bin/python" -m unittest discover -s macos -p 'test_*.py' -v
  ```
- Native UI changes also need the CLT build/signature checks and a separate real-desktop visual test; compilation alone is not proof of rendering.
- Keep the distinction between calculated facts, symbolic interpretation, and subjective feedback. Contributions must preserve consent and privacy boundaries.

The engine and full workflows are AGPL-3.0-only; review dependency terms before redistribution. The isolated ClawHub instruction package is MIT-0. ClawHub publication is separate from a GitHub push.

## License

**AGPL-3.0-only**, except the explicitly isolated files in `distribution/clawhub/`, which are **MIT-0** under their [local LICENSE](distribution/clawhub/LICENSE). The root [LICENSE](LICENSE) continues to apply to the engine, root skill workflows and macOS companion. Kerykeion and pyswisseph retain their own terms.

The ClawHub package consists only of `SKILL.md.in` (renamed `SKILL.md` for publication) and its MIT-0 `LICENSE`. It references the separately installed AGPL engine without bundling or relicensing it. This separation applies to new releases and does not retroactively resolve the old v1.0.0 registry-label discrepancy.
