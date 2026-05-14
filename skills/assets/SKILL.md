---
name: assets
description: Upload, list, or delete TwelveLabs assets — generic reference files (images or videos) used by entities and async-analyze. Triggers on "upload this image", "upload this video as an asset", "delete that asset", or any explicit asset-management request.
---

# Manage Assets

Assets are uploaded media files (images or videos) referenced by ID in downstream tools. Image assets are used as reference images for entity search; video assets are used as input to async-analyze without prior indexing.

## When to Use This Skill

Use this skill when the user:
- Says "upload this image/video as an asset"
- Wants to delete a specific asset by ID
- Wants to pre-upload media before using `/twelvelabs:entities` or `/twelvelabs:async-analyze`

Do **not** use this skill when the user just says "analyze this video" — `/twelvelabs:async-analyze` handles asset upload internally for local files. Asset management is for explicit reuse.

## Instructions

### Step 1: Identify the Action

Determine from the user's message whether they want to:
- **Upload** an image or video as an asset (path or URL)
- **Delete** an existing asset by ID

### Step 2: Upload

Detect input type:
- **URL**: Starts with `http://` or `https://`
- **Local file**: Resolve to absolute path; verify exists

For URLs:
```
Tool: mcp__twelvelabs-mcp__create-asset
Parameters:
  url: "<url>"
```

For local files:
```
Tool: mcp__twelvelabs-mcp__create-asset
Parameters:
  file: "<absolute-path>"
```

Report the returned `Asset ID` and `File Type`. Suggest the next step:
- Image asset → use with `/twelvelabs:entities create-entity`
- Video asset → use with `/twelvelabs:async-analyze`

### Step 3: Delete

Confirm with the user before deleting (the action is irreversible).

```
Tool: mcp__twelvelabs-mcp__delete-asset
Parameters:
  assetId: "<asset-id>"
```

If the API returns a conflict (asset is referenced by an indexed video), offer to retry with `force=true`.

## Notes

- The MCP tool infers asset type from file content; no explicit type parameter is needed.
- Image formats supported: jpg, jpeg, png, webp.
- Video formats supported: mp4, mov, avi, mkv, webm.
- Assets persist until explicitly deleted.
