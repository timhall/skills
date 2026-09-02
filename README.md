# timhall/skills

Personal agent skills for Claude Code and other AI agents.

## Install

```bash
npx skills add timhall/skills
```

Or from a local clone:

```bash
npx skills add ~/dev/timhall/skills
```

If you're actively developing skills in this repo rather than just using them, skip `npx skills add` on your own clone. It materializes copies that drift from source, and with a broad agent scope it can litter your home directory with per-tool directories for agents you don't use. Symlink each skill directly instead:

```bash
ln -s ~/dev/timhall/skills/goodbye ~/.claude/skills/goodbye
```

No cache, no lockfile, no staleness.

## Setup

After installing, seed your global instructions. On a new machine, copy the sections from [`system-instructions.md`](system-instructions.md) into `~/.claude/CLAUDE.md` and fill in the machine-specific paths. At minimum you need an `# Agent skills` section — the skills read it at runtime, so changing a path once there updates all of them:

```markdown
# Agent skills

- **Notes vault**: `~/Documents/notes`
```

To use the `track` CLI, add `bin/` to your PATH (it's a PATH change, so put it in `.zshrc`/`.zprofile`, after macOS `path_helper`):

```bash
export PATH="$HOME/dev/timhall/skills/bin:$PATH"
```

`write-like-tim` pairs with [`simple-english`](https://github.com/AminBlg/SimpleEnglish), a separate skill not in this repo. It's optional — `write-like-tim` skips that pass if it's not installed — but to get it:

```bash
npx skills add AminBlg/SimpleEnglish
```

## Settings

Claude Code merges permission and config settings from several files. Precedence, highest to lowest:

1. `<project>/.claude/settings.local.json` — personal, per-project. Gitignored. "Always allow" clicks made inside a project land here.
2. `<project>/.claude/settings.json` — per-project, committed and shared with a team.
3. `~/.claude/settings.local.json` — personal, applies everywhere, not shared. "Always allow" clicks made outside any project land here.
4. `~/.claude/settings.json` — global baseline. Portable (sync via dotfiles); the durable curated list.

Rule of thumb: **`settings.json` = deliberate and durable; `settings.local.json` = machine-local scratch that fills up automatically.** Keep the curated allowlist (build tools, read-only MCP tools, trusted `WebFetch` domains) in `settings.json`; let the `.local.json` files collect one-offs, and prune them periodically — mis-parsed grants like `Bash(done)` or literal file paths accumulate there.

Where a given grant belongs:

- Cross-project and stable, approved constantly → `~/.claude/settings.json`
- Needed by only one repo → that repo's `.claude/settings.local.json`
- Shared with a team for one repo → that repo's committed `.claude/settings.json`

Permission pattern forms: `Bash(cmd:*)` (prefix — any args), `Bash(cmd)` (exact), `WebFetch(domain:example.com)`, or a full MCP tool name like `mcp__server__tool`. Never blanket-allow arbitrary code execution (`Bash(node:*)`, `Bash(python3:*)`, sandbox `exec`, etc.) — grant the narrow read-only subcommands instead.

The same global-vs-local split applies to instructions: durable personal preferences go in `~/.claude/CLAUDE.md` (seed it from [`system-instructions.md`](system-instructions.md)); per-repo guidance goes in that repo's `CLAUDE.md` or `AGENTS.md`, kept short and linking out to detail rather than inlining it.

## Skills

### Tracker — `/issue`, `/mission`, `/plan`, and the `track` CLI

Everything for personal work tracking lives in `skills/tracker/` — the create skills, the `track` query CLI, and the contract doc. The contract defines the model (issue, mission, task, plan) and is the thing to read first. See [`skills/tracker/README.md`](skills/tracker/README.md) for the full reference.

- **`/issue`** — create a new issue in `{notes vault}/Issues/` (bugs, investigations, small items).
- **`/mission`** — create a new mission in `{notes vault}/Missions/` (idea-to-delivery efforts).
- **`/plan`** — create a plan of tasks for one issue in `{notes vault}/Plans/`, keyed to a local issue (`/plan 50`) or an external ticket (`/plan APICLIENT-4053`).
- **`track`** — read/query issues and missions instead of re-deriving globs: `track list -q status=open --json`, `track get mission 4`, `track path issue 18`.

```
/issue Flicker when switching from Hex to Preview tab https://slack.com/...
/mission Extract @postman/runtime.platform into its own package
/plan APICLIENT-4053
```

### `/work`

Step through a plan's tasks with managed context and worktree isolation. Takes an issue id (`/work 50`), a mission id (`/work M20`), or an external ticket key (`/work APICLIENT-4062`); resolves the plan by folder convention, picks the next unblocked task, and opens a worktree to work in.

```
/work 4
```

### `/hello`

Morning triage ritual. Reads yesterday's daily note, open missions/issues, and GitHub PRs, then runs standup-style prompts, surfaces stuck items, and produces "Today's 3" written to the daily note. Optionally drafts a Slack update.

```
/hello
```

### `/goodbye`

End-of-day shutdown ritual. Captures what got done, surfaces open loops, flags carry-overs, and writes a close-of-day summary to the daily note. Optionally drafts a Slack update.

```
/goodbye
```

### `code-like-tim` and `write-like-tim`

The case law behind `~/.claude/CLAUDE.md`'s comment and Length rules. `code-like-tim` decides whether a comment earns its place; `write-like-tim` decides how any prose — chat, PR/issue bodies, commit messages, or a comment once `code-like-tim` has cleared it — gets trimmed once it does. Invoke explicitly during a comment, writing, or review pass; neither triggers on its own.

### Pair programming — `/driver` and `/navigator`

Pairing styles live in `skills/pair-programming/`, one skill per style. The command names the role *the agent* takes. See [`skills/pair-programming/README.md`](skills/pair-programming/README.md) for the full taxonomy and the unbuilt slots (tour guide, ping pong).

- **`/driver`** — the agent drives, you navigate. It writes at a deliberate pace, surfacing names and forks as it goes, and never loops autonomously. (Formerly `/slow-mode`, recalibrated: the original was written for learners, so the ask-permission rules became surface-the-decision rules.)
- **`/navigator`** — you drive, the agent navigates. You write the code; it re-reads what landed, spots defects, holds the codebase map, prods edge cases, and offers the surrounding work. One keyboard team: it doesn't edit unless you hand it over.

```
/driver
/navigator
```
