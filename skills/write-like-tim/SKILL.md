---
name: write-like-tim
description: Tim's personal terseness standard for prose — chat replies, PR/issue bodies, commit messages, and comments once code-like-tim has ruled one should exist. Use when drafting or trimming anything Tim will read or post, or during a length/clarity pass. Pairs with the Length rules in ~/.claude/CLAUDE.md and with the simple-english skill.
---

# Write like Tim

This is the case law behind the Length rules in `~/.claude/CLAUDE.md`. CLAUDE.md is
the short law; this skill holds the reasoning and worked examples so the judgment is
reproducible outside chat too — PR bodies, issue notes, commit messages, and comments
once `code-like-tim` has decided one should exist. It grows as Tim rules on more cases.

## The bar

> **Terseness wins. Accurate-but-extra words bury the useful ones, so a longer answer
> is a worse answer, not a safer one.**

## The cut order

1. Preamble that frames what's coming ("Two things stand out", "Let me explain").
   Open with the finding.
2. Anything the reader can already see: their screenshot, their error text, the diff
   just written.
3. How it was found — method, tools, ruled-out theories — unless the conclusion rests
   on it, or something couldn't be verified.
4. The second sentence restating the first. Make each point once.
5. Meta-commentary on your own choices: what you left out, what you nearly said, how
   confident you feel.

Keep the dense parts: a table of values, a one-line mechanism, a numbered list of
asks, a correction.

### The test that fails most drafts

**Would cutting this sentence lose a fact, or just a feeling?** If just a feeling —
of thoroughness, of having explained your process — cut it.

### Worked examples

**CUT — preamble that frames what's coming:**
```
before: "Two things stand out here. First, the login flow retries indefinitely on a
         401 because the retry guard checks the wrong status code."
after:  "The login flow retries indefinitely on a 401 — the retry guard checks the
         wrong status code."
```

**CUT — restating what the reader can already see:**
```
before: "Your screenshot shows a blank dashboard with the sidebar collapsed. That's
         happening because the /metrics call is returning 500."
after:  "The dashboard is blank because the /metrics call is returning 500."
```

**CUT — second sentence restating the first:**
```
before: "The build fails because the lockfile is out of date. In other words,
         package.json and package-lock.json are out of sync."
after:  "The build fails because the lockfile is out of date."
```

**CUT — meta-commentary on your own choices:**
```
before: "I decided not to touch the retry logic since that felt out of scope, but
         here's the fix for the timeout:"
after:  "Fix for the timeout:"
```

**KEEP — method earns its line because the conclusion rests on it:**
```
"Confirmed by bisecting: the regression starts at a3f21c, which dropped the http
client's default timeout from 30s to 5s."
```

**Applied to a comment, once `code-like-tim` has already ruled it should exist:**
```
before:
// Note: we need to re-fetch a fresh base here before writing, because if we
// don't, the write will diff against a stale snapshot and could revert fields
// that were changed elsewhere in the meantime. This matters because...
after:
// Re-fetch a fresh base: `updateCollection` diffs against current server
// state, so a stale snapshot could revert fields changed elsewhere.
```
`code-like-tim` decided this comment earns its place (warning of consequences);
this skill is why the second half got cut — it restated the same point the first
half already made.

## Pairs with simple-english

Terseness (this skill) and clarity (`simple-english`, ASD-STE100) cut different
things — this skill removes words that don't earn their place; `simple-english`
replaces the remaining ones with plainer, unambiguous phrasing (short sentences,
one word one meaning, active voice). Tim asks for both together often enough that
they should run together by default: when trimming prose for length, check the
available-skills listing for `simple-english` and invoke it on the same pass
rather than waiting to be asked for it by name.

`simple-english` is a separate skill, not part of this repo (see the README's
Setup section for how to install it). If it isn't in the listing, skip that step —
don't approximate STE rules from memory, and don't fail the rest of this skill
over it.

## Calibration note

When unsure, cut — the bar is strict, and a shorter draft is the normal outcome of a
pass. Surface borderline cuts so Tim can overrule; his overrides are the training
signal that sharpens this file.
