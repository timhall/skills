---
name: check-pr
description: Check the pull request for the currently checked-out branch/repo for CI failures and code-review comments (human or automated/bot), then fix the underlying issue and push, or reply to and resolve the comment. Use when the user invokes /check-pr or asks to check CI status, review feedback, or comments on their current PR/branch. Also runs one autonomous pass when called by land-pr.
---

Operates on the PR for the branch already checked out in the current repo — no worktree, no branch switching. All `gh` calls below omit `-R`; `gh` infers owner/repo from the git remote.

## Modes

- **Interactive** (default, `/check-pr`): confirms with the user before pushing or posting anything (step 5).
- **Autonomous**: only when `land-pr` calls this skill or the user says so. One pass, no confirmation, bounded by the rules in step 5. Anything outside them is reported as **Needs you** instead of acted on.

Both modes write the evidence into the thread (step 4) so the transcript records what happened, not just "addressed feedback".

## Steps

### 1. Find the PR

```bash
gh pr view --json number,url,title,headRefName,statusCheckRollup,reviewDecision
```

No PR for this branch → say so and stop.

### 2. CI failures

```bash
gh pr checks <number> --json name,bucket,state,link,workflow
```

Each check has a `bucket`: `pass`, `fail`, `pending`, `skipping`, or `cancel`. Only `fail` is a failure to diagnose. `pass` and `skipping` are healthy and `pending` is still running, so ignore all three. For `cancel`, report the check with its link; there is no failure log to read, and in autonomous mode it is **Needs you**.

For each check with `bucket` `fail`:

- If `link` is a GitHub Actions run, pull the failure: `gh run view <run-id> --log-failed` (run id is the numeric segment in the link).
- Non-Actions CI (external link) → note it, tell the user to check the provider's UI, skip.
- Diagnose root cause from the log, don't just retry. Note the fix but hold off committing until step 4 is triaged too — a review comment may touch the same lines.

### 3. Gather review feedback

```bash
gh api repos/{owner}/{repo}/pulls/<number>/comments --paginate      # inline diff comments
gh api repos/{owner}/{repo}/pulls/<number>/reviews --paginate       # review summaries (approve/request-changes body)
gh api repos/{owner}/{repo}/issues/<number>/comments --paginate     # general PR conversation
```

`{owner}/{repo}` from step 1's `url`, or `gh repo view --json nameWithOwner -q .nameWithOwner`.

REST doesn't expose thread resolution — pull that from GraphQL, which also gives the thread `id` needed to resolve later:

```bash
gh api graphql -f query='
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100) {
        nodes {
          id
          isResolved
          comments(first: 50) { nodes { databaseId author { login } body path line } }
        }
      }
    }
  }
}' -f owner=<owner> -f repo=<repo> -F pr=<number>
```

Only threads with `isResolved: false` are live work. A `[bot]` suffix on `author.login` (coderabbitai[bot], github-actions[bot], dependabot[bot], …) marks an automated reviewer — weigh its comments the same as a human's, just note the source when reporting back.

### 4. Triage each unresolved thread/comment

For each, decide:

| Verdict                                                                            | Action                                                                                                |
| ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Actionable, clear fix                                                              | Make the code change, queue a reply describing it                                                     |
| Actionable, but the "fix" is a judgment call (design disagreement, scope question) | Don't resolve unilaterally — draft a reply, flag it for the user to weigh in on in step 5             |
| Already addressed by a prior commit                                                | Reply pointing at the commit, resolve                                                                 |
| Not actionable (stale, out of scope, won't-fix)                                    | Reply with the reason, resolve only if the reasoning is clear-cut — otherwise leave open for the user |

**Write the evidence into the thread before acting**, one entry per item, so the context survives compaction and the user can follow the loop:

- CI failure: check name, link, the log excerpt that shows the cause (the failing assertion or error, not the whole log), and your diagnosis.
- Review comment: author (mark bots), `path:line`, the quoted body, the link, and your verdict from the table above.

Then act, and record the outcome per item (commit sha, reply link, or why it was left alone).

### 5. Confirm before acting

**Interactive.** Present the batch: CI fixes queued, comments to reply-and-resolve, comments to reply-only, and any judgment calls needing the user's input. Get a go-ahead before pushing or posting anything — this touches a shared PR, not just local files.

**Autonomous.** Skip the go-ahead. Act on an item only if all of these hold; otherwise leave it untouched and report it under **Needs you**:

- It is a CI failure caused by this PR's change, or a review comment that is from a bot or a concrete, localized suggestion.
- The fix touches only files already in the PR (`gh pr view --json files`). A new file, or any file outside that list, is **Needs you**.
- The fix needs no new behavior, dependency, or API change.
- It is not the third attempt at the same failing check. Count earlier fix attempts for that check name in this thread; two failed attempts means stop and report with what was tried.
- A merge conflict is **Needs you**, except a rebase with no conflicting hunks.

If the failure looks like a flaky test or infrastructure trouble rather than the PR's code, report it as **Needs you** with the evidence. Do not re-run checks to hide it.

### 6. Apply

- Commit the CI and review fixes (new commits — don't rewrite history on a pushed branch), then `git push`. Never force-push, never merge the PR, never bypass branch protection.
- Reply to an inline thread: `gh api repos/{owner}/{repo}/pulls/<number>/comments/<databaseId>/replies -f body="..."`. Reply to a general comment: `gh pr comment <number> --body "..."`.
- Resolve a thread once its reply is posted:
  ```bash
  gh api graphql -f query='mutation($id: ID!) { resolveReviewThread(input: {threadId: $id}) { thread { isResolved } } }' -f id=<thread-id>
  ```

In autonomous mode, resolve only threads from bots that you fixed or that were already addressed. Reply to a human's thread but leave it for the human to resolve.

### 7. Report

Summarize: what got fixed and pushed, which threads got replied-to-and-resolved, which got a reply but were left open, and which still need the user's judgment. Link the PR.

In autonomous mode, end with the pass's outcome for the caller:

- `Handled:` what was done, with the commit shas and reply links.
- `Needs you:` each unhandled item with its evidence (as in step 4) and why it is outside the rules above. Include any items you did handle.

## Notes

- Never resolve a thread whose disagreement isn't settled — leave it open and flag it rather than guessing at intent.
- Bot and human comments go through the same triage; don't auto-dismiss bot findings.
- If CI and a review comment touch the same lines, fix once and mention both in the commit/reply.
