---
name: analyze
description: Deprecated alias for /twelvelabs:sync-analyze
disable-model-invocation: true
argument-hint: "[video-id] [index-id] [prompt]"
---

# /twelvelabs:analyze (deprecated)

This command was renamed to `/twelvelabs:sync-analyze` to be symmetric with the new `/twelvelabs:async-analyze`.

## Instructions for Claude

When the user invokes `/twelvelabs:analyze`, tell them:

```
`/twelvelabs:analyze` was renamed to `/twelvelabs:sync-analyze` in v1.2.0
(symmetric with the new `/twelvelabs:async-analyze`). Running sync-analyze
with your arguments now…
```

Then dispatch the entire `$ARGUMENTS` value to the `/twelvelabs:sync-analyze` flow. The behavior, parameters, and output format are unchanged from the previous `/twelvelabs:analyze`.

Refer to `commands/sync-analyze.md` for the full instructions.
