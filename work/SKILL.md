---
name: work
description: Step through a mission's plan slices with managed context and worktree isolation. Use when user wants to start or continue working on a mission slice. Accepts a mission ID (e.g. `/work 4`) or mission title.
---

Read the **Notes vault** path from the `## Agent skills` section of CLAUDE.md — use it wherever `{notes vault}` appears below.

Set up context and a worktree to work on the next slice of a mission.

## Steps

### 1. Load the mission

Resolve the mission file: for a numeric ID, `track path mission <id>` gives the path directly (or `track get mission <id>` to read it); for a title, find the matching `{notes vault}/Missions/NNNN-*.md`. Read it to get:
- `plans:` — path to the plans folder (relative to `{notes vault}/`)
- `## Progress` — what has already been completed

### 2. Identify the slices

Read the plans folder. Slices are numbered markdown files (e.g. `wire-01-*.md`, `01-*.md`). Read each slice filename and, if needed, its first heading to build an ordered list.

Cross-reference with `## Progress` in the mission file to determine which slice is next.

If no slices exist — only a PRD or unstructured plan docs — tell the user and suggest running `/to-issues` to break the plan into slices first.

### 3. Read the delivery mode

Look for a `delivery:` field anywhere in the plan docs (PRD or slice files):

```
delivery: per-slice    # default — new worktree per slice
delivery: single-pr    # one worktree for the whole mission
```

Default to `per-slice` if not found.

### 4. Present the plan and confirm

Show the user:
- The mission title
- The completed slices (from Progress)
- The **next slice** (title + brief summary)
- Any remaining slices after that

Ask: "Ready to start [slice name]?" before proceeding.

### 5. Create or reuse the worktree

**`per-slice`:** Create a new worktree with branch name `mission-N/slice-slug` (e.g. `mission-4/wire-02-snapshot-http-fidelity`).

**`single-pr`:** Use branch name `mission-N` (e.g. `mission-4`). If a worktree for this mission already exists, note that the user should resume it rather than creating a new one. If it doesn't exist, create it.

Use the EnterWorktree tool to create the worktree in the current working directory.

### 6. Load context

Read the full slice document and present a concise brief:
- What this slice builds
- Acceptance criteria or definition of done
- Any explicit blockers or dependencies noted in the doc

### 7. Work

Assist with implementing the slice. Stay focused on the slice's scope — flag anything that looks out of scope and ask before expanding.

### 8. On completion

When the slice is done and a PR is up:

1. Update `## Progress` in the mission file — add a line for the completed slice with the PR link if available
2. Update the mission `status` if appropriate (e.g. `done` if all slices complete)
3. Tell the user the next slice and suggest running `/work N` again to continue

## Notes

- Always confirm before creating a worktree — state the branch name so the user knows what will be created
- If the user invokes `/work N` mid-slice (resuming), skip worktree creation and just reload context from the slice doc
- The plans folder path in the mission is relative to `{notes vault}/` — resolve it accordingly
- If `plans:` is blank in the mission, ask the user to point you at the plan before proceeding
