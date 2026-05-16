#!/bin/bash
# dev-hud — Claude Code HUD with clickable links to Linear and Cursor.
#
# Renders, when applicable:
#   [RDO-1011 · Add FoldersNavSection molecule] [PR #105] [feat+rdo-1011 *↑2]  [CAVEMAN]
#
# Every bracketed badge is an OSC 8 hyperlink in modern terminals (iTerm2,
# Terminal.app, kitty, WezTerm). Click targets:
#   ticket  → https://linear.app/<workspace>/issue/<id>   (opens Linear app)
#   PR      → cached review URL if available, else issue URL
#   repo    → cursor://file/<absolute-worktree-path>      (opens in Cursor)
#
# Review URL cache:
#   The Linear "review mode" URL contains a server-generated hash that the
#   public GraphQL API does not expose. To get a real review URL, populate
#   ~/.claude/.statusline-cache/review-<TICKET> with the URL — Claude can do
#   this after calling mcp__linear__list_diffs (see ./update-review-url.sh).
#
# Pieces:
# - Linear ticket   — RDO-<n> extracted from the current branch name.
# - Linear title    — Linear GraphQL `issue(id).title`, cached 60 min.
#                     Needs $LINEAR_TOKEN_FILE (~/.claude/linear-token, 600).
# - PR number       — `gh pr view`, cached 10 min per (repo + branch).
# - Repo / worktree — basename of `git rev-parse --show-toplevel`.
# - Branch state    — `*` if dirty, `↑N` if ahead of upstream. Live.
# - Caveman badge   — delegated to caveman-statusline.sh if installed.
#
# Configuration via env (override in shell or settings.json):
#   STATUSLINE_TICKET_PREFIX   Regex for ticket IDs. Default [Rr][Dd][Oo]-[0-9]+
#   LINEAR_TOKEN_FILE          Linear personal API token path.
#   LINEAR_WORKSPACE           Linear workspace slug. Default twelve-labs.
#   STATUSLINE_PR_TTL_MIN      PR cache TTL. Default 10.
#   STATUSLINE_TITLE_TTL_MIN   Title cache TTL. Default 60.
#   STATUSLINE_CAVEMAN         Set "0" to skip caveman badge.
#   STATUSLINE_NO_LINKS        Set "1" to render without OSC 8 hyperlinks
#                              (useful if your terminal mangles them).

set -u

CACHE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.statusline-cache"
mkdir -p "$CACHE_DIR" 2>/dev/null

# Debug log — toggle with STATUSLINE_DEBUG=1. Captures inputs to diagnose
# "I don't see badges" cases. Tail with: tail -f ~/.claude/.statusline-cache/debug.log
DEBUG_LOG="$CACHE_DIR/debug.log"
log_debug() {
  [ "${STATUSLINE_DEBUG:-0}" = "1" ] && printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*" >> "$DEBUG_LOG"
}

TICKET_REGEX="${STATUSLINE_TICKET_PREFIX:-[Rr][Dd][Oo]-[0-9]+}"
LINEAR_TOKEN_FILE="${LINEAR_TOKEN_FILE:-${CLAUDE_CONFIG_DIR:-$HOME/.claude}/linear-token}"
LINEAR_WS="${LINEAR_WORKSPACE:-twelve-labs}"
PR_TTL="${STATUSLINE_PR_TTL_MIN:-10}"
TITLE_TTL="${STATUSLINE_TITLE_TTL_MIN:-60}"
NO_LINKS="${STATUSLINE_NO_LINKS:-0}"

# OSC 8 hyperlink helper: emits `\e]8;;URL\aTEXT\e]8;;\a`. BEL terminator
# (\a / \007) is the most widely-compatible string terminator across terminals.
emit_link() {
  local url="$1" text="$2"
  if [ "$NO_LINKS" = "1" ] || [ -z "$url" ]; then
    printf '%s' "$text"
  else
    printf '\033]8;;%s\007%s\033]8;;\007' "$url" "$text"
  fi
}

# --- read Claude Code's stdin payload ---------------------------------------
INPUT=$(cat 2>/dev/null || true)
CWD=""
GIT_WORKTREE=""
PROJECT_DIR=""
if command -v jq >/dev/null 2>&1 && [ -n "$INPUT" ]; then
  CWD=$(printf '%s' "$INPUT" | jq -r '.workspace.current_dir // .cwd // empty' 2>/dev/null)
  # Claude Code marks the session with the worktree's directory name when one
  # was selected at session start — authoritative when present.
  GIT_WORKTREE=$(printf '%s' "$INPUT" | jq -r '.workspace.git_worktree // empty' 2>/dev/null)
  PROJECT_DIR=$(printf '%s' "$INPUT" | jq -r '.workspace.project_dir // empty' 2>/dev/null)
fi
CWD="${CWD:-$PWD}"

# Resolve focus signal in priority order:
#   1. Claude Code's `workspace.git_worktree` (per-session, authoritative)
#   2. Explicit focus file ~/.claude/.statusline-cache/active-worktree
#      (set by `/cursor`, persists across sessions)
#   3. Live cwd (used as-is below)
FOCUS_WT=""
if [ -n "$GIT_WORKTREE" ] && [ -n "$PROJECT_DIR" ] && [ -d "$PROJECT_DIR/.claude/worktrees/$GIT_WORKTREE" ]; then
  FOCUS_WT="$PROJECT_DIR/.claude/worktrees/$GIT_WORKTREE"
fi
if [ -z "$FOCUS_WT" ]; then
  ACTIVE_WT_FILE="$CACHE_DIR/active-worktree"
  if [ -f "$ACTIVE_WT_FILE" ] && [ ! -L "$ACTIVE_WT_FILE" ]; then
    CANDIDATE=$(head -c 1024 "$ACTIVE_WT_FILE" 2>/dev/null | tr -d '\000-\037\n\r')
    # Refuse paths outside the user's home — defensive against an attacker
    # planting an arbitrary path that becomes a clickable cursor:// URL.
    case "$CANDIDATE" in
      "$HOME"/*) [ -d "$CANDIDATE" ] && FOCUS_WT="$CANDIDATE" ;;
    esac
  fi
fi
[ -n "$FOCUS_WT" ] && CWD="$FOCUS_WT"

log_debug "INPUT_CWD=$(printf '%s' "$INPUT" | jq -r '.workspace.current_dir // empty' 2>/dev/null) GIT_WORKTREE=$GIT_WORKTREE FOCUS_WT=$FOCUS_WT FINAL_CWD=$CWD"

# --- git context ------------------------------------------------------------
TOPLEVEL=$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null)
log_debug "TOPLEVEL=$TOPLEVEL"
if [ -n "$TOPLEVEL" ]; then
  BRANCH=$(git -C "$CWD" symbolic-ref --short HEAD 2>/dev/null || true)
  log_debug "BRANCH=$BRANCH"

  TICKET=""
  if [ -n "$BRANCH" ]; then
    TICKET=$(printf '%s' "$BRANCH" | grep -oE "$TICKET_REGEX" | head -n1 | tr '[:lower:]' '[:upper:]')
  fi

  # Worktree fallback: Claude Code sessions are usually rooted at the main
  # checkout, so the live branch is `main` and no ticket matches. The actual
  # focus is whichever worktree the user is iterating on. Pick the most
  # recently touched `.claude/worktrees/feat+rdo-*` and use it as the context.
  # Skip when STATUSLINE_NO_WORKTREE_FALLBACK=1 — useful for users who want the
  # badge to track the literal HEAD branch only.
  if [ -z "$TICKET" ] && [ "${STATUSLINE_NO_WORKTREE_FALLBACK:-0}" != "1" ]; then
    WORKTREE_GLOB="$TOPLEVEL/.claude/worktrees/feat+rdo-*"
    NEWEST_WT=""
    NEWEST_MTIME=0
    # Rank worktrees by the mtime of their branch ref file — that advances on
    # commits, not on stray file writes (build artifacts, editor saves, etc.).
    # Convention: dir `feat+rdo-1011` ↔ branch `feat/rdo-1011`. Fall back to
    # dir mtime if the ref is packed or missing.
    for wt in $WORKTREE_GLOB; do
      [ -d "$wt" ] || continue
      DIR_NAME=$(basename "$wt")
      BR_NAME=$(printf '%s' "$DIR_NAME" | sed 's|^feat+|feat/|')
      REF_FILE="$TOPLEVEL/.git/refs/heads/$BR_NAME"
      if [ -f "$REF_FILE" ]; then
        WT_MTIME=$(stat -f %m "$REF_FILE" 2>/dev/null || stat -c %Y "$REF_FILE" 2>/dev/null || echo 0)
      else
        WT_MTIME=$(stat -f %m "$wt" 2>/dev/null || stat -c %Y "$wt" 2>/dev/null || echo 0)
      fi
      if [ "$WT_MTIME" -gt "$NEWEST_MTIME" ] 2>/dev/null; then
        NEWEST_MTIME=$WT_MTIME
        NEWEST_WT=$wt
      fi
    done
    if [ -n "$NEWEST_WT" ]; then
      # Switch context to that worktree.
      TOPLEVEL=$(git -C "$NEWEST_WT" rev-parse --show-toplevel 2>/dev/null)
      BRANCH=$(git -C "$NEWEST_WT" symbolic-ref --short HEAD 2>/dev/null || true)
      CWD="$NEWEST_WT"
      [ -n "$BRANCH" ] && TICKET=$(printf '%s' "$BRANCH" | grep -oE "$TICKET_REGEX" | head -n1 | tr '[:lower:]' '[:upper:]')
    fi
  fi

  # Linear title — cached, even on failure.
  TITLE=""
  if [ -n "$TICKET" ]; then
    TITLE_FILE="$CACHE_DIR/title-$TICKET"
    if [ ! -f "$TITLE_FILE" ] || [ -n "$(find "$TITLE_FILE" -mmin "+$TITLE_TTL" 2>/dev/null)" ]; then
      if [ -f "$LINEAR_TOKEN_FILE" ] && [ ! -L "$LINEAR_TOKEN_FILE" ] && command -v curl >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
        LINEAR_TOKEN=$(head -c 256 "$LINEAR_TOKEN_FILE" 2>/dev/null | tr -d '\n\r ')
        if [ -n "$LINEAR_TOKEN" ]; then
          RESPONSE=$(curl -sS --max-time 1.5 \
            -H "Authorization: $LINEAR_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"query\":\"query(\$id:String!){issue(id:\$id){title}}\",\"variables\":{\"id\":\"$TICKET\"}}" \
            https://api.linear.app/graphql 2>/dev/null || true)
          FETCHED=$(printf '%s' "$RESPONSE" | jq -r '.data.issue.title // empty' 2>/dev/null)
          FETCHED=$(printf '%s' "$FETCHED" | tr -d '\000-\037' | head -c 200)
          printf '%s' "$FETCHED" > "$TITLE_FILE"
        else
          : > "$TITLE_FILE"
        fi
      else
        : > "$TITLE_FILE"
      fi
    fi
    if [ -f "$TITLE_FILE" ]; then
      TITLE=$(head -c 200 "$TITLE_FILE" 2>/dev/null)
      if [ ${#TITLE} -gt 48 ]; then
        TITLE="${TITLE:0:45}…"
      fi
    fi
  fi

  # PR number + URL, cached.
  PR_DISPLAY=""
  PR_GH_URL=""
  if [ -n "$BRANCH" ] && command -v gh >/dev/null 2>&1; then
    KEY=$(printf '%s\n%s' "$TOPLEVEL" "$BRANCH" | shasum 2>/dev/null | cut -c1-12)
    if [ -n "$KEY" ]; then
      PR_FILE="$CACHE_DIR/pr-$KEY"
      PR_URL_FILE="$CACHE_DIR/pr-url-$KEY"
      if [ ! -f "$PR_FILE" ] || [ -n "$(find "$PR_FILE" -mmin "+$PR_TTL" 2>/dev/null)" ]; then
        PR_JSON=$(cd "$TOPLEVEL" && gh pr view "$BRANCH" --json number,url 2>/dev/null || true)
        if [ -n "$PR_JSON" ] && command -v jq >/dev/null 2>&1; then
          PR_NUM=$(printf '%s' "$PR_JSON" | jq -r '.number // empty' 2>/dev/null)
          PR_URL=$(printf '%s' "$PR_JSON" | jq -r '.url // empty' 2>/dev/null)
        else
          PR_NUM=""
          PR_URL=""
        fi
        printf '%s' "${PR_NUM:-}" > "$PR_FILE"
        printf '%s' "${PR_URL:-}" > "$PR_URL_FILE"
      fi
      PR_NUM=$(head -c 16 "$PR_FILE" 2>/dev/null | tr -cd '0-9')
      [ -n "$PR_NUM" ] && PR_DISPLAY="PR #$PR_NUM"
      if [ -f "$PR_URL_FILE" ]; then
        PR_GH_URL=$(head -c 512 "$PR_URL_FILE" 2>/dev/null | tr -d '\000-\037\n\r')
      fi
    fi
  fi

  REPO=$(basename "$TOPLEVEL")

  # Live branch state.
  DIRTY=""
  PORCELAIN=$(git -C "$CWD" status --porcelain -uno 2>/dev/null | head -c 1)
  if [ -n "$PORCELAIN" ]; then
    DIRTY="*"
  else
    UNTRACKED=$(git -C "$CWD" ls-files --others --exclude-standard 2>/dev/null | head -1)
    [ -n "$UNTRACKED" ] && DIRTY="*"
  fi
  AHEAD=""
  AHEAD_N=$(git -C "$CWD" rev-list --count '@{upstream}..HEAD' 2>/dev/null || true)
  [ -n "$AHEAD_N" ] && [ "$AHEAD_N" -gt 0 ] 2>/dev/null && AHEAD="↑$AHEAD_N"
  STATE="${DIRTY}${AHEAD}"

  # --- link targets ---------------------------------------------------------
  TICKET_URL=""
  PR_URL=""
  WORKTREE_URL=""

  if [ -n "$TICKET" ] && [ -n "$LINEAR_WS" ]; then
    # Use the linear:// scheme so clicks go straight to the Linear desktop app
    # without depending on a system-wide `linear.app` URL handler.
    TICKET_URL="linear://$LINEAR_WS/issue/$TICKET"
  fi

  # PR URL precedence (highest first):
  #   1. Cached Linear review URL (populated via update-review-url.sh by
  #      Claude after `mcp__linear__list_diffs`). Opens Linear in review mode.
  #   2. GitHub PR URL from `gh pr view` (always reachable).
  #   3. Linear issue URL (last-resort so the badge stays clickable).
  if [ -n "$TICKET" ]; then
    REVIEW_FILE="$CACHE_DIR/review-$TICKET"
    if [ -f "$REVIEW_FILE" ] && [ ! -L "$REVIEW_FILE" ]; then
      CACHED_URL=$(head -c 512 "$REVIEW_FILE" 2>/dev/null | tr -d '\000-\037\n\r')
      # Normalize https://linear.app/... → linear:// so the click opens the
      # desktop app directly, matching the ticket badge's scheme.
      case "$CACHED_URL" in
        https://linear.app/*) CACHED_URL="linear://${CACHED_URL#https://linear.app/}" ;;
      esac
      [ -n "$CACHED_URL" ] && PR_URL="$CACHED_URL"
    fi
  fi
  [ -z "$PR_URL" ] && [ -n "$PR_GH_URL" ] && PR_URL="$PR_GH_URL"
  [ -z "$PR_URL" ] && [ -n "$TICKET_URL" ] && PR_URL="$TICKET_URL"

  WORKTREE_URL="cursor://file$TOPLEVEL"

  # --- render with hyperlinks + colors -------------------------------------
  # ANSI palette:
  #   38;5;39  bright blue — ticket + title
  #   38;5;42  green       — PR
  #   38;5;220 yellow      — repo / worktree
  #   38;5;208 orange      — branch state
  if [ -n "$TICKET" ]; then
    if [ -n "$TITLE" ]; then
      LABEL=$(printf '\033[38;5;39m[%s · %s]\033[0m' "$TICKET" "$TITLE")
    else
      LABEL=$(printf '\033[38;5;39m[%s]\033[0m' "$TICKET")
    fi
    emit_link "$TICKET_URL" "$LABEL"
    printf ' '
  fi
  if [ -n "$PR_DISPLAY" ]; then
    LABEL=$(printf '\033[38;5;42m[%s]\033[0m' "$PR_DISPLAY")
    emit_link "$PR_URL" "$LABEL"
    printf ' '
  fi
  if [ -n "$REPO" ]; then
    if [ -n "$STATE" ]; then
      LABEL=$(printf '\033[38;5;220m[%s \033[38;5;208m%s\033[38;5;220m]\033[0m' "$REPO" "$STATE")
    else
      LABEL=$(printf '\033[38;5;220m[%s]\033[0m' "$REPO")
    fi
    emit_link "$WORKTREE_URL" "$LABEL"
    printf ' '
  fi
fi

# --- optional caveman delegation -------------------------------------------
if [ "${STATUSLINE_CAVEMAN:-1}" != "0" ]; then
  CAVEMAN=""
  STANDALONE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hooks/caveman-statusline.sh"
  [ -f "$STANDALONE" ] && CAVEMAN="$STANDALONE"
  if [ -z "$CAVEMAN" ]; then
    for candidate in "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/caveman/caveman/*/hooks/caveman-statusline.sh; do
      [ -f "$candidate" ] && CAVEMAN="$candidate" && break
    done
  fi
  [ -n "$CAVEMAN" ] && bash "$CAVEMAN"
fi
