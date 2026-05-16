#!/bin/bash
# set-title — prime the Linear title cache without hitting the GraphQL API.
#
# When a workflow already has the Linear title in hand (e.g. /implement just
# called mcp__linear__get_issue), call this to write it into the cache. The
# statusline will use it immediately and the 60-min TTL keeps it fresh until
# the next real refresh. Saves the statusline a curl on the next render and
# is the only path that works when LINEAR_TOKEN_FILE is not configured.
#
# Usage:
#   set-title.sh <TICKET> <title>
#
# Example:
#   set-title.sh RDO-1011 "Add FoldersNavSection molecule"

set -eu

if [ "$#" -ne 2 ]; then
  echo "usage: set-title.sh <TICKET> <title>" >&2
  exit 64
fi

# Normalize to uppercase up front — statusline.sh uppercases the ticket
# before looking up the cache key, so a lowercase write would land in a
# different file than the read.
TICKET=$(printf '%s' "$1" | tr '[:lower:]' '[:upper:]')
TITLE="$2"

# Refuse path-traversal bait and anything that would escape the cache
# filename. After uppercasing, the only remaining "bad" chars are slashes,
# dots, spaces, etc.
case "$TICKET" in
  *[!A-Z0-9-]*) echo "invalid ticket: $1" >&2; exit 65 ;;
esac

# Strip control bytes and clamp length — the statusline already truncates to
# 48 chars for display, but the cache file should stay small.
SAFE=$(printf '%s' "$TITLE" | tr -d '\000-\037' | head -c 200)
if [ -z "$SAFE" ]; then
  echo "title is empty after sanitization" >&2
  exit 66
fi

CACHE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.statusline-cache"
mkdir -p "$CACHE_DIR"
printf '%s' "$SAFE" > "$CACHE_DIR/title-$TICKET"
echo "cached title for $TICKET" >&2
