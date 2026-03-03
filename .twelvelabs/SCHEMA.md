# TwelveLabs Local Config Schema

The `.twelvelabs/config.json` file stores local state for the TwelveLabs plugin.

## Schema

```json
{
  "default_index_id": "<string | null>",
  "videos": {
    "<video_id>": {
      "video_id": "<string>",
      "task_id": "<string>",
      "source": "<string>",
      "filename": "<string | null>",
      "status": "<ready | indexing | failed>",
      "indexed_at": "<ISO timestamp>"
    }
  },
  "pending_tasks": {
    "<task_id>": {
      "task_id": "<string>",
      "source": "<string>",
      "status": "<validating | pending | queued | indexing>",
      "started_at": "<ISO timestamp>"
    }
  },
  "pending_embedding_tasks": {
    "<task_id>": {
      "task_id": "<string>",
      "source": "<string>",
      "status": "<processing | ready | failed>",
      "started_at": "<ISO timestamp>"
    }
  },
  "analysis_cache": {
    "<video_id>": {
      "<analysis_type>": {
        "result": "<any>",
        "cached_at": "<ISO timestamp>"
      }
    }
  }
}
```

## Fields

### default_index_id
The TwelveLabs index ID to use by default for operations. Set this to avoid specifying index ID every time.

### videos
Map of indexed videos keyed by video_id. Contains metadata about successfully indexed videos.

### pending_tasks
Map of indexing tasks in progress keyed by task_id. Tasks are moved to `videos` when complete.

### pending_embedding_tasks
Map of embedding tasks in progress keyed by task_id. Tasks are removed when complete or failed.

### analysis_cache
Cache of analysis results to avoid redundant API calls. Keyed by video_id then analysis_type.

## Usage

Use the `config_helper.py` module to safely read/write config:

```python
from .twelvelabs.config_helper import (
    read_config,
    write_config,
    add_pending_task,
    complete_task,
    cache_analysis,
    get_cached_analysis
)
```
