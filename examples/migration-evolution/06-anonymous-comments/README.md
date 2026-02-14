# Version 6: Anonymous Comments

## Overview
This version allows anonymous comments by making the author field optional.

## Changes
- Modified Comment entity:
  - author_id is now nullable (allows anonymous comments)

## Migration Command
```bash
# Generate migration from v5 to v6
uv run er-gen-tool convert convert -t mermaid -f django blog.mmd -o models.py
```

## Schema
See `blog.mmd` for the complete Mermaid ER diagram.

## Previous/Next
- Previous: [05-enhance-features](../05-enhance-features/)
- Next: [07-rename-to-article](../07-rename-to-article/)
