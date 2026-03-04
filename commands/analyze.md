---
name: analyze
description: Analyze video content using AI
disable-model-invocation: true
argument-hint: "[video-id] [index-id] [prompt]"
---

# /twelvelabs:analyze - Analyze Video Content

Analyze indexed videos using TwelveLabs AI to understand and extract information from video content.

## Usage

```
/twelvelabs:analyze [video-id] [index-id] [prompt]
```

**User provided:** `$ARGUMENTS`

## Arguments

- `video-id` (optional) - The video ID to analyze. If not provided, you will be prompted to select from available videos.
- `index-id` (optional) - The index ID containing the video. If not provided, uses the default index when listing videos.
- `prompt` (optional) - What you want to know about the video. If not provided, generates a comprehensive summary.

## Examples

### Analyze with Defaults
```
/twelvelabs:analyze
```

### Analyze Specific Video
```
/twelvelabs:analyze abc123def456
```

### Analyze Video from Specific Index
```
/twelvelabs:analyze abc123def456 idx789
```

### Analyze with Custom Prompt
```
/twelvelabs:analyze abc123def456 "List all products mentioned"
/twelvelabs:analyze abc123def456 idx789 "What are the main topics discussed?"
/twelvelabs:analyze abc123def456 "Extract action items from this meeting"
```

## Instructions for Claude

When the user invokes `/twelvelabs:analyze`, the arguments are provided in `$ARGUMENTS`. Follow these steps:

### Step 1: Parse Arguments

Extract arguments from `$ARGUMENTS`:
- First token: `video-id` (optional)
- Second token: `index-id` (optional) — only if it does NOT start with a quote. If it starts with `"`, treat it as the prompt instead.
- Remaining text: `prompt` (optional)

### Step 2: Get Video ID (if not provided)

If no video-id was provided in `$ARGUMENTS`, help the user select a video:

1. Call `mcp__twelvelabs-mcp__list-videos` to get available videos (pass `indexId` if an index-id was provided)
2. Display the list to the user with video IDs and filenames
3. Ask the user which video they want to analyze

**Example prompt**:
```
Which video would you like to analyze?

| # | Video ID | Filename |
|---|----------|----------|
| 1 | abc123   | demo.mp4 |
| 2 | def456   | tutorial.mp4 |
| 3 | ghi789   | meeting.mp4 |

Enter the video ID or number:
```

### Step 3: Determine the Prompt

- If no prompt provided: Use "Provide a comprehensive summary of this video including key moments, topics covered, and important details."
- If prompt provided: Use the user's prompt directly

### Step 4: Call the Analyze Video MCP Tool

Use the `mcp__twelvelabs-mcp__analyse-video` tool:

```
Tool: mcp__twelvelabs-mcp__analyse-video
Parameters:
  videoId: "<video-id>"
  prompt: "<prompt>"
```

### Step 5: Display Analysis Results

Format the results clearly:

```
Video Analysis

<analysis output>

Video: <filename or video-id>
```

If a custom prompt was used, also show:
```
Prompt: "<user's prompt>"
```

### Step 6: Handle Errors

**Video not found**:
```
Video Not Found

Could not find video with ID: <video-id>

Use /twelvelabs:videos to see available videos.
```

**Analysis failed**:
```
Analysis Failed

The analysis could not be completed. This might happen if:
- The video is still being indexed (check with /twelvelabs:index-video status)
- The index doesn't support generative models

Error: <error message if available>
```

## Important Notes

- **Indexed Videos Only**: Analysis only works on videos that have been fully indexed
- **Generative Model Required**: The index must include the `generative` model for analysis
- **Processing Time**: Analysis may take a few seconds depending on video length

## Related Commands

- `/twelvelabs:videos` - List all indexed videos
- `/twelvelabs:index-video` - Index a new video
- `/twelvelabs:search` - Search videos for specific content
- `/twelvelabs:index-video status` - Check if videos are ready for analysis
