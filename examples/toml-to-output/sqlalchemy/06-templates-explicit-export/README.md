# Template Example - Explicit Export Path

This example demonstrates the difference between auto-derived and explicit export paths for templates.

## Features Demonstrated

- **Auto-Derived Export Path**: Using only `package` field (automatic transformation)
- **Explicit Export Path**: Using both `package` and `export_path` (explicit override)
- **Direct Export Path**: Using only `export_path` (no package field)
- **Export Path Precedence**: When both are specified, `export_path` takes precedence

## Template Path Strategies

### Strategy 1: Auto-Derived (Recommended)

```toml
[templates.AutoDerivedMixin]
package = "myapp.models.base"
# export_path auto-derived: myapp.models.base_sqlalchemy
```

**When to use**: Default choice for most cases. Follows consistent naming convention.

**Result**: Mixin generated at `myapp/models/base_sqlalchemy/auto_derived_mixin.py`

### Strategy 2: Explicit Override

```toml
[templates.CustomLocationMixin]
package = "myapp.models.base"
export_path = "myapp.custom.mixins"  # Overrides auto-derivation
```

**When to use**: When you need mixins in a specific location that doesn't follow the standard pattern.

**Result**: Mixin generated at `myapp/custom/mixins/custom_location_mixin.py`

### Strategy 3: Direct Export

```toml
[templates.DirectExportMixin]
export_path = "shared.common.base"  # No package field
```

**When to use**: When you're only targeting SQLAlchemy and don't need Django compatibility.

**Result**: Mixin generated at `shared/common/base/direct_export_mixin.py`

## Namespace Transformation Rules

The automatic transformation follows these rules:

1. **Input**: Django-style package path (e.g., `myapp.models.base`)
2. **Transformation**: Append `_sqlalchemy` to the last component
3. **Output**: SQLAlchemy package path (e.g., `myapp.models.base_sqlalchemy`)

**Idempotent**: Transforming twice gives the same result:
- `myapp.models.base` → `myapp.models.base_sqlalchemy`
- `myapp.models.base_sqlalchemy` → `myapp.models.base_sqlalchemy` (unchanged)

## Running the Example

```bash
uv run er-gen-tool convert convert examples/toml-to-output/sqlalchemy/06-templates-explicit-export/input.toml \
  -f sqlalchemy \
  -d examples/toml-to-output/sqlalchemy/06-templates-explicit-export/output/ \
  --inheritance-mode reference
```

## Expected Output Structure

```
output/
├── myapp/
│   ├── models/
│   │   └── base_sqlalchemy/
│   │       └── auto_derived_mixin.py
│   └── custom/
│       └── mixins/
│           └── custom_location_mixin.py
├── shared/
│   └── common/
│       └── base/
│           └── direct_export_mixin.py
└── task.py  # Imports from all three locations
```

## Generated Entity Example

```python
from myapp.models.base_sqlalchemy.auto_derived_mixin import AutoDerivedMixin
from myapp.custom.mixins.custom_location_mixin import CustomLocationMixin
from shared.common.base.direct_export_mixin import DirectExportMixin

class Task(AutoDerivedMixin, CustomLocationMixin, DirectExportMixin):
    __tablename__ = 'task'
    
    title = Column(String, comment="Task title")
    description = Column(Text, comment="Task description")
    due_date = Column(DateTime, nullable=True, comment="Due date")
```

## Best Practices

1. **Use Auto-Derived by Default**: Stick with `package` field only for consistency
2. **Explicit Override Sparingly**: Only use `export_path` when you have a specific reason
3. **Document Custom Paths**: If using explicit paths, document why in comments
4. **Consistent Naming**: Keep package naming consistent across your project

## Validation Rules

- At least one of `package` or `export_path` must be specified
- If both are specified, `export_path` takes precedence
- Export paths must be valid Python package paths
- Package paths must contain valid Python identifiers
