---
name: land-pr
description: >-
  Publish this thread's work as a GitHub PR, then drive it to "ready": watch CI and
  bot reviews, fix what is clearly fixable, and call the user back only when needed.
  Never merges the PR. Use when the user presses Merge or asks to land the change.
  Do not use for review or preparation.
metadata:
  delta-action: land
---

The user pressing Merge means the direction is approved. Own the loop until GitHub is happy, then hand back. Run in the Delta Merge thread so the parent keeps its own context.

Built on two pieces. `scripts/watch-pr` blocks until the PR changes; read [watching.md](watching.md) before the first loop. The `check-pr` skill, in autonomous mode, handles one wake-up.

## Limits

- **Never merge the PR.** Never use admin override or bypass branch protection. Enabling auto-merge is allowed only if the repo's rules opt in (see Repo configuration). Default is off.
- **Never force-push.**
- **Call the user back** (end the turn with a message starting `Needs you:`) when:
  - `check-pr` reports **Needs you** (outside its autonomy rules, same check failed twice, merge conflict, flaky-looking failure, a file outside the PR's diff).
  - 10 wake-ups have been handled.
  - The watch times out before the PR is ready.
- Human review and approval are outside the loop. Never wait for them before reporting **Ready**.

## Repo configuration

This skill is installed per repo and is the same in every repo. A repo's own rules go in its `AGENTS.md` (or `CLAUDE.md`), not in this file. Read them before publishing. Where a rule is absent, use the default:

| Rule | Default |
|---|---|
| Base branch | the repo's default branch |
| Checks to run before pushing | the test and lint commands the repo documents; none if it documents none |
| Merge method for auto-merge | `gh repo view --json viewerDefaultMergeMethod` |
| Auto-merge | off |
| Commit and PR conventions (title format, template, attribution) | the repo's existing history and PR template |

A repo that merges by hand, for example with admin override, says so in `AGENTS.md`. This skill never merges either way, but the note keeps it from enabling auto-merge. Example:

```markdown
## Landing

- Before pushing: `pnpm verify`
- Merge method: squash
- Auto-merge: no. A person merges, using admin override.
```

## Steps

### 1. Publish

1. Commit uncommitted work using the repo's conventions. Run the repo's own checks and fix failures before pushing.
2. Push the branch. If the branch already has a PR, reuse it; otherwise open one with `gh pr create`, following the PR template if the repo has one.

No remote, no `gh` auth, or a failed push: stop with `Needs you:` and the error.

### 2. Arm the watch

1. Wait about a minute so checks register, then run `scripts/watch-pr snapshot` and take its `fingerprint:` as the baseline.
2. Write a loop-state line in the thread. It is how you recover after compaction or a restart:

   `Loop: PR <url> | wake-ups 0/10 | started <time> | ready-since - | fix attempts: -`

3. Start `scripts/watch-pr wait --baseline <fingerprint> --timeout <time left of 24h>` as a **background terminal**, then end the turn with one line (`Watching <url>.`). The terminal's exit wakes the thread.

### 3. On each wake-up

Read the output's first line and exit status.

| Result | Action |
|---|---|
| PR merged | Report **Merged** with the merge commit. End. |
| PR closed unmerged | Report it as `Needs you:`. End. |
| Timeout (exit 8) before ready | `Needs you:` with the last state. End. |
| Timeout after ready | Say the PR is still open and the watch ended. End. |
| Error (exit 1) | Retry once; then `Needs you:` with the error. |
| Changed | Run `check-pr` in autonomous mode, then follow the next step. |

Count the wake-up and update the loop-state line (wake-ups, fix attempts per check name).

### 4. After `check-pr`

- **Needs you** → end the turn with `Needs you:`, quoting each item's evidence. Say what was already handled.
- **Handled** → wait about a minute if `check-pr` pushed (so checks register), then run `scripts/watch-pr snapshot`. Read it for anything `check-pr` didn't see; a comment may have arrived while it worked, and the new baseline would hide it. If there is such an item, run `check-pr` again.
  - `ready: yes` with checks reported → step 5.
  - Otherwise re-arm as in step 2.3 with the snapshot's fingerprint.

### 5. Ready

1. Post a `Ready:` summary in the thread: PR link, check results, which bot threads were handled and how, and what is left (human review, with the reviewers if known).
2. If the repo opted in to auto-merge, enable it (`gh pr merge --auto` with the repo's merge method) and say so.
3. Set `ready-since` in the loop-state line and arm the watch again for up to 24 hours. Wake-ups now are the PR merging, new human feedback, a new commit, or a changed check. Handle them as in step 3. Human feedback that needs judgement is `Needs you:`.

Report **Merged** only when the PR is actually merged. Use the result card Delta provides in this thread if there is one; otherwise say it in plain text.

## If the user replies mid-loop

Answer or act on it, then take a fresh snapshot and re-arm. A `Needs you:` stop does not end the job; resuming means going back to step 2.
