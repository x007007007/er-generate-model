# Version 2: Add Email Field

## Overview
This version adds an email field to the User entity.

## Changes
- Added email field to User entity:
  - email (String, Unique)

## Migration Command
```bash
# Generate migration from v1 to v2
uv run er-gen-tool convert convert -t mermaid -f django blog.mmd -o models.py
```

## Schema
See `blog.mmd` for the complete Mermaid ER diagram.

## Previous/Next
- Previous: [01-initial](../01-initial/)
- Next: [03-add-posts](../03-add-posts/)
