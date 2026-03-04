---
name: embed
description: Create video embeddings or check embedding task status
disable-model-invocation: true
argument-hint: <path-or-url> | status [task-id]
---

# /twelvelabs:embed - Video Embeddings

Create video embeddings from local video files or remote URLs, or check the status of embedding tasks.

## Usage

```
/twelvelabs:embed <path-or-url>
/twelvelabs:embed status [task-id]
```

**User provided:** `$ARGUMENTS`

## Arguments

- `path-or-url` - A local file path or remote URL to a video file
- `status` - Check embedding task status. Optionally provide a task ID.

## Supported Video Formats

- `.mp4` - MPEG-4 Video
- `.mov` - QuickTime Movie
- `.avi` - Audio Video Interleave
- `.mkv` - Matroska Video
- `.webm` - WebM Video

## Examples

### Create Embeddings
```
/twelvelabs:embed ./video.mp4
/twelvelabs:embed /absolute/path/to/video.mp4
/twelvelabs:embed https://example.com/video.mp4
```

### Check Status
```
/twelvelabs:embed status
/twelvelabs:embed status 6789abcd-1234-5678-9012-abcdef123456
```

## Instructions for Claude

When the user invokes `/twelvelabs:embed`, the argument is provided in `$ARGUMENTS`. Follow these steps:

### Step 1: Parse Arguments

If `$ARGUMENTS` is empty:
- Display: "Please provide a video path/URL or use `status` to check tasks."
- Stop processing.

Check if `$ARGUMENTS` starts with `status` (case-insensitive):
- If yes: this is a **status check**. Remove `status` from the front and use any remaining value as an optional task ID. Go to **Status Flow**.
- If no: this is an **embed** request. Go to **Embed Flow**.

---

## Embed Flow

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

1. **On success**:
   ```
   Video embedding started for: <filename-or-url>

   Task ID: <task_id>

   Embedding creation is asynchronous and may take several minutes depending on video length.
   Use `/twelvelabs:embed status` to check the progress.
   ```

2. **On failure**: Report the error to the user with the error message from the API.

---

## Status Flow

### Step 2s: Read Local Pending Embedding Tasks

Check the local config for any tracked pending embedding tasks:

```bash
python3 -c "
import sys
sys.path.insert(0, '.twelvelabs')
from config_helper import get_all_pending_embedding_tasks
import json
print(json.dumps(get_all_pending_embedding_tasks(), indent=2))
"
```

### Step 3s: Determine What to Check

#### If a task-id was provided:
- Check only that specific task

#### If no task-id:
- If there are pending embedding tasks in local config, check those
- If no pending embedding tasks in local config, check the latest 10 tasks from the API

### Step 4s: Call the MCP Tool

Use the `mcp__twelvelabs-mcp__get-video-embeddings-tasks` tool:

#### For a specific task:
```
Tool: mcp__twelvelabs-mcp__get-video-embeddings-tasks
Parameters:
  taskId: "<task-id>"
```

#### For all recent tasks (no task-id):
```
Tool: mcp__twelvelabs-mcp__get-video-embeddings-tasks
Parameters: (none - returns latest 10 tasks)
```

### Step 5s: Handle Results Based on Status

For each task returned:

1. **If status is "ready"**:
   - Automatically retrieve the embeddings:
   ```
   Tool: mcp__twelvelabs-mcp__retrieve-video-embeddings
   Parameters:
     taskId: "<task-id>"
   ```
   - Display the embedding results to the user

2. **If status is "failed"**:
   - Report the failure to the user

3. **If status is "processing"**:
   - Report that the task is still processing

### Step 6s: Display Results

#### Embedding Task Status Values

| Status | Description |
|--------|-------------|
| `processing` | Video is being processed into embeddings |
| `ready` | Embeddings created, ready for retrieval |
| `failed` | Embedding creation failed (check error message) |

#### For a specific task that is ready:
```
Embedding Task: <task-id>

Status: ready
Source: <source-path-or-url>

Embeddings retrieved successfully!
- Number of embeddings: <count>
- Embedding dimension: <dimension>

[Display embedding details or summary]
```

#### For a specific task still processing:
```
Embedding Task: <task-id>

Status: processing
Source: <source-path-or-url>

Embeddings are still being created. Check again later.
```

#### For a specific task that failed:
```
Embedding Task: <task-id>

Status: failed
Source: <source-path-or-url>

Embedding creation failed. Check the video file and try again.
```

#### For multiple tasks:
```
Embedding Task Status

| Task ID | Source | Status |
|---------|--------|--------|
| <id1>   | <src1> | <sts1> |
| <id2>   | <src2> | <sts2> |

[For any ready tasks, auto-retrieve and show embeddings below]
```

#### If no tasks found:
```
No embedding tasks found.

To create video embeddings, use: /twelvelabs:embed <path-or-url>
```

## Important Notes

- **Async Processing**: Embedding creation is asynchronous - it runs in the background
- **Auto-Retrieve**: When checking status and a task is ready, embeddings are automatically retrieved
- **Processing Time**: Embedding creation can take several minutes depending on video length

## Related Commands

- `/twelvelabs:index-video` - Index a video for search and analysis
- `/twelvelabs:index-video status` - Check video indexing task status
- `/twelvelabs:help` - Show all available commands
