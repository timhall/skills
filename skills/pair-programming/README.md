# Pair programming

Pairing styles as skills. Each style decides who holds the keyboard, and the skill name says which role *the agent* takes.

## The styles

| Style | Drives (types) | Navigates (reads, maps, questions) | Skill |
|-------|----------------|------------------------------------|-------|
| Driver–navigator | agent | you | [`/driver`](driver/SKILL.md) |
| Driver–navigator | you | agent | [`/navigator`](navigator/SKILL.md) |
| Navigator–navigator | nobody | both | `/grill-me` (from `mattpocock/skills`) |
| Tour guide | you | agent narrates the codebase to you | not built |
| Ping pong | alternating, test-first | alternating | not built |

The default agent flow, where the agent writes and you review afterward, isn't pairing. Nobody navigates while the code is being written; review arrives after the decisions are already made.

## Naming

The command names the role **the agent** takes. `/driver` means the agent drives; `/navigator` means the agent navigates. Terse because you type it often. Each skill's description names both chairs, so the convention never has to be remembered.

## One keyboard

Every style here assumes one keyboard. Whoever holds it types; whoever doesn't holds the map and the veto. The keyboard changes hands on request, and whoever isn't typing gets exactly one push-back before deferring (`/driver` rule 6 and `/navigator` job 5 are the same rule from opposite chairs).

Design work belongs to `/grill-me`. Both skills escalate there instead of growing a planning mode of their own.

## Mechanics

Both skills are user-invoked (`disable-model-invocation: true`). Choosing how we collaborate is your call, not something the agent should elect mid-task, and an unused skill then costs no context. The trade: the agent can't see that these exist, so remembering to invoke them is on you.

That's also why this file is a plain document rather than a skill. User-invoked skills carry no description, so neither can reach the other, and shared vocabulary has to live outside the skill system.

## Slots

- **`/tour-guide`** — inverts the purpose rather than the roles: context flows to you, instead of critique to the code. Wants its own design pass.
- **`/ping-pong`** — one side writes a failing test, the other makes it pass and writes the next. Overlaps `tdd`; needs a decision about where the line falls.
- **A model-invocable mode selector** — the `grilling`→`grill-me` shape. An engine that can suggest which pairing style fits the moment, with these skills as the terse entry points.
