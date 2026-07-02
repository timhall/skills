---
name: code-like-tim
description: Tim's personal coding conventions — how he decides what earns a place in the code, starting with comments. Use when writing or reviewing code or comments in any of Tim's projects, when deciding whether a comment should exist, when trimming or cutting comments, or during a comment or review pass. Pairs with the always-on rules in ~/.claude/CLAUDE.md.
---

# Code like Tim

This is the case law behind the always-on rules in `~/.claude/CLAUDE.md`. CLAUDE.md
is the short law; this skill holds the reasoning and worked examples so the judgment
is reproducible, not just the verdict. It grows as Tim rules on more cases.

## Comments

### The bar

> **A comment must earn its place. It adds context the code cannot convey — never narrates what the code does.**

Default to no comment. Make the code speak for itself first (naming, structure,
small functions). Reach for a comment only when the code genuinely can't carry the
meaning on its own.

Per *Clean Code*, a comment that earns its place does exactly one of:

- **Intent** — *why* this approach, when the code alone leaves it ambiguous.
- **Clarification** — decode something the reader can't easily see (a non-obvious
  data shape, a round-trip, why a stub/mock is shaped a certain way).
- **Warning of consequences** — flag a landmine: "don't collapse this," "re-fetch
  first or you'll clobber," "this looks wrong but isn't."

If a comment isn't doing one of those, cut it.

### The test that fails most comments

**Does it prevent a wrong edit or a wrong mental model?** If not, it's narration.

- ❌ `// increment the counter` above `counter++` — narration.
- ❌ A comment that restates the function/variable name — the name already said it.
- ❌ In tests: a comment that restates the `it`/`describe` name or duplicates an
  assertion message string — those already carry it.
- ✅ A comment that stops someone from "simplifying" correct-but-surprising code.
- ✅ A comment that explains why a value is `''` when you'd expect `'hello'`.

### Brevity

One or two lines. State the constraint, not the narrative. Rationale, history, and
ticket context belong in the PR body or the issue — **never** in the diff. And never
reference internal trackers (issue/mission numbers, "defect C", review labels) in
code, tests, commits, or PRs.

### Worked examples

From a real review (variable-session promotion fix). Each is a ruling Tim made.

**KEEP — warning of consequences.** Prevents a future dev collapsing two flag checks
into one (which was the original bug):
```js
// V2-cloud and MPC-cloud have separate V3 flags, so check both — don't collapse to
// one. Over-matching is safe: the read/write paths fall back to EC/legacy anyway.
```

**KEEP — clarification of a non-obvious round-trip:**
```js
// Enabled shape for the merge; the write remaps back via `mapEnableToDisable`.
```

**KEEP — warning against a wrong conclusion.** Without it, the `''` looks like a bug:
```js
// The definition gets an empty-value placeholder; the real value lives in
// the session overlay (asserted below) and the editor merges the two.
expect(addedDef.value).to.equal('');
```

**KEEP (test) — why a stub is shaped this way** (code can't convey this):
```js
// Non-beta collection so the write takes the legacy branch, not the Extensible one.
sandbox.stub(ExtensibleCollectionAPI, 'isBetaCollection').returns(false);
```

**CUT — the variable name already says it:**
```js
// Holds the resolved v3 collection when the write goes through CollectionInterfaceV3...
v3CollectionForWrite = null;   // ← name carries the meaning; comment deleted
```

**CUT — duplicates the assertion message:**
```js
// Existing definition-backed key must be preserved (not clobbered).
expect(_.find(values, { key: 'key1' }), 'existing session key should be preserved')...
```

**TRIM — drop the sentence that narrates the next line; keep only the warning:**
```js
// before: "Write the promoted variables through CollectionInterfaceV3. Re-fetch a
//          fresh base first: updateCollection diffs against current server state..."
// after:
// Re-fetch a fresh base: `updateCollection` diffs against current server
// state, so a stale snapshot could revert fields changed elsewhere.
```

### Calibration note

When unsure, lean toward cutting — Tim's bar is strict. A halved comment count on a
review pass is a normal outcome. Surface borderline cuts so he can overrule; his
overrides are the training signal that sharpens this file.
