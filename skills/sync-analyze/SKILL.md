---
name: sync-analyze
description: Synchronously analyze a video to understand its content. Accepts an indexed videoId, a direct video URL, a previously uploaded asset, or a local file path (auto-uploaded). Use when the user asks "what is this video about?", "summarize the video", "analyze this video", or has questions about video content.
---

# Synchronous Video Analysis

Analyse a video using TwelveLabs AI and return the result inline. Works on:

- A previously-indexed `videoId` (pass the `indexId` it came from too, when known).
- A direct http(s) URL.
- A previously-uploaded `assetId`.
- A local file path — this skill uploads it as an asset internally first, then analyses it.

All inputs run on Pegasus 1.6 by default.

For videos longer than 1 hour, or for time-based metadata extraction, use the `async-analyze` skill instead.

## When to Use This Skill

The user wants a quick text/JSON answer about a single video and:

- Provides a video reference (URL, file path, asset ID, or indexed videoId) AND a question / instruction; or
- Asks a general question and references "this video" / "that video" / "the video I just indexed".

For multi-segment structured extraction (e.g. "find every product mention with timestamps"), use the async-analyze skill — that supports `analysisMode: "time_based_metadata"`.

## Model Default

Use **`pegasus1.6`** for every input type (`videoId`, URL, asset, file, base64). Both models support every parameter below (`promptV2`, `startTime`/`endTime`, `jsonSchema`).

Only switch to `pegasus1.5` when the user explicitly asks for it ("use pegasus 1.5").

## Instructions

### Step 1: Classify the Input

Look at what the user gave you:

- 24-char hex string referred to as a "video" → `videoId`. Also pass `indexId` whenever you know which index it came from (the index you searched or listed, or the default index). The server uses it to look up the video's asset ID directly; without it, the server searches all indexes.
- `http(s)://...` URL → `videoUrl`.
- 24-char hex or `asset_*` referred to as an "asset" or "uploaded thing" → `assetId`.
- Anything that looks like a file path → resolve to absolute; verify the file exists; **upload it first**:
  ```
  Tool: mcp__twelvelabs-mcp__create-asset
  Parameters:
    file: "<absolute-path>"
  ```
  Capture the returned `assetId`. Tell the user the asset was created and that they can reuse or delete it via `/twelvelabs:assets`. Then continue as if they had given you an `assetId`.

### Step 2: Build the Prompt

If the user gave a question, use it as `prompt`. Otherwise default to:
`"Provide a comprehensive summary of this video including key moments, topics covered, and important details."`

### Step 3: Call the Analyze Tool

Set exactly one source (`videoId`, `videoUrl`, `assetId`, or `base64Video`) plus `modelName` and `prompt`. With `videoId`, add `indexId` when known:

```
Tool: mcp__twelvelabs-mcp__sync-analyse-video
Parameters:
  <one of: videoId | videoUrl | assetId | base64Video>: "..."
  indexId: "..."                 # only with videoId, when the index is known
  modelName: "pegasus1.6"        # or "pegasus1.5" only on explicit user request
  prompt: "..."
```

### Step 4: Advanced Parameters

Add these only when the user asks for the corresponding behavior:

- `temperature` (0-1, default 0.2) — "more creative" / "more deterministic"
- `maxTokens` — long outputs
- `jsonSchema` — "give me JSON"; provide a JSON Schema (Draft 2020-12); cannot combine with `promptV2`
- `startTime` / `endTime` — clip to a sub-range; `end - start ≥ 4`
- `promptV2` (mutually exclusive with `prompt`) — structured prompt with image references via `<@name>` and a `mediaSources` array (each: `{ name, mediaType: "image", url | assetId | base64String }`)

### Step 5: Display

```
Video Analysis

<analysis output>

Video: <best identifier — filename, URL, asset ID, or videoId>
Model: pegasus1.6    (or pegasus1.5)
```

### Step 6: Errors

- "asset ... does not exist" on a `videoId` call → the video isn't in any of the user's indexes. Check the ID with `/twelvelabs:videos`, or retry with the `indexId` it came from.
- `Provide exactly one of videoId, videoUrl, assetId, or base64Video` → you set zero or multiple sources; re-classify.
- Asset still processing → wait a couple seconds and retry (`create-asset` returns status `pending` initially).

## Example Interactions

**"What is this video about?"** (after listing videos and the user picked one)
→ `sync-analyse-video` with `videoId` + the `indexId` you listed it from + Pegasus 1.6, generic summary prompt.

**"Analyse https://example.com/clip.mp4 and tell me what happens"**
→ `sync-analyse-video` with `videoUrl` + Pegasus 1.6.

**"Summarise /Users/me/keynote.mp4"**
→ `create-asset` with `file: "/Users/me/keynote.mp4"` → `sync-analyse-video` with the new `assetId` + Pegasus 1.6.

**"What products are mentioned in this video? Return JSON: { product, timestamp_sec }[]"**
→ `sync-analyse-video` with the appropriate source + `jsonSchema` set to an array schema.

## Important Notes

- Indexed-video analysis works via `videoId` with the full feature set; the server analyses the video's underlying asset. Pass `indexId` alongside it whenever you know it.
- Pegasus 1.6 is the default for every input; Pegasus 1.5 is available on request. Pegasus 1.2 no longer exists.
- Auto-uploaded assets persist. Always tell the user the asset ID so they can reuse or delete it.
