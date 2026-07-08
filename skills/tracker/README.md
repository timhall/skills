# Tracker

Personal work tracking — issues and missions stored as markdown in the notes vault. This folder holds everything for the tracker in one place: the `/issue` and `/mission` skills, the `track` query CLI, and this contract doc.

> This file is the canonical tracker contract. `~/.claude/agents/issue-tracker.md` symlinks here, so it doubles as the global agent doc. If a repo has its own `docs/agents/issue-tracker.md`, that takes precedence.

## Structure

- Missions (idea-to-delivery): `{vault}/Missions/NNNN-<slug>.md`
- Issues (bugs, small self-contained items): `{vault}/Issues/NNNN-<slug>.md`
- Plans / PRDs: `{vault}/Plans/<mission-slug>/`

The vault defaults to `~/Documents/notes`; `$NOTES_VAULT` overrides it. IDs are plain integers with **no leading zeros** (YAML parses `0042` as octal); filenames zero-pad to 4 digits (`0042-slug.md`) for ordering only.

## Query — the `track` CLI

`track` is the single front door for *reading* issues and missions. Skills and agents call it instead of re-deriving filesystem globs or hand-parsing frontmatter. It only reads — the markdown files remain the source of truth.

```bash
track list [-q key=val[,val2] ...] [--json]   # list, optionally filtered
track get  <issue|mission> <id> [--json]       # print one item's file
track path <issue|mission> <id>                # print one item's path
```

Filters are `-q key=value`, repeatable. Multiple `-q` flags **AND** together; commas within one value **OR** together.

| filter | meaning |
|--------|---------|
| `type=issue` / `type=mission` | restrict to one kind (default: both) |
| `status=open,investigating` | match any of the listed statuses |
| `stale=N` | items untouched ≥ N days (by `last_triaged`, else file mtime) |
| `<any frontmatter key>=…` | match a frontmatter field, e.g. `source=slack`, `tags=infra` |

String matches are case-insensitive; a list-valued field (e.g. `tags`) matches if any entry matches. `list --json` and `get --json` emit structured output for agents (`get --json` splits `frontmatter` and `body`).

```bash
track list -q type=issue -q status=open,investigating
track list -q stale=2 --json
```

The CLI lives at `skills/tracker/track`; the repo's `bin/track` symlinks to it, so adding `bin/` to PATH exposes `track` everywhere. (`bin/` is a PATH change — put it in `.zshrc`/`.zprofile`, after `path_helper`.)

## Create — the skills

- **`/issue`** — new issue in `{vault}/Issues/` with the next sequential ID.
- **`/mission`** — new mission in `{vault}/Missions/` with the next sequential ID.

These own the create-time format (frontmatter schema, ID scheme). Until `track new`/`track set` exist, creation and status edits go through the skills, not the CLI.

## Fetch a specific item

When a skill says "fetch the relevant ticket": given an ID, use `track path <type> <id>` or `track get <type> <id>`. Otherwise read the file at the path the user passes directly.
