# The watcher

`scripts/watch-pr`, in this skill's folder, blocks until a GitHub PR changes and then reports its current state. It is deterministic shell over `gh` and `jq` and makes no model calls. Needs `gh` authenticated with `repo` scope.

## Use

Run from this skill's folder:

```bash
scripts/watch-pr snapshot [--pr REF]
scripts/watch-pr wait --baseline FINGERPRINT [--pr REF] [--timeout 24h] [--heartbeat 120] [--poll 30]
```

`REF` is a number, URL, or branch; default is the current branch's PR.

1. `snapshot` prints the PR's state and a last line `fingerprint: ...`.
2. Run `wait --baseline <that fingerprint>` **in the background** (the terminal tool's `background: true`). It exits when the PR differs from the baseline, and Delta wakes the thread with its output.
3. After handling the change, take a fresh `snapshot` and use its fingerprint as the next baseline. Your own pushes and resolutions change the PR, so reusing the old baseline wakes you on your own actions.

| Exit | Meaning |
|---|---|
| 0 | Changed, or the PR is no longer open. First line names the changed components. |
| 8 | `--timeout` reached with no change. Re-arm or stop. |
| 1 | Error. |

## What changes the fingerprint

| Component | Changes when |
|---|---|
| `state` | open, closed, merged, or draft status changes |
| `head` | the branch gets a new commit |
| `conflict` | the PR starts or stops conflicting with its base |
| `checks` | a check fails while others run, or the last pending check finishes |
| `threads` | an unresolved thread appears, is resolved, or gets a reply from someone else |
| `comments` | someone else posts a conversation comment |
| `reviews` | someone else submits a review |

"Someone else" means anyone but the authenticated `gh` user, so the agent's own replies don't wake it. The same rule means comments you post by hand as that user don't wake it either.

Checks finishing one by one while others still run does not change the fingerprint, so a CI run produces one wake-up when it settles (or at the first failure).

## Limits

- **Right after a push, checks may not be registered yet.** `snapshot` then says `0 reported` and `ready: yes`. Wait about a minute and snapshot again before trusting `ready`.
- **A comment that arrives while you are handling a wake-up is absorbed by the next baseline.** When you take the fresh snapshot, read its threads, comments, and reviews and handle anything you haven't seen.
- **Edits to existing comments are not detected.**
- **Events:** `wait` first tries `gh event listen` (needs `gh` 2.105+ and event subscriptions enabled for the account) and falls back to polling every `--poll` seconds when the stream is unavailable. Either way it re-reads the PR every `--heartbeat` seconds, so missed events cost latency, not correctness. The event path has not been exercised against a real stream; the polling path has.

## Test

`scripts/test.sh` checks the fingerprint rules offline against fixture JSON.
