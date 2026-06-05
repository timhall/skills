---
name: hello
description: Morning triage skill that bookends the workday. Reads yesterday's Obsidian daily note, open missions/issues, and GitHub PRs, then runs a standup-style conversation to surface stuck items, produce "Today's 3" written to today's daily note, and optionally draft a Slack update. Use when user invokes /hello or wants to start their workday with a triage ritual.
---

# /hello — Morning Triage

## Setup

Notes vault: `~/Documents/notes` (override from CLAUDE.md if different)

- Daily notes: `{vault}/Daily Notes/YYYY-MM-DD.md`
- Missions: `{vault}/missions/*.md` (skip status: done)
- Issues: `{vault}/issues/*.md` (skip status: closed, resolved)

## Flow

Run these steps in order. Ask one question at a time — this is a conversation, not a dump.

### 1. Gather context (silently)

- Read yesterday's daily note — note unchecked `- [ ]` items and the **Today's 3** section if present
- Read all open missions and issues (frontmatter `status` field)
  - Staleness: use `last_triaged` frontmatter if present, otherwise fall back to file mtime
  - Flag anything not triaged in 2+ days
- Run for each watched repo: `gh pr list --author @me --repo {repo} --json number,title,url,updatedAt,reviewDecision`
- Run for each watched repo: `gh pr list --review-requested @me --repo {repo} --json number,title,url,updatedAt`
- Watched repos: `postman-eng/unified-runtime-monorepo`, `postman-eng/postman-app`

### 2. Surface digest

Present a compact summary:
- **Context diff** — items that were in yesterday's Today's 3 and are still open (carried over vs. done)
- Unchecked todos from yesterday (if any, outside Today's 3)
- Stuck missions/issues (not triaged in 2+ days) — labelled ⚠️
- PRs waiting on Tim's review
- Tim's PRs with no activity in 2+ days

### 3. Standup prompts (one at a time)

Ask each question, wait for Tim's answer before continuing:

1. "What did you finish yesterday?"
2. "What's your focus today?"
3. "Anything blocking you?"

### 4. Triage stuck items

For any item flagged as stuck (2+ days, no triage), ask Tim to choose:
- **Act** — add to Today's 3
- **Defer** — skip today, revisit tomorrow
- **Delegate** — note who to hand off to
- **Drop** — close/archive it

After triage decisions are made, stamp `last_triaged: YYYY-MM-DD` in the frontmatter of each triaged mission/issue file. Use `sed` or Edit to update the existing frontmatter block — add the field after `status:` if not present, update it if it is.

### 5. Agree on Today's 3

Based on the standup answers and triage, agree on max 3 focus tasks for today. Push back if Tim proposes more than 3 — WIP cap is intentional.

### 6. Write to today's daily note

Append (or create) `{vault}/Daily Notes/YYYY-MM-DD.md`:

```
## Morning

**Today's 3:**
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

**Standup:**
- Done: {yesterday's done items}
- Blocked: {any blockers}

**Triage decisions:**
- {item} → {act/defer/delegate/drop}
```

The `- [ ]` items at the root level will be picked up by Rollover Daily Todos if unchecked at end of day.

### 7. Optional Slack draft

Ask: "Anything worth a Slack update today?"

If yes, draft together using this format:
```
• {what moved / what was done} → {link to PR/doc/artifact}
• {what's next}
• {any blockers or decisions needed}
```

Venue: project channel for major updates, DM to manager for smaller items. Tim posts via Slack MCP — never post autonomously.
