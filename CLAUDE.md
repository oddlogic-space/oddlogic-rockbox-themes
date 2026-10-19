# CLAUDE.md

## Who and where

- Run by A.C at Oddlogic (oddlogic.space). Refer to them as **A.C** everywhere: repo files, commits, PRs and issues. Never write their full name.
- Owner account: `oddlogic-space` on GitHub (Pro plan, upgraded 19 Oct 2026). Only A.C merges; Claude works on a branch and opens a PR, never pushes to `main`.
- A.C's computer: macOS (write instructions for Terminal, `sed -i ''`, the Passwords app).
- Time zone: Australia/Sydney, for dates and any scheduled checks.
- Public contact: themes@oddlogic.space (as in the theme licence files).
- Two-factor sign-in is on for GitHub (`oddlogic-space`), Cloudflare and Google (A.C, 19 Oct, the same accounts as oddlogic-space/batch). Both claude.ai accounts sign in with an emailed link to a Proton mailbox that has two-factor on.
- CONTACT_TO and ALERT_TO: not needed; there is no website.
- Tokens and access (names only, never values):
  - `GITHUB_TOKEN`, created automatically for each run of the Issue digest workflow; `contents: write`, `issues: read`; expires when the run ends.
  - The Claude GitHub App, for Claude Code sessions.
  - The Claude Project's GitHub connection, which reads repo files.
  - None of the tokens listed in oddlogic-space/batch's CLAUDE.md reaches this repo.
  - How A.C pushes from their Mac, any Actions secrets, deploy keys or other apps with access: still to be checked (issue #5).

## Privacy

Level 4, no personal data: the themes and the build tools collect none. Bug reports are public GitHub issues and stay on GitHub. Each PR states the three checks level 4 needs: Need, Processors, Security.

## Decisions

- 2026-10-19: Checked against the Project Standards doc (https://claude.ai/code/artifact/9975d992-47f2-4117-b194-20013013137d), rev 15, first check; whole doc and change log reviewed. Nothing adopted yet; findings and questions for A.C in https://github.com/oddlogic-space/oddlogic-rockbox-themes/issues/5.
- 2026-10-19 (A.C): Privacy coverage is level 4, no personal data.
- 2026-10-19 (A.C): The WCAG contrast target does not apply to theme designs.
- 2026-10-19 (A.C): The Issue digest workflow may keep committing `tracking/issues.md` straight to `main`. It touches only that file. Revisit when `main` is protected.
- 2026-10-19 (A.C): Repo stays public for now. Moving the build tools or the studio app to a private repo is under consideration; A.C is tracing that project's history first.
