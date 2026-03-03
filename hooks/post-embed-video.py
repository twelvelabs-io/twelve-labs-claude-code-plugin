#!/usr/bin/env python3
"""Post-hook for start-video-embeddings-task MCP tool.

This hook runs after the MCP tool completes and extracts task information
from the response to track in local config.

Hook type: PostToolUse
Matcher: mcp__twelvelabs-mcp__start-video-embeddings-task
"""

import json
import sys
import os

# Add plugin root to path for imports
# When installed as a plugin, CLAUDE_PLUGIN_ROOT points to the cached plugin directory
plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(plugin_root, ".twelvelabs"))

from config_helper import add_pending_embedding_task


def extract_task_info(tool_input: dict, tool_result: dict) -> tuple[str | None, str | None]:
    """Extract task_id and source from tool input/result.

    Args:
        tool_input: The input parameters passed to the MCP tool
        tool_result: The result from the MCP tool

    Returns:
        Tuple of (task_id, source) or (None, None) if extraction fails
    """
    # Extract source from input (either videoFilePath or videoUrl)
    source = tool_input.get("videoFilePath") or tool_input.get("videoUrl")

    # Extract task_id from result
    task_id = None

    # Handle different response formats
    if isinstance(tool_result, dict):
        # Direct task_id field
        task_id = tool_result.get("task_id") or tool_result.get("taskId") or tool_result.get("id")

        # Nested in data field
        if not task_id and "data" in tool_result:
            data = tool_result["data"]
            if isinstance(data, dict):
                task_id = data.get("task_id") or data.get("taskId") or data.get("id")

        # Nested in result field
        if not task_id and "result" in tool_result:
            result = tool_result["result"]
            if isinstance(result, dict):
                task_id = result.get("task_id") or result.get("taskId") or result.get("id")

    # Handle string result (might be JSON)
    elif isinstance(tool_result, str):
        try:
            parsed = json.loads(tool_result)
            if isinstance(parsed, dict):
                task_id = parsed.get("task_id") or parsed.get("taskId") or parsed.get("id")
        except json.JSONDecodeError:
            pass

    return task_id, source


def main():
    """Main entry point for the hook.

    Reads hook context from stdin as JSON:
    {
        "tool_name": "mcp__twelvelabs-mcp__start-video-embeddings-task",
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

        # Extract task information
        task_id, source = extract_task_info(tool_input, tool_result)

        if task_id and source:
            # Save task to local config
            success = add_pending_embedding_task(
                task_id=task_id,
                source=source,
                status="processing"
            )

            if success:
                response = {
                    "continue": True,
                    "message": f"Embedding task {task_id} tracked for {source}"
                }
            else:
                response = {
                    "continue": True,
                    "message": f"Warning: Failed to save embedding task {task_id} to local config"
                }
        elif task_id:
            # Have task_id but no source - still track it
            success = add_pending_embedding_task(
                task_id=task_id,
                source="unknown",
                status="processing"
            )
            response = {
                "continue": True,
                "message": f"Embedding task {task_id} tracked (source unknown)"
            }
        else:
            # Could not extract task information
            response = {
                "continue": True,
                "message": "Warning: Could not extract task_id from embeddings response"
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
