---
name: async-analyze
description: Asynchronously analyze a video from a URL, local file, asset ID, or base64 — no prior indexing required
disable-model-invocation: true
argument-hint: "<url-or-path-or-asset-id> [prompt] | status [task-id] | list | delete <task-id>"
---

# /twelvelabs:async-analyze - Async Video Analysis

Asynchronously analyse a video using Pegasus 1.5 (default). Accepts a direct URL, a local file path (auto-uploaded as an asset), a previously uploaded asset ID, or base64 data — no prior indexing required. Handles videos up to 2 hours. Returns a task ID immediately; poll with `status` to retrieve the result.

Use this when:
- You have a video URL, local file, or asset but no indexed `videoId`
- The video is over 1 hour long (sync analyze is capped at 1 hour)
- You want structured time-based metadata segmentation
- You want multimodal prompting with reference images

For already-indexed videos under 1 hour, `/twelvelabs:sync-analyze` is faster.

## Usage

```
/twelvelabs:async-analyze <url-or-path-or-asset-id>
/twelvelabs:async-analyze <url-or-path-or-asset-id> "<prompt>"
/twelvelabs:async-analyze status [task-id]
/twelvelabs:async-analyze list
/twelvelabs:async-analyze delete <task-id>
```

**User provided:** `$ARGUMENTS`

## Arguments

- First positional — one of:
  - Direct http(s) URL to a raw media file (YouTube/Drive/Dropbox share links not accepted)
  - Absolute or relative local path to a video file (this command will upload it as an asset for you)
  - A previously uploaded asset ID (24-char hex string starting with a digit)
- `prompt` - Optional: natural-language question or instruction (max 2000 tokens). Drives general analysis. Cannot be combined with `analysisMode: "time_based_metadata"`.
- `status` - Check task status. Optionally provide a task ID.
- `list` - List recent async analyse tasks (supports filters — see List Flow).
- `delete` - Delete a task by ID.

### Optional advanced parameters (when the user asks for them)

| Param | Purpose |
|---|---|
| `modelName` | `"pegasus1.5"` (default) or `"pegasus1.2"` (legacy, deprecated). Set 1.2 only if the user explicitly requests it. |
| `promptV2` | Structured prompt with `<@name>` references to attached images (Pegasus 1.5 only). Mutually exclusive with `prompt`. Shape: `{ inputText, mediaSources: [{ name, mediaType: "image", url\|assetId\|base64String }] }`. Up to 4 mediaSources. |
| `temperature` | 0-1, default 0.2 |
| `maxTokens` | Pegasus 1.2: 1-4096. Pegasus 1.5: 2048-32768 (default 32768). |
| `jsonSchema` | JSON Schema (Draft 2020-12) — constrain general-mode output to structured JSON. Cannot combine with `segmentDefinitions`. |
| `startTime` / `endTime` | Clip the analysis window (Pegasus 1.5 only). `end - start ≥ 4`. Mutually exclusive with `segmentDefinition.timeRanges`. |
| `analysisMode` | `"time_based_metadata"` — switches output to per-segment structured extraction. Requires `segmentDefinitions`. Pegasus 1.5 only. |
| `segmentDefinitions` | 1-10 segment definitions; each has `id`, `description`, optional `fields` (typed schema), optional `mediaSources` (up to 4 reference images), optional `timeRanges`. |
| `minSegmentDuration` / `maxSegmentDuration` | Constraints on auto-extracted segment lengths. `time_based_metadata` only. Mutually exclusive with per-definition `timeRanges`. |
| `customId` | Caller-supplied tracking ID (1-64 chars, alphanumeric + `-_`). Round-trips through `get-analyse-task` and `list-analyse-tasks`. |

## Examples

### Start Async Analysis
```
/twelvelabs:async-analyze https://example.com/video.mp4
/twelvelabs:async-analyze /Users/me/clips/keynote.mp4 "Summarize the key topics"
/twelvelabs:async-analyze asset_6a04abc... "What is shown?"
/twelvelabs:async-analyze https://example.com/video.mp4 "List all action items from this meeting"
```

### Check Status
```
/twelvelabs:async-analyze status
/twelvelabs:async-analyze status abc123-task-id
```

### List Tasks
```
/twelvelabs:async-analyze list
```

### Delete a Task
```
/twelvelabs:async-analyze delete abc123-task-id
```

## Instructions for Claude

When the user invokes `/twelvelabs:async-analyze`, parse `$ARGUMENTS`.

If `$ARGUMENTS` is empty:
```
Please provide a video URL, or use:
  status [task-id]   — check task status
  list               — list recent tasks
  delete <task-id>   — delete a task
```

Check the first token of `$ARGUMENTS`:
- `status` → **Status Flow**
- `list` → **List Flow**
- `delete` → **Delete Flow**
- Anything else → **Analyse Flow**

---

## Analyse Flow

### Step 1: Parse Input

Extract from `$ARGUMENTS`:
- First token: a URL, local file path, or asset ID
- Remaining text: optional prompt (strip surrounding quotes if present)

Classify the first token:
- **URL**: starts with `http://` or `https://`
- **Asset ID**: matches `^[a-f0-9]{24}$` (24 hex chars, no dots/slashes) or starts with `asset_`
- **Local file**: everything else — resolve to an absolute path; if the file does not exist, error out:
  ```
  Cannot find a video file at: <path>
  Provide a direct http(s) URL, an absolute path to an existing video file, or an asset ID.
  YouTube/Drive/Dropbox share links are not accepted.
  ```

### Step 2: Build Default Prompt

If no prompt provided, use:
`"Provide a comprehensive summary of this video including key topics, main points, and important moments."`

### Step 3a: If Local File, Upload as Asset First

For a local file path, upload it before starting analysis:

```
Tool: mcp__twelvelabs-mcp__create-asset
Parameters:
  file: "<absolute-path>"
```

Capture the returned `assetId`. Surface it to the user so they know an asset was created:

```
Uploaded <path> as asset <assetId>. Starting analysis…
(Reuse this asset with `/twelvelabs:async-analyze <assetId> "<prompt>"`, or delete with
 `/twelvelabs:assets delete <assetId>`.)
```

### Step 3b: Start Async Analysis Task

Use the input parameter that matches the input type. Default `modelName` to `pegasus1.5` unless the user explicitly asked for `pegasus1.2`.

For a URL:
```
Tool: mcp__twelvelabs-mcp__async-analyse-video
Parameters:
  videoUrl: "<url>"
  modelName: "pegasus1.5"
  prompt: "<prompt>"
```

For an asset ID (either user-provided or just uploaded in Step 3a):
```
Tool: mcp__twelvelabs-mcp__async-analyse-video
Parameters:
  assetId: "<asset-id>"
  modelName: "pegasus1.5"
  prompt: "<prompt>"
```

#### Time-based metadata extraction

When the user asks for structured per-segment extraction (e.g. "find all the highlights and tag each one", "extract every product mention with start/end times"), switch modes:

```
Tool: mcp__twelvelabs-mcp__async-analyse-video
Parameters:
  videoUrl: "<url>"                    # or assetId / base64Video
  modelName: "pegasus1.5"
  analysisMode: "time_based_metadata"
  segmentDefinitions:
    - id: "highlight"
      description: "A notable moment in the video"
      fields:
        - { name: "summary", type: "string", description: "What happened" }
        - { name: "importance", type: "integer", description: "1-5" }
      # Optional: mediaSources for reference images
      # Optional: timeRanges to restrict extraction to specific windows
  # Optional: minSegmentDuration / maxSegmentDuration (auto-segmenting bounds)
```

Drop `prompt` and `promptV2` in this mode — the per-segment `description` + `fields` drive the output.

#### Structured JSON output (general mode)

When the user wants JSON-shaped output (not per-segment): add `jsonSchema` instead of `analysisMode`. Mutually exclusive with `segmentDefinitions`.

#### Multimodal prompt with reference images

When the user wants the model to compare the video against attached images: use `promptV2`.

```
promptV2:
  inputText: "Find every shot that looks like <@product-shot> with the lighting of <@reference-light>."
  mediaSources:
    - { name: "product-shot", mediaType: "image", url: "https://..." }      # or assetId / base64String
    - { name: "reference-light", mediaType: "image", assetId: "asset_..." }
```

`promptV2` requires `pegasus1.5` and is mutually exclusive with `prompt`.

### Step 4: Report Result

On success:
```
Async analysis started!

Task ID: <task_id>
Model: pegasus1.5

Analysis runs in the background. Use `/twelvelabs:async-analyze status <task_id>` to poll for results.
Processing typically takes 30 seconds to a few minutes depending on video length.
```

On failure: Report the error message from the API.

---

## Status Flow

### Step 1: Determine What to Check

If a task ID was provided after `status`: check that specific task.
If no task ID: list recent tasks instead (go to List Flow).

### Step 2: Call the MCP Tool

```
Tool: mcp__twelvelabs-mcp__get-analyse-task
Parameters:
  taskId: "<task-id>"
```

### Step 3: Display Results

**If status is `ready`**:
```
Analysis Complete!

Task ID: <task_id>
Status: ready

--- Result ---
<result.data>
```

**If status is `failed`**:
```
Analysis Failed

Task ID: <task_id>
Error: <error details>
```

**If status is `processing`, `pending`, or `queued`**:
```
Analysis In Progress

Task ID: <task_id>
Status: <status>

Still processing. Check again in 10–30 seconds with:
  /twelvelabs:async-analyze status <task_id>
```

---

## List Flow

The MCP `list-analyse-tasks` tool supports filtering and pagination. Add the optional parameters when the user requests them.

```
Tool: mcp__twelvelabs-mcp__list-analyse-tasks
Parameters: (none = newest first, default page size 10)
```

Optional parameters (combine as needed based on user intent):

- `page` (integer, default 1)
- `pageLimit` (integer, max 50, default 10)
- `status` — one of `queued`, `pending`, `processing`, `ready`, `failed`
- `videoUrl` — filter by exact video source URL
- `assetId` — filter by video source asset ID
- `analysisMode` — `"general"` or `"time_based_metadata"`

Example: "show me only failed time-based-metadata tasks from the last batch" →

```
Tool: mcp__twelvelabs-mcp__list-analyse-tasks
Parameters:
  status: "failed"
  analysisMode: "time_based_metadata"
  pageLimit: 50
```

Display a table:
```
Recent Async Analyse Tasks

| Task ID | Status | Created |
|---------|--------|---------|
| <id1>   | ready  | <time1> |
| <id2>   | processing | <time2> |

Use `/twelvelabs:async-analyze status <task-id>` to retrieve a result.
```

If no tasks found:
```
No async analyse tasks found.

Start one with: /twelvelabs:async-analyze <video-url>
```

---

## Delete Flow

Extract the task ID from `$ARGUMENTS` (everything after `delete`).

If no task ID:
```
Usage: /twelvelabs:async-analyze delete <task-id>
```

Warn the user: "This will permanently delete the analyse task and its result. Continue?"

```
Tool: mcp__twelvelabs-mcp__delete-analyse-task
Parameters:
  taskId: "<task-id>"
```

On success: "Analyse task `<task-id>` deleted."
On conflict (task still processing): Report that in-progress tasks cannot be deleted — wait for completion.

---

## Important Notes

- **No indexing required**: `async-analyse-video` accepts a URL or asset directly
- **Local files are auto-uploaded**: when given a local path, this command runs `create-asset` for you and uses the resulting asset ID. The asset persists in your account until you delete it with `/twelvelabs:assets delete <id>`.
- **Video URL must be a direct link**: Share links from YouTube/Drive/Dropbox are rejected; use direct http(s) URLs
- **Fire-and-forget**: The tool returns immediately with a task ID — poll with `status`
- **Model**: Uses Pegasus 1.5 by default (supports videos up to 2 hours)
- **Sync vs Async**: For indexed videos under 1 hour, `/twelvelabs:sync-analyze` is faster

## Related Commands

- `/twelvelabs:sync-analyze` - Synchronously analyze an indexed video (faster for short indexed videos)
- `/twelvelabs:index-video` - Index a video for search and analysis
- `/twelvelabs:assets` - Manage asset uploads and deletions directly
