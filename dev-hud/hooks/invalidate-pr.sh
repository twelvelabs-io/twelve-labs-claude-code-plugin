#!/bin/bash
# invalidate-pr — drop cached PR number + URL so the next statusline render
# fetches fresh data via `gh pr view`.
#
# Background: the PR cache is keyed by sha(repo-toplevel + branch) with a
# 10-min TTL. After `gh pr create` (or any out-of-band PR open/close) the
# cache still holds the prior value (empty if no PR existed, stale if it
# did). Run this from /ship (or any push-and-PR workflow) so the badge
# updates on the next render instead of after the TTL.
#
# Usage:
#   invalidate-pr.sh             # nuke every pr-*/pr-url-* entry
#   invalidate-pr.sh <branch>    # nuke just the entry for $PWD's repo + <branch>
#
# The branch form is keyed by `git rev-parse --show-toplevel` from $PWD, so
# run it from inside the worktree whose PR you just opened.

set -eu

CACHE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.statusline-cache"
mkdir -p "$CACHE_DIR"

if [ "$#" -eq 0 ]; then
  COUNT=0
  for f in "$CACHE_DIR"/pr-* "$CACHE_DIR"/pr-url-*; do
    [ -e "$f" ] || continue
    rm -f "$f"
    COUNT=$((COUNT + 1))
  done
  echo "invalidated $COUNT PR cache entr$([ $COUNT -eq 1 ] && echo y || echo ies)" >&2
  exit 0
fi

BRANCH="$1"

TOPLEVEL=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [ -z "$TOPLEVEL" ]; then
  echo "not inside a git worktree; run from the worktree or call without args" >&2
  exit 65
fi

# Match the keying in statusline.sh: shasum of "<toplevel>\n<branch>", first 12 chars.
KEY=$(printf '%s\n%s' "$TOPLEVEL" "$BRANCH" | shasum 2>/dev/null | cut -c1-12)
if [ -z "$KEY" ]; then
  echo "could not compute cache key (shasum missing?)" >&2
  exit 66
fi

rm -f "$CACHE_DIR/pr-$KEY" "$CACHE_DIR/pr-url-$KEY"
echo "invalidated PR cache for $BRANCH ($KEY)" >&2
