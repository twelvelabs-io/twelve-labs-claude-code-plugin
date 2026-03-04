---
name: videos
description: List your indexed videos
disable-model-invocation: true
argument-hint: [index-id]
---

# /twelvelabs:videos - List Indexed Videos

List all indexed videos in your default index or a specific index.

## Usage

```
/twelvelabs:videos [index-id]
```

**User provided:** `$ARGUMENTS`

## Arguments

- `index-id` - **Optional**. ID of a specific index to list videos from. If not provided, uses the default index.

## Examples

```
/twelvelabs:videos
/twelvelabs:videos abc123
```

## Instructions for Claude

When the user invokes `/twelvelabs:videos`, parse `$ARGUMENTS`.

### Step 1: Determine the Index

If an index ID was provided in `$ARGUMENTS`, use it directly.

If no index ID was provided, first call `mcp__twelvelabs-mcp__list-indexes` to find available indexes. If there is only one index, use it automatically. If there are multiple, ask the user to choose — **always show the Index ID** in the selection table:

```
Which index would you like to list videos from?

| # | Index ID | Name | Videos |
|---|----------|------|--------|
| 1 | abc123   | my-videos | 5 |
| 2 | def456   | tutorials | 3 |
```

### Step 2: Call the MCP Tool

Use the `mcp__twelvelabs-mcp__list-videos` tool:

```
Tool: mcp__twelvelabs-mcp__list-videos
Parameters:
  indexId: "<index-id>"
```

### Step 3: Display Results

```
Indexed Videos

| Video ID | Filename |
|----------|----------|
| <id1>    | <name1>  |
| <id2>    | <name2>  |

Total: <count> videos
```

If pagination is available:
```
Indexed Videos (Page 1)

| Video ID | Filename |
|----------|----------|
| <id1>    | <name1>  |

Showing <count> videos. More available — ask to see the next page.
```

If no videos found:
```
No indexed videos found.

To index a video, use: /twelvelabs:index-video <path-or-url>
```

## Important Notes

- **Default Index**: When no index ID is specified, the default index is used
- **Video IDs**: Use these IDs with `/twelvelabs:analyze` and `/twelvelabs:search`
- **Pagination**: Large lists may be paginated — ask to see more if needed

## Related Commands

- `/twelvelabs:index-video` - Index a new video
- `/twelvelabs:index-video status` - Check indexing task status
- `/twelvelabs:search` - Search indexed videos
- `/twelvelabs:analyze` - Analyze indexed videos
