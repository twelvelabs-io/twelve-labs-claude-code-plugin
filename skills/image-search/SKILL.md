---
name: image-search
description: Search videos using an image combined with text for refined results. Use when the user wants to search with a reference image, says "find videos matching this image", "search with this picture", or wants to combine visual reference with text description.
---

# Composed Text + Image Search

Search indexed videos using an image combined with optional text for more precise results. The text narrows image-based results — for example, an image of a car plus "red color" finds only red versions of that car model.

## When to Use This Skill

Use this skill when the user:
- Provides a reference image and wants to find similar content in videos
- Wants to combine an image with text to refine results ("find this but in blue")
- Asks to search with a picture or screenshot
- Wants to locate specific objects/scenes matching a visual reference

## Prerequisites

- Videos must be indexed with **Marengo 3.0** (composed search requires Marengo 3.0)
- A reference image: either a publicly accessible URL or a local file path

## Instructions

### Step 1: Get the Image and Query

From the user's request, extract:
- **Image**: A publicly accessible URL or an absolute path to a local image file
- **Text query** (optional): Additional text to refine the image search

### Step 2: Call the Search Tool

**Image-only search** (find content similar to the image):

With a URL:
```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  queryMediaUrl: "<image URL>"
  queryMediaType: "image"
```

With a local file:
```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  queryMediaFile: "<absolute path to image file>"
  queryMediaType: "image"
```

**Composed search** (image + text refinement):

With a URL:
```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  query: "<text description>"
  queryMediaUrl: "<image URL>"
  queryMediaType: "image"
```

With a local file:
```
Tool: mcp__twelvelabs-mcp__search
Parameters:
  query: "<text description>"
  queryMediaFile: "<absolute path to image file>"
  queryMediaType: "image"
```

To search a specific index, add `indexId`.

### Step 3: Display Results

Format results the same way as regular text search:

**For each video with matching segments, display**:
- Filename of the video (if available)
- URL of the video stream (if available)
- Bulleted list of start and end times for matching segments

**Example output**:
```
Found matches for image search with "red color":

**demo_video.mp4**
Stream: https://stream.url/video.m3u8

Matching segments:
- 00:12 - 00:28 (16 seconds)
- 01:45 - 02:03 (18 seconds)
```

### Step 4: Format Timestamps

Same as regular search:
- Under 1 hour: `MM:SS`
- 1 hour or more: `HH:MM:SS`
- Show duration in parentheses

## Use Cases

| Image | Text | Finds |
|-------|------|-------|
| Photo of a car | "red color" | Red versions of that car model |
| Photo of a building | "at night" | That building during nighttime |
| Product photo | "premium edition" | Premium version of that product |
| Person's outfit | "on stage" | Similar outfits in stage scenes |

## Example Interactions

**User**: "Find scenes in my videos that look like this image: https://example.com/sunset.jpg"
**Action**: Image-only search with queryMediaUrl

**User**: "Search for this car but in blue: https://example.com/car.jpg"
**Action**: Composed search with query "blue color" + queryMediaUrl

**User**: "Find this building at night: https://example.com/building.jpg"
**Action**: Composed search with query "at night" + queryMediaUrl

## Important Notes

- **Marengo 3.0 Required**: Composed search only works with indexes created using Marengo 3.0
- **Image Source**: Supports both publicly accessible URLs (`queryMediaUrl`) and local file paths (`queryMediaFile`)
- **Text Refines Image**: In composed search, the text narrows results from the image match — it doesn't work independently
- **Visual Search**: Composed search uses the `visual` search option
