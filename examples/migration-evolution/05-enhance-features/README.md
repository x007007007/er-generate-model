# Version 5: Enhance Features

## Overview
This version enhances the schema with additional fields for better functionality.

## Changes
- Added fields to Post entity:
  - published_at (DateTime)
  - view_count (Integer)
- Added fields to Comment entity:
  - is_approved (Boolean)

## Migration Command
```bash
# Generate migration from v4 to v5
uv run er-gen-tool convert convert -t mermaid -f django blog.mmd -o models.py
```

## Schema
See `blog.mmd` for the complete Mermaid ER diagram.

## Previous/Next
- Previous: [04-add-comments](../04-add-comments/)
- Next: [06-anonymous-comments](../06-anonymous-comments/)
