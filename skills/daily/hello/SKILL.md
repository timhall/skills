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
- List active missions and issues via the `track` CLI (on PATH; see repo README):
  - `track list -q type=issue -q status=open,investigating --json`
  - `track list -q type=mission -q status=idea,planning,active,blocked --json`
  - Each result carries `stale_days` (days since `last_triaged`, else file mtime). Flag anything with `stale_days >= 2` as stuck.
- Run for each watched repo: `gh pr list --author @me --repo {repo} --json number,title,url,updatedAt,reviewDecision`
- Run for each watched repo: `gh pr list --review-requested @me --repo {repo} --json number,title,url,updatedAt`
- Watched repos: `postman-eng/unified-runtime-monorepo`, `postman-eng/postman-app`
- Search Slack for recent mentions: use `slack_search_public_and_private` with query `to:me after:YYYY-MM-DD` (yesterday's date) to find DMs and @mentions since last workday

### 2. Surface digest

Present a compact summary:
- **Context diff** — items that were in yesterday's Today's 3 and are still open (carried over vs. done)
- Unchecked todos from yesterday (if any, outside Today's 3)
- Stuck missions/issues (not triaged in 2+ days) — labelled ⚠️
- PRs waiting on Tim's review
- Tim's PRs with no activity in 2+ days
- **Slack mentions & DMs** — list each message with channel, sender, and brief summary; flag any that need a reply or action

### 3. Standup prompts (one at a time)

Ask each question, wait for Tim's answer before continuing:

1. "What did you finish yesterday?"
2. "What's your focus today?"

### 4. Triage stuck items

For any item flagged as stuck (2+ days, no triage), ask Tim to choose:
- **Act** — add to Today's 3
- **Defer** — skip today, revisit tomorrow
- **Delegate** — note who to hand off to
- **Drop** — close/archive it

After triage decisions are made, stamp each triaged item with today's date via `track set <issue|mission> <id> last_triaged=YYYY-MM-DD` — don't hand-edit the frontmatter.

### 5. Agree on Today's 3

Based on the standup answers and triage, agree on max 3 focus tasks for today. Push back if Tim proposes more than 3 — WIP cap is intentional.

### 6. Daily Stoic

Ground the day in the Stoic reading — a deliberate, analog beat:

> "Open *The Daily Stoic* to today's entry. What's the quote?"

Wait for Tim to open the book and enter it. Capture the quote **verbatim as Tim types it** — do not paraphrase, summarize, or look the quote up yourself; the point is that Tim reads it. Don't ask for the attribution (TRMNL doesn't show it). If Tim skips it, omit the section from the note.

### 7. Write to today's daily note

Append (or create) `{vault}/Daily Notes/YYYY-MM-DD.md`:

```
## Morning

**Today's 3:**
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

**Standup:**
- Done: {yesterday's done items}

**Triage decisions:**
- {item} → {act/defer/delegate/drop}

**Daily Stoic:**
> {quote}
```

Omit the **Daily Stoic** block if Tim skipped step 6.

The `- [ ]` items at the root level will be picked up by Rollover Daily Todos if unchecked at end of day.

### 8. Push to TRMNL

After the note is written, push Today's 3 to the TRMNL e-ink display:

```bash
python3 ~/dev/timhall/skills/skills/daily/trmnl/push_daily_note.py
```

Non-fatal — it self-skips if the webhook UUID isn't configured (`../trmnl/uuid.txt`). See `../trmnl/README.md` for one-time setup.

### 9. Optional Slack draft

Ask: "Anything worth a Slack update today?"

If yes, draft together using this format:
```
• {what moved / what was done} → {link to PR/doc/artifact}
• {what's next}
• {any decisions or asks}
```

Venue: project channel for major updates, DM to manager for smaller items. Tim posts via Slack MCP — never post autonomously.
