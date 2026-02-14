# Version 8: Remove Comments

## Overview
This version removes the Comment entity from the schema.

## Changes
- Removed Comment entity
- Removed all relationships involving Comment

## Migration Command
```bash
# Generate migration from v7 to v8
uv run er-convert convert -t mermaid -f django blog.mmd -o models.py
```

## Schema
See `blog.mmd` for the complete Mermaid ER diagram.

## Previous
- Previous: [07-rename-to-article](../07-rename-to-article/)

## Note
This is the final version in the evolution series.
