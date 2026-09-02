---
name: plan
description: Create or open a plan for a piece of work in {notes vault}/Plans/. Use when an issue needs a plan of tasks before implementation, when a mission needs slicing into issues, or when the user says "/plan <id>" — accepts a local issue id (`/plan 50`), a local mission id (`/plan M23`), or an external ticket key (`/plan APICLIENT-4053`).
---

Read the **Notes vault** path from the `## Agent skills` section of CLAUDE.md — use it wherever `{notes vault}` appears below.

A **plan** says *how* a piece of work gets done. It lives at `{notes vault}/Plans/<key>/plan.md`, alongside its tasks and any design docs.

The folder name *is* the link to the work — there is no pointer field. Key by the owner:

| Argument | Key | Means | Plan holds |
|---|---|---|---|
| `50` | `0050-<slug>` | local issue 50 | tasks |
| `M23` | `M0023-<slug>` | local mission 23 | decisions + an issue set |
| `APICLIENT-4053` | `APICLIENT-4053` | external ticket, verbatim | tasks |

Bare integer = local issue; `M`-prefixed = local mission; anything else is an external ticket key, used verbatim.

**A mission plans differently.** Its slices are issues, not tasks — they leave the plan and live on their own. If the target is a mission, read `mission-plan.md` (colocated) and follow it instead of the steps below.

## Steps

1. **Resolve the target.**
   - **Local issue** (bare integer) — `track path issue <id>`. Read it for the problem and any prior investigation.
   - **Local mission** (`M`-prefixed) — stop here and switch to `mission-plan.md`.
   - **External** (letter-prefixed key) — fetch the ticket, including comments. For an `APICLIENT-*` key use the Atlassian MCP with cloudId `postmanlabs.atlassian.net` (not `postman.atlassian.net` — that one is not granted). For a GitHub issue use `gh issue view`. **Do not create a local issue and do not mirror the description.** The ticket stays the source of truth for *what*; the plan is only *how*.
   - Treat the ticket's stated root cause as a claim, not a finding — auto-filed tickets often carry an unverified hypothesis.

2. **Explore the code before planning.** A plan is the *how*, so it needs the seam it will be tested at and the prior art near it. Name the repo and the seam in the plan. Search for related local issues and missions (`track list -q status=open,investigating`) — prior investigation often already exists.

3. **Check for an existing plan** at `Plans/<key>/`. If one exists, read it and continue that plan rather than starting over.

4. **Write `plan.md`** using the template below. Keep the problem statement to a paragraph — for an external ticket, restate it briefly and link out rather than copying.

5. **Draft the tasks.** Vertical slices, each independently verifiable, each sized to fit one fresh context window. Order them; note `Blocked by` only where the order isn't a straight line.

   Inline checkbox by default. Promote a task to its own file (`01-<slug>.md`, colocated) when it needs more than a line — tasks need no frontmatter or IDs.

6. **Confirm** — print the path and the task list, and ask whether the granularity is right before any implementation starts.

## Template

```markdown
---
title: <short descriptive title>
status: active
created: YYYY-MM-DD
---
# <title>

- [<Label>](<URL>)       # the external ticket, PRs, design refs

## Problem

One paragraph. For an external ticket, restate briefly and link out.

## Approach

The *how*: the seam being tested, implementation and testing decisions,
anything ruled out and why. This is the half of a spec that isn't the issue body.
Draw on decisions already reached earlier in this conversation — e.g. a `/grill-me`
session — not just what's on the ticket.

## Tasks

- [ ] 01 — <vertical slice>
- [ ] 02 — <vertical slice>   (Blocked by: 01)

## Progress
```

## Notes

- **Findings go back to the ticket, not into the plan.** When an investigation confirms something, update the issue — locally via `track set`, externally on the ticket itself. The plan is a working space, not a private record.
- **Never write a local issue or mission id into an external ticket, PR, or repo.** Sending findings out is fine; sending internal identifiers is not.
- Design docs and sketches live in the plan folder and evolve with it. The plan is the living artifact.
- Progress through an issue is progress through its plan; progress through a mission is progress through its issues.
- A plan is roughly one issue in size — around five tasks is typical. Twenty is a sign the work is mission-shaped: file a mission and `/plan M<id>` to cut it into issues.
- Links go under the title as markdown bullets, matching what `track new --link` writes for issues — not in frontmatter.
- `/work` consumes the plan and its tasks. `/issue` and `/mission` create the work items; this creates the plan for one.
- The levels run `/mission` → `/plan M23` (decide, slice into issues) → `/plan 51` (how, for one issue) → `/work 51`.
- **Pull in context already surfaced in this conversation, don't just re-fetch the ticket.** A `/grill-me` session's decisions belong in the Approach section; re-reading the tracker/ticket shouldn't silently drop them. `/grill-me` fits naturally right before this skill when an issue needs implementation decisions worked out before planning (as opposed to before `/issue`, for scope/design decisions).
