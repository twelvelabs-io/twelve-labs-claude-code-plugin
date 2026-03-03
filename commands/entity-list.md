---
name: entity-list
description: List all entities in an entity collection
disable-model-invocation: true
argument-hint: <collection-id>
---

# /twelvelabs:entity-list - List Entities in a Collection

List all entities within a specific entity collection, showing their names, IDs, and search syntax.

## Usage

```
/twelvelabs:entity-list <collection-id>
```

**User provided:** `$ARGUMENTS`

## Arguments

- `collection-id` - **Required**. ID of the entity collection

## Examples

```
/twelvelabs:entity-list abc123
```

## Instructions for Claude

When the user invokes `/twelvelabs:entity-list`, parse `$ARGUMENTS`.

### Step 1: Parse Arguments

Extract the collection ID from `$ARGUMENTS`.

If no collection ID provided:
```
Please provide a collection ID.
Usage: /twelvelabs:entity-list <collection-id>

List collections with: /twelvelabs:entity-collection list
```

### Step 2: List Entities

```
Tool: mcp__twelvelabs-mcp__list-entities
Parameters:
  collectionId: "<collection-id>"
```

### Step 3: Report Result

On success, display each entity's name, ID, and search syntax:
```
Entities in collection <collection-id>:

- <name> (ID: <id>)
  Search: /twelvelabs:entity-search <@<id>> <action>
```

If no entities found:
```
No entities found in this collection.

Create one:
  1. /twelvelabs:entity-asset <image-path-or-url>
  2. /twelvelabs:entity-create <collection-id> "Name" <asset-id>
```

On failure: Report the error message.

## Related Commands

- `/twelvelabs:entity-collection` - Manage entity collections
- `/twelvelabs:entity-create` - Create entities from reference images
- `/twelvelabs:entity-delete` - Delete an entity from a collection
- `/twelvelabs:entity-search` - Search for entities in videos
