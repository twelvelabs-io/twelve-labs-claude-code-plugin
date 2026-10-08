---
name: sync-analyze
description: Synchronously analyze a video by ID, URL, asset, or local file path
disable-model-invocation: true
argument-hint: "<video-id-or-url-or-path-or-asset-id> [prompt]"
---

# /twelvelabs:sync-analyze - Synchronous Video Analysis

Synchronously analyse a video and return the generated text (or structured JSON) inline. Accepts a previously-indexed `videoId`, a direct http(s) URL, a previously-uploaded asset ID, a local file path (auto-uploaded as an asset), or base64 data.

For very long videos (>1 hour) or for time-based metadata segmentation, use `/twelvelabs:async-analyze` instead.

## Usage

```
/twelvelabs:sync-analyze <video-id-or-url-or-path-or-asset-id> [prompt]
/twelvelabs:sync-analyze [prompt]                                  # if no input given, prompts you to pick a videoId
```

**User provided:** `$ARGUMENTS`

## Arguments

- First positional — one of:
  - `videoId` of a previously-indexed video (the command also passes the `indexId` it came from, when known)
  - Direct http(s) URL to a raw media file
  - Asset ID (24-char hex, or `asset_*`) from a previous `/twelvelabs:assets upload`
  - Absolute or relative local file path (auto-uploaded as an asset internally)
- `prompt` — Optional. What you want the analysis to produce. If omitted, a default summary prompt is used.

## Model Policy

The MCP server supports two analysis models:

- **Pegasus 1.6** (default) — used for every input type.
- **Pegasus 1.5** — selectable on request.

Both support clip windowing, structured prompts with reference images, and JSON output, for every input type including `videoId`.

| Input type | Default `modelName` |
|---|---|
| Any (`videoId` / URL / asset ID / local file / base64) | **`pegasus1.6`** |

Use `pegasus1.5` only when the user explicitly asks for it (e.g. "use pegasus 1.5").

## Examples

```
/twelvelabs:sync-analyze 6a04abc...                  # videoId, Pegasus 1.6
/twelvelabs:sync-analyze https://example.com/clip.mp4 "summarise"
/twelvelabs:sync-analyze ./video.mp4 "what animal is shown"  # auto-uploads file as asset, Pegasus 1.6
/twelvelabs:sync-analyze asset_6a04xyz... "extract action items"
```

## Instructions for Claude

When the user invokes `/twelvelabs:sync-analyze`, parse `$ARGUMENTS`.

### Step 1: Classify Input

Extract the first token from `$ARGUMENTS`:

- **No argument** → ask the user which video to analyse (call `mcp__twelvelabs-mcp__list-videos`, present a table, capture their pick as `videoId` and remember the `indexId` you listed from — the default index if you didn't pass one).
- Starts with `http://` or `https://` → treat as `videoUrl`.
- Matches `^[a-f0-9]{24}$` or starts with `asset_` → if the user says "asset" / "uploaded asset" / etc., treat as `assetId`. If the user says "video" / refers to an indexed video, treat as `videoId`. When ambiguous, prefer `videoId` (the more common case for a 24-char hex).
- Otherwise → treat as a local file path. Resolve to absolute; verify the file exists. If it doesn't:
  ```
  Cannot find a video file at: <path>
  Provide a videoId, a direct http(s) URL, an asset ID, or an absolute path to an existing video file.
  ```

The rest of `$ARGUMENTS` (everything after the first token, stripped of surrounding quotes) is the optional `prompt`.

### Step 2: Default Prompt

If the user did not provide a prompt, use:
`"Provide a comprehensive summary of this video including key moments, topics covered, and important details."`

### Step 3a: If Local File, Upload as Asset First

For a local file path, upload it before analysing:

```
Tool: mcp__twelvelabs-mcp__create-asset
Parameters:
  file: "<absolute-path>"
```

Capture the returned `assetId`. Surface it to the user:

```
Uploaded <path> as asset <assetId>. Running sync analysis…
(Reuse this asset with `/twelvelabs:sync-analyze <assetId>` or delete with `/twelvelabs:assets delete <assetId>`.)
```

### Step 3b: Pick the Model

- **`modelName: "pegasus1.6"`** for every input type, unless the user explicitly asked for `pegasus1.5`.

### Step 3c: Call the MCP Tool

Use the parameter that matches the classified input type. Provide **exactly one** of `videoId`, `videoUrl`, `assetId`, `base64Video`.

For `videoId` — include `indexId` whenever you know the index the video came from (e.g. from search results, the index you listed, or the default index). The server uses it to look up the video's asset ID directly; without it, the server searches all indexes:
```
Tool: mcp__twelvelabs-mcp__sync-analyse-video
Parameters:
  videoId: "<id>"
  indexId: "<index-id>"     # when known
  modelName: "pegasus1.6"
  prompt: "<prompt>"
```

For `videoUrl`:
```
Tool: mcp__twelvelabs-mcp__sync-analyse-video
Parameters:
  videoUrl: "<url>"
  modelName: "pegasus1.6"
  prompt: "<prompt>"
```

For `assetId` (or the one just uploaded in Step 3a):
```
Tool: mcp__twelvelabs-mcp__sync-analyse-video
Parameters:
  assetId: "<id>"
  modelName: "pegasus1.6"
  prompt: "<prompt>"
```

For base64 (rare — the user explicitly provides base64 data):
```
Tool: mcp__twelvelabs-mcp__sync-analyse-video
Parameters:
  base64Video: "<base64>"
  modelName: "pegasus1.6"
  prompt: "<prompt>"
```

### Step 4: Optional Parameters (when the user asks for them)

These are all optional. Add them to the tool call when the user requests the corresponding behavior:

- `temperature` (0-1, default 0.2): for "more creative" / "more deterministic".
- `maxTokens`: 512-65536 (default 4096).
- `jsonSchema`: when the user wants structured output ("return JSON", "give me an object with these fields"). Provide a JSON Schema (Draft 2020-12) object. Cannot be combined with `promptV2`.
- `startTime` / `endTime`: clip the analysis to a sub-range in seconds. `end - start ≥ 4`.
- `promptV2` (mutually exclusive with `prompt`): structured prompt with `<@name>` references to attached images. Shape: `{ inputText: "...", mediaSources: [{ name, mediaType: "image", url|assetId|base64String }] }`. Use when the user wants to compare a video against reference images.

### Step 5: Display Analysis Result

```
Video Analysis

<analysis output>

Video: <filename | URL | asset ID | videoId>
Model: <pegasus1.6 | pegasus1.5>
```

If a custom prompt was used, also include:
```
Prompt: "<user's prompt>"
```

### Step 6: Errors

**Cannot find video / file**: see Step 1.

**`videoId` call fails with "asset ... does not exist"**: the video wasn't found in any of the user's indexes. Check the ID with `/twelvelabs:videos`, or retry with the `indexId` it came from.

**`Provide exactly one of videoId, videoUrl, assetId, or base64Video`**: too many or zero sources set in the tool call. Re-classify per Step 1.

**Analysis failed**:
```
Analysis Failed

The analysis could not be completed. Possible causes:
- The video is still indexing (check with /twelvelabs:index-video status)
- The `videoId` doesn't exist in any of the user's indexes
- The asset is still processing — wait for status="ready"

Error: <error message from API>
```

## Important Notes

- **Default model is Pegasus 1.6** for every input type. Pegasus 1.5 is available on request.
- **Indexed-video analysis** works with the full feature set: the server sends the `videoId` as the video's asset ID. Pass `indexId` with it whenever the index is known.
- **Indexing not required** for URL/asset/base64 inputs — the analysis happens directly on the source.
- **Video duration cap**: sync analyse handles up to 1 hour. For longer videos, use `/twelvelabs:async-analyze`.
- **Auto-uploaded assets** persist in your account. Surface the asset ID so the user can reuse or delete it via `/twelvelabs:assets`.

## Related Commands

- `/twelvelabs:async-analyze` - Async analysis for >1h videos, time-based metadata extraction, or large structured outputs
- `/twelvelabs:assets` - Upload/delete reusable media assets
- `/twelvelabs:videos` - List indexed videos
- `/twelvelabs:index-video` - Index a new video for search
- `/twelvelabs:search` - Search across indexed videos
