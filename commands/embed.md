---
name: embed
description: Create video embeddings from a file or URL using TwelveLabs
disable-model-invocation: true
argument-hint: [path-or-url]
---

# /twelvelabs:embed - Create Video Embeddings

Create video embeddings from local video files or remote URLs using TwelveLabs.

## Usage

```
/twelvelabs:embed <path-or-url>
```

**User provided:** `$ARGUMENTS`

## Arguments

- `path-or-url` - **Required**. Either:
  - Local file path (absolute or relative) to a video file
  - Remote URL (http:// or https://) to a video

## Supported Video Formats

- `.mp4` - MPEG-4 Video
- `.mov` - QuickTime Movie
- `.avi` - Audio Video Interleave
- `.mkv` - Matroska Video
- `.webm` - WebM Video

## Examples

### Local Files
```
/twelvelabs:embed ./video.mp4
/twelvelabs:embed /absolute/path/to/video.mp4
/twelvelabs:embed ../videos/meeting-recording.mov
```

### Remote URLs
```
/twelvelabs:embed https://example.com/video.mp4
/twelvelabs:embed https://storage.googleapis.com/bucket/video.mp4
```

## Instructions for Claude

When the user invokes `/twelvelabs:embed`, the argument is provided in `$ARGUMENTS`. Follow these steps:

### Step 1: Parse Arguments

Extract the path or URL from `$ARGUMENTS`. If `$ARGUMENTS` is empty or not provided:
- Display: "Please provide a path or URL. Usage: `/twelvelabs:embed <path-or-url>`"
- Stop processing.

### Step 2: Determine Input Type

Determine if the input is a local file path or a URL:

- **URL**: Starts with `http://` or `https://`
- **Local file**: Everything else (absolute or relative path)

### Step 3: Validate the Input

#### For Local Files:
1. Resolve the path to an absolute path if relative
2. Verify the file exists at the specified path
3. Check that the file extension is a supported video format (mp4, mov, avi, mkv, webm)

If validation fails:
- File not found: "Video file not found at: `<path>`. Please check the path and try again."
- Unsupported format: "Unsupported video format: `<extension>`. Supported formats: mp4, mov, avi, mkv, webm"

#### For URLs:
1. Verify the URL is well-formed (starts with http:// or https://)
2. Note: The TwelveLabs API will validate if the URL is accessible

If validation fails:
- Invalid URL: "Invalid URL format. Please provide a valid http:// or https:// URL."

### Step 4: Start Video Embeddings Task

Use the `mcp__twelvelabs-mcp__start-video-embeddings-task` MCP tool:

#### For Local Files:
```
Tool: mcp__twelvelabs-mcp__start-video-embeddings-task
Parameters:
  videoFilePath: "<absolute-path-to-video>"
```

#### For URLs:
```
Tool: mcp__twelvelabs-mcp__start-video-embeddings-task
Parameters:
  videoUrl: "<url>"
```

### Step 5: Report Result

After calling the embeddings tool:

1. **On success**:
   ```
   Video embedding started for: <filename-or-url>

   Task ID: <task_id>

   Embedding creation is asynchronous and may take several minutes depending on video length.
   Use `/twelvelabs:embed-status` to check the progress.
   ```

2. **On failure**: Report the error to the user with the error message from the API.

## Important Notes

- **Async Processing**: Embedding creation is asynchronous - it runs in the background
- **Status Checking**: Use `/twelvelabs:embed-status` to monitor progress
- **Auto-Retrieve**: When the task is ready, `/twelvelabs:embed-status` will automatically retrieve the embeddings

## Related Commands

- `/twelvelabs:embed-status` - Check embedding task status and retrieve results
- `/twelvelabs:index` - Index a video for search and analysis
- `/twelvelabs:help` - Show all available commands
