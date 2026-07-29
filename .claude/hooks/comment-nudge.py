#!/usr/bin/env python3
"""Stop hook: nudge toward code-like-tim comment discipline, once per turn.

Scans only files touched by Edit/Write/MultiEdit since the last user prompt
(not the whole working tree, so pre-existing uncommitted changes are never
flagged), and only newly-added lines (not pre-existing comments). Detection
is a simple per-extension prefix check -- false positives are an accepted,
tunable cost for this first pass.
"""

import difflib
import json
import os
import subprocess
import sys

COMMENT_PREFIXES = {
    ".py": ["#"], ".sh": ["#"], ".bash": ["#"], ".zsh": ["#"],
    ".yml": ["#"], ".yaml": ["#"], ".rb": ["#"], ".toml": ["#"],
    ".js": ["//", "/*", "*"], ".jsx": ["//", "/*", "*"],
    ".ts": ["//", "/*", "*"], ".tsx": ["//", "/*", "*"],
    ".java": ["//", "/*", "*"], ".c": ["//", "/*", "*"], ".h": ["//", "/*", "*"],
    ".cpp": ["//", "/*", "*"], ".hpp": ["//", "/*", "*"],
    ".go": ["//", "/*", "*"], ".rs": ["//", "/*", "*"],
    ".swift": ["//", "/*", "*"], ".kt": ["//", "/*", "*"],
    ".php": ["//", "#", "/*", "*"],
    ".css": ["/*", "*"], ".scss": ["//", "/*", "*"],
    ".html": ["<!--"], ".htm": ["<!--"], ".xml": ["<!--"], ".vue": ["<!--", "//", "/*", "*"],
}


SHEBANG_LANG = {
    "python": ".py", "python3": ".py", "python2": ".py",
    "bash": ".sh", "sh": ".sh", "zsh": ".sh",
    "ruby": ".rb", "node": ".js", "perl": ".pl",
}


def resolve_ext(file_path):
    """Extensionless scripts (e.g. shebang-only) are identified by their shebang on disk."""
    ext = os.path.splitext(file_path)[1]
    if ext in COMMENT_PREFIXES:
        return ext
    try:
        with open(file_path) as f:
            first_line = f.readline()
    except Exception:
        return ext
    if not first_line.startswith("#!"):
        return ext
    parts = first_line[2:].split()
    if not parts:
        return ext
    interp = os.path.basename(parts[0])
    if interp == "env" and len(parts) > 1:
        interp = os.path.basename(parts[1])
    return SHEBANG_LANG.get(interp, ext)


def is_comment_line(stripped, ext):
    prefixes = COMMENT_PREFIXES.get(ext)
    if not prefixes or stripped.startswith("#!"):
        return False
    return any(stripped.startswith(p) for p in prefixes)


def added_lines(old_text, new_text):
    diff = difflib.unified_diff(old_text.splitlines(), new_text.splitlines(), lineterm="", n=0)
    return [line[1:] for line in diff if line.startswith("+") and not line.startswith("+++")]


def git_head_content(repo_root, file_path):
    try:
        relpath = os.path.relpath(file_path, repo_root)
        result = subprocess.run(
            ["git", "-C", repo_root, "show", f"HEAD:{relpath}"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout if result.returncode == 0 else ""
    except Exception:
        return ""


def repo_root_for(path, fallback):
    try:
        result = subprocess.run(
            ["git", "-C", os.path.dirname(path), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return fallback


def load_transcript(transcript_path):
    entries = []
    with open(transcript_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def tool_uses_since_last_prompt(entries):
    start = 0
    for i, entry in enumerate(entries):
        if entry.get("type") == "last-prompt":
            start = i + 1
    uses = []
    for entry in entries[start:]:
        content = entry.get("message", {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") in (
                "Edit", "Write", "MultiEdit",
            ):
                uses.append(block)
    return uses


def find_new_comments(tool_use, cwd):
    name = tool_use.get("name")
    tool_input = tool_use.get("input", {})
    file_path = tool_input.get("file_path")
    if not file_path:
        return []
    ext = resolve_ext(file_path)
    if ext not in COMMENT_PREFIXES:
        return []

    if name == "Edit":
        pairs = [(tool_input.get("old_string", ""), tool_input.get("new_string", ""))]
    elif name == "MultiEdit":
        pairs = [(e.get("old_string", ""), e.get("new_string", "")) for e in tool_input.get("edits", [])]
    else:  # Write
        repo_root = repo_root_for(file_path, cwd)
        pairs = [(git_head_content(repo_root, file_path), tool_input.get("content", ""))]

    found = []
    for old, new in pairs:
        for line in added_lines(old, new):
            if is_comment_line(line.strip(), ext):
                found.append((file_path, line.strip()))
    return found


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if payload.get("stop_hook_active"):
        sys.exit(0)

    transcript_path = payload.get("transcript_path")
    cwd = payload.get("cwd", os.getcwd())
    if not transcript_path or not os.path.exists(transcript_path):
        sys.exit(0)

    try:
        entries = load_transcript(transcript_path)
        tool_uses = tool_uses_since_last_prompt(entries)
        flagged = []
        for tool_use in tool_uses:
            flagged.extend(find_new_comments(tool_use, cwd))
    except Exception as e:
        print(f"comment-nudge hook error (ignored): {e}", file=sys.stderr)
        sys.exit(0)

    if not flagged:
        sys.exit(0)

    print("New comment(s) added this turn -- justify each against the code-like-tim skill's bar", file=sys.stderr)
    print("(does it state a non-obvious constraint a reader would otherwise be misled or waste time without?), or remove it:", file=sys.stderr)
    for file_path, line in flagged:
        print(f"  {file_path}: {line}", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
