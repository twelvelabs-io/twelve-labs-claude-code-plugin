---
name: entity-delete
description: Delete an entity from a collection
disable-model-invocation: true
argument-hint: <collection-id> <entity-id>
---

# /twelvelabs:entity-delete - Delete an Entity

Delete a specific entity from an entity collection.

## Usage

```
/twelvelabs:entity-delete <collection-id> <entity-id>
```

**User provided:** `$ARGUMENTS`

## Arguments

- `collection-id` - **Required**. ID of the entity collection
- `entity-id` - **Required**. ID of the entity to delete

## Examples

```
/twelvelabs:entity-delete abc123 def456
```

## Instructions for Claude

When the user invokes `/twelvelabs:entity-delete`, parse `$ARGUMENTS`.

### Step 1: Parse Arguments

Extract the collection ID and entity ID from `$ARGUMENTS`.

- First token: collection ID
- Second token: entity ID

If arguments are incomplete:
```
Usage: /twelvelabs:entity-delete <collection-id> <entity-id>

Arguments:
  collection-id   ID of the entity collection
  entity-id       ID of the entity to delete

List entities with: /twelvelabs:entity-list <collection-id>
```

### Step 2: Confirm Deletion

Warn the user before proceeding:
```
This will permanently delete the entity. Continue?
```

### Step 3: Delete the Entity

```
Tool: mcp__twelvelabs-mcp__delete-entity
Parameters:
  collectionId: "<collection-id>"
  entityId: "<entity-id>"
```

### Step 4: Report Result

On success:
```
Entity <entity-id> deleted.
```

On failure: Report the error message.

## Related Commands

- `/twelvelabs:entity-list` - List entities in a collection
- `/twelvelabs:entity-create` - Create entities from reference images
- `/twelvelabs:entity-collection` - Manage entity collections
