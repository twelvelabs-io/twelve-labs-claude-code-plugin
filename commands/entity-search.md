---
name: entity-search
description: Search for specific people or objects in videos using entity recognition
disable-model-invocation: true
argument-hint: <@entity_id> [action description]
---

# /twelvelabs:entity-search - Entity Search

Search for specific people or objects in your indexed videos using a registered entity. Requires Marengo 3.0.

## Usage

```
/twelvelabs:entity-search <@entity_id> [action description]
```

**User provided:** `$ARGUMENTS`

## Arguments

- `<@entity_id>` - **Required**. Entity ID wrapped in `<@` and `>`
- `action description` - Optional. Describe what the entity is doing

## Examples

```
/twelvelabs:entity-search <@abc123>
/twelvelabs:entity-search <@abc123> is giving a presentation
/twelvelabs:entity-search <@abc123> is walking
```

## Instructions for Claude

When the user invokes `/twelvelabs:entity-search`, the query is in `$ARGUMENTS`.

### Step 1: Validate Query

Check that `$ARGUMENTS` contains `<@`:

If empty or missing entity ID:
```
Please provide an entity ID to search for.

Usage: /twelvelabs:entity-search <@entity_id> [action description]

Examples:
  /twelvelabs:entity-search <@abc123>
  /twelvelabs:entity-search <@abc123> is giving a presentation

Don't have an entity yet? Set one up:
  1. /twelvelabs:entity-collection create "My Collection"
  2. /twelvelabs:entity-asset ./reference-photo.jpg
  3. /twelvelabs:entity-create <collection-id> "Name" <asset-id>
```

### Step 2: Search

Use the full `$ARGUMENTS` as the query:

```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  query: "<full $ARGUMENTS value>"
```

### Step 3: Display Results

Format results the same way as `/twelvelabs:search`:
- Filename of the video (if available)
- Stream URL (if available)
- Bulleted list of matching segments with start/end timestamps

If no results:
```
No matches found for this entity.

Tips:
- Try searching without an action description: /twelvelabs:entity-search <@entity_id>
- Make sure your videos are indexed with Marengo 3.0
- Check indexing status with /twelvelabs:status
```

## Related Commands

- `/twelvelabs:entity-collection` - Create and manage entity collections
- `/twelvelabs:entity-asset` - Upload reference images
- `/twelvelabs:entity-create` - Create entities from reference images
- `/twelvelabs:search` - Text-based video search
