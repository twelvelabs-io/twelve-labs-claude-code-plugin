# TwelveLabs Claude Code Plugin

Index, search, and analyze videos directly from Claude Code using [TwelveLabs](https://www.twelvelabs.io/) multimodal AI.

## Install

1. Set your TwelveLabs API key as an environment variable (get one at [twelvelabs.io](https://www.twelvelabs.io/)):

```bash
export TWELVELABS_API_KEY=your_api_key_here
```

Add this to your `~/.zshrc` or `~/.bashrc` to persist it.

2. In Claude Code, add the plugin marketplace:

```
/plugin marketplace add twelvelabs-io/twelve-labs-claude-code-plugin
```

3. Then install the plugin:

```
/plugin install twelvelabs@twelvelabs-plugins
```

You may need to restart Claude Code after installing for the plugin and MCP to take effect.

The plugin configures the MCP server, slash commands, skills, and hooks automatically.

## What You Can Do

**Index videos** from local files, remote URLs, or Google Drive links. Once a video is indexed, it becomes searchable and analyzable. Indexing is asynchronous — you can check on progress at any time.

**Search across your videos** using natural language descriptions of what you're looking for — visual elements, actions, sounds, or on-screen text. You can also search using a reference image to find visually similar content, combine an image with text for refined results, or search for specific people and objects using entity recognition.

**Analyze video content** to generate summaries, extract key topics, answer questions, list action items, or perform any open-ended analysis guided by a custom prompt. Both analyze commands accept indexed `videoId`s, direct URLs, asset IDs, or local files (auto-uploaded as assets). Two modes:

- `/twelvelabs:sync-analyze` — returns the result inline. Pegasus 1.5 by default for URL/asset/file inputs; falls back to Pegasus 1.2 only when analysing an existing indexed `videoId` or when the user explicitly requests 1.2. Cap: ≤1 hour video.
- `/twelvelabs:async-analyze` — fire-and-forget for longer videos (up to 2 hours), Pegasus 1.5 throughout. Also supports **time-based metadata extraction** (`analysisMode: "time_based_metadata"` + `segmentDefinitions`) for per-segment structured output, multimodal prompting with reference images (`promptV2`), and structured JSON output (`jsonSchema`).

**Create video embeddings** for use in downstream applications like similarity search, clustering, or recommendation systems.

**Manage indexes** to organize your videos into separate collections. Each index can be configured with different model capabilities — Marengo for search or Pegasus for text generation.

**Set up entity search** by creating collections of people or objects with reference images. Once configured, you can find exactly when and where a specific person appears across all your indexed videos.

## Usage

### Commands

| Command | Description |
|---------|-------------|
| `/twelvelabs:index-video <path-or-url> [index-id]` | Index a local video, URL, or Google Drive link |
| `/twelvelabs:index-video status [task-id]` | Check indexing task status |
| `/twelvelabs:indexes` | List all indexes |
| `/twelvelabs:indexes create <name> [model]` | Create a new index (models: `marengo`, `pegasus`, or both) |
| `/twelvelabs:indexes delete <index-id>` | Delete an index |
| `/twelvelabs:videos [index-id]` | List indexed videos |
| `/twelvelabs:search <query> [index-id]` | Text search across videos |
| `/twelvelabs:search <image> [text] [index-id]` | Image or composed (image + text) search |
| `/twelvelabs:search <@entity_id> [action] [index-id]` | Entity search for specific people/objects |
| `/twelvelabs:sync-analyze <video-id-or-url-or-asset-or-path> [prompt]` | Synchronous analysis. Pegasus 1.5 by default; Pegasus 1.2 forced for `videoId` |
| `/twelvelabs:async-analyze <url-or-path-or-asset> [prompt]` | Async analysis (Pegasus 1.5, ≤2 hours; supports time-based metadata, `promptV2`, `jsonSchema`) |
| `/twelvelabs:async-analyze status [task-id]` | Check async-analyze task status |
| `/twelvelabs:async-analyze list` | List async-analyze tasks |
| `/twelvelabs:async-analyze delete <task-id>` | Delete an async-analyze task |
| `/twelvelabs:embed <path-or-url>` | Create video embeddings |
| `/twelvelabs:embed status [task-id]` | Check embedding task status |
| `/twelvelabs:entities create-collection <name>` | Create an entity collection |
| `/twelvelabs:entities list-collections` | List all entity collections |
| `/twelvelabs:entities create-entity <collection-id> <name> <asset-ids...>` | Create an entity from image asset IDs |
| `/twelvelabs:entities list-entities <collection-id>` | List entities in a collection |
| `/twelvelabs:entities delete-entity <collection-id> <entity-id>` | Delete an entity |
| `/twelvelabs:entities delete-collection <collection-id>` | Delete a collection and all its entities |
| `/twelvelabs:assets upload <path-or-url>` | Upload a local file or URL as an asset (image or video) |
| `/twelvelabs:assets delete <asset-id>` | Delete an asset |
| `/twelvelabs:help` | Show help and available commands |

### Natural Language

You can also skip slash commands and just describe what you want:

#### Indexing

- "Index this video: /path/to/video.mp4"
- "Index this URL: https://example.com/video.mp4"
- "Index every video in /path/to/my-videos/" (batch — folder indexing)
- "Index this file and tag it with `project=demo`" (userMetadata round-trips into search results)
- "Add this video for analysis"
- "Process this video file"
- "Add this Google Drive folder for analysis: https://drive.google.com/drive/folders/ABC123"

#### Checking Status

- "Is my video ready?"
- "How long until indexing is done?"
- "Is it still processing?"
- "Can I search my video yet?"
- "Check status of task abc123"

#### Text Search

- "Find the part where someone is cooking"
- "Search for a red car driving fast"
- "When does the presenter mention AI?"
- "Look for the sunset scene"
- "Find text showing 'hello world'"

#### Image Search

- "Find scenes matching this image: https://example.com/photo.jpg"
- "Search with this picture: /path/to/screenshot.png"
- "Find videos that look like this image"

#### Composed Search (Image + Text)

- "Find this car but in blue: https://example.com/car.jpg"
- "Find this building at night: https://example.com/building.jpg"
- "Search for this product in premium packaging: /path/to/product.jpg"

#### Entity Search

- "Find all clips of Sarah in my videos"
- "I want to track this person across my videos. Here's their photo: https://example.com/sarah.jpg"
- "Set up entity search for Sarah using this photo"
- "Find this person giving a presentation"

#### Analysis (sync — short videos, returns inline)

- "What is this video about?"
- "Summarize the key points of this video"
- "Analyze https://example.com/clip.mp4 and tell me what happens" (URL input — Pegasus 1.5)
- "Analyze /path/to/clip.mp4 in one sentence" (local file — auto-uploaded, Pegasus 1.5)
- "Extract action items from this meeting"
- "Return JSON with `{product, timestamp_sec}[]` for every product mentioned" (structured output via `jsonSchema`)

#### Analysis (async — long videos, segmentation, structured outputs)

- "Analyze this 90-minute keynote and tell me the key takeaways"
- "Analyze this URL without indexing: https://example.com/long-video.mp4"
- "Extract every highlight from this video with a description and importance score for each" (time-based metadata extraction)
- "Find every shot that looks like this product image" (multimodal `promptV2` with reference images)
- "Is my async analyze task done?"
- "Show all my failed async tasks"
- "Delete the analyze task for that long video"

#### Embeddings

- "Create embeddings for this video: /path/to/video.mp4"
- "Embed this video: https://example.com/video.mp4"
- "Are my embeddings ready?"
- "Check embedding status"
- "Get embeddings for video abc123"

#### Managing Videos & Indexes

- "What videos do I have?"
- "Show my videos"
- "Do I have any videos indexed?"
- "Which videos can I search?"
- "I need the video ID for my demo"
- "Show my indexes"
- "What indexes do I have?"
- "Create a new index called marketing-videos"
- "Create a search-only index with marengo"

#### Entity Management

- "Create an entity collection called My Team"
- "Create an entity for Sarah using these reference image asset IDs"
- "List my entity collections"
- "What entities are in this collection?"
- "Delete this entity"

#### Assets

- "Upload this photo as an asset: ./sarah.jpg"
- "Upload this video as an asset: ./keynote.mp4"
- "Upload this image URL as an asset"
- "Delete this asset"

#### Sample Videos

- "I don't have a video to test"
- "Show me sample videos"
- "Can I try with a demo video?"

## Troubleshooting

### "Video too short" error

TwelveLabs requires videos to be at least **4 seconds** long.

### Indexing stuck in "Pending" or "Queued"

Video indexing can take several minutes depending on video length. Use `/twelvelabs:index-video status` to monitor progress.

### "Video format not supported"

Supported formats: MP4, MOV, AVI, MKV, WebM. Convert with:
```bash
ffmpeg -i input.video -c copy output.mp4
```

### Search returns no results

- Ensure the video is fully indexed (status: Ready)
- Try broader or different search terms
- Verify you're searching in the correct index

### Analysis fails

- Verify the video ID with `/twelvelabs:videos`
- Ensure the video is fully indexed

## Development

### Load from a local directory (session-only)

```bash
claude --plugin-dir path/to/twelve-labs-claude-code-plugin
```

### Point the marketplace to a local directory

```
/plugin marketplace add path/to/twelve-labs-claude-code-plugin
/plugin install twelvelabs@twelvelabs-plugins
```

## Links

- [TwelveLabs Documentation](https://docs.twelvelabs.io/)
- [TwelveLabs API Reference](https://docs.twelvelabs.io/reference/api-reference)
- [TwelveLabs Playground](https://playground.twelvelabs.io/)
- [TwelveLabs MCP Server (npm)](https://www.npmjs.com/package/twelvelabs-mcp)
