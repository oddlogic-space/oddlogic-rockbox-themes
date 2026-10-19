# CLAUDE.md

## Who and where

- Owner: the `oddlogic-space` GitHub account. Only the owner merges; Claude works on a branch and opens a PR, never pushes to `main`.
- Owner's computer: macOS (write instructions for Terminal, `sed -i ''`, the Passwords app).
- Time zone: Australia/Sydney, for dates and any scheduled checks.
- Public contact: themes@oddlogic.space (as in the theme licence files).
- CONTACT_TO and ALERT_TO: not needed; there is no website.
- Tokens and access (names only, never values):
  - `GITHUB_TOKEN`, created automatically for each run of the Issue digest workflow; `contents: write`, `issues: read`; expires when the run ends.
  - The Claude GitHub App, for Claude Code sessions.
  - The Claude Project's GitHub connection, which reads repo files.
  - The owner's own personal tokens, SSH keys and app sign-ins: still to be checked (issue #5).

## Privacy

Level 4, no personal data: the themes and the build tools collect none. Bug reports are public GitHub issues and stay on GitHub. Each PR states the three checks level 4 needs: Need, Processors, Security.

## Decisions

- 2026-10-19: Checked against the Project Standards doc (https://claude.ai/code/artifact/9975d992-47f2-4117-b194-20013013137d), rev 15, first check; whole doc and change log reviewed. Nothing adopted yet; findings and owner questions in https://github.com/oddlogic-space/oddlogic-rockbox-themes/issues/5.
- 2026-10-19 (owner): Privacy coverage is level 4, no personal data.
- 2026-10-19 (owner): The WCAG contrast target does not apply to theme designs.
- 2026-10-19 (owner): The Issue digest workflow may keep committing `tracking/issues.md` straight to `main`. It touches only that file. Revisit when `main` is protected.
- 2026-10-19 (owner): Repo stays public for now. Moving the build tools or the studio app to a private repo is under consideration; the owner is tracing that project's history first.
