#!/usr/bin/env python3
"""Push the daily dashboard to a TRMNL private plugin.

Assembles a glanceable screen from several local sources and POSTs it to the TRMNL
webhook as merge_variables. Called at the end of the /hello and /goodbye skills.

Sources:
  - Today's 3 + blocker   -> ~/Documents/notes/Daily Notes/YYYY-MM-DD.md
  - Weekly goals          -> ~/Documents/notes/Weekly Goals.md (## Goals bullets)
  - Stoic quote of the day-> the note's "Daily Stoic" block if present, else
                             ./stoic_quotes.json (public-domain, indexed by day-of-year)
  - Review / PR counts    -> `gh` over WATCHED_REPOS
  - Weather (hi/lo/cond)  -> open-meteo (no API key) for LOCATION

Non-fatal by design: any missing/failed source is simply omitted; the whole thing
exits 0 so it never interrupts a skill run.

Webhook contract (https://docs.trmnl.com/go/private-plugins/webhooks):
  POST https://trmnl.com/api/custom_plugins/{UUID}  (<=2KB, 12 req/hr on standard)
UUID resolution: --uuid arg -> $TRMNL_WEBHOOK_UUID -> ./uuid.txt (next to this script)
"""

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT = os.path.expanduser("~/Documents/notes")
NOTE_DIR = os.path.join(VAULT, "Daily Notes")
WEEKLY_GOALS_FILE = os.path.join(VAULT, "Weekly Goals.md")
STOIC_FILE = os.path.join(HERE, "stoic_quotes.json")
UUID_FILE = os.path.join(HERE, "uuid.txt")

ENDPOINT = "https://trmnl.com/api/custom_plugins/{}"
SIZE_LIMIT = 2048  # standard account; TRMNL+ is 5120
UA = "trmnl-daily-note/1.0 (+https://github.com/timhall/skills)"

# PR counts are summed across these repos (same as the /hello watch list).
WATCHED_REPOS = ["postman-eng/unified-runtime-monorepo", "postman-eng/postman-app"]

# Weather location. Coordinates so no geocoding call is needed. Update name+lat+lon
# if you move. Units are Fahrenheit / mph.
LOCATION = {"name": "Bon Air, VA", "lat": 37.5165, "lon": -77.5566}

# open-meteo WMO weather codes -> (short label, glyph)
WEATHER_CODES = {
    0: ("Clear", "☀"), 1: ("Mostly clear", "🌤"), 2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁"), 45: ("Fog", "🌫"), 48: ("Fog", "🌫"),
    51: ("Drizzle", "🌦"), 53: ("Drizzle", "🌦"), 55: ("Drizzle", "🌦"),
    61: ("Rain", "🌧"), 63: ("Rain", "🌧"), 65: ("Heavy rain", "🌧"),
    66: ("Freezing rain", "🌧"), 67: ("Freezing rain", "🌧"),
    71: ("Snow", "🌨"), 73: ("Snow", "🌨"), 75: ("Heavy snow", "🌨"), 77: ("Snow", "🌨"),
    80: ("Showers", "🌦"), 81: ("Showers", "🌦"), 82: ("Heavy showers", "🌧"),
    85: ("Snow showers", "🌨"), 86: ("Snow showers", "🌨"),
    95: ("Thunderstorm", "⛈"), 96: ("Thunderstorm", "⛈"), 99: ("Thunderstorm", "⛈"),
}


# --- shared helpers -------------------------------------------------------------

def http_get_json(url, timeout=10):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


# --- data sources ---------------------------------------------------------------

def parse_daily_note(text):
    """Today's 3 (with checked state) + the blocker line from the Morning section."""
    tasks, blocker, in_block = [], "", False
    for line in text.splitlines():
        s = line.strip()
        if re.match(r"^\*\*Today'?s 3:?\*\*", s, re.I):
            in_block = True
            continue
        if in_block:
            m = re.match(r"^- \[([ xX])\]\s*(.+)$", s)
            if m:
                tasks.append({"text": m.group(2).strip(), "done": m.group(1).lower() == "x"})
                continue
            if s and not s.startswith("- ["):
                in_block = False
        m = re.match(r"^-?\s*\*{0,2}Blocked:?\*{0,2}\s*(.+)$", s, re.I)
        if m:
            blocker = m.group(1).strip().rstrip("*").strip()
    return tasks, blocker


def parse_stoic_from_note(text):
    """The hand-entered Daily Stoic quote from the note, or None if absent.

    Matches a '**Daily Stoic:**' label followed by blockquote lines:
        **Daily Stoic:**
        > "the quote"
        > — Author
    Blockquote lines beginning with a dash/em-dash are the attribution; the rest
    form the quote. Returns {"text", "author"} or None.
    """
    quote_parts, author, in_block = [], "", False
    for line in text.splitlines():
        s = line.strip()
        if re.match(r"^\*\*Daily Stoic:?\*\*", s, re.I):
            in_block = True
            continue
        if in_block:
            m = re.match(r"^>\s?(.*)$", s)
            if not m:
                break  # blockquote ended
            content = m.group(1).strip()
            if not content:
                continue
            am = re.match(r"^[—–-]\s*(.+)$", content)
            if am:
                author = am.group(1).strip()
            else:
                quote_parts.append(content)
    quote = " ".join(quote_parts).strip().strip('"“”').strip()
    if not quote:
        return None
    return {"text": quote, "author": author}


def read_weekly_goals(max_goals=3):
    """Bullets under the '## Goals' heading of Weekly Goals.md."""
    try:
        with open(WEEKLY_GOALS_FILE) as fh:
            text = fh.read()
    except FileNotFoundError:
        return []
    goals, in_goals = [], False
    for line in text.splitlines():
        s = line.strip()
        if re.match(r"^#{1,6}\s+Goals\b", s, re.I):
            in_goals = True
            continue
        if in_goals:
            if s.startswith("#"):  # next heading ends the section
                break
            m = re.match(r"^[-*]\s+(.+)$", s)
            if m:
                goals.append(m.group(1).strip())
    return goals[:max_goals]


def stoic_for_day(date_obj):
    try:
        with open(STOIC_FILE) as fh:
            quotes = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    if not quotes:
        return None
    return quotes[date_obj.timetuple().tm_yday % len(quotes)]


def gh_pr_counts():
    """(#PRs awaiting my review, #my open PRs) summed across WATCHED_REPOS; None on failure."""
    reviews = my_prs = 0
    ok = False
    for repo in WATCHED_REPOS:
        # user-review-requested (not review-requested) excludes team/codeowner
        # auto-requests, so this counts only PRs asking for *you* specifically.
        for flag, bucket in (("--search=user-review-requested:@me", "reviews"),
                             ("--author=@me", "author")):
            try:
                out = subprocess.run(
                    ["gh", "pr", "list", "--repo", repo, flag, "--json", "number"],
                    capture_output=True, text=True, timeout=20, check=True,
                ).stdout
                n = len(json.loads(out or "[]"))
                if bucket == "reviews":
                    reviews += n
                else:
                    my_prs += n
                ok = True
            except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
                pass
    return (reviews, my_prs) if ok else (None, None)


def fetch_weather():
    lat, lon = LOCATION["lat"], LOCATION["lon"]
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={lat}&longitude={lon}"
           "&daily=temperature_2m_max,temperature_2m_min,weather_code"
           "&temperature_unit=fahrenheit&wind_speed_unit=mph"
           "&timezone=auto&forecast_days=1")
    try:
        data = http_get_json(url)
        daily = data["daily"]
        code = int(daily["weather_code"][0])
        label, glyph = WEATHER_CODES.get(code, ("", ""))
        return {
            "hi": round(daily["temperature_2m_max"][0]),
            "lo": round(daily["temperature_2m_min"][0]),
            "label": label,
            "glyph": glyph,
            "place": LOCATION["name"],
        }
    except (urllib.error.URLError, KeyError, IndexError, ValueError, TimeoutError):
        return None


# --- payload + send -------------------------------------------------------------

def build_payload(date_obj, tasks, blocker, goals, stoic, pr_counts, weather):
    reviews, my_prs = pr_counts
    mv = {
        "date": f"{date_obj.strftime('%A · %b')} {date_obj.day}",
        "week_label": f"Wk {date_obj.isocalendar()[1]}",
        "week_goals": goals,
        "tasks": tasks,
        "done_count": sum(1 for t in tasks if t["done"]),
        "total_count": len(tasks),
        "blocker": blocker or "—",
        "updated": dt.datetime.now().strftime("%-I:%M %p"),
    }
    if stoic:
        mv["stoic_text"] = stoic["text"]
        mv["stoic_author"] = stoic["author"]
    if reviews is not None:
        mv["reviews_waiting"] = reviews
        mv["my_prs"] = my_prs
    if weather:
        mv["weather"] = weather
    return {"merge_variables": mv}


def resolve_uuid(arg_uuid):
    if arg_uuid:
        return arg_uuid.strip()
    if os.environ.get("TRMNL_WEBHOOK_UUID", "").strip():
        return os.environ["TRMNL_WEBHOOK_UUID"].strip()
    try:
        with open(UUID_FILE) as fh:
            for line in fh:
                v = line.strip()
                if v and not v.startswith("#"):
                    return v
    except FileNotFoundError:
        pass
    return ""


def post(uuid, payload):
    data = json.dumps(payload).encode("utf-8")
    if len(data) > SIZE_LIMIT:
        print(f"⚠️  payload is {len(data)} bytes (>{SIZE_LIMIT}); TRMNL may reject it. "
              "Trim text or upgrade to TRMNL+.", file=sys.stderr)
    req = urllib.request.Request(
        ENDPOINT.format(uuid),
        data=data,
        # Real User-Agent required: TRMNL is behind Cloudflare, which bans
        # urllib's default "Python-urllib/*" signature (403, error 1010).
        headers={"Content-Type": "application/json", "User-Agent": UA},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.status


def main():
    ap = argparse.ArgumentParser(description="Push the daily dashboard to TRMNL.")
    ap.add_argument("--date", help="YYYY-MM-DD (default: today)")
    ap.add_argument("--uuid", help="override TRMNL plugin settings UUID")
    ap.add_argument("--dry-run", action="store_true", help="print payload, don't POST")
    args = ap.parse_args()

    date_obj = (dt.datetime.strptime(args.date, "%Y-%m-%d").date()
                if args.date else dt.date.today())
    note_path = os.path.join(NOTE_DIR, f"{date_obj.isoformat()}.md")

    try:
        with open(note_path) as fh:
            note_text = fh.read()
    except FileNotFoundError:
        print(f"No daily note at {note_path} — nothing to push.", file=sys.stderr)
        return 0

    tasks, blocker = parse_daily_note(note_text)
    if not tasks:
        print(f"No Today's 3 found in {note_path} — nothing to push.", file=sys.stderr)
        return 0

    goals = read_weekly_goals()
    # Prefer the quote Tim entered in the note this morning; fall back to the
    # bundled day-of-year quote when the note has no Daily Stoic block.
    stoic = parse_stoic_from_note(note_text) or stoic_for_day(date_obj)
    pr_counts = gh_pr_counts()
    weather = fetch_weather()

    payload = build_payload(date_obj, tasks, blocker, goals, stoic, pr_counts, weather)

    if args.dry_run:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    uuid = resolve_uuid(args.uuid)
    if not uuid:
        print("⚠️  TRMNL webhook UUID not set — skipping push. "
              f"Add it to {UUID_FILE} or set $TRMNL_WEBHOOK_UUID.", file=sys.stderr)
        return 0

    try:
        status = post(uuid, payload)
        mv = payload["merge_variables"]
        extras = []
        if "stoic_text" in mv: extras.append("stoic")
        if "reviews_waiting" in mv: extras.append(f"{mv['reviews_waiting']} reviews")
        if "weather" in mv: extras.append(f"{mv['weather']['hi']}°/{mv['weather']['lo']}°")
        if goals: extras.append(f"{len(goals)} week goals")
        print(f"TRMNL push OK ({status}): {mv['done_count']}/{mv['total_count']} tasks"
              + (f" · {', '.join(extras)}" if extras else ""))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print("⚠️  TRMNL rate limit hit (429) — 12 pushes/hr on standard accounts.",
                  file=sys.stderr)
        else:
            print(f"⚠️  TRMNL push failed ({e.code}): {e.read().decode('utf-8','replace')}",
                  file=sys.stderr)
    except urllib.error.URLError as e:
        print(f"⚠️  TRMNL push failed (network): {e.reason}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
