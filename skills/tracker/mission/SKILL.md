---
name: mission
description: Create a new mission in {notes vault}/missions/. Use when user wants to track an idea-to-delivery work item — a larger effort spanning design, planning, and implementation. Accepts a plain description and optional links.
---

Create a new mission via the `track` CLI, which owns the ID, filename, and frontmatter format. Your job is the judgment; `track new` handles the format.

## Steps

1. **Infer from the description:**
   - **title** — a short human-readable title
   - **`--slug`** — a concise filename slug, *only* if the title is long or awkward; otherwise omit and the CLI slugifies the title
   - **`--link`** — any URLs or references mentioned, one `--link` each, as `"Label|URL"`
   - **`--problem`** — one paragraph on what is broken, missing, or worth improving
   - **`--goal`** — what does done look like? Keep it concise; heavy detail belongs in `plans/`

2. **Create it:**

   ```bash
   track new mission "<title>" [--slug <slug>] [--link "<Label>|<url>"] [--problem "<text>"] [--goal "<text>"]
   ```

   If the description already states a clear problem and goal, use that language directly.

3. **Confirm** — the CLI prints the path and ID. Relay them and ask if anything needs correcting.

## Notes

- `track new` sets `status: idea` and `created` to today, and leaves `plans`, `jira`, and `tags` blank — don't pass those. `plans` is filled in later when a plans/ folder is created.
- To advance the mission, use `track set mission <id> status=planning|active|blocked|done` — never hand-edit the frontmatter.
