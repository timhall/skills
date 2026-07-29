# system-instructions.md

A seed for `~/.claude/CLAUDE.md` — the personal, global instructions Claude Code loads into **every** session. Copy the sections below into that file on a new machine, then fill in the machine-specific vault path.

Keep it lean. This file is always in context, so it should hold durable *preferences* and *gotchas* — not documentation Claude can discover by looking. Detailed procedures belong in skills (this repo), which load on demand. Prefer principles over rigid rules; newer models need fewer guardrails to do the right thing.

Placeholders are written as `{like-this}` — replace them.

---

# Agent skills

- **Notes vault**: `{~/Documents/notes}`
- **Issue tracker**: local markdown — see the tracker skill (`skills/tracker/README.md` in `timhall/skills`).

The skills read this section at runtime — change a path once here and every skill picks it up.

# Work Tracker

I track work items as markdown in my notes vault: `Issues/` (bugs/investigations, status open → investigating → resolved → closed) and `Missions/` (idea-to-delivery work, status idea → planning → active → blocked → done). Full contract in the tracker skill doc.

Read them through the `track` CLI (on PATH) — never glob the vault by hand:

- Status summary / standup / "what am I working on": `track list -q status=open,investigating,idea,planning,active,blocked --json`, then summarize (this omits finished items).
- A specific item: `track get <issue|mission> <id>` or `track path <issue|mission> <id>`.

# Code contributions

These apply to any code, comment, test, commit message, or PR I produce in any project.

## Never leak internal context

Never reference internal trackers in anything that reaches a repo or GitHub — issue/mission IDs, internal review labels, or slugs from my notes vault. Explain what the code does and why in terms a public reader understands, with no pointer to an internal artifact. If a comment only makes sense given an internal ticket, rewrite it to stand alone or delete it. (Ticket keys that are the repo's own convention — e.g. a `[PROJ-000]` commit prefix — are fine.)

## Comments: necessary and brief

Default to no comment. Add one only when the code can't be made self-explanatory and a reader would otherwise be misled or waste time. One or two lines max — state the non-obvious constraint, not the narrative. Rationale and history go in the PR body or the ticket, not the diff.

Write code that reads like the surrounding code — match its naming, idiom, and comment density. Full case law in the code-like-tim skill.
