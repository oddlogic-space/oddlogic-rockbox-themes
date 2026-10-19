# Status

## In progress
- Standards check follow-up: A.C picks which items from issue #5 to fix (https://github.com/oddlogic-space/oddlogic-rockbox-themes/issues/5).

## Outstanding
- Open PRs waiting on A.C: #2 (pin Noto CJK versions), #3 (shared release checks), #4 (shared font module).
- From issue #5, Review now, waiting on A.C's go: pin the issue digest's actions and mark its output untrusted; security/severity labels and fix deadlines.
- A.C settings: confirm how pushes are signed in, Actions secrets, deploy keys and authorised apps; protect `main` with a ruleset in two stages: now, block force pushes and deletions (the digest bot keeps working); later, also require a pull request, once the digest bot opens PRs instead of pushing; turn on Dependabot alerts, secret scanning and CodeQL.
- A.C to decide: which project moves to a private repo (build tools or the studio app), and whether to scrub its history here.

## Recently done
- 2026-10-19: Recorded in CLAUDE.md: 2FA on (same accounts as batch), GitHub Pro, A.C named by initials.
- 2026-10-19: Kickoff answers recorded in CLAUDE.md (privacy level 4, macOS, Sydney, digest bot exception, WCAG not applied to themes).
- 2026-10-19: Standards check filed as issue #5; date recorded in CLAUDE.md Decisions.
