# ClawHub package

Files in this directory are MIT-0; the rest of Astron remains AGPL-3.0-only unless otherwise stated. Publish only SKILL.md.in renamed to SKILL.md and LICENSE, staged in a temporary directory. The template suffix prevents a second skill from being discovered in the canonical repository.

Review the exact staged file list and run `clawhub skill publish <staging-directory> --slug astron --version <new-version> --dry-run` before publishing. Never publish the repository root to ClawHub. Do not include engine code, third-party dependencies or private records. The instruction package requires separately installed AGPL components for calculations and widgets; installation is explicit, not automatic.

Source and contribution entry point: https://github.com/wauputr4/astron
