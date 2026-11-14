# Astron

[![skills.sh](https://www.skills.sh/b/wauputr4/astron)](https://skills.sh/wauputr4/astron)
[ClawHub — MIT-0 instructions](https://clawhub.ai/wauputr4/skills/astron)

[GitHub repository](https://github.com/wauputr4/astron) · [Report an issue](https://github.com/wauputr4/astron/issues) · [Contribute](#contributing)

An astrology companion for your AI agent: calculate a chart, explore a period, and reflect on what actually happened. Astron combines local astronomical calculations with plain-language, symbolic interpretation and an optional private journal.

**Astrology is a reflective practice, not a scientific personality test, a diagnosis, or a reliable prediction of future events.**

## What you can do

- **Understand your natal chart.** Calculate planetary placements and aspects, then explore them at your preferred level of detail. With a known birth time, include houses and angles; without one, use a disclosed noon snapshot without houses.
- **Explore a date range.** Calculate personal transit windows or secondary progressions and turn the results into tentative themes, questions, and practical actions. Keep computed contacts separate from interpretation.
- **Build a sky calendar.** Calculate lunations, planetary aspects, and retrograde/direct stations for a chosen period and timezone. Optionally compare sky-event positions with your natal chart using an explicit aspect and orb; a general sky event is not automatically a personal transit.
- **Export your chart.** Generate a natal SVG wheel or save calculation results as JSON in a private location.
- **Review earlier readings honestly.** Preserve the original projection, record an independent check-in before revealing it, then review matches, partial matches, misses, and uncertainty. Optional fit, usefulness, and clarity ratings stay separate.
- **Carry forward lessons you approve.** Save contextual, reviewable lessons and small action experiments. Personalization uses your feedback; it is not model retraining or evidence that astrology predicts outcomes.
- **Reflect on relationships.** Keep optional alias-based notes about friends, colleagues, or partners, separating observations from interpretations and considering alternative explanations. Without voluntarily supplied birth details, use behavior-based reflection—not an invented chart.

## Install

Use the maintained [skills CLI](https://github.com/vercel-labs/skills) with Node.js/npm available:

```sh
npx skills add wauputr4/astron --skill astron
```

Follow its prompts to choose a supported agent and installation scope. The command installs the skill instructions and resources; it does **not** install Python dependencies, create a personal profile, start onboarding, or install a macOS app.

To inspect the public repository without installing:

```sh
npx skills add wauputr4/astron --skill astron --list
```

**Verified availability (2026-11-11):** a real, project-scoped skills CLI installation from GitHub succeeded in an isolated temporary project, including the latest skill instructions and native calendar resources. Both the [skills.sh repository page](https://www.skills.sh/wauputr4/astron) and [Astron detail page](https://www.skills.sh/wauputr4/astron/astron) now render successfully with the current skill content. Earlier read-only `--list` checks did not register an installation and were insufficient to verify directory availability. Install counts may update separately; no count is claimed here. See [installation and discovery notes](references/install.md).

**Distribution policy:** GitHub is the canonical source for the full AGPL-3.0-only Astron engine and workflows. ClawHub distributes a separate MIT-0 instruction package; it does not bundle the Python engine, dependencies or macOS companion. See [publication instructions](distribution/clawhub/README.md). The skills.sh badge is an official install-count badge, not a compatibility certification.

## Start a conversation

After installation, explicitly ask your agent to use Astron. Installation alone cannot start a conversation.

> Use Astron. I’m new to astrology—help me set up my birth chart, explain the basics, and ask before saving anything.

Astron asks for missing birth details: date, local time if known, and birthplace. It resolves coordinates and the historical timezone rather than guessing. Unknown or uncertain birth time should be disclosed, not replaced with a fabricated precise time. You can decline saving and use it for a single conversation.

Try these prompts:

- “Show the decan of my Sun and explain how its face ruler relates to this placement.” Both natal JSON calculators accept the optional top-level field `"include_decans": true`. They report Chaldean faces for the seven classical bodies. To include Ascendant and Descendant faces, also set `"time_confirmed": true` beside the confirmed birth time (inside `birth` for `astron.py`, at the top level for `chart.py`). A chart with unknown birth time reports provisional noon placements.
- “Use Astron to explain my natal chart in everyday English. Give me three questions I can disagree with.”
- “Calculate my transits for next month. Separate the calculation evidence, approximate timing, and symbolic interpretation.”
- “Create a sky calendar for December 2026 in Asia/Jakarta, with lunations, aspects, and stations. Show local dates and the calculation source.”
- “For that calendar, optionally check contacts to my natal chart. State the aspect and orb, and don’t call a snapshot an exact personal transit.”
- “Save this projection only after I approve it. When we review it, ask for my experience before showing the original.”
- “Review last month’s reading. Keep the misses and uncertainty, and ask which lesson—if any—I want to retain.”
- “Help me reflect on a difficult interaction with a colleague. Use an alias, separate facts from my assumptions, and suggest alternative explanations.”
- “Export my natal chart as SVG to a private folder. Don’t share it.”

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

## Optional macOS companion

Astron’s core features work without a desktop app. The optional [macOS companion](macos/README.md) includes two WidgetKit configurations:

- **Refleksi Hari Ini:** a compact reflective question and capture shortcut. Expanded app controls connect an existing self journal, save only with consent, and review approved lessons privately.
- **Langit & Kamu:** a monthly event calendar; medium/large widgets put the next event and symbolic interpretation beside it. Click a date for details, choose a month/timezone, and optionally enable natal-contact snapshots with a stated 2° orb.

The source builds with Swift and Apple Command Line Tools, without full Xcode. From `macos/`, run `rtk proxy /usr/bin/python3 build.py --install` after completing Python setup. The local installer backs up the existing app, ad-hoc signs/verifies the bundles and registers the extension. It records the checkout/interpreter paths; keep the checkout in place or rebuild after moving it. `rtk` is required by this build wrapper. No notarized binary release is supplied.

The companion is separate from `npx skills add`. Personal desktop output is off by default and requires a selected consented self profile, known birth time and separate display opt-in. Names, birth details and raw journal text do not enter widget caches. Opening capture never automatically saves. Calendars refresh manually; no scheduler is installed.

**Verification (2026-11-11):** 28 core tests plus 16 bridge/calendar tests passed; the CLT build, signature verification, local installation and extension registration succeeded. Desktop verification subsequently exposed an extension bootstrap crash; the CLT linker now enters through `_NSExtensionMain` while retaining the Swift `_main`. After rebuild/install, both widget configurations appeared in the gallery (all supported size previews rendered). A medium Langit & Kamu widget rendered on the desktop, and clicking November 13 opened the corresponding Mercury-direct detail in the companion. Calendar date selection, capture navigation and journal settings were inspected without saving records or enabling natal display. Small/large desktop placement and consented journal saving were not tested; gallery previews are not placement proof.

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
