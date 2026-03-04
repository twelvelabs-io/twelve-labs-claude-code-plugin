# TwelveLabs Claude Code Plugin

Index, search, and analyze videos directly from Claude Code using [TwelveLabs](https://www.twelvelabs.io/) multimodal AI.

## Install

1. Set your TwelveLabs API key as an environment variable (get one at [twelvelabs.io](https://www.twelvelabs.io/)):

```bash
export TWELVELABS_API_KEY=your_api_key_here
```

Add this to your `~/.zshrc` or `~/.bashrc` to persist it.

2. In Claude Code, run:

```
/plugin marketplace add twelvelabs-io/twelve-labs-claude-code-plugin
/plugin install twelvelabs@twelvelabs-plugins
```

You may need to restart Claude Code after installing for the plugin and MCP to take effect.

The plugin configures the MCP server, slash commands, skills, and hooks automatically.

## Usage

### Commands

| Command | Description |
|---------|-------------|
| `/twelvelabs:index-video <path-or-url>` | Index a video (local file, URL, or Google Drive link) |
| `/twelvelabs:index-video status [task-id]` | Check indexing task status |
| `/twelvelabs:indexes` | List, create, or delete indexes |
| `/twelvelabs:videos` | List your indexed videos |
| `/twelvelabs:search <query>` | Search videos by text, image, or entity |
| `/twelvelabs:analyze [video-id] [prompt]` | Analyze video content (summary, Q&A, etc.) |
| `/twelvelabs:embed <path-or-url>` | Create video embeddings or check embedding status |
| `/twelvelabs:entities` | Manage entity collections and entities |
| `/twelvelabs:help` | Show help and available commands |

### Examples

```
/twelvelabs:index-video /path/to/video.mp4
/twelvelabs:index-video https://example.com/video.mp4
/twelvelabs:index-video status
/twelvelabs:search "person giving a presentation"
/twelvelabs:search https://example.com/car.jpg red color
/twelvelabs:entities create-collection "My Team"
/twelvelabs:search <@abc123> is giving a presentation
/twelvelabs:embed /path/to/video.mp4
/twelvelabs:embed status
/twelvelabs:analyze abc123 "What are the main topics?"
```

Or just use natural language:

- "Index this video: /path/to/video.mp4"
- "Is my video ready?"
- "What videos do I have?"
- "Find the part where someone is cooking"
- "Find scenes matching this image: https://example.com/photo.jpg"
- "Set up entity search for Sarah using this photo"
- "Create embeddings for this video: /path/to/video.mp4"
- "Are my embeddings ready?"
- "Get embeddings for video abc123"
- "Summarize the key points of this video"

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
