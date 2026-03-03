#!/usr/bin/env python3
"""Post-hook for get-video-embeddings-tasks MCP tool.

This hook runs after the MCP tool completes and updates local config
based on embedding task status changes (ready, failed, or processing).

Hook type: PostToolUse
Matcher: mcp__twelvelabs-mcp__get-video-embeddings-tasks
"""

import json
import sys
import os

# Add plugin root to path for imports
# When installed as a plugin, CLAUDE_PLUGIN_ROOT points to the cached plugin directory
plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(plugin_root, ".twelvelabs"))

from config_helper import (
    complete_embedding_task,
    fail_embedding_task,
    update_pending_embedding_task_status,
    get_pending_embedding_task,
)


def extract_tasks_from_result(tool_result: dict | str) -> list[dict]:
    """Extract task information from the MCP tool result.

    Args:
        tool_result: The result from the MCP tool

    Returns:
        List of task dictionaries with task_id, status
    """
    tasks = []

    # Handle string result (might be JSON)
    if isinstance(tool_result, str):
        try:
            tool_result = json.loads(tool_result)
        except json.JSONDecodeError:
            return tasks

    if not isinstance(tool_result, dict):
        return tasks

    # Format 1: Direct task object (single task query)
    if "status" in tool_result and ("task_id" in tool_result or "taskId" in tool_result or "id" in tool_result):
        tasks.append(normalize_task(tool_result))
        return tasks

    # Format 2: Array of tasks in 'data' field
    if "data" in tool_result:
        data = tool_result["data"]
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    tasks.append(normalize_task(item))
        elif isinstance(data, dict) and "status" in data:
            tasks.append(normalize_task(data))

    # Format 3: Array of tasks in 'tasks' field
    if "tasks" in tool_result:
        task_list = tool_result["tasks"]
        if isinstance(task_list, list):
            for item in task_list:
                if isinstance(item, dict):
                    tasks.append(normalize_task(item))

    # Format 4: Array of tasks in 'result' field
    if "result" in tool_result:
        result = tool_result["result"]
        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict):
                    tasks.append(normalize_task(item))
        elif isinstance(result, dict) and "status" in result:
            tasks.append(normalize_task(result))

    return tasks


def normalize_task(task: dict) -> dict:
    """Normalize task data to a consistent format.

    Args:
        task: Raw task dictionary from API

    Returns:
        Normalized task with task_id and status
    """
    return {
        "task_id": task.get("task_id") or task.get("taskId") or task.get("id") or task.get("_id"),
        "status": (task.get("status") or "").lower(),
    }


def process_task_status(task: dict) -> dict:
    """Process an embedding task status update.

    Args:
        task: Normalized task dictionary

    Returns:
        Result dictionary with action taken and success status
    """
    task_id = task.get("task_id")
    status = task.get("status")

    if not task_id:
        return {"action": "skipped", "reason": "no task_id"}

    # Check if this task is in our pending embedding tasks
    pending = get_pending_embedding_task(task_id)
    if not pending:
        return {"action": "skipped", "reason": "not tracked locally", "task_id": task_id}

    # Handle based on status
    if status == "ready":
        success = complete_embedding_task(task_id)
        return {
            "action": "completed",
            "task_id": task_id,
            "success": success
        }

    elif status == "failed":
        success = fail_embedding_task(task_id)
        return {
            "action": "failed",
            "task_id": task_id,
            "success": success
        }

    else:
        # Still processing - update status
        success = update_pending_embedding_task_status(task_id, status)
        return {
            "action": "updated",
            "task_id": task_id,
            "status": status,
            "success": success
        }


def main():
    """Main entry point for the hook.

    Reads hook context from stdin as JSON:
    {
        "tool_name": "mcp__twelvelabs-mcp__get-video-embeddings-tasks",
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

        tool_result = input_data.get("tool_result", {})

        # Extract tasks from the result
        tasks = extract_tasks_from_result(tool_result)

        if not tasks:
            response = {
                "continue": True,
                "message": "No embedding task status information found in response"
            }
            print(json.dumps(response))
            return

        # Process each task
        results = []
        completed_count = 0
        failed_count = 0
        updated_count = 0

        for task in tasks:
            result = process_task_status(task)
            results.append(result)

            if result.get("action") == "completed" and result.get("success"):
                completed_count += 1
            elif result.get("action") == "failed" and result.get("success"):
                failed_count += 1
            elif result.get("action") == "updated" and result.get("success"):
                updated_count += 1

        # Build response message
        messages = []
        if completed_count > 0:
            messages.append(f"{completed_count} embedding task(s) completed")
        if failed_count > 0:
            messages.append(f"{failed_count} embedding task(s) failed")
        if updated_count > 0:
            messages.append(f"{updated_count} embedding task(s) status updated")

        response = {
            "continue": True,
            "message": "; ".join(messages) if messages else "Embedding task status processed"
        }

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
