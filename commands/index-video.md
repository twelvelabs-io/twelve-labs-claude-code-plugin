---
name: index-video
description: Index a video file, folder of videos, or URL, or check indexing status
disable-model-invocation: true
argument-hint: <path-or-url-or-folder> [index-id] | status [task-id]
---

# /twelvelabs:index-video - Index Videos for AI Analysis

Index local video files (single or whole folder) or remote URLs for AI analysis using TwelveLabs, or check the status of indexing tasks. Optional `userMetadata` lets you attach JSON key/value pairs that round-trip into search results.

## Usage

```
/twelvelabs:index-video <path-or-url-or-folder> [index-id]
/twelvelabs:index-video status [task-id]
```

**User provided:** `$ARGUMENTS`

## Arguments

- `path-or-url-or-folder` - **Required** (for indexing). One of:
  - Local file path to a video file
  - **Local folder path** containing video files (every `.mp4`/`.mov`/`.avi`/`.mkv`/`.webm` in the folder is indexed)
  - Remote http(s) URL to a video
  - Google Drive link (single file or public folder — folder indexes all MP4s)
- `index-id` - Optional. ID of the index to add the video(s) to. If not provided, uses the default index.
- `userMetadata` - Optional. JSON string of key/value pairs to attach to the indexed video(s). Keys are strings; values can be string/integer/float/boolean. Example: `'{"project": "demo", "source": "/local/path"}'`. The metadata appears in search results.
- `status` - Check indexing task status. Optionally provide a task ID.

## Supported Video Formats

- `.mp4` - MPEG-4 Video
- `.mov` - QuickTime Movie
- `.avi` - Audio Video Interleave
- `.mkv` - Matroska Video
- `.webm` - WebM Video

## Examples

### Index a Video
```
/twelvelabs:index-video ./video.mp4
/twelvelabs:index-video /absolute/path/to/video.mp4
/twelvelabs:index-video https://example.com/video.mp4
/twelvelabs:index-video https://drive.google.com/file/d/FILE_ID/view
/twelvelabs:index-video https://drive.google.com/drive/folders/FOLDER_ID
/twelvelabs:index-video ./video.mp4 abc123
```

### Check Indexing Status
```
/twelvelabs:index-video status
/twelvelabs:index-video status 6789abcd-1234-5678-9012-abcdef123456
```

## Instructions for Claude

When the user invokes `/twelvelabs:index-video`, the argument is provided in `$ARGUMENTS`. Follow these steps:

### Step 1: Parse Arguments

Check if `$ARGUMENTS` starts with `status` (case-insensitive):
- If yes: this is a **status check**. Remove `status` from the front and use any remaining value as an optional task ID. Go to **Status Flow**.
- If no: this is an **index** request. Go to **Index Flow**.

If `$ARGUMENTS` is empty or not provided:
- Display: "Please provide a path/URL or use `status` to check tasks. Usage: `/twelvelabs:index-video <path-or-url> [index-id]`"
- Stop processing.

---

## Index Flow

### Step 2: Determine Input Type

Extract the path or URL from `$ARGUMENTS`.

Check if there is a second argument after the path/URL — if so, treat it as an `indexId`.

Determine the input type:

- **URL**: Starts with `http://` or `https://`
- **Local folder**: An existing directory on disk (not a file). Use `folderFilePath`.
- **Local file**: Everything else (absolute or relative path to a video file). Use `videoFilePath`.

If the user supplied `userMetadata` (e.g. "tag it with project=demo"), capture it as a JSON string to pass through to all three flows.

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
2. Identify if it's a Google Drive link (contains `drive.google.com`)
3. Note: The TwelveLabs API will validate if the URL is accessible

If validation fails:
- Invalid URL: "Invalid URL format. Please provide a valid http:// or https:// URL."

### Step 4: Start Video Indexing

Use the `mcp__twelvelabs-mcp__start-video-indexing-task` MCP tool:

#### For Local Files:
```
Tool: mcp__twelvelabs-mcp__start-video-indexing-task
Parameters:
  videoFilePath: "<absolute-path-to-video>"
  indexId: "<index-id>"          # only include if provided
  userMetadata: "<JSON string>"  # only include if provided
```

#### For Local Folders:
The MCP tool indexes every supported video file in the folder and returns one task per file.

```
Tool: mcp__twelvelabs-mcp__start-video-indexing-task
Parameters:
  folderFilePath: "<absolute-path-to-folder>"
  indexId: "<index-id>"          # only include if provided
  userMetadata: "<JSON string>"  # only include if provided — applied to every video
```

Supported video extensions inside the folder: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`.

#### For URLs (including Google Drive):
```
Tool: mcp__twelvelabs-mcp__start-video-indexing-task
Parameters:
  videoUrl: "<url>"
  indexId: "<index-id>"          # only include if provided
  userMetadata: "<JSON string>"  # only include if provided
```

**Google Drive Notes:**
- Single file links (e.g., `https://drive.google.com/file/d/FILE_ID/view`) will index that file
- Folder links (e.g., `https://drive.google.com/drive/folders/FOLDER_ID`) will index all MP4 videos in the folder and start multiple tasks

### Step 5: Track Task in Config

After a successful indexing start, track the task in the local config:

```bash
python3 -c "
import sys
sys.path.insert(0, '.twelvelabs')
from config_helper import add_pending_task
add_pending_task('<task_id>', '<source_path_or_url>')
"
```

Replace `<task_id>` with the task ID from the MCP tool response and `<source_path_or_url>` with the original input.

### Step 6: Report Result

1. **On success** (single video):

   The MCP tool response includes `indexId` and `indexedAssetId`. Extract these from the response text and show:
   ```
   Video indexing started for: <filename-or-url>

   Index ID: <index_id>
   Indexed Asset ID: <indexed_asset_id>

   Video indexing is asynchronous and may take several minutes depending on video length.
   Use `/twelvelabs:index-video status` to check the indexing progress.
   To check status directly: mcp__twelvelabs-mcp__get-indexed-asset with indexId and indexedAssetId above.
   ```

2. **On success** (Google Drive folder):
   ```
   Video indexing started for Google Drive folder

   Multiple indexing tasks started:
   - Indexed Asset ID: <indexed_asset_id_1> - <filename_1>
   - Indexed Asset ID: <indexed_asset_id_2> - <filename_2>
   ...

   Video indexing is asynchronous and may take several minutes.
   Use `/twelvelabs:index-video status` to check indexing progress for all tasks.
   ```

3. **On failure**: Report the error to the user with the error message from the API.

---

## Status Flow

### Status Values

Tasks progress through these statuses:

| Status | Description |
|--------|-------------|
| `validating` | Video uploaded, being validated (format, duration, etc.) |
| `pending` | Validation complete, waiting for worker server |
| `queued` | Worker assigned, preparing to index |
| `indexing` | Transforming video into embeddings |
| `ready` | Indexing complete, video ready for search/analysis |
| `failed` | Indexing failed (check error message) |

### Step 2s: Read Local Pending Tasks

First, check the local config for any tracked pending tasks:

```bash
python3 -c "
import sys
sys.path.insert(0, '.twelvelabs')
from config_helper import get_all_pending_tasks
import json
print(json.dumps(get_all_pending_tasks(), indent=2))
"
```

This returns a dict of pending tasks keyed by task_id, or an empty dict if none.

### Step 3s: Determine What to Check

#### If a task-id was provided:
- Check only that specific task using the MCP tool

#### If no task-id:
- If there are pending tasks in local config, check those
- If no pending tasks in local config, check the latest 10 tasks from the API

### Step 4s: Call the MCP Tool

If the user has an `indexId` and `indexedAssetId` from a recent `start-video-indexing-task` response, use the preferred tool:

#### For a specific indexed asset (preferred for new tasks):
```
Tool: mcp__twelvelabs-mcp__get-indexed-asset
Parameters:
  indexId: "<index-id>"
  indexedAssetId: "<indexed-asset-id>"
  transcription: true            # only include if the user wants the transcript inline
```

Statuses for `get-indexed-asset`: `pending`, `queued`, `indexing`, `ready`, `failed`.

Set `transcription: true` when the user asks for the transcript ("what does the video say?", "give me the captions") so the response includes the audio transcript alongside metadata. Defaults to false otherwise to keep responses small.

Otherwise, use the legacy task tool:

#### For a specific task (legacy):
```
Tool: mcp__twelvelabs-mcp__get-video-indexing-tasks
Parameters:
  taskId: "<task-id>"
```

#### For all recent tasks (no task-id, legacy):
```
Tool: mcp__twelvelabs-mcp__get-video-indexing-tasks
Parameters: (none - returns latest 10 tasks)
```

### Step 5s: Update Local Config (if tasks completed)

For each task returned:

1. **If status is "ready"**:
   - Extract the `video_id` from the response
   - Move task from pending to videos in config:
   ```bash
   python3 -c "
   import sys
   sys.path.insert(0, '.twelvelabs')
   from config_helper import complete_task
   complete_task('<task_id>', '<video_id>', '<filename>')
   "
   ```

2. **If status is "failed"**:
   - Remove task from pending in config:
   ```bash
   python3 -c "
   import sys
   sys.path.insert(0, '.twelvelabs')
   from config_helper import fail_task
   fail_task('<task_id>')
   "
   ```

3. **If status is still in progress** (validating, pending, queued, indexing):
   - Update the status in local config:
   ```bash
   python3 -c "
   import sys
   sys.path.insert(0, '.twelvelabs')
   from config_helper import update_pending_task_status
   update_pending_task_status('<task_id>', '<status>')
   "
   ```

### Step 6s: Display Results

Format the status information clearly for the user:

#### For a specific task:
```
Task Status: <task-id>

Status: <status>
Source: <source-path-or-url>
Started: <timestamp>

[If ready]
Video is ready for search and analysis!
Video ID: <video_id>

[If failed]
Indexing failed. Check the video file and try again.

[If in progress]
Video is still being processed. Check again later.
```

#### For multiple tasks:
```
Indexing Task Status

| Task ID | Source | Status | Started |
|---------|--------|--------|---------|
| <id1>   | <src1> | <sts1> | <time1> |
| <id2>   | <src2> | <sts2> | <time2> |

Legend:
- ready - Video indexed and ready
- indexing/queued/pending/validating - In progress
- failed - Check error and retry
```

#### If no tasks found:
```
No indexing tasks found.

To index a video, use: /twelvelabs:index-video <path-or-url>
```

---

## Important Notes

- **Minimum Duration**: Videos must be at least 4 seconds long for TwelveLabs indexing
- **Async Processing**: Video indexing is asynchronous - it runs in the background
- **Status Checking**: Use `/twelvelabs:index-video status` to monitor indexing progress
- **File Access**: The file must be accessible to the TwelveLabs MCP server
- **Ready Videos**: Once ready, videos can be searched with `/twelvelabs:search` or analyzed with `/twelvelabs:sync-analyze`

## Related Commands

- `/twelvelabs:videos` - List indexed videos
- `/twelvelabs:search` - Search indexed videos
- `/twelvelabs:sync-analyze` - Analyze indexed videos
