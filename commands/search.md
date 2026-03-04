---
name: search
description: Search videos by text, image, or entity using TwelveLabs
disable-model-invocation: true
argument-hint: <query> [index-id]
---

# /twelvelabs:search - Search Videos

Search your indexed videos using text, images, entities, or combinations. TwelveLabs interprets your query to find matching content based on visual elements, actions, sounds, and on-screen text.

## Usage

```
/twelvelabs:search <text query> [index-id]
/twelvelabs:search <image-url-or-path> [index-id]
/twelvelabs:search <image-url-or-path> <text query> [index-id]
/twelvelabs:search <@entity_id> [action description] [index-id]
```

**User provided:** `$ARGUMENTS`

## Arguments

- `text query` - Natural language description of what you're looking for
- `image-url-or-path` - A publicly accessible image URL or absolute local file path
- `<@entity_id>` - Entity ID wrapped in `<@` and `>` for entity recognition search
- `action description` - Optional text to combine with entity or image search
- `index-id` - **Optional**. ID of a specific index to search. If not provided, searches the default index.

## Examples

### Text Search
```
/twelvelabs:search a person walking through a forest
/twelvelabs:search red car driving fast
/twelvelabs:search someone giving a presentation
/twelvelabs:search text showing "hello world"
```

### Image Search (requires Marengo 3.0)
```
/twelvelabs:search https://example.com/car.jpg
/twelvelabs:search /Users/me/photos/building.jpg
```

### Composed Search (image + text, requires Marengo 3.0)
```
/twelvelabs:search https://example.com/car.jpg red color
/twelvelabs:search /Users/me/photos/building.jpg at night
```

### Entity Search (requires Marengo 3.0)
```
/twelvelabs:search <@abc123>
/twelvelabs:search <@abc123> is giving a presentation
```

## Instructions for Claude

When the user invokes `/twelvelabs:search`, the query is provided in `$ARGUMENTS`. Follow these steps:

### Step 1: Validate Input

Check that `$ARGUMENTS` is not empty. If empty:
```
Please provide a search query, image, or entity ID.

Usage:
  /twelvelabs:search <text query>
  /twelvelabs:search <image-url-or-path>
  /twelvelabs:search <image-url-or-path> <text query>
  /twelvelabs:search <@entity_id> [action]
```

### Step 2: Extract Index ID (if provided)

Check if the **last token** in `$ARGUMENTS` looks like an index ID (a 24-character hex string like `682792e7...`). If so, extract it as the `indexId` and remove it from the query arguments.

### Step 3: Determine Search Type

Classify the remaining query:

1. **Entity search**: Contains `<@` — the input includes an entity ID pattern like `<@abc123>`
2. **Image search**: First token starts with `http://`, `https://`, or `/` and looks like an image file (ends in `.jpg`, `.jpeg`, `.png`, `.webp`) or is a URL
3. **Text search**: Everything else

### Step 4: Call the Search MCP Tool

For all search types below, include `indexId: "<index-id>"` if an index ID was extracted in Step 2.

#### Text Search

```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  query: "<user's search query>"

  indexId: "<index-id>"          # only include if provided
```

#### Image Search (image only, no text)

Determine if the image source is a URL or local file:
- Starts with `http://` or `https://` → use `queryMediaUrl`
- Starts with `/` (absolute path) → use `queryMediaFile`

**Image URL only:**
```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  queryMediaUrl: "<imageUrl>"
  queryMediaType: "image"

  indexId: "<index-id>"          # only include if provided
```

**Local image file only:**
```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  queryMediaFile: "<absolute file path>"
  queryMediaType: "image"

  indexId: "<index-id>"          # only include if provided
```

#### Composed Search (image + text)

If both an image source and text query are present:

**Image URL + text:**
```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  query: "<textQuery>"
  queryMediaUrl: "<imageUrl>"
  queryMediaType: "image"

  indexId: "<index-id>"          # only include if provided
```

**Local image file + text:**
```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  query: "<textQuery>"
  queryMediaFile: "<absolute file path>"
  queryMediaType: "image"

  indexId: "<index-id>"          # only include if provided
```

#### Entity Search

Use the query portion of `$ARGUMENTS` (with index ID removed) as the query:

```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  query: "<entity query>"

  indexId: "<index-id>"          # only include if provided
```

### Step 5: Display Search Results

Format the search results clearly for the user. The search returns matching segments with timestamps.

**For each video with matching segments, display**:
- Filename of the video (if available)
- URL of the video stream (if available)
- Bulleted list of start and end times for matching segments

**Example output with results**:
```
Search Results for: "a person walking"

**video_filename.mp4**
Stream: https://stream.url/video.m3u8

Matching segments:
- 00:12 - 00:28 (16 seconds)
- 01:45 - 02:03 (18 seconds)
- 03:30 - 03:45 (15 seconds)

**another_video.mp4**
Stream: https://stream.url/another.m3u8

Matching segments:
- 00:05 - 00:15 (10 seconds)

Found 4 matching segments across 2 videos.
```

**Example output with no results**:
```
No Results Found

No matching content found for: "a person walking"

Tips:
- Try different keywords or descriptions
- Use broader search terms
- Make sure your videos are fully indexed (check with /twelvelabs:index-video status)
- For image search, ensure your index uses Marengo 3.0
- For entity search, set up entities first with /twelvelabs:entities create-collection
```

### Step 6: Format Timestamps

Convert timestamps to human-readable format:
- For timestamps under 1 hour: `MM:SS` (e.g., `01:45`)
- For timestamps 1 hour or more: `HH:MM:SS` (e.g., `1:23:45`)

Calculate segment duration as `end_time - start_time` and display in parentheses.

## Search Tips

- **Visual elements**: Describe objects, people, colors, actions visible in the video
- **Audio/speech**: Describe sounds, music, or spoken words
- **On-screen text**: Search for text that appears in the video
- **Image search**: Use a reference image to find visually similar content
- **Composed search**: Combine an image with text to refine results (e.g., image of a car + "red color")
- **Entity search**: Use `<@entity_id>` to find a registered person/object, optionally with an action

## Important Notes

- **Indexed Videos Only**: Search only works on videos that have been fully indexed
- **Default Index**: Searches the default index unless specified otherwise
- **Marengo 3.0**: Image search, composed search, and entity search require Marengo 3.0
- **Segment Precision**: Results show specific time ranges where content matches

## Related Commands

- `/twelvelabs:videos` - List all indexed videos
- `/twelvelabs:index-video` - Index a new video
- `/twelvelabs:index-video status` - Check if videos are ready for search
- `/twelvelabs:analyze` - Get detailed analysis of specific video content
- `/twelvelabs:entities` - Manage entities for entity search
