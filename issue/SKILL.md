---
name: issue
description: Create a new issue in {notes vault}/issues/. Use when user reports a bug, investigation, or small self-contained work item — including when they say "/bug". Accepts a plain description and optional links.
---

Read the **Notes vault** path from the `## Agent skills` section of CLAUDE.md — use it wherever `{notes vault}` appears below.

Create a new issue file in `{notes vault}/issues/`.

## Steps

1. **Determine the next ID** — count the existing `.md` files in `{notes vault}/issues/` and add 1. Zero-pad to 4 digits (e.g. `0001`, `0042`).

2. **Infer from the description:**
   - `title` — a short human-readable title (also used for the filename slug, lowercase hyphenated)
   - `source` — detect from context:
     - Slack URL or mention → `slack`
     - Email mention → `email`
     - User report / customer → `user-report`
     - JIRA mention → `jira`
     - Otherwise → `self`
   - Any URLs mentioned → collect as links to place inline under the title

3. **Create the file** at `{notes vault}/issues/NNNN-slug.md`:

```markdown
---
id: NNNN
title: "Human readable title"
status: open
source: slack
created: YYYY-MM-DD
closed:
pr:
jira:
tags: []
---
# Human Readable Title

- [Slack thread](url) (omit links section entirely if none)

## Description

The description as provided, cleaned up for clarity. Do not add "Reported via Slack" or similar — source and links already convey that.

## Investigation


## Resolution

```

4. **Confirm** — tell the user the file path and ID. Ask if anything needs correcting.

## Notes

- Use today's date for `created`
- Leave `closed`, `pr`, `jira` blank
- If the description is sparse, use it as-is in `## Description` — don't invent details
- If links are present, format them as markdown inline under the title
- `/bug` is an alias for this skill
