---
name: embed
description: Create, check, and retrieve video embeddings. Use when user wants to generate embeddings from a video, check embedding status, or retrieve embeddings for a video.
---

# Video Embeddings

Create video embeddings, check embedding task status, and retrieve embeddings from tasks or indexed videos using TwelveLabs.

## When to Use This Skill

Use this skill when the user:
- Wants to create embeddings from a video ("embed this video", "create embeddings for this video")
- Asks about embedding task status ("are my embeddings ready?", "check embedding status")
- Wants to retrieve embeddings from an indexed video ("get embeddings for video abc123")
- Mentions video embeddings in any context

## Instructions

### Creating Embeddings from a Video

#### Step 1: Identify the Video Source

Extract the video path or URL from the user's message:

- **Local file path**: `/path/to/video.mp4`, `./video.mp4`, `~/Videos/demo.mov`
- **Remote URL**: `https://example.com/video.mp4`

If no path/URL is provided, ask the user:
```
Please provide the video file path or URL you'd like to create embeddings for.

Examples:
- Local file: /path/to/video.mp4 or ./video.mp4
- Remote URL: https://example.com/video.mp4
```

#### Step 2: Validate the Input

**For Local Files**:
1. Resolve relative paths to absolute paths
2. Verify the file exists
3. Check file extension is supported: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`

**For URLs**:
1. Verify URL starts with `http://` or `https://`

#### Step 3: Start Embeddings Task

Use the `mcp__twelvelabs-mcp__start-video-embeddings-task` tool:

**For Local Files**:
```
Tool: mcp__twelvelabs-mcp__start-video-embeddings-task
Parameters:
  videoFilePath: "<absolute-path-to-video>"
```

**For URLs**:
```
Tool: mcp__twelvelabs-mcp__start-video-embeddings-task
Parameters:
  videoUrl: "<url>"
```

#### Step 4: Report Result

**On success**:
```
Video embedding started!

Source: <filename-or-url>
Task ID: <task_id>

Embedding creation runs in the background and may take several minutes.
Ask "are my embeddings ready?" to check the progress.
```

---

### Checking Embedding Status

When the user asks about embedding status ("are my embeddings ready?", "check embedding status"):

#### Step 1: Check Local Config

```bash
python3 -c "
import sys
sys.path.insert(0, '.twelvelabs')
from config_helper import get_all_pending_embedding_tasks
import json
print(json.dumps(get_all_pending_embedding_tasks(), indent=2))
"
```

#### Step 2: Query the API

If there are pending tasks, check each one:
```
Tool: mcp__twelvelabs-mcp__get-video-embeddings-tasks
Parameters:
  taskId: "<task-id>"
```

If no pending tasks, check the latest tasks:
```
Tool: mcp__twelvelabs-mcp__get-video-embeddings-tasks
Parameters: (none)
```

#### Step 3: Auto-Retrieve When Ready

If a task status is `ready`, automatically retrieve the embeddings:
```
Tool: mcp__twelvelabs-mcp__retrieve-video-embeddings
Parameters:
  taskId: "<task-id>"
```

Display the results to the user.

---

### Retrieving Embeddings from an Indexed Video

When the user asks for embeddings of an already-indexed video ("get embeddings for video abc123"):

#### Step 1: Identify the Video

The user should provide a video ID. If not, help them find it:
- Check local config for known videos
- Use `mcp__twelvelabs-mcp__list-videos` to list available videos

#### Step 2: Retrieve Embeddings

```
Tool: mcp__twelvelabs-mcp__retrieve-video-embeddings
Parameters:
  videoId: "<video-id>"
  indexId: "<index-id>"  (optional, uses default index if omitted)
```

#### Step 3: Display Results

Show the embedding information:
```
Embeddings retrieved for video: <video-id>

- Number of embeddings: <count>
- Embedding dimension: <dimension>

[Display embedding details or summary]
```

## Example Interactions

**User**: "Create embeddings for /Users/me/Videos/demo.mp4"
**Action**: Validate file exists -> call start-video-embeddings-task with videoFilePath

**User**: "Embed this video https://example.com/video.mp4"
**Action**: Call start-video-embeddings-task with videoUrl

**User**: "Are my embeddings ready?"
**Action**: Check pending embedding tasks -> query API -> auto-retrieve if ready

**User**: "Get embeddings for video abc123"
**Action**: Call retrieve-video-embeddings with videoId

## Important Notes

- **Async Processing**: Embedding creation runs in the background on TwelveLabs servers
- **Processing Time**: Can take several minutes depending on video length
- **Two Retrieval Paths**: Embeddings can be retrieved from a task (using taskId) or from an indexed video (using videoId + indexId)
- **Auto-Retrieve**: Status checks automatically retrieve embeddings when tasks complete
