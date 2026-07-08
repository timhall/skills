---
name: issue
description: Create a new issue in {notes vault}/issues/. Use when user reports a bug, investigation, or small self-contained work item — including when they say "/bug". Accepts a plain description and optional links.
---

Create a new issue via the `track` CLI, which owns the ID, filename, and frontmatter format. Your job is the judgment; `track new` handles the format.

## Steps

1. **Infer from the description:**
   - **title** — a short human-readable title
   - **`--slug`** — a concise filename slug, *only* if the title is long or awkward; otherwise omit and the CLI slugifies the title
   - **`--source`** — detect from context: Slack URL/mention → `slack`; email → `email`; user/customer report → `user-report`; JIRA → `jira`; otherwise `self`
   - **`--link`** — any URLs mentioned, one `--link` each, as `"Label|URL"` (e.g. `"Slack thread|https://…"`)
   - **`--description`** — the description as provided, cleaned up for clarity. Don't add "Reported via Slack" etc. — source and links convey that. If sparse, use it as-is; don't invent detail.

2. **Create it:**

   ```bash
   track new issue "<title>" [--slug <slug>] [--source <source>] [--link "<Label>|<url>"] [--description "<text>"]
   ```

3. **Confirm** — the CLI prints the path and ID. Relay them and ask if anything needs correcting.

## Notes

- `/bug` is an alias for this skill.
- `track new` sets `status: open` and `created` to today, and leaves `closed`, `pr`, `jira`, and `tags` blank — don't pass those.
- To change status or fill fields later, use `track set issue <id> status=… pr=…` — never hand-edit the frontmatter.
