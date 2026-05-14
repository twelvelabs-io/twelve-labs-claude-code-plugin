---
name: assets
description: Upload, list, or delete TwelveLabs assets (reference images and video uploads)
disable-model-invocation: true
argument-hint: "upload <path-or-url> | delete <asset-id>"
---

# /twelvelabs:assets - Manage Assets

Manage TwelveLabs assets. An asset is any uploaded media file (image or video) that can be referenced by ID in other tools:

- **Image assets** — used as reference images for entity search (see `/twelvelabs:entities`).
- **Video assets** — used as input to `/twelvelabs:async-analyze` (analyse a video without indexing it).

## Usage

```
/twelvelabs:assets upload <path-or-url>
/twelvelabs:assets delete <asset-id>
```

**User provided:** `$ARGUMENTS`

## Subcommands

| Subcommand | Description |
|------------|-------------|
| `upload` | Upload an image or video file as an asset (local path or http(s) URL) |
| `delete` | Delete an asset by ID |

## Examples

```
/twelvelabs:assets upload ./sarah-headshot.jpg
/twelvelabs:assets upload /Users/me/videos/keynote.mp4
/twelvelabs:assets upload https://example.com/photo.jpg
/twelvelabs:assets delete asset_abc123
```

## Instructions for Claude

When the user invokes `/twelvelabs:assets`, parse `$ARGUMENTS` to determine the subcommand.

If `$ARGUMENTS` is empty or not recognized:
```
Usage: /twelvelabs:assets <subcommand>

Subcommands:
  upload <path-or-url>     Upload a local file or remote URL as an asset
  delete <asset-id>        Delete an asset by ID

Examples:
  /twelvelabs:assets upload ./photo.jpg
  /twelvelabs:assets upload https://example.com/video.mp4
  /twelvelabs:assets delete asset_abc123
```

---

### Subcommand: `upload`

Extract the path or URL from the remaining arguments.

If no path/URL provided:
```
Please provide a path or URL.
Usage: /twelvelabs:assets upload <path-or-url>
```

Determine input type:
- **URL**: Starts with `http://` or `https://`
- **Local file**: Everything else

#### Supported Formats
- **Images**: `.jpg`, `.jpeg`, `.png`, `.webp`
- **Videos**: `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`

#### For URLs:
```
Tool: mcp__twelvelabs-mcp__create-asset
Parameters:
  url: "<url>"
```

#### For local files:
1. Resolve to an absolute path if relative
2. Verify the file exists

```
Tool: mcp__twelvelabs-mcp__create-asset
Parameters:
  file: "<absolute-path>"
```

#### Report Result

On success:
```
Asset uploaded.

Asset ID: <id>
File Type: <image|video>

Use this asset ID with:
  /twelvelabs:entities create-entity <collection-id> <name> <asset-id>   (image)
  /twelvelabs:async-analyze <asset-id> "<prompt>"                         (video)
```

**Tips for entity reference images**: Use 3-5 reference images from different angles for best accuracy. Images should clearly show the person's face.

---

### Subcommand: `delete`

Extract the asset ID from the remaining arguments.

If no asset ID provided:
```
Usage: /twelvelabs:assets delete <asset-id>
```

Warn the user: "This will permanently delete the asset. If any indexed video references this asset, deletion will be rejected unless `force=true`. Continue?"

```
Tool: mcp__twelvelabs-mcp__delete-asset
Parameters:
  assetId: "<asset-id>"
```

If the API returns a conflict error (asset is referenced by an indexed video), offer to re-run with `force=true`:

```
Tool: mcp__twelvelabs-mcp__delete-asset
Parameters:
  assetId: "<asset-id>"
  force: true
```

On success:
```
Asset <id> deleted.
```

## Related

- `/twelvelabs:entities create-entity` - Use an image asset to create an entity
- `/twelvelabs:async-analyze` - Use a video asset as input for async analysis
- `/twelvelabs:index-video` - Index a video for search and sync analysis
