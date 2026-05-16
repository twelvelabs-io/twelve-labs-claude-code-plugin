#!/bin/bash
# set-focus — point dev-hud at a specific worktree.
#
# The statusline resolves focus in this order:
#   1. Claude Code's `workspace.git_worktree` stdin payload (per-session)
#   2. ~/.claude/.statusline-cache/active-worktree (this script writes that)
#   3. Most-recently-committed feat+rdo-* worktree under .claude/worktrees/
#
# Use this from a workflow that *creates* or *switches into* a worktree
# (e.g. /start after new-ticket.sh, /cursor after `open -a Cursor`) so the
# next statusline render shows the new ticket immediately — without waiting
# for the mtime fallback to catch up after the first commit.
#
# Usage:
#   set-focus.sh <absolute-worktree-path>
#
# Example:
#   set-focus.sh "$HOME/Documents/Repos/tl-rodeo-fe/.claude/worktrees/feat+rdo-1011"
#
# Defenses (mirroring statusline.sh's reader):
#   - Path must be absolute and live under $HOME. Stops an attacker from
#     planting a path that becomes a clickable cursor:// URL via the repo
#     badge.
#   - Path must exist and be a directory.
#   - Path must resolve to a git toplevel (i.e. it is actually a worktree
#     or repo root). Prevents pointing focus at a stray folder.

set -eu

if [ "$#" -ne 1 ]; then
  echo "usage: set-focus.sh <absolute-worktree-path>" >&2
  exit 64
fi

WT="$1"

case "$WT" in
  /*) ;;
  *) echo "path must be absolute: $WT" >&2; exit 65 ;;
esac

case "$WT" in
  "$HOME"/*) ;;
  *) echo "path must live under \$HOME: $WT" >&2; exit 65 ;;
esac

if [ ! -d "$WT" ]; then
  echo "directory does not exist: $WT" >&2
  exit 66
fi

# Confirm it really is a git worktree / repo, not just any folder.
TOPLEVEL=$(git -C "$WT" rev-parse --show-toplevel 2>/dev/null || true)
if [ -z "$TOPLEVEL" ]; then
  echo "not a git worktree (git -C $WT rev-parse failed): $WT" >&2
  exit 67
fi

CACHE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.statusline-cache"
mkdir -p "$CACHE_DIR"
printf '%s' "$TOPLEVEL" > "$CACHE_DIR/active-worktree"
echo "focus → $TOPLEVEL" >&2
