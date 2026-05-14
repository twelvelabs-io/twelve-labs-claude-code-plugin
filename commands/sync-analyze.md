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
  - `videoId` of a previously-indexed video (Pegasus 1.2 only — see model policy below)
  - Direct http(s) URL to a raw media file
  - Asset ID (24-char hex, or `asset_*`) from a previous `/twelvelabs:assets upload`
  - Absolute or relative local file path (auto-uploaded as an asset internally)
- `prompt` — Optional. What you want the analysis to produce. If omitted, a default summary prompt is used.

## Model Policy

The MCP server supports two generative models:

- **Pegasus 1.5** (default for direct inputs) — clip windowing, structured prompts with reference images, larger token budget.
- **Pegasus 1.2** (legacy) — required when input is a `videoId` from an existing index. Mostly there for backwards compatibility.

This command picks the model automatically:

| Input type | Default `modelName` |
|---|---|
| `videoId` (from existing index) | `pegasus1.2` (forced — the MCP rejects 1.5 + videoId) |
| URL / asset ID / local file / base64 | **`pegasus1.5`** |

Override only when the user explicitly asks (e.g. "use pegasus 1.2", "legacy model"). Otherwise the defaults above apply.

## Examples

```
/twelvelabs:sync-analyze 6a04abc...                  # videoId, Pegasus 1.2
/twelvelabs:sync-analyze https://example.com/clip.mp4 "summarise"
/twelvelabs:sync-analyze ./video.mp4 "what animal is shown"  # auto-uploads file as asset, Pegasus 1.5
/twelvelabs:sync-analyze asset_6a04xyz... "extract action items"
```

## Instructions for Claude

When the user invokes `/twelvelabs:sync-analyze`, parse `$ARGUMENTS`.

### Step 1: Classify Input

Extract the first token from `$ARGUMENTS`:

- **No argument** → ask the user which video to analyse (call `mcp__twelvelabs-mcp__list-videos`, present a table, capture their pick as `videoId`).
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

- If input is `videoId` → force `modelName: "pegasus1.2"` (the MCP rejects 1.5 + videoId).
- Otherwise → **`modelName: "pegasus1.5"`** unless the user explicitly asked for 1.2.

### Step 3c: Call the MCP Tool

Use the parameter that matches the classified input type. Provide **exactly one** of `videoId`, `videoUrl`, `assetId`, `base64Video`.

For `videoId`:
```
Tool: mcp__twelvelabs-mcp__sync-analyse-video
Parameters:
  videoId: "<id>"
  modelName: "pegasus1.2"
  prompt: "<prompt>"
```

For `videoUrl`:
```
Tool: mcp__twelvelabs-mcp__sync-analyse-video
Parameters:
  videoUrl: "<url>"
  modelName: "pegasus1.5"
  prompt: "<prompt>"
```

For `assetId` (or the one just uploaded in Step 3a):
```
Tool: mcp__twelvelabs-mcp__sync-analyse-video
Parameters:
  assetId: "<id>"
  modelName: "pegasus1.5"
  prompt: "<prompt>"
```

For base64 (rare — the user explicitly provides base64 data):
```
Tool: mcp__twelvelabs-mcp__sync-analyse-video
Parameters:
  base64Video: "<base64>"
  modelName: "pegasus1.5"
  prompt: "<prompt>"
```

### Step 4: Optional Parameters (when the user asks for them)

These are all optional. Add them to the tool call when the user requests the corresponding behavior:

- `temperature` (0-1, default 0.2): for "more creative" / "more deterministic".
- `maxTokens`:
  - Pegasus 1.2: 1-4096 (default 4096).
  - Pegasus 1.5: 512-65536 (default 4096).
- `jsonSchema`: when the user wants structured output ("return JSON", "give me an object with these fields"). Provide a JSON Schema (Draft 2020-12) object. Cannot be combined with `promptV2`.
- `startTime` / `endTime` (Pegasus 1.5 only): clip the analysis to a sub-range in seconds. `end - start ≥ 4`.
- `promptV2` (Pegasus 1.5 only, mutually exclusive with `prompt`): structured prompt with `<@name>` references to attached images. Shape: `{ inputText: "...", mediaSources: [{ name, mediaType: "image", url|assetId|base64String }] }`. Use when the user wants to compare a video against reference images.

### Step 5: Display Analysis Result

```
Video Analysis

<analysis output>

Video: <filename | URL | asset ID | videoId>
Model: <pegasus1.2 | pegasus1.5>
```

If a custom prompt was used, also include:
```
Prompt: "<user's prompt>"
```

### Step 6: Errors

**Cannot find video / file**: see Step 1.

**`videoId is not accepted with modelName='pegasus1.5'`**: this means the input was misclassified as something needing 1.5. Retry with `modelName: "pegasus1.2"` or switch the input to a `videoUrl`/`assetId`/`base64Video`.

**`Provide exactly one of videoId, videoUrl, assetId, or base64Video`**: too many or zero sources set in the tool call. Re-classify per Step 1.

**Analysis failed**:
```
Analysis Failed

The analysis could not be completed. Possible causes:
- The video is still indexing (check with /twelvelabs:index-video status)
- The index doesn't include the generative model (Pegasus)
- The asset is still processing — wait for status="ready"

Error: <error message from API>
```

## Important Notes

- **Default model is Pegasus 1.5** for URL / asset / file / base64 inputs. Only `videoId` flows force Pegasus 1.2.
- **Indexed-video analysis** still works (pass the `videoId`) but is capped at 1.2's capabilities. New code should prefer URL/asset inputs.
- **Indexing not required** for URL/asset/base64 inputs — the analysis happens directly on the source.
- **Video duration cap**: sync analyse handles up to 1 hour. For longer videos, use `/twelvelabs:async-analyze`.
- **Auto-uploaded assets** persist in your account. Surface the asset ID so the user can reuse or delete it via `/twelvelabs:assets`.

## Related Commands

- `/twelvelabs:async-analyze` - Async analysis for >1h videos, time-based metadata extraction, or large structured outputs
- `/twelvelabs:assets` - Upload/delete reusable media assets
- `/twelvelabs:videos` - List indexed videos
- `/twelvelabs:index-video` - Index a new video for search
- `/twelvelabs:search` - Search across indexed videos
