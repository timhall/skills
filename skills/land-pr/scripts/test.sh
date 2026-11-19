#!/usr/bin/env bash
# Offline tests for watch-pr's digest/fingerprint rules. Run: scripts/test.sh
set -euo pipefail

source "$(dirname "$0")/watch-pr"

BASE='{
  "viewer": "me",
  "pr": {
    "state": "OPEN", "isDraft": false, "mergeable": "MERGEABLE", "headRefOid": "aaa111", "reviewDecision": null,
    "reviewThreads": {"nodes": []}, "comments": {"nodes": []}, "reviews": {"nodes": []}
  },
  "checks": [
    {"name": "build", "workflow": "ci", "bucket": "pass", "state": "SUCCESS", "link": "u"},
    {"name": "test", "workflow": "ci", "bucket": "pass", "state": "SUCCESS", "link": "u"}
  ]
}'

fp() { jq "$1" <<<"$BASE" | digest | fingerprint; }
field() { jq "$1" <<<"$BASE" | digest | jq -r "$2"; }

failures=0
expect() { # name, expected changed components, filter, [baseline filter]
  local got
  got=$(changed_components "$(fp "${4:-.}")" "$(fp "$3")")
  if [[ $got == "$2" ]]; then echo "ok   $1"; else echo "FAIL $1: expected '$2', got '$got'"; failures=$((failures + 1)); fi
}
expect_field() { # name, expected, filter, jq field
  local got
  got=$(field "$3" "$4")
  if [[ $got == "$2" ]]; then echo "ok   $1"; else echo "FAIL $1: expected '$2', got '$got'"; failures=$((failures + 1)); fi
}

THREAD='{"id": "T1", "isResolved": false, "isOutdated": false, "path": "a.ts", "line": 3, "comments": {"nodes": [
  {"databaseId": 10, "url": "u", "body": "nit", "author": {"login": "copilot[bot]", "__typename": "Bot"}}]}}'
WITH_THREAD=".pr.reviewThreads.nodes = [$THREAD]"

expect "identical state is stable" "" '.'
expect "new commit" "head" '.pr.headRefOid = "bbb222"'
expect "merged" "state" '.pr.state = "MERGED"'
expect "merge conflict" "conflict" '.pr.mergeable = "CONFLICTING"'
expect "unknown mergeability is not a conflict" "" '.pr.mergeable = "UNKNOWN"'

expect "others' conversation comment" "comments" \
  '.pr.comments.nodes = [{"databaseId": 5, "url": "u", "body": "hi", "author": {"login": "bob", "__typename": "User"}}]'
expect "own conversation comment is ignored" "" \
  '.pr.comments.nodes = [{"databaseId": 5, "url": "u", "body": "fixed", "author": {"login": "me", "__typename": "User"}}]'
expect "others' review" "reviews" \
  '.pr.reviews.nodes = [{"databaseId": 7, "url": "u", "state": "APPROVED", "body": "", "author": {"login": "bob", "__typename": "User"}}]'

expect "new unresolved thread" "threads" "$WITH_THREAD"
expect "own reply in a thread is ignored" "" \
  "$WITH_THREAD | .pr.reviewThreads.nodes[0].comments.nodes += [{\"databaseId\": 11, \"url\": \"u\", \"body\": \"done\", \"author\": {\"login\": \"me\", \"__typename\": \"User\"}}]" \
  "$WITH_THREAD"
expect "thread starts from a reply by someone else" "threads" \
  "$WITH_THREAD | .pr.reviewThreads.nodes[0].comments.nodes += [{\"databaseId\": 12, \"url\": \"u\", \"body\": \"why?\", \"author\": {\"login\": \"bob\", \"__typename\": \"User\"}}]"
expect "thread with only my comments is ignored" "" \
  '.pr.reviewThreads.nodes = [{"id": "T2", "isResolved": false, "isOutdated": false, "path": "a.ts", "line": 1, "comments": {"nodes": [{"databaseId": 20, "url": "u", "body": "note", "author": {"login": "me", "__typename": "User"}}]}}]'

PENDING='.checks[1].bucket = "pending"'
LINT_RUNNING='.checks += [{"name": "lint", "workflow": "ci", "bucket": "pending", "state": "PENDING", "link": "u"}]'
expect "check finishing while another runs" "" \
  "$LINT_RUNNING | .checks[0].bucket = \"pending\" | .checks[1].bucket = \"pass\"" \
  "$LINT_RUNNING | .checks[0].bucket = \"pending\""
expect "new failure while checks run" "checks" \
  "$PENDING | .checks[0].bucket = \"fail\""

running_fp=$(jq "$PENDING" <<<"$BASE" | digest | fingerprint)
settled_fp=$(fp .)
empty_fp=$(jq '.checks = []' <<<"$BASE" | digest | fingerprint)
if [[ -z $(changed_components "$empty_fp" "$running_fp") ]]; then echo "ok   checks appearing as pending is stable"; else echo "FAIL checks appearing as pending is stable"; failures=$((failures + 1)); fi
if [[ $(changed_components "$running_fp" "$settled_fp") == checks ]]; then echo "ok   running to settled wakes"; else echo "FAIL running to settled wakes"; failures=$((failures + 1)); fi

expect_field "ready when green" true '.' '.ready'
expect_field "not ready with failing check" false '.checks[0].bucket = "fail"' '.ready'
expect_field "not ready while pending" false "$PENDING" '.ready'
expect_field "not ready with unresolved bot thread" false "$WITH_THREAD" '.ready'
expect_field "human thread does not block ready" true \
  "$WITH_THREAD | .pr.reviewThreads.nodes[0].comments.nodes[0].author = {\"login\": \"bob\", \"__typename\": \"User\"}" '.ready'
expect_field "not ready when draft" false '.pr.isDraft = true' '.ready'
expect_field "not ready with conflict" false '.pr.mergeable = "CONFLICTING"' '.ready'

if [[ $(changed_components "garbage" "$(fp .)" | tr , ' ' | wc -w) -eq 7 ]]; then echo "ok   lost baseline changes everything"; else echo "FAIL lost baseline changes everything"; failures=$((failures + 1)); fi

[[ $failures -eq 0 ]] || { echo "$failures failed"; exit 1; }
echo "all passed"
