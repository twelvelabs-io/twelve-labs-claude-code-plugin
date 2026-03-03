---
name: entity-collection
description: Create or list entity collections for grouping people/objects
disable-model-invocation: true
argument-hint: [create <name> | list | delete <id>]
---

# /twelvelabs:entity-collection - Manage Entity Collections

Create, list, or delete entity collections. Collections group related entities (people or objects) for entity search.

## Usage

```
/twelvelabs:entity-collection create <name>
/twelvelabs:entity-collection list
/twelvelabs:entity-collection delete <id>
```

**User provided:** `$ARGUMENTS`

## Arguments

- `create <name>` - Create a new collection with the given name
- `list` - List all existing collections
- `delete <id>` - Delete a collection by ID

## Examples

```
/twelvelabs:entity-collection create "Film Cast"
/twelvelabs:entity-collection create Team A
/twelvelabs:entity-collection list
/twelvelabs:entity-collection delete abc123
```

## Instructions for Claude

When the user invokes `/twelvelabs:entity-collection`, check `$ARGUMENTS`:

### If starts with "create"

Extract the collection name from the rest of the arguments.

If no name provided:
```
Please provide a collection name.
Usage: /twelvelabs:entity-collection create <name>
```

Call the MCP tool:
```
Tool: mcp__twelvelabs-mcp__create-entity-collection
Parameters:
  name: "<collection name>"
```

Display the result:
```
Entity collection created.

Collection ID: <id>
Name: <name>

Next: Upload reference images with /twelvelabs:entity-asset <image-path-or-url>
```

### If "list" or empty

```
Tool: mcp__twelvelabs-mcp__list-entity-collections
```

Display each collection's ID and name. If none exist:
```
No entity collections found.

Create one with: /twelvelabs:entity-collection create <name>
```

### If starts with "delete"

Extract the collection ID from the rest of the arguments.

If no ID provided:
```
Please provide a collection ID.
Usage: /twelvelabs:entity-collection delete <id>

List collections with: /twelvelabs:entity-collection list
```

```
Tool: mcp__twelvelabs-mcp__delete-entity-collection
Parameters:
  collectionId: "<id>"
```

Warn the user this deletes all entities in the collection before proceeding.

### Validation errors

If `$ARGUMENTS` doesn't match any pattern:
```
Usage: /twelvelabs:entity-collection <command>

Commands:
  create <name>    Create a new entity collection
  list             List all entity collections
  delete <id>      Delete an entity collection

Examples:
  /twelvelabs:entity-collection create "Film Cast"
  /twelvelabs:entity-collection list
```

## Related Commands

- `/twelvelabs:entity-asset` - Upload reference images
- `/twelvelabs:entity-create` - Create entities from reference images
- `/twelvelabs:entity-list` - List entities in a collection
- `/twelvelabs:entity-delete` - Delete an entity from a collection
- `/twelvelabs:entity-search` - Search for entities in videos
