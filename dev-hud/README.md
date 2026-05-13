# dev-hud

Always-visible Claude Code HUD showing what you're working on, with clickable links into Linear and Cursor.

```
[RDO-1011 · Add FoldersNavSection molecule] [PR #105] [feat+rdo-1011 *↑2]  [CAVEMAN]
```

## What it shows

| Badge | Color | Clicks to | Source | Refresh |
| --- | --- | --- | --- | --- |
| `RDO-1011 · title` | blue | `linear://<workspace>/issue/<id>` (Linear app) | branch regex + Linear GraphQL `issue.title` | live + 60 min cache |
| `PR #105` | green | cached Linear review URL → GitHub PR URL → Linear issue URL | `gh pr view`, plus `update-review-url.sh` for Linear review | 10 min cache |
| `feat+rdo-1011` (`*↑N`) | yellow | `cursor://file/<absolute-path>` (Cursor) | `git rev-parse --show-toplevel` + `git status` + `rev-list` | live |
| `[CAVEMAN]` | orange | — | delegated to `caveman-statusline.sh` if installed | live |

Hyperlinks use the OSC 8 terminal escape, which renders as clickable text in iTerm2, Terminal.app, kitty, and WezTerm.

## Install

After enabling the plugin, Claude Code detects that `statusLine` is not yet set and emits a setup nudge on session start. Accept the offer, or wire it yourself in `~/.claude/settings.json`:

```json
"statusLine": {
  "type": "command",
  "command": "bash \"/Users/<you>/.claude/plugins/cache/twelvelabs-plugins/dev-hud/<version>/hooks/statusline.sh\""
}
```

## Linear titles (optional)

Drop a Linear personal API token at `~/.claude/linear-token` (mode 600). Generate one at https://linear.app/twelve-labs/settings/api.

```bash
echo 'lin_api_XXXXXXXXXXXX' > ~/.claude/linear-token
chmod 600 ~/.claude/linear-token
```

Without the token the Linear title is skipped silently.

## Helpers — wiring dev-hud into your skills

Beyond the live statusline, dev-hud ships a small set of cache-mutation helpers so other workflows can keep the HUD in sync without writing to the cache directory directly. Every helper validates input, runs in milliseconds, and prints a one-line confirmation to stderr.

| Helper | Purpose | Cross-session reach |
| --- | --- | --- |
| `set-focus.sh <abs-path>` | Pin which worktree the focus-file fallback points at. | **Main-checkout sessions only.** Sessions started inside a worktree carry `workspace.git_worktree` in their stdin payload, which beats the focus file by design (so 3 cmux panes for 3 tickets each stay on their own ticket). |
| `clear-focus.sh` | Drop the pin, returning to the mtime fallback. | Same scope as `set-focus`. |
| `set-title.sh <TICKET> <title>` | Prime the Linear title cache with a known string. | **Any session that resolves to `<TICKET>`** reads `title-<TICKET>`. Works cross-pane as long as you pass the right ticket. |
| `update-review-url.sh <TICKET> <url>` | Cache the Linear review URL so the PR badge deep-links into the in-Linear diff viewer. | Cross-session, keyed by ticket. |
| `invalidate-pr.sh [branch]` | Drop the cached PR number + URL so the next render refetches via `gh pr view`. | Keyed by `sha(repo + branch)` — run inside the worktree whose PR you opened, or pass no arg to nuke everything. |

### Why `set-focus` looks like it does nothing in a watched pane

Focus resolution priority inside `statusline.sh`:

1. `workspace.git_worktree` from Claude Code's stdin payload (per-session, authoritative — set when the session was started inside a worktree).
2. `~/.claude/.statusline-cache/active-worktree` (written by `set-focus.sh`).
3. Most-recently-committed `feat+rdo-*` worktree under `.claude/worktrees/`.

If you run `set-focus.sh feat+rdo-1011` from a main-checkout pane while watching a cmux pane that was started inside `feat+rdo-1028`, the watched pane's badge stays on RDO-1028 — its stdin payload beats the focus file. The focus file only affects sessions that don't already have an authoritative payload (typically the main-checkout pane where you typed `/start` or `/cursor`).

`set-title`, `update-review-url`, and `invalidate-pr` are keyed by ticket or branch — those reach every session that resolves to the same ticket/branch.

All helpers live in `hooks/` and resolve `~/.claude/.statusline-cache/` (override with `$CLAUDE_CONFIG_DIR`). The full path is stable across plugin versions when installed via the cache loader: `${CLAUDE_PLUGIN_ROOT}/hooks/<helper>.sh` from inside a hook, or `~/.claude/plugins/cache/<source>/dev-hud/<version>/hooks/<helper>.sh` from a slash command.

### Wiring recipes

These are the integrations dev-hud was designed for. Drop the snippet into the matching skill or script — every helper is no-op-safe if dev-hud is not installed (the script path simply won't exist, and a guarded call avoids a hard error).

Each recipe says which session the change reaches, so you know what to expect when watching a different pane.

**Ticket bootstrap (`/start`, `new-ticket.sh`)** — after the worktree exists, pin it as the focus. **Effect: the main-checkout pane where you typed `/start` switches over** — the new cmux pane already has stdin authority and doesn't need the focus file.

```bash
HELPER="$HOME/.claude/plugins/cache/twelvelabs-plugins/dev-hud/*/hooks/set-focus.sh"
[ -e $HELPER ] && bash $HELPER "$WT_ABS" || true
```

**Implement (`/implement`)** — after `mcp__linear__get_issue` returns the title, prime the cache; after `mcp__linear__list_diffs` returns the Linear review URL, cache it for the PR badge. **Effect: every session that resolves to the ticket** picks up both on next render.

```bash
bash "${HELPERS}/set-title.sh" RDO-1011 "Add FoldersNavSection molecule"
bash "${HELPERS}/update-review-url.sh" RDO-1011 \
  "https://linear.app/twelve-labs/review/<slug>-<hash>"
```

**Ship (`/ship`)** — after `gh pr create`, invalidate the per-branch PR cache so the badge picks up the new PR number on the next render instead of after the 10-min TTL. **Effect: every session whose toplevel + branch hash matches** refetches via `gh pr view` on next render. Run from inside the worktree the push happened in.

```bash
bash "${HELPERS}/invalidate-pr.sh" "$(git branch --show-current)"
```

**Cursor (`/cursor`)** — after `open -a Cursor <wt-path>`, pin the focus to the worktree the user just opened. **Effect: the main-checkout pane where the user typed `/cursor`** retargets its HUD. The new Cursor window is a separate process and is not affected by Claude Code statusline at all.

```bash
bash "${HELPERS}/set-focus.sh" "<absolute worktree path>"
```

The README has historically claimed `/cursor` did this — as of v0.2.0 the helper exists; wiring it into the skill is a follow-up.

## Focus tracking

When the Claude Code session is rooted at the main checkout (not inside a worktree), dev-hud needs a focus signal to know which ticket to render. Precedence:

1. `workspace.git_worktree` from Claude Code's stdin payload (per-session, authoritative).
2. `~/.claude/.statusline-cache/active-worktree` — absolute path to the focused worktree. Written by `set-focus.sh` (call it from `/start`, `/cursor`, or anywhere that opens a worktree).
3. Most-recently-committed `feat+rdo-*` branch under `.claude/worktrees/`.

## Configuration

Override these in your shell or `settings.json` env:

| Var | Default | Effect |
| --- | --- | --- |
| `STATUSLINE_TICKET_PREFIX` | `[Rr][Dd][Oo]-[0-9]+` | regex used to find a ticket ID in the branch name |
| `LINEAR_TOKEN_FILE` | `~/.claude/linear-token` | path to the Linear personal API token |
| `LINEAR_WORKSPACE` | `twelve-labs` | Linear workspace slug used in `linear://` URLs |
| `STATUSLINE_PR_TTL_MIN` | `10` | PR lookup cache TTL |
| `STATUSLINE_TITLE_TTL_MIN` | `60` | Linear title cache TTL |
| `STATUSLINE_CAVEMAN` | `1` | set `0` to skip caveman badge delegation |
| `STATUSLINE_NO_LINKS` | `0` | set `1` to render plain brackets (no OSC 8 escapes) |
| `STATUSLINE_NO_WORKTREE_FALLBACK` | `0` | set `1` to disable the most-recently-committed worktree fallback |
| `STATUSLINE_DEBUG` | `0` | set `1` to log inputs to `~/.claude/.statusline-cache/debug.log` |

## Failure modes

| Missing | Effect |
| --- | --- |
| `gh` CLI | PR badge omitted |
| `jq` | falls back to `$PWD` when Claude's JSON stdin payload is unavailable |
| Linear token | title cache stub written, no retry until TTL expires |
| Linear API unreachable | empty title cache stub, retries after TTL |
| Caveman plugin | caveman badge omitted, everything else stays |
| OSC 8 unsupported terminal | brackets render plainly, links inert |

## Caches

Live under `~/.claude/.statusline-cache/`. Each row lists the file, what it stores, and the helper that owns the write path (statusline reads them all):

| File | Stores | Writer |
| --- | --- | --- |
| `pr-<hash>` | PR number per `(repo + branch)` hash | statusline (10-min TTL); `invalidate-pr.sh` clears |
| `pr-url-<hash>` | GitHub PR URL per `(repo + branch)` hash | statusline (10-min TTL); `invalidate-pr.sh` clears |
| `title-<TICKET>` | Linear title per ticket | statusline (60-min TTL); `set-title.sh` primes |
| `review-<TICKET>` | Linear review URL per ticket | `update-review-url.sh` |
| `active-worktree` | absolute path to the focused worktree | `set-focus.sh` writes, `clear-focus.sh` removes |

Wipe a single entry to force a refresh: `rm ~/.claude/.statusline-cache/title-RDO-1011`.
