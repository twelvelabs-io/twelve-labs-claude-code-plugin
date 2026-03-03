---
name: entity-asset
description: Upload reference images for entity search
disable-model-invocation: true
argument-hint: [path-or-url]
---

# /twelvelabs:entity-asset - Upload Reference Images

Upload reference images as assets for entity search. These images are used to identify people or objects in your videos.

## Usage

```
/twelvelabs:entity-asset <path-or-url>
```

**User provided:** `$ARGUMENTS`

## Arguments

- `path-or-url` - **Required**. Either:
  - Local file path (absolute or relative) to an image
  - Publicly accessible image URL

## Supported Image Formats

- `.jpg` / `.jpeg`
- `.png`
- `.webp`

## Examples

```
/twelvelabs:entity-asset ./sarah-headshot.jpg
/twelvelabs:entity-asset /Users/me/photos/john.png
/twelvelabs:entity-asset https://example.com/photo.jpg
```

## Instructions for Claude

When the user invokes `/twelvelabs:entity-asset`, the argument is in `$ARGUMENTS`.

### Step 1: Validate Input

If `$ARGUMENTS` is empty:
```
Please provide an image path or URL.
Usage: /twelvelabs:entity-asset <path-or-url>
```

### Step 2: Determine Input Type

- **URL**: Starts with `http://` or `https://`
- **Local file**: Everything else

### Step 3: Upload the Asset

#### For URLs:
```
Tool: mcp__twelvelabs-mcp__create-asset
Parameters:
  imageUrl: "<url>"
```

#### For local files:
1. Resolve to absolute path if relative
2. Verify the file exists

```
Tool: mcp__twelvelabs-mcp__create-asset
Parameters:
  imageFile: "<absolute-path>"
```

### Step 4: Report Result

On success:
```
Reference image uploaded.

Asset ID: <id>

Use this asset ID when creating an entity:
/twelvelabs:entity-create <collection-id> <name> <asset-id>
```

On failure: Report the error message.

## Tips

- Use **3-5 reference images** from different angles for best accuracy
- Images should clearly show the person's face
- Upload multiple images, then use all asset IDs when creating the entity

## Related Commands

- `/twelvelabs:entity-collection` - Manage entity collections
- `/twelvelabs:entity-create` - Create entities from reference images
- `/twelvelabs:entity-search` - Search for entities in videos
