# Version 3: Add Posts Entity

## Overview
This version introduces the Post entity and establishes a relationship with User.

## Changes
- Created Post entity with fields:
  - id (UUID, Primary Key)
  - author_id (UUID, Foreign Key to User)
  - title (String)
  - content (Text)
  - created_at (DateTime)
- Added one-to-many relationship: User writes Posts

## Migration Command
```bash
# Generate migration from v2 to v3
uv run er-convert convert -t mermaid -f django blog.mmd -o models.py
```

## Schema
See `blog.mmd` for the complete Mermaid ER diagram.

## Previous/Next
- Previous: [02-add-email](../02-add-email/)
- Next: [04-add-comments](../04-add-comments/)
