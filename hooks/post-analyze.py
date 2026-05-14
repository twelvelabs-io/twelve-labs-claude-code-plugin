#!/usr/bin/env python3
"""Post-hook for sync-analyse-video MCP tool.

This hook runs after the MCP tool completes and caches the analysis result
to avoid redundant API calls for the same video and analysis type.

Hook type: PostToolUse
Matcher: mcp__twelvelabs-mcp__sync-analyse-video
"""

import json
import sys
import os

# Add plugin root to path for imports
# When installed as a plugin, CLAUDE_PLUGIN_ROOT points to the cached plugin directory
plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(plugin_root, ".twelvelabs"))

from config_helper import cache_analysis


def extract_analysis_info(tool_input: dict, tool_result: dict) -> tuple[str | None, str | None, any]:
    """Extract video_id, type, and result from tool input/result.

    Args:
        tool_input: The input parameters passed to the MCP tool
        tool_result: The result from the MCP tool

    Returns:
        Tuple of (video_id, analysis_type, result) or (None, None, None) if extraction fails
    """
    # Extract video_id and type from input
    # The new sync-analyse-video tool no longer has a 'type' field; fall back to 'prompt' as key
    video_id = tool_input.get("videoId")
    analysis_type = tool_input.get("type") or "sync"

    # The result is the analysis output from the MCP tool
    result = None

    if isinstance(tool_result, dict):
        # The result might be directly in the tool_result
        # Or nested in data, result, or other fields
        if "data" in tool_result:
            result = tool_result["data"]
        elif "result" in tool_result:
            result = tool_result["result"]
        else:
            # Use the whole tool_result as the result
            result = tool_result
    elif isinstance(tool_result, str):
        # String result - use as-is
        result = tool_result
    else:
        result = tool_result

    return video_id, analysis_type, result


def main():
    """Main entry point for the hook.

    Reads hook context from stdin as JSON:
    {
        "tool_name": "mcp__twelvelabs-mcp__sync-analyse-video",
        "tool_input": {...},
        "tool_result": {...}
    }

    Outputs JSON response:
    {
        "continue": true,
        "message": "..." (optional status message)
    }
    """
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        tool_input = input_data.get("tool_input", {})
        tool_result = input_data.get("tool_result", {})

        # Extract analysis information
        video_id, analysis_type, result = extract_analysis_info(tool_input, tool_result)

        if video_id and analysis_type and result is not None:
            # Cache the analysis result
            success = cache_analysis(
                video_id=video_id,
                analysis_type=analysis_type,
                result=result
            )

            if success:
                response = {
                    "continue": True,
                    "message": f"Cached {analysis_type} analysis for video {video_id}"
                }
            else:
                response = {
                    "continue": True,
                    "message": f"Warning: Failed to cache {analysis_type} analysis for video {video_id}"
                }
        elif video_id and analysis_type:
            # Have video_id and type but no result (analysis might have failed)
            response = {
                "continue": True,
                "message": f"No result to cache for {analysis_type} analysis of video {video_id}"
            }
        else:
            # Could not extract required information
            response = {
                "continue": True,
                "message": "Warning: Could not extract video_id/type from analysis response"
            }

        # Output response
        print(json.dumps(response))

    except Exception as e:
        # Always allow continuation even if hook fails
        response = {
            "continue": True,
            "message": f"Hook error: {str(e)}"
        }
        print(json.dumps(response))


if __name__ == "__main__":
    main()
