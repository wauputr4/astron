# Astron

A personal astrology agent skill for private, reflective conversations. Computes natal data, general sky events, transit windows, secondary progressions and natal SVG charts. Astrology is symbolic reflection, not a scientific personality test or a guarantee of future events.

## Setup

Requires Python 3.12+ and local ephemeris support. Install in an isolated environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
```

Install this directory as an AgentSkill and invoke `astron`; follow [SKILL.md](SKILL.md) for the JSON inputs and onboarding. No account, hosted AI service, or Hermex installation is required for local calculations. The chat provider may process conversations. Personal profiles and generated exports should stay outside the repository.

## Scope and limitations

Charts use tropical geocentric positions and Placidus houses. If time is unknown, the basic chart uses a disclosed noon snapshot without houses; advanced features require a known time. Transit windows use sampling and may be clipped; not every closest point is exact. Ephemeris coverage and per-body precision vary; inspect errors and provenance. Calendar calculations currently include lunations, planetary aspects and stations, not eclipse or personal-transit integration. SVGs contain birth data. Automations, PDF exports and synastry are not implemented.

## License

AGPL-3.0-only. Kerykeion and pyswisseph have their own license terms; consult their upstream licenses before distribution or public deployment.
