#!/usr/bin/env python3
"""Helper functions to read/write the TwelveLabs local config safely.

Config Schema:
{
  "default_index_id": string | null,  # Default index for operations
  "videos": {                          # Indexed videos keyed by video_id
    "<video_id>": {
      "video_id": string,
      "task_id": string,
      "source": string,                # File path or URL
      "filename": string | null,
      "status": string,                # "ready", "indexing", "failed"
      "indexed_at": string             # ISO timestamp
    }
  },
  "pending_tasks": {                   # Tasks being indexed, keyed by task_id
    "<task_id>": {
      "task_id": string,
      "source": string,                # File path or URL
      "status": string,                # "validating", "pending", "queued", "indexing"
      "started_at": string             # ISO timestamp
    }
  },
  "pending_embedding_tasks": {         # Embedding tasks in progress, keyed by task_id
    "<task_id>": {
      "task_id": string,
      "source": string,                # File path or URL
      "status": string,                # "processing", "ready", "failed"
      "started_at": string             # ISO timestamp
    }
  },
  "analysis_cache": {                  # Cached analysis results
    "<video_id>": {
      "<analysis_type>": {
        "result": any,
        "cached_at": string            # ISO timestamp
      }
    }
  }
}
"""

import json
import os
import fcntl
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

# Config file location
CONFIG_DIR = Path(__file__).parent
CONFIG_FILE = CONFIG_DIR / "config.json"

# Default config schema
DEFAULT_CONFIG = {
    "default_index_id": None,
    "videos": {},
    "pending_tasks": {},
    "pending_embedding_tasks": {},
    "analysis_cache": {}
}


def get_config_path() -> Path:
    """Get the path to the config file."""
    return CONFIG_FILE


def read_config() -> dict:
    """Read the config file safely.
    
    Returns the config dict, or default config if file doesn't exist.
    """
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        # Ensure all required keys exist
        for key in DEFAULT_CONFIG:
            if key not in config:
                config[key] = DEFAULT_CONFIG[key]
        return config
    except (json.JSONDecodeError, IOError):
        return DEFAULT_CONFIG.copy()


def write_config(config: dict) -> bool:
    """Write the config file safely with file locking.
    
    Returns True on success, False on failure.
    """
    try:
        # Ensure directory exists
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Write with exclusive lock to prevent race conditions
        with open(CONFIG_FILE, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(config, f, indent=2)
                f.write("\n")
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return True
    except (IOError, OSError):
        return False


def get_default_index_id() -> Optional[str]:
    """Get the default index ID from config."""
    config = read_config()
    return config.get("default_index_id")


def set_default_index_id(index_id: str) -> bool:
    """Set the default index ID."""
    config = read_config()
    config["default_index_id"] = index_id
    return write_config(config)


def add_pending_task(task_id: str, source: str, status: str = "pending") -> bool:
    """Add a task to pending_tasks."""
    config = read_config()
    config["pending_tasks"][task_id] = {
        "task_id": task_id,
        "source": source,
        "status": status,
        "started_at": datetime.utcnow().isoformat() + "Z"
    }
    return write_config(config)


def update_pending_task_status(task_id: str, status: str) -> bool:
    """Update the status of a pending task."""
    config = read_config()
    if task_id in config["pending_tasks"]:
        config["pending_tasks"][task_id]["status"] = status
        return write_config(config)
    return False


def complete_task(task_id: str, video_id: str, filename: Optional[str] = None) -> bool:
    """Move a task from pending_tasks to videos when indexing completes."""
    config = read_config()
    
    task = config["pending_tasks"].pop(task_id, None)
    if task is None:
        return False
    
    config["videos"][video_id] = {
        "video_id": video_id,
        "task_id": task_id,
        "source": task.get("source", "unknown"),
        "filename": filename,
        "status": "ready",
        "indexed_at": datetime.utcnow().isoformat() + "Z"
    }
    return write_config(config)


def fail_task(task_id: str) -> bool:
    """Mark a pending task as failed and remove from pending."""
    config = read_config()
    if task_id in config["pending_tasks"]:
        del config["pending_tasks"][task_id]
        return write_config(config)
    return False


def get_video(video_id: str) -> Optional[dict]:
    """Get video info by video_id."""
    config = read_config()
    return config["videos"].get(video_id)


def get_video_by_source(source: str) -> Optional[dict]:
    """Find a video by its source path/URL."""
    config = read_config()
    for video in config["videos"].values():
        if video.get("source") == source:
            return video
    return None


def is_video_indexed(source: str) -> bool:
    """Check if a video source is already indexed."""
    return get_video_by_source(source) is not None


def get_pending_task(task_id: str) -> Optional[dict]:
    """Get a pending task by task_id."""
    config = read_config()
    return config["pending_tasks"].get(task_id)


def get_all_pending_tasks() -> dict:
    """Get all pending tasks."""
    config = read_config()
    return config["pending_tasks"]


def add_pending_embedding_task(task_id: str, source: str, status: str = "processing") -> bool:
    """Add an embedding task to pending_embedding_tasks."""
    config = read_config()
    config["pending_embedding_tasks"][task_id] = {
        "task_id": task_id,
        "source": source,
        "status": status,
        "started_at": datetime.utcnow().isoformat() + "Z"
    }
    return write_config(config)


def update_pending_embedding_task_status(task_id: str, status: str) -> bool:
    """Update the status of a pending embedding task."""
    config = read_config()
    if task_id in config["pending_embedding_tasks"]:
        config["pending_embedding_tasks"][task_id]["status"] = status
        return write_config(config)
    return False


def complete_embedding_task(task_id: str) -> bool:
    """Mark an embedding task as complete and remove from pending."""
    config = read_config()
    if task_id in config["pending_embedding_tasks"]:
        del config["pending_embedding_tasks"][task_id]
        return write_config(config)
    return False


def fail_embedding_task(task_id: str) -> bool:
    """Mark a pending embedding task as failed and remove from pending."""
    config = read_config()
    if task_id in config["pending_embedding_tasks"]:
        del config["pending_embedding_tasks"][task_id]
        return write_config(config)
    return False


def get_pending_embedding_task(task_id: str) -> Optional[dict]:
    """Get a pending embedding task by task_id."""
    config = read_config()
    return config["pending_embedding_tasks"].get(task_id)


def get_all_pending_embedding_tasks() -> dict:
    """Get all pending embedding tasks."""
    config = read_config()
    return config["pending_embedding_tasks"]


def cache_analysis(video_id: str, analysis_type: str, result: Any) -> bool:
    """Cache an analysis result."""
    config = read_config()
    if video_id not in config["analysis_cache"]:
        config["analysis_cache"][video_id] = {}
    
    config["analysis_cache"][video_id][analysis_type] = {
        "result": result,
        "cached_at": datetime.utcnow().isoformat() + "Z"
    }
    return write_config(config)


def get_cached_analysis(video_id: str, analysis_type: str) -> Optional[dict]:
    """Get a cached analysis result."""
    config = read_config()
    video_cache = config["analysis_cache"].get(video_id, {})
    return video_cache.get(analysis_type)


def clear_analysis_cache(video_id: Optional[str] = None) -> bool:
    """Clear analysis cache for a video or all videos."""
    config = read_config()
    if video_id:
        if video_id in config["analysis_cache"]:
            del config["analysis_cache"][video_id]
    else:
        config["analysis_cache"] = {}
    return write_config(config)


if __name__ == "__main__":
    # Test the config helper
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "read":
            print(json.dumps(read_config(), indent=2))
        elif cmd == "path":
            print(get_config_path())
        else:
            print(f"Unknown command: {cmd}")
    else:
        print(json.dumps(read_config(), indent=2))
