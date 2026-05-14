---
name: async-analyze
description: Asynchronously analyze a video — by URL, local file path (auto-uploaded), asset ID, or base64 — no prior indexing required. Use for URL inputs, videos over 1 hour, time-based metadata extraction, multimodal prompting with reference images, structured JSON output, or when the user asks to check/list/delete async analysis tasks.
---

# Async Video Analysis

Asynchronously analyse a video using Pegasus 1.5 (default). Accepts a direct http(s) URL, a local file path (auto-uploaded as an asset), a previously uploaded asset ID, or base64 data — no prior indexing required. Handles videos up to 2 hours. Returns a task ID immediately; poll with `get-analyse-task` for the result.

## When to Use This Skill

Use this skill when the user:

- Provides a video URL or local file path they want analysed
- Has a video over 1 hour long (sync analyze caps at 1 hour)
- Wants **time-based metadata extraction** — structured per-segment output (e.g. "find every highlight and tag each one with description+importance")
- Wants **multimodal prompting** with reference images (`promptV2` + `mediaSources`)
- Wants **structured JSON output** (`jsonSchema`)
- Asks about a pending async analysis task ("is my analysis done?")
- Asks to check, list, filter, or delete async analysis tasks

For short, prompt-only analysis of an already-indexed video, use `sync-analyze` instead — it returns inline.

## Model Default

`pegasus1.5` for everything. Only set `pegasus1.2` when the user explicitly asks for legacy mode.

## Instructions

### Starting Async Analysis

#### Step 1: Classify the Input

- `http(s)://...` URL → `videoUrl`
- 24-char hex or `asset_*` → `assetId`
- Local file path → resolve absolute; verify exists; **auto-upload** via `create-asset`:
  ```
  Tool: mcp__twelvelabs-mcp__create-asset
  Parameters:
    file: "<absolute-path>"
  ```
  Surface the returned `assetId` to the user — they can reuse or delete it via `/twelvelabs:assets`. Then continue as `assetId`.

If a URL is given that's a YouTube/Drive/Dropbox **share link**, refuse — the MCP only accepts direct http(s) links to raw media.

#### Step 2: Build the Prompt

Use the user's question/instruction as `prompt`. Default:
`"Provide a comprehensive summary of this video including key topics, main points, and important moments."`

#### Step 3: Start the Task

Exactly one source (`videoUrl` / `assetId` / `base64Video`), `modelName: "pegasus1.5"`, plus `prompt`:

```
Tool: mcp__twelvelabs-mcp__async-analyse-video
Parameters:
  <videoUrl | assetId | base64Video>: "..."
  modelName: "pegasus1.5"
  prompt: "..."
```

#### Step 4: Advanced Capabilities

Add these when the user's intent matches.

**Time-based metadata extraction** — the user wants structured per-segment output:

```
analysisMode: "time_based_metadata"
segmentDefinitions:
  - id: "highlight"
    description: "A notable moment in the video"
    fields:
      - { name: "summary", type: "string", description: "What happened" }
      - { name: "importance", type: "integer", description: "1-5" }
    # Optional: mediaSources (up to 4 reference images per definition)
    # Optional: timeRanges (restrict extraction to specific [start,end] windows)
# Optional: minSegmentDuration / maxSegmentDuration (auto-segmenting bounds)
```

Don't set `prompt` or `promptV2` in this mode — the per-segment `description` + `fields` drive the output. Pegasus 1.5 only.

**Structured JSON output** (general mode) — the user wants JSON, not per-segment:

```
jsonSchema: { ...Draft 2020-12 schema... }
```

Mutually exclusive with `segmentDefinitions`.

**Multimodal prompting with reference images** — the user wants the model to compare the video against images:

```
promptV2:
  inputText: "Find every shot that looks like <@product> with the lighting of <@light-ref>."
  mediaSources:
    - { name: "product", mediaType: "image", url: "https://..." }      # or assetId / base64String
    - { name: "light-ref", mediaType: "image", assetId: "asset_..." }
```

Mutually exclusive with `prompt`. Requires Pegasus 1.5.

**Clip windowing** — restrict analysis to a sub-range (Pegasus 1.5 only):

```
startTime: 60
endTime: 180
```

`end - start ≥ 4`. Mutually exclusive with `segmentDefinition.timeRanges`.

**Other knobs**:

- `temperature` (0-1, default 0.2)
- `maxTokens` (Pegasus 1.5: 2048-32768, default 32768)
- `customId` (1-64 chars, alphanumeric+`-_`; round-trips through `get-analyse-task` / `list-analyse-tasks` — useful for caller-side correlation)

#### Step 5: Report to User

```
Async analysis started!

Task ID: <task_id>
Model: pegasus1.5
<customId surfaced if set>

Polling with: /twelvelabs:async-analyze status <task_id>
(typical wall time: 30s-several minutes; 2-hour videos can take ~10 min)
```

---

### Checking Analysis Status

User asks "is my analysis done?" / "check status of X":

```
Tool: mcp__twelvelabs-mcp__get-analyse-task
Parameters:
  taskId: "<task-id>"
```

The MCP returns plain text "Task <id> is READY." with the result below when done, "Task <id> is FAILED." with error info on failure, or "Task <id> is PROCESSING/QUEUED/PENDING." with a "poll again in 5-10s" hint while running. Watch for the substring "is READY"/"is FAILED" to decide; don't try to JSON-parse the response.

If the task is `ready` and the `result.data` is JSON (from `jsonSchema`) or a per-segment object map (from `time_based_metadata`), the response carries it as a string — parse if needed for display.

If `finishReason=length` is present, warn the user that the output may be truncated and that any JSON output might fail to parse.

---

### Listing Tasks (with filters)

The MCP `list-analyse-tasks` tool supports:

- `page` (default 1)
- `pageLimit` (max 50, default 10)
- `status` — `queued` | `pending` | `processing` | `ready` | `failed`
- `videoUrl` — exact match on the source URL
- `assetId` — exact match on the source asset ID
- `analysisMode` — `general` | `time_based_metadata`

Examples:

- "Show all failed tasks" → `status: "failed"`
- "Show segmentation tasks from URL X" → `videoUrl: "X"`, `analysisMode: "time_based_metadata"`
- "Latest 50 tasks" → `pageLimit: 50`

Default (no filter): newest first, 10 per page.

---

### Deleting a Task

```
Tool: mcp__twelvelabs-mcp__delete-analyse-task
Parameters:
  taskId: "<task-id>"
```

The MCP returns a 409 if the task is still processing — surface that as "still processing, wait for it to finish before deleting".

## Example Interactions

**"Analyze https://nasa.gov/video.mp4 and tell me what's shown"**
→ `async-analyse-video` with `videoUrl` + default prompt → poll status → report result.

**"Analyze /Users/me/clip.mp4"**
→ `create-asset` with `file: ...` → `async-analyse-video` with the new `assetId` + Pegasus 1.5 → poll → report. Surface the asset ID for reuse.

**"For this 90-minute keynote, extract every product mention with timestamp"**
→ `async-analyse-video` with `analysisMode: "time_based_metadata"`, `segmentDefinitions: [{ id: "product-mention", description: "...", fields: [{name: "product_name", type: "string"}, {name: "context", type: "string"}] }]`.

**"Find every shot of <@anchor1> giving a presentation"**
→ Resolve the entity ID via the entities skill (or assume the user already has it) → `async-analyse-video` with `promptV2: { inputText: "<@anchor1> ...", mediaSources: [reference images] }`.

**"List my failed async analyses"**
→ `list-analyse-tasks` with `status: "failed"`.

## Important Notes

- **Pegasus 1.5 default** for everything — only switch to 1.2 on explicit request.
- **Direct URLs only**: YouTube/Drive/Dropbox share links are rejected by the MCP.
- **Local files auto-upload** — assets persist; surface the ID.
- **Up to 2 hours** of video per task.
- **Async — fire-and-forget**: poll status every 5-10s with `get-analyse-task`.
