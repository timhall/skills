---
name: setup-zed-thread
description: Move the current thread into a fresh git worktree and branch, run setup, then optionally run a follow-up command there. Use when the user invokes /setup-zed-thread [command or brief], e.g. `/setup-zed-thread /work 165`, or asks to set up this thread in its own worktree instead of spinning off a new one.
---

# Setup Zed thread

Like `create-zed-thread`, but the current thread does the work. It enters the new worktree instead of opening another Zed thread.

## 1. Resolve and create

Read `~/.claude/skills/create-zed-thread/SKILL.md` and follow its steps 1 to 4 (resolve repo and base branch, name it, create the worktree, set it up). Differences:

- The argument is the follow-up command or brief, not a brief to write down. With no argument, derive the slug from the conversation.
- For `/work <id>` or similar, take the slug from the item's title: `track get <issue|mission> <id>`, or the Jira summary for a ticket key.
- Skip step 5 (no `BRIEF.md`) and step 6 (no `zed` or `open` calls).

## 2. Enter the worktree

The user invoking this skill is the explicit worktree request. Load the deferred tool with `ToolSearch` (`select:EnterWorktree`), then call `EnterWorktree` with `path` set to the new worktree. Run setup after entering so it runs with the worktree as the working directory.

All later work happens in the worktree. Use absolute paths under it, and `git -C` for git.

## 3. Run the command

If the argument is a slash command, invoke it with the Skill tool, passing the rest as args. Tell it the worktree and branch already exist and to skip any worktree step. Otherwise treat the argument as the brief and start on it.

End with the worktree path and branch. Nothing else.
