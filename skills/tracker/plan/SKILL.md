---
name: plan
description: Create or open a plan for a piece of work in {notes vault}/Plans/. Use when an issue needs a plan of tasks before implementation, or when the user says "/plan <id>" — accepts a local issue id (`/plan 50`) or an external ticket key (`/plan APICLIENT-4053`).
---

Read the **Notes vault** path from the `## Agent skills` section of CLAUDE.md — use it wherever `{notes vault}` appears below.

A **plan** says *how* a piece of work gets done. It lives at `{notes vault}/Plans/<key>/plan.md`, alongside its tasks and any design docs.

The folder name *is* the link to the work — there is no pointer field. Key by the owner:

| Argument | Key | Means |
|---|---|---|
| `50` | `0050-<slug>` | local issue 50 |
| `APICLIENT-4053` | `APICLIENT-4053` | external ticket, verbatim |

Bare 4-digit prefix = local issue; `M`-prefixed = local mission (rare — a mission's plan is normally its issue set); anything else is an external ticket key, used verbatim.

## Steps

1. **Resolve the target.**
   - **Local** (bare integer) — `track path issue <id>`. Read it for the problem and any prior investigation.
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
- A plan is roughly one issue in size — around five tasks is typical. Twenty is a sign the work is mission-shaped and wants splitting into issues.
- Links go under the title as markdown bullets, matching what `track new --link` writes for issues — not in frontmatter.
- `/work` consumes the plan and its tasks. `/issue` and `/mission` create the work items; this creates the plan for one.
