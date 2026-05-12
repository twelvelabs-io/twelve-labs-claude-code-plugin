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

## Linear review URL (optional)

The PR badge prefers a cached Linear review URL when present. The slug is server-generated and isn't exposed by Linear's public GraphQL, so the plugin can't derive it. Claude (or you) can populate the cache after `mcp__linear__list_diffs`:

```bash
bash hooks/update-review-url.sh RDO-1011 \
  "https://linear.app/twelve-labs/review/<slug>-<hash>"
```

Without the cache, the PR badge falls back to the GitHub URL.

## Focus tracking

When the Claude Code session is rooted at the main checkout (not inside a worktree), dev-hud needs a focus signal to know which ticket to render. Precedence:

1. `workspace.git_worktree` from Claude Code's stdin payload (per-session, authoritative).
2. `~/.claude/.statusline-cache/active-worktree` — absolute path to the focused worktree. Written by `/cursor` and any other workflow that opens a worktree.
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

Live under `~/.claude/.statusline-cache/`:

- `pr-<hash>` — PR number per `(repo + branch)` hash
- `pr-url-<hash>` — GitHub PR URL per `(repo + branch)` hash
- `title-<TICKET>` — Linear title per ticket
- `review-<TICKET>` — Linear review URL per ticket (populated by `update-review-url.sh`)
- `active-worktree` — absolute path to the focused worktree

Wipe a single entry to force a refresh: `rm ~/.claude/.statusline-cache/title-RDO-1011`.
