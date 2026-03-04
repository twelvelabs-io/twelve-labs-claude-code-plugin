#!/usr/bin/env python3
"""Pre-hook for start-video-indexing-task MCP tool.

This hook runs before the MCP tool and validates the input:
- For local files: validates file exists and has a video extension
- For URLs: validates URL format
- Warns if the video is already indexed

Hook type: PreToolUse
Matcher: mcp__twelvelabs-mcp__start-video-indexing-task
"""

import json
import sys
import os
import re

# Add plugin root to path for imports
# When installed as a plugin, CLAUDE_PLUGIN_ROOT points to the cached plugin directory
plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(plugin_root, ".twelvelabs"))

from config_helper import is_video_indexed, get_video_by_source, get_all_pending_tasks

# Supported video extensions
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


def is_video_extension(file_path: str) -> bool:
    """Check if the file path has a video extension.

    Args:
        file_path: The path to the file

    Returns:
        True if the file has a video extension, False otherwise
    """
    if not file_path:
        return False
    _, ext = os.path.splitext(file_path.lower())
    return ext in VIDEO_EXTENSIONS


def is_valid_url(url: str) -> bool:
    """Check if the string is a valid HTTP/HTTPS URL.

    Args:
        url: The URL string to validate

    Returns:
        True if the URL is valid, False otherwise
    """
    if not url:
        return False
    # Basic URL pattern for http/https
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'[^\s/$.?#]'  # at least one character that's not whitespace or special
        r'[^\s]*$',    # followed by any non-whitespace characters
        re.IGNORECASE
    )
    return bool(url_pattern.match(url))


def is_google_drive_url(url: str) -> bool:
    """Check if the URL is a Google Drive link.

    Args:
        url: The URL to check

    Returns:
        True if the URL is a Google Drive link, False otherwise
    """
    if not url:
        return False
    return "drive.google.com" in url.lower()


def is_video_pending(source: str) -> tuple[bool, str | None]:
    """Check if a video source has a pending indexing task.

    Args:
        source: The file path or URL of the video

    Returns:
        Tuple of (is_pending, task_id) where task_id is the pending task ID if found
    """
    pending_tasks = get_all_pending_tasks()
    for task_id, task in pending_tasks.items():
        if task.get("source") == source:
            return True, task_id
    return False, None


def validate_local_file(file_path: str) -> tuple[bool, str | None]:
    """Validate a local file path.

    Args:
        file_path: The path to the local file

    Returns:
        Tuple of (is_valid, error_message) where error_message is None if valid
    """
    if not file_path:
        return False, "No file path provided"

    # Check if file exists
    if not os.path.exists(file_path):
        return False, f"File does not exist: {file_path}"

    # Check if it's a file (not a directory)
    if not os.path.isfile(file_path):
        return False, f"Path is not a file: {file_path}"

    # Check extension
    if not is_video_extension(file_path):
        _, ext = os.path.splitext(file_path)
        return False, f"Unsupported video format '{ext}'. Supported formats: {', '.join(sorted(VIDEO_EXTENSIONS))}"

    return True, None


def validate_url(url: str) -> tuple[bool, str | None]:
    """Validate a URL.

    Args:
        url: The URL to validate

    Returns:
        Tuple of (is_valid, error_message) where error_message is None if valid
    """
    if not url:
        return False, "No URL provided"

    if not is_valid_url(url):
        return False, f"Invalid URL format: {url}. URL must start with http:// or https://"

    return True, None


def main():
    """Main entry point for the hook.

    Reads hook context from stdin as JSON:
    {
        "tool_name": "mcp__twelvelabs-mcp__start-video-indexing-task",
        "tool_input": {
            "videoFilePath": "..." (optional),
            "videoUrl": "..." (optional)
        }
    }

    Outputs JSON response:
    {
        "continue": true/false,
        "message": "..." (validation result or warning)
    }

    Note: This hook is informational and provides warnings, but generally
    allows continuation unless the input is clearly invalid.
    """
    try:
        # Read input from stdin
        input_data = json.load(sys.stdin)

        tool_input = input_data.get("tool_input", {})
        video_file_path = tool_input.get("videoFilePath")
        video_url = tool_input.get("videoUrl")

        messages = []
        should_continue = True

        # Determine which source is being used
        if video_file_path:
            # Validate local file
            is_valid, error_msg = validate_local_file(video_file_path)
            if not is_valid:
                messages.append(f"Validation error: {error_msg}")
                should_continue = False
            else:
                # Normalize path for checking
                abs_path = os.path.abspath(video_file_path)
                source = abs_path

                # Check if already indexed
                if is_video_indexed(abs_path) or is_video_indexed(video_file_path):
                    video = get_video_by_source(abs_path) or get_video_by_source(video_file_path)
                    video_id = video.get("video_id", "unknown") if video else "unknown"
                    messages.append(
                        f"Warning: Video '{os.path.basename(video_file_path)}' is already indexed "
                        f"(video_id: {video_id}). Proceeding will create a duplicate."
                    )

                # Check if indexing is pending
                is_pending, task_id = is_video_pending(abs_path)
                if not is_pending:
                    is_pending, task_id = is_video_pending(video_file_path)
                if is_pending:
                    messages.append(
                        f"Warning: Video '{os.path.basename(video_file_path)}' has a pending indexing task "
                        f"(task_id: {task_id}). Use /twelvelabs:index-video status to check progress."
                    )

        elif video_url:
            # Validate URL
            is_valid, error_msg = validate_url(video_url)
            if not is_valid:
                messages.append(f"Validation error: {error_msg}")
                should_continue = False
            else:
                # Add info for Google Drive URLs
                if is_google_drive_url(video_url):
                    messages.append(
                        "Google Drive link detected. For folder links, all MP4 videos will be indexed."
                    )

                # Check if already indexed
                if is_video_indexed(video_url):
                    video = get_video_by_source(video_url)
                    video_id = video.get("video_id", "unknown") if video else "unknown"
                    messages.append(
                        f"Warning: This URL is already indexed (video_id: {video_id}). "
                        f"Proceeding will create a duplicate."
                    )

                # Check if indexing is pending
                is_pending, task_id = is_video_pending(video_url)
                if is_pending:
                    messages.append(
                        f"Warning: This URL has a pending indexing task (task_id: {task_id}). "
                        f"Use /twelvelabs:index-video status to check progress."
                    )

        else:
            # Neither file path nor URL provided
            messages.append(
                "Validation error: Either videoFilePath or videoUrl must be provided"
            )
            should_continue = False

        # Build response
        response = {
            "continue": should_continue
        }

        if messages:
            response["message"] = " ".join(messages)

        print(json.dumps(response))

    except Exception as e:
        # On hook errors, allow continuation but report the error
        response = {
            "continue": True,
            "message": f"Hook error: {str(e)}"
        }
        print(json.dumps(response))


if __name__ == "__main__":
    main()
