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

## Skills

### `/issue`

Create a new issue in `{notes vault}/issues/`. For bugs, investigations, and small self-contained work items.

```
/issue Flicker when switching from Hex to Preview tab https://slack.com/...
```

### `/mission`

Create a new mission in `{notes vault}/missions/`. For idea-to-delivery work items spanning design, planning, and implementation.

```
/mission Extract @postman/runtime.platform into its own package
```

### `/work`

Step through a mission's plan slices with managed context and worktree isolation. Reads the mission's `plans/` folder, identifies the next slice, and opens a worktree to work in.

```
/work 4
```
