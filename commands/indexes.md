---
name: indexes
description: List, create, or delete your TwelveLabs indexes
disable-model-invocation: true
argument-hint: [create | delete] [args]
---

# /twelvelabs:indexes - Manage Indexes

List your TwelveLabs indexes, create new ones, or delete existing ones.

## Usage

```
/twelvelabs:indexes
/twelvelabs:indexes create <name> [model]
/twelvelabs:indexes delete <index-id>
```

**User provided:** `$ARGUMENTS`

## Arguments

- *(no arguments)* — List all available indexes
- `create <name> [model]` — Create a new index with the given name and optional model
- `delete <index-id>` — Delete an index

## Models

| Model | Purpose |
|-------|---------|
| `marengo` | Search — visual, text-in-video, conversational search, image search, entity search |
| `pegasus` | Generation — summarization, chapters, highlights, open-ended text |

By default, both marengo and pegasus are enabled. Specify one to create a single-model index.

## Examples

```
/twelvelabs:indexes
/twelvelabs:indexes create "marketing-videos"
/twelvelabs:indexes create "search-index" marengo
/twelvelabs:indexes create "generation-index" pegasus
/twelvelabs:indexes delete abc123
```

## Instructions for Claude

When the user invokes `/twelvelabs:indexes`, parse `$ARGUMENTS` to determine the action.

If `$ARGUMENTS` is empty: **list indexes**.
If `$ARGUMENTS` starts with `create`: **create an index**.
If `$ARGUMENTS` starts with `delete`: **delete an index**.

If `$ARGUMENTS` doesn't match any pattern:
```
Usage: /twelvelabs:indexes [command]

Commands:
  (none)                   List all indexes
  create <name> [model]    Create a new index
  delete <index-id>        Delete an index

Models:
  marengo   - Search (visual, text, conversational, image, entity)
  pegasus   - Generation (summaries, chapters, highlights)
  (default) - Both marengo and pegasus

Examples:
  /twelvelabs:indexes
  /twelvelabs:indexes create "marketing-videos"
  /twelvelabs:indexes create "search-index" marengo
  /twelvelabs:indexes delete abc123
```

---

### List Indexes (default)

```
Tool: mcp__twelvelabs-mcp__list-indexes
```

#### Display Results

```
Available Indexes

| Index ID | Name | Models |
|----------|------|--------|
| <id1>    | <name1> | <models1> |
| <id2>    | <name2> | <models2> |

Total: <count> indexes
```

If no indexes found:
```
No indexes found.

Create one with: /twelvelabs:indexes create <name>

A default index is also created automatically when you index your first video.
```

---

### Create

Extract the index name and optional model from `$ARGUMENTS` (everything after `create`).

- First token (or quoted string): index name
- Second token (optional): model name

If no name provided:
```
Please provide a name for the index.

Usage: /twelvelabs:indexes create <name> [model]

Models:
  marengo   - Search (visual, text, conversational, image, entity)
  pegasus   - Generation (summaries, chapters, highlights)
  (default) - Both marengo and pegasus

Examples:
  /twelvelabs:indexes create "marketing-videos"
  /twelvelabs:indexes create "search-index" marengo
```

Map the model name to the API `models` array:
- `marengo` → `["embedding"]`
- `pegasus` → `["generative"]`
- nothing (default) → `["embedding", "generative"]`

The user may also use versioned names like `marengo3.0` or `pegasus3.0` — treat these the same as the base name.

```
Tool: mcp__twelvelabs-mcp__create-index
Parameters:
  name: "<index name>"
  models: ["<model1>", "<model2>"]
```

On success:
```
Index created!

Index ID: <id>
Name: <name>
Models: <models>

Next: /twelvelabs:index-video <path-or-url>    Index a video into this index
```

On failure: Report the error message.

---

### Delete

Extract the index ID from `$ARGUMENTS` (everything after `delete`).

If no index ID provided:
```
Please provide an index ID.
Usage: /twelvelabs:indexes delete <index-id>

List indexes with: /twelvelabs:indexes
```

Warn the user: "This will permanently delete the index and all videos in it. Continue?"

```
Tool: mcp__twelvelabs-mcp__delete-index
Parameters:
  indexId: "<index-id>"
```

On success: "Index `<index-id>` deleted."
On failure: Report the error message.

## Important Notes

- **Default**: Both marengo (search) and pegasus (generation) are enabled
- **Marengo**: Required for `/twelvelabs:search` including image and entity search
- **Pegasus**: Required for `/twelvelabs:analyze` (summaries, chapters, etc.)
- **Deletion**: Deleting an index removes all videos in it permanently

## Related Commands

- `/twelvelabs:index-video` - Index videos into an index
- `/twelvelabs:videos` - List indexed videos
- `/twelvelabs:help` - Show all available commands
