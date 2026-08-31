---
name: work
description: Step through a plan's tasks with managed context and worktree isolation. Use when the user wants to start or continue work on a piece of work. Accepts an issue id (`/work 50`), a mission id (`/work M20`), or an external ticket key (`/work APICLIENT-4062`).
---

Read the **Notes vault** path from the `## Agent skills` section of CLAUDE.md — use it wherever `{notes vault}` appears below.

Work happens at **task** level. A task lives in a plan; a plan belongs to one issue. See the tracker contract (`~/.claude/agents/issue-tracker.md`) for the model.

## Steps

### 1. Resolve the target

| Argument | Means |
|---|---|
| `50` | local issue 50 |
| `M20` | local mission 20 — resolve to its next unfinished issue via `track list -q mission=20` |
| `APICLIENT-4062` | external ticket |

Then find the plan: `track path plan <arg>` — it accepts all three forms. `track get plan <arg> --json` gives the frontmatter, body, and a `tasks: {done, total}` count.

If there is no plan, say so and offer `/plan <arg>` to create one. Do not invent tasks without a plan.

For a local issue, also read the issue itself (`track get issue <id>`) for the problem and prior investigation. For an external ticket, the ticket is the source of truth for *what* — fetch it if you need the statement of the problem.

### 2. Pick the next task

Tasks live under `## Tasks` in `plan.md` as ordered checkboxes. Unchecked items are outstanding; `## Progress` records what has landed.

- Respect any `Blocked by:` note — only offer a task whose blockers are ticked.
- If a task was promoted to its own file (`NN-<slug>.md`, colocated in the plan folder), read that file for the detail.
- Design docs in the plan folder are context, not tasks.

### 3. Present and confirm

Show the plan title, the done/total count, the **next task**, and what remains. Ask before starting.

### 4. Worktree

Read `delivery:` from the plan frontmatter — `per-task` (default) or `single-pr`. For `per-task`, one worktree per task; for `single-pr`, one for the whole plan, reused.

Branch naming, and this matters:

- **External ticket** — `APICLIENT-4062/<task-slug>`. The Jira key is the repo's own convention.
- **Local issue or mission** — use a descriptive slug only, e.g. `fix/graphql-cookie-context`. **Never put a local issue or mission id in a branch name.** Branches are pushed; that would leak an internal tracker reference into the repo.

Use the EnterWorktree tool. Always state the branch name before creating it.

### 5. Load context

Brief the task concisely: what it builds, its acceptance criteria, and the plan's `## Approach` (the seam, and anything already ruled out). Don't re-derive what the plan settled.

### 6. Work

Stay in the task's scope. Flag anything out of scope and ask before expanding — a task that grows is usually a missing task, or an issue of its own.

### 7. On completion

1. Tick the task's checkbox in `plan.md`.
2. Add a line to the plan's `## Progress` — what landed, with the PR link.
3. **Findings go to the issue or ticket, not the plan.** If the work confirmed or refuted something, record it there (`track set` for a local issue; the ticket itself for an external one). The plan is a working space.
4. If every task is ticked, set the plan's `status: done` and update the issue (`track set issue <id> status=resolved`) if the work is genuinely finished.
5. Tell the user the next task and that `/work <arg>` continues.

## Notes

- Progress through an issue is progress through its plan; progress through a mission is progress through its issues. Don't hand-maintain a separate tally.
- A task that turns out to be independently valuable and closable is an issue, not a task — offer `/issue` rather than growing the plan.
- If a plan exceeds roughly ten tasks, say so: the work is probably mission-shaped and wants splitting into issues.
- Never hand-edit frontmatter; `track set` owns it.
