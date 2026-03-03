---
name: embed-status
description: Check the status of video embedding tasks on TwelveLabs
disable-model-invocation: true
argument-hint: [task-id]
---

# /twelvelabs:embed-status - Check Video Embedding Status

Check the status of video embedding tasks. When a task is ready, automatically retrieves the embeddings.

## Usage

```
/twelvelabs:embed-status [task-id]
```

**User provided:** `$ARGUMENTS`

## Arguments

- `task-id` - **Optional**. Specific task ID to check. If not provided, shows all pending embedding tasks.

## Examples

### Check All Pending Embedding Tasks
```
/twelvelabs:embed-status
```

### Check Specific Task
```
/twelvelabs:embed-status 6789abcd-1234-5678-9012-abcdef123456
```

## Status Values

Embedding tasks have these statuses:

| Status | Description |
|--------|-------------|
| `processing` | Video is being processed into embeddings |
| `ready` | Embeddings created, ready for retrieval |
| `failed` | Embedding creation failed (check error message) |

## Instructions for Claude

When the user invokes `/twelvelabs:embed-status`, the optional argument is provided in `$ARGUMENTS`. Follow these steps:

### Step 1: Parse Arguments

Check if a task ID was provided in `$ARGUMENTS`:
- If `$ARGUMENTS` contains a task ID, use it to check a specific task
- If `$ARGUMENTS` is empty, check all pending embedding tasks

### Step 2: Read Local Pending Embedding Tasks

First, check the local config for any tracked pending embedding tasks:

```bash
python3 -c "
import sys
sys.path.insert(0, '.twelvelabs')
from config_helper import get_all_pending_embedding_tasks
import json
print(json.dumps(get_all_pending_embedding_tasks(), indent=2))
"
```

This returns a dict of pending embedding tasks keyed by task_id, or an empty dict if none.

### Step 3: Determine What to Check

#### If `$ARGUMENTS` contains a task-id:
- Check only that specific task using the MCP tool

#### If `$ARGUMENTS` is empty (no task-id):
- If there are pending embedding tasks in local config, check those
- If no pending embedding tasks in local config, check the latest 10 tasks from the API

### Step 4: Call the MCP Tool

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

### Step 5: Handle Results Based on Status

For each task returned:

1. **If status is "ready"**:
   - Automatically retrieve the embeddings using `mcp__twelvelabs-mcp__retrieve-video-embeddings`:
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

### Step 6: Display Results

Format the status information clearly for the user:

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

- **Auto-Retrieve**: When a task is ready, embeddings are automatically retrieved and displayed
- **Async Processing**: Embedding creation runs asynchronously on TwelveLabs servers
- **Processing Time**: Embedding creation can take several minutes depending on video length
- **Status Sync**: Local config is updated when you check status

## Related Commands

- `/twelvelabs:embed` - Start creating video embeddings
- `/twelvelabs:status` - Check video indexing task status
- `/twelvelabs:help` - Show all available commands
