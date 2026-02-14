# Version 4: Add Comments Entity

## Overview
This version adds the Comment entity to enable user comments on posts.

## Changes
- Created Comment entity with fields:
  - id (UUID, Primary Key)
  - post_id (UUID, Foreign Key to Post)
  - author_id (UUID, Foreign Key to User)
  - content (Text)
  - created_at (DateTime)
- Added relationships:
  - Post has many Comments
  - User writes many Comments

## Migration Command
```bash
# Generate migration from v3 to v4
uv run er-convert convert -t mermaid -f django blog.mmd -o models.py
```

## Schema
See `blog.mmd` for the complete Mermaid ER diagram.

## Previous/Next
- Previous: [03-add-posts](../03-add-posts/)
- Next: [05-enhance-features](../05-enhance-features/)
