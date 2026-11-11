# Installation and skills.sh discovery

## Install from GitHub

With Node.js/npm available:

```sh
npx skills add wauputr4/astron --skill astron
```

The maintained CLI is [`vercel-labs/skills`](https://github.com/vercel-labs/skills), published as the npm package `skills`. It prompts for agent targets and scope. Project installation is the default; `--global` explicitly selects user-level installation. Review the prompts rather than adding global or unattended flags unnecessarily.

This installs the AgentSkill, not Python packages or a native application. Follow the [README setup section](../README.md#local-calculation-setup), then explicitly ask your agent to use Astron. If your host does not discover skills automatically, consult its own skill-location and reload instructions.

## Inspect without installing

```sh
npx skills add wauputr4/astron --skill astron --list
```

`--list` clones the public source for inspection and lists discovered skills without installing them into agent directories. Running via `npx` may download/cache the CLI and contact npm/GitHub; it is not an offline operation. The CLI documents `DISABLE_TELEMETRY=1` or `DO_NOT_TRACK=1` for opting out of telemetry and security-audit requests.

The repository-root `SKILL.md` with `name` and `description` frontmatter is a supported discovery layout. No separate registry manifest is required for this layout.

## Verified status: 2026-11-11

Commands run:

```sh
npx --yes skills --version
# 1.8.1

npm view skills repository.url version
# repository.url = 'git+https://github.com/vercel-labs/skills.git'
# version = '1.8.1'

npx --yes skills add wauputr4/astron --skill astron --list
```

The last command exited successfully and reported the following (terminal banner and animated progress omitted; wording preserved):

```text
◇  Source: https://github.com/wauputr4/astron.git
◇  Repository cloned
◇  Found 1 skill
◇  Available Skills
│    astron
│      Personal astrology companion for calculating and interpreting natal charts, with first-use birth-profile onboarding and conversational feedback. Use for personal natal readings or astrology questions involving the user's chart.
└  Use --skill <name> to install specific skills
```

This verifies discovery of the **then-published remote source**, not unpushed local changes, Python setup, agent invocation, or desktop functionality. No global or project skill installation was performed during this check.

The detail URL <https://skills.sh/wauputr4/astron/astron> returned HTTP 200 but displayed an in-page 404:

```text
404
astron
isn’t available in this repository.
It may have been renamed or removed.
```

An HTTP success response alone therefore does not establish that the directory page is available. The directory/indexing status remains unresolved even though direct CLI discovery works.

## How directory listing works

The [official FAQ](https://skills.sh/docs/faq) states that leaderboard listing happens automatically through anonymous installation telemetry when users run `npx skills add <owner/repo>`. This is distinct from read-only `--list` discovery. Do not fabricate installs to raise counts or promise immediate indexing. A repository push updates the GitHub source but does not, by itself, prove that the skills.sh page has refreshed.

After releasing source changes, repeat remote `--list` discovery, then independently inspect the detail page’s visible content. If real users can install but the page remains unavailable, investigate the directory/indexing issue with the upstream service; no local manifest change has been shown necessary here.

Official references:

- [Skills documentation](https://skills.sh/docs)
- [CLI usage](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)
- [Discovery layouts and required frontmatter](https://github.com/vercel-labs/skills/blob/main/docs/creating-skills.md)
- [Telemetry configuration](https://github.com/vercel-labs/skills/blob/main/docs/troubleshooting.md#telemetry)

## License caution

The GitHub repository is AGPL-3.0-only. Its ClawHub listing has an unresolved MIT-0 platform-label discrepancy; see the [README license note](../README.md#license). Directory availability does not resolve licensing terms.


## Registry publication and source links

The source repository and contribution entry point are <https://github.com/wauputr4/astron>. `SKILL.md` includes this link in its rendered body and the documented `metadata.openclaw.homepage` field; the README includes repository, issues and contribution links. ClawHub renders `SKILL.md`, so a README-only link is not sufficient to rely on for the skill's rendered page. New metadata will only reach ClawHub after a separate new-version publication, not a GitHub push.

Rechecked the official [skills.sh FAQ](https://skills.sh/docs/faq) and [documentation](https://skills.sh/docs) on 2026-11-11: listing/ranking uses installation telemetry. No additional registration manifest is documented for a public GitHub repository with a discoverable root `SKILL.md`. A source link or `--list` inspection does not create an installation. Do not manufacture installs, promise immediate indexing, or treat a rendered 404 with HTTP 200 as a working listing.

ClawHub's [skill-format license policy](https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md#license) requires MIT-0 for every published skill and explicitly disallows conflicting terms or per-skill overrides. Astron's repository remains AGPL-3.0-only; no license change or new ClawHub publication is authorized by merely adding source links. Resolve rights and licensing before republishing; keep upstream dependency obligations intact.


## Current distribution decision

Keep AGPL-3.0-only and GitHub as the canonical distribution path. The existing ClawHub v1.0.0 listing is legacy; do not republish the AGPL bundle under MIT-0 or imply that it contains the latest GitHub functionality. No separate MIT-0 package is planned by this change. README badges link to the official skills.sh repository badge and the explicitly labeled legacy ClawHub listing; badges are navigation/status aids, not evidence of indexing, compatibility, or desktop verification.
