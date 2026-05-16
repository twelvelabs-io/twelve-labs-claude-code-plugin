#!/bin/bash
# update-review-url — write a Linear review URL into the statusline cache.
#
# The statusline PR badge links to a Linear "review" URL (the in-app diff view)
# when one is cached. Those URLs contain a server-generated hash that isn't
# exposed by Linear's public GraphQL API, so they can't be derived from the
# ticket ID alone. Claude can fetch the URL via the Linear MCP
# (`mcp__linear__list_diffs`) and call this script to populate the cache.
#
# Usage:
#   update-review-url.sh <TICKET> <URL>
#
# Example:
#   update-review-url.sh RDO-1011 \
#     "https://linear.app/twelve-labs/review/feat-folders-rdo-1011-aec12b029ef7"

set -eu

if [ "$#" -ne 2 ]; then
  echo "usage: update-review-url.sh <TICKET> <URL>" >&2
  exit 64
fi

TICKET="$1"
URL="$2"

# Validate ticket — kebab-uppercase. Refuse anything that could escape the
# cache path (e.g. ../, slashes, control bytes).
case "$TICKET" in
  *[!A-Z0-9-]*) echo "invalid ticket: $TICKET" >&2; exit 65 ;;
esac

# Require an https:// Linear URL — refuses arbitrary URLs to keep the cache
# strictly purposed (clicking a malicious URL in your statusline would be bad).
case "$URL" in
  https://linear.app/*/review/*) ;;
  linear://*/review/*) ;;
  *) echo "expected https://linear.app/<workspace>/review/<slug> or linear://<workspace>/review/<slug>, got: $URL" >&2; exit 66 ;;
esac

CACHE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.statusline-cache"
mkdir -p "$CACHE_DIR"
printf '%s' "$URL" > "$CACHE_DIR/review-$TICKET"
echo "cached review URL for $TICKET" >&2
