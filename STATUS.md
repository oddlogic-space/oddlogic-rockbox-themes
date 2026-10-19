# Status

## In progress
- Standards check follow-up: A.C picks which items from issue #5 to fix (https://github.com/oddlogic-space/oddlogic-rockbox-themes/issues/5).

## Outstanding
- A.C settings: limit the Cloudflare Workers and Pages GitHub App to the repos that need it (this repo doesn't); turn on private vulnerability reporting; protect `main` with a ruleset in two stages: now, block force pushes and deletions (the digest bot keeps working); later, also require a pull request, once the digest bot opens PRs instead of pushing.
- A.C to decide: which project moves to a private repo (build tools or the studio app), and whether to scrub its history here.

## Recently done
- 2026-10-19: `tools/verify-rebuild.sh` PASSes for all five themes with the pinned packages (Pillow 12.3.0, numpy 2.5.4, fontTools 4.67.0) and the pinned Noto fonts. Pillow 13.0.0 fails the Studio Console font build, so Pillow stays on 12.3.0.
- 2026-10-19: Issue digest fixed: runs fired close together failed to push ("fetch first") because each checked out the commit its event fired on; it now checks out the newest main.
- 2026-10-19: A.C merged #2 (pin Noto CJK), #3 (shared release checks) and #4 (shared font module).
- 2026-10-19: Access checked with A.C: browser only, no tokens, SSH keys, Actions secrets, deploy keys or webhooks; apps are Claude and Cloudflare Workers and Pages.
- 2026-10-19: A.C created the `security` and `sev-*` labels, and turned on Dependabot alerts, secret scanning with push protection, and CodeQL default setup.
- 2026-10-19: Checks workflow added (Gitleaks, pip-audit); Issue digest actions pinned and its output marked untrusted; security labels and fix deadlines in CLAUDE.md; no scheduled issue check for this repo.
- 2026-10-19: Recorded in CLAUDE.md: 2FA on (same accounts as batch), GitHub Pro, A.C named by initials.
- 2026-10-19: Kickoff answers recorded in CLAUDE.md (privacy level 4, macOS, Sydney, digest bot exception, WCAG not applied to themes).
- 2026-10-19: Standards check filed as issue #5; date recorded in CLAUDE.md Decisions.
