#!/bin/bash
# clear-focus — drop the active-worktree pin, letting dev-hud fall back to
# the mtime heuristic (most-recently-committed feat+rdo-* worktree).
#
# Use after a PR is merged and the worktree removed, or when switching
# context away from a specific ticket and you want the statusline to
# auto-track the next thing you commit to.
#
# Usage:
#   clear-focus.sh

set -eu

CACHE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.statusline-cache"
FILE="$CACHE_DIR/active-worktree"

if [ -f "$FILE" ] && [ ! -L "$FILE" ]; then
  rm -f "$FILE"
  echo "focus cleared" >&2
else
  echo "focus already cleared" >&2
fi
