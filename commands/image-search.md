---
name: image-search
description: Search videos using a reference image, optionally combined with text
disable-model-invocation: true
argument-hint: <image-url> [text query]
---

# /twelvelabs:image-search - Image and Composed Search

Search your indexed videos using a reference image, optionally combined with text for refined results. Requires Marengo 3.0.

## Usage

```
/twelvelabs:image-search <image-url-or-path>
/twelvelabs:image-search <image-url-or-path> <text query>
```

**User provided:** `$ARGUMENTS`

## Arguments

- `image-url-or-path` - **Required**. Either a publicly accessible URL or an absolute local file path to the reference image
- `text query` - Optional. Text to refine the image search results

## Examples

```
/twelvelabs:image-search https://example.com/car.jpg
/twelvelabs:image-search https://example.com/car.jpg red color
/twelvelabs:image-search /Users/me/photos/building.jpg at night
/twelvelabs:image-search https://example.com/product.jpg premium edition
```

## Instructions for Claude

When the user invokes `/twelvelabs:image-search`:

### Step 1: Parse Arguments

Extract from `$ARGUMENTS`:
- First token that looks like a URL (starts with `http://` or `https://`) or a file path (starts with `/`) → `imageSource`
- Everything after the image source → `textQuery` (optional)

Determine if the source is a URL or a local file path:
- Starts with `http://` or `https://` → URL → use `queryMediaUrl`
- Starts with `/` (absolute path) → local file → use `queryMediaFile`

If neither found:
```
Please provide an image URL or local file path.

Usage: /twelvelabs:image-search <image-url-or-path> [text query]
Examples:
  /twelvelabs:image-search https://example.com/car.jpg red color
  /twelvelabs:image-search /path/to/photo.jpg at night
```

### Step 2: Call the Search Tool

**Image-only with URL** (no text query):
```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  queryMediaUrl: "<imageUrl>"
  queryMediaType: "image"
```

**Image-only with local file**:
```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  queryMediaFile: "<absolute file path>"
  queryMediaType: "image"
```

**Composed search with URL** (with text query):
```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  query: "<textQuery>"
  queryMediaUrl: "<imageUrl>"
  queryMediaType: "image"
```

**Composed search with local file**:
```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  query: "<textQuery>"
  queryMediaFile: "<absolute file path>"
  queryMediaType: "image"
```

### Step 3: Display Results

Format results with video filenames, stream URLs, and timestamps — same format as `/twelvelabs:search`.

**Example output**:
```
Image search results:

**demo_video.mp4**
Stream: https://stream.url/video.m3u8

Matching segments:
- 00:12 - 00:28 (16 seconds)
- 01:45 - 02:03 (18 seconds)
```

**No results**:
```
No matching content found for your image search.

Tips:
- Try adding a text description to refine results
- Ensure your videos are indexed with Marengo 3.0
- Check that the image URL is publicly accessible
```

## Related Commands

- `/twelvelabs:search` - Text-based video search
- `/twelvelabs:entity-search` - Search for specific people using entity recognition
- `/twelvelabs:list` - List indexed videos
