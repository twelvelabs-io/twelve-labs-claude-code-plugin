---
name: help
description: Show TwelveLabs plugin help documentation
disable-model-invocation: true
---

# TwelveLabs Plugin Help

Welcome to the TwelveLabs Claude Code plugin! This plugin enables video AI capabilities including indexing, searching, and analyzing videos using TwelveLabs' multimodal AI platform.

## Quick Start

### 1. Index a Video

```
/twelvelabs:index-video /path/to/video.mp4
```
or from a URL:
```
/twelvelabs:index-video https://example.com/video.mp4
```

### 2. Check Indexing Status

```
/twelvelabs:index-video status
```

### 3. Search or Analyze

Once indexed, search your videos:
```
/twelvelabs:search "person walking in the park"
```

Or analyze for insights:
```
/twelvelabs:analyze <video-id>
```

---

## Commands

| Command | Description |
|---------|-------------|
| `/twelvelabs:index-video` | Index a video file or URL for AI analysis |
| `/twelvelabs:index-video status` | Check video indexing task status |
| `/twelvelabs:indexes` | List, create, or delete indexes |
| `/twelvelabs:videos` | List your indexed videos |
| `/twelvelabs:embed` | Create video embeddings or check embedding status |
| `/twelvelabs:search` | Search videos by text, image, or entity |
| `/twelvelabs:analyze` | Analyze video content for insights |
| `/twelvelabs:entities` | Manage entity collections and entities |
| `/twelvelabs:help` | Show this help documentation |

---

### `/twelvelabs:index-video`

Index a video file or URL for AI analysis, or check indexing status. Supports local files and remote URLs including Google Drive links.

**Usage:**
```
/twelvelabs:index-video <path-or-url>
/twelvelabs:index-video status [task-id]
```

**Supported formats:** MP4, MOV, AVI, MKV, WebM

**Examples:**
```
/twelvelabs:index-video ./video.mp4
/twelvelabs:index-video https://example.com/video.mp4
/twelvelabs:index-video https://drive.google.com/file/d/FILE_ID/view
/twelvelabs:index-video status
/twelvelabs:index-video status abc123
```

**Status values:** Validating → Pending → Queued → Indexing → Ready / Failed

**Note:** Video indexing is asynchronous. Use `/twelvelabs:index-video status` to check progress.

### `/twelvelabs:indexes`

List, create, or delete your TwelveLabs indexes.

**Usage:**
```
/twelvelabs:indexes                              # List all indexes
/twelvelabs:indexes create <name> [model]        # Create a new index
/twelvelabs:indexes delete <index-id>            # Delete an index
```

**Models:**
- `marengo` — Search: visual, text-in-video, conversational, image, entity
- `pegasus` — Generation: summaries, chapters, highlights
- *(default)* — Both marengo and pegasus

**Examples:**
```
/twelvelabs:indexes
/twelvelabs:indexes create "marketing-videos"
/twelvelabs:indexes create "search-index" marengo
/twelvelabs:indexes delete abc123
```

### `/twelvelabs:videos`

List your indexed videos.

**Usage:**
```
/twelvelabs:videos              # List videos in default index
/twelvelabs:videos <index-id>   # List videos in a specific index
```

**Examples:**
```
/twelvelabs:videos
/twelvelabs:videos abc123
```

### `/twelvelabs:embed`

Create video embeddings or check embedding task status.

**Usage:**
```
/twelvelabs:embed <path-or-url>
/twelvelabs:embed status [task-id]
```

**Examples:**
```
/twelvelabs:embed ./video.mp4
/twelvelabs:embed https://example.com/video.mp4
/twelvelabs:embed status
/twelvelabs:embed status abc123
```

**Note:** Embedding creation is asynchronous. Use `/twelvelabs:embed status` to check progress.

### `/twelvelabs:search`

Search indexed videos using text, images, entities, or combinations.

**Usage:**
```
/twelvelabs:search <query> [index-id]
/twelvelabs:search <image-url-or-path> [index-id]
/twelvelabs:search <image-url-or-path> <text query> [index-id]
/twelvelabs:search <@entity_id> [action] [index-id]
```

**Examples:**
```
/twelvelabs:search "person giving a presentation"
/twelvelabs:search "person giving a presentation" abc123
/twelvelabs:search https://example.com/car.jpg
/twelvelabs:search <@abc123> is walking
```

**Returns:** Matching video segments with timestamps, filenames, and stream URLs.
**Note:** Image and entity search require Marengo 3.0.

### `/twelvelabs:analyze`

Analyze video content to extract insights.

**Usage:**
```
/twelvelabs:analyze [video-id] [index-id] [prompt]
```

**Examples:**
```
/twelvelabs:analyze                                    # Analyze with video selection
/twelvelabs:analyze abc123                             # Analyze specific video
/twelvelabs:analyze abc123 idx789                      # Video from specific index
/twelvelabs:analyze abc123 "List all products mentioned"
/twelvelabs:analyze abc123 "What are the main topics?"
```

### `/twelvelabs:entities`

Manage entity collections, upload reference images, and create entities for entity-based video search.

**Usage:**
```
/twelvelabs:entities create-collection <name>               # Create a collection
/twelvelabs:entities upload <path-or-url>                   # Upload reference image
/twelvelabs:entities list-collections                       # List all collections
/twelvelabs:entities list-entities <collection-id>          # List entities in a collection
/twelvelabs:entities create-entity <collection-id> <name> <ids>  # Create entity
/twelvelabs:entities delete-entity <collection-id> <entity-id>    # Delete an entity
/twelvelabs:entities delete-collection <collection-id>           # Delete a collection
```

**Typical workflow:**
1. `/twelvelabs:entities create-collection "My Team"` — create a collection
2. `/twelvelabs:entities upload ./photo.jpg` — upload reference images (returns asset IDs)
3. `/twelvelabs:entities create-entity <collection-id> "Name" <asset-id>` — create the entity
4. `/twelvelabs:search <@entity_id>` — search for the entity in videos

---

## Troubleshooting

### "Video too short" error

TwelveLabs requires videos to be at least 4 seconds long. Check your video duration before indexing.

### Indexing stuck in "Pending" or "Queued"

Video indexing can take several minutes depending on video length and server load. Use `/twelvelabs:index-video status` to monitor progress. For long videos, indexing may take longer.

### "Video format not supported"

Ensure your video is in a supported format: MP4, MOV, AVI, MKV, or WebM. If using another format, convert it first:
```bash
ffmpeg -i input.video -c copy output.mp4
```

### Search returns no results

- Ensure the video is fully indexed (status: Ready)
- Try broader or different search terms
- Check that you're searching in the correct index
- For image/entity search, ensure your index uses Marengo 3.0

### Analysis fails

- Verify the video ID is correct (use `/twelvelabs:videos` to find video IDs)
- Ensure the video is fully indexed

---

## Documentation

- [TwelveLabs Documentation](https://docs.twelvelabs.io/)
- [TwelveLabs API Reference](https://docs.twelvelabs.io/reference/api-reference)
- [TwelveLabs Playground](https://playground.twelvelabs.io/)
- [Video Indexing Guide](https://docs.twelvelabs.io/docs/create-indexes)
- [Search Guide](https://docs.twelvelabs.io/docs/search-overview)
- [Generate Text Guide](https://docs.twelvelabs.io/docs/generate-text-from-video)

---

## Support

For issues with this plugin, check the troubleshooting section above or report issues on the plugin repository.

For TwelveLabs platform questions, visit [TwelveLabs Support](https://twelvelabs.io/support).
