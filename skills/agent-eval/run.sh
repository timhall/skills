#!/usr/bin/env bash
# One eval trial: a fresh Claude session against a worktree at <ref>.
#
# usage: run.sh <task-file> <git-ref> <label>
#
# Runs serially by design -- a task that reaches shared external state (a
# database, fixed ports, named Docker containers) can collide across
# concurrent worktrees.
set -euo pipefail

TASK="${1:?task file}"; REF="${2:?git ref}"; LABEL="${3:?label}"
ROOT="$(git rev-parse --show-toplevel)"
WT="${EVAL_WORKTREES:-$(dirname "$ROOT")/agent-eval}/$LABEL"
OUT="${EVAL_OUT:-$ROOT/.agents/eval-results}"
DOC="${EVAL_DOC:-AGENTS.md}"
mkdir -p "$OUT" "$(dirname "$WT")"

if [ -e "$WT/.git" ]; then
  git -C "$WT" checkout --detach --quiet "$REF"
  git -C "$WT" reset --hard --quiet
  git -C "$WT" clean -qfd            # -x omitted on purpose: keeps node_modules
else
  git -C "$ROOT" worktree add --detach --quiet "$WT" "$REF"
fi

SETUP="${EVAL_SETUP:-}"
if [ -z "$SETUP" ] && [ -f "$WT/package.json" ]; then
  if [ -f "$WT/pnpm-lock.yaml" ]; then SETUP="pnpm install --silent"
  elif [ -f "$WT/yarn.lock" ]; then SETUP="yarn install --silent"
  elif [ -f "$WT/package-lock.json" ]; then SETUP="npm ci --silent"
  fi
fi
[ -n "$SETUP" ] && [ ! -d "$WT/node_modules" ] && (cd "$WT" && eval "$SETUP" >/dev/null)

# Overlay lets a trial test an uncommitted doc edit without committing it.
[ -n "${EVAL_OVERLAY_DOC:-}" ] && cp "$EVAL_OVERLAY_DOC" "$WT/$DOC"

PROMPT="${EVAL_PROMPT:-Complete the following task, including test coverage where relevant.}

Leave your changes uncommitted in the working tree when you are done, and finish by reporting what you changed and how you confirmed it works.

$(cat "$TASK")"

STAMP="$(date +%Y%m%d-%H%M%S)"
RESULT="$OUT/${LABEL}-${STAMP}.json"
cd "$WT"
claude -p "$PROMPT" --permission-mode auto --output-format json > "$RESULT" || true
# An overlaid doc is our edit, not the agent's, so keep it out of both captures.
# mnemonicPrefix is off here so a diff always carries a/ and b/ prefixes.
if [ -n "${EVAL_OVERLAY_DOC:-}" ]; then
  git -C "$WT" status --porcelain -- . ":(exclude)$DOC" > "${RESULT%.json}.files"
  git -C "$WT" -c diff.mnemonicPrefix=false diff -- . ":(exclude)$DOC" > "${RESULT%.json}.diff"
else
  git -C "$WT" status --porcelain > "${RESULT%.json}.files"
  git -C "$WT" -c diff.mnemonicPrefix=false diff > "${RESULT%.json}.diff"
fi
basename "$TASK" .md > "${RESULT%.json}.task"

node -e '
const f=process.argv[1], r=require(f);
console.log(`${process.argv[2]}  ${r.subtype}  ${Math.round(r.duration_ms/1000)}s  ${r.num_turns} turns  session=${r.session_id}`);
' "$RESULT" "$LABEL"
echo "$RESULT"
