# Tracker

Personal work tracking — markdown in the notes vault, queried through one CLI. This folder holds everything for the tracker in one place: the `/issue`, `/mission`, and `/plan` skills, the `track` CLI, and this contract doc.

> This file is the canonical tracker contract. `~/.claude/agents/issue-tracker.md` symlinks here, so it doubles as the global agent doc. If a repo has its own `docs/agents/issue-tracker.md`, that takes precedence.

## Model

Four types, two of them optional:

| Type | Is | Relationship |
|---|---|---|
| **Issue** | something to be done | — |
| **Mission** | a set of things to be done | `Mission = Issue[]` |
| **Task** | how something is to be done | — |
| **Plan** | a set of tasks | `Plan = Task[]` |

Work happens at **issue** and **task** level. Mission and plan are the bigger picture and are optional — most issues have no mission, and plenty need no plan.

**The independence test** separates issue from task. It is a difference of kind, not size:

- An **issue can live independently.** It is closable on its own and still makes sense with its parent deleted.
- A **task only exists inside its plan.** Delete the plan and the task is meaningless.

**A mission is not a topic label.** It is a set of issues delivering *one* outcome. Grouping issues because their titles share a word buys no sequencing and no shared definition of done — that is a folder, not a mission.

**Progress composes upward.** Progress through a mission is progress through its issues; progress through an issue is progress through its plan. Issues without a plan are simply binary.

**Sizing.** A plan is roughly one issue in size — around five tasks is typical. Twenty tasks means the work is mission-shaped and wants splitting into issues.

## Structure

- Missions: `{vault}/Missions/NNNN-<slug>.md`
- Issues: `{vault}/Issues/NNNN-<slug>.md`
- Plans: `{vault}/Plans/<key>/plan.md`, with tasks and design docs colocated

The vault defaults to `~/Documents/notes`; `$NOTES_VAULT` overrides it. IDs are plain integers with **no leading zeros** (YAML parses `0042` as octal); filenames zero-pad to 4 digits (`0042-slug.md`) for ordering only. Resolution keys on the numeric prefix — the slug is decoration and may drift.

A plan's `<key>` names its owner, and the folder name **is** the link. There is no `plans:` pointer field:

| Key | Means |
|---|---|
| `0050-relax-platform-type-only-deps` | local issue 50 |
| `M0023-agent-efficiency` | local mission 23 |
| `APICLIENT-4053` | external ticket, verbatim |

Issue and mission IDs are separate sequences, so a bare number would be ambiguous — **missions take an `M` prefix, issues stay bare**. `M0004` is mission 4; `0004` is issue 4. An external ticket uses its own key verbatim, already namespaced by its project prefix.

Missions usually hold a plan, and it is a different artifact from an issue's. A **mission plan decides and cuts**: it settles the open questions, records what was deferred, and carries the ordered issue set with its blockers. An **issue plan says how**: tasks. `/plan M23` writes the first, `/plan 50` the second — see `plan/mission-plan.md`.

## Edges

- **`mission:` on an issue is the canonical membership edge.** Missions may mention their issues in prose, but that prose is descriptive — `mission:` is what `track` reads.
- **A mission plan's `## Issues` list is not a duplicate of that edge.** It holds the order, the blockers, and whether a slice needs you in the loop — none of which fit in frontmatter. Membership is queried with `track list -q mission=<id>`; sequencing is read from the plan.
- **Plans carry no pointer.** Convention over field: the folder name resolves both directions, and a convention cannot be left unset. Two pointer fields have already failed here by non-population.
- **`jira:` / `pr:` on an issue** point outward at the org's record.

## Plans and tasks

- **Tasks are flexible.** No IDs, no frontmatter. Attached to their plan by colocation or by being listed in it.
- **Inline checkbox by default**; promote a task to its own file (`01-<slug>.md`) only when it needs more than a line.
- Tasks are **vertical slices** — each cuts a complete path through the layers, is independently verifiable, and fits one fresh context window. Order them; declare `Blocked by` only where the order is not a straight line.
- **Design docs live in the plan folder** and evolve with it. The plan is the living artifact — it is where the work happens.
- **Findings go to the issue, not the plan.** When an investigation confirms something, update the issue (`track set`, or the external ticket). The plan is a working space, not the record.

## External tickets

Work that originates in Jira or GitHub stays there. Do **not** mirror it into a local issue.

- `/plan APICLIENT-4053` creates `Plans/APICLIENT-4053/plan.md`. The ticket remains the source of truth for *what*; the plan holds only *how*.
- **Push content, never identifiers.** Sending findings back to a ticket is expected. Writing a local issue or mission id into any external ticket, PR, or repo is not — see the "never leak internal trackers" rule in `~/.claude/CLAUDE.md`.

## Query — the `track` CLI

`track` is the single front door for *reading*. Skills and agents call it instead of re-deriving filesystem globs or hand-parsing frontmatter. The markdown files remain the source of truth.

```bash
track list [-q key=val[,val2] ...] [--json]   # list, optionally filtered
track get  <issue|mission> <id> [--json]       # print one item's file
track path <issue|mission> <id>                # print one item's path
track get  plan <key> [--json]                 # a plan, by key or owner id
track path plan <key>                          # e.g. 50, M23, APICLIENT-4062
```

Filters are `-q key=value`, repeatable. Multiple `-q` flags **AND** together; commas within one value **OR** together.

| filter | meaning |
|--------|---------|
| `type=issue` / `type=mission` / `type=plan` | restrict to one kind (default: all) |
| `status=open,investigating` | match any of the listed statuses |
| `stale=N` | items untouched ≥ N days (by `last_triaged`, else file mtime) |
| `<any frontmatter key>=…` | match a frontmatter field, e.g. `source=slack`, `mission=20` |

String matches are case-insensitive; a list-valued field (e.g. `tags`) matches if any entry matches. `list --json` and `get --json` emit structured output for agents (`get --json` splits `frontmatter` and `body`).

```bash
track list -q type=issue -q status=open,investigating
track list -q mission=20                       # a mission's issue set
track list -q type=plan                        # plans, with done/total tasks
```

Plans are a first-class source alongside `Issues/` and `Missions/`. A plan is
`Plans/<key>/plan.md`; the folder name resolves its owner, and `list --json`
carries `key`, `owner` and a `tasks: {done, total}` count read from the plan's
checkboxes. Folders holding only design docs are reference material, not plans,
and are not listed.

The CLI lives at `skills/tracker/track`; the repo's `bin/track` symlinks to it, so adding `bin/` to PATH exposes `track` everywhere. (`bin/` is a PATH change — put it in `.zshrc`/`.zprofile`, after `path_helper`.)

## Create and update

`track new` and `track set` own the on-disk format — the ID scheme, filename padding, frontmatter schema, and body scaffold live in code, not in prose.

```bash
track new issue   "<title>" [--slug S] [--source S] [--link "Label|URL"] [--description TEXT] [--mission N]
track new mission "<title>" [--slug S] [--link "Label|URL"] [--problem TEXT] [--goal TEXT]
track set <issue|mission> <id> key=value ...   # e.g. status=resolved, mission=20
```

`--link` writes markdown bullets **under the title**, not frontmatter. Plans follow the same convention. `--mission` takes `23` or `M23`, checks the mission exists, and refuses to file a dangling edge — it is how a mission's slices get created.

The **`/issue`**, **`/mission`**, and **`/plan`** skills are thin wrappers: the agent supplies judgment, the CLI owns the format. Nothing hand-edits frontmatter.

**Do not bulk-stamp `last_triaged`.** Stamp only items that actually received a decision, or the field stops carrying information — a uniform date across the backlog reads as 70 triage events when it was one.

## Not yet implemented

The model above is the target. These gaps are real as of 2026-08-31:

- **`Plans/0004-runtime-timings-reuse-brief.md`** is a bare file rather than `<key>/plan.md`, so `track` does not see it. Legacy shape, left alone.
- **`/hello` and `/goodbye` do not read plan-level state yet**, so task progress does not show up in the morning digest.

## Fetch a specific item

When a skill says "fetch the relevant ticket": given an ID, use `track path <type> <id>` or `track get <type> <id>`. Otherwise read the file at the path the user passes directly.
