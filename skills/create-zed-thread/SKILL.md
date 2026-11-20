---
name: create-zed-thread
description: Spin off a chunk of work into its own Zed agent thread in a fresh git worktree. Creates the worktree and branch from a brief, runs setup, and gives the commands that open a new Zed window and a thread with the brief prefilled. Use when the user invokes /create-zed-thread [brief] or asks to spin off, hand off, or start a new thread for a piece of work.
---

# Create Zed thread

Spins one chunk of work into a full Zed thread the user can review and work in collaboratively. Not a subagent.

## 1. Resolve the project and brief

- Repo: from the current directory, `git rev-parse --path-format=absolute --git-common-dir`; its parent is the main checkout and its basename is `<repo>`. This works from inside a worktree too.
- Base branch: `git symbolic-ref --short refs/remotes/origin/HEAD` in the main checkout (`origin/main`, or `origin/develop` for postman-app).
- Brief: the argument. With no argument, write one from the current conversation: the work the user just described or deferred, with the context a cold-start agent needs (goal, relevant files, constraints, what is already decided or ruled out).

## 2. Name it

Pick a kebab-case slug of 2 to 4 words that names the work, with no prefix and no ticket-style IDs unless the brief gives one. Use it as the branch name and the worktree name. If the user asks for "no branch", use a detached worktree and the slug for the directory only.

## 3. Create the worktree

Follow the existing layout, `~/dev/postman-eng/worktrees/<repo>/<slug>/<repo>`:

```sh
git -C <main> fetch origin <base-branch>
git -C <main> worktree add -b <slug> ~/dev/postman-eng/worktrees/<repo>/<slug>/<repo> origin/<base-branch>
```

Detached: `git -C <main> worktree add --detach <path> origin/<base-branch>`. Stop and ask if the branch or path already exists. Worktree creation writes outside the sandbox allowlist; retry unsandboxed on "Operation not permitted".

## 4. Set it up

- If the worktree has an executable `.agents/prepare`, run it with the worktree as the working directory.
- Otherwise, `postman-app`: run the `prepare` skill's script from inside the worktree.
- Otherwise skip, and say so.

## 5. Write the brief

Write it to `$(git -C <worktree> rev-parse --git-dir)/BRIEF.md`, which git never tracks, so the worktree stays clean. Lead with the worktree path, branch, and base.

## 6. Hand off to Zed

Run these as two separate, standalone Bash calls with no pipes or chaining, because the user's `excludedCommands` and allow rules match only whole commands:

```sh
zed -e <worktree>
open "zed://agent?prompt=<url-encoded prompt>"
```

`-e` opens the worktree in the existing Zed window and makes it the active workspace. The URL has no folder parameter and lands in the active workspace, so without `-e` the thread can open in the wrong window.

The prompt says to read the brief file and start. If the brief is itself a slash command such as `/work 165`, make the prompt that command, followed by a line saying the worktree and branch already exist and to skip any worktree step. Encode with `node -e 'process.stdout.write(encodeURIComponent(process.argv[1]))' "<prompt>"`. Zed prefills the prompt in a new thread and does not send it, so the user reviews and presses send.

If either call fails with a sandbox error, print both commands for the user to run instead of retrying unsandboxed.

End with the worktree path and branch. Nothing else.
