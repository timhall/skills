---
name: mission
description: Create a new mission in {notes vault}/missions/. Use when user wants to track an idea-to-delivery work item — a larger effort spanning design, planning, and implementation. Accepts a plain description and optional links.
---

Read the **Notes vault** path from the `## Agent skills` section of CLAUDE.md — use it wherever `{notes vault}` appears below.

Create a new mission file in `{notes vault}/missions/`.

## Steps

1. **Determine the next ID** — count the existing `.md` files in `{notes vault}/missions/` and add 1. Zero-pad to 4 digits (e.g. `0001`, `0042`).

2. **Infer from the description:**
   - `title` — a short human-readable title (also used for the filename slug, lowercase hyphenated)
   - Any URLs or file references mentioned → collect as links to place inline under the title

3. **Create the file** at `{notes vault}/missions/NNNN-slug.md`:

```markdown
---
id: NNNN
title: "Human readable title"
status: idea
created: YYYY-MM-DD
plans:
jira:
tags: []
---
# Human Readable Title

- [link](url) (omit links section entirely if none)

## Problem

What is broken, missing, or worth improving? One paragraph.

## Goal

What does done look like?

## Progress


## Resolution

```

4. **Confirm** — tell the user the file path and ID. Ask if anything needs correcting.

## Notes

- Use today's date for `created`
- `status` starts as `idea` — the user will move it to `planning`, `active`, `blocked`, or `done` as work progresses
- Leave `plans` and `jira` blank — `plans` is filled in manually when a plans/ folder is created
- If the description already contains a clear problem statement and goal, use that language directly
- Keep `## Problem` and `## Goal` concise — the heavy detail belongs in `plans/`
