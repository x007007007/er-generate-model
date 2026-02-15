# ER Diagram Generator Tool

Unified CLI tool for ER diagram operations including conversion, AI-assisted modeling, and database migrations.

> **Note**: This package is part of the ER monorepo workspace. For workspace development setup, see the [root README](../../README.md) and [DEVELOPMENT.md](../../DEVELOPMENT.md).

## Installation

### Workspace Installation (Development)

If you're working in the monorepo workspace:

```bash
# From workspace root
uv sync
```

This installs all packages in editable mode, including `er-gen-tool` and its internal dependency `er-gen-core`.

### Standalone Installation

For standalone use outside the workspace:

### Basic Installation (Core Features)

```bash
uv pip install x007007007-er-gen-tool
```

This includes:
- `convert` - Convert ER diagrams to code
- `makemigration` - Generate database migrations
- `migrate` - Manage database migrations

### With AI Features

```bash
uv pip install x007007007-er-gen-tool[ai]
# or
uv pip install x007007007-er-gen-tool x007007007-er-gen-tool-ai
```

This adds:
- `ai-assist` - AI-powered ER modeling

## Usage

### Convert Command

Convert ER diagrams to code:

```bash
# Convert Mermaid to Django models
er-gen-tool convert schema.mmd -f django -o models.py

# Convert TOML to SQLAlchemy
er-gen-tool convert schema.toml -t toml -f sqlalchemy -o models.py

# Convert with custom options
er-gen-tool convert schema.mmd -f django -a myapp -p myapp_ -o models.py

# Split Django models into separate files
er-gen-tool convert schema.mmd -f django --split-models -d output/
```

**Options:**
- `-t, --input-type`: Input type (mermaid, plantuml, db, toml)
- `-f, --format`: Output format (django, sqlalchemy, mermaid, plantuml)
- `-o, --output`: Output file path
- `-d, --output-dir`: Output directory for multi-file output
- `-a, --app-label`: Django app label
- `-p, --table-prefix`: Table name prefix
- `--split-models`: Split Django models into separate files

### Migration Commands

Generate and manage database migrations:

```bash
# Generate migration from ER diagram
er-gen-tool makemigration -n blog -e schema.mmd

# Show all migrations
er-gen-tool migrate showmigrations

# Show migrations for specific namespace
er-gen-tool migrate showmigrations -n blog
```

**Options:**
- `-n, --namespace`: Migration namespace
- `-e, --er-file`: ER diagram file (Mermaid format)
- `-d, --migrations-dir`: Migrations directory (default: .migrations)
- `--name`: Custom migration name

### AI-Assist Commands (Requires AI Extension)

AI-powered ER modeling:

```bash
# Generate ER model from requirements
er-gen-tool ai-assist generate "Design a blog system with posts and comments"

# Refine existing TOML configuration
er-gen-tool ai-assist refine existing.toml "Add user authentication"

# Interactive refinement
er-gen-tool ai-assist chat existing.toml
```

**Note:** AI features require the `x007007007-er-gen-tool-ai` package to be installed.

### Internal Dependencies

This package depends on:
- `x007007007-er-gen-core>=0.3.0` - Core ER diagram functionality (required)
- `x007007007-er-gen-tool-ai>=0.3.0` - AI features (optional, via `[ai]` extra)

In the workspace, these dependencies are automatically resolved from local packages.

## Plugin System

The tool supports plugins via entry points. Plugins can add new subcommands automatically.

To create a plugin:

1. Create a Click command in your package
2. Register it in your `pyproject.toml`:

```toml
[project.entry-points."er_gen_tool.plugins"]
my-command = "my_package.cli:my_command"
```

3. Install your plugin package

The command will automatically appear in `er-gen-tool --help`.

## Dependencies

- Core: `x007007007-er-gen-core>=0.3.0`
- CLI: `click>=8.1.0`
- AI (optional): `x007007007-er-gen-tool-ai>=0.3.0`

## License

MIT
