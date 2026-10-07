# Plugin Changes — v1.4.0 (sync with MCP server 1.1.0)

This section covers the changes that bring the plugin in sync with `twelvelabs-mcp` v1.1.0. TwelveLabs removed Pegasus 1.2 on 2026-08-18; MCP 1.1.0 follows that removal.

## Default-model policy (supersedes the v1.3.0 policy below)

Pegasus 1.6 is the default for all analysis. Pegasus 1.5 is still selectable when the user asks for it. Pegasus 1.2 no longer exists, so every "force pegasus1.2" / "legacy 1.2" instruction is gone.

| Command | Default `modelName` |
|---|---|
| `/sync-analyze` (any input, including `videoId`) | **`pegasus1.6`** |
| `/async-analyze` (any input) | **`pegasus1.6`** |
| `/indexes create` | `marengo3.0` only (no model choice) |

Both models support `promptV2`, `startTime`/`endTime`, `jsonSchema`, and `time_based_metadata`. The old "Pegasus 1.5 only" caveats and the 1.2 `maxTokens` range were removed from the docs.

## Indexed videos: `videoId` → `asset_id`

`sync-analyse-video` now accepts `videoId` on any model. The server sends it to TwelveLabs as `video.asset_id`, and takes a new optional `indexId` to look up the asset ID for videos indexed before assets existed.

- `commands/sync-analyze.md`, `skills/sync-analyze/SKILL.md`: when analysing an indexed `videoId`, pass the `indexId` it came from whenever it's known (search results, the index that was listed, or the default index). The "videoId is not accepted with pegasus1.5" error guidance is replaced with "retry with `indexId`".
- Indexed-video analysis now has the full feature set; it is no longer described as legacy.

## Indexes are Marengo 3.0 only

`create-index` always creates a Marengo 3.0 (search/embedding) index. Its `models` param is deprecated: `"generative"` is accepted but ignored, and the response adds a note. `list-indexes` labels each model and includes the raw `modelName`.

- `commands/indexes.md`: removed the `pegasus` model choice and the `[model]` argument; `create-index` is called without `models`. Explains that analysis doesn't need an index.
- `commands/help.md`, `skills/list/SKILL.md`, `README.md`: same — no more `generative` / Pegasus index option; index listings show `modelName`.

## Async tasks: `canceled` + `cancel-analyse-task`

- `get-analyse-task` treats `ready`, `failed`, and `canceled` as final. The plugin now stops polling on `canceled` and tells the user the task produced no result.
- `list-analyse-tasks` accepts `status: "canceled"`; the docs list it.
- New MCP tool `cancel-analyse-task` (`taskId`). Exposed as `/twelvelabs:async-analyze cancel <task-id>`, mentioned after a task starts, while it's still running, and when delete fails because the task is still processing. Listed in `commands/help.md` and `README.md`.

## Other fixes in this release

- **Copilot CLI `argument-hint` fix** ([issue #4](https://github.com/twelvelabs-io/twelve-labs-claude-code-plugin/issues/4) / [PR #5](https://github.com/twelvelabs-io/twelve-labs-claude-code-plugin/pull/5)): `argument-hint` frontmatter values are quoted so YAML parses them as strings. GitHub Copilot CLI ≥ 1.0.65 silently dropped commands whose hint was a bare `[...]` (parsed as an array).
- **Windows hooks fix** ([issue #6](https://github.com/twelvelabs-io/twelve-labs-claude-code-plugin/issues/6)): all six hooks crashed on Windows because `.twelvelabs/config_helper.py` imported the Unix-only `fcntl` module. Hooks now run on Windows.

## Version

`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` bumped to `1.4.0`.

---

# Plugin Changes — v1.3.0 (sync with MCP server 1.0.0)

> **History.** Superseded by v1.4.0 above. Pegasus 1.2 was removed by TwelveLabs on 2026-08-18; the model policy and index notes in this section no longer apply.

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
