# Plugin Changes — v1.3.0 (sync with MCP server 1.0.0)

This document summarises every change made to bring the plugin in sync with the upstream TwelveLabs MCP server (`twelvelabs-mcp` v1.0.0, SDK `twelvelabs-js` ^1.2.4).

## Default-model policy

Pegasus 1.5 supersedes Pegasus 1.2 for direct-input analysis. The plugin defaults to Pegasus 1.5 everywhere the MCP allows it, and only falls back to Pegasus 1.2 when:

1. The user is analysing an indexed `videoId` (the MCP forces 1.2 here — `modelName="pegasus1.5"` + `videoId` is a hard error).
2. The user explicitly requests 1.2 ("use pegasus 1.2", "legacy model", etc.).

| Command | Default `modelName` |
|---|---|
| `/sync-analyze` with `videoId` | `pegasus1.2` (forced) |
| `/sync-analyze` with `videoUrl` / `assetId` / `base64Video` / local file | **`pegasus1.5`** |
| `/async-analyze` (any input) | **`pegasus1.5`** |
| `/indexes create` | `pegasus1.2` + `marengo3.0` (hardcoded by MCP — indexes use 1.2 for backwards compatibility; Pegasus 1.5 features are reached via the direct-input analyze flows instead) |

---

## Breaking changes

### `/twelvelabs:analyze` slash command renamed to `/twelvelabs:sync-analyze`

To make the sync/async pair symmetric alongside the new `/twelvelabs:async-analyze`, the existing slash command was renamed:

- `commands/analyze.md` → `commands/sync-analyze.md`
- `skills/analyze/` → `skills/sync-analyze/`
- All cross-references in `commands/help.md`, `commands/index-video.md`, `commands/indexes.md`, `commands/search.md`, `commands/videos.md`, and `README.md` updated.
- A thin `commands/analyze.md` shim is kept as a deprecation alias that dispatches to `/twelvelabs:sync-analyze` with a one-line banner, so existing muscle memory still works during the migration window.

Naming note: the slash command uses US spelling (`sync-analyze`) while the underlying MCP tool retains the upstream's British spelling (`sync-analyse-video`). Intentional — kept to match each ecosystem's conventions.

### Asset management split out into `/twelvelabs:assets`

Previously `create-asset` and `delete-asset` were exposed only under `/twelvelabs:entities` (as `upload` and `delete-asset` subcommands), because the upstream API grouped them that way. But assets are general-purpose — image assets are used as entity reference images, AND video assets are used as inputs to `/twelvelabs:async-analyze`. Hiding asset management under `/entities` was confusing UX.

New top-level command:

- `commands/assets.md` (new) + `skills/assets/SKILL.md` (new): `upload <path-or-url>` and `delete <asset-id>` subcommands.

`commands/entities.md` no longer exposes `upload` or `delete-asset` — they live at `/twelvelabs:assets` now. All next-step hints inside `entities.md` (e.g. after creating a collection) now point at `/twelvelabs:assets upload`.

## Bug fixes

### `/twelvelabs:sync-analyze` now accepts URL / asset / local file inputs

The MCP `sync-analyse-video` tool accepts four input sources (`videoId`, `videoUrl`, `assetId`, `base64Video`), but the plugin's `commands/sync-analyze.md` only documented `videoId`. Passing a URL would error with "requires videoId" guidance and (wrongly) redirect users to `/twelvelabs:async-analyze`.

- `commands/sync-analyze.md` and `skills/sync-analyze/SKILL.md`: input-classification step distinguishes URL, asset ID, local file path, and videoId. Local paths are auto-uploaded as assets (same pattern as `/async-analyze`). `modelName` is selected per the default-model policy.

### `commands/search.md` response format

Search results no longer include a "video stream URL" — the MCP `search` tool returns `userMetadata` (per-segment) and pre-signed `thumbnail` URLs (1-hour validity). Updated Step 5 to surface `userMetadata` and per-segment thumbnail hyperlinks (text hyperlink form `[View thumbnail](url)`, NOT markdown image syntax).

## New parameter coverage

### `/sync-analyze` and `/async-analyze` Pegasus 1.5 feature set

Both commands now document the optional parameters the MCP exposes for Pegasus 1.5:

- `modelName` — explicit override
- `promptV2` — structured prompt with `<@name>` references to attached images via a `mediaSources` array (mutually exclusive with `prompt`; Pegasus 1.5 only)
- `temperature`, `maxTokens`
- `jsonSchema` — constrain output to a JSON Schema (Draft 2020-12)
- `startTime` / `endTime` — clip the analysis window to a sub-range (Pegasus 1.5 only)

### `/async-analyze` time-based metadata extraction

Major new capability surfaced in `commands/async-analyze.md`:

- `analysisMode: "time_based_metadata"` — switch from prompt-only output to per-segment structured extraction.
- `segmentDefinitions` — 1-10 definitions, each with `id`, `description`, optional typed `fields`, optional `mediaSources` (reference images), optional `timeRanges`.
- `minSegmentDuration` / `maxSegmentDuration` — auto-segmenting bounds.
- `customId` — caller-supplied tracking ID that round-trips through `get-analyse-task` and `list-analyse-tasks`.

### `/async-analyze list` filtering

The MCP `list-analyse-tasks` tool supports `page`, `pageLimit` (max 50), `status`, `videoUrl`, `assetId`, `analysisMode` filters. Plugin now documents them.

### `/index-video` folder + metadata

`commands/index-video.md` now documents:

- `folderFilePath` — batch-index every `.mp4`/`.mov`/`.avi`/`.mkv`/`.webm` in a local folder; one task per file.
- `userMetadata` — JSON string of key/value pairs attached at index time; surfaces in `search` results.
- `transcription: true` on `get-indexed-asset` — return the audio transcript alongside metadata.

### `/embed` retrieve-by-index path

`commands/embed.md` now exposes the second mode of the `retrieve-video-embeddings` MCP tool: pass `indexId + videoId` to retrieve embeddings of an already-indexed video without starting a new embedding task.

### Pagination + addons in `/indexes` and `/videos`

- `commands/indexes.md`: `list-indexes` `page` parameter and `create-index` `addons` parameter (currently `"thumbnail"`, default-on) are now documented.
- `commands/videos.md`: `list-videos` `page` parameter is now wired through the tool-call code block.

## UX improvements

### `/twelvelabs:async-analyze` accepts local file paths directly

Previously, passing a local file path to `/twelvelabs:async-analyze` would error out and tell the user to go run `/twelvelabs:entities upload` first. This was confusing busywork.

Now `commands/async-analyze.md` detects when the first argument is a local file path (not a URL or asset ID) and runs `create-asset` internally before calling `async-analyse-video`. The created asset ID is surfaced to the user so they know it persists in their account and can reuse or delete it via `/twelvelabs:assets`.

The command's input classification is:
- starts with `http://`/`https://` → use `videoUrl`
- 24-char hex or `asset_*` → use `assetId` directly
- otherwise → treat as local file path, auto-upload, use returned `assetId`

## Fixes

### `analyse-video` tool renamed to `sync-analyse-video`

The MCP server no longer exposes a tool called `analyse-video`. It was split into two tools:
- `sync-analyse-video` — synchronous, returns result inline (Pegasus 1.2 default; also supports 1.5 with extended params)
- `async-analyse-video` — asynchronous, fire-and-forget, returns a `taskId` (Pegasus 1.5 default)

**Files changed:**
- `commands/analyze.md` — updated tool call from `mcp__twelvelabs-mcp__analyse-video` → `mcp__twelvelabs-mcp__sync-analyse-video`; removed defunct `type` parameter from the tool call; added note pointing to `/twelvelabs:async-analyze` for videos over 1 hour.
- `skills/analyze/SKILL.md` — same tool rename; removed `type: "open-ended"` parameter (no longer in API).
- `hooks/hooks.json` — PostToolUse matcher updated from `mcp__twelvelabs-mcp__analyse-video` → `mcp__twelvelabs-mcp__sync-analyse-video`.
- `hooks/post-analyze.py` — updated docstring/comments to reference the new tool name; added fallback `analysis_type = tool_input.get("type") or "sync"` so the cache key is always populated (the new API no longer sends a `type` field in the tool input).

### `create-asset` parameter names changed

The MCP server changed `create-asset` params: `imageUrl` → `url`, `imageFile`/`imageFilePath` → `file`. The new parameter names cover both image and video assets.

**Files changed:**
- `commands/entities.md` — `imageUrl` → `url`, `imageFile` → `file` in the `upload` subcommand instructions.
- `skills/entity-search/SKILL.md` — `imageUrl` → `url`, `imageFilePath` → `file` in Step 3 (Upload Reference Images).

---

## New Features

### `async-analyse-video` + analyse task management

The MCP server now exposes four new tools for async video analysis:
- `async-analyse-video` — start an async analyse task (URL/asset/base64, Pegasus 1.5 default)
- `get-analyse-task` — poll task status and retrieve result
- `list-analyse-tasks` — list tasks with pagination/filtering
- `delete-analyse-task` — delete a completed/failed task

**Files added:**
- `commands/async-analyze.md` — new slash command `/twelvelabs:async-analyze` covering all four tools; supports `<url> [prompt]`, `status [task-id]`, `list`, and `delete <task-id>` subcommands.
- `skills/async-analyze/SKILL.md` — new skill that triggers when the user provides a video URL to analyze or asks about pending analysis tasks.

### `get-indexed-asset` — new preferred indexing status tool

The `start-video-indexing-task` tool was refactored internally: it now uses the new `assets → indexed-assets` API flow and returns an `indexedAssetId` (not a legacy task ID). The new `get-indexed-asset` tool is the preferred way to poll indexing status.

**Files changed:**
- `commands/index-video.md`:
  - Step 6 (Report Result) updated to show `indexId` and `indexedAssetId` from the response and explain how to poll with `get-indexed-asset`.
  - Status Flow Step 4s updated: `get-indexed-asset` (with `indexId` + `indexedAssetId`) is now shown as the preferred status check; `get-video-indexing-tasks` is retained as the legacy fallback for old task IDs.

### `delete-asset` tool

The MCP server now exposes `delete-asset` (params: `assetId`, optional `force`). Assets are used for entity reference images and async-analyse video inputs.

**Files changed:**
- `commands/entities.md` — added `delete-asset` subcommand to the usage block, subcommand table, dispatcher help text, and a full subcommand instructions section (including conflict handling with `force=true`).

---

## Documentation Updates

- `commands/help.md` — added `/twelvelabs:async-analyze` to the command table with description; added full detail section; updated `/twelvelabs:analyze` description to note it is sync/≤1 hour; updated `/twelvelabs:entities` description and usage to include `delete-asset`.
- `.claude-plugin/plugin.json` — version bumped `1.1.0` → `1.2.0`.

---

## Questions / Ambiguities

None. All tool changes were unambiguous from the MCP server source code.
