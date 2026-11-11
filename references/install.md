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

## Earlier read-only discovery: 2026-11-11

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

An HTTP success response alone therefore does not establish that the directory page is available. This was the earlier status; the later actual-install verification below supersedes it.

## How directory listing works

The [official FAQ](https://skills.sh/docs/faq) states that leaderboard listing happens automatically through anonymous installation telemetry when users run `npx skills add <owner/repo>`. This is distinct from read-only `--list` discovery. Do not fabricate installs to raise counts or promise immediate indexing. A repository push updates the GitHub source but does not, by itself, prove that the skills.sh page has refreshed.

After releasing source changes, repeat remote `--list` discovery, then independently inspect the detail page’s visible content. If real users can install but the page remains unavailable, investigate the directory/indexing issue with the upstream service; no local manifest change has been shown necessary here.

Official references:

- [Skills documentation](https://skills.sh/docs)
- [CLI usage](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)
- [Discovery layouts and required frontmatter](https://github.com/vercel-labs/skills/blob/main/docs/creating-skills.md)
- [Telemetry configuration](https://github.com/vercel-labs/skills/blob/main/docs/troubleshooting.md#telemetry)

## License boundary

The full GitHub engine and workflows remain AGPL-3.0-only. The isolated [ClawHub instruction package](../distribution/clawhub/README.md) is MIT-0 and does not bundle the engine or dependencies. Earlier publication notes below are historical; the new split supersedes the publication hold, not earlier-version licensing questions.

## Registry publication and source links

The source repository and contribution entry point are <https://github.com/wauputr4/astron>. `SKILL.md` includes this link in its rendered body and the documented `metadata.openclaw.homepage` field; the README includes repository, issues and contribution links. ClawHub renders `SKILL.md`, so a README-only link is not sufficient to rely on for the skill's rendered page. New metadata will only reach ClawHub after a separate new-version publication, not a GitHub push.

Rechecked the official [skills.sh FAQ](https://skills.sh/docs/faq) and [documentation](https://skills.sh/docs) on 2026-11-11: listing/ranking uses installation telemetry. No additional registration manifest is documented for a public GitHub repository with a discoverable root `SKILL.md`. A source link or `--list` inspection does not create an installation. Do not manufacture installs, promise immediate indexing, or treat a rendered 404 with HTTP 200 as a working listing.

ClawHub requires MIT-0 for published contents. Publish only the staged two-file MIT-0 package described above, never the AGPL repository root. A GitHub push alone does not update the registry. The old v1.0.0 license-label discrepancy is not retroactively resolved by the new package.

## Actual installation and live pages verified: 2026-11-11

After checking the official FAQ and `vercel-labs/skills` telemetry source, performed an actual project-scoped installation in an isolated temporary project—not merely `--list`. No global install, owner birth data, journal access, or live Astron checkout replacement was involved. The supported CLI was used normally, without manually submitting telemetry or altering installation counts. Existing telemetry opt-out settings were not changed. The test command included an explicit purpose label:

```sh
npx --yes skills add wauputr4/astron --skill astron --agent claude-code --copy --yes --metadata '{"purpose":"publisher-install-smoke-test"}'
```

The CLI reported successful installation. The copied `SKILL.md` included the GitHub contribution links, and the native `sky_calendar.py` resource was present. Afterward, both <https://www.skills.sh/wauputr4/astron> and <https://www.skills.sh/wauputr4/astron/astron> returned HTTP 200 and rendered real content: the repository page listed one skill, and the detail page showed the current source/contribution links and Langit & Kamu workflow. They no longer showed the previous 404. This sequence is consistent with the documented installation-telemetry indexing path; no manual registry manifest was added. Displayed install counts are not evidence of completed indexing for every surface and may update separately.

Official badge format: `[![skills.sh](https://skills.sh/b/owner/repo)](https://skills.sh/owner/repo)` from <https://www.skills.sh/docs>. The README uses the same official route on its canonical `www.skills.sh` host (verified SVG), not a custom Shields.io substitute. ClawHub's latest was independently rechecked as v1.0.0 with MIT-0; source updates on GitHub do not update that release. No official ClawHub README-badge endpoint has been verified, so its legacy listing is a plain link instead of a custom badge presented as official.
