---
name: agent-eval
description: Measure whether a line of AGENTS.md or CLAUDE.md actually changes how an agent works. Use when editing agent instructions, when deciding which guidance to keep or delete, or when the instructions file is growing too long.
---

# Agent eval

Each claim in the instructions file is a test case. A trial runs one coding task in a fresh agent session; the scorer then asserts over the tool calls the agent made and the diff it produced.

## Setup

Needs a git repo with worktree support and the `claude` CLI on PATH. Unlike the other skills in this repo, install this one **per target repo** rather than symlinking a single shared copy — `assertions.json` and `tasks/` are meant to diverge, since they encode that repo's own commands and claims:

```sh
cd <target repo>                                  # not this one
npx skills add timhall/skills --skill agent-eval -a claude-code
```

Run without `-g`, this lands project-local at `./.claude/skills/agent-eval/` — a real copy, not a symlink — which you then commit to the target repo. `assertions.json` and `tasks/example.md` as shipped here are a template: keep the shape, replace the content the first time this runs for real, and let that copy diverge from this one from there on.

## Steps

1. **Identify the claim.** Use the line the user pointed at, or ask which line in `AGENTS.md`/`CLAUDE.md` is in question. A claim with no task reaching it is unfalsifiable — don't proceed without one.

2. **Find or write the task.** Check `tasks/` for one that already exercises the claim. If none exists, write one following `tasks/example.md`'s shape (Problem, Fix) — a task works when the fix is unambiguous, so trials differ in process rather than in approach. Show it to the user and write down the expected outcome before running anything; any transcript reads as a success after the fact.

3. **Find or write the assertion.** Check `assertions.json` for an entry testing this claim; if none exists, add one. Name the claim it tests, and set `on` to `files` or `diff` when it needs to check what changed rather than what commands ran. If the claim can't be written as an assertion, say so — that alone is evidence against keeping the line.

4. **Resolve the two refs.** "With guidance" is the ref carrying the claim — usually `HEAD`, or the working tree via `EVAL_OVERLAY_DOC` if it's still uncommitted. "Without guidance" is a ref before the claim existed; `git log -S '<snippet>' -- AGENTS.md` finds when a line was added, and its parent is the control ref. Ask rather than guess if this doesn't resolve unambiguously.

5. **Run three trials per arm** — one run cannot separate an effect from noise — labelled so each is traceable to its arm:

   ```sh
   for n in 1 2 3; do skills/agent-eval/run.sh tasks/<task>.md <with-ref> withdoc$n; done
   for n in 1 2 3; do skills/agent-eval/run.sh tasks/<task>.md <without-ref> control$n; done
   ```

   `EVAL_DOC` names the file under test if it isn't `AGENTS.md`. `EVAL_SETUP` overrides the install step if the repo isn't a plain `pnpm`/`yarn`/`npm` install.

6. **Score and report:**

   ```sh
   node skills/agent-eval/score.mjs .agents/eval-results/*.json
   ```

   Read the table against the rubric below, read any failure before concluding from it — an assertion matches a pattern, not an intent, and an agent can satisfy the intent another way — then report the verdict itself (keep / delete / reword / investigate), not just the raw table.

## Read the result

A single arm measures the model, not the document. Compare the two.

| Control | With guidance | Verdict                                            |
| ------- | ------------- | -------------------------------------------------- |
| fail    | pass          | The line works. Keep it.                           |
| pass    | pass          | The line is a no-op. Consider deleting it.         |
| fail    | fail          | The line is unlearnable. Reword once, then delete. |
| pass    | fail          | The line does harm. Investigate.                   |

A no-op is not always a deletion. A line that prevents a rare but expensive failure earns its place even when the model rarely needs it. Treat tool calls and seconds as description, not evidence.

## Constraints

- **Run trials one at a time** if a task reaches shared external state — a database, fixed ports, named Docker containers — that concurrent worktrees would collide on.
- **Keep the arm type constant.** A subagent and a `claude -p` session load different instructions, which is a second variable. Subagents do not receive the instructions file at all unless the parent session loaded it at startup.
