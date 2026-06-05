---
name: goodbye
description: Shutdown ritual skill that bookends the workday. Runs a Newport-style end-of-day conversation to capture what got done, surface open loops, flag carry-overs, and write a close-of-day summary to today's daily note. Optionally drafts a Slack update. Use when user invokes /goodbye or wants to close out their workday.
---

# /goodbye — Shutdown Ritual

## Setup

Notes vault: `~/Documents/notes` (override from CLAUDE.md if different)

- Daily notes: `{vault}/Daily Notes/YYYY-MM-DD.md`
- Missions: `{vault}/missions/*.md`
- Issues: `{vault}/issues/*.md`

## Flow

Run these steps in order. Ask one question at a time — this is a conversation, not a dump.

### 1. Gather context (silently)

- Read today's daily note — check Today's 3 completion, any morning triage decisions
- Note any unchecked `- [ ]` items (Rollover Daily Todos will carry these forward automatically)

### 2. Shutdown prompts (one at a time)

Ask each question, wait for Tim's answer before continuing:

1. "What did you get done today?"
2. "What's still open or carrying over to tomorrow?"
3. "Anything loose in Slack or your head that isn't captured yet?"
4. "Anything that needs to be first thing tomorrow?"

### 3. Capture loose items

For anything uncaptured from Slack or Tim's head:
- Small self-contained item → offer to create an issue (`/issue`)
- Larger effort → offer to add to an open mission's Progress section
- Quick note → add inline to today's daily note

### 4. Write close-of-day summary

Append to today's `{vault}/Daily Notes/YYYY-MM-DD.md`:

```
## Evening

**Done today:**
- {item}

**Carry-overs:**
- [ ] {item} ← these will roll over via Rollover Daily Todos

**Open loops captured:**
- {item} → {issue/mission reference or note}

**First thing tomorrow:**
- {item}
```

### 5. Optional Slack draft

If anything significant was completed, ask: "Worth a Slack update?"

If yes, draft together using this format:
```
• {what moved / what was done} → {link to PR/doc/artifact}
• {what's next}
• {any blockers or decisions needed}
```

Venue: project channel for major updates, DM to manager for smaller items. Tim posts via Slack MCP — never post autonomously.

### 6. Close out

End with a clear signal that work is done. Everything unfinished is captured; nothing is left as a mental open loop.
