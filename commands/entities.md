---
name: entities
description: Manage entity collections and entities for video search
disable-model-invocation: true
argument-hint: <subcommand>
---

# /twelvelabs:entities - Manage Entities

Manage entity collections and entities for entity-based video search. Requires Marengo 3.0.

For uploading the reference images themselves, use `/twelvelabs:assets upload <path-or-url>`.

## Usage

```
/twelvelabs:entities create-collection <name>
/twelvelabs:entities list-collections
/twelvelabs:entities create-entity <collection-id> <name> <asset-ids...>
/twelvelabs:entities list-entities <collection-id>
/twelvelabs:entities delete-entity <collection-id> <entity-id>
/twelvelabs:entities delete-collection <collection-id>
```

**User provided:** `$ARGUMENTS`

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `create-collection` | Create a new entity collection |
| `list-collections` | List all entity collections |
| `create-entity` | Create a named entity from reference image assets |
| `list-entities` | List entities in a collection |
| `delete-entity` | Delete an entity from a collection |
| `delete-collection` | Delete an entire collection |

## Examples

### Create a Collection
```
/twelvelabs:entities create-collection "Team Alpha"
```

### Upload Reference Images

Reference images for entities are uploaded via the dedicated `/twelvelabs:assets` command:
```
/twelvelabs:assets upload ./sarah-headshot.jpg
/twelvelabs:assets upload https://example.com/photo.jpg
```

### List Collections
```
/twelvelabs:entities list-collections
```

### List Entities in a Collection
```
/twelvelabs:entities list-entities abc123
```

### Create an Entity
```
/twelvelabs:entities create-entity abc123 "Sarah Chen" asset_001
/twelvelabs:entities create-entity abc123 "Sarah Chen" asset_001 asset_002 asset_003
```

### Delete an Entity
```
/twelvelabs:entities delete-entity abc123 entity_456
```

### Delete a Collection
```
/twelvelabs:entities delete-collection abc123
```

## Instructions for Claude

When the user invokes `/twelvelabs:entities`, parse `$ARGUMENTS` to determine the subcommand.

If `$ARGUMENTS` is empty or not recognized:
```
Usage: /twelvelabs:entities <subcommand>

Subcommands:
  create-collection <name>               Create a new entity collection
  list-collections                       List all collections
  create-entity <collection-id> <name> <ids>  Create an entity from reference image assets
  list-entities <collection-id>          List entities in a collection
  delete-entity <collection-id> <entity-id>  Delete an entity
  delete-collection <collection-id>      Delete an entire collection

To upload reference images for an entity, use /twelvelabs:assets upload <path-or-url>.

Quick start: /twelvelabs:entities create-collection "My Collection"
```

---

### Subcommand: `create-collection`

Extract the collection name from the remaining arguments.

If no name provided:
```
Please provide a name for the collection.
Usage: /twelvelabs:entities create-collection <name>
```

```
Tool: mcp__twelvelabs-mcp__create-entity-collection
Parameters:
  name: "<collection name>"
```

On success:
```
Collection created.

Collection ID: <id>
Name: <name>

Next steps:
  1. /twelvelabs:assets upload <image-path-or-url>     Upload reference images
  2. /twelvelabs:entities create-entity <collection-id> "Name" <asset-id>   Create an entity
```

---

### Subcommand: `list-collections`

```
Tool: mcp__twelvelabs-mcp__list-entity-collections
```

Display each collection's ID and name. If none exist:
```
No entity collections found.

Create one with: /twelvelabs:entities create-collection <name>
```

---

### Subcommand: `list-entities`

Extract the collection ID from the remaining arguments.

If no collection ID provided:
```
Please provide a collection ID.
Usage: /twelvelabs:entities list-entities <collection-id>

List collections: /twelvelabs:entities list-collections
```

```
Tool: mcp__twelvelabs-mcp__list-entities
Parameters:
  collectionId: "<collection-id>"
```

Display each entity's name, ID, and search syntax:
```
Entities in collection <collection-id>:

- <name> (ID: <id>)
  Search: /twelvelabs:search <@<id>> <action>
```

If no entities found:
```
No entities found in this collection.

Create one:
  1. /twelvelabs:assets upload <image-path-or-url>
  2. /twelvelabs:entities create-entity <collection-id> "Name" <asset-id>
```

---

### Subcommand: `create-entity`

Parse the remaining arguments:
- First token: collection ID
- Quoted string or next token: entity name
- Remaining tokens: asset IDs (at least one required)

If arguments are incomplete:
```
Usage: /twelvelabs:entities create-entity <collection-id> <name> <asset-id-1> [asset-id-2...]

Example:
  /twelvelabs:entities create-entity abc123 "Sarah Chen" asset_001 asset_002

Steps to get here:
  1. /twelvelabs:entities list-collections          (find your collection ID)
  2. /twelvelabs:assets upload ./photo1.jpg        (get asset IDs)
  3. /twelvelabs:assets upload ./photo2.jpg
  4. /twelvelabs:entities create-entity <collection-id> "Name" <asset-id-1> <asset-id-2>
```

Create the entity:
```
Tool: mcp__twelvelabs-mcp__create-entity
Parameters:
  collectionId: "<collection-id>"
  name: "<entity name>"
  assetIds: ["<asset-id-1>", "<asset-id-2>"]
```

On success:
```
Entity created.

Entity ID: <id>
Name: <name>

Search for this entity:
  /twelvelabs:search <@<id>>
  /twelvelabs:search <@<id>> is giving a presentation
```

---

### Subcommand: `delete-entity`

Extract the collection ID and entity ID from the remaining arguments.

If arguments are incomplete:
```
Usage: /twelvelabs:entities delete-entity <collection-id> <entity-id>

List entities: /twelvelabs:entities list-entities <collection-id>
```

Warn the user: "This will permanently delete the entity. Continue?"

```
Tool: mcp__twelvelabs-mcp__delete-entity
Parameters:
  collectionId: "<collection-id>"
  entityId: "<entity-id>"
```

On success: "Entity `<entity-id>` deleted from collection `<collection-id>`."

---

### Subcommand: `delete-collection`

Extract the collection ID from the remaining arguments.

If no collection ID provided:
```
Usage: /twelvelabs:entities delete-collection <collection-id>

List collections: /twelvelabs:entities list-collections
```

Warn the user: "This will permanently delete the collection and all entities in it. Continue?"

```
Tool: mcp__twelvelabs-mcp__delete-entity-collection
Parameters:
  collectionId: "<collection-id>"
```

On success: "Collection `<id>` deleted."

## Related Commands

- `/twelvelabs:assets` - Upload reference images / delete assets (used to create entities)
- `/twelvelabs:search` - Search for entities in videos using `<@entity_id>`
- `/twelvelabs:index-video` - Index videos for entity search
- `/twelvelabs:help` - Show all available commands
