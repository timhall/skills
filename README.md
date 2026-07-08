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

## Setup

After installing, add an `## Agent skills` section to `~/.claude/CLAUDE.md`:

```markdown
## Agent skills

- **Notes vault**: `~/Documents/notes`
```

The skills read this at runtime — change it once and all skills pick it up.

To use the `track` CLI, add `bin/` to your PATH (it's a PATH change, so put it in `.zshrc`/`.zprofile`, after macOS `path_helper`):

```bash
export PATH="$HOME/dev/timhall/skills/bin:$PATH"
```

## Skills

### Tracker — `/issue`, `/mission`, and the `track` CLI

Everything for personal work tracking lives in `skills/tracker/` — the two create skills, the `track` query CLI, and the contract doc. See [`skills/tracker/README.md`](skills/tracker/README.md) for the full reference.

- **`/issue`** — create a new issue in `{notes vault}/Issues/` (bugs, investigations, small items).
- **`/mission`** — create a new mission in `{notes vault}/Missions/` (idea-to-delivery efforts).
- **`track`** — read/query issues and missions instead of re-deriving globs: `track list -q status=open --json`, `track get mission 4`, `track path issue 18`.

```
/issue Flicker when switching from Hex to Preview tab https://slack.com/...
/mission Extract @postman/runtime.platform into its own package
```

### `/work`

Step through a mission's plan slices with managed context and worktree isolation. Reads the mission's `plans/` folder, identifies the next slice, and opens a worktree to work in.

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
