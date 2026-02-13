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

The plugin configures the MCP server, slash commands, skills, and hooks automatically.

## Usage

### Commands

| Command | Description |
|---------|-------------|
| `/twelvelabs:index <path-or-url>` | Index a video (local file, URL, or Google Drive link) |
| `/twelvelabs:status [task-id]` | Check indexing task status |
| `/twelvelabs:list [indexes]` | List indexed videos or available indexes |
| `/twelvelabs:search <query>` | Search videos with natural language |
| `/twelvelabs:analyze [video-id] [prompt]` | Analyze video content (summary, Q&A, etc.) |
| `/twelvelabs:help` | Show help and available commands |

### Examples

```
/twelvelabs:index /path/to/video.mp4
/twelvelabs:index https://example.com/video.mp4
/twelvelabs:search "person giving a presentation"
/twelvelabs:analyze abc123 "What are the main topics?"
```

Or just use natural language:

- "Index this video: /path/to/video.mp4"
- "Is my video ready?"
- "What videos do I have?"
- "Find the part where someone is cooking"
- "Summarize the key points of this video"

## Troubleshooting

### "Video too short" error

TwelveLabs requires videos to be at least **4 seconds** long.

### Indexing stuck in "Pending" or "Queued"

Video indexing can take several minutes depending on video length. Use `/twelvelabs:status` to monitor progress.

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

- Verify the video ID with `/twelvelabs:list`
- Ensure the video is fully indexed

## Development

Load the plugin from a local directory (session-only, not persisted):

```bash
claude --plugin-dir ./twelve-labs-claude-code-plugin
```

## Links

- [TwelveLabs Documentation](https://docs.twelvelabs.io/)
- [TwelveLabs API Reference](https://docs.twelvelabs.io/reference/api-reference)
- [TwelveLabs Playground](https://playground.twelvelabs.io/)
- [TwelveLabs MCP Server (npm)](https://www.npmjs.com/package/twelvelabs-mcp)
