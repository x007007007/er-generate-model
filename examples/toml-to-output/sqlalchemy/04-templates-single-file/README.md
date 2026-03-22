# Template Example - Single File

This example demonstrates how to use templates to share common fields across multiple entities within a single TOML file.

## Features Demonstrated

- **Template Definition**: Define reusable templates with the `package` field
- **Auto-Derived Export Path**: The `export_path` is automatically derived from `package` by appending `_sqlalchemy`
- **Multiple Templates**: Use multiple templates in a single file
- **Template Inheritance**: Entities can extend multiple templates using the `extends` field
- **Field Reuse**: Common fields (timestamps, soft delete) are defined once and reused

## Template Syntax

### Defining a Template

```toml
[templates.TemplateName]
package = "your.package.path"  # Django-style package path

[[templates.TemplateName.columns]]
name = "field_name"
type = "field_type"
# ... other field attributes
```

### Using Templates in Entities

```toml
[entities.EntityName]
extends = ["Template1", "Template2"]  # List of template names
columns = [
    # Entity-specific columns
]
```

## Namespace Transformation

When you define a template with `package = "myapp.models.base"`, the system automatically:

1. Transforms the package to SQLAlchemy namespace: `myapp.models.base_sqlalchemy`
2. Generates a mixin file at: `myapp/models/base_sqlalchemy/timestamp_mixin.py`
3. Creates the mixin class with `__abstract__ = True`

## Running the Example

### Reference Mode (Default)

Generate mixin files and use Python inheritance:

```bash
uv run er-gen-tool convert convert examples/toml-to-output/sqlalchemy/04-templates-single-file/input.toml \
  -f sqlalchemy \
  -d examples/toml-to-output/sqlalchemy/04-templates-single-file/output/ \
  --inheritance-mode reference
```

This will generate:
- `myapp/models/base_sqlalchemy/timestamp_mixin.py` - TimestampMixin class
- `myapp/models/base_sqlalchemy/soft_delete_mixin.py` - SoftDeleteMixin class
- Entity files that import and inherit from these mixins

### Flatten Mode

Expand all template fields inline:

```bash
uv run er-gen-tool convert convert examples/toml-to-output/sqlalchemy/04-templates-single-file/input.toml \
  -f sqlalchemy \
  -d examples/toml-to-output/sqlalchemy/04-templates-single-file/output/ \
  --inheritance-mode flatten
```

This will generate entity files with all fields expanded inline (no separate mixin files).

## Expected Output (Reference Mode)

### Mixin File: `myapp/models/base_sqlalchemy/timestamp_mixin.py`

```python
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TimestampMixin(Base):
    __abstract__ = True
    
    created_at = Column(DateTime, comment="Creation timestamp")
    updated_at = Column(DateTime, comment="Last update timestamp")
```

### Entity File: `user.py`

```python
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from myapp.models.base_sqlalchemy.timestamp_mixin import TimestampMixin
from myapp.models.base_sqlalchemy.soft_delete_mixin import SoftDeleteMixin

class User(TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'user'
    
    id = Column(UUID, primary_key=True, comment="Primary key")
    username = Column(String, unique=True, comment="Unique username")
    email = Column(String, unique=True, comment="User email address")
```

## Benefits

- **DRY Principle**: Define common fields once, reuse everywhere
- **Consistency**: All entities with the same template have identical field definitions
- **Maintainability**: Update template once to update all entities
- **Type Safety**: Generated code uses proper Python inheritance
