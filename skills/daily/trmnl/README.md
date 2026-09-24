# trmnl — daily note on a TRMNL display

Pushes the **Today's 3** from the Obsidian daily note
(`~/Documents/notes/Daily Notes/YYYY-MM-DD.md`) to a [TRMNL](https://usetrmnl.com)
e-ink display via a private-plugin webhook. Called automatically at the end of the
`/hello` and `/goodbye` skills.

## One-time setup

1. **Create the plugin.** In the TRMNL web UI: *Plugins → Private Plugin → Add New*.
   Give it a name (e.g. "Daily Note") and choose the **Webhook** strategy.
2. **Grab the UUID.** Open the plugin's settings; the webhook URL looks like
   `https://trmnl.com/api/custom_plugins/<UUID>`. Copy the `<UUID>` part.
3. **Store it.** Paste the UUID into `uuid.txt` (this file is gitignored):
   ```
   echo "PASTE-UUID-HERE" > ~/dev/timhall/skills/skills/daily/trmnl/uuid.txt
   ```
   Or set `TRMNL_WEBHOOK_UUID` in your shell env instead.
4. **Paste the markup.** Copy `template.liquid` into the plugin's **Markup** editor
   (Full layout). Adjust in TRMNL's live preview to taste.
5. **Add the plugin to a playlist / mashup** so it appears in the device rotation.

## Usage

```bash
# push today's note
python3 push_daily_note.py

# preview the JSON without sending
python3 push_daily_note.py --dry-run

# a specific day, or override the UUID once
python3 push_daily_note.py --date 2026-07-07 --uuid <UUID>
```

## Data shape

The script POSTs `{"merge_variables": {...}}` with:

| variable | example |
|----------|---------|
| `date` | `Tuesday · Jul 7` |
| `tasks` | `[{"text": "Ship the release notes", "description": "final pass before send"}, …]` |
| `stoic_text` (optional) | `"You have power over your mind — not outside events."` |
| `reviews_waiting` / `my_prs` (optional pair) | `2` / `1` |

## Limits (from TRMNL docs)

- Payload ≤ **2 KB** (5 KB on TRMNL+) — the script warns if exceeded.
- **12 pushes/hour** (30 on TRMNL+); over that returns `429`.

The script is **non-fatal by design**: a missing note, missing UUID, rate limit, or
network error prints a warning and exits `0`, so it never interrupts a skill run.
