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
/twelvelabs:indexes create <name>
/twelvelabs:indexes delete <index-id>
```

**User provided:** `$ARGUMENTS`

## Arguments

- *(no arguments)* — List all available indexes
- `create <name>` — Create a new index with the given name
- `delete <index-id>` — Delete an index

## Model

Every index uses **Marengo 3.0**, the search and embedding model (visual, text-in-video, conversational search, image search, entity search). There is no model choice.

Indexes are for search and embeddings only. Video analysis (`/twelvelabs:sync-analyze`, `/twelvelabs:async-analyze`) runs on Pegasus directly and does not need an index.

## Examples

```
/twelvelabs:indexes
/twelvelabs:indexes create "marketing-videos"
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
  create <name>            Create a new index (Marengo 3.0 search/embedding)
  delete <index-id>        Delete an index

Examples:
  /twelvelabs:indexes
  /twelvelabs:indexes create "marketing-videos"
  /twelvelabs:indexes delete abc123
```

---

### List Indexes (default)

```
Tool: mcp__twelvelabs-mcp__list-indexes
Parameters: (none = page 1, 10 per page)
```

If the API response says more pages are available, surface this to the user and only fetch the next page after they confirm:

```
Tool: mcp__twelvelabs-mcp__list-indexes
Parameters:
  page: <next-page-number>
```

#### Display Results

```
Available Indexes

| Index ID | Name | Models |
|----------|------|--------|
| <id1>    | <name1> | <modelName1> |
| <id2>    | <name2> | <modelName2> |

Total: <count> indexes
```

For the Models column, show each model's raw `modelName` (e.g. `marengo3.0`) from the response. The `name` label (`embedding` / `generative`) is the server's category; older indexes may still list a `generative` (Pegasus) model, which the plugin no longer uses — analysis doesn't go through the index.

If no indexes found:
```
No indexes found.

Create one with: /twelvelabs:indexes create <name>

A default index is also created automatically when you index your first video.
```

---

### Create

Extract the index name from `$ARGUMENTS` (everything after `create`).

- First token (or quoted string): index name
- If a second token names a model (`marengo`, `pegasus`, `marengo3.0`, …), ignore it. If it was `pegasus`, tell the user indexes are search-only and analysis doesn't need an index.

If no name provided:
```
Please provide a name for the index.

Usage: /twelvelabs:indexes create <name>

Examples:
  /twelvelabs:indexes create "marketing-videos"
```

Don't pass `models` — it's deprecated. The server always creates a Marengo 3.0 index.

```
Tool: mcp__twelvelabs-mcp__create-index
Parameters:
  name: "<index name>"
  addons: ["thumbnail"]          # optional, default-on; omit to use the default
```

The `addons` parameter currently accepts only `"thumbnail"` (returns per-segment thumbnail URLs in search results). Enabled by default if omitted. Set `addons: []` to disable thumbnails.

> Note: `create-index` always creates a Marengo 3.0-only index (search and embeddings). If the response includes a note that a model was ignored, that's expected. To analyse videos, use `/twelvelabs:sync-analyze` or `/twelvelabs:async-analyze` — they run Pegasus 1.6 directly and don't need an index. An indexed video can still be analysed with `/twelvelabs:sync-analyze <videoId>`.

On success:
```
Index created!

Index ID: <id>
Name: <name>
Model: marengo3.0

Next: /twelvelabs:index-video <path-or-url>    Index a video into this index
```

On failure: Report the error message.

---

### Delete

Extract the index reference from `$ARGUMENTS` (everything after `delete`).

#### Step 1: Resolve the index ID

Classify the remaining argument:

- **24-char hex string** → that's the index ID directly. Skip to Step 2.
- **A name in quotes or a fuzzy reference** ("the index I just created", "marketing-videos", "the one from yesterday") → resolve it:
  1. Call `mcp__twelvelabs-mcp__list-indexes` to enumerate available indexes.
  2. Match the user's reference against the returned `name` field (case-insensitive, allow partial substring matches).
  3. If exactly one index matches → use its ID, proceed to Step 2.
  4. If multiple match or no match → show the user the list and ask them to pick by name or ID. **Do not guess.**
- **No argument at all** → list indexes and ask:
  ```
  Which index would you like to delete?

  | # | Index ID | Name | Videos |
  |---|----------|------|--------|
  | 1 | <id>     | <name> | <count> |
  | 2 | <id>     | <name> | <count> |

  Reply with a name or the index ID.
  ```

#### Step 2: Confirm + delete

Warn the user: "This will permanently delete the index `<name>` (`<id>`) and all videos in it. Continue?"

If the user has already authorised the deletion in their original request (e.g. "delete it" after listing, or an explicit "yes, delete X"), proceed without re-asking.

```
Tool: mcp__twelvelabs-mcp__delete-index
Parameters:
  indexId: "<index-id>"
```

On success: "Index `<name>` (`<index-id>`) deleted."
On failure: Report the error message.

## Important Notes

- **Model**: Every index is Marengo 3.0 (search and embeddings). There is no model choice.
- **Search**: `/twelvelabs:search` (including image and entity search) runs against an index
- **Analysis doesn't need an index**: `/twelvelabs:sync-analyze` and `/twelvelabs:async-analyze` run Pegasus 1.6 on a URL, asset, file, or indexed `videoId`
- **Deletion**: Deleting an index removes all videos in it permanently

## Related Commands

- `/twelvelabs:index-video` - Index videos into an index
- `/twelvelabs:videos` - List indexed videos
- `/twelvelabs:help` - Show all available commands
