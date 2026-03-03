---
name: entity-search
description: Set up and search for specific people or objects in videos using entity search. Use when the user wants to find a specific person, track someone across videos, or set up face/object recognition. Triggers on phrases like "find this person", "set up entity search", "track this person in my videos", "who is in this video".
---

# Entity Search - Find Specific People in Videos

Find specific people or objects in your indexed videos using reference images. Entity search lets you register a person with reference photos, then search for them across all your videos.

## When to Use This Skill

Use this skill when the user:
- Wants to find a specific person in their videos
- Asks to set up face recognition or person tracking
- Has reference images of someone they want to locate in video content
- Wants to search for a known individual (e.g., "find all clips of John")

## Prerequisites

- Videos must be indexed with **Marengo 3.0** (entity search is a Marengo 3.0 feature)
- Reference images of the person/object (publicly accessible URLs or local file paths)
- Free plan: 1 collection, up to 15 entities. Developer plan: multiple collections.

## Instructions

### Step 1: Check for Existing Entity Collections

First check if the user already has entity collections set up:

```
Tool: mcp__twelvelabs-mcp__list-entity-collections
```

If collections exist, show them and ask if the user wants to use an existing one or create a new one.

### Step 2: Create an Entity Collection (if needed)

An entity collection groups related entities. Create one per logical group (e.g., "Team A", "Film Cast").

```
Tool: mcp__twelvelabs-mcp__create-entity-collection
Parameters:
  name: "<collection name>"
```

### Step 3: Upload Reference Images as Assets

Upload one or more reference images for the person. Multiple images from different angles and lighting improve accuracy.

**From a URL**:
```
Tool: mcp__twelvelabs-mcp__create-asset
Parameters:
  imageUrl: "<publicly accessible image URL>"
```

**From a local file**:
```
Tool: mcp__twelvelabs-mcp__create-asset
Parameters:
  imageFilePath: "<absolute path to image file>"
```

Repeat for each reference image. Collect all returned asset IDs.

### Step 4: Create the Entity

Create an entity within the collection, linking it to the reference image assets:

```
Tool: mcp__twelvelabs-mcp__create-entity
Parameters:
  collectionId: "<collection ID from step 2>"
  name: "<person's name>"
  assetIds: ["<asset_id_1>", "<asset_id_2>"]
```

The response will include the entity ID and the search query format.

### Step 5: Search for the Entity

Use the search tool with the entity ID in the query:

```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  query: "<@entity_id> action description"
```

**Query format**: Wrap the entity ID with `<@` and `>`, then add an optional action description.

**Examples**:
- `<@abc123>` - find all appearances
- `<@abc123> is giving a presentation` - find specific actions
- `<@abc123> is walking` - find movement scenes

### Step 6: Display Results

Format results the same way as regular search:
- Filename of the video
- Stream URL (if available)
- Bulleted list of matching segments with timestamps

## Managing Entities

**List entities in a collection**:
```
Tool: mcp__twelvelabs-mcp__list-entities
Parameters:
  collectionId: "<collection ID>"
```

**Delete an entity**:
```
Tool: mcp__twelvelabs-mcp__delete-entity
Parameters:
  collectionId: "<collection ID>"
  entityId: "<entity ID>"
```

**Delete a collection**:
```
Tool: mcp__twelvelabs-mcp__delete-entity-collection
Parameters:
  collectionId: "<collection ID>"
```

## Example Interaction

**User**: "I want to find all clips of Sarah in my videos. Here's her photo: https://example.com/sarah.jpg"

**Steps**:
1. Create entity collection "People"
2. Create asset from the photo URL
3. Create entity "Sarah" with the asset
4. Search with `<@entity_id>` query
5. Display matching segments

## Tips for Better Results

- Use **3-5 reference images** from different angles for best accuracy
- Images should clearly show the person's face
- Separate unrelated groups into different collections
- The `visual` and `audio` search options are used for entity search

## Important Notes

- **Marengo 3.0 Required**: Entity search only works with indexes created using Marengo 3.0
- **Beta Feature**: Entity search is currently in beta
- **Plan Limits**: Free plan allows 1 collection with up to 15 entities
