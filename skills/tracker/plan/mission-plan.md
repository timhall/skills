# Planning a mission

Read this when `/plan`'s target resolves to a **mission** (`M23`). For an issue or
an external ticket, stay in `SKILL.md`.

A mission plan is not a bigger issue plan. Its output is **decisions plus an
ordered issue set** — the mission's "tasks" are issues, and they leave the plan
to live on their own. It lives at `{notes vault}/Plans/M<NNNN>-<slug>/plan.md`.

The plan holds what frontmatter cannot: the order, the blockers, and why the cut
falls where it does. The `mission:` field on each issue stays the canonical
membership edge — `track list -q mission=23` is the query, this list is the
sequencing.

## Steps

1. **Read the mission** — `track get mission <id>` for its problem and goal.

2. **Take stock before cutting.**
   - `track list -q mission=<id>` — issues already attached. Some slices may exist.
   - `track list -q status=open,investigating` — an open issue may belong to this
     mission. Adopt it (`track set issue <n> mission=<id>`) rather than filing a
     near-duplicate.
   - `Plans/M<NNNN>-*/` — if a plan exists, continue it rather than starting over.

3. **Explore the code.** The cut has to fall on real seams, so find them first.
   Name the repo and the seams in `## Decisions`.

4. **Settle the open questions.** This is the bulk of the work and the reason the
   plan exists. Record each decision with its reasoning, and record what you
   deferred — a mission plan that loses its deferrals invites re-litigating them.

5. **Propose the cut. Do not create issues yet.** Show the numbered list and get
   sign-off on the boundaries. Issue files are tedious to unpick, and the cut is
   exactly the thing worth arguing about.

6. **Create the approved slices**, one call each:

   ```bash
   track new issue "<title>" --mission <id> --description "<the slice>"
   ```

   Then write the returned ids back into `## Issues` as wikilinks
   (`[[0051-walking-skeleton]]`).

7. **Confirm** — print the plan path and the issue set, and say that
   `/plan <first-issue-id>` plans the first slice.

## Making the cut

**The independence test decides what is an issue.** A slice that is closable on
its own, and still makes sense with the mission deleted, is an issue. Anything
that evaporates without its parent is a task — it belongs in an issue's plan, not
here.

**Cut by deliverable, never by layer.** "Backend slice, then frontend slice" is
not two issues: the first delivers nothing usable and neither closes alone. Each
slice cuts through the layers.

**Tracer bullet first.** Slice 1 is a walking skeleton — the narrowest end-to-end
path that works. The rest fan out from it. This is what makes the later slices
independent, because they each extend a spine that already exists.

**Prefer fan-out to chains.** After the skeleton, slices should mostly run in
parallel. A straight chain of six is a task list wearing issue clothes; look for
a different cut.

**Size each slice at roughly one plan** — about five tasks. Twenty means the slice
is mission-shaped. One line means it is a task; fold it into a neighbor.

**Three to six slices.** Past eight, either the cut is too fine or the mission is
two missions.

**A small mission need not be sliced at all.** If the whole thing is under one
issue's worth, say so and write ordinary tasks under `## Tasks` instead — the
issue-plan template in `SKILL.md` applies.

## Template

```markdown
---
title: <short descriptive title>
status: active
created: YYYY-MM-DD
---
# <title>

- [<Label>](<URL>)       # design refs, tickets, prior art

## Goal

What done looks like for the whole mission. A paragraph.

## Decisions

Each settled question with its reasoning, and the seams the cut lands on.
Sub-head per question. This is the half of the mission that isn't the issue set.

## Issues

1. [[NNNN-slug]] — <what it delivers> · **HITL** · no blockers
2. [[NNNN-slug]] — <what it delivers> · AFK · blocked by NNNN

A line on the shape: what fans out from what, and what can run in parallel.

## Deferred

Out of scope, with the reason. Keep these — they are what stops the mission
re-litigating its own boundaries.

## Acceptance

The demo that proves the mission landed.
```

Tag each slice **HITL** when it needs you in the loop, **AFK** when it can run
unattended. That split is what makes the set schedulable rather than just ordered.

## Notes

- **Findings go to the mission or the issue, not the plan.** `track set` owns
  frontmatter; the plan is a working space.
- Keep `## Issues` after the issues exist. The order, blockers, and HITL/AFK tags
  live nowhere else.
- Advance the mission as it moves: `track set mission <id> status=planning|active`.
- Never write a local issue or mission id into an external ticket, PR, or repo.
