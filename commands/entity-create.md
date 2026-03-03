---
name: entity-create
description: Create an entity from reference images for video search
disable-model-invocation: true
argument-hint: <collection-id> <name> <asset-ids...>
---

# /twelvelabs:entity-create - Create an Entity

Create a named entity (person or object) within a collection, linking it to reference image assets. Once created, you can search for this entity across your indexed videos.

## Usage

```
/twelvelabs:entity-create <collection-id> <name> <asset-id-1> [asset-id-2] ...
```

**User provided:** `$ARGUMENTS`

## Arguments

- `collection-id` - **Required**. ID of the entity collection
- `name` - **Required**. Name for the entity (e.g. person's name)
- `asset-ids` - **Required**. One or more asset IDs (reference images uploaded via `/twelvelabs:entity-asset`)

## Examples

```
/twelvelabs:entity-create abc123 "Sarah Chen" asset_001
/twelvelabs:entity-create abc123 "Sarah Chen" asset_001 asset_002 asset_003
```

## Instructions for Claude

When the user invokes `/twelvelabs:entity-create`, parse `$ARGUMENTS`.

### Step 1: Parse Arguments

Extract collection ID, entity name, and asset IDs from `$ARGUMENTS`.

- First token: collection ID
- Quoted string or next token: entity name
- Remaining tokens: asset IDs (at least one required)

If arguments are incomplete:
```
Usage: /twelvelabs:entity-create <collection-id> <name> <asset-id-1> [asset-id-2...]

Arguments:
  collection-id   ID of the entity collection
  name            Name of the entity (quote if it contains spaces)
  asset-ids       One or more asset IDs from /twelvelabs:entity-asset

Example:
  /twelvelabs:entity-create abc123 "Sarah Chen" asset_001 asset_002

Steps:
  1. /twelvelabs:entity-collection create "My Collection"
  2. /twelvelabs:entity-asset ./photo1.jpg
  3. /twelvelabs:entity-asset ./photo2.jpg
  4. /twelvelabs:entity-create <collection-id> "Name" <asset-id-1> <asset-id-2>
```

### Step 2: Create the Entity

```
Tool: mcp__twelvelabs-mcp__create-entity
Parameters:
  collectionId: "<collection-id>"
  name: "<entity name>"
  assetIds: ["<asset-id-1>", "<asset-id-2>"]
```

### Step 3: Report Result

On success:
```
Entity created.

Entity ID: <id>
Name: <name>

Search for this entity:
/twelvelabs:entity-search <@<id>>
/twelvelabs:entity-search <@<id>> is giving a presentation
```

On failure: Report the error message.

## Related Commands

- `/twelvelabs:entity-collection` - Manage entity collections
- `/twelvelabs:entity-asset` - Upload reference images
- `/twelvelabs:entity-list` - List entities in a collection
- `/twelvelabs:entity-delete` - Delete an entity from a collection
- `/twelvelabs:entity-search` - Search for entities in videos
