---
name: list
description: List indexed videos and available indexes. Use when user wants to know what videos they have indexed, asks "what videos do I have?", "show my videos", or needs to find a video ID for analysis.
---

# List Indexed Videos and Indexes

List all indexed videos or available indexes to help users discover what content is available for search and analysis.

## When to Use This Skill

Use this skill when the user:
- Asks what videos they have ("what videos do I have?", "show my videos")
- Wants to see indexed content ("do I have any videos indexed?", "list my videos")
- Needs to find a video ID ("which videos are available?", "what can I search?")
- Asks about indexes ("show my indexes", "what indexes do I have?")

## Instructions

### Step 1: Determine What to List

Based on the user's request:

- **Videos** (default): User asks about videos, content, or what they can search/analyze
- **Indexes**: User specifically asks about indexes or collections

### Step 2: Call the Appropriate MCP Tool

**For listing videos** (default):
```
Tool: mcp__twelvelabs-mcp__list-videos
Parameters: (none - uses default index)
```

To list videos from a specific index:
```
Tool: mcp__twelvelabs-mcp__list-videos
Parameters:
  indexId: "<index-id>"
```

**For listing indexes**:
```
Tool: mcp__twelvelabs-mcp__list-indexes
Parameters: (none)
```

### Step 3: Display Results

**For videos (with results)**:
```
Your Indexed Videos

| Video ID | Filename |
|----------|----------|
| abc123   | demo.mp4 |
| def456   | meeting-2024-01-15.mp4 |
| ghi789   | tutorial-part1.mov |

Total: 3 videos

You can:
- Search any video: "find the part where someone mentions pricing"
- Analyze a video: "summarize video abc123" or "create chapters for the demo"
```

**For videos (no results)**:
```
No indexed videos found.

To get started:
1. Index a video: "index this video: /path/to/video.mp4"
2. Or try a sample: "I don't have a video to test"

Once indexed, you can search and analyze your videos with natural language.
```

**For videos (with pagination)**:
```
Your Indexed Videos (Page 1)

| Video ID | Filename |
|----------|----------|
| abc123   | demo.mp4 |
| def456   | meeting.mp4 |
... (showing 10 videos)

More videos available. Ask to see the next page.
```

**For indexes (with results)**:
```
Your Indexes

| Index ID | Name | Models |
|----------|------|--------|
| idx_abc  | default | marengo3.0 |
| idx_def  | archive | marengo3.0 |

Total: 2 indexes

Indexes use Marengo 3.0 for search and embeddings. Analysis doesn't need an index.
```

Show each model's raw `modelName` from the response. Older indexes may also list a `generative` (Pegasus) model; the plugin doesn't use it — analysis runs Pegasus directly on the video.

**For indexes (no results)**:
```
No indexes found.

A default index will be created automatically when you index your first video.
To get started: "index this video: /path/to/video.mp4"
```

### Step 4: Offer Next Steps

After listing, suggest relevant actions:

- If videos exist: Suggest searching or analyzing
- If no videos: Guide to indexing or sample videos
- If listing indexes: Explain the model capabilities

## Example Interactions

**User**: "What videos do I have?"
**Action**: Call list-videos → display table of videos with helpful tips

**User**: "Do I have any videos indexed?"
**Action**: Call list-videos → show results or guide to indexing

**User**: "Show me my indexes"
**Action**: Call list-indexes → display table with model info

**User**: "Which videos can I search?"
**Action**: Call list-videos → all listed videos are searchable

**User**: "I need the video ID for my demo"
**Action**: Call list-videos → help user find the matching video ID

## Important Notes

- **Default Index**: Videos are listed from the default index unless specified otherwise
- **Video IDs**: These IDs are used for targeted search and analysis operations
- **Models**: `list-indexes` labels each model (`embedding` = Marengo search/embeddings) and includes the raw `modelName`. New indexes are Marengo 3.0 only. Analysis (sync/async) doesn't depend on the index's models.
- **Pagination**: Large lists may be paginated - offer to show more if needed
