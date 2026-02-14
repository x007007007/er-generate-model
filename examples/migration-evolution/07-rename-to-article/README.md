# Version 7: Rename Post to Article

## Overview
This version renames the Post entity to Article for better semantic clarity.

## Changes
- Renamed Post entity to Article
- Updated all foreign key references from post_id to article_id

## Migration Command
```bash
# Generate migration from v6 to v7
uv run er-gen-tool convert convert -t mermaid -f django blog.mmd -o models.py
```

## Schema
See `blog.mmd` for the complete Mermaid ER diagram.

## Previous/Next
- Previous: [06-anonymous-comments](../06-anonymous-comments/)
- Next: [08-remove-comments](../08-remove-comments/)
