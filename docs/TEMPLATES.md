# Template System Documentation

This document provides comprehensive documentation for the template and mixin generation system in ER Generate Model.

## Table of Contents

1. [Overview](#overview)
2. [Template Syntax](#template-syntax)
3. [Namespace Transformation](#namespace-transformation)
4. [Inheritance Modes](#inheritance-modes)
5. [Cross-File References](#cross-file-references)
6. [CLI Options](#cli-options)
7. [Best Practices](#best-practices)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)

## Overview

The template system allows you to define reusable field sets (mixins) that can be shared across multiple entities. This promotes the DRY (Don't Repeat Yourself) principle and ensures consistency across your data models.

### Key Features

- **Automatic Namespace Transformation**: Django package paths are automatically converted to SQLAlchemy equivalents
- **Cross-File Template References**: Define templates in one file and use them in another
- **Two Inheritance Modes**: Choose between reference mode (Python inheritance) or flatten mode (inline expansion)
- **Flexible Export Paths**: Use auto-derived paths or specify custom locations

## Template Syntax

### Basic Template Definition

```toml
[templates.TemplateName]
package = "your.package.path"

[[templates.TemplateName.columns]]
name = "field_name"
type = "field_type"
# ... other field attributes
```

### Template Fields

- **package** (optional): Django-style package path (e.g., `myapp.models.base`)
- **export_path** (optional): Explicit SQLAlchemy package path (overrides auto-derivation)
- **columns** (required): Array of column definitions

**Validation Rules**:
- At least one of `package` or `export_path` must be specified
- If both are specified, `export_path` takes precedence
- Column array must not be empty

### Using Templates in Entities

```toml
[entities.EntityName]
extends = ["Template1", "Template2"]  # List of template names
columns = [
    # Entity-specific columns
]
```

## Namespace Transformation

The system automatically transforms Django-style package paths to SQLAlchemy equivalents.

### Transformation Rules

1. **Input**: Django package path (e.g., `myapp.models.base`)
2. **Process**: Append `_sqlalchemy` to the last component
3. **Output**: SQLAlchemy package path (e.g., `myapp.models.base_sqlalchemy`)

### Examples

| Django Package | SQLAlchemy Export Path |
|----------------|------------------------|
| `myapp.models.base` | `myapp.models.base_sqlalchemy` |
| `company.common.infrastructure.models` | `company.common.infrastructure.models_sqlalchemy` |
| `shared.mixins` | `shared.mixins_sqlalchemy` |

### Idempotence

The transformation is idempotent - applying it twice gives the same result:

```python
transform("myapp.models.base")           # → "myapp.models.base_sqlalchemy"
transform("myapp.models.base_sqlalchemy") # → "myapp.models.base_sqlalchemy" (unchanged)
```

### File Path Generation

The export path is converted to a file system path:

1. Replace dots with directory separators: `myapp.models.base_sqlalchemy` → `myapp/models/base_sqlalchemy/`
2. Convert class name to snake_case: `TimestampMixin` → `timestamp_mixin.py`
3. Result: `myapp/models/base_sqlalchemy/timestamp_mixin.py`

## Inheritance Modes

The system supports two inheritance modes for handling templates.

### Reference Mode (Default)

**What it does**: Generates separate mixin class files and uses Python inheritance.

**When to use**:
- You want proper Python inheritance
- You need to import and reuse mixins in other code
- You want to maintain a library of reusable mixins
- You're building a large application with shared base classes

**Example**:

```bash
er-gen-tool convert convert models.toml -f sqlalchemy --inheritance-mode reference
```

**Generated Structure**:
```
output/
├── myapp/
│   └── models/
│       └── base_sqlalchemy/
│           ├── __init__.py
│           └── timestamp_mixin.py  # Mixin class
└── user.py  # Imports and inherits from TimestampMixin
```

**Generated Code**:
```python
# timestamp_mixin.py
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TimestampMixin(Base):
    __abstract__ = True
    
    created_at = Column(DateTime, comment="Creation timestamp")
    updated_at = Column(DateTime, comment="Update timestamp")

# user.py
from myapp.models.base_sqlalchemy.timestamp_mixin import TimestampMixin

class User(TimestampMixin):
    __tablename__ = 'user'
    # ... entity-specific fields
```

### Flatten Mode

**What it does**: Expands all template fields directly into entity classes (no separate mixin files).

**When to use**:
- You want simpler output with fewer files
- You don't need to reuse mixins outside of generation
- You're generating code for a simple application
- You want to avoid import dependencies

**Example**:

```bash
er-gen-tool convert convert models.toml -f sqlalchemy --inheritance-mode flatten
```

**Generated Structure**:
```
output/
└── user.py  # All fields expanded inline
```

**Generated Code**:
```python
# user.py
from sqlalchemy import Column, String, DateTime

class User(Base):
    __tablename__ = 'user'
    
    # Fields from TimestampMixin (expanded inline)
    created_at = Column(DateTime, comment="Creation timestamp")
    updated_at = Column(DateTime, comment="Update timestamp")
    
    # Entity-specific fields
    username = Column(String, unique=True)
    email = Column(String, unique=True)
```

### Comparison

| Feature | Reference Mode | Flatten Mode |
|---------|---------------|--------------|
| Mixin Files | ✅ Generated | ❌ Not generated |
| Python Inheritance | ✅ Yes | ❌ No |
| File Count | More files | Fewer files |
| Reusability | High | Low |
| Complexity | Higher | Lower |
| Import Dependencies | Yes | No |

## Cross-File References

You can define templates in one TOML file and reference them from entities in another file.

### File Structure

```
project/
├── base_templates.toml  # Shared templates
├── user_models.toml     # User entities
└── product_models.toml  # Product entities
```

### base_templates.toml

```toml
[templates.AuditMixin]
package = "company.common.models.base"

[[templates.AuditMixin.columns]]
name = "created_at"
type = "datetime"

[[templates.AuditMixin.columns]]
name = "created_by"
type = "string"
```

### user_models.toml

```toml
[entities.USER]
extends = ["AuditMixin"]  # References template from base_templates.toml
columns = [
    {name = "id", type = "uuid", is_pk = true},
    {name = "username", type = "string"},
]
```

### Command

```bash
er-gen-tool convert convert user_models.toml -f sqlalchemy -d output/ \
  --toml-files base_templates.toml
```

**Important**:
- The main input file is specified as the first argument
- Additional template files are specified with `--toml-files`
- You can specify `--toml-files` multiple times for multiple template files
- All templates are registered in a unified registry

## CLI Options

### --inheritance-mode, -i

Controls how templates are handled.

**Values**:
- `reference` (default): Generate mixin files, use Python inheritance
- `flatten`: Expand fields inline, no mixin files

**Example**:
```bash
er-gen-tool convert convert models.toml -f sqlalchemy --inheritance-mode reference
```

### --toml-files

Specifies additional TOML files for cross-file template references.

**Usage**:
```bash
# Single additional file
er-gen-tool convert convert entities.toml -f sqlalchemy \
  --toml-files base_templates.toml

# Multiple additional files
er-gen-tool convert convert entities.toml -f sqlalchemy \
  --toml-files base_templates.toml \
  --toml-files common_mixins.toml \
  --toml-files audit_templates.toml
```

**Notes**:
- Can be specified multiple times
- Each file must exist and be readable
- Templates from all files are merged into a unified registry
- Duplicate template names across files will cause an error

## Best Practices

### 1. Use Auto-Derived Paths by Default

Prefer using only the `package` field and let the system auto-derive the `export_path`:

```toml
# Good
[templates.TimestampMixin]
package = "myapp.models.base"

# Avoid unless necessary
[templates.TimestampMixin]
package = "myapp.models.base"
export_path = "myapp.custom.location"
```

### 2. Organize Templates by Purpose

Group related templates together:

```toml
# Audit templates
[templates.AuditMixin]
package = "company.common.audit"

[templates.VersionMixin]
package = "company.common.audit"

# Timestamp templates
[templates.TimestampMixin]
package = "company.common.timestamps"
```

### 3. Use Descriptive Template Names

Template names should clearly indicate their purpose:

```toml
# Good
[templates.TimestampMixin]
[templates.SoftDeleteMixin]
[templates.AuditTrailMixin]

# Avoid
[templates.Mixin1]
[templates.Base]
[templates.Common]
```

### 4. Document Template Purpose

Add comments to explain what each template provides:

```toml
# Provides created_at and updated_at timestamps for all entities
[templates.TimestampMixin]
package = "myapp.models.base"
```

### 5. Choose the Right Inheritance Mode

- **Use Reference Mode** for:
  - Large applications
  - Shared mixin libraries
  - When you need Python inheritance
  - Enterprise applications

- **Use Flatten Mode** for:
  - Simple applications
  - Quick prototypes
  - When you want minimal file count
  - Single-use models

### 6. Organize Cross-File Templates

For large projects, organize templates into logical files:

```
templates/
├── base_templates.toml      # Core mixins (timestamps, audit)
├── business_templates.toml  # Business logic mixins
└── security_templates.toml  # Security-related mixins
```

### 7. Consistent Naming Conventions

Use consistent naming for packages and templates:

```toml
# Package naming: company.domain.purpose
[templates.AuditMixin]
package = "company.common.audit"

[templates.SecurityMixin]
package = "company.common.security"
```

## Examples

See the [examples/toml-to-output/sqlalchemy/](../examples/toml-to-output/sqlalchemy/) directory for complete examples:

- **04-templates-single-file**: Basic template usage in a single file
- **05-templates-cross-file**: Cross-file template references
- **06-templates-explicit-export**: Different export path strategies

## Troubleshooting

### Error: "Duplicate template name"

**Cause**: Two TOML files define templates with the same name.

**Solution**: Rename one of the templates or use a different template file.

```toml
# File 1
[templates.TimestampMixin]  # ❌ Duplicate

# File 2
[templates.TimestampMixin]  # ❌ Duplicate

# Fix: Rename one
[templates.AuditTimestampMixin]  # ✅ Unique
```

### Error: "Template not found"

**Cause**: Entity references a template that doesn't exist or wasn't loaded.

**Solution**: 
1. Check template name spelling
2. Ensure template file is specified with `--toml-files`
3. Verify template is defined in one of the loaded files

```bash
# Wrong - template file not specified
er-gen-tool convert convert entities.toml -f sqlalchemy

# Correct - template file specified
er-gen-tool convert convert entities.toml -f sqlalchemy \
  --toml-files base_templates.toml
```

### Error: "Invalid package path"

**Cause**: Package path contains invalid Python identifiers.

**Solution**: Use valid Python identifiers (letters, numbers, underscores):

```toml
# Wrong
[templates.MyMixin]
package = "my-app.models.base"  # ❌ Hyphens not allowed

# Correct
[templates.MyMixin]
package = "my_app.models.base"  # ✅ Underscores OK
```

### Generated imports not working

**Cause**: Output directory not in Python path or incorrect import paths.

**Solution**:
1. Ensure output directory is a Python package (has `__init__.py`)
2. Add output directory to PYTHONPATH
3. Use correct import paths based on export_path

```python
# If export_path is "myapp.models.base_sqlalchemy"
from myapp.models.base_sqlalchemy.timestamp_mixin import TimestampMixin
```

### Mixin files not generated

**Cause**: Using flatten mode instead of reference mode.

**Solution**: Use `--inheritance-mode reference`:

```bash
er-gen-tool convert convert models.toml -f sqlalchemy --inheritance-mode reference
```

## Advanced Topics

### Custom Export Paths

You can override the auto-derived export path:

```toml
[templates.CustomMixin]
package = "myapp.models.base"
export_path = "myapp.custom.location"  # Overrides auto-derivation
```

**When to use**:
- You need mixins in a specific location
- You're integrating with existing code structure
- You have special naming requirements

### Template Validation

The system validates templates during discovery:

- At least one of `package` or `export_path` must be specified
- Column array must not be empty
- Package paths must contain valid Python identifiers
- Export paths must be valid Python package paths
- Template names must be valid Python identifiers

### Field Order Preservation

When entities extend templates, field order is preserved:

1. Fields from first template
2. Fields from second template
3. ...
4. Entity-specific fields

```toml
[entities.USER]
extends = ["TimestampMixin", "SoftDeleteMixin"]
columns = [
    {name = "id", type = "uuid", is_pk = true},
    {name = "username", type = "string"},
]

# Generated field order:
# 1. created_at (from TimestampMixin)
# 2. updated_at (from TimestampMixin)
# 3. is_deleted (from SoftDeleteMixin)
# 4. deleted_at (from SoftDeleteMixin)
# 5. id (entity-specific)
# 6. username (entity-specific)
```

## Related Documentation

- [Main README](../README.md) - Project overview and installation
- [Examples](../examples/README.md) - Complete examples
- [SQLAlchemy Examples](../examples/toml-to-output/sqlalchemy/README.md) - SQLAlchemy-specific examples
